from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Replace this with your Discord channel URL
url = "https://discord.com/channels/@me/1427685330311712829"

# --- Setup Chrome options ---
options = Options()
# comment this out if you want to see the browser window
# options.add_argument("--headless=new")

# keeps Chrome logged in if you specify a profile directory
# options.add_argument("--user-data-dir=C:/Users/YourName/AppData/Local/Google/Chrome/User Data")

# --- Launch the browser ---
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# --- Open the Discord chat URL ---
driver.get(url)

print("Discord chat opened.")
