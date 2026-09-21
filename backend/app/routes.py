"""
FastAPI Router for IP Sakti Endpoints.
"""
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import List, Dict, Any
import io
from app.schemas import (
    ChatRequest, ChatResponse,
    FormulationAnalysisRequest, FormulationAnalysisResponse, PatentabilityRiskScore,
    LicenseWizardRequest, LicenseWizardResponse,
    NBACalculatorRequest, NBACalculatorResponse
)
from app.rag_engine import retrieve_context
from app.llm_service import call_gemini_api, generate_rag_response
from app.multilingual import LANGUAGES
from app.kb_data import KNOWLEDGE_BASE, AYURVEDIC_IPC_GLOSSARY



router = APIRouter()

def translate_payload(text: str, target_lang: str) -> str:
    if target_lang == "en" or not text: 
        return text
    lang_name = LANGUAGES.get(target_lang, {}).get("name", "English")
    prompt = f"Translate the following legal text into {lang_name}. Return ONLY the translated text, nothing else.\n\nText: {text}"
    translated = call_gemini_api(prompt, "You are a professional legal translator.")
    return translated if not translated.startswith("API Error") else text

@router.get("/languages")
def get_supported_languages():
    return LANGUAGES

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")
        
    rag_data = retrieve_context(request.query)
    jur = request.jurisdiction or "india"
    answer = generate_rag_response(request.query, request.language, jur, rag_data)
    
    return ChatResponse(
        query=request.query,
        language=request.language,
        answer=answer,
        citations=rag_data["citations"],
        matched_ingredients=rag_data["matched_ingredients"]
    )

@router.post("/analyze-formulation", response_model=FormulationAnalysisResponse)
def analyze_formulation_endpoint(request: FormulationAnalysisRequest):
    ingredients_lower = [i.lower().strip() for i in request.ingredients]
    novelty_text = request.novelty_description.lower()
    
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
                    
    base_score = 45 
    
    novel_keywords = ["liposomal", "nano", "phytosome", "extract ratio", "standardized biomarker", "synergistic ratio", "bio-enhancer", "asava", "samskara"]
    has_novel_tech = any(kw in novelty_text for kw in novel_keywords) or any(kw in request.formulation_name.lower() for kw in novel_keywords)
    
    if has_novel_tech:
        base_score += 35
        sec_3p_risk = translate_payload("Low-Medium (Novel Technology / Delivery System Claimed)", request.language)
        sec_3e_risk = translate_payload("Low (Synergistic Bioavailability Enhancement Claimed)", request.language)
    else:
        sec_3p_risk = translate_payload("High (Classical Combination Risk under Indian Patent Act Sec 3(p))", request.language)
        sec_3e_risk = translate_payload("High (Requires Quantitative Experimental Synergy Proof under Sec 3(e))", request.language)
        
    if tkdl_overlap_count >= 2:
        tkdl_overlap = translate_payload("High Prior Art Overlap (Ingredients recorded in TKDL)", request.language)
        base_score -= 10
    elif tkdl_overlap_count == 1:
        tkdl_overlap = translate_payload("Medium Prior Art Overlap", request.language)
    else:
        tkdl_overlap = translate_payload("Low Classical Overlap", request.language)
        base_score += 10
        
    overall_score = max(10, min(95, base_score))
    
    recommendations = []
    if not has_novel_tech:
        recommendations.append("To overcome Section 3(p), incorporate a standardized biomarker ratio (e.g. 95% Curcuminoids + 5% Piperine) or novel nano-formulation pathway.")
        recommendations.append("Provide in-vitro / in-vivo comparative trial data demonstrating statistical synergy (Combination Index < 0.8) to overcome Section 3(e).")
    else:
        recommendations.append("Draft patent claims focusing on the specific method of preparation, particle size distribution, and enhanced pharmacokinetic AUC profiles.")
    
    recommendations.append("Obtain National Biodiversity Authority (NBA) Form III clearance prior to grant of patent if utilizing raw herbs sourced in India.")
    recommendations.append("Conduct an exhaustive search on CSIR-TKDL and WIPO Patentscope under IPC A61K 36/00.")
    
    translated_recs = [translate_payload(rec, request.language) for rec in recommendations]
    
    query = f"Patentability analysis for {request.formulation_name} with ingredients {', '.join(request.ingredients)}. Novelty: {request.novelty_description}"
    rag_data = retrieve_context(query)
    detailed_report = generate_rag_response(query, request.language, "india", rag_data)
    
    risk_assessment = PatentabilityRiskScore(
        overall_score=overall_score,
        sec_3p_risk=sec_3p_risk,
        sec_3e_synergy_risk=sec_3e_risk,
        tkdl_prior_art_overlap=tkdl_overlap,
        nba_abs_required=True,
        recommended_ipc=recommended_ipc,
        recommendations=translated_recs
    )
    
    return FormulationAnalysisResponse(
        formulation_name=request.formulation_name,
        risk_assessment=risk_assessment,
        detailed_report=detailed_report,
        citations=rag_data["citations"]
    )

@router.post("/regulatory-wizard", response_model=LicenseWizardResponse)
def regulatory_wizard_endpoint(request: LicenseWizardRequest):
    cat = request.product_category
    claims = request.therapeutic_claims
    source = request.ingredients_source
    
    if cat == "classical" and source == "api_texts":
        reqs = [
            "Formulation recipe must strictly adhere to First Schedule texts of Drugs & Cosmetics Act (e.g. API, Charaka Samhita).",
            "Compliance with Schedule T Good Manufacturing Practices (GMP).",
            "Heavy metal, pesticide residue, and microbial testing report.",
            "Textual reference mandatory on product label."
        ]
        return LicenseWizardResponse(
            recommended_license=translate_payload("Classical Ayurvedic Medicine License", request.language),
            form_number="Form 25D (In-House)",
            governing_authority=translate_payload("State Licensing Authority (AYUSH Department)", request.language),
            key_requirements=[translate_payload(r, request.language) for r in reqs],
            ctri_trial_needed=False,
            safety_toxicity_needed=False,
            fssai_applicable=False
        )
    elif cat == "proprietary" or (claims and source != "api_texts"):
        reqs = [
            "Proof of Safety and Efficacy under Rule 158B of Drugs & Cosmetics Rules.",
            "Published scientific pilot literature or acute/sub-acute toxicity studies.",
            "Schedule T GMP certified manufacturing facility.",
            "No claims for Schedule J prohibited diseases (Cancer, Diabetes cure, etc.)."
        ]
        return LicenseWizardResponse(
            recommended_license=translate_payload("Patent or Proprietary (P&P) Ayurvedic Medicine License", request.language),
            form_number="Form 25D (In-House) / Form 25E (Loan License) under Rule 158B",
            governing_authority=translate_payload("State Licensing Authority (AYUSH) & DCGI Review", request.language),
            key_requirements=[translate_payload(r, request.language) for r in reqs],
            ctri_trial_needed=True,
            safety_toxicity_needed=True,
            fssai_applicable=False
        )
    elif cat == "health_supplement" or (not claims and cat != "cosmetic"):
        reqs = [
            "Ingredients must comply with FSSAI Schedule VI approved botanical list.",
            "Vitamins/minerals must stay within Recommended Daily Allowance (RDA) limits.",
            "STRICT PROHIBITION of disease prevention/cure therapeutic claims.",
            "Label must clearly state 'NOT FOR MEDICINAL USE'."
        ]
        return LicenseWizardResponse(
            recommended_license=translate_payload("FSSAI Health Supplement / Nutraceutical License", request.language),
            form_number="FSSAI Central / State License (Form B)",
            governing_authority=translate_payload("Food Safety and Standards Authority of India (FSSAI)", request.language),
            key_requirements=[translate_payload(r, request.language) for r in reqs],
            ctri_trial_needed=False,
            safety_toxicity_needed=False,
            fssai_applicable=True
        )
    else:
        reqs = [
            "Dermatological safety testing & heavy metal limits.",
            "Non-therapeutic skin/hair benefit claims only.",
            "Schedule T GMP compliance."
        ]
        return LicenseWizardResponse(
            recommended_license=translate_payload("AYUSH Cosmetic / Topical Herbal Product License", request.language),
            form_number="Form 32 / Form 25C",
            governing_authority=translate_payload("State AYUSH / State Licensing Authority", request.language),
            key_requirements=[translate_payload(r, request.language) for r in reqs],
            ctri_trial_needed=False,
            safety_toxicity_needed=False,
            fssai_applicable=False
        )

