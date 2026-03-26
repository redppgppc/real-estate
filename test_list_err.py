import requests

list_url = "https://m.land.naver.com/cluster/ajax/articleList"
headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)'}
list_params = {
    'itemId': '212211101213', # From previous test
    'rletTpCd': 'A01',
    'tradTpCd': 'A1:B1:B2',
    'z': 12,
    'lat': 37.5109375,
    'lon': 127.11350098,
    'btm': 37.4,
    'lft': 127.0,
    'top': 37.6,
    'rgt': 127.2,
    'page': 1
}
res = requests.get(list_url, params=list_params, headers=headers)
print(res.status_code)
try:
    print(res.json().keys())
except:
    print(res.text[:200])
