import urllib.request
from urllib.parse import quote
import re
query = '강남구'
url = f"https://m.land.naver.com/search/result/{quote(query)}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)'})
html = urllib.request.urlopen(req).read().decode('utf-8')
match = re.search(r"lat:\s*'([\d.]+)',\s*lon:\s*'([\d.]+)'", html)
if match:
    print(match.groups())
