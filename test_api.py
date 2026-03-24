import requests
import json

try:
    response = requests.get('http://localhost:8000/api/v1/search', params={
        'locations': ['강남구', '마포구']
    })
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")