/**
 * Chat Assistant Controller with STT & UI-Disabled TTS for IP Sakti
 */

let recognition = null;
let isRecording = false;
let currentCloudAudio = null;

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

// Clean markdown syntax for clear voice readout
function stripMarkdownForSpeech(text) {
    return text
        .replace(/[#*`_~]/g, '')
        .replace(/\[(.*?)\]\(.*?\)/g, '$1')
        .replace(/<[^>]*>/g, '')
        .trim();
}

async function sendChatMessage(customQuery = null) {
    const inputElem = document.getElementById("chatInput");
    const query = (customQuery !== null ? customQuery : inputElem.value).trim();
    if (!query) return;

    // Stop voice and audio immediately
    stopVoiceInput();
    stopSpeaking();

    if (!customQuery) inputElem.value = "";

    const jurElem = document.getElementById("chatJurisdiction");
    const jurisdiction = jurElem ? jurElem.value : "india";

    const messagesContainer = document.getElementById("chatMessages");

    const userBubble = document.createElement("div");
    userBubble.className = "message-bubble message-user";
    userBubble.innerHTML = `<strong>You:</strong> ${query}`;
    messagesContainer.appendChild(userBubble);

    const dict = (typeof I18N_TRANSLATIONS !== "undefined" && I18N_TRANSLATIONS[currentLang]) 
        ? I18N_TRANSLATIONS[currentLang] 
        : { loadingIntl: "Evaluating International Treaties...", loadingIndia: "Evaluating Indian Statutes..." };
        
    const loadingText = jurisdiction === "international" ? dict.loadingIntl : dict.loadingIndia;

    const botBubble = document.createElement("div");
    botBubble.className = "message-bubble message-assistant";
    botBubble.innerHTML = `<em>${loadingText}</em>`;
    messagesContainer.appendChild(botBubble);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
        // const response = await fetch("/api/chat", {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/chat`, {
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
        const rawAnswer = data.answer;
        
        const safeText = encodeURIComponent(stripMarkdownForSpeech(rawAnswer)).replace(/'/g, "%27");
        
        botBubble.innerHTML = `
            <div>${formatMarkdown(rawAnswer)}</div>
            <div class="tts-action-row" style="margin-top:0.8rem; display:flex; gap:0.5rem;">
                <button class="tts-btn play-btn" onclick="playTextToSpeech(decodeURIComponent('${safeText}'), this)" title="Listen to answer">
                    <i class="fas fa-volume-up"></i> Listen
                </button>
                <button class="tts-btn stop-btn" onclick="stopSpeaking()" title="Stop voice">
                    <i class="fas fa-stop"></i> Stop
                </button>
            </div>
        `;
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

    } catch (err) {
        // console.error("Chat error:", err);
        botBubble.innerHTML = `⚠️ <strong>Server Issue:</strong> ${err.message}`;
    }
}

/* ==========================================================================
   SPEECH-TO-TEXT (STT) 
   ========================================================================== */

function getLangSTTCode(lang) {
    const sttMap = {
        "en": "en-IN",
        "hi": "hi-IN",
        "mr": "mr-IN",
        "ta": "ta-IN",
        "te": "te-IN",
        "gu": "gu-IN",
        "bn": "bn-IN",
        "sa": "hi-IN" 
    };
    return sttMap[lang] || "en-IN";
}

function handleVoiceInput() {
    if (isRecording) {
        stopVoiceInput();
        return;
    }
    startVoiceInput();
}

function startVoiceInput() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert("Speech recognition is not supported in this browser.");
        return;
    }

    try {
        recognition = new SpeechRecognition();
        recognition.lang = getLangSTTCode(currentLang);
        recognition.interimResults = true;
        recognition.continuous = false;

        const voiceBtn = document.getElementById("voiceBtn");
        const chatInput = document.getElementById("chatInput");

        recognition.onstart = () => {
            isRecording = true;
            if (voiceBtn) {
                voiceBtn.classList.add("recording-active");
                voiceBtn.innerHTML = `<i class="fas fa-stop" style="color: #FF5252;"></i>`;
            }
            chatInput.placeholder = "Listening...";
        };

        recognition.onresult = (event) => {
            let transcript = "";
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                transcript += event.results[i][0].transcript;
            }
            chatInput.value = transcript;
        };

        recognition.onerror = () => stopVoiceInput();
        
        recognition.onend = () => {
            stopVoiceInput();
            if (chatInput.value.trim().length > 2) sendChatMessage();
        };

        recognition.start();
    } catch (err) {
        stopVoiceInput();
    }
}

function stopVoiceInput() {
    isRecording = false;
    const voiceBtn = document.getElementById("voiceBtn");
    const chatInput = document.getElementById("chatInput");

    if (voiceBtn) {
        voiceBtn.classList.remove("recording-active");
        voiceBtn.innerHTML = `<i class="fas fa-microphone"></i>`;
    }
    if (chatInput) {
        const dict = (typeof I18N_TRANSLATIONS !== "undefined" && I18N_TRANSLATIONS[currentLang]) ? I18N_TRANSLATIONS[currentLang] : {};
        chatInput.placeholder = dict.chatPlaceholder || "Ask about Section 3(p)...";
    }
    if (recognition) {
        try { recognition.stop(); } catch (e) {}
        recognition = null;
    }
}

