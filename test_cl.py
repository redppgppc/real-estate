import requests
url = "https://m.land.naver.com/cluster/clusterList"
params = {'view': 'atcl', 'cortarNo': '1168010600', 'rletTpCd': 'A01', 'tradTpCd': 'A1:B1:B2', 'z': 12}
res = requests.get(url, params=params, headers={'User-Agent': 'Mozilla/5.0 (iPhone;)'})
print(res.json().get('data', {}).get('ARTICLE', [])[:2])
