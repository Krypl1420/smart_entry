from datetime import datetime, timedelta, timezone
from ib_async import IB, Ticker, Future, MarketOrder, Trade, Contract
import asyncio
from dataclasses import dataclass
from zoneinfo import ZoneInfo
from typing import Literal
import time
import math

TESTING = True
if TESTING:
    from random import randint
    def get_cboe_datetime() -> datetime:
        """Return the current datetime in Cboe (Chicago) timezone."""
        return datetime.now(ZoneInfo("America/Chicago"))

@dataclass
class Tick:
    timestamp: datetime
    price: float



def seconds_until_next_5m(dt: datetime | None = None) -> float:
    dt = dt or datetime.now(timezone.utc)
    stripped = dt.replace(second=0, microsecond=0)
    minute_mod = stripped.minute % 5
    next_close = stripped - timedelta(minutes=minute_mod) + timedelta(minutes=5)
    return float((next_close - dt).total_seconds())


class Timer:
    def __init__(self, length:float|Literal["next_5m_close"]) -> None:
        """returns a timer that checks if length seconds have passed since creation."""
        self.start_time: float = time.time()
        self.length:float = seconds_until_next_5m() if length == "next_5m_close" else length
        self.ended: bool = False
    def check(self) -> bool:
        if self.ended:
            raise RuntimeError("Timer already ended")
        if self.start_time + self.length < time.time():
            self.ended = True
            return True
        return False
        

    
class IBClient:
    def __init__(self) -> None:
        self.ib:IB = IB()
        self.sp_contract: Contract|None = None
        self.testprice:float = 6700.0

    async def connect(self, host="127.0.0.1", port=7497, clientId=2) -> None:
        self.ib.RequestTimeout = 10  # Increase timeout to 30 seconds
        await self.ib.connectAsync(host, port, clientId=clientId)
        if not self.ib.isConnected():
            raise ConnectionRefusedError("Could not connect to IB Gateway/TWS")
        template = Future(
        symbol="MES",
        exchange="CME",
        currency="USD"
        )
        details = await self.ib.reqContractDetailsAsync(template)
        # details are sorted from nearest expiry to furthest
        self.sp_contract = details[0].contract
        if self.sp_contract is None:
            raise ValueError("Could not get MES contract details")
        

    async def get_latest_tick_mes(self, timeout=5.0) -> Tick:
        if not self.ib.isConnected():
            raise ConnectionError("Not connected to IB")
        if TESTING:
            ticker: Ticker = Ticker(self.sp_contract)
            ticker.last = self.testprice +randint(-20,20)
            self.testprice = ticker.last
            ticker.time = get_cboe_datetime()
        else:
            ticker: Ticker = self.ib.reqMktData(self.sp_contract, '', False, False)
        start = time.time()
        while math.isnan(ticker.last):
            if time.time() - start > timeout:
                raise TimeoutError("No tick received within timeout")
            await asyncio.sleep(0.01) 
        if ticker.time is None:
            raise ValueError("Ticker time is None")
        return Tick(ticker.time, ticker.last)
    
    async def trade_mes(self, action: Literal["BUY", "SELL"], quantity: int) -> Trade:
        """
        Place a market order for ES/MES futures.

        Parameters:
            ib: IB() instance
            action: 'BUY' or 'SELL'
            qty: number of contracts
        """
        if not self.ib.isConnected():
            raise ConnectionError("Not connected to IB")
        contract = self.sp_contract
        await self.ib.qualifyContractsAsync(contract)  # ensure IB knows the contract

        order = MarketOrder(action, quantity)
        trade = self.ib.placeOrder(contract, order)
        print(f"Order placed: {action} {quantity} MES at market price.")
        return trade
        
    async def disconnect(self):
        if self.ib and self.ib.isConnected():
            self.ib.disconnect()

async def test_loop():
    client = IBClient()
    await client.connect()
    try:
        await client.trade_mes("BUY", 100)
    finally:
        pass
        # await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_loop())
