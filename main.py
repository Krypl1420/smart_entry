"""
1. aktualni price = last traded
2. pro spx live je potreba subscription (spy)

"""
import asyncio
from chart import LiveChart, PriceData
from discord_api import DiscordFeeder 
from ib_api import Tick, IBClient
from ui import Loading

def manage_price_data(prices: PriceData, time_window:int = 900) -> list[PriceData]:
    """
    removes price data older than time_window in seconds
    """
    if len(prices.timestamp) < 10:
        return
    for val in prices.timestamp[:]:
        diff = prices.timestamp[-1] - val
        if diff.seconds > time_window:
            for i in [prices.timestamp, prices.smart_entry_high, prices.smart_entry_low, prices.price]:
                i.pop(0)
        else:
            continue

async def manage_orders(price:PriceData, ib:IBClient, quantity: int = 1) -> None:
    if price.smart_entry_high[-1] is None or price.smart_entry_low[-1] is None:
        raise ValueError("last smart entry is None")

    if price.price[-1] > price.smart_entry_high[-1]:
        return await ib.trade_mes("BUY",quantity)
    elif price.price[-1] < price.smart_entry_low[-1]:
        return await ib.trade_mes("SELL",quantity)
    
    return

async def main():
    ib: IBClient = IBClient()
    try:
        await ib.connect()
    except ConnectionRefusedError:
        print('Nepodařilo se pripojit, ujisti se ze je zapnuta TWS a v nastavení api je zaskrtnuto "enable activeX and socket client" a vypnut "read only api"')
        exit()
        
    
    last_tick: Tick = Tick(None,None)

    prices: PriceData = PriceData(timestamp=[], smart_entry_high=[], smart_entry_low=[], price=[])
    d: DiscordFeeder = DiscordFeeder()
    chart: LiveChart = LiveChart(title="Smart entry", xlabel="Time", ylabel="Price")
    has_entry_data:bool = False
    loading = Loading("Čekám na smart entry data: ")
    trade_since_new_data:bool = False
    try:
        while True:
            high_low, new_tick = await asyncio.gather(
                d.get_smart_entries_async(),  
                ib.get_latest_tick_mes()
            )
            
            high, low = high_low
            if high == 0 and low == 0:
                high, low = None, None
            new_smart_data: bool = high and low
            new_price_data: bool = new_tick != last_tick

            if new_smart_data:
                trade_since_new_data = False

            if new_price_data or new_smart_data:#new data
                last_high = prices.smart_entry_high[-1] if len(prices.smart_entry_high) > 0 else None
                last_low = prices.smart_entry_low[-1] if len(prices.smart_entry_low) > 0 else None
                prices.timestamp.append(new_tick.timestamp)
                prices.smart_entry_high.append(high if high is not None else last_high)
                prices.smart_entry_low.append(low if low is not None else last_low)
                prices.price.append(new_tick.price)


                if not has_entry_data:
                    loading.update()
                    if new_smart_data:
                        loading.end("\nData nalezeny")
                        del loading
                        has_entry_data = True
                elif not trade_since_new_data:
                    trade = await manage_orders(prices,ib)
                    if trade:
                        trade_since_new_data = True
                chart.update(prices)
 
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
        await ib.disconnect()
        d.kill_chrome_processes()

asyncio.run(main())