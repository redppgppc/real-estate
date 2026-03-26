import requests
import json
url = "https://new.land.naver.com/api/search"
params = {'keyword': '강남구'}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://new.land.naver.com/complexes'
}
res = requests.get(url, params=params, headers=headers)
print(res.status_code)
if res.status_code == 200:
    print(json.dumps(res.json(), indent=2, ensure_ascii=False)[:300])
else:
    print(res.text)
