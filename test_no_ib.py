"""
1. aktualni price = last traded
2. pro spx live je potreba subscription (spy)

"""
from dataclasses import dataclass
import random
import time
import asyncio
from chart import LiveChart, PriceData
from discord_api import DiscordFeeder 
from ib_api import Tick
from ib_api import get_cboe_datetime
from typing import List, Dict
from datetime import datetime
# from ib_async import IB

# IB = ib_api.initialize_ib()



def manage_price_data(prices:list[PriceData], time_window:int = 900) -> list[PriceData]:
    current_time = time.time()
    # Remove Pricedata older than time_window
    prices = [data for data in prices if current_time - data.timestamp <= time_window]
    return prices

smart_entry_high:float = 0.0
smart_entry_low:float = 0.0
# ib: IB = initialize_ib()
last_tick:Tick = Tick(price=0.0, timestamp=0.0)
@dataclass
class PriceClass():
    timestamp: List[datetime]
    smart_entry_high: List[float]
    smart_entry_low: List[float]
    price: List[float]
prices: PriceClass = PriceClass(timestamp=[], smart_entry_high=[], smart_entry_low=[], price=[])


d:DiscordFeeder = DiscordFeeder()
chart: LiveChart = LiveChart(title="Smart entry", xlabel="Time", ylabel="Price")

try:
    while True:
        high, low = d.get_smart_entries()
        # new_tick = asyncio.run(get_live_spx_data(ib))
        if random.randint(0,10) == 7:
            new_tick:Tick = Tick(price=0.0, timestamp=get_cboe_datetime())  # placeholder for live data
        else:
            new_tick:Tick = prices[-1] if len(prices)>0 else Tick(price=0.0, timestamp=get_cboe_datetime())
        new_smart_data: bool = high and low
        new_price_data: bool = new_tick != last_tick
        
        if new_price_data or new_smart_data:
            last_high = prices.smart_entry_high[-1]
            last_low = prices.smart_entry_low[-1]

            prices.timestamp.append(new_tick.timestamp if new_price_data else get_cboe_datetime())
            prices.smart_entry_high.append(high if high is not None else prices.smart_entry_high[-1])
            prices.smart_entry_low.append(low if low is not None else prices.smart_entry_low[-1])
            prices.price.append(new_tick.price)

            chart.update(prices)


        if new_smart_data:
            smart_entry_high = high
            smart_entry_low = low
        if new_price_data:
            manage_price_data(prices)
            if len(prices) > 50:
                prices.pop(0)
        if len(prices) > 0:
            print(prices[-1])
            print(f"len: {len(prices)} time: {prices[-1].timestamp} price: {prices[-1].price:.2f}, smart_entry_high: {prices[-1].smart_entry_high:.2f}, smart_entry_low: {prices[-1].smart_entry_low:.2f}")
        last_tick = new_tick
        time.sleep(0.05)

except KeyboardInterrupt:
    print(smart_entry_low, smart_entry_high)
    print("Stopped monitoring.")
finally:
    print("Closing driver...")
    d.kill_chrome_processes()
