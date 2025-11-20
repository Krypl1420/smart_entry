"""
1. aktualni price = last traded
2. pro spx live je potreba subscription (spy)

"""
import asyncio
from chart import LiveChart, PriceData
from discord_api import DiscordFeeder 
from ib_api import Tick, IBClient, Timer
from ui import Loading
from typing import List
from datetime import datetime
from ib_async import Trade
  
async def main():
    async def _wait_for_entry_data(prices: PriceData, d:DiscordFeeder, ib: IBClient, loading:Loading, chart: LiveChart) -> None:
        last_tick: Tick = Tick(None,None)
        while True:
            loading.update()
            high_low, new_tick = await asyncio.gather(
            d.get_smart_entries_async(),  
            ib.get_latest_tick_mes()
            )
            if high_low != (None,None):
                loading.end("Data nalezeny")
                del loading
                break
            if new_tick != last_tick:
                last_tick = new_tick
                prices.timestamp.append(new_tick.timestamp)
                prices.price.append(new_tick.price)
                prices.smart_entry_high.append(None)
                prices.smart_entry_low.append(None)
                chart.update(prices)

            await asyncio.sleep(0.1)
        return None
    
    def _manage_price_data(prices: PriceData, time_window:int = 900) -> None:
        """
        removes price data older than time_window in seconds
        """
        if len(prices.timestamp) < 10:
            return None
        for val in prices.timestamp[:]:
            diff = prices.timestamp[-1] - val
            if diff.seconds > time_window:
                li: List[List[datetime]|List[float]] = [prices.timestamp, prices.smart_entry_high, prices.smart_entry_low, prices.price]
                for i in li:
                    i.pop(0)
            else:
                continue
        return None

    async def _manage_orders(price:PriceData, ib:IBClient, quantity: int = 1) -> Trade|None:
        if price.smart_entry_high[-1] is None or price.smart_entry_low[-1] is None:
            raise ValueError("last smart entry is None")

        if price.price[-1] > price.smart_entry_high[-1]:
            return await ib.trade_mes("BUY",quantity)
        elif price.price[-1] < price.smart_entry_low[-1]:
            return await ib.trade_mes("SELL",quantity)
        else:
            price
        return None
    

    ib: IBClient = IBClient()
    try:
        print("Připojuji se k IB...")
        await ib.connect()
        print("Připojeno.")
    except ConnectionRefusedError:
        print('Nepodařilo se pripojit, ujisti se ze je zapnuta TWS a v nastavení api je zaskrtnuto "enable activeX and socket client" a vypnut "read only api"')
        exit()
    last_tick: Tick = Tick(None,None)
    prices: PriceData = PriceData(timestamp=[], smart_entry_high=[], smart_entry_low=[], price=[])
    d: DiscordFeeder = DiscordFeeder()
    chart: LiveChart = LiveChart(prices,title="Smart entry", xlabel="Time", ylabel="Price")
    loading = Loading("Čekám na smart entry data: ")
    current_timer: Timer = Timer("next_5m_close")

    try:
        await _wait_for_entry_data(prices, d, ib, loading, chart)
        while True:
            new_tick = await ib.get_latest_tick_mes()
            new_price_data: bool = new_tick != last_tick

            if new_price_data: # update prices
                prices.append(new_tick.timestamp, prices.smart_entry_high[-1], prices.smart_entry_low[-1], new_tick.price)

            if current_timer.check():
                await _manage_orders(prices, ib, quantity=1)
                current_timer = Timer("next_5m_close")

            _manage_price_data(prices)
            last_tick = new_tick
            chart.update()
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