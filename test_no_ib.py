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

def manage_price_data(prices: PriceData, time_window:int = 90) -> list[PriceData]:
    """
    removes price data older than time_window in seconds"""
    for val in prices.timestamp[:]:
        diff = get_cboe_datetime() - val
        if diff.seconds > time_window:
            for i in [prices.timestamp, prices.smart_entry_high, prices.smart_entry_low, prices.price]:
                i.pop(0)
        else:
            continue

async def ib_data_sim(last_tick: Tick) -> Tick:
    """Simulated IB tick generator. Always returns a Tick (creates an initial tick if needed)."""
    await asyncio.sleep(0.1)
    if last_tick is None:
        # initial tick
        return Tick(price=random.randint(1000,2000)/10, timestamp=get_cboe_datetime())
    # occasionally change price
    if random.randint(0,4) == 1:
        return Tick(price=last_tick.price + random.randint(-100,100)/10, timestamp=get_cboe_datetime())
    # otherwise return same tick object (no update)
    return last_tick

async def main():
    smart_entry_high: float = 0.0
    smart_entry_low: float = 0.0
    # ib: IB = initialize_ib()
    last_tick: Tick = Tick(get_cboe_datetime(),6600.0)

    prices: PriceData = PriceData(timestamp=[], smart_entry_high=[], smart_entry_low=[], price=[])
    d: DiscordFeeder = DiscordFeeder()
    chart: LiveChart = LiveChart(title="Smart entry", xlabel="Time", ylabel="Price")

    try:
        while True:
            # Run Discord and IB data fetching concurrently
            high_low, new_tick = await asyncio.gather(
                d.get_smart_entries_async(),  # You'll need to add this method to DiscordFeeder
                ib_data_sim(last_tick)
                # get_live_spx_data(ib)

            )
            
            high, low = high_low
            if high == 0 and low == 0:
                high, low = None, None
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
            chart.chart_pause()
            await asyncio.sleep(0.05)

    except (KeyboardInterrupt, asyncio.CancelledError):
        # 🔹 Cancel all other running tasks except this one
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    finally:
        print("Cleaning up...")
        d.kill_chrome_processes()

asyncio.run(main())