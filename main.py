"""
1. aktualni price = last traded
2. pro spx live je potreba subscription (spy)

"""

import time
from datetime import datetime, timezone
from dataclasses import dataclass
import time
import asyncio
from chart import LiveChart
from discord_api import DiscordFeeder 
from ib_api import initialize_ib, get_live_spx_data, Tick
from ib_async import IB
# IB = ib_api.initialize_ib()



def manage_ticks(prices:list[Tick], time_window:int = 900) -> list[Tick]:
    current_time = time.time()
    # Remove ticks older than time_window
    prices = [tick for tick in prices if current_time - tick.timestamp <= time_window]
    return prices

smart_entry_high:float
smart_entry_low:float
ib: IB = initialize_ib()
last_tick:Tick = Tick(price=0.0, timestamp=0.0)
prices: list[Tick] = []


d:DiscordFeeder = DiscordFeeder()
chart: LiveChart = LiveChart(title="Smart entry", xlabel="Time", ylabel="Price")
try:
    while True:
        high, low = d.get_smart_entries()
        if high and low:
            smart_entry_high = high
            smart_entry_low = low
            print(f"Smart Entry High: {smart_entry_high:.2f}, Low: {smart_entry_low:.2f}")
        current_tick = asyncio.run(get_live_spx_data(ib))
        if current_tick != last_tick:
            manage_ticks(prices)
            prices.append(Tick(price=current_tick, ))
            if len(prices) > 50:
                prices.pop(0)
        print(f"SPX Current: {current_tick:.2f}, Smart Entry High: {smart_entry_high:.2f}, Low: {smart_entry_low:.2f}")
        chart.update()
        time.sleep(0.05)

except KeyboardInterrupt:
    print(smart_entry_low, smart_entry_high)
    print("Stopped monitoring.")
finally:
    print("Closing driver...")
    d.kill_chrome_processes()
