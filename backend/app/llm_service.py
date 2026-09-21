"""
LLM Service Module for IP Sakti.
Integrates Google Gemini API for real-time generative responses with RAG injection.
"""

import os
import requests
from typing import Dict, Any
from app.config import settings
from app.multilingual import LANGUAGES

def call_gemini_api(prompt: str, system_instruction: str) -> str:
    """Call Google Gemini API."""
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return "API Error: GEMINI_API_KEY is missing. Please add it to your .env file."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{system_instruction}\n\n{prompt}"}]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "topP": 0.8,
            "maxOutputTokens": 1024
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=90)
        if response.status_code == 200:
            res_json = response.json()
            candidates = res_json.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "")
        else:
            return f"API Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"[Gemini API Exception]: {e}"
        
    return "Error: Failed to generate response from Gemini API."

def generate_rag_response(query: str, lang: str = "en", jurisdiction: str = "india", rag_data: Dict[str, Any] = None) -> str:
    """Generate response using Gemini API with strict language & jurisdiction rules."""
    if not rag_data:
        from app.rag_engine import retrieve_context
        rag_data = retrieve_context(query)
        
    target_lang_name = LANGUAGES.get(lang, {}).get("name", "English")
    
    if jurisdiction == "international":
        jur_guidance = """JURISDICTION: INTERNATIONAL IP REGIME
Focus on: WIPO Treaty on Intellectual Property, Genetic Resources and Associated Traditional Knowledge (GRATK 2024), Patent Cooperation Treaty (PCT), TRIPS Agreement, Nagoya Protocol on Access and Benefit Sharing, Budapest Treaty for Micro-organisms, and key export compliance frameworks (US FDA Botanical Drug Guidance / EU EMA Herbal Directives). Highlight mandatory disclosure of origin."""
    else:
        jur_guidance = """JURISDICTION: INDIAN NATIONAL IP REGIME
Focus on: Indian Patents Act 1970 (Section 3(p) traditional knowledge, Section 3(e) mere admixture, Section 3(c) natural substances), CSIR-TKDL prior art defense, Biological Diversity Act 2002 (amended 2023) NBA Form III clearance, and Drugs & Cosmetics Act (Form 25D In-House vs Form 25E Loan License, Rule 158B for proprietary medicines)."""
    
    system_instruction = f"""You are 'IP Sakti', an authoritative AI advisor for Ayurvedic Intellectual Property & Regulatory Compliance.

{jur_guidance}

CRITICAL LANGUAGE REQUIREMENT: You MUST write your response ENTIRELY in {target_lang_name}. Do not switch back to English mid-response except for specific Latin plant names, IPC codes, or standard statutory labels.
Ground your guidance in the provided RAG Context whenever relevant. Give clear, direct bullet points and actionable legal steps.
"""
    
    gemini_prompt = f"User Query: {query}\n\nRetrieved Knowledge Base Context:\n{rag_data['context_str']}"
    
    return call_gemini_api(gemini_prompt, system_instruction)

# """
# LLM Service Module for IP Sakti.
# Integrates Google Gemini API for real-time generative responses with RAG injection.
# """

# import os
# import requests
# from typing import Dict, Any
# from app.config import settings
# from app.multilingual import LANGUAGES

# def call_gemini_api(prompt: str, system_instruction: str) -> str:
#     """Call Google Gemini API."""
#     api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
#     if not api_key:
#         return "API Error: GEMINI_API_KEY is missing. Please add it to your .env file."
    
#     url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={api_key}"
#     headers = {"Content-Type": "application/json"}
#     payload = {
#         "contents": [
#             {
#                 "role": "user",
#                 "parts": [{"text": f"{system_instruction}\n\n{prompt}"}]
#             }
#         ],
#         "generationConfig": {
#             "temperature": 0.3,
#             "topP": 0.8,
#             "maxOutputTokens": 1024
#         }
#     }
    
#     try:
#         response = requests.post(url, headers=headers, json=payload, timeout=45)
#         if response.status_code == 200:
#             res_json = response.json()
#             candidates = res_json.get("candidates", [])
#             if candidates:
#                 parts = candidates[0].get("content", {}).get("parts", [])
#                 if parts:
#                     return parts[0].get("text", "")
#         else:
#             return f"API Error: {response.status_code} - {response.text}"
#     except Exception as e:
#         return f"[Gemini API Exception]: {e}"
        
#     return "Error: Failed to generate response from Gemini API."

# def generate_rag_response(query: str, lang: str = "en", jurisdiction: str = "india", rag_data: Dict[str, Any] = None) -> str:
#     """Generate response using Gemini API with strict language & jurisdiction rules."""
#     if not rag_data:
#         from app.rag_engine import retrieve_context
#         rag_data = retrieve_context(query)
        