@router.post("/nba-calculator", response_model=NBACalculatorResponse)
def nba_calculator_endpoint(request: NBACalculatorRequest):
    turnover = request.annual_turnover_inr
    
    if turnover <= 10000000:
        percentage = 0.1
    elif turnover <= 30000000:
        percentage = 0.2
    else:
        percentage = 0.5
        
    estimated_royalty = (turnover * percentage) / 100.0
    form_type = "Form III (Prior Approval for Applying IPR)" if request.entity_type == "foreign_with_foreign_equity" else "Form I / SBB Intimation"
    note = "Mandatory under Biological Diversity Act 2002 (amended 2023). Prior approval from NBA is required before commercial exploitation or grant of patent."
    
    return NBACalculatorResponse(
        annual_turnover_inr=turnover,
        abs_percentage=percentage,
        estimated_royalty_inr=round(estimated_royalty, 2),
        nba_approval_form=form_type,
        legal_mandatory_note=note
    )

@router.get("/tkdl-search")
def tkdl_search_endpoint(q: str = ""):
    q_lower = q.lower().strip()
    results = []
    
    for name, data in AYURVEDIC_IPC_GLOSSARY.items():
        if not q_lower or q_lower in name or q_lower in data["sanskrit"].lower() or q_lower in data["latin"].lower():
            results.append({"name": name, **data})
            
    return {"query": q, "total": len(results), "results": results}



# --- LIGHTNING FAST NEURAL TTS ARCHITECTURE ---
import edge_tts
class TTSRequest(BaseModel):
    text: str
    language: str = "en"

