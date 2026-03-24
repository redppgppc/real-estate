from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
from typing import List, Optional
from pydantic import BaseModel
import os
from pathlib import Path

from app.services.crawler_service import crawler_service
from app.config import settings

# FastAPI 라우터 인스턴스 생성
router = APIRouter()

# Pydantic 모델 정의 (데이터 검증 및 직렬화)
class SearchRequest(BaseModel):
    """
    검색 요청 데이터 모델
    
    Attributes:
        locations: 검색할 지역 목록 (예: ["강남구", "마포구"])
        property_type: 매물 유형 (선택사항)
        price_min: 최소 가격 (만원 단위)
        price_max: 최대 가격 (만원 단위)
        area_min: 최소 면적 (㎡ 단위)
        area_max: 최대 면적 (㎡ 단위)
    """
    locations: List[str]  # 필수: 검색할 지역 목록
    property_type: Optional[str] = None  # 선택: 매물 유형
    price_min: Optional[int] = None  # 선택: 최소 가격
    price_max: Optional[int] = None  # 선택: 최대 가격
    area_min: Optional[int] = None  # 선택: 최소 면적
    area_max: Optional[int] = None  # 선택: 최대 면적

class PropertyResponse(BaseModel):
    """
    매물 응답 데이터 모델
    
    Attributes:
        id: 매물 고유 ID
        title: 매물 제목
        location: 매물 위치
        price: 매물 가격 (만원 단위)
        area: 매물 면적 (㎡ 단위)
        description: 매물 설명
        url: 매물 원문 URL
        crawled_at: 크롤링 시간 (ISO 형식)
    """
    id: str
    title: str
    location: str
    price: int
    area: float
    description: str
    url: str
    crawled_at: str

@router.get("/search")
async def search_properties(
    locations: List[str] = Query(..., description="검색할 지역 목록"),
    property_type: Optional[str] = Query(None, description="매물 유형"),
    price_min: Optional[int] = Query(None, description="최소 가격"),
    price_max: Optional[int] = Query(None, description="최대 가격"),
    area_min: Optional[int] = Query(None, description="최소 면적"),
    area_max: Optional[int] = Query(None, description="최대 면적")
):
    """부동산 검색 API"""
    try:
        filters = {
            'property_type': property_type,
            'price_min': price_min,
            'price_max': price_max,
            'area_min': area_min,
            'area_max': area_max
        }
        
        # None 값 제거
        filters = {k: v for k, v in filters.items() if v is not None}
        
        # 크롤링 서비스 호출
        properties = await crawler_service.search_properties(locations, filters)
        
        return {
            "status": "success",
            "count": len(properties),
            "properties": properties,
            "locations": locations,
            "filters": filters
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 실패: {str(e)}")

@router.get("/properties/{property_id}")
async def get_property(property_id: str):
    """개별 매물 상세 정보 API"""
    # 캐시된 데이터에서 매물 찾기
    cache_dir = Path(settings.CACHE_DIR)
    
    for cache_file in cache_dir.glob("*.json"):
        try:
            import json
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for property_data in data:
                    if property_data.get('id') == property_id:
                        return {
                            "status": "success",
                            "property": property_data
                        }
        except:
            continue
    
    raise HTTPException(status_code=404, detail="매물을 찾을 수 없습니다")

@router.get("/export")
async def export_data(
    format: str = Query("csv", description="내보내기 형식 (csv, excel)"),
    property_ids: List[str] = Query(..., description="내보낼 매물 ID 목록")
):
    """데이터 내보내기 API"""
    try:
        # 매물 데이터 수집
        properties = []
        cache_dir = Path(settings.CACHE_DIR)
        
        for cache_file in cache_dir.glob("*.json"):
            try:
                import json
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for property_data in data:
                        if property_data.get('id') in property_ids:
                            properties.append(property_data)
            except:
                continue
        
        if not properties:
            raise HTTPException(status_code=404, detail="내보낼 매물을 찾을 수 없습니다")
        
        # 파일 경로 생성
        if format.lower() == 'excel':
            file_path = await crawler_service.export_to_excel(properties)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:  # csv
            file_path = await crawler_service.export_to_csv(properties)
            media_type = "text/csv"
        
        # 파일명 추출
        filename = os.path.basename(file_path)
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type=media_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"내보내기 실패: {str(e)}")

@router.get("/stats")
async def get_statistics():
    """통계 정보 API"""
    try:
        stats = crawler_service.get_statistics()
        return {
            "status": "success",
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")

@router.post("/update")
async def update_data():
    """데이터 업데이트 API"""
    try:
        await crawler_service.update_all_locations()
        return {
            "status": "success",
            "message": "데이터 업데이트 완료"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"업데이트 실패: {str(e)}")