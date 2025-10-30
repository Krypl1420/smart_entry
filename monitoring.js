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