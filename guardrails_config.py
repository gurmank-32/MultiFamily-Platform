"""
Guardrails configuration for Texas Housing Regulation Compliance Assistant
"""

# Supported jurisdictions
SUPPORTED_CITIES = ["Dallas", "Austin", "Houston", "San Antonio"]
SUPPORTED_STATE = "Texas"

# Allowed topics
ALLOWED_TOPICS = [
    # Federal
    "hud", "housing and urban development", "doj", "department of justice",
    "fair housing", "fair housing act", "fha",
    # Regulations
    "esa", "emotional support animal", "assistance animal", "service animal",
    "rent control", "rent cap", "rent limit", "rent increase",
    "zoning", "zoning law", "zoning ordinance",
    "section 8", "hcv", "housing choice voucher", "voucher program",
    # Professional roles
    "leasing manager", "leasing agent", "property manager", "landlord", "tenant",
    # Compliance
    "compliance", "compliant", "regulation", "law", "rule", "requirement",
    "lease", "leasing", "lease agreement", "lease terms",
    # Locations (supported only)
    "dallas", "austin", "houston", "san antonio", "texas",
    # Housing terms
    "housing", "property", "rental", "tenant rights", "landlord obligations",
    "habitability", "repair", "maintenance", "security deposit",
    # Related
    "discrimination", "accommodation", "disability", "reasonable accommodation"
]

# Irrelevant topic keywords (triggers guardrail)
IRRELEVANT_TOPICS = [
    "weather", "cooking", "recipe", "sports", "music", "movie", "tv show",
    "celebrity", "recipe", "food", "restaurant", "travel", "vacation",
    "shopping", "fashion", "entertainment", "game", "gaming", "technology",
    "computer", "software", "app", "phone", "crypto", "bitcoin", "stock",
    "investment", "finance", "banking", "insurance", "medical", "health",
    "doctor", "medicine", "education", "school", "university", "course"
]

# Out-of-scope states
OUT_OF_SCOPE_STATES = [
    "california", "cali", "new york", "florida", "illinois", "pennsylvania",
    "ohio", "georgia", "north carolina", "michigan", "new jersey", "virginia",
    "washington", "arizona", "massachusetts", "tennessee", "indiana", "missouri",
    "maryland", "wisconsin", "colorado", "minnesota", "south carolina",
    "alabama", "louisiana", "kentucky", "oregon", "oklahoma", "connecticut",
    "utah", "nevada", "iowa", "arkansas", "mississippi", "kansas", "new mexico",
    "nebraska", "west virginia", "idaho", "hawaii", "new hampshire", "maine",
    "montana", "rhode island", "delaware", "south dakota", "north dakota",
    "alaska", "vermont", "wyoming", "dc", "district of columbia"
]

# Unsupported Texas cities
UNSUPPORTED_TEXAS_CITIES = [
    "fort worth", "el paso", "arlington", "corpus christi", "plano", "laredo",
    "lubbock", "garland", "irving", "amarillo", "grand prairie", "brownsville",
    "mckinney", "frisco", "pasadena", "killeen", "mesquite", "mcallen",
    "carrollton", "midland", "denton", "abilene", "round rock", "odessa",
    "waco", "beaumont", "richardson", "lewisville", "tyler", "pearland"
]

# Legal reliance indicators
LEGAL_RELIANCE_KEYWORDS = [
    "i'll use this advice", "i will use this", "use this advice",
    "is this legally safe", "legally safe", "is this safe to",
    "can i rely on", "should i rely on", "follow your guidance",
    "rewrite my lease", "use this to", "based on your advice",
    "if i follow your", "legal guarantee", "legal advice"
]

# Inappropriate content keywords
INAPPROPRIATE_KEYWORDS = [
    # Hate speech indicators (be careful with false positives)
    # Harassment indicators
]

# Guardrail response messages
GUARDRAIL_RESPONSES = {
    "nonsense": "I'm here to assist with housing and leasing policies specifically for Texas cities. Please provide a question related to regulations in Dallas, Austin, Houston, or San Antonio.",
    "irrelevant": "I'm here to assist with housing and leasing policies specifically for Texas cities. Please provide a question related to regulations in Dallas, Austin, Houston, or San Antonio.",
    "out_of_scope_geography": "At this time, I only provide information on housing and leasing regulations within Dallas, Austin, Houston, and San Antonio, Texas. For questions related to other cities or states, please consult additional resources or local authorities.",
    "inappropriate": "I'm here to assist with housing and leasing policies specifically for Texas cities. Please provide a question related to regulations in Dallas, Austin, Houston, or San Antonio.",
    "legal_reliance": "I am not a legal advisor. Please consult a qualified legal professional to ensure full compliance with housing regulations and policies.",
    "legal_advice": "I am not a legal advisor. Please consult a qualified legal professional to ensure full compliance with housing regulations and policies.",
    "ambiguous": "I'm here to assist with housing and leasing policies specifically for Texas cities. Please provide a question related to regulations in Dallas, Austin, Houston, or San Antonio.",
    "missing_information": "I apologize — I do not currently have this information in my data sources. Please check back later for updates.",
    "fallback": "I'm here to assist with housing and leasing policies specifically for Texas cities. Please provide a question related to regulations in Dallas, Austin, Houston, or San Antonio."
}

