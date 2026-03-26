import requests
url = "https://m.land.naver.com/search/autocomplete.json"
params = {'query': '강남구'}
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(url, params=params, headers=headers)
print(res.status_code)
print(res.text[:300])
