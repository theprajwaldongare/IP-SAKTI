/**
 * Chat Assistant Controller for IP Sakti
 */

function formatMarkdown(text) {
    if (!text) return "";
    let html = text
        .replace(/### (.*?)\n/g, '<h3>$1</h3>')
        .replace(/#### (.*?)\n/g, '<h4>$1</h4>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
        .replace(/\n- (.*?)/g, '<br>• $1')
        .replace(/\n1\. (.*?)/g, '<br>1. $1')
        .replace(/\n2\. (.*?)/g, '<br>2. $1')
        .replace(/\n3\. (.*?)/g, '<br>3. $1')
        .replace(/\n4\. (.*?)/g, '<br>4. $1')
        .replace(/\n/g, '<br>');
    return html;
}

async function sendChatMessage(customQuery = null) {
    const inputElem = document.getElementById("chatInput");
    const query = (customQuery !== null ? customQuery : inputElem.value).trim();
    if (!query) return;

    if (!customQuery) inputElem.value = "";

    const jurElem = document.getElementById("chatJurisdiction");
    const jurisdiction = jurElem ? jurElem.value : "india";

    const messagesContainer = document.getElementById("chatMessages");

    const userBubble = document.createElement("div");
    userBubble.className = "message-bubble message-user";
    userBubble.innerHTML = `<strong>You:</strong> ${query}`;
    messagesContainer.appendChild(userBubble);

    // Get translated loading text based on current language and jurisdiction
    const dict = I18N_TRANSLATIONS[currentLang] || I18N_TRANSLATIONS["en"];
    const loadingText = jurisdiction === "international" ? dict.loadingIntl : dict.loadingIndia;

    const botBubble = document.createElement("div");
    botBubble.className = "message-bubble message-assistant";
    botBubble.innerHTML = `<em>${loadingText}</em>`;
    messagesContainer.appendChild(botBubble);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: query,
                language: currentLang,
                jurisdiction: jurisdiction
            })
        });

        if (!response.ok) {
            const errText = await response.text();
            throw new Error(`Server returned HTTP ${response.status}: ${errText}`);
        }

        const data = await response.json();
        botBubble.innerHTML = formatMarkdown(data.answer);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

    } catch (err) {
        console.error("Chat error:", err);
        botBubble.innerHTML = `⚠️ <strong>Server Issue:</strong> ${err.message}`;
    }
}

function handleVoiceInput() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert("Speech recognition is not supported in this browser. Please type your query.");
        return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = currentLang === 'hi' ? 'hi-IN' : (currentLang === 'mr' ? 'mr-IN' : (currentLang === 'sa' ? 'sa-IN' : (currentLang === 'ta' ? 'ta-IN' : 'en-US')));
    recognition.interimResults = false;

    const voiceBtn = document.getElementById("voiceBtn");
    voiceBtn.style.color = "#FF5252";

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById("chatInput").value = transcript;
        voiceBtn.style.color = "#E6C265";
        sendChatMessage(transcript);
    };

    recognition.onerror = () => {
        voiceBtn.style.color = "#E6C265";
    };

    recognition.onend = () => {
        voiceBtn.style.color = "#E6C265";
    };

    recognition.start();
}

// /**
//  * Chat Assistant Controller for IP Sakti
//  */

// function formatMarkdown(text) {
//     if (!text) return "";
//     let html = text
//         .replace(/### (.*?)\n/g, '<h3>$1</h3>')
//         .replace(/#### (.*?)\n/g, '<h4>$1</h4>')
//         .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
//         .replace(/\*(.*?)\*/g, '<em>$1</em>')
//         .replace(/`([^`]+)`/g, '<code>$1</code>')
//         .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
//         .replace(/\n- (.*?)/g, '<br>• $1')
//         .replace(/\n1\. (.*?)/g, '<br>1. $1')
//         .replace(/\n2\. (.*?)/g, '<br>2. $1')
//         .replace(/\n3\. (.*?)/g, '<br>3. $1')
//         .replace(/\n4\. (.*?)/g, '<br>4. $1')
//         .replace(/\n/g, '<br>');
//     return html;
// }

// async function sendChatMessage(customQuery = null) {
//     const inputElem = document.getElementById("chatInput");
//     const query = (customQuery !== null ? customQuery : inputElem.value).trim();
//     if (!query) return;

//     if (!customQuery) inputElem.value = "";

//     const jurElem = document.getElementById("chatJurisdiction");
//     const jurisdiction = jurElem ? jurElem.value : "india";

//     const messagesContainer = document.getElementById("chatMessages");

//     const userBubble = document.createElement("div");
//     userBubble.className = "message-bubble message-user";
//     userBubble.innerHTML = `<strong>You:</strong> ${query}`;
//     messagesContainer.appendChild(userBubble);

//     const botBubble = document.createElement("div");
//     botBubble.className = "message-bubble message-assistant";
//     const jurTag = jurisdiction === "international" ? "International Treaties (WIPO/PCT)" : "Indian Statutes (Patents Act/AYUSH/NBA)";
//     botBubble.innerHTML = `<em>🌿 IP Sakti is evaluating ${jurTag}...</em>`;
//     messagesContainer.appendChild(botBubble);
//     messagesContainer.scrollTop = messagesContainer.scrollHeight;

//     try {
//         const response = await fetch("/api/chat", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({
//                 query: query,
//                 language: currentLang,
//                 jurisdiction: jurisdiction
//             })
//         });

//         if (!response.ok) {
//             const errText = await response.text();
//             throw new Error(`Server returned HTTP ${response.status}: ${errText}`);
//         }