/* ==========================================================================
   TEXT-TO-SPEECH (TTS) - ECHO-PROOF SESSION TRACKING
   ========================================================================== */

let currentAudioSession = 0; // The Ultimate Kill Switch

async function playTextToSpeech(text, clickedBtn = null) {
    // 1. Instantly kill any currently playing audio AND invalidate any background downloads
    stopSpeaking(); 
    
    // 2. Claim the new session ID for this specific click
    const mySession = ++currentAudioSession;

    // 3. Lock the UI so the user cannot double-click
    const allPlayBtns = document.querySelectorAll('.play-btn');
    allPlayBtns.forEach(btn => {
        btn.disabled = true;
        btn.style.opacity = "0.5";
        btn.style.cursor = "not-allowed";
    });

    if (clickedBtn) {
        clickedBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Loading...`;
        clickedBtn.style.opacity = "1"; 
    }

    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/tts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text, language: currentLang })
        });

        // 4. FATAL CHECK: Did the user click STOP or SEND while we were waiting for the server?
        if (mySession !== currentAudioSession) return; 

        if (!response.ok) throw new Error("Cloud TTS generation failed.");

        const blob = await response.blob();
        
        // 5. FATAL CHECK 2: Did they click STOP while the audio file was downloading?
        if (mySession !== currentAudioSession) return;

        const audioUrl = URL.createObjectURL(blob);
        currentCloudAudio = new Audio(audioUrl);
        
        // When audio finishes naturally, re-enable everything
        currentCloudAudio.onended = () => {
            if (mySession === currentAudioSession) resetTTSButtons();
        };

        await currentCloudAudio.play();

        if (clickedBtn && mySession === currentAudioSession) {
            clickedBtn.innerHTML = `<i class="fas fa-volume-up" style="color: #20C997;"></i> Playing`;
        }

    } catch (err) {
        // console.error("TTS Error:", err);
        // Only reset buttons if this error belongs to the active session
        if (mySession === currentAudioSession) resetTTSButtons();
    }
}

function stopSpeaking() {
    // 1. Invalidate any network requests that are currently loading in the background
    currentAudioSession++;

    // 2. Physically kill any audio that is currently playing out loud
    if (currentCloudAudio) {
        currentCloudAudio.pause();
        currentCloudAudio.currentTime = 0;
        currentCloudAudio.src = ""; // Dump file from memory
        currentCloudAudio = null;
    }
    
    // 3. Re-enable the UI
    resetTTSButtons();
}

function resetTTSButtons() {
    const allPlayBtns = document.querySelectorAll('.play-btn');
    allPlayBtns.forEach(btn => {
        btn.disabled = false;
        btn.style.opacity = "1";
        btn.style.cursor = "pointer";
        if (btn.innerHTML.includes("Loading") || btn.innerHTML.includes("Playing")) {
            btn.innerHTML = `<i class="fas fa-volume-up"></i> Listen`;
        }
    });
}

// /* ==========================================================================
//    TEXT-TO-SPEECH (TTS) - FRONTEND DISABLE APPROACH
//    ========================================================================== */

// async function playTextToSpeech(text, clickedBtn = null) {
//     stopSpeaking(); 

//     // 1. Disable ALL "Listen" buttons so the user can't double click
//     const allPlayBtns = document.querySelectorAll('.play-btn');
//     allPlayBtns.forEach(btn => {
//         btn.disabled = true;
//         btn.style.opacity = "0.5";
//         btn.style.cursor = "not-allowed";
//     });

//     if (clickedBtn) {
//         clickedBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Loading...`;
//         clickedBtn.style.opacity = "1"; // Keep the one they clicked visible
//     }

//     try {
//         const response = await fetch('/api/tts', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ text: text, language: currentLang })
//         });

//         if (!response.ok) throw new Error("Cloud TTS generation failed.");

//         const blob = await response.blob();
//         const audioUrl = URL.createObjectURL(blob);
        
//         currentCloudAudio = new Audio(audioUrl);
        
//         // When audio finishes naturally, re-enable everything
//         currentCloudAudio.onended = () => resetTTSButtons();

//         await currentCloudAudio.play();

//         if (clickedBtn) {
//             clickedBtn.innerHTML = `<i class="fas fa-volume-up" style="color: #20C997;"></i> Playing`;
//         }

//     } catch (err) {
//         console.error("TTS Error:", err);
//         resetTTSButtons();
//     }
// }

// function stopSpeaking() {
//     if (currentCloudAudio) {
//         currentCloudAudio.pause();
//         currentCloudAudio.currentTime = 0;
//         currentCloudAudio.src = "";
//         currentCloudAudio = null;
//     }
//     resetTTSButtons();
// }

// function resetTTSButtons() {
//     const allPlayBtns = document.querySelectorAll('.play-btn');
//     allPlayBtns.forEach(btn => {
//         btn.disabled = false;
//         btn.style.opacity = "1";
//         btn.style.cursor = "pointer";
//         if (btn.innerHTML.includes("Loading") || btn.innerHTML.includes("Playing")) {
//             btn.innerHTML = `<i class="fas fa-volume-up"></i> Listen`;
//         }
//     });
// }


// <<<Good code>>>

// /**
//  * Chat Assistant Controller with STT & TTS for IP Sakti
//  */

// let recognition = null;
// let isRecording = false;
// let currentCloudAudio = null;

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

// // Clean markdown syntax for clear voice readout
// function stripMarkdownForSpeech(text) {
//     return text
//         .replace(/[#*`_~]/g, '')
//         .replace(/\[(.*?)\]\(.*?\)/g, '$1')
//         .replace(/<[^>]*>/g, '')
//         .trim();
// }

// async function sendChatMessage(customQuery = null) {
//     const inputElem = document.getElementById("chatInput");
//     const query = (customQuery !== null ? customQuery : inputElem.value).trim();
//     if (!query) return;

//     // Stop voice if user sends a message
//     stopVoiceInput();
//     stopSpeaking();

//     if (!customQuery) inputElem.value = "";

//     const jurElem = document.getElementById("chatJurisdiction");
//     const jurisdiction = jurElem ? jurElem.value : "india";

//     const messagesContainer = document.getElementById("chatMessages");

//     const userBubble = document.createElement("div");
//     userBubble.className = "message-bubble message-user";
//     userBubble.innerHTML = `<strong>You:</strong> ${query}`;
//     messagesContainer.appendChild(userBubble);

//     const dict = (typeof I18N_TRANSLATIONS !== "undefined" && I18N_TRANSLATIONS[currentLang]) 
//         ? I18N_TRANSLATIONS[currentLang] 
//         : { loadingIntl: "Evaluating International Treaties...", loadingIndia: "Evaluating Indian Statutes..." };
        
//     const loadingText = jurisdiction === "international" ? dict.loadingIntl : dict.loadingIndia;

//     const botBubble = document.createElement("div");
//     botBubble.className = "message-bubble message-assistant";
//     botBubble.innerHTML = `<em>${loadingText}</em>`;
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
//         const rawAnswer = data.answer;
        
//         // FIX: Properly escape single quotes to prevent breaking the HTML onclick attribute
//         const safeText = encodeURIComponent(stripMarkdownForSpeech(rawAnswer)).replace(/'/g, "%27");
        
//         botBubble.innerHTML = `
//             <div>${formatMarkdown(rawAnswer)}</div>
//             <div class="tts-action-row" style="margin-top:0.8rem; display:flex; gap:0.5rem;">
//                 <button class="tts-btn" onclick="playTextToSpeech(decodeURIComponent('${safeText}'))" title="Listen to answer">
//                     <i class="fas fa-volume-up"></i> Listen
//                 </button>
//                 <button class="tts-btn" onclick="stopSpeaking()" title="Stop voice">
//                     <i class="fas fa-stop"></i> Stop
//                 </button>
//             </div>
//         `;
//         messagesContainer.scrollTop = messagesContainer.scrollHeight;

//     } catch (err) {
//         console.error("Chat error:", err);
//         botBubble.innerHTML = `⚠️ <strong>Server Issue:</strong> ${err.message}`;
//     }
// }

// /* ==========================================================================
//    SPEECH-TO-TEXT (STT) - WITH START / STOP TOGGLE
//    ========================================================================== */

// function getLangSTTCode(lang) {
//     const sttMap = {
//         "en": "en-IN",
//         "hi": "hi-IN",
//         "mr": "mr-IN",
//         "ta": "ta-IN",
//         "te": "te-IN",
//         "gu": "gu-IN",
//         "bn": "bn-IN",
//         "sa": "hi-IN" 
//     };
//     return sttMap[lang] || "en-IN";
// }

// function handleVoiceInput() {
//     if (isRecording) {
//         stopVoiceInput();
//         return;
//     }
//     startVoiceInput();
// }

// function startVoiceInput() {
//     const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
//     if (!SpeechRecognition) {
//         alert("Speech recognition is not supported in this browser. Please use Chrome or Edge.");
//         return;
//     }

//     try {
//         recognition = new SpeechRecognition();
//         recognition.lang = getLangSTTCode(currentLang);
//         recognition.interimResults = true;
//         recognition.continuous = false;

//         const voiceBtn = document.getElementById("voiceBtn");
//         const chatInput = document.getElementById("chatInput");

//         recognition.onstart = () => {
//             isRecording = true;
//             if (voiceBtn) {
//                 voiceBtn.classList.add("recording-active");
//                 voiceBtn.innerHTML = `<i class="fas fa-stop" style="color: #FF5252;"></i>`;
//                 voiceBtn.title = "Click to stop recording";
//             }
//             chatInput.placeholder = "Listening... Speak clearly into your microphone...";
//         };

//         recognition.onresult = (event) => {
//             let transcript = "";
//             for (let i = event.resultIndex; i < event.results.length; ++i) {
//                 transcript += event.results[i][0].transcript;
//             }
//             chatInput.value = transcript;
//         };

//         recognition.onerror = (event) => {
//             console.warn("Speech recognition error:", event.error);
//             stopVoiceInput();
//         };

//         recognition.onend = () => {
//             stopVoiceInput();
//             if (chatInput.value.trim().length > 2) {
//                 sendChatMessage();
//             }
//         };

//         recognition.start();

//     } catch (err) {
//         console.error("Recognition start error:", err);
//         stopVoiceInput();
//     }
// }

// function stopVoiceInput() {
//     isRecording = false;
//     const voiceBtn = document.getElementById("voiceBtn");
//     const chatInput = document.getElementById("chatInput");

//     if (voiceBtn) {
//         voiceBtn.classList.remove("recording-active");
//         voiceBtn.innerHTML = `<i class="fas fa-microphone"></i>`;
//         voiceBtn.title = "Voice Input";
//     }
//     if (chatInput) {
//         const dict = (typeof I18N_TRANSLATIONS !== "undefined" && I18N_TRANSLATIONS[currentLang]) ? I18N_TRANSLATIONS[currentLang] : {};
//         chatInput.placeholder = dict.chatPlaceholder || "Ask about Section 3(p), TKDL prior art, Form 25D/25E...";
//     }

//     if (recognition) {
//         try {
//             recognition.stop();
//         } catch (e) {
//             // ignore if already stopped
//         }
//         recognition = null;
//     }
// }


// /* ==========================================================================
//    TEXT-TO-SPEECH (TTS) - READ OUT RESPONSES (CLOUD/BACKEND INTEGRATED)
//    ========================================================================== */

// let currentCloudAudio = null;
// let ttsAbortController = null; // New: Tracks and kills overlapping network requests

// async function playTextToSpeech(text) {
//     // 1. Instantly kill any currently playing audio and cancel pending network requests
//     stopSpeaking(); 

//     // 2. Create a new kill switch for this specific click
//     ttsAbortController = new AbortController();

//     const allVoiceBtns = document.querySelectorAll('.tts-btn');
//     let activeBtn = null;
//     allVoiceBtns.forEach(btn => {
//         if (btn.getAttribute("onclick").includes(encodeURIComponent(text.substring(0, 10)))) {
//             activeBtn = btn;
//             btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Loading...`;
//         }
//     });

//     try {
//         const response = await fetch('/api/tts', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ 
//                 text: text, 
//                 language: currentLang 
//             }),
//             signal: ttsAbortController.signal // Attach the kill switch to the fetch request
//         });

//         if (!response.ok) throw new Error("Cloud TTS generation failed.");

//         const blob = await response.blob();
//         const audioUrl = URL.createObjectURL(blob);
        
//         currentCloudAudio = new Audio(audioUrl);
        
//         currentCloudAudio.onended = () => {
//             if (activeBtn) activeBtn.innerHTML = `<i class="fas fa-volume-up"></i> Listen`;
//         };

//         // Double check that we didn't hit stop while the blob was downloading
//         if (!ttsAbortController.signal.aborted) {
//             await currentCloudAudio.play();
//             if (activeBtn) activeBtn.innerHTML = `<i class="fas fa-volume-up" style="color: #20C997;"></i> Playing`;
//         }

//     } catch (err) {
//         // Ignore the error if we intentionally aborted it by clicking another button
//         if (err.name === 'AbortError') return; 
        
//         console.error("TTS Error:", err);
//         alert("Audio generation failed. Please ensure the backend is running.");
//         if (activeBtn) activeBtn.innerHTML = `<i class="fas fa-volume-up"></i> Listen`;
//     }
// }

// function stopSpeaking() {
//     // 1. Kill any network request that is currently downloading audio
//     if (ttsAbortController) {
//         ttsAbortController.abort();
//         ttsAbortController = null;
//     }

//     // 2. Stop any audio that is currently playing out loud
//     if (currentCloudAudio) {
//         currentCloudAudio.pause();
//         currentCloudAudio.currentTime = 0;
//         currentCloudAudio.src = ""; // Force the browser to dump the audio file from memory
//         currentCloudAudio = null;
//     }
    
//     // 3. Reset all buttons back to normal state
//     const allVoiceBtns = document.querySelectorAll('.tts-btn');
//     allVoiceBtns.forEach(btn => {
//         if (btn.innerHTML.includes("Loading") || btn.innerHTML.includes("Playing")) {
//             btn.innerHTML = `<i class="fas fa-volume-up"></i> Listen`;
//         }
//     });
// }


// <<< BELOW OLD CODE >>>














// /* ==========================================================================
//    TEXT-TO-SPEECH (TTS) - READ OUT RESPONSES (CLOUD/BACKEND INTEGRATED)
//    ========================================================================== */

// async function playTextToSpeech(text) {
//     stopSpeaking(); 

//     const allVoiceBtns = document.querySelectorAll('.tts-btn');
//     let activeBtn = null;
//     allVoiceBtns.forEach(btn => {
//         // Safe check using a smaller substring just to find the active button visually
//         if (btn.getAttribute("onclick").includes(encodeURIComponent(text.substring(0, 10)))) {
//             activeBtn = btn;
//             btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Loading...`;
//         }
//     });

//     try {
//         const response = await fetch('/api/tts', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ 
//                 text: text, 
//                 language: currentLang 
//             })
//         });

//         if (!response.ok) throw new Error("Cloud TTS generation failed.");

//         const blob = await response.blob();
//         const audioUrl = URL.createObjectURL(blob);
        
//         currentCloudAudio = new Audio(audioUrl);
        
//         currentCloudAudio.onended = () => {
//             if (activeBtn) activeBtn.innerHTML = `<i class="fas fa-volume-up"></i> Listen`;
//         };

//         await currentCloudAudio.play();

//         if (activeBtn) activeBtn.innerHTML = `<i class="fas fa-volume-up" style="color: #20C997;"></i> Playing`;

//     } catch (err) {
//         console.error("TTS Error:", err);
//         alert("Audio generation failed. Please ensure the backend is running.");
//         if (activeBtn) activeBtn.innerHTML = `<i class="fas fa-volume-up"></i> Listen`;
//     }
// }

// function stopSpeaking() {
//     if (currentCloudAudio) {
//         currentCloudAudio.pause();
//         currentCloudAudio.currentTime = 0;
//         currentCloudAudio = null;
//     }
    
//     const allVoiceBtns = document.querySelectorAll('.tts-btn');
//     allVoiceBtns.forEach(btn => {
//         if (btn.innerHTML.includes("Loading") || btn.innerHTML.includes("Playing")) {
//             btn.innerHTML = `<i class="fas fa-volume-up"></i> Listen`;
//         }
//     });
// }

// /**
//  * Chat Assistant Controller with STT & TTS for IP Sakti
//  */

// let recognition = null;
// let isRecording = false;
// let currentUtterance = null;

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

// // Clean markdown syntax for clear voice readout
// function stripMarkdownForSpeech(text) {
//     return text
//         .replace(/[#*`_~]/g, '')
//         .replace(/\[(.*?)\]\(.*?\)/g, '$1')
//         .replace(/<[^>]*>/g, '')
//         .trim();
// }

// async function sendChatMessage(customQuery = null) {
//     const inputElem = document.getElementById("chatInput");
//     const query = (customQuery !== null ? customQuery : inputElem.value).trim();
//     if (!query) return;

//     // Stop voice if user sends a message
//     stopVoiceInput();
//     stopSpeaking();

//     if (!customQuery) inputElem.value = "";

//     const jurElem = document.getElementById("chatJurisdiction");
//     const jurisdiction = jurElem ? jurElem.value : "india";

//     const messagesContainer = document.getElementById("chatMessages");

//     const userBubble = document.createElement("div");
//     userBubble.className = "message-bubble message-user";
//     userBubble.innerHTML = `<strong>You:</strong> ${query}`;
//     messagesContainer.appendChild(userBubble);

//     const dict = (typeof I18N_TRANSLATIONS !== "undefined" && I18N_TRANSLATIONS[currentLang]) 
//         ? I18N_TRANSLATIONS[currentLang] 
//         : { loadingIntl: "Evaluating International Treaties...", loadingIndia: "Evaluating Indian Statutes..." };
        
//     const loadingText = jurisdiction === "international" ? dict.loadingIntl : dict.loadingIndia;

//     const botBubble = document.createElement("div");
//     botBubble.className = "message-bubble message-assistant";
//     botBubble.innerHTML = `<em>${loadingText}</em>`;
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
//         const rawAnswer = data.answer;
        
//         // Render answer with TTS button
//         botBubble.innerHTML = `
//             <div>${formatMarkdown(rawAnswer)}</div>
//             <div class="tts-action-row" style="margin-top:0.8rem; display:flex; gap:0.5rem;">
//                 <button class="tts-btn" onclick="playTextToSpeech(decodeURIComponent('${encodeURIComponent(stripMarkdownForSpeech(rawAnswer))}'))" title="Listen to answer">
//                     <i class="fas fa-volume-up"></i> Listen
//                 </button>
//                 <button class="tts-btn" onclick="stopSpeaking()" title="Stop voice">
//                     <i class="fas fa-stop"></i> Stop
//                 </button>
//             </div>
//         `;
//         messagesContainer.scrollTop = messagesContainer.scrollHeight;

//     } catch (err) {
//         console.error("Chat error:", err);
//         botBubble.innerHTML = `⚠️ <strong>Server Issue:</strong> ${err.message}`;
//     }
// }

// /* ==========================================================================
//    SPEECH-TO-TEXT (STT) - WITH START / STOP TOGGLE
//    ========================================================================== */

// function getLangSTTCode(lang) {
//     const sttMap = {
//         "en": "en-IN",
//         "hi": "hi-IN",
//         "mr": "mr-IN",
//         "ta": "ta-IN",
//         "te": "te-IN",
//         "gu": "gu-IN",
//         "bn": "bn-IN",
//         "sa": "hi-IN" // Fallback: Google Speech has no sa-IN; hi-IN phonetics parse Sanskrit accurately
//     };
//     return sttMap[lang] || "en-IN";
// }

// function handleVoiceInput() {
//     if (isRecording) {
//         stopVoiceInput();
//         return;
//     }
//     startVoiceInput();
// }

// function startVoiceInput() {
//     const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
//     if (!SpeechRecognition) {
//         alert("Speech recognition is not supported in this browser. Please use Chrome or Edge.");
//         return;
//     }

//     try {
//         recognition = new SpeechRecognition();
//         recognition.lang = getLangSTTCode(currentLang);
//         recognition.interimResults = true;
//         recognition.continuous = false;

//         const voiceBtn = document.getElementById("voiceBtn");
//         const chatInput = document.getElementById("chatInput");

//         recognition.onstart = () => {
//             isRecording = true;
//             if (voiceBtn) {
//                 voiceBtn.classList.add("recording-active");
//                 voiceBtn.innerHTML = `<i class="fas fa-stop" style="color: #FF5252;"></i>`;
//                 voiceBtn.title = "Click to stop recording";
//             }
//             chatInput.placeholder = "Listening... Speak clearly into your microphone...";
//         };

//         recognition.onresult = (event) => {
//             let transcript = "";
//             for (let i = event.resultIndex; i < event.results.length; ++i) {
//                 transcript += event.results[i][0].transcript;
//             }
//             chatInput.value = transcript;
//         };

//         recognition.onerror = (event) => {
//             console.warn("Speech recognition error:", event.error);
//             stopVoiceInput();
//         };

//         recognition.onend = () => {
//             stopVoiceInput();
//             if (chatInput.value.trim().length > 2) {
//                 sendChatMessage();
//             }
//         };

//         recognition.start();

//     } catch (err) {
//         console.error("Recognition start error:", err);
//         stopVoiceInput();
//     }
// }

// function stopVoiceInput() {
//     isRecording = false;
//     const voiceBtn = document.getElementById("voiceBtn");
//     const chatInput = document.getElementById("chatInput");

//     if (voiceBtn) {
//         voiceBtn.classList.remove("recording-active");
//         voiceBtn.innerHTML = `<i class="fas fa-microphone"></i>`;
//         voiceBtn.title = "Voice Input";
//     }
//     if (chatInput) {
//         const dict = (typeof I18N_TRANSLATIONS !== "undefined" && I18N_TRANSLATIONS[currentLang]) ? I18N_TRANSLATIONS[currentLang] : {};
//         chatInput.placeholder = dict.chatPlaceholder || "Ask about Section 3(p), TKDL prior art, Form 25D/25E...";
//     }

//     if (recognition) {
//         try {
//             recognition.stop();
//         } catch (e) {
//             // ignore if already stopped
//         }
//         recognition = null;
//     }
// }

// /* ==========================================================================
//    TEXT-TO-SPEECH (TTS) - READ OUT RESPONSES (CLOUD/BACKEND INTEGRATED)
//    ========================================================================== */

// let currentCloudAudio = null;

// async function playTextToSpeech(text) {
//     stopSpeaking(); // Stop anything currently playing

//     // Find the specific button that was clicked and make it spin
//     const allVoiceBtns = document.querySelectorAll('.tts-btn');
//     let activeBtn = null;
//     allVoiceBtns.forEach(btn => {
//         if (btn.getAttribute("onclick").includes(encodeURIComponent(text.substring(0, 10)))) {
//             activeBtn = btn;
//             btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Loading...`;
//         }
//     });

//     try {
//         const response = await fetch('/api/tts', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ 
//                 text: text, 
//                 language: currentLang 
//             })
//         });

//         if (!response.ok) throw new Error("Cloud TTS generation failed.");

//         const blob = await response.blob();
//         const audioUrl = URL.createObjectURL(blob);
        
//         currentCloudAudio = new Audio(audioUrl);
        
//         // Reset the button when audio finishes naturally
//         currentCloudAudio.onended = () => {
//             if (activeBtn) activeBtn.innerHTML = `<i class="fas fa-volume-up"></i> Listen`;
//         };

//         await currentCloudAudio.play();

//         // Change button to show playing state
//         if (activeBtn) activeBtn.innerHTML = `<i class="fas fa-volume-up" style="color: #20C997;"></i> Playing`;

//     } catch (err) {
//         console.error("TTS Error:", err);
//         alert("Audio generation failed. Please ensure the backend is running.");
//         if (activeBtn) activeBtn.innerHTML = `<i class="fas fa-volume-up"></i> Listen`;
//     }
// }

// function stopSpeaking() {
//     if (currentCloudAudio) {
//         currentCloudAudio.pause();
//         currentCloudAudio.currentTime = 0;
//         currentCloudAudio = null;
//     }
    
//     // Reset all buttons back to normal state
//     const allVoiceBtns = document.querySelectorAll('.tts-btn');
//     allVoiceBtns.forEach(btn => {
//         if (btn.innerHTML.includes("Loading") || btn.innerHTML.includes("Playing")) {
//             btn.innerHTML = `<i class="fas fa-volume-up"></i> Listen`;
//         }
//     });
// }

// // /* ==========================================================================
// //    TEXT-TO-SPEECH (TTS) - READ OUT RESPONSES
// //    ========================================================================== */

// // function playTextToSpeech(text) {
// //     if (!('speechSynthesis' in window)) {
// //         alert("Text-to-speech is not supported in this browser.");
// //         return;
// //     }

// //     stopSpeaking();

// //     currentUtterance = new SpeechSynthesisUtterance(text);
// //     const targetLocale = getLangSTTCode(currentLang);
// //     currentUtterance.lang = targetLocale;

// //     // Pick an Indian accent voice if available
// //     const voices = window.speechSynthesis.getVoices();
// //     const matchedVoice = voices.find(v => v.lang === targetLocale || v.lang.replace('_', '-') === targetLocale);
// //     if (matchedVoice) {
// //         currentUtterance.voice = matchedVoice;
// //     }

// //     currentUtterance.rate = 1.0;
// //     currentUtterance.pitch = 1.0;

// //     window.speechSynthesis.speak(currentUtterance);
// // }

// // function stopSpeaking() {
// //     if ('speechSynthesis' in window) {
// //         window.speechSynthesis.cancel();
// //     }
// // }

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

// //     const jurElem = document.getElementById("chatJurisdiction");
// //     const jurisdiction = jurElem ? jurElem.value : "india";

// //     const messagesContainer = document.getElementById("chatMessages");

// //     const userBubble = document.createElement("div");
// //     userBubble.className = "message-bubble message-user";
// //     userBubble.innerHTML = `<strong>You:</strong> ${query}`;
// //     messagesContainer.appendChild(userBubble);

// //     // Get translated loading text based on current language and jurisdiction
// //     const dict = I18N_TRANSLATIONS[currentLang] || I18N_TRANSLATIONS["en"];
// //     const loadingText = jurisdiction === "international" ? dict.loadingIntl : dict.loadingIndia;

// //     const botBubble = document.createElement("div");
// //     botBubble.className = "message-bubble message-assistant";
// //     botBubble.innerHTML = `<em>${loadingText}</em>`;
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
// //             const errText = await response.text();
// //             throw new Error(`Server returned HTTP ${response.status}: ${errText}`);
// //         }

// //         const data = await response.json();
// //         botBubble.innerHTML = formatMarkdown(data.answer);
// //         messagesContainer.scrollTop = messagesContainer.scrollHeight;

// //     } catch (err) {
// //         console.error("Chat error:", err);
// //         botBubble.innerHTML = `⚠️ <strong>Server Issue:</strong> ${err.message}`;
// //     }
// // }

// // function handleVoiceInput() {
// //     if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
// //         alert("Speech recognition is not supported in this browser. Please type your query.");
// //         return;
// //     }
// //     const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
// //     const recognition = new SpeechRecognition();
// //     recognition.lang = currentLang === 'hi' ? 'hi-IN' : (currentLang === 'mr' ? 'mr-IN' : (currentLang === 'sa' ? 'sa-IN' : (currentLang === 'ta' ? 'ta-IN' : 'en-US')));
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

// // // /**
// // //  * Chat Assistant Controller for IP Sakti
// // //  */

// // // function formatMarkdown(text) {
// // //     if (!text) return "";
// // //     let html = text
// // //         .replace(/### (.*?)\n/g, '<h3>$1</h3>')
// // //         .replace(/#### (.*?)\n/g, '<h4>$1</h4>')
// // //         .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
// // //         .replace(/\*(.*?)\*/g, '<em>$1</em>')
// // //         .replace(/`([^`]+)`/g, '<code>$1</code>')
// // //         .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
// // //         .replace(/\n- (.*?)/g, '<br>• $1')
// // //         .replace(/\n1\. (.*?)/g, '<br>1. $1')
// // //         .replace(/\n2\. (.*?)/g, '<br>2. $1')
// // //         .replace(/\n3\. (.*?)/g, '<br>3. $1')
// // //         .replace(/\n4\. (.*?)/g, '<br>4. $1')
// // //         .replace(/\n/g, '<br>');
// // //     return html;
// // // }

// // // async function sendChatMessage(customQuery = null) {
// // //     const inputElem = document.getElementById("chatInput");
// // //     const query = (customQuery !== null ? customQuery : inputElem.value).trim();
// // //     if (!query) return;

// // //     if (!customQuery) inputElem.value = "";

// // //     const jurElem = document.getElementById("chatJurisdiction");
// // //     const jurisdiction = jurElem ? jurElem.value : "india";

// // //     const messagesContainer = document.getElementById("chatMessages");

// // //     const userBubble = document.createElement("div");
// // //     userBubble.className = "message-bubble message-user";
// // //     userBubble.innerHTML = `<strong>You:</strong> ${query}`;
// // //     messagesContainer.appendChild(userBubble);

// // //     const botBubble = document.createElement("div");
// // //     botBubble.className = "message-bubble message-assistant";
// // //     const jurTag = jurisdiction === "international" ? "International Treaties (WIPO/PCT)" : "Indian Statutes (Patents Act/AYUSH/NBA)";
// // //     botBubble.innerHTML = `<em>🌿 IP Sakti is evaluating ${jurTag}...</em>`;
// // //     messagesContainer.appendChild(botBubble);
// // //     messagesContainer.scrollTop = messagesContainer.scrollHeight;

// // //     try {
// // //         const response = await fetch("/api/chat", {
// // //             method: "POST",
// // //             headers: { "Content-Type": "application/json" },
// // //             body: JSON.stringify({
// // //                 query: query,
// // //                 language: currentLang,
// // //                 jurisdiction: jurisdiction
// // //             })
// // //         });

// // //         if (!response.ok) {
// // //             const errText = await response.text();
// // //             throw new Error(`Server returned HTTP ${response.status}: ${errText}`);
// // //         }

// // //         const data = await response.json();
// // //         botBubble.innerHTML = formatMarkdown(data.answer);
// // //         messagesContainer.scrollTop = messagesContainer.scrollHeight;

// // //     } catch (err) {
// // //         console.error("Chat error:", err);
// // //         botBubble.innerHTML = `⚠️ <strong>Server Issue:</strong> ${err.message}`;
// // //     }
// // // }

// // // function handleVoiceInput() {
// // //     if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
// // //         alert("Speech recognition is not supported in this browser. Please type your query.");
// // //         return;
// // //     }
// // //     const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
// // //     const recognition = new SpeechRecognition();
// // //     recognition.lang = currentLang === 'hi' ? 'hi-IN' : (currentLang === 'mr' ? 'mr-IN' : (currentLang === 'sa' ? 'sa-IN' : 'en-US'));
// // //     recognition.interimResults = false;

// // //     const voiceBtn = document.getElementById("voiceBtn");
// // //     voiceBtn.style.color = "#FF5252";

// // //     recognition.onresult = (event) => {
// // //         const transcript = event.results[0][0].transcript;
// // //         document.getElementById("chatInput").value = transcript;
// // //         voiceBtn.style.color = "#E6C265";
// // //         sendChatMessage(transcript);
// // //     };

// // //     recognition.onerror = () => {
// // //         voiceBtn.style.color = "#E6C265";
// // //     };

// // //     recognition.onend = () => {
// // //         voiceBtn.style.color = "#E6C265";
// // //     };

// // //     recognition.start();
// // // }

// // // // /**
// // // //  * Chat Assistant Controller for IP Sakti
// // // //  */

// // // // function formatMarkdown(text) {
// // // //     if (!text) return "";
// // // //     let html = text
// // // //         .replace(/### (.*?)\n/g, '<h3>$1</h3>')
// // // //         .replace(/#### (.*?)\n/g, '<h4>$1</h4>')
// // // //         .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
// // // //         .replace(/\*(.*?)\*/g, '<em>$1</em>')
// // // //         .replace(/`([^`]+)`/g, '<code>$1</code>')
// // // //         .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
// // // //         .replace(/\n- (.*?)/g, '<br>• $1')
// // // //         .replace(/\n1\. (.*?)/g, '<br>1. $1')
// // // //         .replace(/\n2\. (.*?)/g, '<br>2. $1')
// // // //         .replace(/\n3\. (.*?)/g, '<br>3. $1')
// // // //         .replace(/\n4\. (.*?)/g, '<br>4. $1')
// // // //         .replace(/\n/g, '<br>');
// // // //     return html;
// // // // }

// // // // async function sendChatMessage(customQuery = null) {
// // // //     const inputElem = document.getElementById("chatInput");
// // // //     const query = (customQuery !== null ? customQuery : inputElem.value).trim();
// // // //     if (!query) return;

// // // //     if (!customQuery) inputElem.value = "";

// // // //     // Read selected jurisdiction
// // // //     const jurElem = document.getElementById("chatJurisdiction");
// // // //     const jurisdiction = jurElem ? jurElem.value : "india";

// // // //     const messagesContainer = document.getElementById("chatMessages");

// // // //     // Render User Bubble
// // // //     const userBubble = document.createElement("div");
// // // //     userBubble.className = "message-bubble message-user";
// // // //     userBubble.innerHTML = `<strong>You:</strong> ${query}`;
// // // //     messagesContainer.appendChild(userBubble);

// // // //     // Render Assistant Loading State
// // // //     const botBubble = document.createElement("div");
// // // //     botBubble.className = "message-bubble message-assistant";
// // // //     const jurTag = jurisdiction === "international" ? "International Treaties (WIPO/PCT)" : "Indian Statutes (Patents Act/AYUSH/NBA)";
// // // //     botBubble.innerHTML = `<em>🌿 IP Sakti is evaluating ${jurTag}...</em>`;
// // // //     messagesContainer.appendChild(botBubble);
// // // //     messagesContainer.scrollTop = messagesContainer.scrollHeight;

// // // //     try {
// // // //         const response = await fetch("/api/chat", {
// // // //             method: "POST",
// // // //             headers: { "Content-Type": "application/json" },
// // // //             body: JSON.stringify({
// // // //                 query: query,
// // // //                 language: currentLang,
// // // //                 jurisdiction: jurisdiction
// // // //             })
// // // //         });

// // // //         if (!response.ok) {
// // // //             throw new Error(`Server returned status ${response.status}`);
// // // //         }

// // // //         const data = await response.json();
// // // //         botBubble.innerHTML = formatMarkdown(data.answer);
// // // //         messagesContainer.scrollTop = messagesContainer.scrollHeight;

// // // //     } catch (err) {
// // // //         console.error("Chat error:", err);
// // // //         botBubble.innerHTML = `⚠️ <strong>System Error:</strong> Unable to reach the IP Sakti backend. Please ensure the server is active.`;
// // // //     }
// // // // }

// // // // function handleVoiceInput() {
// // // //     if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
// // // //         alert("Speech recognition is not supported in this browser. Please type your query.");
// // // //         return;
// // // //     }
// // // //     const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
// // // //     const recognition = new SpeechRecognition();
// // // //     recognition.lang = currentLang === 'hi' ? 'hi-IN' : (currentLang === 'mr' ? 'mr-IN' : (currentLang === 'sa' ? 'sa-IN' : 'en-US'));
// // // //     recognition.interimResults = false;

// // // //     const voiceBtn = document.getElementById("voiceBtn");
// // // //     voiceBtn.style.color = "#FF5252";

// // // //     recognition.onresult = (event) => {
// // // //         const transcript = event.results[0][0].transcript;
// // // //         document.getElementById("chatInput").value = transcript;
// // // //         voiceBtn.style.color = "#E6C265";
// // // //         sendChatMessage(transcript);
// // // //     };

// // // //     recognition.onerror = () => {
// // // //         voiceBtn.style.color = "#E6C265";
// // // //     };

// // // //     recognition.onend = () => {
// // // //         voiceBtn.style.color = "#E6C265";
// // // //     };

// // // //     recognition.start();
// // // // }