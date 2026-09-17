# IP Sakti - Multilingual AI Assistant for Ayurvedic IP & Regulatory Guidance

**IP Sakti** is an AI-powered platform for Intellectual Property Rights (IPR), Patentability (Section 3(p) and 3(e) of the Indian Patents Act, 1970), Traditional Knowledge Digital Library (TKDL) prior art search, National Biodiversity Authority (NBA) Access and Benefit Sharing (ABS), and AYUSH / FSSAI regulatory compliance for Ayurvedic formulations.

---

## Key Features

1. **RAG-Powered Multilingual AI Assistant**:
   - Intelligent chatbot trained on Ayurvedic IP laws, TKDL rules, AYUSH notifications, and FSSAI standards.
   - 8 Indian Languages Supported: **English**, **Hindi (हिंदी)**, **Sanskrit (संस्कृतम्)**, **Tamil (தமிழ்)**, **Telugu (తెలుగు)**, **Marathi (मराठी)**, **Gujarati (ગુજરાતી)**, and **Bengali (বাংলা)**.
   - Built-in Voice Input recognition and quick suggested prompts.

2. **Ayurvedic Formulation Patentability Analyzer**:
   - Evaluates herbal formulation ingredient lists for Section 3(p) traditional knowledge barriers.
   - Assesses Section 3(e) synergistic data requirements.
   - Generates visual patentability score index, TKDL prior art overlap risk, and recommended International Patent Classification (IPC) subclass codes (e.g. `A61K 36/00`).

3. **AYUSH vs. FSSAI Regulatory License Navigator**:
   - Guided wizard for determining exact manufacturing licensing requirements:
     - **Form 25D**: Classical Ayurvedic Medicines (Ayurvedic Pharmacopoeia of India API).
     - **Form 25E**: Patent or Proprietary (P&P) Ayurvedic Medicines under Rule 158B.
     - **FSSAI License**: Health Supplements / Dietary Nutraceuticals.
     - Clinical trial mandatory registration requirements under CTRI.

4. **National Biodiversity Act (NBA) ABS Royalty Calculator**:
   - Interactive calculator to compute mandatory Access & Benefit Sharing contribution rates under Biological Diversity Act 2002.

5. **TKDL & GI Knowledge Explorer**:
   - Searchable repository mapping Sanskrit names, botanical Latin names, IPC subclassifications, and landmark prior art cases.

---

## Tech Stack

- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism, Earthy Emerald & Warm Gold visual palette), Vanilla JavaScript (ES6+).
- **Backend**: FastAPI (Python 3.10+), Uvicorn server, Pydantic v2 schemas.
- **RAG Engine**: Semantic TF-IDF vector indexer, context scoring, and domain knowledge base.
- **LLM Integration**: Google Gemini API (`GEMINI_API_KEY`) with dynamic multi-lingual RAG fallback synthesis engine for zero-config offline execution.

---

## How to Run

### Step 1: Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: (Optional) Set Google Gemini API Key
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your_google_gemini_api_key_here"

# Windows Command Prompt
set GEMINI_API_KEY=your_google_gemini_api_key_here
```
*(Note: If no API key is set, the system automatically uses the dynamic RAG synthesis engine!)*

### Step 3: Start FastAPI Server
```bash
python backend/run.py
```
Or:
```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 4: Open Application in Web Browser
Open your browser and navigate to:
```
http://127.0.0.1:8000
```
API Documentation (Swagger UI):
```
http://127.0.0.1:8000/docs
```
