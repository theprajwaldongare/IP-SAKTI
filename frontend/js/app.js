/**
 * Main Application Orchestrator for IP Sakti
 */

document.addEventListener("DOMContentLoaded", () => {
    // Initial health check
    checkBackendHealth();

    // Tab Navigation Handling
    const navButtons = document.querySelectorAll(".nav-btn");
    navButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");
            
            navButtons.forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-view").forEach(tab => tab.classList.remove("active"));
            
            btn.classList.add("active");
            document.getElementById(targetTab).classList.add("active");
        });
    });

    // Language selector change
    const langSelect = document.getElementById("langSelect");
    if (langSelect) {
        setAppLanguage(langSelect.value);
        langSelect.addEventListener("change", (e) => {
            setAppLanguage(e.target.value);
        });
    }

    // Chat textarea enter key trigger
    const chatInput = document.getElementById("chatInput");
    if (chatInput) {
        chatInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }

    // Load initial TKDL grid
    fetchTkdlData();
});

async function checkBackendHealth() {
    const statusPill = document.getElementById("statusPill");
    try {
        const res = await fetch(`${CONFIG.API_BASE_URL}/health`);
        if (res.ok) {
            const data = await res.json();
            statusPill.innerHTML = `
                <div class="status-dot"></div>
                <span>Backend RAG Active ${data.gemini_api_configured ? '' : '(Offline Synthesis)'}</span>
            `;
            statusPill.style.borderColor = "var(--primary-mint)";
        } else {
            throw new Error("Health check failed");
        }
    } catch (err) {
        console.warn("Backend not reachable directly via relative URL. Setting local dev indicator.", err);
        statusPill.innerHTML = `
            <div class="status-dot" style="background-color:var(--warning); box-shadow:0 0 8px var(--warning);"></div>
            <span>RAG Active (Local FastAPI)</span>
        `;
    }
}

async function fetchTkdlData(query = "") {
    const tableBody = document.getElementById("tkdlTableBody");
    if (!tableBody) return;

    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/tkdl-search?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error("Failed to fetch TKDL data");

        const data = await response.json();
        
        if (data.results.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:var(--text-muted);">No records found for '${query}'. Try searching 'turmeric', 'ashwagandha', or 'neem'.</td></tr>`;
            return;
        }

        let html = "";
        data.results.forEach(item => {
            html += `
                <tr>
                    <td><strong>${item.name.toUpperCase()}</strong></td>
                    <td><code>${item.sanskrit}</code></td>
                    <td><em>${item.latin}</em></td>
                    <td><span class="risk-badge" style="background:rgba(30,107,84,0.3); color:var(--accent-gold);">${item.ipc}</span></td>
                    <td style="font-size:0.82rem; color:var(--text-muted);">${item.tkdl_status}</td>
                </tr>
            `;
        });

        tableBody.innerHTML = html;
    } catch (err) {
        console.error("TKDL fetch error:", err);
    }
}

function searchTkdl() {
    const query = document.getElementById("tkdlSearchInput").value.trim();
    fetchTkdlData(query);
}

// /**
//  * Main Application Orchestrator for IP Sakti
//  */

// document.addEventListener("DOMContentLoaded", () => {
//     // Initial health check
//     checkBackendHealth();

//     // Tab Navigation Handling
//     const navButtons = document.querySelectorAll(".nav-btn");
//     navButtons.forEach(btn => {
//         btn.addEventListener("click", () => {
//             const targetTab = btn.getAttribute("data-tab");
            
//             navButtons.forEach(b => b.classList.remove("active"));
//             document.querySelectorAll(".tab-view").forEach(tab => tab.classList.remove("active"));
            
//             btn.classList.add("active");
//             document.getElementById(targetTab).classList.add("active");
//         });
//     });

//     // Language selector change
//     const langSelect = document.getElementById("langSelect");
//     if (langSelect) {
//         langSelect.addEventListener("change", (e) => {
//             setAppLanguage(e.target.value);
//         });
//     }

//     // Chat textarea enter key trigger
//     const chatInput = document.getElementById("chatInput");
//     if (chatInput) {
//         chatInput.addEventListener("keydown", (e) => {
//             if (e.key === "Enter" && !e.shiftKey) {
//                 e.preventDefault();
//                 sendChatMessage();
//             }
//         });
//     }

//     // Load initial TKDL grid
//     fetchTkdlData();
// });

// async function checkBackendHealth() {
//     const statusPill = document.getElementById("statusPill");
//     try {
//         const res = await fetch("/health");
//         if (res.ok) {
//             const data = await res.json();
//             statusPill.innerHTML = `
//                 <div class="status-dot"></div>
//                 <span>Backend RAG Active ${data.gemini_api_configured ? '(Gemini AI)' : '(Offline Synthesis)'}</span>
//             `;
//             statusPill.style.borderColor = "var(--primary-mint)";
//         } else {
//             throw new Error("Health check failed");
//         }
//     } catch (err) {
//         console.warn("Backend not reachable directly via relative URL. Setting local dev indicator.", err);
//         statusPill.innerHTML = `
//             <div class="status-dot" style="background-color:var(--warning); box-shadow:0 0 8px var(--warning);"></div>
//             <span>RAG Active (Local FastAPI)</span>
//         `;
//     }
// }

// async function fetchTkdlData(query = "") {
//     const tableBody = document.getElementById("tkdlTableBody");
//     if (!tableBody) return;

//     try {
//         const response = await fetch(`/api/tkdl-search?q=${encodeURIComponent(query)}`);
//         if (!response.ok) throw new Error("Failed to fetch TKDL data");

//         const data = await response.json();
        
//         if (data.results.length === 0) {
//             tableBody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:var(--text-muted);">No records found for '${query}'. Try searching 'turmeric', 'ashwagandha', or 'neem'.</td></tr>`;
//             return;
//         }

//         let html = "";
//         data.results.forEach(item => {
//             html += `
//                 <tr>
//                     <td><strong>${item.name.toUpperCase()}</strong></td>
//                     <td><code>${item.sanskrit}</code></td>
//                     <td><em>${item.latin}</em></td>
//                     <td><span class="risk-badge" style="background:rgba(30,107,84,0.3); color:var(--accent-gold);">${item.ipc}</span></td>
//                     <td style="font-size:0.82rem; color:var(--text-muted);">${item.tkdl_status}</td>
//                 </tr>
//             `;
//         });

//         tableBody.innerHTML = html;
//     } catch (err) {
//         console.error("TKDL fetch error:", err);
//     }
// }

// function searchTkdl() {
//     const query = document.getElementById("tkdlSearchInput").value.trim();
//     fetchTkdlData(query);
// }
