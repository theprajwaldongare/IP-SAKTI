"""
LLM Service Module for IP Sakti.
Integrates Google Gemini API for real-time generative responses with RAG injection.
Includes an intelligent RAG fallback synthesis engine for zero-config offline execution.
"""

import os
import json
import requests
from typing import Dict, Any, List
from app.config import settings
from app.multilingual import get_localized_header

SYSTEM_PROMPT = """You are 'IP Sakti', an expert AI consultant on Intellectual Property Rights (IPR), Patentability (Indian Patent Act 1970 Sec 3(p), 3(e)), Traditional Knowledge Digital Library (TKDL), Biological Diversity Act 2002 (NBA ABS), and AYUSH / FSSAI regulatory compliance for Ayurvedic formulations and products.

Always ground your answers in the retrieved RAG Context provided below.
Provide structured, clear, and actionable advice with headers, bullet points, legal section citations, and step-by-step guidance.
Respond in the language requested by the user.
"""

def call_gemini_api(prompt: str, system_instruction: str = SYSTEM_PROMPT) -> str:
    """Call Google Gemini API if GEMINI_API_KEY is available."""
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return ""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{system_instruction}\n\nUser Query & Context:\n{prompt}"}]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "topP": 0.8,
            "maxOutputTokens": 1024
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=12)
        if response.status_code == 200:
            res_json = response.json()
            candidates = res_json.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "")
    except Exception as e:
        print(f"[Gemini API Exception]: {e}")
        
    return ""

def synthesize_rag_fallback(query: str, rag_data: Dict[str, Any], lang: str = "en") -> str:
    """
    Intelligent Dynamic RAG Synthesizer when no external LLM API key is present.
    Constructs a rich, professional, domain-grounded response using retrieved context.
    """
    docs = rag_data.get("docs", [])
    citations = rag_data.get("citations", [])
    ingredients = rag_data.get("matched_ingredients", [])
    
    disclaimer = get_localized_header(lang, "disclaimer")
    sources_header = get_localized_header(lang, "sources")
    action_header = get_localized_header(lang, "action_plan")
    
    response_parts = []
    
    # Header & Overview
    response_parts.append(f"### 🛡️ IP Sakti Legal & Regulatory Guidance")
    
    if ingredients:
        ing_str = ", ".join([f"**{i['ingredient'].title()}** ({i['sanskrit']}, *{i['latin']}*)" for i in ingredients])
        response_parts.append(f"**Identified Botanical Components**: {ing_str}\n")
    
    # Primary Retrieval Snippets & Analysis
    response_parts.append("#### 📑 Key Findings & Regulatory Directives:")
    for idx, doc in enumerate(docs, 1):
        response_parts.append(f"**{idx}. {doc['title']}** ({doc['category']})")
        # Extract main guidance points
        content_lines = [line.strip() for line in doc['content'].split('\n') if line.strip()]
        for line in content_lines[:4]:
            response_parts.append(f"- {line}")
        response_parts.append("")
        
    # Ingredient-specific TKDL Risk if present
    if ingredients:
        response_parts.append("#### 🌿 Specific Herbal Prior Art & IPC Classification:")
        for ing in ingredients:
            response_parts.append(f"- **{ing['ingredient'].title()}**: Sanskrit: `{ing['sanskrit']}` | Latin: `*{ing['latin']}*` | Recommended IPC Subclass: `{ing['ipc']}` | TKDL Status: *{ing['tkdl_status']}*")
        response_parts.append("")
        
    # Actionable Steps
    response_parts.append(f"#### 🎯 {action_header}:")
    if "patent" in query.lower() or "section 3p" in query.lower() or "tkdl" in query.lower():
        response_parts.append("1. **Verify Prior Art in TKDL**: Conduct thorough search in CSIR-TKDL database for identical classical references before filing.")
        response_parts.append("2. **Establish Statistical Synergy**: Conduct comparative bio-assays demonstrating that combined ingredient efficacy exceeds sum of individual herbal components (Synergy Index > 1.0).")
        response_parts.append("3. **Highlight Novel Samskara / Extraction**: Document specific non-aqueous extraction, bio-enhancers (e.g., Trikatu/Piperine), or liposomal drug delivery pathways.")
        response_parts.append("4. **Apply for NBA Form III Clearance**: Submit Form III to National Biodiversity Authority prior to filing patent grant if using Indian botanicals.")
    elif "license" in query.lower() or "form 25" in query.lower() or "ayush" in query.lower() or "fssai" in query.lower():
        response_parts.append("1. **Determine Intent**: Use Form 25D for exact classical remedies in Ayurvedic Pharmacopoeia of India (API); Use Form 25E for novel combinations or proprietary dosage forms.")
        response_parts.append("2. **GMP Schedule T Compliance**: Ensure manufacturing facility meets Schedule T requirements with SLA validation.")
        response_parts.append("3. **FSSAI Boundary**: If marketing as health supplement, ensure label contains NO therapeutic/cure claims and ingredients comply with FSSAI Schedule VI RDA limits.")
    else:
        response_parts.append("1. **Document Formulation Standards**: Prepare complete batch manufacturing records (BMR) with raw material standardization certificates.")
        response_parts.append("2. **Obtain NBA Clearance**: Ensure compliance under Biological Diversity Act for raw bio-resource procurement.")
        response_parts.append("3. **Consult Registered Patent Agent**: Engage a registered Indian Patent Agent specializing in traditional phytomedicine patents.")
        
    # Citations
    response_parts.append(f"\n#### 📚 {sources_header}:")
    for cit in citations:
        response_parts.append(f"- `[{cit['id']}]` **{cit['title']}** — *{cit['source']}*")
        
    response_parts.append(f"\n> ⚖️ *{disclaimer}*")
    
    return "\n".join(response_parts)

def generate_rag_response(query: str, lang: str = "en", rag_data: Dict[str, Any] = None) -> str:
    """Generate final response combining Gemini API or RAG dynamic synthesis."""
    if not rag_data:
        from app.rag_engine import retrieve_context
        rag_data = retrieve_context(query)
        
    # Try Gemini API call first
    gemini_prompt = f"Target Language: {lang}\nQuery: {query}\n\nRetrieved Context:\n{rag_data['context_str']}"
    api_response = call_gemini_api(gemini_prompt)
    
    if api_response and len(api_response.strip()) > 50:
        return api_response
        
    # Fallback to dynamic RAG synthesis engine
    return synthesize_rag_fallback(query, rag_data, lang)
