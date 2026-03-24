from crawler.naver_crawler import NaverRealEstateCrawler

try:
    print("Testing with Selenium...")
    crawler = NaverRealEstateCrawler(use_selenium=True, headless=True)
    print("Crawler initialized")
    
    properties = crawler.search_region("강남구")
    print(f"Found {len(properties)} properties")
    
    if properties:
        for prop in properties[:3]:
            print(f" - {prop['title']}: {prop['price']}만원")
    else:
        print("No properties found")
    
    crawler.close()
    print("Crawler closed")
except Exception as e:
    print(f"Crawler error: {e}")
    import traceback
    traceback.print_exc()