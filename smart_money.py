import ib_api
from discord_api import 
IB = ib_api.initialize_ib()
def trade_range(range_high, range_low):
    while(True):
        bars = ib_api.get_last_n_bars(IB,)
        current_price = bars['close'].iloc[-1]
        candles = ib_api.get_last_n_bars(IB, 'AAPL', 5, '1 min')
        if current_price >= range_high:
            pass
            #sell function
        elif current_price <= range_low:
            pass
            #buy function