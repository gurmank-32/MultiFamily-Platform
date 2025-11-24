"""
Retrieval configuration for enhanced query processing and source prioritization
"""
from typing import List, Dict, Optional
import re

# Authoritative source patterns (higher priority)
AUTHORITATIVE_SOURCES = {
    "high_priority": [
        r"\.gov\b",  # Government websites
        r"\.edu\b",  # Educational institutions
        r"hud\.gov",  # HUD
        r"justice\.gov",  # DOJ
        r"texas\.gov",  # Texas government
        r"dallas\.gov",  # Dallas government
        r"houston\.gov",  # Houston government
        r"austin\.gov",  # Austin government
        r"sanantonio\.gov",  # San Antonio government
        r"texasattorneygeneral\.gov",  # Texas AG
        r"propertycode",  # Property code references
        r"statute",  # Statutes
        r"ordinance",  # Ordinances
    ],
    "medium_priority": [
        r"legal",  # Legal sites
        r"law",  # Law sites
        r"compliance",  # Compliance sites
    ],
    "low_priority": [
        r"news",  # News sites
        r"blog",  # Blogs
        r"opinion",  # Opinion pieces
    ]
}

# Legal and leasing terminology enhancement
LEGAL_TERMINOLOGY = {
    "housing": ["housing", "residential", "dwelling", "premises", "property", "rental", "lease"],
    "tenant": ["tenant", "lessee", "renter", "resident", "occupant"],
    "landlord": ["landlord", "lessor", "property owner", "property manager", "management"],
    "compliance": ["compliance", "comply", "requirement", "mandatory", "obligation", "duty"],
    "violation": ["violation", "violate", "prohibited", "illegal", "unlawful", "forbidden"],
    "rights": ["right", "entitlement", "privilege", "protection", "safeguard"],
    "fees": ["fee", "charge", "cost", "deposit", "rent", "payment"],
    "esa": ["esa", "emotional support animal", "service animal", "assistance animal", "reasonable accommodation"],
    "fair_housing": ["fair housing", "discrimination", "protected class", "equal opportunity"],
    "security_deposit": ["security deposit", "deposit", "refund", "deduction", "return"],
    "eviction": ["eviction", "evict", "termination", "remove", "dispossess"],
    "habitability": ["habitable", "habitability", "warranty", "maintenance", "repair"],
}

# Geographical context keywords
GEOGRAPHICAL_KEYWORDS = {
    "texas": ["texas", "tx", "statewide", "state-wide", "state law"],
    "dallas": ["dallas", "dfw", "dallas-fort worth"],
    "houston": ["houston", "harris county"],
    "austin": ["austin", "travis county"],
    "san_antonio": ["san antonio", "bexar county"],
}

# Query enhancement patterns
QUERY_ENHANCEMENT_PATTERNS = {
    "definition": {
        "keywords": ["what is", "what does", "define", "meaning", "explain"],
        "enhancement": "legal definition regulation statute ordinance code"
    },
    "compliance": {
        "keywords": ["compliant", "compliance", "legal", "violate", "required", "mandatory"],
        "enhancement": "compliance requirement obligation mandatory regulation law"
    },
    "scenario": {
        "keywords": ["if", "can i", "should i", "tenant", "landlord", "what if"],
        "enhancement": "regulation law requirement obligation right duty"
    },
    "new_law": {
        "keywords": ["new", "recent", "update", "latest", "change"],
        "enhancement": "recent update new regulation change amendment"
    }
}

def enhance_query_with_terminology(query: str, context: Optional[Dict] = None) -> str:
    """
    Enhance query with legal and leasing terminology
    """
    query_lower = query.lower()
    enhanced_terms = []
    
    # Add base query
    enhanced_terms.append(query)
    
    # Detect query type and add relevant terminology
    for query_type, pattern in QUERY_ENHANCEMENT_PATTERNS.items():
        if any(keyword in query_lower for keyword in pattern["keywords"]):
            enhanced_terms.append(pattern["enhancement"])
            break
    
    # Add legal terminology based on detected subjects
    for subject, terms in LEGAL_TERMINOLOGY.items():
        if any(term in query_lower for term in terms):
            # Add related terms
            enhanced_terms.extend(terms[:3])  # Add first 3 related terms
    
    # Add geographical context if detected
    if context and context.get("city"):
        city = context["city"].lower()
        for geo_key, keywords in GEOGRAPHICAL_KEYWORDS.items():
            if geo_key in city or any(kw in city for kw in keywords):
                enhanced_terms.extend(keywords[:2])
                break
    
    # Add Texas context if not already present
    if "texas" not in query_lower:
        enhanced_terms.append("texas")
    
    # Combine and deduplicate
    enhanced_query = " ".join(enhanced_terms)
    # Remove duplicate words while preserving order
    words = enhanced_query.split()
    seen = set()
    unique_words = []
    for word in words:
        word_lower = word.lower()
        if word_lower not in seen:
            seen.add(word_lower)
            unique_words.append(word)
    
    return " ".join(unique_words)

