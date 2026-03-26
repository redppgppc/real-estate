import urllib.request
from urllib.parse import quote
import re

query = '은마아파트'
url = f"https://m.land.naver.com/search/result/{quote(query)}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)'})
html = urllib.request.urlopen(req).read().decode('utf-8')
for match in re.finditer(r"cortarNo\s*[:=]\s*['\"](\d+)['\"]", html):
    print(match.group(0))
