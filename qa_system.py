"""
Q&A System for answering questions from regulations using RAG
"""
from vector_store import RegulationVectorStore
from database import RegulationDB
from scraper import RegulationScraper
from config import OPENAI_API_KEY, LEGAL_DISCLAIMER
from prompts_config import (
    QA_SYSTEM_PROMPT, JARGON_EXPLANATION_PROMPT, 
    enhance_prompt_with_subject, get_subject_prompt
)
from guardrails_config import (
    ALLOWED_TOPICS, IRRELEVANT_TOPICS, OUT_OF_SCOPE_STATES,
    UNSUPPORTED_TEXAS_CITIES, LEGAL_RELIANCE_KEYWORDS,
    GUARDRAIL_RESPONSES, SUPPORTED_CITIES
)
from typing import Dict, List, Optional

class QASystem:
    def __init__(self):
        self.vector_store = RegulationVectorStore()
        self.db = RegulationDB()
    
    def answer_question_with_context(self, question: str, chat_history: List[Dict] = None) -> Dict:
        """Answer question with conversation context for follow-up questions - ENHANCED GUARDRAILS"""
        # 1. Validate question quality first (nonsense detection)
        validation = self._validate_question(question)
        if not validation['is_valid']:
            return {
                "answer": validation['message'],
                "sources": [],
                "confidence": "low",
                "has_information": False
            }
        
        # 2. Check for inappropriate content
        if self._check_inappropriate_content(question):
            return {
                "answer": GUARDRAIL_RESPONSES["inappropriate"],
                "sources": [],
                "confidence": "low",
                "has_information": False
            }
        
        # 3. Check if question is relevant to housing/leasing/regulations
        relevance_check = self._check_relevance(question)
        if not relevance_check['is_relevant']:
            return {
                "answer": relevance_check['message'],
                "sources": [],
                "confidence": "low",
                "has_information": False
            }
        
        # 4. Check for ambiguous questions
        if self._check_ambiguous(question):
            return {
                "answer": GUARDRAIL_RESPONSES["ambiguous"],
                "sources": [],
                "confidence": "low",
                "has_information": False
            }
        
        # 5. Handle greetings specially (before answering)
        if validation.get('message') == "greeting":
            return {
                "answer": "Hello! 👋 I'm your IP Agent, an AI assistant specialized in Texas housing regulations. I can help you with:\n\n• Questions about housing laws and regulations\n• ESA (Emotional Support Animal) requirements\n• Rent control and tenant rights\n• Compliance checking for lease documents\n• City-specific regulations for Dallas, Houston, Austin, and San Antonio\n\nWhat would you like to know?",
                "sources": [],
                "confidence": "high",
                "has_information": False
            }
        
        # 6. Check for legal reliance - flag it for disclaimer in answer
        has_legal_reliance = self._check_legal_reliance(question)
        
        # 6.5. Check for legal advice requests - return disclaimer message immediately
        legal_advice_keywords = ["legal advice", "legal counsel", "should i", "can i legally", "is it legal", 
                                 "is this legal", "legal opinion", "what should i do", "what can i do",
                                 "legal guidance", "legal help", "consult a lawyer", "need legal"]
        is_legal_advice_request = any(keyword in question.lower() for keyword in legal_advice_keywords)
        
        # If legal advice is requested, return disclaimer immediately
        if is_legal_advice_request:
            return {
                "answer": GUARDRAIL_RESPONSES["legal_advice"],
                "sources": [],
                "confidence": "low",
                "has_information": False
            }
        
        # 7. Build context from recent chat history for follow-up questions (BEFORE calling answer_question)
        context = ""
        question_lower = question.lower()
        is_followup = any(word in question_lower for word in ["it", "that", "this", "also", "and", "what about", "how about"])
        
        # Only build context if it's clearly a follow-up question and we have chat history
        if is_followup and chat_history and len(chat_history) > 2:
            # Get last 2 exchanges for context
            recent_messages = chat_history[-4:] if len(chat_history) > 4 else chat_history
            for msg in recent_messages[:-1]:  # Exclude current question
                if msg['role'] == 'user':
                    context += f"Previous question: {msg['content']}\n"
                elif msg['role'] == 'assistant':
                    context += f"Previous answer: {msg['content'][:150]}...\n"
        
        # 8. Enhance question with context if available (for follow-up questions)
        enhanced_question = question
        if is_followup and context:
            enhanced_question = f"{context}\n\nCurrent question: {question}"
        
        # 9. Answer the question (with context if it's a follow-up)
        result = self.answer_question(enhanced_question, city=None)
        
        # 10. Add legal disclaimer if needed (only for legal reliance, not advice requests - those are handled above)
        if has_legal_reliance and result.get('has_information'):
            result['answer'] = result['answer'] + "\n\n**⚠️ Important Disclaimer:** This information is provided for informational purposes only and does not constitute legal advice. Use at your own discretion and consult with a qualified legal advisor to ensure alignment with current policies and regulations."
        
        return result
    
    def _validate_question(self, question: str) -> Dict:
        """Validate if question is meaningful and not rubbish"""
        question_lower = question.lower().strip()
        
        # Handle greetings and casual messages
        greetings = ["hi", "hey", "hello", "whats up", "what's up", "howdy"]
        if question_lower in greetings or any(greeting in question_lower for greeting in greetings):
            return {
                "is_valid": True,  # Allow greetings but handle them specially
                "message": "greeting"
            }
        
        # Single character or too short
        if len(question.strip()) <= 1:
            return {
                "is_valid": False,
                "message": "Please type your question again."
            }
        
        # Check for gibberish - improved detection
        # Count ratio of consonants to vowels and check for meaningless character sequences
        import re
        words = question.split()
        
        # Check if all words are gibberish (no meaningful English words)
        meaningful_word_count = 0
        gibberish_score = 0
        
        for word in words:
            word_clean = re.sub(r'[^a-z]', '', word.lower())
            if len(word_clean) > 1:
                # Check if word looks like English (has vowels and consonants)
                vowels = len(re.findall(r'[aeiou]', word_clean))
                consonants = len(re.findall(r'[bcdfghjklmnpqrstvwxyz]', word_clean))
                
                if vowels > 0 and consonants > 0:
                    # Check for common English letter patterns
                    common_patterns = ['th', 'he', 'in', 'er', 'an', 're', 'ed', 'nd', 'on', 'en', 'at', 'ou', 'it', 'is', 'or', 'ti', 'as', 'to']
                    has_pattern = any(pattern in word_clean for pattern in common_patterns)
                    
                    # Check if word length is reasonable
                    if 2 <= len(word_clean) <= 15:
                        if has_pattern or (vowels >= 1 and consonants >= 1):
                            meaningful_word_count += 1
                            continue
                
                # Word doesn't look like English
                gibberish_score += 1
        
        # If most words are gibberish or no meaningful words found
        total_words = len([w for w in words if len(re.sub(r'[^a-z]', '', w.lower())) > 1])
        if total_words > 0:
            gibberish_ratio = gibberish_score / total_words
            if gibberish_ratio > 0.7 or meaningful_word_count == 0:
                return {
                    "is_valid": False,
                    "message": GUARDRAIL_RESPONSES["nonsense"]
                }
        
        return {"is_valid": True, "message": ""}
    
    def _check_relevance(self, question: str) -> Dict:
        """Check if question is within allowed scope - ENHANCED guardrails"""
        question_lower = question.lower()
        
        # 1. Check for irrelevant topics (weather, cooking, sports, etc.)
        for irrelevant_topic in IRRELEVANT_TOPICS:
            if irrelevant_topic in question_lower:
                return {
                    "is_relevant": False,
                    "message": GUARDRAIL_RESPONSES["irrelevant"]
                }
        
        # 2. Check for out-of-scope states
        for state in OUT_OF_SCOPE_STATES:
            # Check if state is mentioned with housing-related context
            if state in question_lower:
                # Check if it's actually about housing/regulations
                housing_keywords = ["housing", "regulation", "law", "rent", "lease", "tenant", "landlord", "property"]
                if any(keyword in question_lower for keyword in housing_keywords):
                    return {
                        "is_relevant": False,
                        "message": GUARDRAIL_RESPONSES["out_of_scope_geography"]
                    }
        
        # 3. Check for unsupported Texas cities - STRICT: Only 4 cities supported
        for city in UNSUPPORTED_TEXAS_CITIES:
            if city in question_lower:
                housing_keywords = ["housing", "regulation", "law", "rent", "lease", "tenant", "landlord", "property"]
                if any(keyword in question_lower for keyword in housing_keywords):
                    return {
                        "is_relevant": False,
                        "message": GUARDRAIL_RESPONSES["out_of_scope_geography"]
                    }
        
        # 3.5. Check for any other Texas cities not in the supported list
        texas_city_patterns = ["fort worth", "el paso", "arlington", "corpus christi", "plano", "laredo", 
                               "lubbock", "garland", "irving", "amarillo", "grand prairie", "brownsville",
                               "mckinney", "frisco", "pasadena", "killeen", "mesquite", "mcallen",
                               "carrollton", "midland", "denton", "abilene", "round rock", "odessa",
                               "waco", "beaumont", "richardson", "lewisville", "tyler", "pearland"]
        for city_pattern in texas_city_patterns:
            if city_pattern in question_lower:
                housing_keywords = ["housing", "regulation", "law", "rent", "lease", "tenant", "landlord", "property"]
                if any(keyword in question_lower for keyword in housing_keywords):
                    return {
                        "is_relevant": False,
                        "message": GUARDRAIL_RESPONSES["out_of_scope_geography"]
                    }
        
        # 4. Check if question contains allowed topics
        has_allowed_topic = any(topic in question_lower for topic in ALLOWED_TOPICS)
        
        # 5. Allow greetings
        greetings = ["hi", "hey", "hello", "whats up", "what's up", "howdy", "greetings"]
        is_greeting = any(greeting in question_lower for greeting in greetings) and len(question.split()) <= 3
        
        if has_allowed_topic or is_greeting:
            return {"is_relevant": True, "message": ""}
        
        # Question is OUT OF SCOPE
        return {
            "is_relevant": False,
            "message": GUARDRAIL_RESPONSES["irrelevant"]
        }
    
    def _check_legal_reliance(self, question: str) -> bool:
        """Check if user's question indicates they plan to rely on the advice legally"""
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in LEGAL_RELIANCE_KEYWORDS)
    
    def _check_ambiguous(self, question: str) -> bool:
        """Check if question is too vague or ambiguous"""
        question_lower = question.lower().strip()
        
        # Very short questions that aren't greetings
        if len(question.split()) <= 2 and not any(g in question_lower for g in ["hi", "hey", "hello", "what", "who", "when", "where", "why", "how"]):
            return True
        
        # Questions with only vague words
        vague_patterns = [
            "tell me about", "explain", "what about", "how about",
            "information", "help", "question", "advice"
        ]
        
        # If question is only vague words without specific topic
        has_vague = any(pattern in question_lower for pattern in vague_patterns)
        has_specific_topic = any(topic in question_lower for topic in ALLOWED_TOPICS)
        
        if has_vague and not has_specific_topic and len(question.split()) <= 4:
            return True
        
        return False
    
    def _check_inappropriate_content(self, question: str) -> bool:
        """Check for inappropriate, offensive, or harmful content"""
        question_lower = question.lower()
        
        # Basic inappropriate content detection
        inappropriate_patterns = [
            # Add patterns if needed - be careful with false positives
        ]
        
        # Check for excessive profanity or offensive language
        # This is a basic check - more sophisticated filtering can be added
        return False  # Placeholder - enhance as needed
    
    def answer_question(self, question: str, city: str = None) -> Dict:
        """Answer a question using RAG from regulations"""
        
        # Check if question is outside Texas scope (only if explicitly asking about another state)
        question_lower = question.lower()
        
        # Skip scope check for casual greetings or very short questions
        if len(question.split()) <= 3 and any(word in question_lower for word in ["hey", "hi", "hello", "whats", "what's", "up", "how"]):
            # Allow casual greetings to proceed
            pass
        else:
            # Only check for out-of-scope if question explicitly mentions another state
            out_of_scope_patterns = [
                r"\b(california|cali|new york|florida|illinois|pennsylvania|ohio|georgia|north carolina|michigan|new jersey|virginia|washington|arizona|massachusetts|tennessee|indiana|missouri|maryland|wisconsin|colorado|minnesota|south carolina|alabama|louisiana|kentucky|oregon|oklahoma|connecticut|utah|nevada|iowa|arkansas|mississippi|kansas|new mexico|nebraska|west virginia|idaho|hawaii|new hampshire|maine|montana|rhode island|delaware|south dakota|north dakota|alaska|vermont|wyoming|dc|district of columbia)\b.*(housing|regulation|law|rent|lease|tenant|landlord|property)",
                r"\b(housing|regulation|law|rent|lease|tenant|landlord|property).*(california|cali|new york|florida|illinois|pennsylvania|ohio|georgia|north carolina|michigan|new jersey|virginia|washington|arizona|massachusetts|tennessee|indiana|missouri|maryland|wisconsin|colorado|minnesota|south carolina|alabama|louisiana|kentucky|oregon|oklahoma|connecticut|utah|nevada|iowa|arkansas|mississippi|kansas|new mexico|nebraska|west virginia|idaho|hawaii|new hampshire|maine|montana|rhode island|delaware|south dakota|north dakota|alaska|vermont|wyoming|dc|district of columbia)\b"
            ]
            
            import re
            for pattern in out_of_scope_patterns:
                if re.search(pattern, question_lower):
                    match = re.search(pattern, question_lower)
                    state = match.group(1) if match.group(1) else match.group(2)
                    return {
                        "answer": GUARDRAIL_RESPONSES["out_of_scope_geography"],
                        "sources": [],
                        "confidence": "low",
                        "has_information": False
                    }
        
        # Extract city from question if mentioned
        detected_city = None
        
        city_keywords = {
            "Dallas": ["dallas"],
            "Houston": ["houston"],
            "Austin": ["austin"],
            "San Antonio": ["san antonio", "san antonio"],
            "Texas-Statewide": ["texas", "statewide", "state-wide"]
        }
        
        # Check for unsupported cities in Texas
        unsupported_texas_cities = ["fort worth", "el paso", "arlington", "corpus christi", "plano", "laredo", "lubbock", "garland", "irving", "amarillo", "grand prairie", "brownsville", "mckinney", "frisco", "pasadena", "killeen", "mesquite", "mcallen", "carrollton", "midland", "denton", "abilene", "round rock", "odessa", "waco", "beaumont", "richardson", "lewisville", "tyler", "pearland"]
        
        for unsupported_city in unsupported_texas_cities:
            if unsupported_city in question_lower:
                return {
                    "answer": GUARDRAIL_RESPONSES["out_of_scope_geography"],
                    "sources": [],
                    "confidence": "low",
                    "has_information": False
                }
        
        for city_name, keywords in city_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                detected_city = city_name
                break
        
        # Use detected city or provided city
        final_city = detected_city or city or "Texas-Statewide"
        
        # Enhance query with city context only if city is relevant
        enhanced_query = question
        if final_city and final_city != "Texas-Statewide":
            enhanced_query = f"{question} for {final_city}, Texas"
        
        # Handle multi-term explanation questions (e.g., "Explain these leasing terms: HUD, DOJ, ESA, rent control, zoning")
        question_lower = question.lower()
        if "explain these" in question_lower or ("explain" in question_lower and "terms" in question_lower and ":" in question):
            # Extract terms from the question
            terms_to_explain = []
            if ":" in question:
                after_colon = question.split(":")[-1].strip()
                terms_to_explain = [t.strip() for t in after_colon.split(",")]
            
            if terms_to_explain:
                # Search for all terms together first
                enhanced_query = question
                search_results = self.vector_store.search(
                    query=enhanced_query,
                    n_results=7,
                    context={"city": final_city},
                    prioritize_reliable=True,
                    filter_geography=final_city if final_city != "Texas-Statewide" else None
                )
                
                # Build structured answer using LLM if available, otherwise use context
                if search_results:
                    # Use LLM to generate structured answer
                    context_parts = []
                    sources = []
                    seen_urls = set()
                    
                    for result in search_results:
                        doc_text = result['document']
                        metadata = result['metadata']
                        source_name = metadata.get('source_name', 'Unknown')
                        url = metadata.get('url', '')
                        
                        if url in seen_urls:
                            continue
                        seen_urls.add(url)
                        
                        # Clean text - remove URLs
                        import re
                        clean_text = re.sub(r'https?://[^\s\)]+', '', doc_text)
                        clean_text = clean_text[:500]  # Limit length
                        
                        context_parts.append(f"Source: {source_name}\n{clean_text}")
                        sources.append({
                            "source": source_name,
                            "url": url,
                            "category": metadata.get('category', 'Unknown')
                        })
                    
                    full_context = "\n\n---\n\n".join(context_parts[:5])
                    
                    # Generate answer using LLM
                    import os
                    from dotenv import load_dotenv
                    load_dotenv()
                    current_api_key = os.getenv("OPENAI_API_KEY", "") or OPENAI_API_KEY
                    
                    if current_api_key and current_api_key != "your_openai_api_key_here" and len(current_api_key) >= 20:
                        try:
                            answer = self._generate_llm_answer(question, full_context, final_city)
                            return {
                                "answer": answer,
                                "sources": sources,
                                "confidence": "high",
                                "has_information": True
                            }
                        except:
                            pass
        
        # REMOVED: Basic definition questions - NO OUTSIDE KNOWLEDGE
        # All answers must come from scraped text only
        
        # KEYWORD-STRICT FILTERING: If user asks about "HUD", ONLY retrieve HUD-related chunks
        question_lower = question.lower()
        
        # Detect key terms for strict filtering with synonym matching
        key_terms = {
            "hud": ["hud", "housing and urban development", "department of housing", "fair housing act", "federal housing"],
            "doj": ["doj", "department of justice", "justice department"],
            "esa": ["esa", "emotional support animal", "emotional support", "assistance animal", "assistance animal notice"],
            "rent control": ["rent control", "rent cap", "rent limit", "rent stabilization", "tenant protections"],
            "zoning": ["zoning", "zoning law", "zoning ordinance"],
            "section 8": ["section 8", "hcv", "housing choice voucher", "voucher"],
            "disability": ["disability", "reasonable accommodation"],
            "pets": ["pets", "assistance animal", "assistance animal notice"],
            "leasing manager": ["leasing manager", "leasing agent", "property manager duties"]
        }
        
        # Source match rules: semantic matching for synonyms
        synonym_mapping = {
            "esa": ["assistance animal", "emotional support animal", "assistance animal notice"],
            "hud": ["fair housing act", "federal housing", "housing and urban development"],
            "voucher": ["section 8", "hcv", "housing choice voucher"],
            "disability": ["reasonable accommodation"],
            "pets": ["assistance animal notice", "assistance animal"],
            "rent cap": ["rent stabilization", "tenant protections", "rent control"]
        }
        
        # Determine which key term is being asked about
        detected_key_term = None
        for term, keywords in key_terms.items():
            if any(kw in question_lower for kw in keywords):
                detected_key_term = term
                break
        
        # Search with keyword-strict filtering and synonym expansion
        if detected_key_term:
            # Use the key term directly in query for strict matching
            strict_query = f"{detected_key_term} {question}"
            # Also add synonyms for semantic matching
            if detected_key_term in synonym_mapping:
                synonyms = synonym_mapping[detected_key_term]
                strict_query = f"{strict_query} {' '.join(synonyms)}"
        else:
            strict_query = enhanced_query
        
        # Increase results for ESA/HUD to ensure we find relevant content
        n_search_results = 30 if detected_key_term in ["esa", "hud"] else 20
        
        search_results = self.vector_store.search(
            query=strict_query,
            n_results=n_search_results,  # Get more results for keyword filtering
            context={"city": final_city},
            prioritize_reliable=True,
            filter_geography=final_city if final_city != "Texas-Statewide" else None
        )
        
        # KEYWORD-STRICT FILTERING: Filter results to only include chunks that actually mention the key term or its synonyms
        if detected_key_term:
            filtered_results = []
            key_term_keywords = key_terms[detected_key_term]
            # Also include synonyms for semantic matching
            if detected_key_term in synonym_mapping:
                key_term_keywords = key_term_keywords + synonym_mapping[detected_key_term]
            
            for result in search_results:
                doc_lower = result['document'].lower()
                # Only include if document actually mentions the key term or its synonyms
                if any(kw in doc_lower for kw in key_term_keywords):
                    # For ESA questions, prioritize chunks that actually define ESA, not just mention it
                    if detected_key_term == "esa":
                        # Prioritize chunks that contain definition keywords
                        definition_keywords = ["emotional support animal", "esa is", "esa refers", "definition", "means", "is an animal", "provides comfort", "assistance animal"]
                        has_definition = any(dk in doc_lower for dk in definition_keywords)
                        if has_definition:
                            # Boost priority for definition chunks
                            filtered_results.insert(0, result)
                        else:
                            filtered_results.append(result)
                    else:
                        filtered_results.append(result)
            search_results = filtered_results[:15]  # Increased to allow more sources
        
        # FALLBACK SCRAPING: If no results or poor results, try alternative links with same category
        if not search_results or len(search_results) < 3:
            # Try to find alternative regulations with the same category
            category_match = None
            for term, keywords in key_terms.items():
                if any(kw in question_lower for kw in keywords):
                    # Try to match category from detected key term
                    category_map = {
                        "esa": ["ESA", "Fair Housing"],
                        "hud": ["Fair Housing", "Federal"],
                        "doj": ["Fair Housing", "Federal"],
                        "rent control": ["Rent Caps", "Rent Control"],
                        "zoning": ["Zoning"],
                        "section 8": ["Housing Programs", "Section 8"]
                    }
                    category_match = category_map.get(term, [])
                    break
            
            if category_match:
                # Get all regulations with matching category
                all_regulations = self.db.get_all_regulations()
                alternative_regs = [r for r in all_regulations 
                                   if any(cat.lower() in r.get('category', '').lower() for cat in category_match)]
                
                # Try scraping alternative links
                scraper = RegulationScraper()
                
                for alt_reg in alternative_regs[:5]:  # Try up to 5 alternatives
                    url = alt_reg.get('url', '')
                    if url and url.startswith(('http://', 'https://')):
                        try:
                            content = scraper.fetch_url_content(url)
                            if content and content.get('content') and len(content['content']) > 500:
                                # Create a synthetic search result from scraped content
                                chunks = scraper.chunk_text(content['content'])
                                if chunks:
                                    # Add first few chunks as search results
                                    for chunk in chunks[:3]:
                                        search_results.append({
                                            'document': chunk,
                                            'metadata': {
                                                'source_name': alt_reg.get('source_name', 'Unknown'),
                                                'url': url,
                                                'category': alt_reg.get('category', 'Unknown')
                                            },
                                            'distance': 0.8  # Lower similarity score
                                        })
                                    if len(search_results) >= 5:
                                        break
                        except:
                            continue
        
        if not search_results:
            # Return standard missing message
            return {
                "answer": GUARDRAIL_RESPONSES["missing_information"],
                "sources": [],
                "confidence": "low",
                "has_information": False
            }
        
        # Extract relevant context with STRICT filtering - only legal rules, definitions, policy content
        context_parts = []
        sources = []
        seen_urls = set()
        
        # Keywords that indicate irrelevant content (news, unrelated topics, navigation)
        irrelevant_keywords = [
            "trooper", "game", "players", "university", "student", "detention", 
            "immigration", "motorcyclist", "crash", "backhoe", "abandoned", "dit",
            "sports", "football", "basketball", "arrest", "police", "crime",
            "skip to", "menu", "search", "view all", "back to top", "navigation",
            "federal register", "govinfo", "gpo", "administrative committee", "code of federal regulations",
            "congressional", "sitemap", "developer hub", "bulk data", "api", "feeds"
        ]
        
        # URLs that indicate general government navigation sites (not specific content)
        irrelevant_url_patterns = [
            "federalregister.gov", "govinfo.gov", "gpo.gov", 
            "congress.gov", "uscode.house.gov"
        ]
        
        # Legal content keywords - only keep chunks with these
        legal_keywords = [
            "regulation", "law", "ordinance", "code", "statute", "rule", "requirement",
            "housing", "rent", "lease", "tenant", "landlord", "property",
            "fair housing", "esa", "zoning", "compliance", "right", "require", 
            "prohibit", "allow", "must", "shall", "may", "definition", "means",
            "refers to", "is defined", "policy", "procedure"
        ]
        
        # Process ALL search results to collect multiple sources
        # Allow multiple chunks from same source, but track unique sources for citation
        for result in search_results:
            doc_text = result['document']
            metadata = result['metadata']
            source_name = metadata.get('source_name', 'Unknown')
            url = metadata.get('url', '')
            
            # Allow multiple chunks from same source (don't skip duplicates)
            # We want comprehensive context from all relevant chunks
            # Track unique sources for citation separately
            
            # STRICT FILTERING: Only keep legal rules, definitions, and policy content
            doc_lower = doc_text.lower()
            
            # Filter out general government navigation sites
            if any(pattern in url.lower() for pattern in irrelevant_url_patterns):
                # Only keep if it's clearly about housing/HUD/ESA and not just navigation
                if not any(term in doc_lower for term in ["housing", "hud", "fair housing", "esa", "emotional support", "assistance animal", "tenant", "landlord", "lease", "rent"]):
                    continue
            
            # For HUD questions, prioritize HUD-specific sources
            if detected_key_term == "hud" and "what is" in question_lower:
                # Skip if URL is not HUD-related
                if "hud.gov" not in url.lower() and "housing and urban development" not in doc_lower:
                    # Only keep if it clearly defines HUD
                    if not any(term in doc_lower for term in ["housing and urban development", "hud", "department of housing"]):
                        continue
            
            # For ESA questions, filter out general fair housing content that doesn't define ESA
            if detected_key_term == "esa" and "what is" in question_lower:
                # Skip chunks that are about fair housing in general but don't define ESA
                if ("fair housing" in doc_lower or "discriminatory housing" in doc_lower) and not any(term in doc_lower for term in ["emotional support animal", "esa", "assistance animal", "service animal"]):
                    continue
                # Must contain ESA-related terms
                if not any(term in doc_lower for term in ["emotional support animal", "esa", "assistance animal", "assistance animal notice"]):
                    continue
            
            # Skip if contains irrelevant keywords (unless it's clearly about regulations)
            if any(keyword in doc_lower for keyword in irrelevant_keywords):
                # Only keep if it also contains legal keywords
                if not any(keyword in doc_lower for keyword in legal_keywords):
                    continue  # Skip - it's not about regulations
            
            # Must contain legal keywords to be relevant
            if not any(keyword in doc_lower for keyword in legal_keywords):
                continue  # Skip - not legal/regulation content
            
            # Filter by city if specified
            if final_city and final_city != "Texas-Statewide":
                city_lower = final_city.lower()
                # Must mention city, Texas, or be a general regulation
                if city_lower not in doc_lower and "texas" not in doc_lower and "state" not in doc_lower:
                    # Skip if it's clearly about a different city
                    if any(other_city in doc_lower for other_city in ["austin", "houston", "san antonio", "dallas"]):
                        if city_lower not in doc_lower:
                            continue  # Skip - it's about a different city
            
            # Clean up the text - remove very short or fragmented content
            if len(doc_text.strip()) < 50:
                continue
            
            # Extract meaningful sentences only - legal rules, definitions, policy
            sentences = doc_text.split('.')
            relevant_sentences = []
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20:  # Only meaningful sentences
                    sentence_lower = sentence.lower()
                    # Must contain legal keywords
                    if any(keyword in sentence_lower for keyword in legal_keywords):
                        # Remove navigation/menu text and government site navigation
                        skip_patterns = ['skip to', 'menu', 'search', 'view all', 'back to top', 
                                        'federal register', 'govinfo', 'gpo', 'developer hub', 
                                        'bulk data', 'sitemap', 'congressional', 'code of federal regulations',
                                        'administrative committee', 'unofficial informational resource']
                        if not any(skip in sentence_lower for skip in skip_patterns):
                            # For ESA/HUD questions, prioritize definition sentences
                            if detected_key_term in ["esa", "hud"] and "what is" in question_lower:
                                definition_indicators = ["is", "refers to", "means", "defined as", "definition"]
                                if any(indicator in sentence_lower for indicator in definition_indicators):
                                    relevant_sentences.insert(0, sentence)  # Prioritize definition sentences
                                else:
                                    relevant_sentences.append(sentence)
                            else:
                                relevant_sentences.append(sentence)
            
            if not relevant_sentences:
                continue  # Skip if no relevant sentences found
            
            clean_text = '. '.join(relevant_sentences[:5])  # Take first 5 relevant sentences
            if len(clean_text) < 100:
                continue  # Skip if too short
            
            # Add context - clean text only, no source names in text
            context_parts.append(clean_text)
            
            # Add ALL unique sources (don't limit to one source per URL)
            # This allows multiple chunks from same source to contribute
            # For ESA questions, prioritize ESA-specific sources
            if url not in seen_urls:
                # For ESA questions, check if source is ESA-specific
                if detected_key_term == "esa" and "what is" in question_lower:
                    source_lower = source_name.lower()
                    url_lower = url.lower()
                    # Prioritize ESA-specific sources
                    is_esa_source = any(term in source_lower or term in url_lower for term in ["esa", "emotional support", "assistance animal", "assistance_animals", "hud.gov/assistance"])
                    if is_esa_source:
                        # Add ESA sources first (at the beginning)
                        sources.insert(0, {
                            "source": source_name,
                            "url": url,
                            "category": metadata.get('category', 'Unknown')
                        })
                    else:
                        sources.append({
                            "source": source_name,
                            "url": url,
                            "category": metadata.get('category', 'Unknown')
                        })
                # For HUD questions, prioritize HUD-specific sources
                elif detected_key_term == "hud" and "what is" in question_lower:
                    source_lower = source_name.lower()
                    url_lower = url.lower()
                    # Prioritize HUD-specific sources (hud.gov)
                    is_hud_source = "hud.gov" in url_lower or "housing and urban development" in source_lower
                    if is_hud_source:
                        # Add HUD sources first (at the beginning)
                        sources.insert(0, {
                            "source": source_name,
                            "url": url,
                            "category": metadata.get('category', 'Unknown')
                        })
                    else:
                        sources.append({
                            "source": source_name,
                            "url": url,
                            "category": metadata.get('category', 'Unknown')
                        })
                else:
                    sources.append({
                        "source": source_name,
                        "url": url,
                        "category": metadata.get('category', 'Unknown')
                    })
                seen_urls.add(url)
        
        if not context_parts:
            # Return standard missing message
            return {
                "answer": GUARDRAIL_RESPONSES["missing_information"],
                "sources": [],
                "confidence": "low",
                "has_information": False
            }
        
        # Combine context - clean chunks only (allow more sources for comprehensive answers)
        full_context = "\n\n---\n\n".join(context_parts[:10])  # Increased to allow more sources (up to 10 chunks)
        
        # Check for "new law" or "recent update" questions
        if any(keyword in question_lower for keyword in ["new law", "new regulation", "recent law", "recent update", "latest law", "latest update", "what is new", "what's new"]):
            # Check for recent updates in database
            recent_updates = self.db.get_recent_updates(limit=10)
            if recent_updates:
                update_context = "\n\n=== RECENT UPDATES (NEW LAWS) ===\n"
                updates_added = False
                for update in recent_updates:
                    affected_cities_str = str(update.get('affected_cities', '')).lower()
                    update_city = final_city.lower() if final_city else ""
                    
                    # Match if city matches or it's a general update
                    if (final_city == "Texas-Statewide" or 
                        update_city in affected_cities_str or 
                        ("dallas" in update_city and "dallas" in affected_cities_str) or
                        ("austin" in update_city and "austin" in affected_cities_str) or
                        ("houston" in update_city and "houston" in affected_cities_str) or
                        ("san antonio" in update_city and "san antonio" in affected_cities_str)):
                        
                        update_url = update.get('url', '')
                        update_summary = update.get('update_summary', '')
                        # Clean update summary - remove formatting artifacts
                        import re
                        # Fix character-by-character spacing issues - join single characters that form words
                        # Pattern: single letter followed by space, repeated (like "2 5 0" should become "250")
                        update_summary = re.sub(r'(\d+)\s+(\d+)', r'\1\2', update_summary)  # Fix numbers
                        update_summary = re.sub(r'\s+', ' ', update_summary)  # Normalize all spaces
                        update_summary = update_summary.strip()
                        update_context += f"\n{update.get('source_name', 'Unknown')}\n"
                        update_context += f"Summary: {update_summary}\n"
                        update_context += f"URL: {update_url}\n"
                        
                        # Add to sources (avoid duplicates)
                        if not any(s.get('url') == update_url for s in sources):
                            sources.append({
                                "source": f"{update.get('source_name', 'Unknown')} (NEW UPDATE)",
                                "url": update_url,
                                "category": update.get('category', 'Update')
                            })
                        updates_added = True
                
                if updates_added:
                    # Clean update context - remove formatting artifacts and ensure proper text
                    clean_update_context = update_context.replace("===", "").strip()
                    # Remove any character-by-character artifacts
                    import re
                    # Fix any spacing issues in update summaries
                    clean_update_context = re.sub(r'\s+', ' ', clean_update_context)
                    clean_update_context = re.sub(r'\n\s*\n', '\n\n', clean_update_context)
                    full_context = clean_update_context + "\n\n=== REGULATION DATABASE ===\n" + full_context
        
        # Generate answer using LLM if available, otherwise use context extraction
        # Reload API key to get latest value
        import os
        from dotenv import load_dotenv
        load_dotenv()
        current_api_key = os.getenv("OPENAI_API_KEY", "") or OPENAI_API_KEY
        
        if current_api_key and current_api_key != "your_openai_api_key_here" and len(current_api_key) >= 20:
            try:
                answer = self._generate_llm_answer(question, full_context, final_city)
            except Exception as e:
                # Fall back to free mode if API fails
                answer = self._extract_answer_from_context(question, full_context, final_city)
        else:
            # Free mode: extract relevant snippets
            answer = self._extract_answer_from_context(question, full_context, final_city)
        
        # Format sources - Source names only (no URLs)
        # Format: List of source names for display as "Sources: Name 1; Name 2"
        formatted_sources = []
        seen_names = set()
        for source in sources:
            # Get source name only - no URLs
            source_name = source.get('source', source.get('source_name', 'Unknown Source'))
            if source_name and source_name not in seen_names:
                seen_names.add(source_name)
                formatted_sources.append({
                    "source": source_name,
                    "source_name": source_name,
                    "url": source.get('url', ''),  # Keep URL internally but don't display
                    "category": source.get('category', 'Unknown')
                })
        
        # Check if answer is missing - return fallback message
        if not answer or len(answer.strip()) < 20:
            return {
                "answer": GUARDRAIL_RESPONSES["missing_information"],
                "sources": [],
                "confidence": "low",
                "has_information": False
            }
        
        return {
            "answer": answer,
            "sources": formatted_sources,
            "confidence": "high" if len(formatted_sources) > 0 else "low",
            "has_information": True
        }
    
    def _generate_llm_answer(self, question: str, context: str, city: str) -> str:
        """Generate answer using OpenAI LLM - STRICT RULES: 4-6 lines, plain English, no outside knowledge"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            # Clean context - remove URLs, source text, navigation menus
            import re
            clean_context = context
            # Remove URL patterns completely
            clean_context = re.sub(r'https?://[^\s\)]+', '', clean_context)
            clean_context = re.sub(r'\(https?://[^\)]+\)', '', clean_context)
            # Remove navigation and menu text
            clean_context = re.sub(r'Skip to [^\n]+', '', clean_context, flags=re.IGNORECASE)
            clean_context = re.sub(r'Back to top[^\n]*', '', clean_context, flags=re.IGNORECASE)
            clean_context = re.sub(r'Menu[^\n]*', '', clean_context, flags=re.IGNORECASE)
            clean_context = re.sub(r'Search[^\n]*', '', clean_context, flags=re.IGNORECASE)
            clean_context = re.sub(r'View all[^\n]*', '', clean_context, flags=re.IGNORECASE)
            clean_context = re.sub(r'Landlord/Tenant Law[^\n]*', '', clean_context, flags=re.IGNORECASE)
            # Remove update formatting markers
            clean_context = re.sub(r'=== RECENT UPDATES[^=]*===', '', clean_context, flags=re.IGNORECASE)
            clean_context = re.sub(r'=== REGULATION DATABASE[^=]*===', '', clean_context, flags=re.IGNORECASE)
            # Fix character-by-character spacing issues (remove single character lines)
            lines = clean_context.split('\n')
            cleaned_lines = []
            for line in lines:
                # Skip lines that are just single characters or weird spacing
                if len(line.strip()) > 1 or (line.strip() and line.strip().isalnum()):
                    cleaned_lines.append(line)
            clean_context = '\n'.join(cleaned_lines)
            # Fix excessive spacing
            clean_context = re.sub(r'\s+', ' ', clean_context)
            clean_context = re.sub(r'\n\s*\n\s*\n+', '\n\n', clean_context)
            
            # Detect key term for specific missing message
            question_lower = question.lower()
            key_term_missing_msg = GUARDRAIL_RESPONSES["missing_information"]
            
            if "hud" in question_lower and "housing and urban development" not in clean_context.lower() and "hud" not in clean_context.lower():
                key_term_missing_msg = GUARDRAIL_RESPONSES["missing_information"]
            elif "doj" in question_lower and "department of justice" not in clean_context.lower() and "doj" not in clean_context.lower():
                key_term_missing_msg = GUARDRAIL_RESPONSES["missing_information"]
            elif ("esa" in question_lower or "emotional support" in question_lower) and "emotional support" not in clean_context.lower() and "esa" not in clean_context.lower():
                key_term_missing_msg = GUARDRAIL_RESPONSES["missing_information"]
            elif "rent control" in question_lower and "rent control" not in clean_context.lower():
                key_term_missing_msg = GUARDRAIL_RESPONSES["missing_information"]
            elif "zoning" in question_lower and "zoning" not in clean_context.lower():
                key_term_missing_msg = GUARDRAIL_RESPONSES["missing_information"]
            elif ("section 8" in question_lower or "hcv" in question_lower or "housing choice voucher" in question_lower) and "section 8" not in clean_context.lower() and "hcv" not in clean_context.lower() and "housing choice voucher" not in clean_context.lower():
                key_term_missing_msg = GUARDRAIL_RESPONSES["missing_information"]
            elif ("leasing manager" in question_lower or "leasing agent" in question_lower) and "leasing manager" not in clean_context.lower() and "leasing agent" not in clean_context.lower():
                key_term_missing_msg = GUARDRAIL_RESPONSES["missing_information"]
            
            # Extract the question term for "What is X?" questions
            question_term = None
            import re
            if "what is" in question_lower:
                # Extract term after "what is"
                match = re.search(r'what is\s+([^?]+)', question_lower)
                if match:
                    question_term = match.group(1).strip()
                    # Clean up the term (remove articles, extra words)
                    question_term = re.sub(r'^(a|an|the)\s+', '', question_term)
                    # Take first meaningful word/phrase (up to 3 words for compound terms)
                    words = question_term.split()
                    if len(words) > 3:
                        question_term = ' '.join(words[:3])
                    question_term = question_term.strip('?.,!').strip()
            
            # Build answer start instruction based on question term
            answer_start_instruction = ""
            if question_term:
                # Capitalize first letter
                question_term_capitalized = question_term[0].upper() + question_term[1:] if len(question_term) > 1 else question_term.upper()
                answer_start_instruction = f"- CRITICAL: Your answer MUST start with \"{question_term_capitalized} is\" or \"{question_term_capitalized} refers to\" or similar direct answer format. For example, if the question is \"What is ESA?\", start with \"ESA is\" followed by the definition."
            
            prompt = f"""You are a Leasing Compliance Answer Assistant. You ONLY answer questions about HOUSING and LEASING compliance rules and policies in Dallas, Austin, Houston, and San Antonio, Texas.

