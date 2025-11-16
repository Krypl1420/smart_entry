from datetime import datetime
from ib_async import IB, Index, util, Ticker, Stock, Contract, Order, Future, ticker, MarketOrder, Trade
import asyncio
from dataclasses import dataclass
from zoneinfo import ZoneInfo
from typing import Literal
import time
import math
from random import randint
@dataclass
class Tick:
    timestamp: datetime
    price: float

def get_cboe_datetime() -> datetime:
    """Return the current datetime in Cboe (Chicago) timezone."""
    return datetime.now(ZoneInfo("America/Chicago"))

class IBClient:
    def __init__(self):
        self.ib = IB()
        self.sp_contract =  None
        self.testprice:float = 6700.0

    async def connect(self, host="127.0.0.1", port=7497, clientId=1) -> None:
        await self.ib.connectAsync(host, port, clientId=clientId)
        template = Future(
        symbol="MES",
        exchange="CME",
        currency="USD"
        )
        details = await self.ib.reqContractDetailsAsync(template)
        # details are sorted from nearest expiry to furthest
        self.sp_contract = details[0].contract
        

    async def get_latest_tick_mes(self, timeout=5.0) -> Tick:
        # ticker: Ticker = self.ib.reqMktData(self.sp_contract, '', False, False)
        ticker: Ticker = Ticker(self.sp_contract)
        ticker.last = self.testprice +randint(-20,20)
        self.testprice = ticker.last
        ticker.time = get_cboe_datetime()
        start = time.time()
        while math.isnan(ticker.last):
            if time.time() - start > timeout:
                raise TimeoutError("No tick received within timeout")
            await asyncio.sleep(0.01) 

        return Tick(ticker.time, ticker.last)
    
    async def trade_mes(self, action: Literal["BUY", "SELL"], quantity: int) -> Trade:
        """
        Place a market order for ES/MES futures.

        Parameters:
            ib: IB() instance
            action: 'BUY' or 'SELL'
            qty: number of contracts
        """
        contract = self.sp_contract
        await self.ib.qualifyContractsAsync(contract)  # ensure IB knows the contract

        order = MarketOrder(action, quantity)
        trade = self.ib.placeOrder(contract, order)
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
