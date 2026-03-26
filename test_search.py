import requests
import json
url = "https://new.land.naver.com/api/search"
params = {'keyword': '강남구', 'page': 1}
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(url, params=params, headers=headers)
print(json.dumps(res.json(), indent=2, ensure_ascii=False))
