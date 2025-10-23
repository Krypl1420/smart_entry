"""
1. aktualni price = last traded
2. pro spx live je potreba subscription (spy)

"""

import time
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import atexit
import psutil
from ui import get_env_var, clear_env_var
from discord_js_scripts import OBSERVER_SCRIPT, LOGIN_SCRIPT
from ib_api import initialize_ib, get_live_spx_data
from ib_async import IB, Index
import asyncio
# IB = ib_api.initialize_ib()

@dataclass
class Tick:
    price: float
    timestamp: float

def manage_ticks(prices:list[Tick], time_window:int = 900) -> list[Tick]:
    current_time = time.time()
    # Remove ticks older than time_window
    prices = [tick for tick in prices if current_time - tick.timestamp <= time_window]
    return prices

def kill_chrome_processes():
    for proc in psutil.process_iter(['pid', 'name']):
        name = proc.info['name']
        if not name:
            continue
        if "chrome" in name.lower() or "chromedriver" in name.lower():
            try:
                proc.kill()
            except Exception:
                pass

atexit.register(kill_chrome_processes)

URL:str = "https://discord.com/channels/1427735994538659890/1427735994538659893"
NAME:str = get_env_var("email")
PASS:str = get_env_var("heslo")

options = Options()
while (True):
    x = input("1) Zapnout program 2) Zapnout s viditelnym prohlizecem 3) Nove prihlasovaci udaje !vymaze stare!(jde změnit v .env): ").strip()
    if x == "1":
        options.add_argument("--headless=new")
        break
    elif x == "2":
        break
    elif x == "3":
        clear_env_var()
        break
    else:
        print("Neplatna volba, zkus to znovu.")
options.add_argument("--no-sandbox")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.get(URL)
time.sleep(6)  # wait for page to load
# --- Log in ---
driver.execute_script(LOGIN_SCRIPT(NAME, PASS))
time.sleep(5)
# --- Inject MutationObserver on <ol> ---

driver.execute_script(OBSERVER_SCRIPT)
print("Observer injected, monitoring <ol>...")

last_time = None
smart_entry_high:float
smart_entry_low:float
ib: IB = initialize_ib()
last_price:float = 0.0
prices: list[Tick] = []

try:
    while True:
        newest = driver.execute_script("return window.__latestElement || null;")
        if not newest:
            time.sleep(0.05)
            continue

        text:str = newest.get("text")
        timestamp:int = newest.get("time")

        if timestamp == last_time:
            time.sleep(0.05)
            continue 
        if text.startswith("error"):
            raise Exception(text)

        parts = text.split("|")
        smart_entry_high, smart_entry_low = map(float, parts[6:8])

        current_price = asyncio.run(get_live_spx_data(ib))
        if current_price != last_price:
            manage_ticks(prices)
            prices.append(Tick(price=current_price, timestamp=time.time()))
        print(f"SPX Current: {current_price:.2f}, Smart Entry High: {smart_entry_high:.2f}, Low: {smart_entry_low:.2f}")

        last_time = timestamp
        time.sleep(0.05)

except KeyboardInterrupt:
    print(smart_entry_low, smart_entry_high)
    print("Stopped monitoring.")
finally:
    print("Closing driver...")
    driver.quit()
    service.stop()
    kill_chrome_processes()
