"""
네이버 부동산 크롤링 서비스 FastAPI 애플리케이션

주요 기능:
- 네이버 부동산 매물 정보 크롤링
- 지도 기반 부동산 검색 서비스
- 다중 지역 검색 및 필터링
- 데이터 시각화 및 내보내기
- 사용자 친화적 인터페이스

기술 스택:
- Backend: FastAPI, Python 3.13
- Crawling: requests, Selenium, BeautifulSoup4
- Frontend: HTML5, CSS3, JavaScript, Leaflet.js, Chart.js
- Data: JSON 캐시, CSV/Excel 내보내기

보안 고려사항:
- CORS 설정을 통한 접근 제어
- 입력 데이터 검증 (Pydantic)
- 에러 핸들링 및 로깅
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.routers import api
from app.config import settings

# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="네이버 부동산 크롤링 서비스",
    description="네이버 부동산에서 부동산 정보를 크롤링하고 지도 기반으로 제공하는 서비스",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI 문서 경로
    redoc_url="/redoc"     # ReDoc 문서 경로
)

# CORS (Cross-Origin Resource Sharing) 미들웨어 설정
# 브라우저가 다른 도메인에서 리소스를 요청할 수 있도록 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # 허용할Origins 목록 (설정 파일에서 가져옴)
    allow_credentials=True,                  # 쿠키 등 자격 증명 허용
    allow_methods=["*"],                     # 모든 HTTP 메서드 허용
    allow_headers=["*"],                     # 모든 헤더 허용
)

# 정적 파일 설정 (CSS, JavaScript, 이미지 등)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# HTML 템플릿 설정 (Jinja2 템플릿 엔진)
templates = Jinja2Templates(directory="app/templates")

# API 라우터 포함
# 모든 API 엔드포인트는 /api/v1 접두사로 그룹화
app.include_router(api.router, prefix="/api/v1")

@app.get("/")
async def root(request: Request):
    """홈 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/search")
async def search_page(request: Request):
    """검색 페이지"""
    return templates.TemplateResponse("search.html", {"request": request})

@app.get("/guide")
async def guide_page(request: Request):
    """사용 방법 설명서 페이지"""
    return templates.TemplateResponse("guide.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "healthy"}