import requests
import json
import time
import random
from datetime import datetime
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MolitCrawler:
    """
    국토교통부 실거래가 공공 API 크롤러
    
    주요 기능:
    - 국토교통부 실거래가 공개시스템 API 연동
    - 아파트, 연립/다세대, 오피스텔 매매/전월세 데이터 수집
    - 공식 데이터로 법적 리스크 없음
    - JSON 응답 처리 및 데이터 변환
    
    사용 방법:
    1. 공공 데이터 포털(data.go.kr)에서 서비스 키 발급
    2. MolitCrawler 인스턴스 생성 (서비스 키 전달)
    3. 메서드 호출을 통해 데이터 조회
    
    법적 주의사항:
    - 국토교통부 실거래가 공개시스템은 공공데이터로 freely 사용 가능
    - 네이버 부동산과 달리 크롤링 제한 없음
    - 단, API 사용량 제한(하루 1000회) 준수 필요
    """
    
    # 국토교통부 실거래가 공공 API 기본 URL
    BASE_URL = "https://apis.data.go.kr/1613000/RTMSDataSvc"
    
    # 서비스별 엔드포인트 매핑
    # 각 서비스는 다른 유형의 부동산 거래 데이터를 제공
    ENDPOINTS = {
        'apt_trade': '/AptTradeSvc/getAptTrade',           # 아파트 매매 실거래가
        'apt_rent': '/AptRentSvc/getAptRent',              # 아파트 전월세 실거래가
        'villa_trade': '/VillaTradeSvc/getVillaTrade',     # 연립/다세대 주택 매매
        'villa_rent': '/VillaRentSvc/getVillaRent',        # 연립/다세대 주택 전월세
        'officetel_trade': '/OffiTradeSvc/getOffiTrade',   # 오피스텔 매매
        'officetel_rent': '/OffiRentSvc/getOffiRent',     # 오피스텔 전월세
    }
    
    def __init__(self, service_key: str):
        """
        크롤러 초기화
        
        Args:
            service_key: 공공 데이터 포털 서비스 키
        """
        self.service_key = service_key
        self.session = requests.Session()
        
        # 요청 헤더 설정
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        })
    
    def get_apt_trade(self, lawd_cd: str, deal_ymd: str, page: int = 1, rows: int = 10) -> List[Dict]:
        """
        아파트 매매 실거래가 조회
        
        Args:
            lawd_cd: 법정동 코드 (5자리, 예: "11680" = 강남구)
            deal_ymd: 계약년월 (예: "202603")
            page: 페이지 번호
            rows: 한 페이지 결과 수
            
        Returns:
            매매 거래 목록
        """
        return self._fetch_data('apt_trade', lawd_cd, deal_ymd, page, rows)
    
    def get_apt_rent(self, lawd_cd: str, deal_ymd: str, page: int = 1, rows: int = 10) -> List[Dict]:
        """
        아파트 전월세 실거래가 조회
        """
        return self._fetch_data('apt_rent', lawd_cd, deal_ymd, page, rows)
    
    def _fetch_data(self, service_type: str, lawd_cd: str, deal_ymd: str, page: int, rows: int) -> List[Dict]:
        """데이터 fetching 공통 메서드"""
        endpoint = self.ENDPOINTS.get(service_type)
        if not endpoint:
            logger.error(f"알 수 없는 서비스 유형: {service_type}")
            return []
        
        url = f"{self.BASE_URL}{endpoint}"
        
        params = {
            'serviceKey': self.service_key,
            'LAWD_CD': lawd_cd,
            'DEAL_YMD': deal_ymd,
            'pageNo': page,
            'numOfRows': rows,
            '_type': 'json'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # JSON 응답 파싱
            data = response.json()
            
            # 응답 구조 확인
            if 'response' in data and 'body' in data['response']:
                body = data['response']['body']
                if 'items' in body and body['items']:
                    items = body['items'].get('item', [])
                    if isinstance(items, dict):
                        items = [items]  # 단일 항목을 리스트로 변환
                    
                    # 데이터 변환
                    return self._transform_data(items, service_type)
                else:
                    logger.info(f"데이터 없음: {service_type}, {lawd_cd}, {deal_ymd}")
                    return []
            else:
                logger.error(f"예상치 못한 응답 구조: {data}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API 요청 실패: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}")
            return []
    
    def _transform_data(self, items: List[Dict], service_type: str) -> List[Dict]:
        """API 응답을 표준 형식으로 변환"""
        transformed = []
        
        for item in items:
            try:
                # 가격 정보 파싱
                price_str = item.get('dealAmount', '0')
                price = self._parse_price(price_str)
                
                # 면적 정보 파싱
                area_str = item.get('excluUseAr', '0')
                area = float(area_str) if area_str else 0.0
                
                # 날짜 정보
                deal_date = f"{item.get('dealYear', '')}-{item.get('dealMonth', '').zfill(2)}-{item.get('dealDay', '').zfill(2)}"
                
                # 매물 정보 구성
                property_data = {
                    'id': f"molit_{item.get('aptSeq', '') or item.get('sggCd', '')}_{deal_date}",
                    'title': f"{item.get('aptNm', '') or item.get('bdNm', '')}",
                    'location': f"{item.get('sggNm', '')} {item.get('umdNm', '')}",
                    'price': price,
                    'area': area,
                    'description': f"{item.get('floor', '')}층, {deal_date} 거래",
                    'url': f"https://rt.molit.go.kr/",
                    'crawled_at': datetime.now().isoformat(),
                    'property_type': self._get_property_type(service_type),
                    'trade_type': self._get_trade_type(service_type),
                    'deal_date': deal_date,
                    'year': item.get('dealYear', ''),
                    'month': item.get('dealMonth', ''),
                    'day': item.get('dealDay', ''),
                    'build_year': item.get('buildYear', ''),
                    'floor': item.get('floor', ''),
                    'source': 'molit'
                }
                
                transformed.append(property_data)
                
            except Exception as e:
                logger.error(f"데이터 변환 실패: {e}")
                continue
        
        return transformed
    
    def _parse_price(self, price_str: str) -> int:
        """가격 문자열 파싱 (만원 단위)"""
        if not price_str:
            return 0
        
        # 쉼표 제거 및 공백 제거
        price_str = price_str.replace(',', '').replace(' ', '')
        
        try:
            return int(price_str)
        except ValueError:
            # 억 단위 처리
            if '억' in price_str:
                parts = price_str.split('억')
                억 = int(parts[0]) * 10000 if parts[0] else 0
                만 = int(parts[1]) if len(parts) > 1 and parts[1] else 0
                return 억 + 만
            return 0
    
    def _get_property_type(self, service_type: str) -> str:
        """서비스 유형에 따른 매물 유형 반환"""
        if 'apt' in service_type:
            return '아파트'
        elif 'villa' in service_type:
            return '연립/다세대'
        elif 'offi' in service_type:
            return '오피스텔'
        else:
            return '부동산'
    
    def _get_trade_type(self, service_type: str) -> str:
        """서비스 유형에 따른 거래 유형 반환"""
        if 'trade' in service_type:
            return '매매'
        elif 'rent' in service_type:
            return '전세'
        else:
            return '거래'
    
    def search_region(self, region_code: str, deal_ymd: str = None) -> List[Dict]:
        """
        지역 검색 (호환성을 위한 메서드)
        
        Args:
            region_code: 지역 코드 (법정동 코드 5자리)
            deal_ymd: 거래 년월 (기본값: 최근 3개월)
            
        Returns:
            매물 목록
        """
        if not deal_ymd:
            # 최근 3개월 데이터 조회
            now = datetime.now()
            deal_ymd = f"{now.year}{now.month:02d}"
        
        logger.info(f"국토교통부 API 지역 검색: {region_code}, {deal_ymd}")
        
        # 아파트 매매 데이터 조회
        properties = self.get_apt_trade(region_code, deal_ymd, rows=20)
        
        logger.info(f"검색된 매물 수: {len(properties)}")
        
        return properties
    
    def close(self):
        """리소스 정리"""
        self.session.close()
        logger.info("국토교통부 크롤러 종료")

# 사용 예시
if __name__ == "__main__":
    # 서비스 키는 공공 데이터 포털에서 발급받아야 합니다
    SERVICE_KEY = "YOUR_SERVICE_KEY"
    
    crawler = MolitCrawler(SERVICE_KEY)
    
    # 강남구 2026년 3월 데이터 조회
    properties = crawler.search_region("11680", "202603")
    
    print(f"검색된 매물: {len(properties)}개")
    for prop in properties[:3]:
        print(f"- {prop['title']}: {prop['price']}만원")
    
    crawler.close()