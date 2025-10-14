import discord
# import ib_api
import os
from dotenv import load_dotenv, set_key
import time
from dataclasses import dataclass

# IB = ib_api.initialize_ib()
intents = discord.Intents.default()
intents.message_content = True  
client = discord.Client(intents=intents)

@dataclass
class SmartMoney:
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

def get_env_var() -> str:
    dotenv_path = "../.env"
    load_dotenv(dotenv_path)
    key = "DIS_TKN"

    val = os.getenv(key)
    if val:
        return val
    else:
        val = input("Discord Bot Token nenalezen. Zadejte jej prosím: ")
        set_key(dotenv_path, key, val)
        return val

def trade_range(range_high, range_low):
    start_time = time.time()
    while(True):
        delta = time.time() - start_time
        if delta > 60 * 5:  
            break
        # bars = ib_api.get_last_n_bars(IB,)
        # current_price = bars['close'].iloc[-1]
        # candles = ib_api.get_last_n_bars(IB, 'AAPL', 5, '1 min')
        # if current_price >= range_high:
        #     pass
        #     #sell function
        # elif current_price <= range_low:
        #     pass
            #buy function
            



@client.event
async def on_message(message):
    if message.author == client.user:  # ignore the bot's own messages
        return
    msg_list = message.content.split("|")
    smart_money = {
        "high" : float(msg_list[6].strip()),
        "low" : float(msg_list[7].strip())
    }
    return smart_money

# Paste your bot token here
client.run(get_env_var())
"""
+------------------+---------+---------+
| 2025-10-08 15:25 |  Horní  |  Dolní  |
+------------------+---------+---------+
| Smart entry zone | 6773.20 | 6771.40 |
|   Denní levely   | 6796.48 | 6753.52 |
|  Týdenní levely  | 6786.44 | 6693.56 |
+------------------+---------+---------+/
"""