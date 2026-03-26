import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import random
from datetime import datetime
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NaverRealEstateCrawler:
    """
    네이버 부동산 크롤러 클래스
    
    주요 기능:
    - 네이버 부동산 API를 통한 매물 정보 크롤링
    - requests와 Selenium을 이용한 하이브리드 크롤링
    - User-Agent 로테이션을 통한 차단 회피
    - 랜덤 지연 시간을 통한 요청 간격 조절
    - 에러 핸들링 및 재시도 로직
    
    주의사항:
    - 네이버 부동산의 robots.txt를 준수해야 합니다
    - 과도한 요청은 429 오류(Too Many Requests)를 유발할 수 있습니다
    - 크롤링 시 적절한 지연 시간(3-10초)을 설정하세요
    """
    
    # 기본 URL 설정
    BASE_URL = "https://new.land.naver.com"  # 네이버 부동산 메인 URL
    API_URL = "https://new.land.naver.com/api"  # 네이버 부동산 API URL
    
    # User-Agent 리스트 (브라우저마다 다른 User-Agent 사용)
    # 로테이션을 통해 차단 회피 확률 높임
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',  # Chrome 122
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',  # Chrome 121
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',  # Chrome 120
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',  # Mac Chrome
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',  # Firefox 123
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',  # Firefox 122
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',  # Mac Firefox
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',  # Safari 17.3
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0', # Edge
    ]
    
    def __init__(self, use_selenium: bool = False, headless: bool = True):
        """
        크롤러 초기화
        
        Args:
            use_selenium: Selenium 사용 여부 (JavaScript 렌더링 필요 시 True)
            headless: 헤드리스 모드 (브라우저 창 숨김)
        """
        self.use_selenium = use_selenium
        self.headless = headless
        self.driver = None
        self.session = None
        self._reset_session()
        
        if use_selenium:
            self._init_selenium(headless)

    def _reset_session(self):
        """세션 초기화 (쿠키 및 헤더 재설정)"""
        if self.session:
            self.session.close()
        self.session = requests.Session()
        logger.info("세션 초기화 완료")

    def _get_mobile_headers(self):
        """모바일 환경에 맞는 깨끗한 헤더 생성"""
        return {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://m.land.naver.com/',
            'Origin': 'https://m.land.naver.com',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }
    
    def _random_delay(self, min_seconds: float = 3.0, max_seconds: float = 10.0):
        """랜덤 지연 시간 (요청 간격 조절)"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def _wait_with_backoff(self, attempt: int, base_min: float = 20.0, base_max: float = 40.0):
        """429 오류 발생 시 지수 백오프 적용 대기"""
        multiplier = 2 ** attempt
        delay = random.uniform(base_min, base_max) * multiplier
        logger.warning(f"429 감지됨. {delay:.1f}초 동안 대기 후 재시도합니다. (시도 {attempt+1})")
        time.sleep(delay)
    
    def _rotate_user_agent(self):
        """User-Agent 변경 (모바일 환경의 경우 기본 설정 유지)"""
        if self.session is None:
            self._reset_session()
        # 모바일 환경에서는 User-Agent 로테이션보다 일관성 있는 세션이 차단 방지에 유리함
        pass
    
    def _init_selenium(self, headless: bool):
        """Selenium WebDriver 초기화"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Selenium WebDriver 초기화 완료")
        except Exception as e:
            logger.error(f"Selenium 초기화 실패: {e}")
            self.use_selenium = False
    
    def search_region(self, region_name: str) -> List[Dict]:
        """
        지역 검색
        
        Args:
            region_name: 지역명 (예: "강남구", "마포구")
            
        Returns:
            검색된 매물 목록
        """
        logger.info(f"지역 검색 시작: {region_name}")
        
        # 지역 코드 조회
        region_code = self._get_region_code(region_name)
        if not region_code:
            logger.warning(f"지역 코드를 찾을 수 없음: {region_name}")
            return []
        
        # 매물 검색
        properties = self._search_properties(region_code)
        
        return properties
    
    def _get_region_code(self, region_name: str, max_retries: Optional[int] = None) -> Optional[str]:
        """지역 코드 조회 (모바일 웹 페이지 스크래핑 방식)"""
        from app.config import settings
        import urllib.parse
        import re
        retries = max_retries or settings.MAX_RETRIES
        
        for attempt in range(retries):
            try:
                if attempt > 0:
                    self._rotate_user_agent()
                else:
                    self._random_delay(2.0, 5.0)
                
                # 모바일 검색 페이지 호출
                encoded_query = urllib.parse.quote(region_name)
                url = f"https://m.land.naver.com/search/result/{encoded_query}"
                
                if self.session is None:
                    self._reset_session()
                
                # 모바일 헤더 명시적 설정
                headers = self._get_mobile_headers()
                
                response = self.session.get(url, headers=headers, timeout=30) # type: ignore
                
                if response.status_code == 429:
                    self._wait_with_backoff(attempt)
                    self._reset_session()
                    continue
                
                response.raise_for_status()
                html = response.text
                
                # HTML에서 cortarNo 추출
                match = re.search(r"cortarNo\s*[:=]\s*['\"](\d+)['\"]", html)
                if match:
                    return match.group(1)
                
                # 지역을 찾지 못한 경우
                logger.warning(f"HTML에서 지역 코드를 찾을 수 없음: {region_name}")
                return None
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"지역 코드 조회 시도 {attempt + 1}/{retries} 실패: {e}")
                if attempt == retries - 1:
                    logger.error(f"지역 코드 조회 최종 실패: {region_name}")
                    return None
                
                self._random_delay(5.0, 10.0)
                self._reset_session()
                continue
        
        return None
    
    def _search_properties(self, region_code: str, max_retries: Optional[int] = None) -> List[Dict]:
        """모바일 클러스터 API를 활용한 매물 검색 (429 차단 우회)"""
        from app.config import settings
        retries = max_retries or settings.MAX_RETRIES
        properties = []
        
        # 1. 클러스터 목록 조회 (해당 지역의 매물 그룹핑 정보)
        cluster_url = "https://m.land.naver.com/cluster/clusterList"
        cluster_params = {
            'view': 'atcl',
            'cortarNo': region_code,
            'rletTpCd': 'A01',  # 아파트
            'tradTpCd': 'A1:B1:B2', # 매매/전세/월세
            'z': 12
        }
        
        clusters = []
        for attempt in range(retries):
            try:
                if attempt > 0: self._rotate_user_agent()
                else: self._random_delay(2.0, 5.0)
                
                if self.session is None: self._reset_session()
                
                # 모바일 헤더 강제
                headers = self._get_mobile_headers()
                
                response = self.session.get(cluster_url, params=cluster_params, headers=headers, timeout=30) # type: ignore
                
                if response.status_code == 429:
                    self._wait_with_backoff(attempt)
                    self._reset_session()
                    continue
                
                response.raise_for_status()
                data = response.json()
                clusters = data.get('data', {}).get('ARTICLE', [])
                logger.info(f"지역코드 {region_code}에서 클러스터 {len(clusters)}개 발견")
                break
                
            except Exception as e:
                logger.error(f"클러스터 검색 실패: {e}")
                if attempt == retries - 1:
                    return properties
                self._random_delay(5.0, 10.0)
                self._reset_session()
        
        if not clusters:
            return properties
            
        # 2. 각 클러스터별로 매물 상세 목록 조회 (최대 10개 클러스터만 수집하여 부하 방지)
        for idx, cluster in enumerate(clusters[:10]):
            lgeo = cluster.get('lgeo')
            lat, lon = cluster.get('lat'), cluster.get('lon')
            if not lgeo or not lat or not lon:
                continue
                
            page = 1
            has_more = True
            
            while has_more and page <= 5:  # 클러스터당 최대 5페이지(100개)만 수집
                for attempt in range(retries):
                    try:
                        self._random_delay(1.5, 3.5)
                        
                        list_url = "https://m.land.naver.com/cluster/ajax/articleList"
                        list_params = {
                            'itemId': lgeo,
                            'rletTpCd': 'A01',
                            'tradTpCd': 'A1:B1:B2',
                            'z': 12,
                            'lat': lat,
                            'lon': lon,
                            'btm': float(lat) - 0.1,
                            'lft': float(lon) - 0.1,
                            'top': float(lat) + 0.1,
                            'rgt': float(lon) + 0.1,
                            'page': page
                        }
                        
                        if self.session is None: self._reset_session()
                        
                        headers = self._get_mobile_headers()
                        
                        res = self.session.get(list_url, params=list_params, headers=headers, timeout=30) # type: ignore
                        
                        if res.status_code == 429:
                            self._wait_with_backoff(attempt)
                            self._reset_session()
                            continue
                            
                        res.raise_for_status()
                        list_data = res.json()
                        
                        items = list_data.get('body', [])
                        for item in items:
                            property_data = self._parse_property(item, region_code)
                            if property_data:
                                properties.append(property_data)
                        
                        has_more = list_data.get('more', False)
                        page += 1
                        break  # 성공 시 재시도 루프 탈출
                        
                    except Exception as e:
                        logger.error(f"매물 목록 수집 실패 (클러스터 {idx}, 페이지 {page}): {e}")
                        if attempt == retries - 1:
                            has_more = False
                            break
                        self._random_delay(3.0, 8.0)
                        self._reset_session()
        
        logger.info(f"총 {len(properties)}개 매물 수집 완료")
        
        # 중복 제거 (id 기준)
        unique_properties = {p['id']: p for p in properties}.values()
        return list(unique_properties)
    
    def _search_properties_selenium(self, region_code: str) -> List[Dict]:
        """Selenium을 사용한 매물 검색"""
        properties = []
        
        if not self.driver:
            logger.error("Selenium WebDriver가 초기화되지 않았습니다.")
            return []
            
        try:
            # 네이버 부동산 페이지 접속
            url = f"{self.BASE_URL}/articles?cortarNo={region_code}"
            self.driver.get(url)
            
            # 페이지 로딩 대기
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "list_item"))
            )
            
            # 매물 목록 파싱
            items = self.driver.find_elements(By.CLASS_NAME, "list_item")
            
            for item in items:
                try:
                    property_data = self._parse_property_selenium(item, region_code)
                    if property_data:
                        properties.append(property_data)
                except Exception as e:
                    logger.error(f"매물 파싱 실패: {e}")
                    continue
            
            logger.info(f"Selenium으로 매물 {len(properties)}개 검색됨")
            
        except Exception as e:
            logger.error(f"Selenium 매물 검색 실패: {e}")
        
        return properties
    
    def _parse_property(self, item: Dict, region_code: str) -> Optional[Dict]:
        """매물 데이터 파싱 (모바일 JSON 응답)"""
        try:
            # 가격 계산 (모바일 API의 경우 prc 필드가 정수로 직접 제공됨)
            price = item.get('prc')
            if price is None or price == 0:
                price = self._parse_price(item.get('prcInfo', item.get('dealPrice', 0)))
                
            return {
                'id': item.get('atclNo', item.get('articleNo', '')),
                'title': item.get('atclNm', item.get('articleName', '')),
                'location': item.get('address', ''), # 모바일 API에는 상세 주소가 없을 수 있음
                'price': price,
                'area': float(item.get('spc2', item.get('area', 0))),
                'description': item.get('atclFetrDesc', item.get('description', '')),
                'url': f"https://m.land.naver.com/article/info/{item.get('atclNo', item.get('articleNo', ''))}",
                'crawled_at': datetime.now().isoformat(),
                'region_code': region_code,
                'property_type': item.get('rletTpNm', item.get('realEstateType', '아파트')),
                'trade_type': item.get('tradTpNm', item.get('tradeType', '')),
                'floor': item.get('flrInfo', ''),
                'direction': item.get('direction', '')
            }
        except Exception as e:
            logger.error(f"매물 데이터 파싱 실패: {e}")
            return None
    
    def _parse_property_selenium(self, element, region_code: str) -> Optional[Dict]:
        """매물 데이터 파싱 (Selenium 요소)"""
        try:
            # 요소에서 데이터 추출
            title = element.find_element(By.CLASS_NAME, "item_name").text
            location = element.find_element(By.CLASS_NAME, "item_address").text
            price_text = element.find_element(By.CLASS_NAME, "price").text
            area_text = element.find_element(By.CLASS_NAME, "area").text
            
            # 가격 파싱
            price = self._parse_price(price_text)
            
            # 면적 파싱
            area = float(area_text.replace('㎡', '').strip())
            
            return {
                'id': element.get_attribute('data-article-no') or '',
                'title': title,
                'location': location,
                'price': price,
                'area': area,
                'description': '',
                'url': f"{self.BASE_URL}/articles/{element.get_attribute('data-article-no') or ''}",
                'crawled_at': datetime.now().isoformat(),
                'region_code': region_code,
            }
        except Exception as e:
            logger.error(f"Selenium 매물 파싱 실패: {e}")
            return None
    
    def _parse_price(self, price_input) -> int:
        """
        가격 파싱 공통 메서드
        
        지원 형식:
        - 숫자 (int, float): 즉시 반환
        - 문자열 ("10000", "1억", "1억 5000만")
        - "만원" 단위 제거
        
        Returns:
            가격 (만원 단위)
        """
        # 숫자인 경우 바로 반환
        if isinstance(price_input, (int, float)):
            return int(price_input)
        
        # 문자열 정리
        price_str = str(price_input).replace(',', '').replace(' ', '').replace('만원', '')
        
        try:
            # 억 단위 처리
            if '억' in price_str:
                parts = price_str.split('억')
                억 = int(parts[0]) * 10000 if parts[0] else 0
                만 = int(parts[1]) if len(parts) > 1 and parts[1] else 0
                return 억 + 만
            # 순수 숫자
            else:
                return int(price_str)
        except (ValueError, IndexError):
            logger.warning(f"가격 파싱 실패: {price_input}")
            return 0
    
    def close(self):
        """리소스 정리"""
        if self.driver:
            self.driver.quit()
        if self.session:
            self.session.close()
        logger.info("크롤러 종료")

# 사용 예시
if __name__ == "__main__":
    # requests만 사용
    crawler = NaverRealEstateCrawler(use_selenium=False)
    properties = crawler.search_region("강남구")
    print(f"검색된 매물 수: {len(properties)}")
    crawler.close()
    
    # Selenium 사용
    crawler_selenium = NaverRealEstateCrawler(use_selenium=True, headless=True)
    properties_selenium = crawler_selenium.search_region("마포구")
    print(f"Selenium 검색된 매물 수: {len(properties_selenium)}")
    crawler_selenium.close()