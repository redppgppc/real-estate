import requests
import json

url = "https://m.land.naver.com/cluster/clusterList"
params = {
    'view': 'atcl',
    'cortarNo': '1168000000', # Gangnam-gu
    'rletTpCd': 'A01',
    'tradTpCd': 'A1',
    'z': 12,
    'lat': 37.5172,
    'lon': 127.0473,
    'btm': 37.4,
    'lft': 126.9,
    'top': 37.6,
    'rgt': 127.1,
}
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(url, params=params, headers=headers)
print(res.status_code)
data = res.json()
print("Clusters:", len(data.get('data', {}).get('ARTICLE', [])))
