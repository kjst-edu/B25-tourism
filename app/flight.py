import requests
import json

host = 'flights-sky.p.rapidapi.com/web/flights/detai'

url = "https://flights-sky.p.rapidapi.com/web/flights/search-one-way"
headers = {
    "X-RapidAPI-Key": "0cf250c0a9msh4b6d63cf748e07fp1cb7bcjsn5d4fa8bde963",
    "X-RapidAPI-Host": "flights-sky.p.rapidapi.com"
}
params = {
    
  "placeIdFrom": "KIX",
  "placeIdTo": "ICN",
  "departDate": "2025-12-10",
  "currency": "JPY"


}

response = requests.get(url, headers=headers, params=params)
data = response.json()

print(json.dumps(data, indent=2))
