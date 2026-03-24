from crawler.naver_crawler import NaverRealEstateCrawler

try:
    crawler = NaverRealEstateCrawler(use_selenium=False)
    properties = crawler.search_region("강남구")
    print(f"Found {len(properties)} properties")
    if properties:
        for prop in properties[:3]:
            print(f" - {prop['title']}: {prop['price']}만원")
    crawler.close()
except Exception as e:
    print(f"Crawler error: {e}")
    import traceback
    traceback.print_exc()