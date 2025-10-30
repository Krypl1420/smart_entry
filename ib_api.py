from datetime import datetime, timezone
from ib_async import IB, Index, util, Ticker 
import asyncio
from dataclasses import dataclass
import time


@dataclass
class Tick:
    price: float
    timestamp: datetime

def initialize_ib(host="127.0.0.1", port=7497, clientId=1) -> IB:
    """
    Connect to Interactive Brokers TWS or Gateway and return IB instance.
    
    Args:
        host (str): TWS/Gateway host (usually 127.0.0.1).
        port (int): Port (default 7497 for TWS, 4002 for Gateway).
        clientId (int): Unique client ID for this session.
    
    Returns:
        IB: Connected IB instance.
    """
    ib = IB()
    ib.connect(host, port, clientId=clientId)
    return ib

def get_last_n_bars(ib: IB, contract, n=50, bar_size="1 min", what_to_show="TRADES", useRTH=True):
    """
    Fetch last n bars for a given contract from IB.
    """
    bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr="1 D",          # always fetch 1 day, safe for intraday
        barSizeSetting=bar_size,
        whatToShow=what_to_show,
        useRTH=useRTH,
        formatDate=1
    )
    df = util.df(bars)
    return df.tail(n)

async def get_live_spx_data(
    ib: IB,
    symbol: str = "SPY",
    exchange: str = "CBOE",
    currency: str = "USD",
    delay: float = 0.1
) -> Tick:
    """
    Fetch live SPX data with reliable timestamping.
    Prioritizes exchange-provided timestamp, falls back to system UTC time.
    """
    spy = Index(symbol, exchange, currency)
    ib.qualifyContracts(spy)
    ib.reqMktData(spy)

    await asyncio.sleep(delay)  # allow IB to stream data

    ticker: Ticker = ib.ticker(spy)
    price = ticker.last or ticker.close or None

    if price is None:
        raise ValueError("No valid price data received")

    # Prefer exchange timestamp if available
    if not ticker.time:
        timestamp = datetime.now(timezone.utc)

    return Tick(price=price, timestamp=timestamp)

if __name__ == "__main__":
    ib = initialize_ib()
    try:
        while True:
            print(get_live_spx_data(ib))
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")