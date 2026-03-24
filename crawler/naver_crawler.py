import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
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
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',  # Chrome 120
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',  # Chrome 119
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',  # Mac Chrome
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',  # Firefox 121
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',  # Safari 17
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
        self.session = requests.Session()
        
        # 랜덤 User-Agent 선택
        user_agent = random.choice(self.USER_AGENTS)
        
        # 요청 헤더 설정
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://new.land.naver.com/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        if use_selenium:
            self._init_selenium(headless)
    
    def _random_delay(self, min_seconds: float = 3.0, max_seconds: float = 10.0):
        """랜덤 지연 시간 (요청 간격 조절)"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def _rotate_user_agent(self):
        """User-Agent 변경"""
        user_agent = random.choice(self.USER_AGENTS)
        self.session.headers.update({'User-Agent': user_agent})
        logger.info(f"User-Agent 변경: {user_agent[:50]}...")
    
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
    
    def _get_region_code(self, region_name: str, max_retries: int = 3) -> Optional[str]:
        """지역 코드 조회 (네이버 API 사용)"""
        for attempt in range(max_retries):
            try:
                # 랜덤 지연 시간 추가
                if attempt > 0:
                    self._random_delay(5.0, 15.0)
                    self._rotate_user_agent()
                
                # 지역 검색 API 호출
                url = f"{self.API_URL}/search"
                params = {
                    'keyword': region_name,
                    'page': 1
                }
                
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                # 지역 코드 파싱
                if 'result' in data and 'regionList' in data['result']:
                    regions = data['result']['regionList']
                    if regions:
                        return regions[0].get('regionCode')
                
                return None
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"지역 코드 조회 시도 {attempt + 1}/{max_retries} 실패: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"지역 코드 조회 최종 실패: {region_name}")
                    return None
                continue
        
        return None
    
    def _search_properties(self, region_code: str, max_retries: int = 2) -> List[Dict]:
        """매물 검색"""
        properties = []
        
        for attempt in range(max_retries):
            try:
                # 랜덤 지연 시간 추가
                if attempt > 0:
                    self._random_delay(8.0, 20.0)
                    self._rotate_user_agent()
                
                # 매물 목록 API 호출
                url = f"{self.API_URL}/articles"
                params = {
                    'regionCode': region_code,
                    'type': 'A1',  # 아파트
                    'order': 'rank',
                    'page': 1,
                    'limit': 20
                }
                
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                # 매물 파싱
                if 'result' in data and 'list' in data['result']:
                    for item in data['result']['list']:
                        property_data = self._parse_property(item, region_code)
                        if property_data:
                            properties.append(property_data)
                
                logger.info(f"매물 {len(properties)}개 검색됨")
                break  # 성공하면 루프 탈출
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    logger.warning(f"429 Too Many Requests - 시도 {attempt + 1}/{max_retries}")
                    if attempt == max_retries - 1:
                        logger.error("매물 검색 최종 실패 (429)")
                        break
                else:
                    logger.error(f"매물 검색 HTTP 오류: {e}")
                    break
            except Exception as e:
                logger.error(f"매물 검색 실패: {e}")
                break
        
        # 매물이 없으면 Selenium으로 재시도
        if not properties and self.use_selenium and self.driver:
            logger.info("Selenium으로 재시도...")
            properties = self._search_properties_selenium(region_code)
        
        return properties
    
    def _search_properties_selenium(self, region_code: str) -> List[Dict]:
        """Selenium을 사용한 매물 검색"""
        properties = []
        
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
        """매물 데이터 파싱 (JSON 응답)"""
        try:
            return {
                'id': item.get('articleNo', ''),
                'title': item.get('articleName', ''),
                'location': item.get('address', ''),
                'price': self._parse_price(item.get('dealPrice', 0)),
                'area': float(item.get('area', 0)),
                'description': item.get('description', ''),
                'url': f"{self.BASE_URL}/articles/{item.get('articleNo', '')}",
                'crawled_at': datetime.now().isoformat(),
                'region_code': region_code,
                'property_type': item.get('realEstateType', ''),
                'trade_type': item.get('tradeType', ''),
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