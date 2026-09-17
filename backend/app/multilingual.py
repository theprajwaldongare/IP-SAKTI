"""
Multilingual Support Module for IP Sakti.
Provides translation mapping, localized prompts, and terminology conversions across 8 Indian languages.
"""

LANGUAGES = {
    "en": {"name": "English", "native": "English", "flag": "🇮🇳"},
    "hi": {"name": "Hindi", "native": "हिंदी", "flag": "🇮🇳"},
    "sa": {"name": "Sanskrit", "native": "संस्कृतम्", "flag": "🕉️"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "flag": "🇮🇳"},
    "te": {"name": "Telugu", "native": "తెలుగు", "flag": "🇮🇳"},
    "mr": {"name": "Marathi", "native": "मराठी", "flag": "🇮🇳"},
    "gu": {"name": "Gujarati", "native": "ગુજરાતી", "flag": "🇮🇳"},
    "bn": {"name": "Bengali", "native": "বাংলা", "flag": "🇮🇳"}
}

LOCALIZED_HEADERS = {
    "en": {
        "disclaimer": "IP Sakti Legal & Regulatory AI Advice (Subject to official IPO / AYUSH SLA verification)",
        "sources": "Referenced Legal Sources & Guidelines",
        "action_plan": "Recommended Action Plan",
        "patent_status": "Patentability Risk Status",
        "license_req": "Mandatory Licensing Requirement"
    },
    "hi": {
        "disclaimer": "आईपी शक्ति कानूनी और नियामक एआई सलाह (आधिकारिक पेटेंट कार्यालय / आयुष प्राधिकरण द्वारा सत्यापन के अधीन)",
        "sources": "संदर्भित कानूनी स्रोत एवं दिशा-निर्देश",
        "action_plan": "अनुशंसित कार्य योजना",
        "patent_status": "पेटेंट जोखिम स्थिति",
        "license_req": "अनिवार्य लाइसेंसिंग आवश्यकता"
    },
    "sa": {
        "disclaimer": "आईपी शक्ति विधि एवं नियमन एआई परामर्श (आयुष एवं पेटेंट कार्यालय प्रमाणाधीनम्)",
        "sources": "संदर्भित विधि ग्रन्थाः एवं मार्गदर्शिकाः",
        "action_plan": "अनुशंसितः कार्यप्रणाली योजना",
        "patent_status": "पेटेंट पात्रता स्थितिः",
        "license_req": "अनिवार्य लाइसेंसिंग आवश्यकता"
    },
    "ta": {
        "disclaimer": "IP Sakti சட்ட மற்றும் ஒழுங்குமுறை AI வழிகாட்டுதல்",
        "sources": "குறிப்பிடப்பட்ட சட்ட ஆதாரங்கள்",
        "action_plan": "பரிந்துரைக்கப்பட்ட நடவடிக்கை திட்டம்",
        "patent_status": "காப்புரிமை ஆபத்து நிலை",
        "license_req": "கட்டாய உரிம தேவை"
    },
    "te": {
        "disclaimer": "IP Sakti న్యాయ మరియు నియంత్రణ ఏఐ సలహా",
        "sources": "ప్రస్తావించబడిన చట్టపరమైన మూలాలు",
        "action_plan": "సిఫార్సు చేయబడిన కార్యాచరణ ప్రణాళిక",
        "patent_status": "పేటెంట్ ప్రమాద స్థితి",
        "license_req": "నిర్బంధ లైసెన్సింగ్ అవసరం"
    },
    "mr": {
        "disclaimer": "आयपी शक्ती कायदेशीर आणि नियामक एआय सल्ला",
        "sources": "संदर्भित कायदेशीर स्रोत आणि मार्गदर्शक तत्त्वे",
        "action_plan": "शिफारस केलेली कृती योजना",
        "patent_status": "पेटंट पात्रता धोका स्थिती",
        "license_req": "अनिवार्य परवाना आवश्यकता"
    },
    "gu": {
        "disclaimer": "IP Sakti કાનૂની અને નિયમનકારી AI સલાહ",
        "sources": "સંદર્ભિત કાનૂની સ્ત્રોતો અને માર્ગદર્શિકા",
        "action_plan": "ભલામણ કરેલ કાર્ય યોજના",
        "patent_status": "પેટન્ટ જોખમ સ્થિતિ",
        "license_req": "અનિવાર્ય લાઇસન્સિંગ જરૂરિયાત"
    },
    "bn": {
        "disclaimer": "IP Sakti আইনি ও নিয়ন্ত্রণকারী AI পরামর্শ",
        "sources": "উল্লেখিত আইনি উৎস এবং নির্দেশিকা",
        "action_plan": "সুপারিশকৃত কর্মপরিকল্পনা",
        "patent_status": "পেটেন্ট ঝুঁকি স্থিতি",
        "license_req": "বাধ্যতামূলক লাইসেন্সিং আবশ্যকতা"
    }
}

def get_localized_header(lang_code: str, key: str) -> str:
    lang_dict = LOCALIZED_HEADERS.get(lang_code, LOCALIZED_HEADERS["en"])
    return lang_dict.get(key, LOCALIZED_HEADERS["en"].get(key, ""))
