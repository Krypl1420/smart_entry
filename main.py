"""
1. aktualni price = last traded
2. pro spx live je potreba subscription (spy)

"""

import time
from datetime import datetime, timezone
import time
import asyncio
from chart import LiveChart, PriceData
from discord_api import DiscordFeeder 
from ib_api import initialize_ib, get_live_spx_data, get_cboe_datetime, Tick
from ib_async import IB
from typing import List, Dict, TypedDict
# IB = ib_api.initialize_ib()



smart_entry_high:float
smart_entry_low:float
ib: IB = initialize_ib()
last_tick:Tick = Tick(price=0.0, timestamp=0.0)
class PriceType(TypedDict):
    timestamp: List[datetime]
    smart_entry_high: List[float]
    smart_entry_low: List[float]
    price: List[float]

prices: PriceType = {"timestamp": [], "smart_entry_high": [], "smart_entry_low": [], "price": []}


d:DiscordFeeder = DiscordFeeder()
chart: LiveChart = LiveChart(title="Smart entry", xlabel="Time", ylabel="Price")

try:
    while True:
        high, low = d.get_smart_entries()
        new_tick = asyncio.run(get_live_spx_data(ib))

        new_smart_data: bool = high and low
        new_price_data: bool = new_tick != last_tick
        
        if new_price_data or new_smart_data:
            last_high = prices["smart_entry_high"][-1]
            last_low = prices["smart_entry_low"][-1]

            new_price = PriceData(
                timestamp=new_tick.timestamp if new_price_data else get_cboe_datetime(),
                price=new_tick.price,
                smart_entry_low=low or last_low,
                smart_entry_high=high or last_high
            )


        if new_smart_data:
            smart_entry_high = high
            smart_entry_low = low
            print(f"Smart Entry High: {smart_entry_high:.2f}, Low: {smart_entry_low:.2f}")
        if new_price_data:
            manage_ticks(prices)
            prices.append(new_tick)
            if len(prices) > 50:
                prices.pop(0)
        print(f"SPX Current: {new_tick:.2f}, Smart Entry High: {smart_entry_high:.2f}, Low: {smart_entry_low:.2f}")
        chart.update()
        time.sleep(0.05)

except KeyboardInterrupt:
    print(smart_entry_low, smart_entry_high)
    print("Stopped monitoring.")
finally:
    print("Closing driver...")
    d.kill_chrome_processes()
