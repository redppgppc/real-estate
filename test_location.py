import requests
import json
import logging

def search_by_coord(lat, lon, max_price=200000):
    z = 16
    btm = lat - 0.015
    top = lat + 0.015
    lft = lon - 0.02
    rgt = lon + 0.02
    
    # 1. Get Clusters
    cluster_url = "https://m.land.naver.com/cluster/clusterList"
    cluster_params = {
        'view': 'atcl',
        'rletTpCd': 'A01', # Apartment
        'tradTpCd': 'A1',  # Trade (매매)
        'z': z,
        'lat': lat,
        'lon': lon,
        'btm': btm,
        'lft': lft,
        'top': top,
        'rgt': rgt,
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': 'https://m.land.naver.com/'
    }
    
    print(f"=== 위치 기반 아파트 매매 검색 ===")
    print(f"위도: {lat}, 경도: {lon}")
    print(f"조건: 아파트, 매매, 20억 미만\n")
    
    try:
        res = requests.get(cluster_url, params=cluster_params, headers=headers)
        data = res.json()
        clusters = data.get('data', {}).get('ARTICLE', [])
        
        if not clusters:
            print("해당 영역에 매물 클러스터가 없습니다.")
            return
            
        print(f"주변 매물 클러스터 {len(clusters)}개 발견. 데이터 수집 중...\n")
        
        all_properties = []
        
        for cluster in clusters[:10]: # 10개 클러스터 조회
            lgeo = cluster.get('lgeo')
            
            list_url = "https://m.land.naver.com/cluster/ajax/articleList"
            list_params = {
                'itemId': lgeo,
                'rletTpCd': 'A01',
                'tradTpCd': 'A1',
                'z': z,
                'lat': lat,
                'lon': lon,
                'btm': btm,
                'lft': lft,
                'top': top,
                'rgt': rgt,
            }
            
            article_res = requests.get(list_url, params=list_params, headers=headers)
            article_data = article_res.json()
            items = article_data.get('body', [])
            
            for item in items:
                prc = item.get('prc', 0)
                if prc > 0 and prc < max_price:
                    all_properties.append({
                        'id': item.get('atclNo'),
                        'title': item.get('atclNm'),
                        'type': item.get('rletTpNm'),
                        'trade_type': item.get('tradTpNm'),
                        'hanPrc': item.get('hanPrc'),
                        'price_num': prc,
                        'area': item.get('spc2'),
                        'floor': item.get('flrInfo'),
                        'direction': item.get('direction'),
                        'desc': item.get('atclFetrDesc', ''),
                    })
        
        # 중복 제거 (id 기준)
        unique_properties = {p['id']: p for p in all_properties}.values()
        sorted_properties = sorted(unique_properties, key=lambda x: x['price_num'])
        
        print(f"[검색 결과 요약] 20억 미만 매물 총 {len(sorted_properties)}개 발견 (가격 낮은 순 정렬)\n")
        print("-" * 80)
        
        for i, p in enumerate(sorted_properties[:15]): # 상위 15개 출력
            print(f"{i+1:2d}. 단지명: {p['title']}")
            print(f"    가  격: {p['trade_type']} {p['hanPrc']} ({p['price_num']}만원)")
            print(f"    면  적: 전용 {p['area']}㎡ | 층: {p['floor']} | 방향: {p['direction']}")
            print(f"    특  징: {p['desc']}")
            print("-" * 80)
            
    except Exception as e:
        print(f"크롤링 실패: {e}")

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    search_by_coord(37.5033, 127.1205, 200000)
