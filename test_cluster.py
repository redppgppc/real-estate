import requests
import json

lat = 37.5033
lon = 127.1205
zoom = 16

# Calculate approximate bounding box
btm = lat - 0.01
top = lat + 0.01
lft = lon - 0.01
rgt = lon + 0.01

url = f"https://m.land.naver.com/cluster/clusterList"
params = {
    'view': 'atcl',
    'cortarNo': '1171000000', # Songpa-gu as default if needed, or omit
    'rletTpCd': 'A01', # Apartment
    'tradTpCd': 'A1:B1:B2', # Trade types
    'z': zoom,
    'lat': lat,
    'lon': lon,
    'btm': btm,
    'lft': lft,
    'top': top,
    'rgt': rgt,
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://m.land.naver.com/map/37.5033:127.1205:16:1171000000/A01/A1:B1:B2',
}

response = requests.get(url, params=params, headers=headers)
print(response.status_code)
try:
    data = response.json()
    print("Success:", json.dumps(data)[:200])
except Exception as e:
    print("Failed:", response.text[:200])