@router.post("/tts")
async def generate_speech_endpoint(request_data: TTSRequest):
    text = request_data.text
    lang = request_data.language
    
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
        
    # Map to Microsoft Azure's Premium Indian Neural Voices
    voice_map = {
        "en": "en-IN-NeerjaNeural",
        "hi": "hi-IN-SwaraNeural",
        "mr": "mr-IN-AarohiNeural",
        "ta": "ta-IN-PallaviNeural",
        "te": "te-IN-ShrutiNeural",
        "gu": "gu-IN-DhwaniNeural",
        "bn": "bn-IN-TanishaaNeural",
        "sa": "hi-IN-SwaraNeural" # Sanskrit falls back to Hindi phonetics
    }
    
    target_voice = voice_map.get(lang, "hi-IN-SwaraNeural")
    
    try:
        # Generate audio using Edge's async WebSocket API (Extremely Fast)
        communicate = edge_tts.Communicate(text, target_voice)
        audio_data = bytearray()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.extend(chunk["data"])
                
        return Response(content=bytes(audio_data), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# # --- FIXED CLOUD TTS ENDPOINT ---
# class TTSRequest(BaseModel):
#     text: str
#     language: str = "en"

# @router.post("/tts")
# def generate_speech_endpoint(request_data: TTSRequest):
#     text = request_data.text
#     lang = request_data.language
    
#     if not text:
#         raise HTTPException(status_code=400, detail="Text is required")
        
#     gtts_lang_map = {
#         "en": "en", "hi": "hi", "mr": "mr", "ta": "ta", 
#         "te": "te", "gu": "gu", "bn": "bn", "sa": "hi" # Fallback sa to hi
#     }
#     target_lang = gtts_lang_map.get(lang, "hi")
    
#     try:
#         tts = gTTS(text=text, lang=target_lang)
#         audio_fp = io.BytesIO()
#         tts.write_to_fp(audio_fp)
#         audio_fp.seek(0)
        
#         # FIX: Send raw bytes directly instead of StreamingResponse to prevent line-reading hangups
#         return Response(content=audio_fp.getvalue(), media_type="audio/mpeg")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# """
# FastAPI Router for IP Sakti Endpoints.
# """

# from fastapi import APIRouter, HTTPException
# from fastapi.responses import StreamingResponse
# from typing import List, Dict, Any
# import io
# from app.schemas import (
#     ChatRequest, ChatResponse,
#     FormulationAnalysisRequest, FormulationAnalysisResponse, PatentabilityRiskScore,
#     LicenseWizardRequest, LicenseWizardResponse,
#     NBACalculatorRequest, NBACalculatorResponse
# )
# from app.rag_engine import retrieve_context
# from app.llm_service import call_gemini_api, generate_rag_response
# from app.multilingual import LANGUAGES
# from app.kb_data import KNOWLEDGE_BASE, AYURVEDIC_IPC_GLOSSARY

# # Import the new Cloud TTS library
# from gtts import gTTS

# router = APIRouter()

# def translate_payload(text: str, target_lang: str) -> str:
#     """Helper to translate hardcoded backend strings on the fly."""
#     if target_lang == "en" or not text: 
#         return text
#     lang_name = LANGUAGES.get(target_lang, {}).get("name", "English")
#     prompt = f"Translate the following legal text into {lang_name}. Return ONLY the translated text, nothing else.\n\nText: {text}"
#     translated = call_gemini_api(prompt, "You are a professional legal translator.")
#     return translated if not translated.startswith("API Error") else text

# @router.get("/languages")
# def get_supported_languages():
#     return LANGUAGES

# @router.post("/chat", response_model=ChatResponse)
# def chat_endpoint(request: ChatRequest):
#     if not request.query.strip():
#         raise HTTPException(status_code=400, detail="Query string cannot be empty.")
        
#     rag_data = retrieve_context(request.query)
#     jur = request.jurisdiction or "india"
#     answer = generate_rag_response(request.query, request.language, jur, rag_data)
    
#     return ChatResponse(
#         query=request.query,
#         language=request.language,
#         answer=answer,
#         citations=rag_data["citations"],
#         matched_ingredients=rag_data["matched_ingredients"]
#     )

# @router.post("/analyze-formulation", response_model=FormulationAnalysisResponse)
# def analyze_formulation_endpoint(request: FormulationAnalysisRequest):
#     ingredients_lower = [i.lower().strip() for i in request.ingredients]
#     novelty_text = request.novelty_description.lower()
    
#     matched_glossary = []
#     tkdl_overlap_count = 0
#     recommended_ipc = ["A61K 36/00"]
    
#     for ing in ingredients_lower:
#         for name, data in AYURVEDIC_IPC_GLOSSARY.items():
#             if name in ing or ing in name:
#                 matched_glossary.append(data)
#                 tkdl_overlap_count += 1
#                 if data["ipc"] not in recommended_ipc:
#                     recommended_ipc.append(data["ipc"])
                    
#     base_score = 45 
    
#     novel_keywords = ["liposomal", "nano", "phytosome", "extract ratio", "standardized biomarker", "synergistic ratio", "bio-enhancer", "asava", "samskara"]
#     has_novel_tech = any(kw in novelty_text for kw in novel_keywords) or any(kw in request.formulation_name.lower() for kw in novel_keywords)
    
#     if has_novel_tech:
#         base_score += 35
#         sec_3p_risk = translate_payload("Low-Medium (Novel Technology / Delivery System Claimed)", request.language)
#         sec_3e_risk = translate_payload("Low (Synergistic Bioavailability Enhancement Claimed)", request.language)
#     else:
#         sec_3p_risk = translate_payload("High (Classical Combination Risk under Indian Patent Act Sec 3(p))", request.language)
#         sec_3e_risk = translate_payload("High (Requires Quantitative Experimental Synergy Proof under Sec 3(e))", request.language)
        
#     if tkdl_overlap_count >= 2:
#         tkdl_overlap = translate_payload("High Prior Art Overlap (Ingredients recorded in TKDL)", request.language)
#         base_score -= 10
#     elif tkdl_overlap_count == 1:
#         tkdl_overlap = translate_payload("Medium Prior Art Overlap", request.language)
#     else:
#         tkdl_overlap = translate_payload("Low Classical Overlap", request.language)
#         base_score += 10
        
#     overall_score = max(10, min(95, base_score))
    
#     recommendations = []
#     if not has_novel_tech:
#         recommendations.append("To overcome Section 3(p), incorporate a standardized biomarker ratio (e.g. 95% Curcuminoids + 5% Piperine) or novel nano-formulation pathway.")
#         recommendations.append("Provide in-vitro / in-vivo comparative trial data demonstrating statistical synergy (Combination Index < 0.8) to overcome Section 3(e).")
#     else:
#         recommendations.append("Draft patent claims focusing on the specific method of preparation, particle size distribution, and enhanced pharmacokinetic AUC profiles.")
    
#     recommendations.append("Obtain National Biodiversity Authority (NBA) Form III clearance prior to grant of patent if utilizing raw herbs sourced in India.")
#     recommendations.append("Conduct an exhaustive search on CSIR-TKDL and WIPO Patentscope under IPC A61K 36/00.")
    
#     translated_recs = [translate_payload(rec, request.language) for rec in recommendations]
    
#     query = f"Patentability analysis for {request.formulation_name} with ingredients {', '.join(request.ingredients)}. Novelty: {request.novelty_description}"
#     rag_data = retrieve_context(query)
#     detailed_report = generate_rag_response(query, request.language, "india", rag_data)
    
#     risk_assessment = PatentabilityRiskScore(
#         overall_score=overall_score,
#         sec_3p_risk=sec_3p_risk,
#         sec_3e_synergy_risk=sec_3e_risk,
#         tkdl_prior_art_overlap=tkdl_overlap,
#         nba_abs_required=True,
#         recommended_ipc=recommended_ipc,
#         recommendations=translated_recs
#     )
    
#     return FormulationAnalysisResponse(
#         formulation_name=request.formulation_name,
#         risk_assessment=risk_assessment,
#         detailed_report=detailed_report,
#         citations=rag_data["citations"]
#     )

# @router.post("/regulatory-wizard", response_model=LicenseWizardResponse)
# def regulatory_wizard_endpoint(request: LicenseWizardRequest):
#     cat = request.product_category
#     claims = request.therapeutic_claims
#     source = request.ingredients_source
    
#     if cat == "classical" and source == "api_texts":
#         reqs = [
#             "Formulation recipe must strictly adhere to First Schedule texts of Drugs & Cosmetics Act (e.g. API, Charaka Samhita).",
#             "Compliance with Schedule T Good Manufacturing Practices (GMP).",
#             "Heavy metal, pesticide residue, and microbial testing report.",
#             "Textual reference mandatory on product label."
#         ]
#         return LicenseWizardResponse(
#             recommended_license=translate_payload("Classical Ayurvedic Medicine License", request.language),
#             form_number="Form 25D (In-House)",
#             governing_authority=translate_payload("State Licensing Authority (AYUSH Department)", request.language),
#             key_requirements=[translate_payload(r, request.language) for r in reqs],
#             ctri_trial_needed=False,
#             safety_toxicity_needed=False,
#             fssai_applicable=False
#         )
#     elif cat == "proprietary" or (claims and source != "api_texts"):
#         reqs = [
#             "Proof of Safety and Efficacy under Rule 158B of Drugs & Cosmetics Rules.",
#             "Published scientific pilot literature or acute/sub-acute toxicity studies.",
#             "Schedule T GMP certified manufacturing facility.",
#             "No claims for Schedule J prohibited diseases (Cancer, Diabetes cure, etc.)."
#         ]
#         return LicenseWizardResponse(
#             recommended_license=translate_payload("Patent or Proprietary (P&P) Ayurvedic Medicine License", request.language),
#             form_number="Form 25D (In-House) / Form 25E (Loan License) under Rule 158B",
#             governing_authority=translate_payload("State Licensing Authority (AYUSH) & DCGI Review", request.language),
#             key_requirements=[translate_payload(r, request.language) for r in reqs],
#             ctri_trial_needed=True,
#             safety_toxicity_needed=True,
#             fssai_applicable=False
#         )
#     elif cat == "health_supplement" or (not claims and cat != "cosmetic"):
#         reqs = [
#             "Ingredients must comply with FSSAI Schedule VI approved botanical list.",
#             "Vitamins/minerals must stay within Recommended Daily Allowance (RDA) limits.",
#             "STRICT PROHIBITION of disease prevention/cure therapeutic claims.",
#             "Label must clearly state 'NOT FOR MEDICINAL USE'."
#         ]
#         return LicenseWizardResponse(
#             recommended_license=translate_payload("FSSAI Health Supplement / Nutraceutical License", request.language),
#             form_number="FSSAI Central / State License (Form B)",
#             governing_authority=translate_payload("Food Safety and Standards Authority of India (FSSAI)", request.language),
#             key_requirements=[translate_payload(r, request.language) for r in reqs],
#             ctri_trial_needed=False,
#             safety_toxicity_needed=False,
#             fssai_applicable=True
#         )
#     else:
#         reqs = [
#             "Dermatological safety testing & heavy metal limits.",
#             "Non-therapeutic skin/hair benefit claims only.",
#             "Schedule T GMP compliance."
#         ]
#         return LicenseWizardResponse(
#             recommended_license=translate_payload("AYUSH Cosmetic / Topical Herbal Product License", request.language),
#             form_number="Form 32 / Form 25C",
#             governing_authority=translate_payload("State AYUSH / State Licensing Authority", request.language),
#             key_requirements=[translate_payload(r, request.language) for r in reqs],
#             ctri_trial_needed=False,
#             safety_toxicity_needed=False,
#             fssai_applicable=False
#         )

# @router.post("/nba-calculator", response_model=NBACalculatorResponse)
# def nba_calculator_endpoint(request: NBACalculatorRequest):
#     turnover = request.annual_turnover_inr
    
#     if turnover <= 10000000:
#         percentage = 0.1
#     elif turnover <= 30000000:
#         percentage = 0.2
#     else:
#         percentage = 0.5
        
#     estimated_royalty = (turnover * percentage) / 100.0
#     form_type = "Form III (Prior Approval for Applying IPR)" if request.entity_type == "foreign_with_foreign_equity" else "Form I / SBB Intimation"
#     note = "Mandatory under Biological Diversity Act 2002 (amended 2023). Prior approval from NBA is required before commercial exploitation or grant of patent."
    
#     return NBACalculatorResponse(
#         annual_turnover_inr=turnover,
#         abs_percentage=percentage,
#         estimated_royalty_inr=round(estimated_royalty, 2),
#         nba_approval_form=form_type,
#         legal_mandatory_note=note
#     )

# @router.get("/tkdl-search")
# def tkdl_search_endpoint(q: str = ""):
#     q_lower = q.lower().strip()
#     results = []
    
#     for name, data in AYURVEDIC_IPC_GLOSSARY.items():
#         if not q_lower or q_lower in name or q_lower in data["sanskrit"].lower() or q_lower in data["latin"].lower():
#             results.append({"name": name, **data})
            
#     return {"query": q, "total": len(results), "results": results}

# # --- NEW CLOUD TTS (BHASHINI PLACEHOLDER) ARCHITECTURE ---
# @router.post("/tts")
# def generate_speech_endpoint(request_data: dict):
#     text = request_data.get("text", "")
#     lang = request_data.get("language", "en")
    
#     if not text:
#         raise HTTPException(status_code=400, detail="Text is required")
        
#     gtts_lang_map = {
#         "en": "en", "hi": "hi", "mr": "mr", "ta": "ta", 
#         "te": "te", "gu": "gu", "bn": "bn", "sa": "hi" # Fallback sa to hi
#     }
#     target_lang = gtts_lang_map.get(lang, "hi")
    
#     try:
#         tts = gTTS(text=text, lang=target_lang)
#         audio_fp = io.BytesIO()
#         tts.write_to_fp(audio_fp)
#         audio_fp.seek(0)
#         return StreamingResponse(audio_fp, media_type="audio/mpeg")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # """
# # FastAPI Router for IP Sakti Endpoints.
# # """

# # from fastapi import APIRouter, HTTPException
# # from typing import List, Dict, Any
# # from app.schemas import (
# #     ChatRequest, ChatResponse,
# #     FormulationAnalysisRequest, FormulationAnalysisResponse, PatentabilityRiskScore,
# #     LicenseWizardRequest, LicenseWizardResponse,
# #     NBACalculatorRequest, NBACalculatorResponse
# # )
# # from app.rag_engine import retrieve_context
# # from app.llm_service import call_gemini_api, generate_rag_response
# # from app.multilingual import LANGUAGES
# # from app.kb_data import KNOWLEDGE_BASE, AYURVEDIC_IPC_GLOSSARY

# # router = APIRouter()

# # def translate_payload(text: str, target_lang: str) -> str:
# #     """Helper to translate hardcoded backend strings on the fly."""
# #     if target_lang == "en" or not text: 
# #         return text
# #     lang_name = LANGUAGES.get(target_lang, {}).get("name", "English")
# #     prompt = f"Translate the following legal text into {lang_name}. Return ONLY the translated text, nothing else.\n\nText: {text}"
# #     translated = call_gemini_api(prompt, "You are a professional legal translator.")
# #     return translated if not translated.startswith("API Error") else text

# # @router.get("/languages")
# # def get_supported_languages():
# #     return LANGUAGES

# # @router.post("/chat", response_model=ChatResponse)
# # def chat_endpoint(request: ChatRequest):
# #     if not request.query.strip():
# #         raise HTTPException(status_code=400, detail="Query string cannot be empty.")
        
# #     rag_data = retrieve_context(request.query)
# #     jur = request.jurisdiction or "india"
# #     answer = generate_rag_response(request.query, request.language, jur, rag_data)
    
# #     return ChatResponse(
# #         query=request.query,
# #         language=request.language,
# #         answer=answer,
# #         citations=rag_data["citations"],
# #         matched_ingredients=rag_data["matched_ingredients"]
# #     )

# # @router.post("/analyze-formulation", response_model=FormulationAnalysisResponse)
# # def analyze_formulation_endpoint(request: FormulationAnalysisRequest):
# #     ingredients_lower = [i.lower().strip() for i in request.ingredients]
# #     novelty_text = request.novelty_description.lower()
    
# #     matched_glossary = []
# #     tkdl_overlap_count = 0
# #     recommended_ipc = ["A61K 36/00"]
    
# #     for ing in ingredients_lower:
# #         for name, data in AYURVEDIC_IPC_GLOSSARY.items():
# #             if name in ing or ing in name:
# #                 matched_glossary.append(data)
# #                 tkdl_overlap_count += 1
# #                 if data["ipc"] not in recommended_ipc:
# #                     recommended_ipc.append(data["ipc"])
                    
# #     base_score = 45 
    
# #     novel_keywords = ["liposomal", "nano", "phytosome", "extract ratio", "standardized biomarker", "synergistic ratio", "bio-enhancer", "asava", "samskara"]
# #     has_novel_tech = any(kw in novelty_text for kw in novel_keywords) or any(kw in request.formulation_name.lower() for kw in novel_keywords)
    
# #     if has_novel_tech:
# #         base_score += 35
# #         sec_3p_risk = translate_payload("Low-Medium (Novel Technology / Delivery System Claimed)", request.language)
# #         sec_3e_risk = translate_payload("Low (Synergistic Bioavailability Enhancement Claimed)", request.language)
# #     else:
# #         sec_3p_risk = translate_payload("High (Classical Combination Risk under Indian Patent Act Sec 3(p))", request.language)
# #         sec_3e_risk = translate_payload("High (Requires Quantitative Experimental Synergy Proof under Sec 3(e))", request.language)
        
# #     if tkdl_overlap_count >= 2:
# #         tkdl_overlap = translate_payload("High Prior Art Overlap (Ingredients recorded in TKDL)", request.language)
# #         base_score -= 10
# #     elif tkdl_overlap_count == 1:
# #         tkdl_overlap = translate_payload("Medium Prior Art Overlap", request.language)
# #     else:
# #         tkdl_overlap = translate_payload("Low Classical Overlap", request.language)
# #         base_score += 10
        
# #     overall_score = max(10, min(95, base_score))
    
# #     recommendations = []
# #     if not has_novel_tech:
# #         recommendations.append("To overcome Section 3(p), incorporate a standardized biomarker ratio (e.g. 95% Curcuminoids + 5% Piperine) or novel nano-formulation pathway.")
# #         recommendations.append("Provide in-vitro / in-vivo comparative trial data demonstrating statistical synergy (Combination Index < 0.8) to overcome Section 3(e).")
# #     else:
# #         recommendations.append("Draft patent claims focusing on the specific method of preparation, particle size distribution, and enhanced pharmacokinetic AUC profiles.")
    
# #     recommendations.append("Obtain National Biodiversity Authority (NBA) Form III clearance prior to grant of patent if utilizing raw herbs sourced in India.")
# #     recommendations.append("Conduct an exhaustive search on CSIR-TKDL and WIPO Patentscope under IPC A61K 36/00.")
    
# #     translated_recs = [translate_payload(rec, request.language) for rec in recommendations]
    
# #     query = f"Patentability analysis for {request.formulation_name} with ingredients {', '.join(request.ingredients)}. Novelty: {request.novelty_description}"
# #     rag_data = retrieve_context(query)
# #     detailed_report = generate_rag_response(query, request.language, "india", rag_data)
    
# #     risk_assessment = PatentabilityRiskScore(
# #         overall_score=overall_score,
# #         sec_3p_risk=sec_3p_risk,
# #         sec_3e_synergy_risk=sec_3e_risk,
# #         tkdl_prior_art_overlap=tkdl_overlap,
# #         nba_abs_required=True,
# #         recommended_ipc=recommended_ipc,
# #         recommendations=translated_recs
# #     )
    
# #     return FormulationAnalysisResponse(
# #         formulation_name=request.formulation_name,
# #         risk_assessment=risk_assessment,
# #         detailed_report=detailed_report,
# #         citations=rag_data["citations"]
# #     )

# # @router.post("/regulatory-wizard", response_model=LicenseWizardResponse)
# # def regulatory_wizard_endpoint(request: LicenseWizardRequest):
# #     cat = request.product_category
# #     claims = request.therapeutic_claims
# #     source = request.ingredients_source
    
# #     if cat == "classical" and source == "api_texts":
# #         reqs = [
# #             "Formulation recipe must strictly adhere to First Schedule texts of Drugs & Cosmetics Act (e.g. API, Charaka Samhita).",
# #             "Compliance with Schedule T Good Manufacturing Practices (GMP).",
# #             "Heavy metal, pesticide residue, and microbial testing report.",
# #             "Textual reference mandatory on product label."
# #         ]
# #         return LicenseWizardResponse(
# #             recommended_license=translate_payload("Classical Ayurvedic Medicine License", request.language),
# #             form_number="Form 25D (In-House)",
# #             governing_authority=translate_payload("State Licensing Authority (AYUSH Department)", request.language),
# #             key_requirements=[translate_payload(r, request.language) for r in reqs],
# #             ctri_trial_needed=False,
# #             safety_toxicity_needed=False,
# #             fssai_applicable=False
# #         )
# #     elif cat == "proprietary" or (claims and source != "api_texts"):
# #         reqs = [
# #             "Proof of Safety and Efficacy under Rule 158B of Drugs & Cosmetics Rules.",
# #             "Published scientific pilot literature or acute/sub-acute toxicity studies.",
# #             "Schedule T GMP certified manufacturing facility.",
# #             "No claims for Schedule J prohibited diseases (Cancer, Diabetes cure, etc.)."
# #         ]
# #         return LicenseWizardResponse(
# #             recommended_license=translate_payload("Patent or Proprietary (P&P) Ayurvedic Medicine License", request.language),
# #             form_number="Form 25D (In-House) / Form 25E (Loan License) under Rule 158B",
# #             governing_authority=translate_payload("State Licensing Authority (AYUSH) & DCGI Review", request.language),
# #             key_requirements=[translate_payload(r, request.language) for r in reqs],
# #             ctri_trial_needed=True,
# #             safety_toxicity_needed=True,
# #             fssai_applicable=False
# #         )
# #     elif cat == "health_supplement" or (not claims and cat != "cosmetic"):
# #         reqs = [
# #             "Ingredients must comply with FSSAI Schedule VI approved botanical list.",
# #             "Vitamins/minerals must stay within Recommended Daily Allowance (RDA) limits.",
# #             "STRICT PROHIBITION of disease prevention/cure therapeutic claims.",
# #             "Label must clearly state 'NOT FOR MEDICINAL USE'."
# #         ]
# #         return LicenseWizardResponse(
# #             recommended_license=translate_payload("FSSAI Health Supplement / Nutraceutical License", request.language),
# #             form_number="FSSAI Central / State License (Form B)",
# #             governing_authority=translate_payload("Food Safety and Standards Authority of India (FSSAI)", request.language),
# #             key_requirements=[translate_payload(r, request.language) for r in reqs],
# #             ctri_trial_needed=False,
# #             safety_toxicity_needed=False,
# #             fssai_applicable=True
# #         )
# #     else:
# #         reqs = [
# #             "Dermatological safety testing & heavy metal limits.",
# #             "Non-therapeutic skin/hair benefit claims only.",
# #             "Schedule T GMP compliance."
# #         ]
# #         return LicenseWizardResponse(
# #             recommended_license=translate_payload("AYUSH Cosmetic / Topical Herbal Product License", request.language),
# #             form_number="Form 32 / Form 25C",
# #             governing_authority=translate_payload("State AYUSH / State Licensing Authority", request.language),
# #             key_requirements=[translate_payload(r, request.language) for r in reqs],
# #             ctri_trial_needed=False,
# #             safety_toxicity_needed=False,
# #             fssai_applicable=False
# #         )

# # @router.post("/nba-calculator", response_model=NBACalculatorResponse)
# # def nba_calculator_endpoint(request: NBACalculatorRequest):
# #     turnover = request.annual_turnover_inr
    
# #     if turnover <= 10000000:
# #         percentage = 0.1
# #     elif turnover <= 30000000:
# #         percentage = 0.2
# #     else:
# #         percentage = 0.5
        
# #     estimated_royalty = (turnover * percentage) / 100.0
# #     form_type = "Form III (Prior Approval for Applying IPR)" if request.entity_type == "foreign_with_foreign_equity" else "Form I / SBB Intimation"
# #     note = "Mandatory under Biological Diversity Act 2002 (amended 2023). Prior approval from NBA is required before commercial exploitation or grant of patent."
    
# #     return NBACalculatorResponse(
# #         annual_turnover_inr=turnover,
# #         abs_percentage=percentage,
# #         estimated_royalty_inr=round(estimated_royalty, 2),
# #         nba_approval_form=form_type,
# #         legal_mandatory_note=note
# #     )

# # @router.get("/tkdl-search")
# # def tkdl_search_endpoint(q: str = ""):
# #     q_lower = q.lower().strip()
# #     results = []
    
# #     for name, data in AYURVEDIC_IPC_GLOSSARY.items():
# #         if not q_lower or q_lower in name or q_lower in data["sanskrit"].lower() or q_lower in data["latin"].lower():
# #             results.append({"name": name, **data})
            
# #     return {"query": q, "total": len(results), "results": results}

# # # """
# # # FastAPI Router for IP Sakti Endpoints.
# # # """

# # # from fastapi import APIRouter, HTTPException
# # # from typing import List, Dict, Any
# # # from app.schemas import (
# # #     ChatRequest, ChatResponse,
# # #     FormulationAnalysisRequest, FormulationAnalysisResponse, PatentabilityRiskScore,
# # #     LicenseWizardRequest, LicenseWizardResponse,
# # #     NBACalculatorRequest, NBACalculatorResponse
# # # )
# # # from app.rag_engine import retrieve_context
# # # from app.llm_service import call_gemini_api, generate_rag_response
# # # from app.multilingual import LANGUAGES
# # # from app.kb_data import KNOWLEDGE_BASE, AYURVEDIC_IPC_GLOSSARY

# # # router = APIRouter()

# # # def translate_payload(text: str, target_lang: str) -> str:
# # #     """Helper to translate hardcoded backend strings on the fly."""
# # #     if target_lang == "en" or not text: 
# # #         return text
# # #     lang_name = LANGUAGES.get(target_lang, {}).get("name", "English")
# # #     prompt = f"Translate the following legal text into {lang_name}. Return ONLY the translated text, nothing else.\n\nText: {text}"
# # #     translated = call_gemini_api(prompt, "You are a professional legal translator.")
# # #     return translated if not translated.startswith("API Error") else text

# # # @router.get("/languages")
# # # def get_supported_languages():
# # #     return LANGUAGES

# # # @router.post("/chat", response_model=ChatResponse)
# # # def chat_endpoint(request: ChatRequest):
# # #     if not request.query.strip():
# # #         raise HTTPException(status_code=400, detail="Query string cannot be empty.")
        
# # #     rag_data = retrieve_context(request.query)
# # #     answer = generate_rag_response(request.query, request.language, request.jurisdiction, rag_data)
    
# # #     return ChatResponse(
# # #         query=request.query,
# # #         language=request.language,
# # #         answer=answer,
# # #         citations=rag_data["citations"],
# # #         matched_ingredients=rag_data["matched_ingredients"]
# # #     )

# # # @router.post("/analyze-formulation", response_model=FormulationAnalysisResponse)
# # # def analyze_formulation_endpoint(request: FormulationAnalysisRequest):
# # #     ingredients_lower = [i.lower().strip() for i in request.ingredients]
# # #     novelty_text = request.novelty_description.lower()
    
# # #     matched_glossary = []
# # #     tkdl_overlap_count = 0
# # #     recommended_ipc = ["A61K 36/00"]
    
# # #     for ing in ingredients_lower:
# # #         for name, data in AYURVEDIC_IPC_GLOSSARY.items():
# # #             if name in ing or ing in name:
# # #                 matched_glossary.append(data)
# # #                 tkdl_overlap_count += 1
# # #                 if data["ipc"] not in recommended_ipc:
# # #                     recommended_ipc.append(data["ipc"])
                    
# # #     base_score = 45 
    
# # #     novel_keywords = ["liposomal", "nano", "phytosome", "extract ratio", "standardized biomarker", "synergistic ratio", "bio-enhancer", "asava", "samskara"]
# # #     has_novel_tech = any(kw in novelty_text for kw in novel_keywords) or any(kw in request.formulation_name.lower() for kw in novel_keywords)
    
# # #     if has_novel_tech:
# # #         base_score += 35
# # #         sec_3p_risk = translate_payload("Low-Medium (Novel Technology / Delivery System Claimed)", request.language)
# # #         sec_3e_risk = translate_payload("Low (Synergistic Bioavailability Enhancement Claimed)", request.language)
# # #     else:
# # #         sec_3p_risk = translate_payload("High (Classical Combination Risk under Indian Patent Act Sec 3(p))", request.language)
# # #         sec_3e_risk = translate_payload("High (Requires Quantitative Experimental Synergy Proof under Sec 3(e))", request.language)
        
# # #     if tkdl_overlap_count >= 2:
# # #         tkdl_overlap = translate_payload("High Prior Art Overlap (Ingredients recorded in TKDL)", request.language)
# # #         base_score -= 10
# # #     elif tkdl_overlap_count == 1:
# # #         tkdl_overlap = translate_payload("Medium Prior Art Overlap", request.language)
# # #     else:
# # #         tkdl_overlap = translate_payload("Low Classical Overlap", request.language)
# # #         base_score += 10
        
# # #     overall_score = max(10, min(95, base_score))
    
# # #     recommendations = []
# # #     if not has_novel_tech:
# # #         recommendations.append("To overcome Section 3(p), incorporate a standardized biomarker ratio (e.g. 95% Curcuminoids + 5% Piperine) or novel nano-formulation pathway.")
# # #         recommendations.append("Provide in-vitro / in-vivo comparative trial data demonstrating statistical synergy (Combination Index < 0.8) to overcome Section 3(e).")
# # #     else:
# # #         recommendations.append("Draft patent claims focusing on the specific method of preparation, particle size distribution, and enhanced pharmacokinetic AUC profiles.")
    
# # #     recommendations.append("Obtain National Biodiversity Authority (NBA) Form III clearance prior to grant of patent if utilizing raw herbs sourced in India.")
# # #     recommendations.append("Conduct an exhaustive search on CSIR-TKDL and WIPO Patentscope under IPC A61K 36/00.")
    
# # #     translated_recs = [translate_payload(rec, request.language) for rec in recommendations]
    
# # #     query = f"Patentability analysis for {request.formulation_name} with ingredients {', '.join(request.ingredients)}. Novelty: {request.novelty_description}"
# # #     rag_data = retrieve_context(query)
# # #     detailed_report = generate_rag_response(query, request.language, "india", rag_data)
    
# # #     risk_assessment = PatentabilityRiskScore(
# # #         overall_score=overall_score,
# # #         sec_3p_risk=sec_3p_risk,
# # #         sec_3e_synergy_risk=sec_3e_risk,
# # #         tkdl_prior_art_overlap=tkdl_overlap,
# # #         nba_abs_required=True,
# # #         recommended_ipc=recommended_ipc,
# # #         recommendations=translated_recs
# # #     )
    
# # #     return FormulationAnalysisResponse(
# # #         formulation_name=request.formulation_name,
# # #         risk_assessment=risk_assessment,
# # #         detailed_report=detailed_report,
# # #         citations=rag_data["citations"]
# # #     )

# # # @router.post("/regulatory-wizard", response_model=LicenseWizardResponse)
# # # def regulatory_wizard_endpoint(request: LicenseWizardRequest):
# # #     cat = request.product_category
# # #     claims = request.therapeutic_claims
# # #     source = request.ingredients_source
    
# # #     if cat == "classical" and source == "api_texts":
# # #         reqs = [
# # #             "Formulation recipe must strictly adhere to First Schedule texts of Drugs & Cosmetics Act (e.g. API, Charaka Samhita).",
# # #             "Compliance with Schedule T Good Manufacturing Practices (GMP).",
# # #             "Heavy metal, pesticide residue, and microbial testing report.",
# # #             "Textual reference mandatory on product label."
# # #         ]
# # #         return LicenseWizardResponse(
# # #             recommended_license=translate_payload("Classical Ayurvedic Medicine License", request.language),
# # #             form_number="Form 25D (In-House)",
# # #             governing_authority=translate_payload("State Licensing Authority (AYUSH Department)", request.language),
# # #             key_requirements=[translate_payload(r, request.language) for r in reqs],
# # #             ctri_trial_needed=False,
# # #             safety_toxicity_needed=False,
# # #             fssai_applicable=False
# # #         )
# # #     elif cat == "proprietary" or (claims and source != "api_texts"):
# # #         reqs = [
# # #             "Proof of Safety and Efficacy under Rule 158B of Drugs & Cosmetics Rules.",
# # #             "Published scientific pilot literature or acute/sub-acute toxicity studies.",
# # #             "Schedule T GMP certified manufacturing facility.",
# # #             "No claims for Schedule J prohibited diseases (Cancer, Diabetes cure, etc.)."
# # #         ]
# # #         return LicenseWizardResponse(
# # #             recommended_license=translate_payload("Patent or Proprietary (P&P) Ayurvedic Medicine License", request.language),
# # #             form_number="Form 25D (In-House) / Form 25E (Loan License) under Rule 158B",
# # #             governing_authority=translate_payload("State Licensing Authority (AYUSH) & DCGI Review", request.language),
# # #             key_requirements=[translate_payload(r, request.language) for r in reqs],
# # #             ctri_trial_needed=True,
# # #             safety_toxicity_needed=True,
# # #             fssai_applicable=False
# # #         )
# # #     elif cat == "health_supplement" or (not claims and cat != "cosmetic"):
# # #         reqs = [
# # #             "Ingredients must comply with FSSAI Schedule VI approved botanical list.",
# # #             "Vitamins/minerals must stay within Recommended Daily Allowance (RDA) limits.",
# # #             "STRICT PROHIBITION of disease prevention/cure therapeutic claims.",
# # #             "Label must clearly state 'NOT FOR MEDICINAL USE'."
# # #         ]
# # #         return LicenseWizardResponse(
# # #             recommended_license=translate_payload("FSSAI Health Supplement / Nutraceutical License", request.language),
# # #             form_number="FSSAI Central / State License (Form B)",
# # #             governing_authority=translate_payload("Food Safety and Standards Authority of India (FSSAI)", request.language),
# # #             key_requirements=[translate_payload(r, request.language) for r in reqs],
# # #             ctri_trial_needed=False,
# # #             safety_toxicity_needed=False,
# # #             fssai_applicable=True
# # #         )
# # #     else:
# # #         reqs = [
# # #             "Dermatological safety testing & heavy metal limits.",
# # #             "Non-therapeutic skin/hair benefit claims only.",
# # #             "Schedule T GMP compliance."
# # #         ]
# # #         return LicenseWizardResponse(
# # #             recommended_license=translate_payload("AYUSH Cosmetic / Topical Herbal Product License", request.language),
# # #             form_number="Form 32 / Form 25C",
# # #             governing_authority=translate_payload("State AYUSH / State Licensing Authority", request.language),
# # #             key_requirements=[translate_payload(r, request.language) for r in reqs],
# # #             ctri_trial_needed=False,
# # #             safety_toxicity_needed=False,
# # #             fssai_applicable=False
# # #         )

# # # @router.post("/nba-calculator", response_model=NBACalculatorResponse)
# # # def nba_calculator_endpoint(request: NBACalculatorRequest):
# # #     turnover = request.annual_turnover_inr
    
# # #     if turnover <= 10000000:
# # #         percentage = 0.1
# # #     elif turnover <= 30000000:
# # #         percentage = 0.2
# # #     else:
# # #         percentage = 0.5
        
# # #     estimated_royalty = (turnover * percentage) / 100.0
# # #     form_type = "Form III (Prior Approval for Applying IPR)" if request.entity_type == "foreign_with_foreign_equity" else "Form I / SBB Intimation"
# # #     note = "Mandatory under Biological Diversity Act 2002 (amended 2023). Prior approval from NBA is required before commercial exploitation or grant of patent."
    
# # #     return NBACalculatorResponse(
# # #         annual_turnover_inr=turnover,
# # #         abs_percentage=percentage,
# # #         estimated_royalty_inr=round(estimated_royalty, 2),
# # #         nba_approval_form=form_type,
# # #         legal_mandatory_note=note
# # #     )

# # # @router.get("/tkdl-search")
# # # def tkdl_search_endpoint(q: str = ""):
# # #     q_lower = q.lower().strip()
# # #     results = []
    
# # #     for name, data in AYURVEDIC_IPC_GLOSSARY.items():
# # #         if not q_lower or q_lower in name or q_lower in data["sanskrit"].lower() or q_lower in data["latin"].lower():
# # #             results.append({"name": name, **data})
            
# # #     return {"query": q, "total": len(results), "results": results}

# # # # """
# # # # FastAPI Router for IP Sakti Endpoints.
# # # # """

# # # # from fastapi import APIRouter, HTTPException
# # # # from typing import List, Dict, Any
# # # # from app.schemas import (
# # # #     ChatRequest, ChatResponse,
# # # #     FormulationAnalysisRequest, FormulationAnalysisResponse, PatentabilityRiskScore,
# # # #     LicenseWizardRequest, LicenseWizardResponse,
# # # #     NBACalculatorRequest, NBACalculatorResponse
# # # # )
# # # # from app.rag_engine import retrieve_context
# # # # from app.llm_service import call_gemini_api, generate_rag_response
# # # # from app.multilingual import LANGUAGES
# # # # from app.kb_data import KNOWLEDGE_BASE, AYURVEDIC_IPC_GLOSSARY

# # # # router = APIRouter()

# # # # def translate_payload(text: str, target_lang: str) -> str:
# # # #     """Helper to translate hardcoded backend strings on the fly."""
# # # #     if target_lang == "en" or not text: 
# # # #         return text
# # # #     lang_name = LANGUAGES.get(target_lang, {}).get("name", "English")
# # # #     prompt = f"Translate the following text into {lang_name}. Return ONLY the translated text, nothing else.\n\nText: {text}"
# # # #     translated = call_gemini_api(prompt, "You are a professional legal translator.")
# # # #     return translated if not translated.startswith("API Error") else text

# # # # @router.get("/languages")
# # # # def get_supported_languages():
# # # #     return LANGUAGES

# # # # @router.post("/chat", response_model=ChatResponse)
# # # # def chat_endpoint(request: ChatRequest):
# # # #     if not request.query.strip():
# # # #         raise HTTPException(status_code=400, detail="Query string cannot be empty.")
        
# # # #     rag_data = retrieve_context(request.query)
# # # #     answer = generate_rag_response(request.query, request.language, rag_data)
    
# # # #     return ChatResponse(
# # # #         query=request.query,
# # # #         language=request.language,
# # # #         answer=answer,
# # # #         citations=rag_data["citations"],
# # # #         matched_ingredients=rag_data["matched_ingredients"]
# # # #     )

# # # # @router.post("/analyze-formulation", response_model=FormulationAnalysisResponse)
# # # # def analyze_formulation_endpoint(request: FormulationAnalysisRequest):
# # # #     ingredients_lower = [i.lower().strip() for i in request.ingredients]
# # # #     novelty_text = request.novelty_description.lower()
    
# # # #     matched_glossary = []
# # # #     tkdl_overlap_count = 0
# # # #     recommended_ipc = ["A61K 36/00"]
    
# # # #     for ing in ingredients_lower:
# # # #         for name, data in AYURVEDIC_IPC_GLOSSARY.items():
# # # #             if name in ing or ing in name:
# # # #                 matched_glossary.append(data)
# # # #                 tkdl_overlap_count += 1
# # # #                 if data["ipc"] not in recommended_ipc:
# # # #                     recommended_ipc.append(data["ipc"])
                    
# # # #     base_score = 45 
    
# # # #     novel_keywords = ["liposomal", "nano", "phytosome", "extract ratio", "standardized biomarker", "synergistic ratio", "bio-enhancer", "asava", "samskara"]
# # # #     has_novel_tech = any(kw in novelty_text for kw in novel_keywords) or any(kw in request.formulation_name.lower() for kw in novel_keywords)
    
# # # #     if has_novel_tech:
# # # #         base_score += 35
# # # #         sec_3p_risk = translate_payload("Low-Medium (Novel Technology / Delivery System Claimed)", request.language)
# # # #         sec_3e_risk = translate_payload("Low (Synergistic Bioavailability Enhancement Claimed)", request.language)
# # # #     else:
# # # #         sec_3p_risk = translate_payload("High (Classical Combination Risk under Indian Patent Act Sec 3(p))", request.language)
# # # #         sec_3e_risk = translate_payload("High (Requires Quantitative Experimental Synergy Proof under Sec 3(e))", request.language)
        
# # # #     if tkdl_overlap_count >= 2:
# # # #         tkdl_overlap = translate_payload("High Prior Art Overlap (Ingredients recorded in TKDL)", request.language)
# # # #         base_score -= 10
# # # #     elif tkdl_overlap_count == 1:
# # # #         tkdl_overlap = translate_payload("Medium Prior Art Overlap", request.language)
# # # #     else:
# # # #         tkdl_overlap = translate_payload("Low Classical Overlap", request.language)
# # # #         base_score += 10
        
# # # #     overall_score = max(10, min(95, base_score))
    
# # # #     recommendations = []
# # # #     if not has_novel_tech:
# # # #         recommendations.append("To overcome Section 3(p), incorporate a standardized biomarker ratio (e.g. 95% Curcuminoids + 5% Piperine) or novel nano-formulation pathway.")
# # # #         recommendations.append("Provide in-vitro / in-vivo comparative trial data demonstrating statistical synergy (Combination Index < 0.8) to overcome Section 3(e).")
# # # #     else:
# # # #         recommendations.append("Draft patent claims focusing on the specific method of preparation, particle size distribution, and enhanced pharmacokinetic AUC profiles.")
    
# # # #     recommendations.append("Obtain National Biodiversity Authority (NBA) Form III clearance prior to grant of patent if utilizing raw herbs sourced in India.")
# # # #     recommendations.append("Conduct an exhaustive search on CSIR-TKDL and WIPO Patentscope under IPC A61K 36/00.")
    
# # # #     # Translate the hardcoded recommendations list
# # # #     translated_recs = [translate_payload(rec, request.language) for rec in recommendations]
    
# # # #     query = f"Patentability analysis for {request.formulation_name} with ingredients {', '.join(request.ingredients)}. Novelty: {request.novelty_description}"
# # # #     rag_data = retrieve_context(query)
# # # #     detailed_report = generate_rag_response(query, request.language, rag_data)
    
# # # #     risk_assessment = PatentabilityRiskScore(
# # # #         overall_score=overall_score,
# # # #         sec_3p_risk=sec_3p_risk,
# # # #         sec_3e_synergy_risk=sec_3e_risk,
# # # #         tkdl_prior_art_overlap=tkdl_overlap,
# # # #         nba_abs_required=True,
# # # #         recommended_ipc=recommended_ipc,
# # # #         recommendations=translated_recs
# # # #     )
    
# # # #     return FormulationAnalysisResponse(
# # # #         formulation_name=request.formulation_name,
# # # #         risk_assessment=risk_assessment,
# # # #         detailed_report=detailed_report,
# # # #         citations=rag_data["citations"]
# # # #     )

# # # # @router.post("/regulatory-wizard", response_model=LicenseWizardResponse)
# # # # def regulatory_wizard_endpoint(request: LicenseWizardRequest):
# # # #     cat = request.product_category
# # # #     claims = request.therapeutic_claims
# # # #     source = request.ingredients_source
    
# # # #     if cat == "classical" and source == "api_texts":
# # # #         reqs = [
# # # #             "Formulation recipe must strictly adhere to First Schedule texts of Drugs & Cosmetics Act (e.g. API, Charaka Samhita).",
# # # #             "Compliance with Schedule T Good Manufacturing Practices (GMP).",
# # # #             "Heavy metal, pesticide residue, and microbial testing report.",
# # # #             "Textual reference mandatory on product label."
# # # #         ]
# # # #         return LicenseWizardResponse(
# # # #             recommended_license=translate_payload("Classical Ayurvedic Medicine License", request.language),
# # # #             form_number="Form 25D",
# # # #             governing_authority=translate_payload("State Licensing Authority (AYUSH Department)", request.language),
# # # #             key_requirements=[translate_payload(r, request.language) for r in reqs],
# # # #             ctri_trial_needed=False,
# # # #             safety_toxicity_needed=False,
# # # #             fssai_applicable=False
# # # #         )
# # # #     elif cat == "proprietary" or (claims and source != "api_texts"):
# # # #         reqs = [
# # # #             "Proof of Safety and Efficacy under Rule 158B of Drugs & Cosmetics Rules.",
# # # #             "Published scientific pilot literature or acute/sub-acute toxicity studies.",
# # # #             "Schedule T GMP certified manufacturing facility.",
# # # #             "No claims for Schedule J prohibited diseases (Cancer, Diabetes cure, etc.)."
# # # #         ]
# # # #         return LicenseWizardResponse(
# # # #             recommended_license=translate_payload("Patent or Proprietary (P&P) Ayurvedic Medicine License", request.language),
# # # #             form_number="Form 25E / Form 25D (under Rule 158B)",
# # # #             governing_authority=translate_payload("State Licensing Authority (AYUSH) & DCGI Review", request.language),
# # # #             key_requirements=[translate_payload(r, request.language) for r in reqs],
# # # #             ctri_trial_needed=True,
# # # #             safety_toxicity_needed=True,
# # # #             fssai_applicable=False
# # # #         )
# # # #     elif cat == "health_supplement" or (not claims and cat != "cosmetic"):
# # # #         reqs = [
# # # #             "Ingredients must comply with FSSAI Schedule VI approved botanical list.",
# # # #             "Vitamins/minerals must stay within Recommended Daily Allowance (RDA) limits.",
# # # #             "STRICT PROHIBITION of disease prevention/cure therapeutic claims.",
# # # #             "Label must clearly state 'NOT FOR MEDICINAL USE'."
# # # #         ]
# # # #         return LicenseWizardResponse(
# # # #             recommended_license=translate_payload("FSSAI Health Supplement / Nutraceutical License", request.language),
# # # #             form_number="FSSAI Central / State License (Form B)",
# # # #             governing_authority=translate_payload("Food Safety and Standards Authority of India (FSSAI)", request.language),
# # # #             key_requirements=[translate_payload(r, request.language) for r in reqs],
# # # #             ctri_trial_needed=False,
# # # #             safety_toxicity_needed=False,
# # # #             fssai_applicable=True
# # # #         )
# # # #     else:
# # # #         reqs = [
# # # #             "Dermatological safety testing & heavy metal limits.",
# # # #             "Non-therapeutic skin/hair benefit claims only.",
# # # #             "Schedule T GMP compliance."
# # # #         ]
# # # #         return LicenseWizardResponse(
# # # #             recommended_license=translate_payload("AYUSH Cosmetic / Topical Herbal Product License", request.language),
# # # #             form_number="Form 32 / Form 25C",
# # # #             governing_authority=translate_payload("State AYUSH / State Licensing Authority", request.language),
# # # #             key_requirements=[translate_payload(r, request.language) for r in reqs],
# # # #             ctri_trial_needed=False,
# # # #             safety_toxicity_needed=False,
# # # #             fssai_applicable=False
# # # #         )

# # # # @router.post("/nba-calculator", response_model=NBACalculatorResponse)
# # # # def nba_calculator_endpoint(request: NBACalculatorRequest):
# # # #     turnover = request.annual_turnover_inr
    
# # # #     if turnover <= 10000000:
# # # #         percentage = 0.1
# # # #     elif turnover <= 30000000:
# # # #         percentage = 0.2
# # # #     else:
# # # #         percentage = 0.5
        
# # # #     estimated_royalty = (turnover * percentage) / 100.0
# # # #     form_type = "Form III" if request.entity_type == "foreign_with_foreign_equity" else "Form I / SBB Intimation"
    
# # # #     note = "Mandatory under Biological Diversity Act 2002 (amended 2023). Failure to obtain NBA clearance before commercial exploitation or patent grant can invite penalties under Section 55."
    
# # # #     # Optional: If you pass language in this request schema, you can translate 'note' here too. 
# # # #     # Defaulting to English since the original schema didn't include language.
    
# # # #     return NBACalculatorResponse(
# # # #         annual_turnover_inr=turnover,
# # # #         abs_percentage=percentage,
# # # #         estimated_royalty_inr=round(estimated_royalty, 2),
# # # #         nba_approval_form=form_type,
# # # #         legal_mandatory_note=note
# # # #     )

# # # # @router.get("/tkdl-search")
# # # # def tkdl_search_endpoint(q: str = ""):
# # # #     q_lower = q.lower().strip()
# # # #     results = []
    
# # # #     for name, data in AYURVEDIC_IPC_GLOSSARY.items():
# # # #         if not q_lower or q_lower in name or q_lower in data["sanskrit"].lower() or q_lower in data["latin"].lower():
# # # #             results.append({"name": name, **data})
            
# # # #     return {"query": q, "total": len(results), "results": results}