def calculate_source_reliability(url: str, source_name: str, category: str) -> float:
    """
    Calculate reliability score for a source (0.0 to 1.0)
    Higher score = more reliable/authoritative
    """
    score = 0.5  # Base score
    
    url_lower = url.lower()
    source_lower = source_name.lower()
    category_lower = category.lower()
    
    # Check for high priority sources
    for pattern in AUTHORITATIVE_SOURCES["high_priority"]:
        if re.search(pattern, url_lower) or re.search(pattern, source_lower):
            score = min(1.0, score + 0.4)
            break
    
    # Check for medium priority sources
    if score < 0.8:
        for pattern in AUTHORITATIVE_SOURCES["medium_priority"]:
            if re.search(pattern, url_lower) or re.search(pattern, source_lower):
                score = min(1.0, score + 0.2)
                break
    
    # Penalize low priority sources
    for pattern in AUTHORITATIVE_SOURCES["low_priority"]:
        if re.search(pattern, url_lower) or re.search(pattern, source_lower):
            score = max(0.0, score - 0.2)
            break
    
    # Boost for specific categories
    authoritative_categories = [
        "fair housing", "esa", "rent caps", "zoning", 
        "landlord/tenant", "state housing rules", "federal housing updates"
    ]
    if category_lower in [cat.lower() for cat in authoritative_categories]:
        score = min(1.0, score + 0.1)
    
    return round(score, 2)

def rerank_results(results: List[Dict], query: str, context: Optional[Dict] = None) -> List[Dict]:
    """
    Rerank search results based on:
    1. Source reliability
    2. Relevance score (from vector search)
    3. Geographical match
    4. Category relevance
    """
    if not results:
        return results
    
    query_lower = query.lower()
    context_city = context.get("city", "").lower() if context else ""
    
    scored_results = []
    
    for result in results:
        metadata = result.get("metadata", {})
        url = metadata.get("url", "")
        source_name = metadata.get("source_name", "")
        category = metadata.get("category", "")
        document = result.get("document", "").lower()
        
        # Base score from vector search (distance/score)
        base_score = 1.0 - result.get("distance", 1.0)  # Convert distance to similarity
        
        # Source reliability score
        reliability_score = calculate_source_reliability(url, source_name, category)
        
        # Geographical match score
        geo_score = 0.0
        if context_city:
            city_keywords = GEOGRAPHICAL_KEYWORDS.get(context_city.replace(" ", "_"), [])
            if any(kw in document for kw in city_keywords):
                geo_score = 0.3
            elif "texas" in document:
                geo_score = 0.1
        
        # Category relevance score
        category_score = 0.0
        if category:
            # Check if category matches query intent
            category_lower = category.lower()
            if any(term in query_lower for term in category_lower.split()):
                category_score = 0.2
        
        # Keyword match bonus
        keyword_score = 0.0
        query_words = set(query_lower.split())
        doc_words = set(document.split())
        common_words = query_words.intersection(doc_words)
        if common_words:
            keyword_score = min(0.2, len(common_words) * 0.05)
        
        # Calculate final score
        final_score = (
            base_score * 0.4 +           # Vector similarity (40%)
            reliability_score * 0.3 +    # Source reliability (30%)
            geo_score * 0.15 +            # Geographical match (15%)
            category_score * 0.1 +       # Category relevance (10%)
            keyword_score * 0.05          # Keyword match (5%)
        )
        
        scored_results.append({
            **result,
            "final_score": final_score,
            "reliability_score": reliability_score,
            "geo_score": geo_score,
            "category_score": category_score,
            "keyword_score": keyword_score
        })
    
    # Sort by final score (descending)
    scored_results.sort(key=lambda x: x["final_score"], reverse=True)
    
    return scored_results

def filter_by_geography(results: List[Dict], city: Optional[str] = None) -> List[Dict]:
    """
    Filter results by geographical relevance
    """
    if not city or city == "Texas-Statewide":
        return results
    
    city_lower = city.lower()
    city_keywords = GEOGRAPHICAL_KEYWORDS.get(city_lower.replace(" ", "_"), [city_lower])
    
    filtered = []
    for result in results:
        document = result.get("document", "").lower()
        metadata = result.get("metadata", {})
        source_name = metadata.get("source_name", "").lower()
        url = metadata.get("url", "").lower()
        
        # Check if document mentions the city or is Texas-wide
        is_relevant = (
            any(kw in document for kw in city_keywords) or
            any(kw in source_name for kw in city_keywords) or
            any(kw in url for kw in city_keywords) or
            "texas" in document or
            "statewide" in document or
            "state-wide" in document
        )
        
        if is_relevant:
            filtered.append(result)
    
    # If filtering removed all results, return original (fallback)
    return filtered if filtered else results

