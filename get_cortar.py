import urllib.request
from urllib.parse import quote
import json

def get_region_code(query):
    url = f"https://m.land.naver.com/search/result/{quote(query)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'})
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
        # We need to find something like filter: { cortarNo: '1168000000' }
        import re
        match = re.search(r"cortarNo:\s*'(\d+)'", html)
        if match: return match.group(1)
        
        # let's find any json embedded
        match = re.search(r"var\s+filter\s*=\s*({.*?})", html, re.DOTALL)
        if match: print(match.group(1))
        
        # Or look for '1168000000'
        return "Not found"
    except Exception as e:
        return str(e)
print(get_region_code('강남구'))
