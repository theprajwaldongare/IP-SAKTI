/**
 * Regulatory License Wizard Controller
 */

async function runLicenseWizard() {
    const category = document.getElementById("wizCategory").value;
    const claims = document.getElementById("wizClaims").value === "true";
    const dosage = document.getElementById("wizDosage").value;
    const source = document.getElementById("wizSource").value;

    const resultBox = document.getElementById("wizardResults");
    resultBox.style.display = "block";
    resultBox.innerHTML = `<em>Calculating regulatory pathway...</em>`;

    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/regulatory-wizard`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                product_category: category,
                therapeutic_claims: claims,
                dosage_form: dosage,
                ingredients_source: source,
                language: currentLang
            })
        });

        if (!response.ok) throw new Error("Wizard server request failed");

        const data = await response.json();

        let badgeStyle = "background:rgba(32, 201, 151, 0.2); color:var(--primary-mint); border:1px solid var(--primary-mint);";
        if (data.form_number.includes("25E")) {
            badgeStyle = "background:rgba(230, 194, 101, 0.2); color:var(--accent-gold); border:1px solid var(--accent-gold);";
        } else if (data.fssai_applicable) {
            badgeStyle = "background:rgba(30, 144, 255, 0.2); color:#1E90FF; border:1px solid #1E90FF;";
        }

        let html = `
            <div class="glass-card">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
                    <div>
                        <h3 class="card-title"><i class="fas fa-file-contract"></i> ${data.recommended_license}</h3>
                        <p class="card-subtitle">Governing Body: <strong>${data.governing_authority}</strong></p>
                    </div>
                    <div>
                        <span class="risk-badge" style="${badgeStyle}">
                            ${data.form_number}
                        </span>
                    </div>
                </div>

                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:1rem; margin:1rem 0;">
                    <div style="background:rgba(0,0,0,0.3); padding:0.8rem; border-radius:8px;">
                        <span style="font-size:0.8rem; color:var(--text-muted);">CTRI Clinical Trial</span>
                        <div style="font-weight:700; color:${data.ctri_trial_needed ? 'var(--warning)' : 'var(--primary-mint)'}; font-size:0.95rem;">
                            ${data.ctri_trial_needed ? 'Mandatory Trial Registration' : 'Exempt (Classical Record)'}
                        </div>
                    </div>
                    <div style="background:rgba(0,0,0,0.3); padding:0.8rem; border-radius:8px;">
                        <span style="font-size:0.8rem; color:var(--text-muted);">Safety & Toxicity Data</span>
                        <div style="font-weight:700; color:${data.safety_toxicity_needed ? 'var(--warning)' : 'var(--primary-mint)'}; font-size:0.95rem;">
                            ${data.safety_toxicity_needed ? 'Rule 158B Evidence Required' : 'Historical Pharmacopoeial Proof'}
                        </div>
                    </div>
                    <div style="background:rgba(0,0,0,0.3); padding:0.8rem; border-radius:8px;">
                        <span style="font-size:0.8rem; color:var(--text-muted);">FSSAI Compliance</span>
                        <div style="font-weight:700; color:${data.fssai_applicable ? '#1E90FF' : 'var(--text-muted)'}; font-size:0.95rem;">
                            ${data.fssai_applicable ? 'Food Safety License Required' : 'AYUSH SLA Exemption'}
                        </div>
                    </div>
                </div>

                <h4 style="color:var(--accent-gold); margin-top:1rem;">📋 Mandatory Regulatory Steps:</h4>
                <ul style="margin-left:1.2rem; margin-top:0.5rem; line-height:1.6;">
                    ${data.key_requirements.map(req => `<li>${req}</li>`).join('')}
                </ul>
            </div>
        `;

        resultBox.innerHTML = html;
        resultBox.scrollIntoView({ behavior: "smooth" });

    } catch (err) {
        console.error("Wizard error:", err);
        resultBox.innerHTML = `⚠️ Error calculating license requirement.`;
    }
}
