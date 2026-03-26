import requests
import json
url = "https://m.land.naver.com/cluster/clusterList"
params = {
    'view': 'atcl',
    'cortarNo': '1168000000',
    'rletTpCd': 'A01',
    'tradTpCd': 'A1',
    'z': 12
}
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(url, params=params, headers=headers)
print(res.status_code)
try:
    data = res.json()
    print("Clusters:", len(data.get('data', {}).get('ARTICLE', [])))
except Exception as e:
    print(res.text[:200])
