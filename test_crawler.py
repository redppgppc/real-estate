import logging
from crawler.naver_crawler import NaverRealEstateCrawler

logging.basicConfig(level=logging.INFO)

def test():
    crawler = NaverRealEstateCrawler()
    print("Searching for '대치동'...")
    properties = crawler.search_region("대치동")
    print(f"Found {len(properties)} properties!")
    for p in properties[:5]:
        print(f"[{p['trade_type']}] {p['title']} - {p['price']}만원 ({p['area']}㎡)")
    crawler.close()

if __name__ == "__main__":
    test()
