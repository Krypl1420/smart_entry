from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Discord chat URL
url = "https://discord.com/channels/1427735994538659890/1427735994538659893"

options = Options()
# options.add_argument("--headless=new")  # comment out if you want visible browser
options.add_argument(r"user-data-dir=D:\selenium")
options.add_argument("profile-directory=Default")  # or "Profile 1"
options.binary_location = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--disable-gpu")
# options.add_argument("--remote-debugging-port=9222")
# options.add_argument("--no-first-run")
# options.add_argument("--no-default-browser-check")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(url)
time.sleep(5)  # wait for page to load

# --- Inject MutationObserver on <ol> ---
observer_js = """
if (!window.__observerInjected) {
    window.__observerInjected = true;

    const target = document.querySelector('ol');
    if (target) {
        const observer = new MutationObserver(mutations => {
            for (const mutation of mutations) {
                for (const node of mutation.addedNodes) {

                    if (
                        node.tagName?.toLowerCase() === 'li' &&
                        node.className === "messageListItem__5126c"
                        ) {
                        const spans = node.querySelectorAll('span');
                        if (spans.length >= 2) {
                            for (const span of spans) {
                                console.log(span.textContent,"|", span.className);
                                console.log("-----");
                            }
                            window.__latestElement = {
                                text: "error"
                            };
                        }else{
                            window.__latestElement = {
                                text: node.textContent
                            };
                        }


                    }

                }
            }
        });
        observer.observe(target, { childList: true, subtree: true });
    }
}
"""
driver.execute_script(observer_js)
print("Observer injected, monitoring <ol>...")

# --- Loop to fetch new element immediately when it appears ---
last_content = None

try:
    while True:
        newest = driver.execute_script("return window.__latestElement || null;")
        if newest and newest.get("text") != last_content:
            last_content = newest.get("text")
            print("New message detected:")
            print(last_content)
            print("---")
        time.sleep(0.05)  # small sleep to avoid CPU spike
except KeyboardInterrupt:
    print("Stopped monitoring.")
finally:
    driver.quit()
