"""
1. aktualni price = last traded
2. pro spx live je potreba subscription (spy)

"""
import random
import time
import asyncio
from chart import LiveChart, PriceData
from discord_api import DiscordFeeder 
from ib_api import Tick
from ib_api import get_cboe_datetime

def manage_price_data(prices: PriceData, time_window:int = 900) -> list[PriceData]:
    """
    removes price data older than time_window in seconds"""
    for val in prices.timestamp[:]:
        diff = get_cboe_datetime() - val
        if diff.seconds > time_window:
            for i in [prices.timestamp, prices.smart_entry_high, prices.smart_entry_low, prices.price]:
                i.pop(0)
        else:
            continue

smart_entry_high:float = 0.0
smart_entry_low:float = 0.0
# ib: IB = initialize_ib()
last_tick:Tick = Tick(price=6485.6, timestamp=get_cboe_datetime())

prices: PriceData = PriceData(timestamp=[], smart_entry_high=[], smart_entry_low=[], price=[])
d:DiscordFeeder = DiscordFeeder()
chart: LiveChart = LiveChart(title="Smart entry", xlabel="Time", ylabel="Price")

try:
    while True:
        high, low = d.get_smart_entries()
        # new_tick = asyncio.run(get_live_spx_data(ib))
        if random.randint(0,10) == 7:
            new_tick:Tick = Tick(price=last_tick.price+random.randint(-100,100)/10, timestamp=get_cboe_datetime())  # placeholder for live data
        else:
            new_tick:Tick = last_tick
        new_smart_data: bool = high and low
        new_price_data: bool = new_tick != last_tick
        new_smart_data: bool = high and low
        new_price_data: bool = new_tick != last_tick

        if new_price_data or new_smart_data:
            last_high = prices.smart_entry_high[-1] if len(prices.smart_entry_high)>0 else None
            last_low = prices.smart_entry_low[-1] if len(prices.smart_entry_low)>0 else None

            prices.timestamp.append(new_tick.timestamp if new_price_data else get_cboe_datetime())
            prices.smart_entry_high.append(high if high is not None else last_high)
            prices.smart_entry_low.append(low if low is not None else last_low)
            prices.price.append(new_tick.price)

            chart.update(prices)


        if new_smart_data:
            smart_entry_high = high
            smart_entry_low = low
        manage_price_data(prices)
        last_tick = new_tick
        time.sleep(0.25)

except KeyboardInterrupt:
    print(smart_entry_low, smart_entry_high)
    print("Stopped monitoring.")
finally:
    print("Closing driver...")
    d.kill_chrome_processes()



