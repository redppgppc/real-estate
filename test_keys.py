import requests
import json

lat, lon = 37.5033, 127.1205
cluster_url = "https://m.land.naver.com/cluster/clusterList"
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(cluster_url, params={'view':'atcl','rletTpCd':'A01','tradTpCd':'A1','z':16,'lat':lat,'lon':lon,'btm':lat-0.015,'lft':lon-0.02,'top':lat+0.015,'rgt':lon+0.02}, headers=headers).json()
lgeo = res.get('data', {}).get('ARTICLE', [])[0].get('lgeo')
articles = requests.get("https://m.land.naver.com/cluster/ajax/articleList", params={'itemId':lgeo,'rletTpCd':'A01','tradTpCd':'A1','z':16,'lat':lat,'lon':lon,'btm':lat-0.015,'lft':lon-0.02,'top':lat+0.015,'rgt':lon+0.02}, headers=headers).json().get('body', [])
if articles:
    print(json.dumps(articles[0], indent=2, ensure_ascii=False))
