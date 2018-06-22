import gemini
import inspect
import numpy as np
import pandas as pd
import datetime
import time


r = gemini.PublicClient()

r.symbols()

r.get_ticker("BTCUSD")

r.get_current_order_book("BTCUSD")

# Will get the latest 500 trades
r.get_trade_history("BTCUSD")
# Alternatively, it can be specified for a specific date
r.get_trade_history("BTCUSD", since="17/06/2017")



# Will get the latest 500 auctions
r.get_auction_history("BTCUSD")
# Alternatively, it can be specified for a specific date
r.get_auction_history("BTCUSD", since="17/06/2017")