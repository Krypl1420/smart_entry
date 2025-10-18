from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import dotenv
import atexit
import psutil

# Discord chat URL
URL = "https://discord.com/channels/1427735994538659890/1427735994538659893"
def get_env_var(key: str) -> str:
    dotenv_path = "../.env"
    dotenv.load_dotenv(dotenv_path)

    val = dotenv.get_key(dotenv_path, key)
    if val:
        return val
    else:
        val = input(f"{key} nenalezen. Zadejte jej prosím: ")
        print("\n")
        dotenv.set_key(dotenv_path, key, val)
        return val
def clear_env_var():
    dotenv_path = "../.env"
    dotenv.set_key(dotenv_path, "email", "")
    dotenv.set_key(dotenv_path, "heslo", "")


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


NAME = get_env_var("email")
PASS = get_env_var("heslo")

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
time.sleep(3)  # wait for page to load
# --- Log in ---
driver.execute_script(f"""
console.log(window.location.pathname);
function sleep(ms) {{
    return new Promise(resolve => setTimeout(resolve, ms));
}}
if (window.location.pathname === "/login" && document.readyState === "interactive") {{
    console.log("On login page");
}}else{{
    console.log("Not on login page");
    await sleep(5000);
}}

const email = document.querySelector('[autocomplete~="username"]');
const password = document.querySelector('[autocomplete~="current-password"]');
const submit = document.querySelector('button[type="submit"]');
console.log(email, password, submit, "LOGIN ELEMENTS");

if (email && password && submit) {{
    function setNativeValue(element, value) {{
        const valueSetter = Object.getOwnPropertyDescriptor(element.__proto__, 'value').set;
        const prototype = Object.getPrototypeOf(element);
        const prototypeValueSetter = Object.getOwnPropertyDescriptor(prototype, 'value').set;
        if (valueSetter && valueSetter !== prototypeValueSetter) {{
            prototypeValueSetter.call(element, value);
        }} else {{
            valueSetter.call(element, value);
        }}
        element.dispatchEvent(new Event('input', {{ bubbles: true }}));
        element.dispatchEvent(new Event('change', {{ bubbles: true }}));
    }}

    setNativeValue(email, "{NAME}");
    setNativeValue(password, "{PASS}");

    setTimeout(() => {{
        submit.click();
    }}, 800);
}}
""")
time.sleep(1)
# --- Inject MutationObserver on <ol> ---
observer_js = """
function sleep(ms) {{
    return new Promise(resolve => setTimeout(resolve, ms));
}}
if(!window.location.pathname.includes("/channels/") || document.readyState !== "complete"){
    await sleep(5000);
}
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
                        let mySpan;
                        for (const span of spans) {
                            if (span.parentElement.className.includes("messageContent")) {
                                if (mySpan) {
                                    window.__latestElement = {
                                        text: "error: multiple spans"
                                    }
                                    console.log("ERROR: multiple messageContent spans found")
                                }
                                mySpan = span;
                                break;
                            }
                        }
                        if (mySpan) {
                            console.log("New message detected:", mySpan.innerText);
                            window.__latestElement = {
                                text: mySpan.innerText,
                                time: new Date().toLocaleString()
                            }
                        }else{
                            window.__latestElement = {
                                text: "error: no span found"
                            }
                            console.log("ERROR: no messageContent span found")
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
last_time = None

try:
    while True:
        newest = driver.execute_script("return window.__latestElement || null;")
        if newest and newest.get("time") != last_time:
            if newest.get("text").startswith("error"):
                raise Exception(newest.get("text"))
            last_time = newest.get("time")
            print("New message detected:")
            print(newest.get("text"))
            print("---")
        time.sleep(0.05)  # small sleep to avoid CPU spike
except KeyboardInterrupt:
    print("Stopped monitoring.")
finally:
    print("Closing driver...")
    driver.quit()
    service.stop()
    kill_chrome_processes()
