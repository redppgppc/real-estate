import requests
import json
url = "https://m.land.naver.com/search/result/강남구"
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(url, headers=headers)
print(res.status_code)
# Search inside HTML for lat, lon or cortarNo
import re
print(re.findall(r"cortarNo':'(\d+)'", res.text)[:1])
print(re.findall(r"lat':'([\d.]+)'", res.text)[:1])
print(re.findall(r"lon':'([\d.]+)'", res.text)[:1])
