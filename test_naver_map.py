import requests
import json
url = "https://map.naver.com/v5/api/search"
params = {'query': '강남구'}
headers = {'User-Agent': 'Mozilla/5.0'}
try:
    res = requests.get(url, params=params, headers=headers)
    print(res.status_code)
    print(res.text[:300])
except Exception as e:
    print(e)
