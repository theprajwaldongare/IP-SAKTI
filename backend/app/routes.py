"""
FastAPI Router for IP Sakti Endpoints.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.schemas import (
    ChatRequest, ChatResponse,
    FormulationAnalysisRequest, FormulationAnalysisResponse, PatentabilityRiskScore,
    LicenseWizardRequest, LicenseWizardResponse,
    NBACalculatorRequest, NBACalculatorResponse
)
from app.rag_engine import retrieve_context
from app.llm_service import generate_rag_response
from app.multilingual import LANGUAGES
from app.kb_data import KNOWLEDGE_BASE, AYURVEDIC_IPC_GLOSSARY

router = APIRouter()

@router.get("/languages")
def get_supported_languages():
    """Return list of supported languages."""
    return LANGUAGES

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    RAG-powered Chat Assistant for Ayurvedic IP & Regulatory Queries.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")
        
    rag_data = retrieve_context(request.query)
    answer = generate_rag_response(request.query, request.language, rag_data)
    
    return ChatResponse(
        query=request.query,
        language=request.language,
        answer=answer,
        citations=rag_data["citations"],
        matched_ingredients=rag_data["matched_ingredients"]
    )

@router.post("/analyze-formulation", response_model=FormulationAnalysisResponse)
def analyze_formulation_endpoint(request: FormulationAnalysisRequest):
    """
    Analyze Ayurvedic Formulation for Patentability under Sec 3(p), 3(e), TKDL prior art, and NBA compliance.
    """
    ingredients_lower = [i.lower().strip() for i in request.ingredients]
    novelty_text = request.novelty_description.lower()
    
    # Analyze components against TKDL & Patent Law rules
    matched_glossary = []
    tkdl_overlap_count = 0
    recommended_ipc = ["A61K 36/00"]
    
    for ing in ingredients_lower:
        for name, data in AYURVEDIC_IPC_GLOSSARY.items():
            if name in ing or ing in name:
                matched_glossary.append(data)
                tkdl_overlap_count += 1
                if data["ipc"] not in recommended_ipc:
                    recommended_ipc.append(data["ipc"])
                    
    # Calculate score metrics
    base_score = 45 # Default mid score for traditional formulations
    
    # Has novel drug delivery or special processing?
    novel_keywords = ["liposomal", "nano", "phytosome", "extract ratio", "standardized biomarker", "synergistic ratio", "bio-enhancer", "asava", "samskara"]
    has_novel_tech = any(kw in novelty_text for kw in novel_keywords) or any(kw in request.formulation_name.lower() for kw in novel_keywords)
    
    if has_novel_tech:
        base_score += 35
        sec_3p_risk = "Low-Medium (Novel Technology / Delivery System Claimed)"
        sec_3e_risk = "Low (Synergistic Bioavailability Enhancement Claimed)"
    else:
        sec_3p_risk = "High (Classical Combination Risk under Indian Patent Act Sec 3(p))"
        sec_3e_risk = "High (Requires Quantitative Experimental Synergy Proof under Sec 3(e))"
        
    if tkdl_overlap_count >= 2:
        tkdl_overlap = "High Prior Art Overlap (Ingredients recorded in TKDL)"
        base_score -= 10
    elif tkdl_overlap_count == 1:
        tkdl_overlap = "Medium Prior Art Overlap"
    else:
        tkdl_overlap = "Low Classical Overlap"
        base_score += 10
        
    overall_score = max(10, min(95, base_score))
    
    # Recommendations
    recommendations = []
    if not has_novel_tech:
        recommendations.append("To overcome Section 3(p), incorporate a standardized biomarker ratio (e.g. 95% Curcuminoids + 5% Piperine) or novel nano-formulation pathway.")
        recommendations.append("Provide in-vitro / in-vivo comparative trial data demonstrating statistical synergy (Combination Index < 0.8) to overcome Section 3(e).")
    else:
        recommendations.append("Draft patent claims focusing on the specific method of preparation, particle size distribution, and enhanced pharmacokinetic AUC profiles.")
    
    recommendations.append("Obtain National Biodiversity Authority (NBA) Form III clearance prior to grant of patent if utilizing raw herbs sourced in India.")
    recommendations.append("Conduct an exhaustive search on CSIR-TKDL and WIPO Patentscope under IPC A61K 36/00.")
    
    # Generate detailed report via RAG engine
    query = f"Patentability analysis for {request.formulation_name} with ingredients {', '.join(request.ingredients)}. Novelty: {request.novelty_description}"
    rag_data = retrieve_context(query)
    detailed_report = generate_rag_response(query, request.language, rag_data)
    
    risk_assessment = PatentabilityRiskScore(
        overall_score=overall_score,
        sec_3p_risk=sec_3p_risk,
        sec_3e_synergy_risk=sec_3e_risk,
        tkdl_prior_art_overlap=tkdl_overlap,
        nba_abs_required=True,
        recommended_ipc=recommended_ipc,
        recommendations=recommendations
    )
    
    return FormulationAnalysisResponse(
        formulation_name=request.formulation_name,
        risk_assessment=risk_assessment,
        detailed_report=detailed_report,
        citations=rag_data["citations"]
    )

@router.post("/regulatory-wizard", response_model=LicenseWizardResponse)
def regulatory_wizard_endpoint(request: LicenseWizardRequest):
    """
    AYUSH vs FSSAI Regulatory License Decision Tree.
    """
    cat = request.product_category
    claims = request.therapeutic_claims
    source = request.ingredients_source
    
    if cat == "classical" and source == "api_texts":
        return LicenseWizardResponse(
            recommended_license="Classical Ayurvedic Medicine License",
            form_number="Form 25D",
            governing_authority="State Licensing Authority (AYUSH Department)",
            key_requirements=[
                "Formulation recipe must strictly adhere to First Schedule texts of Drugs & Cosmetics Act (e.g. API, Charaka Samhita).",
                "Compliance with Schedule T Good Manufacturing Practices (GMP).",
                "Heavy metal, pesticide residue, and microbial testing report.",
                "Textual reference mandatory on product label."
            ],
            ctri_trial_needed=False,
            safety_toxicity_needed=False,
            fssai_applicable=False
        )
    elif cat == "proprietary" or (claims and source != "api_texts"):
        return LicenseWizardResponse(
            recommended_license="Patent or Proprietary (P&P) Ayurvedic Medicine License",
            form_number="Form 25E (under Rule 158B)",
            governing_authority="State Licensing Authority (AYUSH) & DCGI Review",
            key_requirements=[
                "Proof of Safety and Efficacy under Rule 158B of Drugs & Cosmetics Rules.",
                "Published scientific pilot literature or acute/sub-acute toxicity studies.",
                "Schedule T GMP certified manufacturing facility.",
                "No claims for Schedule J prohibited diseases (Cancer, Diabetes cure, etc.)."
            ],
            ctri_trial_needed=True,
            safety_toxicity_needed=True,
            fssai_applicable=False
        )
    elif cat == "health_supplement" or (not claims and cat != "cosmetic"):
        return LicenseWizardResponse(
            recommended_license="FSSAI Health Supplement / Nutraceutical License",
            form_number="FSSAI Central / State License (Form B)",
            governing_authority="Food Safety and Standards Authority of India (FSSAI)",
            key_requirements=[
                "Ingredients must comply with FSSAI Schedule VI approved botanical list.",
                "Vitamins/minerals must stay within Recommended Daily Allowance (RDA) limits.",
                "STRICT PROHIBITION of disease prevention/cure therapeutic claims.",
                "Label must clearly state 'NOT FOR MEDICINAL USE'."
            ],
            ctri_trial_needed=False,
            safety_toxicity_needed=False,
            fssai_applicable=True
        )
    else:
        return LicenseWizardResponse(
            recommended_license="AYUSH Cosmetic / Topical Herbal Product License",
            form_number="Form 32 / Form 25C",
            governing_authority="State AYUSH / State Licensing Authority",
            key_requirements=[
                "Dermatological safety testing & heavy metal limits.",
                "Non-therapeutic skin/hair benefit claims only.",
                "Schedule T GMP compliance."
            ],
            ctri_trial_needed=False,
            safety_toxicity_needed=False,
            fssai_applicable=False
        )

@router.post("/nba-calculator", response_model=NBACalculatorResponse)
def nba_calculator_endpoint(request: NBACalculatorRequest):
    """
    Calculate Access & Benefit Sharing (ABS) Royalty under Biological Diversity Act 2002.
    """
    turnover = request.annual_turnover_inr
    
    # Calculation tiers under Biological Diversity Act Regulations
    if turnover <= 10000000: # Up to 1 Crore
        percentage = 0.1
    elif turnover <= 30000000: # 1 to 3 Crore
        percentage = 0.2
    else: # Above 3 Crore
        percentage = 0.5
        
    estimated_royalty = (turnover * percentage) / 100.0
    
    form_type = "Form III (Prior Approval for Applying IPR)" if request.entity_type == "foreign_with_foreign_equity" else "Form I / SBB Intimation"
    
    note = "Mandatory under Biological Diversity Act 2002 (amended 2023). Failure to obtain NBA clearance before commercial exploitation or patent grant can invite penalties under Section 55."
    
    return NBACalculatorResponse(
        annual_turnover_inr=turnover,
        abs_percentage=percentage,
        estimated_royalty_inr=round(estimated_royalty, 2),
        nba_approval_form=form_type,
        legal_mandatory_note=note
    )

@router.get("/tkdl-search")
def tkdl_search_endpoint(q: str = ""):
    """
    Search TKDL and IPC records for botanical ingredients.
    """
    q_lower = q.lower().strip()
    results = []
    
    for name, data in AYURVEDIC_IPC_GLOSSARY.items():
        if not q_lower or q_lower in name or q_lower in data["sanskrit"].lower() or q_lower in data["latin"].lower():
            results.append({"name": name, **data})
            
    return {"query": q, "total": len(results), "results": results}
