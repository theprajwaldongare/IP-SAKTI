from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatRequest(BaseModel):
    query: str = Field(..., description="User question or query about Ayurvedic IP / regulatory law")
    language: str = Field("en", description="Target language code (en, hi, sa, ta, te, mr, gu, bn)")

class CitationItem(BaseModel):
    id: str
    title: str
    source: str
    relevance: float

class ChatResponse(BaseModel):
    query: str
    language: str
    answer: str
    citations: List[CitationItem]
    matched_ingredients: List[Dict[str, Any]]

class FormulationAnalysisRequest(BaseModel):
    formulation_name: str = Field(..., example="Triphala Curcumin Liposomal Syrup")
    ingredients: List[str] = Field(..., example=["Turmeric", "Triphala", "Piperine"])
    novelty_description: Optional[str] = Field("", example="Liposomal nano-emulsion extract with 5x enhanced bioavailability")
    intended_use: Optional[str] = Field("Anti-inflammatory & digestive health", example="Anti-inflammatory & joint care")
    language: str = Field("en")

class PatentabilityRiskScore(BaseModel):
    overall_score: int # 0-100 (Higher means more patentable)
    sec_3p_risk: str # High, Medium, Low
    sec_3e_synergy_risk: str # High, Medium, Low
    tkdl_prior_art_overlap: str # High, Medium, Low
    nba_abs_required: bool
    recommended_ipc: List[str]
    recommendations: List[str]

class FormulationAnalysisResponse(BaseModel):
    formulation_name: str
    risk_assessment: PatentabilityRiskScore
    detailed_report: str
    citations: List[CitationItem]

class LicenseWizardRequest(BaseModel):
    product_category: str # "classical", "proprietary", "health_supplement", "cosmetic"
    therapeutic_claims: bool # True if claims to cure/mitigate disease
    dosage_form: str # "traditional_asava", "syrup", "tablet", "capsule", "nano_emulsion"
    ingredients_source: str # "api_texts", "novel_combination", "standardized_extract"
    language: str = Field("en")

class LicenseWizardResponse(BaseModel):
    recommended_license: str
    form_number: str
    governing_authority: str
    key_requirements: List[str]
    ctri_trial_needed: bool
    safety_toxicity_needed: bool
    fssai_applicable: bool

class NBACalculatorRequest(BaseModel):
    annual_turnover_inr: float = Field(..., description="Annual Gross Ex-Factory Sale Price in INR")
    entity_type: str = Field("indian", description="indian or foreign_with_foreign_equity")
    bio_resource_origin: str = Field("cultivated", description="wild or cultivated")

class NBACalculatorResponse(BaseModel):
    annual_turnover_inr: float
    abs_percentage: float
    estimated_royalty_inr: float
    nba_approval_form: str
    legal_mandatory_note: str