DATA POLICY (STRICT MODE):
- You MUST cite at least one verifiable source from the provided Data Source (Excel hyperlinks and scraped text).
- If NO MATCHING SOURCE is found: respond with EXACT message: "I apologize — I do not currently have this information in my data sources. Please check back later for updates."
- NEVER use general model knowledge, speculation, assumptions, or outside content.
- NO fallback to public information or OpenAI knowledge
- NO mention of sources not present in Excel
- NO government encyclopedia content
- NO long prefaces or disclaimers outside guardrail rules

STRICT RULES (MANDATORY):
1. ONLY use information from the provided context chunks - NO outside knowledge
2. If information is NOT in the context, respond EXACTLY: "I apologize — I do not currently have this information in my data sources. Please check back later for updates."
3. DO NOT guess, hallucinate, or combine unrelated text
4. DO NOT use HUD/DOJ/ESA definitions from your own memory
5. DO NOT add "Applicable To" sections
6. DO NOT add legal disclaimers in the answer text
7. DO NOT dump menus, tags, or junk text from websites
8. DO NOT answer with general definitions not found in scraped data
9. DO NOT use prior model knowledge - ONLY scraped text
10. DO NOT copy long legal paragraphs - summarize concisely in plain language
11. DO NOT include unrelated legal analysis, news, or commentary content
12. DO NOT make policy predictions or advice outside Texas housing law
13. DO NOT include case citations unless explicitly stored in database sources
14. NO emojis, NO hashtags, NO bold formatting

