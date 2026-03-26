import requests
import json

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
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://m.land.naver.com/',
}

response = requests.get(url, params=params, headers=headers)
print(response.status_code)
try:
    data = response.json()
    print("Success. Articles count:", len(data.get('body', [])))
    for item in data.get('body', [])[:3]:
        print(f"{item.get('atclNm')} - {item.get('prcInfo')} (ID: {item.get('atclNo')})")
except Exception as e:
    print("Failed:", response.text[:200])