//         const data = await response.json();
//         botBubble.innerHTML = formatMarkdown(data.answer);
//         messagesContainer.scrollTop = messagesContainer.scrollHeight;

//     } catch (err) {
//         console.error("Chat error:", err);
//         botBubble.innerHTML = `⚠️ <strong>Server Issue:</strong> ${err.message}`;
//     }
// }

// function handleVoiceInput() {
//     if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
//         alert("Speech recognition is not supported in this browser. Please type your query.");
//         return;
//     }
//     const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
//     const recognition = new SpeechRecognition();
//     recognition.lang = currentLang === 'hi' ? 'hi-IN' : (currentLang === 'mr' ? 'mr-IN' : (currentLang === 'sa' ? 'sa-IN' : 'en-US'));
//     recognition.interimResults = false;

//     const voiceBtn = document.getElementById("voiceBtn");
//     voiceBtn.style.color = "#FF5252";

//     recognition.onresult = (event) => {
//         const transcript = event.results[0][0].transcript;
//         document.getElementById("chatInput").value = transcript;
//         voiceBtn.style.color = "#E6C265";
//         sendChatMessage(transcript);
//     };

//     recognition.onerror = () => {
//         voiceBtn.style.color = "#E6C265";
//     };

//     recognition.onend = () => {
//         voiceBtn.style.color = "#E6C265";
//     };

//     recognition.start();
// }

// // /**
// //  * Chat Assistant Controller for IP Sakti
// //  */

// // function formatMarkdown(text) {
// //     if (!text) return "";
// //     let html = text
// //         .replace(/### (.*?)\n/g, '<h3>$1</h3>')
// //         .replace(/#### (.*?)\n/g, '<h4>$1</h4>')
// //         .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
// //         .replace(/\*(.*?)\*/g, '<em>$1</em>')
// //         .replace(/`([^`]+)`/g, '<code>$1</code>')
// //         .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
// //         .replace(/\n- (.*?)/g, '<br>• $1')
// //         .replace(/\n1\. (.*?)/g, '<br>1. $1')
// //         .replace(/\n2\. (.*?)/g, '<br>2. $1')
// //         .replace(/\n3\. (.*?)/g, '<br>3. $1')
// //         .replace(/\n4\. (.*?)/g, '<br>4. $1')
// //         .replace(/\n/g, '<br>');
// //     return html;
// // }

// // async function sendChatMessage(customQuery = null) {
// //     const inputElem = document.getElementById("chatInput");
// //     const query = (customQuery !== null ? customQuery : inputElem.value).trim();
// //     if (!query) return;

// //     if (!customQuery) inputElem.value = "";

// //     // Read selected jurisdiction
// //     const jurElem = document.getElementById("chatJurisdiction");
// //     const jurisdiction = jurElem ? jurElem.value : "india";

// //     const messagesContainer = document.getElementById("chatMessages");

// //     // Render User Bubble
// //     const userBubble = document.createElement("div");
// //     userBubble.className = "message-bubble message-user";
// //     userBubble.innerHTML = `<strong>You:</strong> ${query}`;
// //     messagesContainer.appendChild(userBubble);

// //     // Render Assistant Loading State
// //     const botBubble = document.createElement("div");
// //     botBubble.className = "message-bubble message-assistant";
// //     const jurTag = jurisdiction === "international" ? "International Treaties (WIPO/PCT)" : "Indian Statutes (Patents Act/AYUSH/NBA)";
// //     botBubble.innerHTML = `<em>🌿 IP Sakti is evaluating ${jurTag}...</em>`;
// //     messagesContainer.appendChild(botBubble);
// //     messagesContainer.scrollTop = messagesContainer.scrollHeight;

// //     try {
// //         const response = await fetch("/api/chat", {
// //             method: "POST",
// //             headers: { "Content-Type": "application/json" },
// //             body: JSON.stringify({
// //                 query: query,
// //                 language: currentLang,
// //                 jurisdiction: jurisdiction
// //             })
// //         });

// //         if (!response.ok) {
// //             throw new Error(`Server returned status ${response.status}`);
// //         }

// //         const data = await response.json();
// //         botBubble.innerHTML = formatMarkdown(data.answer);
// //         messagesContainer.scrollTop = messagesContainer.scrollHeight;

// //     } catch (err) {
// //         console.error("Chat error:", err);
// //         botBubble.innerHTML = `⚠️ <strong>System Error:</strong> Unable to reach the IP Sakti backend. Please ensure the server is active.`;
// //     }
// // }

// // function handleVoiceInput() {
// //     if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
// //         alert("Speech recognition is not supported in this browser. Please type your query.");
// //         return;
// //     }
// //     const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
// //     const recognition = new SpeechRecognition();
// //     recognition.lang = currentLang === 'hi' ? 'hi-IN' : (currentLang === 'mr' ? 'mr-IN' : (currentLang === 'sa' ? 'sa-IN' : 'en-US'));
// //     recognition.interimResults = false;

// //     const voiceBtn = document.getElementById("voiceBtn");
// //     voiceBtn.style.color = "#FF5252";

// //     recognition.onresult = (event) => {
// //         const transcript = event.results[0][0].transcript;
// //         document.getElementById("chatInput").value = transcript;
// //         voiceBtn.style.color = "#E6C265";
// //         sendChatMessage(transcript);
// //     };

// //     recognition.onerror = () => {
// //         voiceBtn.style.color = "#E6C265";
// //     };

// //     recognition.onend = () => {
// //         voiceBtn.style.color = "#E6C265";
// //     };

// //     recognition.start();
// // }