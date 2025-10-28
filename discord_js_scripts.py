from typing import Callable

LOGIN_SCRIPT:Callable[[str,str], str] = lambda NAME, PASS: f"""
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
"""

OBSERVER_SCRIPT = """
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