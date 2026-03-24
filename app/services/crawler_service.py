import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import os
from pathlib import Path

from crawler.naver_crawler import NaverRealEstateCrawler
from app.config import settings

class CrawlerService:
    """
    크롤링 서비스 클래스
    
    주요 기능:
    - 네이버 부동산 크롤링 수행
    - 캐시 시스템을 통한 데이터 관리
    - 더미 데이터 생성 (크롤링 실패 시 대체)
    - 데이터 내보내기 (CSV/Excel)
    - 통계 정보 제공
    
    아키텍처:
    - 크롤러 인스턴스를 통한 실제 데이터 수집
    - JSON 파일 기반 캐시 시스템
    - 비동기 처리를 통한 여러 지역 동시 검색
    - 필터링 시스템을 통한 데이터 정제
    """
    
    def __init__(self):
        """
        크롤링 서비스 초기화
        
        설정:
        - Selenium 사용 설정 (JavaScript 렌더링 필요)
        - 헤드리스 모드 (브라우저 창 숨김)
        - 디렉토리 생성 (데이터, 캐시)
        """
        # 네이버 부동산 크롤러 초기화
        self.crawler = NaverRealEstateCrawler(
            use_selenium=True,  # Selenium 사용 (JavaScript 렌더링 필요 시 True)
            headless=True       # 헤드리스 모드 (브라우저 창 숨김)
        )
        
        # 데이터 저장 디렉토리 설정
        self.data_dir = Path(settings.DATA_DIR)      # 내보내기 파일 저장 디렉토리
        self.cache_dir = Path(settings.CACHE_DIR)    # 캐시 파일 저장 디렉토리
        
        # 디렉토리 생성 (존재하지 않을 경우)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def search_properties(self, locations: List[str], filters: Dict = None) -> List[Dict]:
        """
        여러 지역의 부동산 검색
        
        Args:
            locations: 지역 목록
            filters: 검색 필터
            
        Returns:
            매물 목록
        """
        all_properties = []
        
        for location in locations:
            try:
                # 캐시 확인
                cached_data = self._load_from_cache(location)
                if cached_data:
                    all_properties.extend(cached_data)
                    continue
                
                # 크롤링 수행
                properties = await asyncio.to_thread(
                    self.crawler.search_region, location
                )
                
                # 크롤링 실패 시 더미 데이터 사용
                if not properties:
                    properties = self._generate_dummy_data(location)
                    print(f"크롤링 실패, 더미 데이터 사용: {location}")
                
                # 캐시 저장
                self._save_to_cache(location, properties)
                
                all_properties.extend(properties)
                
                # 크롤링 간격 조절
                await asyncio.sleep(settings.CRAWLER_DELAY)
                
            except Exception as e:
                print(f"지역 검색 실패 ({location}): {e}")
                continue
        
        # 필터 적용
        if filters:
            all_properties = self._apply_filters(all_properties, filters)
        
        return all_properties
    
    def _load_from_cache(self, location: str) -> Optional[List[Dict]]:
        """캐시에서 데이터 로드"""
        cache_file = self.cache_dir / f"{location}.json"
        
        if cache_file.exists():
            try:
                # 캐시 파일이 24시간 이내인지 확인
                file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if datetime.now() - file_time < timedelta(hours=settings.UPDATE_INTERVAL_HOURS):
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        print(f"캐시에서 데이터 로드: {location} ({len(data)}개)")
                        return data
            except Exception as e:
                print(f"캐시 로드 실패: {e}")
        
        return None
    
    def _save_to_cache(self, location: str, properties: List[Dict]):
        """데이터를 캐시에 저장"""
        cache_file = self.cache_dir / f"{location}.json"
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(properties, f, ensure_ascii=False, indent=2)
            print(f"캐시 저장: {location} ({len(properties)}개)")
        except Exception as e:
            print(f"캐시 저장 실패: {e}")
    
    def _apply_filters(self, properties: List[Dict], filters: Dict) -> List[Dict]:
        """필터 적용"""
        filtered = properties.copy()
        
        # 가격 필터
        price_min = filters.get('price_min')
        price_max = filters.get('price_max')
        
        if price_min is not None:
            filtered = [p for p in filtered if p['price'] >= price_min]
        if price_max is not None:
            filtered = [p for p in filtered if p['price'] <= price_max]
        
        # 면적 필터
        area_min = filters.get('area_min')
        area_max = filters.get('area_max')
        
        if area_min is not None:
            filtered = [p for p in filtered if p['area'] >= area_min]
        if area_max is not None:
            filtered = [p for p in filtered if p['area'] <= area_max]
        
        # 매물 유형 필터
        property_type = filters.get('property_type')
        if property_type:
            filtered = [p for p in filtered if p.get('property_type') == property_type]
        
        return filtered
    
    async def export_to_csv(self, properties: List[Dict], filename: str = None) -> str:
        """CSV로 내보내기"""
        if not filename:
            filename = f"부동산_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = self.data_dir / filename
        
        df = pd.DataFrame(properties)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return str(filepath)
    
    async def export_to_excel(self, properties: List[Dict], filename: str = None) -> str:
        """Excel로 내보내기"""
        if not filename:
            filename = f"부동산_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = self.data_dir / filename
        
        df = pd.DataFrame(properties)
        df.to_excel(filepath, index=False, engine='openpyxl')
        
        return str(filepath)
    
    async def update_all_locations(self):
        """모든 저장된 지역 업데이트"""
        # 캐시된 지역 목록 로드
        cache_files = list(self.cache_dir.glob("*.json"))
        
        for cache_file in cache_files:
            location = cache_file.stem
            print(f"업데이트 중: {location}")
            
            try:
                # 크롤링 수행
                properties = await asyncio.to_thread(
                    self.crawler.search_region, location
                )
                
                # 캐시 업데이트
                self._save_to_cache(location, properties)
                
                # 업데이트 지연
                await asyncio.sleep(settings.CRAWLER_DELAY)
                
            except Exception as e:
                print(f"업데이트 실패 ({location}): {e}")
    
    def get_statistics(self) -> Dict:
        """통계 정보 조회"""
        cache_files = list(self.cache_dir.glob("*.json"))
        
        total_properties = 0
        total_locations = len(cache_files)
        
        for cache_file in cache_files:
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    total_properties += len(data)
            except:
                pass
        
        return {
            'total_properties': total_properties,
            'total_locations': total_locations,
            'cache_files': len(cache_files),
            'last_update': datetime.now().isoformat()
        }
    
    def close(self):
        """서비스 종료"""
        self.crawler.close()
    
    def _generate_dummy_data(self, location: str) -> List[Dict]:
        """테스트용 더미 데이터 생성"""
        import random
        from datetime import datetime
        
        dummy_data = []
        property_types = ['아파트', '빌라', '주택', '오피스텔']
        for i in range(5):
            property_data = {
                'id': f'{location}_{i+1}',
                'title': f'{location} 더미 매물 {i+1}',
                'location': f'{location} 더미 지역 {i+1}',
                'price': random.randint(10000, 100000),
                'area': random.randint(50, 150),
                'description': f'{location} 지역의 테스트 매물입니다.',
                'url': f'https://example.com/{location}/{i+1}',
                'crawled_at': datetime.now().isoformat(),
                'property_type': random.choice(property_types),
                'trade_type': random.choice(['매매', '전세', '월세']),
            }
            dummy_data.append(property_data)
        
        return dummy_data

# 싱글턴 인스턴스
crawler_service = CrawlerService()