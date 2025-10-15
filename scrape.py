from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scan_new_dom_elements(url, observe_time=10):

    driver = webdriver.Chrome(service=Service())
    driver.get(url)
    time.sleep(2)  # Wait for initial load

    # Inject MutationObserver script
    observer_script = """
    window.newElements = [];
    var observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // Element node
                    window.newElements.push(node.outerHTML);
                }
            });
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });
    """

    driver.execute_script(observer_script)

    # Wait for observe_time seconds to collect new elements
    time.sleep(observe_time)

    # Get collected new elements
    new_elements = driver.execute_script("return window.newElements;")

    driver.quit()
    return new_elements

# Example usage:
if __name__ == "__main__":
    url = "https://example.com"
    new_dom_elements = scan_new_dom_elements(url)
    print(f"Found {len(new_dom_elements)} new DOM elements.")
    # Optionally print or process new_dom_elements