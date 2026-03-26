import requests
import json
url = "https://m.land.naver.com/cluster/clusterList"
params = {'view': 'atcl', 'cortarNo': '1168000000', 'rletTpCd': 'A01', 'tradTpCd': 'A1', 'z': 12}
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(url, params=params, headers=headers)
clusters = res.json().get('data', {}).get('ARTICLE', [])

if clusters:
    cluster = clusters[0]
    lgeo = cluster.get('lgeo')
    lat = cluster.get('lat')
    lon = cluster.get('lon')
    print("lat:", lat, "lon:", lon)
    
    list_url = "https://m.land.naver.com/cluster/ajax/articleList"
    list_params = {
        'itemId': lgeo,
        'rletTpCd': 'A01',
        'tradTpCd': 'A1',
        'z': 12,
        'lat': lat,
        'lon': lon,
        'btm': lat - 0.1,
        'lft': lon - 0.1,
        'top': lat + 0.1,
        'rgt': lon + 0.1,
    }
    articles = requests.get(list_url, params=list_params, headers=headers).json().get('body', [])
    print("Articles in first cluster:", len(articles))
