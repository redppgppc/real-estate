import requests
import json
headers = {'User-Agent': 'Mozilla/5.0'}
url = "https://m.land.naver.com/cluster/ajax/articleList"
params = {
    'itemId': '212211101213',
    'rletTpCd': 'A01',
    'tradTpCd': 'A1:B1:B2',
    'z': '16',
    'lat': '37.5109375',
    'lon': '127.11350098',
    'btm': '37.4933',
    'lft': '127.1105',
    'top': '37.5133',
    'rgt': '127.1305',
    'page': 2
}
res = requests.get(url, params=params, headers=headers)
data = res.json()
print("Articles:", len(data.get('body', [])))
print("More?", data.get('more', False))
