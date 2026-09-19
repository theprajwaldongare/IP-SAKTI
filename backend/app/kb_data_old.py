"""
Comprehensive Knowledge Base for Ayurvedic IP & Regulatory Guidance.
Contains structured legal clauses, AYUSH notifications, Indian Patent Act sections,
TKDL guidelines, NBA ABS rules, FSSAI regulations, and GI tag records.
"""

KNOWLEDGE_BASE = [
    {
        "id": "pat_sec3p",
        "category": "Patent Law",
        "title": "Section 3(p) of Indian Patents Act, 1970 - Traditional Knowledge Exclusion",
        "keywords": ["section 3p", "traditional knowledge", "patent act", "patentability", "prior art", "ayurvedic formulation", "herbal composition"],
        "content": """Section 3(p) of the Patents Act, 1970 explicitly states that 'an invention which in effect, is traditional knowledge or which is an aggregation or duplication of known properties of traditionally known component or components' is NOT patentable. 

Key Requirements for Ayurvedic Patentability:
1. Mere combination of classical herbs (e.g., Turmeric + Neem) described in Samhitas (Charaka, Sushruta, Astanga Hridaya) is excluded under Sec 3(p).
2. To overcome Section 3(p), the applicant must demonstrate SYNERGY (where the combined biological effect is statistically superior to sum of individual ingredients) or a NOVEL extraction pathway/standardized biomarker ratio/novel delivery mechanism (e.g. liposomal, phytosome, nano-emulsion).
3. The synergistic claims must be supported by quantitative bio-assay data, in-vitro/in-vivo comparative experimental results in the specification.""",
        "source": "Indian Patents Act, 1970 (as amended 2005) - IPO Guidelines for Patenting Traditional Knowledge"
    },
    {
        "id": "pat_sec3e",
        "category": "Patent Law",
        "title": "Section 3(e) of Indian Patents Act - Mere Admixture",
        "keywords": ["section 3e", "mere admixture", "synergy", "synergistic effect", "formulation patent", "polyherbal"],
        "content": """Section 3(e) prohibits patenting of 'a substance obtained by a mere admixture resulting only in the aggregation of the properties of the components thereof or a process for producing such substance'.

In Ayurvedic Polyherbal formulations:
- Combining Herb A (antidiabetic) + Herb B (antidiabetic) will be rejected under 3(e) unless a synergistic interaction is proven.
- Experimental proof: Must include individual ingredient dosage testing vs combined dosage showing non-additive, enhanced therapeutic efficacy (Synergy Index > 1.0).""",
        "source": "Manual of Patent Office Practice and Procedure (MPOPP), CGPDTM India"
    },
    {
        "id": "tkdl_01",
        "category": "TKDL Prior Art",
        "title": "Traditional Knowledge Digital Library (TKDL) & Prior Art Search",
        "keywords": ["tkdl", "prior art", "traditional knowledge digital library", "csir", "ayush", "sanskrit texts", "samhita", "patent revocation"],
        "content": """The Traditional Knowledge Digital Library (TKDL) is a landmark Indian initiative managed by CSIR and Ministry of AYUSH containing over 480,000 formulation entries translated from Sanskrit, Arabic, Persian, and Tamil into 5 international languages (English, French, German, Japanese, Spanish).

Impact on Patent Applications:
- International Patent Offices (EPO, USPTO, JPO, IPO) access TKDL to verify prior art.
- If an Ayurvedic formulation matches a classical remedy recorded in Charaka Samhita, Sushruta Samhita, Sharangdhara Samhita, Rasa Ratna Samuccaya, or API (Ayurvedic Pharmacopoeia of India), it is cited as prior art to reject claims.
- Strategy: Formulations must demonstrate clear non-obvious modifications, specific novel processing (Samskara), novel solvent extractions beyond traditional water/decoction/asava methods.""",
        "source": "CSIR-TKDL Access Agreement & IPO Search Guidelines"
    },
    {
        "id": "nba_01",
        "category": "Biodiversity & ABS",
        "title": "National Biodiversity Authority (NBA) & Access and Benefit Sharing (ABS)",
        "keywords": ["nba", "national biodiversity act", "abs", "access and benefit sharing", "biological diversity act 2002", "raw material clearance", "foreign entity", "royalty"],
        "content": """Under the Biological Diversity Act 2002 (amended 2023):
1. Foreign Entities / Indian Entities with Foreign Equity: Must obtain prior approval from National Biodiversity Authority (NBA) (Form I) before accessing Indian biological resources (Ayurvedic herbs, raw plants, micro-organisms) for commercialization or applying for IP rights (Form III).
2. Indian Citizens/Entities: Must notify State Biodiversity Boards (SBB) for commercial utilization of bio-resources.
3. Access & Benefit Sharing (ABS) Fee Structure:
   - Annual Gross Ex-Factory Sale Price up to ₹1 Crore: 0.1% ABS Royalty.
   - ₹1 Crore to ₹3 Crore: 0.2% ABS Royalty.
   - Exceeding ₹3 Crore: 0.5% ABS Royalty.
4. Section 6(1) IP Approval: NBA Form III approval is mandatory BEFORE obtaining grant of patent in India or overseas if the invention utilizes Indian biological material.""",
        "source": "Biological Diversity Act, 2002 & BD (Amendment) Act, 2023 - NBA Guidelines"
    },
    {
        "id": "ayush_25d",
        "category": "Regulatory Licensing",
        "title": "AYUSH Manufacturing License: Form 25D (Classical Ayurvedic Medicines)",
        "keywords": ["form 25d", "classical ayurvedic medicine", "ayush license", "gmp certification", "schedule t", "api standards", "manufacturing license"],
        "content": """Form 25D is the license issued by State Licensing Authorities (SLA - AYUSH) to manufacture Classical Ayurvedic Medicines.

Key Requirements:
1. Formulation Source: Must strictly adhere to recipes mentioned in authoritative texts specified in the First Schedule of Drugs & Cosmetics Act, 1940 (e.g. Ayurvedic Pharmacopoeia of India, Sahasrayogam, Bharat Bhashajya Ratnakara).
2. Clinical Data: NO prior clinical trial data required since classical safety and efficacy is historically recognized under section 3(a) of Drugs & Cosmetics Act.
3. Quality & Safety: Must comply with Schedule T Good Manufacturing Practices (GMP) and API limits for heavy metals (Lead, Arsenic, Cadmium, Mercury), pesticide residues, and aflatoxins.
4. Labeling: Must display exact textual reference and dosage on the outer carton.""",
        "source": "Drugs and Cosmetics Act, 1940 & Rules 1945 (Rule 153, Schedule T)"
    },
    {
        "id": "ayush_25e",
        "category": "Regulatory Licensing",
        "title": "AYUSH Manufacturing License: Form 25E (Proprietary Ayurvedic Medicines - Rule 158B)",
        "keywords": ["form 25e", "proprietary ayurvedic medicine", "rule 158b", "patent or proprietary", "proof of efficacy", "safety data", "pilot clinical study"],
        "content": """Form 25E grants approval for Patent or Proprietary (P&P) Ayurvedic Medicines under Rule 158B of Drugs & Cosmetics Rules.

Requirements under Rule 158B:
1. Product Concept: Formulation containing ingredients mentioned in Ayurvedic texts, but in non-classical ratios, novel dosage forms (tablets, capsules, syrups), or new combined indications.
2. Safety & Efficacy Evidence:
   - Category A (New Combination of Known Ayurvedic Ingredients): Requires published scientific literature or 1-year safety pilot observation study.
   - Category B (New Extract Ratio or Non-traditional Solvent): Requires acute/sub-acute animal toxicity studies and Phase I/II clinical trial evidence.
3. Labeling: Cannot claim instant cures for diseases listed in Schedule J (e.g., Cancer, Diabetes, AIDS, Blindness). Must clearly state 'Proprietary Ayurvedic Medicine'.""",
        "source": "Drugs & Cosmetics Rules 1945 - Rule 158B Notification (GSR 85(E))"
    },
    {
        "id": "fssai_vs_ayush",
        "category": "Regulatory Licensing",
        "title": "FSSAI Health Supplements vs. AYUSH Medicines Classification",
        "keywords": ["fssai", "ayush vs fssai", "nutraceuticals", "health supplements", "botanicals", "food safety act", "therapeutic claim"],
        "content": """Borderline Classification between FSSAI Nutraceuticals and AYUSH Drugs:

1. AYUSH Licensing (Drugs & Cosmetics Act):
   - Scope: Intended to prevent, mitigate, or treat diseases (Therapeutic / Prophylactic claims).
   - Ingredients: Classical Ayurvedic herbs, Bhasmas, Kwaths, Asavas.
   - Regulatory Body: Ministry of AYUSH & State Licensing Authority (SLA).

2. FSSAI Licensing (Food Safety Standards Act, 2006):
   - Scope: Maintenance of health, general well-being, dietary supplementation. CANNOT make disease cure/treatment claims.
   - Ingredients: Schedule VI approved botanical ingredients, vitamins, minerals within Recommended Daily Allowance (RDA) limits.
   - Regulatory Body: Food Safety and Standards Authority of India (FSSAI).
   - Penalty for Misclassification: Labeling therapeutic claims on FSSAI products leads to heavy fines under Section 52/53 of FSS Act.""",
        "source": "FSSAI (Health Supplements, Nutraceuticals, Food for Special Dietary Use) Regulations, 2022"
    },
    {
        "id": "ctri_trials",
        "category": "Clinical Trials & Validation",
        "title": "CTRI Registration & Clinical Validation for Ayurvedic Formulations",
        "keywords": ["ctri", "clinical trial registry india", "clinical trials", "ayurvedic trial", "gcp guidelines", "ethical approval", "icmr"],
        "content": """Clinical Trials Registry - India (CTRI) registration is mandatory for all clinical studies conducted on human subjects in India involving Ayurvedic drugs.

Validation Roadmap:
1. Ethical Clearance: Approval from Institutional Ethics Committee (IEC) registered with CDSCO/DHR.
2. Trial Registration: Mandatory registration on ctri.nic.in BEFORE enrolling the first participant.
3. Guidelines: Must follow Ministry of AYUSH General Guidelines for Clinical Evaluation of Ayurvedic Interventions and ICMR Ethical Guidelines.
4. Outcome Indicators: Must use validated primary/secondary clinical endpoints alongside traditional Ayurvedic parameter measurements (Agni, Prakriti, Dhatu balance).""",
        "source": "ICMR Guidelines for Biomedical Research & Ministry of AYUSH Clinical Trial Protocols"
    },
    {
        "id": "gi_tags",
        "category": "Geographical Indications",
        "title": "Geographical Indications (GI Tags) for Indian Medicinal Herbs & Ayurvedic Regions",
        "keywords": ["geographical indication", "gi tag", "kashmiri saffron", "navara rice", "darjeeling", "malabar pepper", "regional herbs", "ip protection"],
        "content": """Geographical Indication (GI) tag protects regional traditional products whose quality, reputation, or characteristics are attributable to their geographical origin.

Key Ayurvedic GI Tags in India:
1. Navara Rice (Kerala) - Used in Navarakizhi Ayurvedic rejuvenation therapy.
2. Kashmiri Saffron (Kumkuma) - Renowned for high crocin and safranal content.
3. Malabar Black Pepper - High piperine bioactive content.
4. Elettaria Cardamom (Idukki) - Premium therapeutic essential oils.
5. Jalgaon Banana & Nagpur Orange - Applied in specific fermented preparations.

Commercial IP Advantage:
- Authorized users of GI tags gain premium market positioning and international protection under TRIPS Agreement against counterfeits.""",
        "source": "Geographical Indications of Goods (Registration and Protection) Act, 1999"
    },
    {
        "id": "ipc_classification",
        "category": "Patent Strategy",
        "title": "International Patent Classification (IPC) Codes for Ayurvedic Inventions",
        "keywords": ["ipc code", "patent classification", "a61k", "a61p", "medicinal plants", "phytomedicine", "patent search"],
        "content": """Key IPC (International Patent Classification) Subclasses for Herbal & Ayurvedic Patent Filings:

1. A61K 36/00: Medicinal preparations containing material from algae, fungi, lichens or plants (e.g. A61K 36/53 for Lamiaceae/Tulsi, A61K 36/9068 for Zingiberaceae/Ginger).
2. A61K 35/00: Medicinal preparations containing materials of animal or indeterminate origin (e.g., Panchagavya, Honey, Ghee vehicles).
3. A61P 29/00: Non-central analgesic, antipyretic or anti-inflammatory remedies (e.g. Shallaki/Boswellia formulations).
4. A61P 3/10: Drugs for treatment of Diabetes Mellitus (e.g. Gurmar/Gymnema sylvestre, Vijaysar).
5. A61K 9/127 & A61K 9/51: Nano-carrier, phytosome, liposomal delivery of phytochemicals (High patent approval probability).""",
        "source": "WIPO International Patent Classification Manual (IPC 2024.01)"
    }
]

