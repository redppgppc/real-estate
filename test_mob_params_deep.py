import requests
import json
url = "https://m.land.naver.com/cluster/clusterList"
params = {
    'view': 'atcl',
    'cortarNo': '1168000000',
    'rletTpCd': 'A01',
    'tradTpCd': 'A1',
    'z': 12
}
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(url, params=params, headers=headers)
clusters = res.json().get('data', {}).get('ARTICLE', [])
print("Clusters:", len(clusters))

if clusters:
    # Get articles from first cluster
    lgeo = clusters[0].get('lgeo')
    list_url = "https://m.land.naver.com/cluster/ajax/articleList"
    list_params = {
        'itemId': lgeo,
        'rletTpCd': 'A01',
        'tradTpCd': 'A1',
        'z': 12
    }
    articles = requests.get(list_url, params=list_params, headers=headers).json().get('body', [])
    print("Articles in first cluster:", len(articles))
