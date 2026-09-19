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
    const query = customQuery || inputElem.value.trim();
    if (!query) return;

    if (!customQuery) inputElem.value = "";

    const messagesContainer = document.getElementById("chatMessages");

    // Render User Message
    const userBubble = document.createElement("div");
    userBubble.className = "message-bubble message-user";
    userBubble.innerHTML = `<strong>You:</strong> ${query}`;
    messagesContainer.appendChild(userBubble);

    // Render Loading Indicator for Assistant
    const botBubble = document.createElement("div");
    botBubble.className = "message-bubble message-assistant";
    botBubble.innerHTML = `<em>🌿 IP Sakti is searching TKDL, Indian Patent Act & AYUSH database...</em>`;
    messagesContainer.appendChild(botBubble);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: query,
                language: currentLang
            })
        });

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }

        const data = await response.json();
        
        let formattedAnswer = formatMarkdown(data.answer);
        botBubble.innerHTML = formattedAnswer;

        // Auto-scroll chat
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

    } catch (err) {
        console.error("Chat error:", err);
        botBubble.innerHTML = `⚠️ <strong>System Error:</strong> Unable to connect to backend server. Please verify FastAPI backend is running at http://127.0.0.1:8000.`;
    }
}

function handleVoiceInput() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert("Speech recognition is not supported by your current browser. Please type your query.");
        return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = currentLang === 'hi' ? 'hi-IN' : (currentLang === 'sa' ? 'sa-IN' : 'en-US');
    recognition.interimResults = false;

    const voiceBtn = document.getElementById("voiceBtn");
    voiceBtn.style.color = "#FF5252";

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById("chatInput").value = transcript;
        voiceBtn.style.color = "#E6C265";
        sendChatMessage(transcript);
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error", event.error);
        voiceBtn.style.color = "#E6C265";
    };

    recognition.onend = () => {
        voiceBtn.style.color = "#E6C265";
    };

    recognition.start();
}
