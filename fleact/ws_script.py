ws_script = """
<script>

    function checkReactiveIsLoading() {
        // Iterate through all elements with fleact-if

        document.querySelectorAll("[fleact-if]").forEach((element) => {
            console.log("Element:", element);
            const condition = element.getAttribute("fleact-if") === "True"; // Explicit comparison

            if (condition) {
                element.style.display = ""; // Show element
            } else {
                element.style.display = "none"; // Hide element
            }
        });


        // Iterate through all elements with fleact-else
        document.querySelectorAll("[fleact-else]").forEach((element) => {
            const condition = element.getAttribute("fleact-else");
            if (!data[condition]) {
                element.style.display = ""; // Show element
            } else {
                element.style.display = "none"; // Hide element
            }
        });
    }

    checkReactiveIsLoading()

    function checkReactiveIsLoadingfromWS() {
        // Iterate through all elements with fleact-if
        document.querySelectorAll("[fleact-if]").forEach((element) => {
            const fleactId = element.getAttribute("fleact-id");

            if (fleactId) {
                // Emit event to request `if_else` from backend
                socket.emit("get-if-else", { "fleact-id": fleactId }, (response) => {
                    console.log("Response for fleact-id", fleactId, ":", response);
                    if (response && response.if_else !== undefined) {
                        // Update element display based on `if_else` value
                        console.log("Setting display for fleact-id", fleactId, ":", response.if_else);
                        element.style.display = response.if_else ? "none" : "";
                    } else {
                        console.error(`Invalid response for fleact-id ${fleactId}:`, response);
                    }
                });
            }
        });
    }

</script>
        <script src="https://cdn.socket.io/4.8.1/socket.io.min.js" integrity="sha384-mkQ3/7FUtcGyoppY6bz/PORYoGqOl7/aSUMn2ymDOJcapfS6PHqxhRTMh1RR0Q6+" crossorigin="anonymous"></script>
        <script>
            const socket = io.connect("http://" + window.location.host);

            socket.on("connect", () => {
                console.log("Connected to WebSocket");
            });

            // Updated socket.on logic
            socket.on("message", (data) => {
                console.log("Received message:", data);
                const parsed = typeof data === "string" ? JSON.parse(data) : data; // Check if it's a string before parsing
                console.log("Parsed message:", parsed);
                console.log("Parsed message:", parsed.target);



                if (parsed.action === "update-counter") {
                    const targetElement = document.querySelector(`[fleact-id="${parsed.target}"]`);
                    if (!targetElement) {
                        console.error("Target element not found for fleact-id:", parsed.target);
                        return;
                    }
                    console.log("Updating counter:", parsed.value);
                    targetElement.innerText = "Counter: " + parsed.value;
                } else if (parsed.action === "update-content") {
                    const targetElement = document.querySelector(`[fleact-id="${parsed.target}"]`);
                    if (!targetElement) {
                        console.error("Target element not found for fleact-id:", parsed.target);
                        return;
                    }
                    console.log("Updating content:", parsed.content);
                    targetElement.innerText = parsed.content;
                }
            });


            socket.on("state-updated", (data) => {
                console.log("State updated:", data);

                if (data.action === "update-content") {
                    const targetElement = document.querySelector(`[fleact-id="${data.target}"]`);
                    if (targetElement) {
                        targetElement.innerText = data.content;
                    } else {
                        console.error("Target element not found for fleact-id:", data.target);
                    }
                } else if (data.action === "toggle-visibility") {
                    const targetElement = document.querySelector(`[fleact-id="${data.target}"]`);
                    if (targetElement) {
                        targetElement.style.display = data.visible ? "" : "none";
                    }
                }
            });


            socket.on("if-else", (data) => {
                console.log("If/else data:", data);
                checkReactiveIsLoadingfromWS()
            });




            function sendMessage(message, event) {
                // Ensure the event is valid
                event = event || window.event;

                // Get the element that triggered the event
                const target = event.target || event.srcElement;

                // Log information about the target element
                console.log("Event Target:", target);

                // Optionally include details about the element in the message
                const elementInfo = {
                    tag: target.tagName,
                    classes: target.className,
                    attributes: [...target.attributes].map(attr => ({
                        name: attr.name,
                        value: attr.value
                    })),
                    text: target.innerText || target.textContent
                };

                console.log("Element Info:", elementInfo);
                const fleact_id = elementInfo.attributes.find(attr => attr.name === "fleact-id").value;
                socket.send(JSON.stringify({ message, elementInfo, "fleact-id": fleact_id }));
            }

            // Trigger on_load callbacks on page load
            window.onload = () => {
                console.log("Page loaded");
                // Locate all elements with a fleact-id
                document.querySelectorAll("[fleact-id]").forEach((element) => {
                    console.log("Element:", element);
                    const fleactId = element.getAttribute("fleact-id");
                    const callbacks = element.getAttribute("fleact-callbacks");
                    console.log("Callbacks:", callbacks);
                    console.log("Fleact ID:", fleactId);
                    if (callbacks) {
                        console.log("Callbacks found:", callbacks);
                        const parsedCallbacks = JSON.parse(callbacks);
                        Object.keys(parsedCallbacks).forEach((callbackName) => {
                            const callbackConfig = parsedCallbacks[callbackName];
                            if (callbackConfig.on_load) {
                                console.log(`Triggering on_load callback: ${callbackName}`);
                                socket.send(
                                    JSON.stringify({
                                        message: "trigger-callback",
                                        "fleact-id": fleactId,
                                        callback_name: callbackName,
                                    })
                                );
                            }
                        });
                    }
                });
            };

        </script>
        """
