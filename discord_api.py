import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import atexit
import psutil
from ui import get_env_var, clear_env_var
from discord_js_scripts import OBSERVER_SCRIPT
import os
class DiscordFeeder:
    def __init__(self):
        self.last_time = None
        self.driver: webdriver.Chrome


        atexit.register(self.kill_chrome_processes)
        URL:str = get_env_var("chat_url")
        ACCOUNT_PATH = get_env_var("account_path").replace("\\", "/")

        os.makedirs(ACCOUNT_PATH, exist_ok=True)

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
        options.add_argument(f"--user-data-dir={ACCOUNT_PATH}")
        options.add_argument("--no-sandbox")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.get(URL)
        time.sleep(6)

        self.driver.execute_script(OBSERVER_SCRIPT)
        print("Observer injected, monitoring <ol>...")

        self.last_time = None

    def get_smart_entries(self):
        """
        returns new smart entries high, low or 0, 0"""
        newest = self.driver.execute_script("return window.__latestElement || null;")
        if not newest:
            return 0, 0

        text:str = newest.get("text")
        js_timestamp:str = newest.get("time")

        if js_timestamp == self.last_time:
            return 0, 0
        if text.startswith("error"):
            # JS returned an error
            self.kill_chrome_processes()
            raise Exception(text)

        parts = text.split("|")
        smart_entry_high, smart_entry_low = map(float, parts[6:8])
        self.last_time = js_timestamp
        return smart_entry_high, smart_entry_low
    
    async def get_smart_entries_async(self):
        newest = self.driver.execute_script("return window.__latestElement || null;")
        if not newest:
            return 0, 0

        text:str = newest.get("text")
        js_timestamp:str = newest.get("time")

        if js_timestamp == self.last_time:
            return 0, 0
        if text.startswith("error"):
            # JS returned an error
            self.kill_chrome_processes()
            raise Exception(text)

        parts = text.split("|")
        smart_entry_high, smart_entry_low = map(float, parts[6:8])
        self.last_time = js_timestamp
        return smart_entry_high, smart_entry_low
    

    
    @staticmethod
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
