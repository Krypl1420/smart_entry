"""
1. aktualni price = last traded
2. pro spx live je potreba subscription (spy)

"""
import time
import asyncio
from chart import LiveChart, PriceData
from discord_api import DiscordFeeder 
from ib_api import Tick, get_cboe_datetime, initialize_ib, get_live_spx_data
from ib_async import IB



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

async def main():
    smart_entry_high: float = 0.0
    smart_entry_low: float = 0.0
    ib: IB = initialize_ib()
    last_tick: Tick = None

    prices: PriceData = PriceData(timestamp=[], smart_entry_high=[], smart_entry_low=[], price=[])
    d: DiscordFeeder = DiscordFeeder()
    chart: LiveChart = LiveChart(title="Smart entry", xlabel="Time", ylabel="Price")

    try:
        while True:
            # Run Discord and IB data fetching concurrently
            high_low, new_tick = await asyncio.gather(
                d.get_smart_entries_async(),  # You'll need to add this method to DiscordFeeder
                get_live_spx_data(ib)
            )
            
            high, low = high_low if high_low else (None, None)
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
            await asyncio.sleep(0.05)

    except KeyboardInterrupt:
        print(f"Smart Entry Levels - Low: {smart_entry_low}, High: {smart_entry_high}")
        print("Stopped monitoring.")
    finally:
        print("Cleaning up...")
        await ib.disconnect()
        d.kill_chrome_processes()

