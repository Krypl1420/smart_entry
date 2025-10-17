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
        while (true) {
            console.log(window.__latestElement.text??"No new element yet");
            await new Promise(r => setTimeout(r, 100));
        }
    }
}