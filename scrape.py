from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import dotenv

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

NAME = get_env_var("email")
PASS = get_env_var("heslo")

options = Options()
# options.add_argument("--headless=new")  # comment out if you want visible browser

options.add_experimental_option("detach", False)
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(URL)
time.sleep(10)  # wait for page to load
# --- Log in ---
driver.execute_script(f"""
console.log(window.location.pathname);

if (window.location.pathname === "/login") {{
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
}}
""")
time.sleep(2)
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
