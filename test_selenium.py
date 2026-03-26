import logging
from crawler.naver_crawler import NaverRealEstateCrawler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_selenium():
    print("=== Selenium 테스트 시작 ===")
    crawler = NaverRealEstateCrawler(use_selenium=True, headless=True)
    try:
        properties = crawler._search_properties_selenium("1171010700") # Songpa-gu Garak-dong example region code
        if properties:
            print(f"성공: {len(properties)}개의 매물을 찾았습니다.")
            for i, p in enumerate(properties[:3]):
                print(f"  [{i+1}] {p['title']} - {p['price']}만원 ({p['location']})")
        else:
            print("실패: 매물을 찾지 못했습니다.")
    except Exception as e:
        print(f"오류: {e}")
    finally:
        crawler.close()

if __name__ == "__main__":
    test_selenium()
