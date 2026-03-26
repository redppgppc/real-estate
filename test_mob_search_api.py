import requests
import json
url = "https://m.land.naver.com/search/result"
params = {'query': '강남구'}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://m.land.naver.com/'
}
res = requests.get(url, params=params, headers=headers)
print(res.status_code)

import re
# check for anything looking like coordinates or cortarNo
cortar_no = re.search(r"filter: \{.*cortarNo:\s*'(\d+)'", res.text)
if cortar_no: print("cortarNo:", cortar_no.group(1))

lat = re.search(r"lat:\s*'([\d.]+)'", res.text)
if lat: print("lat:", lat.group(1))

lon = re.search(r"lon:\s*'([\d.]+)'", res.text)
if lon: print("lon:", lon.group(1))
