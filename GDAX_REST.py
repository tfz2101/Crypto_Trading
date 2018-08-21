import requests

url = 'https://api.pro.coinbase.com/products/BTC-USD/book'
headers = {'X-CoinAPI-Key' : '7C973F6B-9E95-49DA-8E9E-55F35FC3092F', 'Accept' : 'application/json'}
response = requests.get(url)
print(response.json())