# Glossaries for Terminology Mapping
AYURVEDIC_IPC_GLOSSARY = {
    "turmeric": {"sanskrit": "Haridra (हरिद्रा)", "latin": "Curcuma longa", "active": "Curcuminoids", "ipc": "A61K 36/9066", "tkdl_status": "High prior art protection"},
    "ashwagandha": {"sanskrit": "Ashwagandha (अश्वगंधा)", "latin": "Withania somnifera", "active": "Withanolides", "ipc": "A61K 36/81", "tkdl_status": "High prior art protection"},
    "neem": {"sanskrit": "Nimba (निम्ब)", "latin": "Azadirachta indica", "active": "Azadirachtin", "ipc": "A61K 36/58", "tkdl_status": "Landmark revoked patent prior art (EPO EPO 0436257)"},
    "tulsi": {"sanskrit": "Tulasi (तुलसी)", "latin": "Ocimum sanctum", "active": "Eugenol, Ursolic acid", "ipc": "A61K 36/53", "tkdl_status": "High prior art protection"},
    "guggulu": {"sanskrit": "Guggulu (गुग्गुलु)", "latin": "Commiphora mukul", "active": "Guggulsterones", "ipc": "A61K 36/32", "tkdl_status": "Protected classical resin"},
    "shallaki": {"sanskrit": "Shallaki (शल्लकी)", "latin": "Boswellia serrata", "active": "Boswellic acids", "ipc": "A61K 36/324", "tkdl_status": "Anti-inflammatory prior art"},
    "triphala": {"sanskrit": "Triphala (त्रिफला)", "latin": "Amalaki + Haritaki + Vibhitaki", "active": "Tannins, Gallic acid", "ipc": "A61K 36/185", "tkdl_status": "Classical polyherbal prior art"},
    "trikatu": {"sanskrit": "Trikatu (त्रिकटु)", "latin": "Sunthi + Maricha + Pippali", "active": "Piperine, Gingerol", "ipc": "A61K 36/906", "tkdl_status": "Bio-enhancer prior art"},
    "giloy": {"sanskrit": "Guduchi (गुडूची)", "latin": "Tinospora cordifolia", "active": "Tinosporoside", "ipc": "A61K 36/59", "tkdl_status": "Immunomodulator prior art"},
    "brahmi": {"sanskrit": "Brahmi (ब्राह्मी)", "latin": "Bacopa monnieri", "active": "Bacosides", "ipc": "A61K 36/80", "tkdl_status": "Nootropic prior art"}
}
