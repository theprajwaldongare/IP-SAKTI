/**
 * Multilingual UI Translations for IP Sakti Frontend
 */
const I18N_TRANSLATIONS = {
    en: {
        appTitle: "IP Sakti",
        subtitle: "Multilingual AI Assistant for Ayurvedic IP & Regulatory Guidance",
        navChat: "AI Assistant",
        navAnalyzer: "Formulation Analyzer",
        navWizard: "License Navigator",
        navNba: "NBA ABS Calculator",
        navTkdl: "TKDL & GI Explorer",
        onlineStatus: "Backend RAG Active",
        offlineStatus: "Offline Mode (RAG Fallback)",
        chatPlaceholder: "Ask about Section 3(p), TKDL prior art, Form 25D/25E, FSSAI, or patenting turmeric + ashwagandha...",
        sendBtn: "Ask IP Sakti",
        voiceBtn: "Voice Input",
        suggestTitle: "Suggested Prompts:",
        sug1: "How to overcome Section 3(p) for polyherbal syrup?",
        sug2: "Difference between Form 25D and Form 25E licenses?",
        sug3: "Is TKDL clearance mandatory before filing Indian patent?",
        sug4: "FSSAI RDA limits vs AYUSH medicinal claims?",
        analyzerTitle: "Ayurvedic Formulation Patentability Analyzer",
        analyzerDesc: "Evaluate Section 3(p) patent risk, TKDL prior art overlap, and Section 3(e) synergy requirements.",
        formNameLabel: "Formulation / Product Name",
        formNameHolder: "e.g., Liposomal Triphala Curcumin Extract",
        ingredientsLabel: "Herbal Ingredients (comma separated)",
        ingredientsHolder: "e.g., Turmeric, Ashwagandha, Piperine, Neem",
        noveltyLabel: "Novel Extraction / Technology Process",
        noveltyHolder: "e.g., Phytosome nano-emulsion with 5x bioavailability enhancement",
        intendedUseLabel: "Intended Therapeutic Benefit",
        intendedUseHolder: "e.g., Anti-inflammatory joint pain relief",
        analyzeBtn: "Analyze Patentability & Prior Art",
        wizardTitle: "AYUSH vs FSSAI Regulatory License Navigator",
        wizardDesc: "Determine whether your product needs Form 25D, Form 25E (Rule 158B), or FSSAI Nutraceutical licensing.",
        nbaTitle: "National Biodiversity Act (NBA) ABS Royalty Calculator",
        nbaDesc: "Calculate mandatory Access & Benefit Sharing contribution under Biological Diversity Act 2002.",
        tkdlTitle: "TKDL & IPC Patent Classification Explorer",
        tkdlDesc: "Browse classical Sanskrit Ayurvedic remedies, Latin plant names, and IPC A61K classification codes."
    },
    hi: {
        appTitle: "आईपी शक्ति",
        subtitle: "आयुर्वेदिक बौद्धिक संपदा एवं नियामक मार्गदर्शन हेतु बहुभाषी एआई सहायक",
        navChat: "एआई सहायक",
        navAnalyzer: "फॉर्मूलेशन विश्लेषक",
        navWizard: "लाइसेंस नेविगेटर",
        navNba: "एनबीए एबीएस कैलकुलेटर",
        navTkdl: "टीकेडीएल एवं जीआई एक्सप्लोरर",
        onlineStatus: "आरएजी इंजन सक्रिय",
        offlineStatus: "ऑफ़लाइन मोड (आरएजी फ़ॉलबैक)",
        chatPlaceholder: "धारा 3(p), टीकेडीएल पूर्व कला, फॉर्म 25D/25E, या पेटेंटability के बारे में पूछें...",
        sendBtn: "आईपी शक्ति से पूछें",
        voiceBtn: "वॉयस इनपुट",
        suggestTitle: "सुझाए गए प्रश्न:",
        sug1: "हर्बल सिरप के लिए धारा 3(p) को कैसे पार करें?",
        sug2: "फॉर्म 25D और फॉर्म 25E लाइसेंस में क्या अंतर है?",
        sug3: "क्या भारतीय पेटेंट से पहले TKDL जांच अनिवार्य है?",
        sug4: "FSSAI पोषण सीमा बनाम आयुष औषधीय दावे?",
        analyzerTitle: "आयुर्वेदिक फॉर्मूलेशन पेटेंट पात्रता विश्लेषक",
        analyzerDesc: "धारा 3(p) पेटेंट जोखिम, टीकेडीएल पूर्व कला और धारा 3(e) तालमेल का मूल्यांकन करें।",
        formNameLabel: "फॉर्मूलेशन / उत्पाद का नाम",
        formNameHolder: "उदा., लिपोसोमल त्रिफला करक्यूमिन एक्सट्रैक्ट",
        ingredientsLabel: "जड़ी-बूटी सामग्री (कॉमा से अलग करें)",
        ingredientsHolder: "उदा., हल्दी, अश्वगंधा, पिपरी, नीम",
        noveltyLabel: "नवीन निष्कर्षण / तकनीक प्रक्रिया",
        noveltyHolder: "उदा., 5x जैव उपलब्धता वृद्धि के साथ फाइटोसोम नैनो-इमल्शन",
        intendedUseLabel: "चिकित्सीय लाभ",
        intendedUseHolder: "उदा., सूजन रोधी जोड़ों के दर्द में राहत",
        analyzeBtn: "पेटेंट पात्रता का विश्लेषण करें",
        wizardTitle: "आयुष बनाम एफएसएसएआई नियामक लाइसेंस नेविगेटर",
        wizardDesc: "जानें कि आपके उत्पाद को फॉर्म 25D, फॉर्म 25E या FSSAI लाइसेंस की आवश्यकता है।",
        nbaTitle: "राष्ट्रीय जैव विविधता अधिनियम (NBA) एबीएस कैलकुलेटर",
        nbaDesc: "जैविक विविधता अधिनियम 2002 के तहत अनिवार्य रॉयल्टी योगदान की गणना करें।",
        tkdlTitle: "टीकेडीएल एवं आईपीसी पेटेंट वर्गीकरण खोज",
        tkdlDesc: "पारंपरिक संस्कृत आयुर्वेदिक औषधियों, लैटिन वनस्पति नामों और आईपीसी कोड का अन्वेषण करें।"
    },
    sa: {
        appTitle: "आईपी शक्तिः",
        subtitle: "आयुर्वेद बौद्धिकसम्पदा एवं नियमन परामर्श एआई सहायकः",
        navChat: "एआई परामर्शदाता",
        navAnalyzer: "योग विश्लेषणम्",
        navWizard: "अनुज्ञप्ति दर्शकम्",
        navNba: "एनबीए एबीएस गणकम्",
        navTkdl: "टीकेडीएल ज्ञानकोशः",
        onlineStatus: "आरएजी सक्रियः",
        offlineStatus: "ऑफ़लाइन मोड",
        chatPlaceholder: "आयुर्वेद पेटेंट विधिं, टीकेडीएल ज्ञानं, आयुष नियमं च पृच्छतु...",
        sendBtn: "पृच्छतु",
        voiceBtn: "वाणी इनपुट",
        suggestTitle: "अनुशंसित प्रश्नाः:",
        sug1: "बहुऔषध योगे धारा 3(p) कथं निवर्त्यम्?",
        sug2: "फॉर्म 25D तथा 25E अनुज्ञप्ति भेदः कः?",
        sug3: "पेटेंट आवदेनात् पूर्वं टीकेडीएल परीक्षणं अनिवार्यं किम्?",
        sug4: "एफएसएसएआई तथा आयुष नियम भेदः कः?",
        analyzerTitle: "आयुर्वेदिक योग पेटेंट पात्रता विश्लेषणम्",
        analyzerDesc: "धारा 3(p) पेटेंट जोखिमं तथा टीकेडीएल पूर्वज्ञानं परीक्षताम्।",
        formNameLabel: "औषध योग नाम",
        formNameHolder: "उदा., लिपोसोमल त्रिफला करक्यूमिन",
        ingredientsLabel: "द्रव्याणि (अल्पविरामेन पृथक् करोतु)",
        ingredientsHolder: "उदा., हरिद्रा, अश्वगंधा, पिप्पली, निम्बः",
        noveltyLabel: "नवीन निष्कर्षण विधिः",
        noveltyHolder: "उदा., नैनो-इमल्शन तकनीक विधिः",
        intendedUseLabel: "चिकित्सा प्रयोजनम्",
        intendedUseHolder: "उदा., शोधहर प्रभावः",
        analyzeBtn: "पात्रतां विश्लेषयतु",
        wizardTitle: "आयुष एवं एफएसएसएआई अनुज्ञप्ति दर्शकम्",
        wizardDesc: "फॉर्म 25D अथवा 25E अनुज्ञप्ति आवश्यकतां जानीहि।",
        nbaTitle: "राष्ट्रीय जैवविविधता अधिनियम (NBA) रॉयल्टी गणकम्",
        nbaDesc: "जैवविविधता अधिनियम 2002 अनुसारं एबीएस योगदानं गणयतु।",
        tkdlTitle: "टीकेडीएल संस्कृत ग्रन्थ एवं आईपीसी वर्गीकरणम्",
        tkdlDesc: "चरक सुश्रुत संहिता पादप नामानि एवं आईपीसी कोड पश्यतु।"
    }
};

let currentLang = "en";

function setAppLanguage(langCode) {
    currentLang = langCode;
    const dict = I18N_TRANSLATIONS[langCode] || I18N_TRANSLATIONS["en"];
    
    document.querySelectorAll("[data-i18n]").forEach(elem => {
        const key = elem.getAttribute("data-i18n");
        if (dict[key]) {
            if (elem.tagName === "INPUT" || elem.tagName === "TEXTAREA") {
                elem.placeholder = dict[key];
            } else {
                elem.textContent = dict[key];
            }
        }
    });
}
