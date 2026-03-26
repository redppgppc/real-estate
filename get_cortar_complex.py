import urllib.request
from urllib.parse import quote
import re
query = '은마아파트'
url = f"https://m.land.naver.com/search/result/{quote(query)}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)'})
html = urllib.request.urlopen(req).read().decode('utf-8')
print("hscpNo:", re.findall(r"hscpNo\s*[:=]\s*['\"](\d+)['\"]", html))
print("lat:", re.findall(r"lat\s*[:=]\s*['\"]([\d.]+)['\"]", html))
print("lon:", re.findall(r"lon\s*[:=]\s*['\"]([\d.]+)['\"]", html))
print("cortarNo:", re.findall(r"cortarNo\s*[:=]\s*['\"](\d+)['\"]", html))
