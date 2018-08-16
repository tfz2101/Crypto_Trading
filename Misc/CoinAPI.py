import requests

url = 'https://rest.coinapi.io/v1/trades/BITSTAMP_SPOT_BTC_USD/history?time_start=2018-07-15T00:00:00'
headers = {'X-CoinAPI-Key' : '7C973F6B-9E95-49DA-8E9E-55F35FC3092F'}
response = requests.get(url, headers=headers)

print(response)