#     target_lang_name = LANGUAGES.get(lang, {}).get("name", "English")
    
#     if jurisdiction == "international":
#         jur_guidance = """JURISDICTION: INTERNATIONAL IP REGIME
# Focus on: WIPO Treaty on Intellectual Property, Genetic Resources and Associated Traditional Knowledge (GRATK 2024), Patent Cooperation Treaty (PCT), TRIPS Agreement, Nagoya Protocol on Access and Benefit Sharing, Budapest Treaty for Micro-organisms, and key export compliance frameworks (US FDA Botanical Drug Guidance / EU Herbal Medicinal Products Directive EMA/HMPC). Explain mandatory disclosure requirements for genetic resources."""
#     else:
#         jur_guidance = """JURISDICTION: INDIAN NATIONAL IP REGIME
# Focus on: Indian Patents Act 1970 (Section 3(p) traditional knowledge, Section 3(e) admixture, Section 3(c) natural substances), CSIR-TKDL prior art defense, Biological Diversity Act 2002 (amended 2023) NBA Form III clearance, and Drugs & Cosmetics Act (Form 25D In-House vs Form 25E Loan License, Rule 158B for proprietary medicines)."""
    
#     system_instruction = f"""You are 'IP Sakti', an authoritative AI advisor for Ayurvedic Intellectual Property & Regulatory Compliance.

# {jur_guidance}

# CRITICAL LANGUAGE REQUIREMENT: You MUST write your response ENTIRELY in {target_lang_name}. Do not switch back to English mid-response except for specific Latin plant names, IPC codes, or standard statutory labels.
# Ground your guidance in the provided RAG Context whenever relevant. Give clear, direct bullet points and actionable legal steps.
# """
    
#     gemini_prompt = f"User Query: {query}\n\nRetrieved Knowledge Base Context:\n{rag_data['context_str']}"
    
#     return call_gemini_api(gemini_prompt, system_instruction)

# # """
# # LLM Service Module for IP Sakti.
# # Integrates Google Gemini API for real-time generative responses with RAG injection.
# # """

# # import os
# # import requests
# # from typing import Dict, Any
# # from app.config import settings
# # from app.multilingual import LANGUAGES

# # def call_gemini_api(prompt: str, system_instruction: str) -> str:
# #     """Call Google Gemini API."""
# #     api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
# #     if not api_key:
# #         return "API Error: GEMINI_API_KEY is missing. Please add it to your .env file."
    
# #     # url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
# #     url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={api_key}"
# #     headers = {"Content-Type": "application/json"}
# #     payload = {
# #         "contents": [
# #             {
# #                 "role": "user",
# #                 "parts": [{"text": f"{system_instruction}\n\n{prompt}"}]
# #             }
# #         ],
# #         "generationConfig": {
# #             "temperature": 0.3,
# #             "topP": 0.8,
# #             "maxOutputTokens": 1024
# #         }
# #     }
    
# #     try:
# #         response = requests.post(url, headers=headers, json=payload, timeout=45)
# #         if response.status_code == 200:
# #             res_json = response.json()
# #             candidates = res_json.get("candidates", [])
# #             if candidates:
# #                 parts = candidates[0].get("content", {}).get("parts", [])
# #                 if parts:
# #                     return parts[0].get("text", "")
# #         else:
# #             return f"API Error: {response.status_code} - {response.text}"
# #     except Exception as e:
# #         return f"[Gemini API Exception]: {e}"
        
# #     return "Error: Failed to generate response from Gemini API."

# # def generate_rag_response(query: str, lang: str = "en", rag_data: Dict[str, Any] = None) -> str:
# #     """Generate final response using Gemini API with strict language enforcement."""
# #     if not rag_data:
# #         from app.rag_engine import retrieve_context
# #         rag_data = retrieve_context(query)
        
# #     target_lang_name = LANGUAGES.get(lang, {}).get("name", "English")
    
# #     # 1. Force the prompt to strictly adhere to the requested language
# #     system_instruction = f"""You are 'IP Sakti', an expert AI consultant on Intellectual Property Rights (IPR), Patentability (Indian Patent Act 1970 Sec 3(p), 3(e)), Traditional Knowledge Digital Library (TKDL), Biological Diversity Act 2002 (NBA ABS), and AYUSH / FSSAI regulatory compliance.

# # CRITICAL INSTRUCTION: You MUST write your ENTIRE response in {target_lang_name}. Do not use English unless you are citing a specific Latin botanical name or an IPC code. 

# # Always ground your answers in the retrieved RAG Context provided below. Provide structured, clear, and actionable advice with headers, bullet points, and step-by-step guidance.
# # """
    
# #     gemini_prompt = f"User Query: {query}\n\nRetrieved Context:\n{rag_data['context_str']}"
    
# #     return call_gemini_api(gemini_prompt, system_instruction)