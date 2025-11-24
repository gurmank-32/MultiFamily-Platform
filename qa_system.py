"""
Q&A System for answering questions from regulations using RAG
"""
from vector_store import RegulationVectorStore
from database import RegulationDB
from config import OPENAI_API_KEY, LEGAL_DISCLAIMER
from prompts_config import (
    QA_SYSTEM_PROMPT, JARGON_EXPLANATION_PROMPT, 
    enhance_prompt_with_subject, get_subject_prompt
)
from typing import Dict, List, Optional

class QASystem:
    def __init__(self):
        self.vector_store = RegulationVectorStore()
        self.db = RegulationDB()
    
    def answer_question_with_context(self, question: str, chat_history: List[Dict] = None) -> Dict:
        """Answer question with conversation context for follow-up questions"""
        # Validate question quality first
        validation = self._validate_question(question)
        if not validation['is_valid']:
            return {
                "answer": validation['message'],
                "sources": [],
                "confidence": "low",
                "has_information": False
            }
        
        # Check if question is relevant to housing/leasing/regulations
        relevance_check = self._check_relevance(question)
        if not relevance_check['is_relevant']:
            return {
                "answer": relevance_check['message'],
                "sources": [],
                "confidence": "low",
                "has_information": False
            }
        
        # Handle greetings specially
        if validation.get('message') == "greeting":
            return {
                "answer": "Hello! 👋 I'm your IP Agent, an AI assistant specialized in Texas housing regulations. I can help you with:\n\n• Questions about housing laws and regulations\n• ESA (Emotional Support Animal) requirements\n• Rent control and tenant rights\n• Compliance checking for lease documents\n• City-specific regulations for Dallas, Houston, Austin, and San Antonio\n\nWhat would you like to know?",
                "sources": [],
                "confidence": "high",
                "has_information": False
            }
        
        # Build context from recent chat history for follow-up questions
        context = ""
        if chat_history and len(chat_history) > 2:
            # Get last 2 exchanges for context (only if it's a follow-up)
            recent_messages = chat_history[-4:] if len(chat_history) > 4 else chat_history
            for msg in recent_messages[:-1]:  # Exclude current question
                if msg['role'] == 'user':
                    context += f"Previous question: {msg['content']}\n"
                elif msg['role'] == 'assistant':
                    context += f"Previous answer: {msg['content'][:150]}...\n"
        
        # Use original question for search (not enhanced with context) to avoid confusion
        # Only add context if it's clearly a follow-up question
        question_lower = question.lower()
        is_followup = any(word in question_lower for word in ["it", "that", "this", "also", "and", "what about", "how about"])
        
        enhanced_question = question
        if is_followup and context:
            enhanced_question = f"{context}\n\nCurrent question: {question}"
        
        return self.answer_question(enhanced_question, city=None)
    
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
                "message": "I'm sorry, I didn't understand your request. Could you please rephrase your question? For example, you could ask about housing regulations, ESA laws, rent control, or compliance requirements."
            }
        
        # Check for random characters or gibberish
        if len(question) < 3:
            return {
                "is_valid": False,
                "message": "I'm sorry, I didn't understand your request. Could you please write your question again? I can help you with questions about Texas housing regulations, compliance, ESA laws, rent control, and more."
            }
        
        # Check for obvious gibberish (too many random characters)
        words = question.split()
        if len(words) > 0:
            meaningful_words = [w for w in words if len(w) > 1 and any(c.isalpha() for c in w)]
            if len(meaningful_words) == 0 and len(question) > 2:
                return {
                    "is_valid": False,
                    "message": "I'm sorry, I didn't understand your request. Could you please rephrase your question? I can help you with questions about Texas housing regulations, compliance, ESA laws, rent control, and more."
                }
        
        return {"is_valid": True, "message": ""}
    
    def _check_relevance(self, question: str) -> Dict:
        """Check if question is within allowed scope - STRICT validation"""
        question_lower = question.lower()
        
        # ALLOWED topics only (as per requirements)
        allowed_topics = [
            # Core topics
            "hud", "doj", "esa", "emotional support", "rent control", "zoning",
            "section 8", "hcv", "housing choice voucher",
            "leasing manager", "lease", "leasing",
            # Regulations
            "regulation", "law", "rule", "requirement", "compliance", "compliant",
            # Cities
            "dallas", "houston", "austin", "san antonio", "texas",
            # Related terms
            "fair housing", "tenant", "landlord", "property", "housing"
        ]
        
        # Check if question contains allowed topics
        has_allowed_topic = any(topic in question_lower for topic in allowed_topics)
        
        # Allow greetings
        greetings = ["hi", "hey", "hello", "whats up", "what's up", "howdy"]
        is_greeting = any(greeting in question_lower for greeting in greetings) and len(question.split()) <= 3
        
        if has_allowed_topic or is_greeting:
            return {"is_relevant": True, "message": ""}
        
        # Question is OUT OF SCOPE
        return {
            "is_relevant": False,
            "message": "I can only answer questions about:\n\n• HUD, DOJ, ESA\n• Rent control and zoning\n• Section 8 / HCV (Texas)\n• Leasing manager duties (Texas)\n• Federal, Texas state, and city (Dallas, Austin, Houston, San Antonio) housing regulations\n• Lease compliance checking\n\nPlease ask a question related to these topics."
        }
    
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
                        "answer": f"I'm sorry, but this agent's scope is limited to Texas only, specifically: Dallas, Austin, Houston, and San Antonio. I cannot provide information about {state.title()} housing regulations. Please consult local resources for that state.",
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
                    "answer": "**Currently we support Texas only: Dallas, Austin, Houston, San Antonio.**\n\nI don't have information about housing regulations for other Texas cities. Please consult local resources or add the relevant regulation sources to `source.csv`.",
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
        
        # Handle basic definition questions first
        question_lower = question.lower()
        basic_questions = {
            "esa": "ESA stands for Emotional Support Animal. In Texas housing law, ESAs are animals that provide emotional support to individuals with disabilities. Unlike service animals, ESAs do not require specific training but must be prescribed by a licensed mental health professional. Under the Fair Housing Act, landlords must make reasonable accommodations for ESAs, including waiving pet fees and deposits.",
            "emotional support animal": "An Emotional Support Animal (ESA) is an animal that provides therapeutic benefit to an individual with a mental or emotional disability. In Texas, landlords must accommodate ESAs under the Fair Housing Act, even if they have a 'no pets' policy. Landlords cannot charge pet fees or deposits for ESAs.",
            "fair housing": "The Fair Housing Act is a federal law that prohibits discrimination in housing based on race, color, religion, sex, national origin, familial status, or disability. In Texas, this law applies to most housing providers and requires reasonable accommodations for people with disabilities.",
            "rent control": "Rent control refers to laws that limit how much landlords can increase rent. In Texas, there is generally no statewide rent control. However, some cities may have local ordinances. Most Texas cities, including Dallas and Houston, do not have rent control laws, but Austin has some tenant protection measures.",
            "zoning": "Zoning refers to local government regulations that control how land can be used in different areas. Zoning laws determine what types of buildings and activities are allowed in specific areas, such as residential, commercial, or mixed-use zones."
        }
        
        # Check for basic definition questions
        for key, answer in basic_questions.items():
            if key in question_lower and ("what is" in question_lower or "what does" in question_lower or "mean" in question_lower):
                # Still search for regulations to provide sources with enhanced retrieval
                search_results = self.vector_store.search(
                    query=enhanced_query, 
                    n_results=3,
                    context={"city": final_city},
                    prioritize_reliable=True,
                    filter_geography=final_city if final_city != "Texas-Statewide" else None
                )
                sources = []
                for result in search_results:
                    sources.append({
                        "source": result['metadata'].get('source_name', 'Unknown'),
                        "url": result['metadata'].get('url', ''),
                        "category": result['metadata'].get('category', 'Unknown')
                    })
                
                return {
                    "answer": answer + "\n\n[This is a general explanation. See sources below for official regulations.]",
                    "sources": sources,
                    "confidence": "high",
                    "has_information": True
                }
        
        # Search for relevant regulations with enhanced retrieval
        search_results = self.vector_store.search(
            query=enhanced_query,
            n_results=7,  # Get more results for better context
            context={"city": final_city},
            prioritize_reliable=True,  # Prioritize authoritative sources
            filter_geography=final_city if final_city != "Texas-Statewide" else None
        )
        
        if not search_results:
            # Suggest which missing hyperlink is needed
            question_lower = question.lower()
            missing_topic = "this topic"
            if "esa" in question_lower or "emotional support" in question_lower:
                missing_topic = "ESA regulations"
            elif "hud" in question_lower:
                missing_topic = "HUD requirements"
            elif "doj" in question_lower:
                missing_topic = "DOJ regulations"
            elif "rent control" in question_lower:
                missing_topic = "rent control laws"
            elif "zoning" in question_lower:
                missing_topic = "zoning regulations"
            elif "section 8" in question_lower or "hcv" in question_lower:
                missing_topic = "Section 8 / HCV program information"
            elif "leasing manager" in question_lower:
                missing_topic = "leasing manager duties"
            
            return {
                "answer": f"**This question cannot be answered from the current knowledge base.**\n\nMissing data. Add link for {missing_topic} to source.xlsx.",
                "sources": [],
                "confidence": "low",
                "has_information": False
            }
        
        # Extract relevant context with filtering
        context_parts = []
        sources = []
        seen_urls = set()
        
        # Keywords that indicate irrelevant content (news, unrelated topics)
        irrelevant_keywords = [
            "trooper", "game", "players", "university", "student", "detention", 
            "immigration", "motorcyclist", "crash", "backhoe", "abandoned", "dit",
            "sports", "football", "basketball", "arrest", "police", "crime"
        ]
        
        for result in search_results:
            doc_text = result['document']
            metadata = result['metadata']
            source_name = metadata.get('source_name', 'Unknown')
            url = metadata.get('url', '')
            
            # Skip if we've already seen this URL
            if url in seen_urls:
                continue
            
            # Filter out irrelevant content (news articles, etc.)
            doc_lower = doc_text.lower()
            if any(keyword in doc_lower for keyword in irrelevant_keywords):
                # Check if it's actually about regulations
                regulation_keywords = ["regulation", "law", "ordinance", "code", "statute", 
                                     "housing", "rent", "lease", "tenant", "landlord", 
                                     "fair housing", "esa", "zoning", "compliance"]
                if not any(keyword in doc_lower for keyword in regulation_keywords):
                    continue  # Skip this result - it's not about regulations
            
            # Filter by city if specified
            if final_city and final_city != "Texas-Statewide":
                doc_lower = doc_text.lower()
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
            
            # Extract meaningful sentences only
            sentences = doc_text.split('.')
            relevant_sentences = []
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20:  # Only meaningful sentences
                    # Check if it contains regulation-related content
                    if any(keyword in sentence.lower() for keyword in ["regulation", "law", "ordinance", "code", 
                                                                       "housing", "rent", "lease", "tenant", "landlord",
                                                                       "fair housing", "esa", "zoning", "compliance", 
                                                                       "right", "require", "prohibit", "allow", "must", "shall"]):
                        relevant_sentences.append(sentence)
            
            if not relevant_sentences:
                continue  # Skip if no relevant sentences found
            
            clean_text = '. '.join(relevant_sentences[:5])  # Take first 5 relevant sentences
            if len(clean_text) < 100:
                continue  # Skip if too short
            
            # Add context without "From..." prefix and without URLs in the text
            context_parts.append(f"Source: {source_name}\n{clean_text}")
            sources.append({
                "source": source_name,
                "url": url,
                "category": metadata.get('category', 'Unknown')
            })
            seen_urls.add(url)
        
        if not context_parts:
            return {
                "answer": "**No verified information available from the current source list.**\n\nThis question cannot be answered using the regulations currently loaded in the system. Please ensure the relevant regulation sources are added to `source.csv` and loaded into the system.",
                "sources": [],
                "confidence": "low",
                "has_information": False
            }
        
        # Combine context
        full_context = "\n\n---\n\n".join(context_parts)
        
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
                        update_context += f"\n**{update.get('source_name', 'Unknown')}**\n"
                        update_context += f"Summary: {update.get('update_summary', '')}\n"
                        update_context += f"URL: {update_url}\n"
                        update_context += f"Detected: {update.get('detected_at', 'Unknown')}\n"
                        
                        # Add to sources (avoid duplicates)
                        if not any(s.get('url') == update_url for s in sources):
                            sources.append({
                                "source": f"{update.get('source_name', 'Unknown')} (NEW UPDATE)",
                                "url": update_url,
                                "category": update.get('category', 'Update')
                            })
                        updates_added = True
                
                if updates_added:
                    full_context = update_context + "\n\n=== REGULATION DATABASE ===\n" + full_context
        
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
                error_msg = str(e)
                if "quota" not in error_msg.lower() and "429" not in error_msg.lower():
                    # Only fall back for non-quota errors
                    answer = self._extract_answer_from_context(question, full_context, final_city)
                else:
                    # For quota errors, use free mode
                    answer = self._extract_answer_from_context(question, full_context, final_city)
        else:
            # Free mode: extract relevant snippets
            answer = self._extract_answer_from_context(question, full_context, final_city)
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": "high" if len(sources) > 0 else "low",
            "has_information": True
        }
    
    def _generate_llm_answer(self, question: str, context: str, city: str) -> str:
        """Generate answer using OpenAI LLM"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            # Check if question is general and needs clarification
            question_lower = question.lower()
            is_general = not any(city_name.lower() in question_lower for city_name in ["dallas", "houston", "austin", "san antonio", "texas"])
            needs_clarification = is_general and any(keyword in question_lower for keyword in ["rent", "regulation", "law", "policy", "rule", "requirement", "what", "how", "when", "explain"])
            
            # Clean context - remove URLs, source text, navigation menus
            import re
            clean_context = context
            # Remove URL patterns completely
            clean_context = re.sub(r'https?://[^\s\)]+', '', clean_context)
            clean_context = re.sub(r'\(https?://[^\)]+\)', '', clean_context)
            # Remove "From Source (URL):" patterns
            clean_context = re.sub(r'From [^:]+ \(http[^\)]+\):', '', clean_context)
            clean_context = re.sub(r'From [^:]+:', '', clean_context)
            clean_context = re.sub(r'Source: [^\n]+', '', clean_context)
            # Remove navigation and menu text
            clean_context = re.sub(r'Skip to [^\n]+', '', clean_context)
            clean_context = re.sub(r'Landlord/Tenant Law[^\n]*', '', clean_context)
            clean_context = re.sub(r'Search this Guide[^\n]*', '', clean_context)
            clean_context = re.sub(r'View all pages[^\n]*', '', clean_context)
            clean_context = re.sub(r'Javascript must be enabled[^\n]*', '', clean_context)
            clean_context = re.sub(r'Back to top[^\n]*', '', clean_context)
            clean_context = re.sub(r'Menu[^\n]*', '', clean_context)
            clean_context = re.sub(r'Keywords Search[^\n]*', '', clean_context)
            # Remove any remaining URL fragments
            clean_context = re.sub(r'guides\.', '', clean_context)
            clean_context = re.sub(r'www\.', '', clean_context)
            
            # Detect if this is a multi-term explanation question
            is_multi_term = any(phrase in question_lower for phrase in ["explain these", "what are", "define", "terms"])
            
            prompt = f"""You are a Housing Regulation Compliance Agent. You answer ONLY using information from the provided knowledge base chunks.

