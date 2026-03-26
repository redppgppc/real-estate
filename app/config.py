"""
애플리케이션 설정 모듈

환경 변수 및 애플리케이션 설정을 관리합니다.
.env 파일에서 환경 변수를 로드합니다.

사용법:
1. .env 파일을 프로젝트 루트에 생성
2. 필요한 환경 변수 설정
3. 설정 클래스를 통해 애플리케이션 설정에 접근
"""

import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

class Settings:
    """
    애플리케이션 설정 클래스
    
    환경 변수와 기본값을 관리합니다.
    모든 설정은 .env 파일에서 오버라이드할 수 있습니다.
    """
    
    # FastAPI 애플리케이션 기본 설정
    APP_NAME: str = "네이버 부동산 크롤링 서비스"  # 애플리케이션 이름
    APP_VERSION: str = "1.0.0"                     # 애플리케이션 버전
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"  # 디버그 모드 (기본값: False)
    
    # CORS (Cross-Origin Resource Sharing) 설정
    # 브라우저 보안 정책에 따라 다른 도메인에서의 요청을 제어
    ALLOWED_ORIGINS: list = ["*"]  # 모든 Origins 허용 (개발용), 프로덕션에서는 구체적으로 지정
    
    # 크롤링 설정
    CRAWLER_DELAY: int = int(os.getenv("CRAWLER_DELAY", "15"))    # 크롤링 지연 시간 (초), 429 오류 방지 (기본 15초로 상향)
    CRAWLER_TIMEOUT: int = int(os.getenv("CRAWLER_TIMEOUT", "30")) # HTTP 요청 타임아웃 (초)
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "5"))         # 최대 재시도 횟수 (기본 5회로 상향)
    
    # 데이터 저장소 설정
    DATA_DIR: str = "app/data"          # 내보내기 파일 저장 디렉토리
    CACHE_DIR: str = "app/data/cache"   # 캐시 파일 저장 디렉토리
    
    # 스케줄러 설정
    UPDATE_INTERVAL_HOURS: int = int(os.getenv("UPDATE_INTERVAL_HOURS", "24"))  # 데이터 업데이트 주기 (시간)

# 설정 인스턴스 생성 (싱글턴 패턴)
settings = Settings()