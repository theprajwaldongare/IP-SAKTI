/**
 * National Biodiversity Act (NBA) Royalty Calculator Controller
 */

async function calculateNbaAbs() {
    const turnoverInput = parseFloat(document.getElementById("nbaTurnover").value);
    const entityType = document.getElementById("nbaEntity").value;

    if (isNaN(turnoverInput) || turnoverInput <= 0) {
        alert("Please enter a valid turnover amount in ₹ INR.");
        return;
    }

    const resultBox = document.getElementById("nbaResults");
    resultBox.style.display = "block";

    try {
        const response = await fetch("/api/nba-calculator", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                annual_turnover_inr: turnoverInput,
                entity_type: entityType,
                bio_resource_origin: "cultivated"
            })
        });

        if (!response.ok) throw new Error("NBA calculator request failed");

        const data = await response.json();

        const formattedTurnover = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(data.annual_turnover_inr);
        const formattedRoyalty = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(data.estimated_royalty_inr);

        let html = `
            <div class="glass-card" style="border-color: var(--primary-mint);">
                <h3 class="card-title"><i class="fas fa-seedling"></i> NBA Access & Benefit Sharing Assessment</h3>
                
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:1rem; margin:1.2rem 0;">
                    <div style="background:rgba(0,0,0,0.3); padding:1rem; border-radius:10px;">
                        <span style="font-size:0.8rem; color:var(--text-muted);">Annual Ex-Factory Sales</span>
                        <div style="font-weight:700; font-size:1.1rem; color:#FFF; margin-top:0.3rem;">${formattedTurnover}</div>
                    </div>
                    <div style="background:rgba(0,0,0,0.3); padding:1rem; border-radius:10px;">
                        <span style="font-size:0.8rem; color:var(--text-muted);">Applicable ABS Royalty Rate</span>
                        <div style="font-weight:700; font-size:1.1rem; color:var(--accent-gold); margin-top:0.3rem;">${data.abs_percentage}%</div>
                    </div>
                    <div style="background:rgba(0,0,0,0.3); padding:1rem; border-radius:10px;">
                        <span style="font-size:0.8rem; color:var(--text-muted);">Estimated Annual Royalty Obligation</span>
                        <div style="font-weight:700; font-size:1.1rem; color:var(--primary-mint); margin-top:0.3rem;">${formattedRoyalty}</div>
                    </div>
                    <div style="background:rgba(0,0,0,0.3); padding:1rem; border-radius:10px;">
                        <span style="font-size:0.8rem; color:var(--text-muted);">Mandatory Clearance Application</span>
                        <div style="font-weight:700; font-size:0.95rem; color:#FFF; margin-top:0.3rem;">${data.nba_approval_form}</div>
                    </div>
                </div>

                <div style="background:rgba(230, 194, 101, 0.1); border:1px solid var(--border-gold); padding:1rem; border-radius:10px; margin-top:1rem; font-size:0.88rem; line-height:1.5;">
                    <strong style="color:var(--accent-gold);"><i class="fas fa-gavel"></i> Legal Requirement Note:</strong><br>
                    ${data.legal_mandatory_note}
                </div>
            </div>
        `;

        resultBox.innerHTML = html;
        resultBox.scrollIntoView({ behavior: "smooth" });

    } catch (err) {
        console.error("NBA calculator error:", err);
        resultBox.innerHTML = `⚠️ Error calculating ABS royalty.`;
    }
}
