import requests
import json

lat, lon = 37.5033, 127.1205
cluster_url = "https://m.land.naver.com/cluster/clusterList"
cluster_params = {
    'view': 'atcl',
    'rletTpCd': 'A01',
    'tradTpCd': 'A1',
    'z': 16,
    'lat': lat,
    'lon': lon,
    'btm': lat - 0.015,
    'lft': lon - 0.02,
    'top': lat + 0.015,
    'rgt': lon + 0.02,
}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
res = requests.get(cluster_url, params=cluster_params, headers=headers).json()
clusters = res.get('data', {}).get('ARTICLE', [])
print("Clusters:", len(clusters))

if clusters:
    lgeo = clusters[0].get('lgeo')
    list_url = "https://m.land.naver.com/cluster/ajax/articleList"
    list_params = {
        'itemId': lgeo,
        'rletTpCd': 'A01',
        'tradTpCd': 'A1',
        'z': 16,
        'lat': lat,
        'lon': lon,
        'btm': lat - 0.015,
        'lft': lon - 0.02,
        'top': lat + 0.015,
        'rgt': lon + 0.02,
    }
    articles = requests.get(list_url, params=list_params, headers=headers).json().get('body', [])
    print("Articles in first cluster:", len(articles))
    for a in articles[:3]:
        print(a.get('atclNm'), a.get('prcInfo'), a.get('tradTpNm'), a.get('flrInfo'))