HARD RULES:
1. ONLY use information from the provided context chunks
2. If information is NOT in the context, say "Information not found in the source database."
3. DO NOT hallucinate, guess, or use knowledge outside the provided chunks
4. Be EXTREMELY CONCISE - 1-2 sentences per term maximum (6th-grade English)
5. NEVER include URLs, hyperlinks, or source names in your answer text
6. For acronyms, explain simply: "HUD stands for the U.S. Department of Housing and Urban Development. It enforces fair housing laws."
7. For multiple terms, use this EXACT format:
   **HUD:** [1 sentence explanation]
   **DOJ:** [1 sentence explanation]
   **ESA:** [1 sentence explanation]
8. Keep it SIMPLE - no complex legal jargon
9. If the question is general (no city mentioned), answer briefly then ask: "Which city are you asking about - Dallas, Austin, Houston, San Antonio, or all of Texas?"
10. Remove ALL source text, navigation menus, and website content from your answer
11. Only use information that directly answers the question from the chunks

Question: {question}
City Context: {city or 'Texas-Statewide'}

Knowledge Base Chunks (ONLY use these):
{clean_context[:6000]}

Provide a VERY CONCISE answer using ONLY the chunks above. If information is missing, say "Information not found in the source database." Maximum 1-2 sentences per term."""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful legal compliance assistant. Be EXTREMELY CONCISE. Never include URLs, source names, or 'From...' phrases. Maximum 1-2 sentences per term. For general questions, ask which city."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Post-process to ensure no URLs slipped through
            answer = re.sub(r'https?://[^\s]+', '', answer)
            answer = re.sub(r'\(https?://[^\)]+\)', '', answer)
            answer = re.sub(r'From [^:]+ \(http[^\)]+\):', '', answer)
            answer = re.sub(r'From [^:]+:', '', answer)
            
            # Add follow-up question for general questions if needed
            if needs_clarification and city == "Texas-Statewide" and not any(city_name.lower() in answer.lower() for city_name in ["dallas", "houston", "austin", "san antonio"]):
                answer += "\n\n**Is this for Dallas, Austin, Houston, San Antonio, or all of Texas?** I can provide city-specific details once you let me know."
            
            return answer
        
        except Exception as e:
            return self._extract_answer_from_context(question, context, city)
    
    def _extract_answer_from_context(self, question: str, context: str, city: str) -> str:
        """Extract answer from context without LLM (free mode) - improved version"""
        import re
        
        # Clean context - remove URLs
        clean_context = re.sub(r'https?://[^\s\)]+', '', context)
        clean_context = re.sub(r'\(https?://[^\)]+\)', '', clean_context)
        clean_context = re.sub(r'From [^:]+ \(http[^\)]+\):', 'Source:', clean_context)
        clean_context = re.sub(r'From [^:]+:', 'Source:', clean_context)
        
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
                    if sent_lower not in seen:
                        seen.add(sent_lower)
                        unique_sentences.append(sent)
                
                answer = ". ".join(unique_sentences[:6])
                if "[Note:" not in answer:
                    answer += f"\n\n[Note: This is extracted from regulations. For complete information, please check the official sources linked below.]"
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
            
            answer = ". ".join(unique_sentences)
            
            # Remove any remaining URL patterns
            answer = re.sub(r'https?://[^\s\)]+', '', answer)
            answer = re.sub(r'\(https?://[^\)]+\)', '', answer)
            
            # Add follow-up question for general questions if needed
            is_general = not any(city_name.lower() in question_lower for city_name in ["dallas", "houston", "austin", "san antonio", "texas"])
            needs_clarification = is_general and any(keyword in question_lower for keyword in ["rent", "regulation", "law", "policy", "rule", "requirement", "what", "how", "when", "explain"])
            if needs_clarification and city == "Texas-Statewide" and not any(city_name.lower() in answer.lower() for city_name in ["dallas", "houston", "austin", "san antonio"]):
                answer += "\n\n**Is this for Dallas, Austin, Houston, San Antonio, or all of Texas?** I can provide city-specific details once you let me know."
            if "[Note:" not in answer:
                answer += f"\n\n[Note: This is extracted from regulations. For complete information, please check the official sources linked below.]"
            return answer
        else:
            return f"I found some regulations related to your question, but I don't have a complete answer in our database. Please check the official sources for detailed information about '{question}'."
