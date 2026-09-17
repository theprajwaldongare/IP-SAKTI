/**
 * Formulation Patentability Analyzer Controller
 */

async function runFormulationAnalysis() {
    const nameInput = document.getElementById("formName").value.trim();
    const ingredientsInput = document.getElementById("formIngredients").value.trim();
    const noveltyInput = document.getElementById("formNovelty").value.trim();
    const intendedInput = document.getElementById("formIntended").value.trim();

    if (!nameInput || !ingredientsInput) {
        alert("Please enter the formulation name and at least one herbal ingredient.");
        return;
    }

    const ingredientsList = ingredientsInput.split(",").map(i => i.trim()).filter(i => i.length > 0);
    const resultsContainer = document.getElementById("analyzerResults");
    resultsContainer.style.display = "block";
    resultsContainer.innerHTML = `<em>Evaluating Section 3(p), TKDL prior art, and NBA ABS compliance...</em>`;

    try {
        const response = await fetch("/api/analyze-formulation", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                formulation_name: nameInput,
                ingredients: ingredientsList,
                novelty_description: noveltyInput,
                intended_use: intendedInput,
                language: currentLang
            })
        });

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }

        const data = await response.json();
        const risk = data.risk_assessment;

        let riskBadgeClass = "risk-low";
        if (risk.overall_score < 40) riskBadgeClass = "risk-high";
        else if (risk.overall_score < 70) riskBadgeClass = "risk-med";

        let html = `
            <div class="glass-card" style="border-color: var(--accent-gold);">
                <div style="display:flex; justify-shadow:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
                    <div>
                        <h3 class="card-title"><i class="fas fa-microscope"></i> ${data.formulation_name}</h3>
                        <p class="card-subtitle">Patentability Score: <strong>${risk.overall_score} / 100</strong></p>
                    </div>
                    <div>
                        <span class="risk-badge ${riskBadgeClass}">
                            Score Index: ${risk.overall_score}/100
                        </span>
                    </div>
                </div>

                <div class="score-meter">
                    <div class="score-fill" style="width: ${risk.overall_score}%;"></div>
                </div>

                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:1rem; margin:1.2rem 0;">
                    <div style="background:rgba(0,0,0,0.3); padding:1rem; border-radius:10px; border-left:4px solid var(--danger);">
                        <div style="font-size:0.8rem; color:var(--text-muted);">Section 3(p) Traditional Knowledge Risk</div>
                        <div style="font-weight:600; font-size:0.9rem; margin-top:0.3rem;">${risk.sec_3p_risk}</div>
                    </div>
                    <div style="background:rgba(0,0,0,0.3); padding:1rem; border-radius:10px; border-left:4px solid var(--warning);">
                        <div style="font-size:0.8rem; color:var(--text-muted);">Section 3(e) Synergy Requirement</div>
                        <div style="font-weight:600; font-size:0.9rem; margin-top:0.3rem;">${risk.sec_3e_synergy_risk}</div>
                    </div>
                    <div style="background:rgba(0,0,0,0.3); padding:1rem; border-radius:10px; border-left:4px solid var(--primary-mint);">
                        <div style="font-size:0.8rem; color:var(--text-muted);">TKDL Prior Art Overlap</div>
                        <div style="font-weight:600; font-size:0.9rem; margin-top:0.3rem;">${risk.tkdl_prior_art_overlap}</div>
                    </div>
                    <div style="background:rgba(0,0,0,0.3); padding:1rem; border-radius:10px; border-left:4px solid var(--accent-gold);">
                        <div style="font-size:0.8rem; color:var(--text-muted);">Recommended IPC Codes</div>
                        <div style="font-weight:600; font-size:0.9rem; margin-top:0.3rem;">${risk.recommended_ipc.join(", ")}</div>
                    </div>
                </div>

                <h4 style="color:var(--accent-gold); margin-top:1rem;">🎯 Strategic Patent Recommendations:</h4>
                <ul style="margin-left:1.2rem; margin-top:0.5rem; line-height:1.6;">
                    ${risk.recommendations.map(r => `<li>${r}</li>`).join('')}
                </ul>

                <details style="margin-top:1.5rem; background:rgba(0,0,0,0.4); padding:1rem; border-radius:10px;">
                    <summary style="cursor:pointer; color:var(--accent-gold); font-weight:600;">Click to view full RAG Patentability Evaluation Report</summary>
                    <div style="margin-top:1rem; line-height:1.6;">${formatMarkdown(data.detailed_report)}</div>
                </details>
            </div>
        `;

        resultsContainer.innerHTML = html;
        resultsContainer.scrollIntoView({ behavior: "smooth" });

    } catch (err) {
        console.error("Analyzer error:", err);
        resultsContainer.innerHTML = `⚠️ <strong>Error analyzing formulation:</strong> Check backend connection.`;
    }
}