MANDATORY RESPONSE FORMAT (STRICT - Follow exactly):

[ANSWER]

Short, clear explanation in paragraphs using ONLY verified source content. Maximum 4-6 sentences. Be direct and factual. Use proper punctuation and complete sentences. Do NOT use bullet lists. Do NOT include sources or URLs in the answer text.

[SOURCES]

- Name: hyperlink

(Each source on a new line with format: - Source Name: https://url)

CONCISENESS REQUIREMENTS:
- Maximum 4-6 sentences total
- Each sentence should be clear and complete with proper punctuation
- Remove unnecessary words and filler
- Focus on the core answer to the question
- Be direct and factual

Do NOT include:
- Bullet lists or numbered lists in the answer
- Long legal paragraphs copied verbatim
- URLs in the answer text
- Source citations in the answer text
- Emojis or special formatting
- Unnecessary background information

SPECIFIC TOPIC RULES:
- When answering ESA: Provide a concise definition starting with "An Emotional Support Animal (ESA) is..." (NO bold headers, NO markdown formatting). Explain key points: ESA vs service animal distinction, provides comfort and emotional support without special training, helps with anxiety/depression/PTSD. Keep it brief (4-6 sentences). Do NOT include sources or URLs in the answer text - sources will be added separately.
- When answering ESA law in a specific city: Start with the city name (e.g., "Dallas follows..." or "In Dallas, ESA laws...") and explain how federal ESA rules apply in that city. Keep it brief (4-6 sentences).
- When answering HUD: Start with "HUD is" or "HUD (Housing and Urban Development) is..." and provide a concise explanation of what HUD is and its role. Keep it brief (4-6 sentences).
- When answering Section 8: Start with "Section 8 is..." and provide a concise explanation. Keep it brief (4-6 sentences).
- When answering rent control or new laws: Start with the city name or "The new regulation in [city]..." and provide concise information about what the law does. Do NOT include raw update summaries or formatting markers. Write in natural sentences. Keep it brief (4-6 sentences).
- When answering "what is new law" questions: Start with the city name (e.g., "Dallas has enacted..." or "In Dallas, a new law...") and provide a clear, concise summary of the new regulation. Keep it brief (4-6 sentences).
- When answering landlord obligations: Start with "Under Texas law..." and provide concise information. Keep it brief (4-6 sentences).

CRITICAL ANSWER FORMAT RULES: 
{answer_start_instruction}
- ALWAYS start your answer with a complete sentence that directly answers the question using the question term (e.g., for "What is ESA?", start with "ESA is...")
- NEVER start with connecting words like "However", "But", "Also", "Additionally", "Furthermore"
- NEVER start mid-sentence or with a fragment from the middle of a paragraph
- Your first sentence must be a complete, standalone statement that answers "What is X?" using proper punctuation
- Make sure your answer is complete and ends with a proper sentence with correct punctuation
- Use proper punctuation throughout (periods, commas, etc.)
- Keep the answer concise - maximum 4-6 sentences total
- Explain terminology clearly but briefly - assume the leasing manager may not know legal jargon

Always assume audience is a leasing professional needing quick, concise compliance guidance. Write in a clear, professional, direct style with proper punctuation. Be brief and accurate.

Question: {question}
City Context: {city or 'Texas-Statewide'}

Scraped Text Chunks (ONLY use these - NO outside knowledge):
{clean_context[:5000]}

CRITICAL: If the scraped text chunks above do NOT contain information that directly answers the question, you MUST respond EXACTLY: "I apologize — I do not currently have this information in my data sources. Please check back later for updates."

SOURCE MATCH RULES:
- Perform semantic matching for synonyms:
  - ESA → "Assistance Animal"
  - HUD → "Fair Housing Act" or "Federal Housing"
  - Voucher → "Section 8"
  - Disability → "Reasonable Accommodation"
  - Pets → "Assistance Animal Notice"
  - Rent Cap → "Rent Stabilization / Tenant Protections"
- If a synonym is used but the root concept is present in data sources, USE IT.

Provide answer in the EXACT format specified above using ONLY the chunks above. Format must be:
[ANSWER]
[your answer here]

[SOURCES]
- Source Name: https://url

If information is missing, respond with the missing message above. Remember: Be concise (4-6 sentences), use proper punctuation, NO markdown formatting."""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a Leasing Compliance Answer Assistant. Provide clear, concise Texas housing law compliance guidance to leasing managers. Format: **Answer:** followed by a concise explanation in plain language (1-2 paragraphs, maximum 4-6 sentences total). No bullet lists. Only use information from provided chunks. Never use outside knowledge. Always start with the question term (e.g., 'ESA is...' for 'What is ESA?'). Use proper punctuation throughout. Make sure your answer is complete and ends with proper punctuation. If information is missing, say the missing message. Do not include URLs or source citations in the answer. Be concise and direct."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=400  # Reduced for more concise answers (4-6 sentences)
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Parse [ANSWER] and [SOURCES] sections
            if "[ANSWER]" in answer and "[SOURCES]" in answer:
                # Extract answer and sources sections
                parts = answer.split("[SOURCES]")
                if len(parts) == 2:
                    answer_part = parts[0].replace("[ANSWER]", "").strip()
                    sources_part = parts[1].strip()
                    # The sources will be handled separately, so just return the answer part
                    answer = answer_part
                else:
                    # Fallback: remove markers if format is wrong
                    answer = answer.replace("[ANSWER]", "").replace("[SOURCES]", "").strip()
            elif "[ANSWER]" in answer:
                answer = answer.replace("[ANSWER]", "").strip()
            elif "[SOURCES]" in answer:
                answer = answer.split("[SOURCES]")[0].strip()
            
            # Remove "**Answer:**" or "Answer:" prefix if present (legacy format)
            if answer.startswith("**Answer:**"):
                answer = answer.replace("**Answer:**", "", 1).strip()
            elif answer.startswith("Answer:"):
                answer = answer.replace("Answer:", "", 1).strip()
            
            # Extract question term for "What is X?" questions to ensure answer starts correctly
            question_term = None
            if "what is" in question.lower():
                match = re.search(r'what is\s+([^?]+)', question.lower())
                if match:
                    question_term = match.group(1).strip()
                    question_term = re.sub(r'^(a|an|the)\s+', '', question_term)
                    words = question_term.split()
                    if len(words) > 3:
                        question_term = ' '.join(words[:3])
                    question_term = question_term.strip('?.,!').strip()
            
            # Ensure answer doesn't start with sentence fragments (e.g., "However,")
            # Remove leading connectors and ensure it starts with a complete sentence
            if answer and len(answer) > 0:
                # Remove leading connectors (case-insensitive)
                connectors = ['however,', 'however', 'but,', 'but', 'also,', 'also', 'additionally,', 'additionally', 'furthermore,', 'furthermore']
                answer_lower = answer.lower().strip()
                for conn in connectors:
                    if answer_lower.startswith(conn):
                        # Remove the connector
                        answer = answer[len(conn):].strip()
                        # Remove any leading comma, period, or space
                        answer = re.sub(r'^[,.\s]+', '', answer)
                        # Capitalize first letter
                        if answer:
                            answer = answer[0].upper() + answer[1:] if len(answer) > 1 else answer.upper()
                        break
                
                # Check if starts with lowercase (likely a fragment from mid-sentence)
                if answer and answer[0].islower():
                    # Try to find where the first complete sentence starts
                    # Look for sentence boundaries and find first uppercase letter
                    sentences = re.split(r'([.!?]+\s+)', answer)
                    found_start = False
                    for i in range(0, len(sentences), 2):
                        if i < len(sentences):
                            sentence = sentences[i].strip()
                            # Skip empty sentences
                            if not sentence:
                                continue
                            # Look for a sentence that starts with uppercase and is meaningful (not just a single word)
                            if sentence[0].isupper() and len(sentence.split()) > 3:
                                # Found first complete sentence - use from here
                                answer = ''.join(sentences[i:]).strip()
                                found_start = True
                                break
                    
                    # If we couldn't find a proper start, just capitalize first letter
                    if not found_start and answer:
                        answer = answer[0].upper() + answer[1:] if len(answer) > 1 else answer.upper()
                
                # Ensure answer starts with question term if available
                if question_term and question_term:
                    question_term_capitalized = question_term[0].upper() + question_term[1:] if len(question_term) > 1 else question_term.upper()
                    answer_lower_start = answer.lower().strip()[:50]  # Check first 50 chars
                    # Check if answer doesn't start with the question term
                    if not answer_lower_start.startswith(question_term.lower() + ' ') and not answer_lower_start.startswith(question_term.lower() + ' is') and not answer_lower_start.startswith('an ' + question_term.lower()):
                        # Try to find where the actual answer starts
                        # Look for patterns like "X is", "X refers to", etc.
                        sentences = re.split(r'([.!?]+\s+)', answer)
                        found_start = False
                        for i in range(0, len(sentences), 2):
                            if i < len(sentences):
                                sentence = sentences[i].strip()
                                if sentence and (sentence.lower().startswith(question_term.lower() + ' ') or 
                                                sentence.lower().startswith(question_term.lower() + ' is') or
                                                sentence.lower().startswith('an ' + question_term.lower())):
                                    # Found sentence starting with question term - use from here
                                    answer = ''.join(sentences[i:]).strip()
                                    found_start = True
                                    break
                        
                        # If we couldn't find it, prepend the question term
                        if not found_start and not answer.lower().startswith(question_term.lower()):
                            # Check if answer already has the term somewhere
                            if question_term.lower() not in answer.lower()[:100]:
                                answer = f"{question_term_capitalized} is {answer[0].lower() + answer[1:] if len(answer) > 1 and answer[0].islower() else answer}"
                
                # Ensure answer ends with proper punctuation (if it's a complete sentence)
                if answer and not answer.rstrip().endswith(('.', '!', '?')):
                    # If it looks like it was cut off mid-sentence, try to complete it
                    # Otherwise, just ensure it ends with a period if it's a statement
                    if len(answer.split()) > 5:  # Only if it's a substantial answer
                        answer = answer.rstrip() + '.'
                
                # Ensure proper punctuation throughout - fix common issues
                # Ensure no double punctuation
                answer = re.sub(r'([.!?]){2,}', r'\1', answer)
                # Ensure space after punctuation (but not if it's already there)
                answer = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', answer)
                # Remove extra spaces
                answer = re.sub(r'\s+', ' ', answer)
                answer = re.sub(r'\s+([.!?])', r'\1', answer)
            
            # Post-process to ensure strict format - remove URLs
            answer = re.sub(r'https?://[^\s]+', '', answer)
            answer = re.sub(r'\(https?://[^\)]+\)', '', answer)
            answer = re.sub(r'From [^:]+ \(http[^\)]+\):', '', answer)
            answer = re.sub(r'From [^:]+:', '', answer)
            answer = re.sub(r'Source: [^\n]+', '', answer)
            answer = re.sub(r'📚 Sources:?[^\n]*', '', answer)
            answer = re.sub(r'🔗 \[[^\]]+\]\([^\)]+\)', '', answer)
            
            # Final check: If answer still starts with a connector or fragment, rebuild it
            answer_stripped = answer.strip()
            if answer_stripped:
                first_word = answer_stripped.split()[0].lower() if answer_stripped.split() else ""
                problematic_starters = ['however', 'but', 'also', 'additionally', 'furthermore', 'moreover', 'meanwhile']
                
                if first_word in problematic_starters or not answer_stripped[0].isupper():
                    # Try to find the first complete sentence
                    sentences = re.split(r'([.!?]+(?:\s+|$))', answer_stripped)
                    complete_answer = ""
                    found_proper_start = False
                    
                    for i in range(0, len(sentences) - 1, 2):
                        if i + 1 < len(sentences):
                            sentence = (sentences[i] + sentences[i+1]).strip()
                            if sentence:
                                first_char = sentence[0] if sentence else ""
                                first_words = sentence.split()[:2]
                                first_phrase = ' '.join(first_words).lower() if len(first_words) >= 2 else ""
                                
                                # Check if this is a proper sentence start
                                if first_char.isupper() and first_phrase.split()[0] not in problematic_starters:
                                    complete_answer = ''.join(sentences[i:]).strip()
                                    found_proper_start = True
                                    break
                    
                    if found_proper_start:
                        answer = complete_answer
                    else:
                        # Last resort: remove first problematic word and capitalize
                        words = answer_stripped.split()
                        if words and words[0].lower() in problematic_starters:
                            answer = ' '.join(words[1:])
                            if answer:
                                answer = answer[0].upper() + answer[1:] if len(answer) > 1 else answer.upper()
                        elif answer_stripped and answer_stripped[0].islower():
                            answer = answer_stripped[0].upper() + answer_stripped[1:] if len(answer_stripped) > 1 else answer_stripped.upper()
            
            return answer.strip() if answer else answer
        
        except Exception as e:
            return self._extract_answer_from_context(question, context, city)
    
    def _extract_answer_from_context(self, question: str, context: str, city: str) -> str:
        """Extract answer from context without LLM (free mode) - Format: Natural paragraphs + Sources"""
        import re
        
        # Clean context - remove URLs, navigation, menus
        clean_context = re.sub(r'https?://[^\s\)]+', '', context)
        clean_context = re.sub(r'\(https?://[^\)]+\)', '', clean_context)
        clean_context = re.sub(r'Skip to [^\n]+', '', clean_context, flags=re.IGNORECASE)
        clean_context = re.sub(r'Back to top[^\n]*', '', clean_context, flags=re.IGNORECASE)
        clean_context = re.sub(r'Menu[^\n]*', '', clean_context, flags=re.IGNORECASE)
        clean_context = re.sub(r'Search[^\n]*', '', clean_context, flags=re.IGNORECASE)
        clean_context = re.sub(r'View all[^\n]*', '', clean_context, flags=re.IGNORECASE)
        
        question_lower = question.lower()
        
        # Check for "new" or "recent" - prioritize recent updates section
        if ("new" in question_lower or "recent" in question_lower or "latest" in question_lower) and "RECENT UPDATES" in context:
            try:
                if "REGULATION DATABASE" in context:
                    update_section = context.split("RECENT UPDATES")[1].split("REGULATION DATABASE")[0]
                else:
                    update_section = context.split("RECENT UPDATES")[1]
                
                if update_section:
                    lines = update_section.split('\n')
                    answer_parts = []
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('===') and len(line) > 10:
                            if line.startswith('**') and line.endswith('**'):
                                answer_parts.append(f"\n{line}")
                            elif 'Summary:' in line or 'URL:' in line or 'Detected:' in line:
                                answer_parts.append(line)
                            else:
                                answer_parts.append(line)
                    if answer_parts:
                        answer = "\n".join(answer_parts[:15])
                        if "[Note:" not in answer:
                            answer += f"\n\n[Note: This is extracted from recent regulation updates. For complete information, please check the official sources linked below.]"
                        return answer
            except:
                pass
        
        # Handle definition questions with better extraction
        if "what does" in question_lower or "what is" in question_lower or "mean" in question_lower:
            sentences = context.split('.')
            relevant_sentences = []
            definition_keywords = ["means", "refers to", "is defined", "is a", "are", "includes", "stands for", "refers"]
            
            # Extract the term being asked about
            question_words = []
            if "what is" in question_lower:
                parts = question_lower.split("what is")
                if len(parts) > 1:
                    term = parts[1].strip().split()[0:3]
                    question_words.extend(term)
            if "what does" in question_lower:
                parts = question_lower.split("what does")
                if len(parts) > 1:
                    term = parts[1].strip().split()[0:3]
                    question_words.extend(term)
            question_words.extend([w for w in question_lower.split() if len(w) > 3])
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) < 20:
                    continue
                sentence_lower = sentence.lower()
                is_definition = any(keyword in sentence_lower for keyword in definition_keywords)
                is_relevant = any(word in sentence_lower for word in question_words if len(word) > 3)
                
                if (is_definition or is_relevant) and any(kw in sentence_lower for kw in ["regulation", "law", "housing", "tenant", "landlord", "esa", "fair housing", "rent", "lease"]):
                    relevant_sentences.append(sentence)
            
            if relevant_sentences:
                seen = set()
                unique_sentences = []
                for sent in relevant_sentences:
                    sent_lower = sent.lower()
                    if sent_lower not in seen and len(sent.strip()) > 20:
                        seen.add(sent_lower)
                        unique_sentences.append(sent.strip())
                
                # Limit to 4-6 sentences, then format as 4-6 lines
                answer = ". ".join(unique_sentences[:6])
                # Remove any remaining navigation text
                answer = re.sub(r'Skip to [^\n]+', '', answer, flags=re.IGNORECASE)
                answer = re.sub(r'Menu[^\n]*', '', answer, flags=re.IGNORECASE)
                # Split into lines and limit to 4-6 lines
                lines = [line.strip() for line in answer.split('\n') if line.strip()]
                if len(lines) > 6:
                    answer = '\n'.join(lines[:6])
                elif len(lines) < 4 and len(unique_sentences) >= 4:
                    # If we have enough sentences but not enough lines, split sentences into lines
                    answer = ". ".join(unique_sentences[:6])
                    # Try to split long sentences into lines (rough heuristic)
                    sentences_list = answer.split('. ')
                    lines = []
                    for sent in sentences_list[:6]:
                        if len(sent) > 100:  # Long sentence, might split
                            words = sent.split()
                            mid = len(words) // 2
                            lines.append(' '.join(words[:mid]) + '.')
                            lines.append(' '.join(words[mid:]))
                        else:
                            lines.append(sent)
                    answer = '\n'.join(lines[:6])
                return answer
        
        # Find relevant sentences with better keyword matching
        sentences = context.split('.')
        relevant_sentences = []
        keywords = []
        keywords.extend([w for w in question_lower.split() if len(w) > 3])
        if "rent control" in question_lower:
            keywords.append("rent control")
        if "fair housing" in question_lower:
            keywords.append("fair housing")
        if "emotional support" in question_lower or "esa" in question_lower:
            keywords.extend(["emotional support", "esa"])
        if "service animal" in question_lower:
            keywords.append("service animal")
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 30:
                continue
            sentence_lower = sentence.lower()
            matches = sum(1 for keyword in keywords if keyword in sentence_lower)
            
            if matches > 0 and any(kw in sentence_lower for kw in ["regulation", "law", "ordinance", "code", "statute", 
                                                                    "housing", "rent", "lease", "tenant", "landlord",
                                                                    "fair housing", "esa", "zoning", "compliance",
                                                                    "require", "prohibit", "allow", "must", "shall"]):
                relevant_sentences.append((sentence, matches))
        
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        
        if relevant_sentences:
            top_sentences = [s[0] for s in relevant_sentences[:8]]
            # Clean URLs and source text from sentences
            cleaned_sentences = []
            for sent in top_sentences:
                cleaned = re.sub(r'https?://[^\s\)]+', '', sent)
                cleaned = re.sub(r'\(https?://[^\)]+\)', '', cleaned)
                cleaned = re.sub(r'Source: [^\(]+ \(http[^\)]+\)', '', cleaned)
                cleaned = re.sub(r'Source: [^\n]+', '', cleaned)
                cleaned = re.sub(r'From [^:]+:', '', cleaned)
                cleaned = re.sub(r'Skip to [^\n]+', '', cleaned)
                cleaned = re.sub(r'Landlord/Tenant Law[^\n]*', '', cleaned)
                cleaned = re.sub(r'Search this Guide[^\n]*', '', cleaned)
                cleaned = re.sub(r'View all pages[^\n]*', '', cleaned)
                # Only keep sentences that are meaningful (not navigation/menu text)
                if cleaned.strip() and len(cleaned.strip()) > 20 and not any(skip in cleaned.lower() for skip in ['skip to', 'menu', 'search', 'view all', 'back to top']):
                    cleaned_sentences.append(cleaned.strip())
            
            seen = set()
            unique_sentences = []
            for sent in cleaned_sentences:
                sent_lower = sent.lower()
                if sent_lower not in seen:
                    seen.add(sent_lower)
                    unique_sentences.append(sent)
            
            # Limit to 4-6 sentences, then format as 4-6 lines
            answer = ". ".join(unique_sentences[:6])
            
            # Remove any remaining URL patterns and navigation
            answer = re.sub(r'https?://[^\s\)]+', '', answer)
            answer = re.sub(r'\(https?://[^\)]+\)', '', answer)
            answer = re.sub(r'Skip to [^\n]+', '', answer, flags=re.IGNORECASE)
            answer = re.sub(r'Menu[^\n]*', '', answer, flags=re.IGNORECASE)
            
            # Ensure 4-6 lines format
            lines = [line.strip() for line in answer.split('\n') if line.strip()]
            if len(lines) > 6:
                answer = '\n'.join(lines[:6])
            elif len(lines) < 4:
                # If not enough lines, split sentences into lines
                sentences_list = answer.split('. ')
                lines = []
                for sent in sentences_list[:6]:
                    sent = sent.strip()
                    if sent:
                        if len(sent) > 120:  # Long sentence, might split
                            words = sent.split()
                            mid = len(words) // 2
                            if mid > 0:
                                lines.append(' '.join(words[:mid]) + '.')
                                lines.append(' '.join(words[mid:]))
                            else:
                                lines.append(sent)
                        else:
                            lines.append(sent)
                answer = '\n'.join(lines[:6]) if len(lines) >= 4 else '\n'.join(lines)
            
            return answer
        else:
            # Return standard missing message
            return GUARDRAIL_RESPONSES["missing_information"]
