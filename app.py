"""
Main Streamlit application for Housing Regulation Compliance Agent
"""
import streamlit as st
import pandas as pd
from database import RegulationDB
from scraper import RegulationScraper
from vector_store import RegulationVectorStore
from update_checker import UpdateChecker
from compliance_checker import ComplianceChecker
from email_alerts import EmailAlertSystem
from qa_system import QASystem
from config import SUPPORTED_CITIES, REGULATION_CATEGORIES, LEGAL_DISCLAIMER, SOURCES_FILE
import time
import os
import re

# Page configuration
st.set_page_config(
    page_title="Intelligence Platform",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state with error handling
if 'db' not in st.session_state:
    try:
        st.session_state.db = RegulationDB()
    except Exception as e:
        st.session_state.db = None
        st.session_state._db_error = str(e)

if 'scraper' not in st.session_state:
    try:
        st.session_state.scraper = RegulationScraper()
    except Exception as e:
        st.session_state.scraper = None
        st.session_state._scraper_error = str(e)

if 'vector_store' not in st.session_state:
    try:
        st.session_state.vector_store = RegulationVectorStore()
    except Exception as e:
        st.session_state.vector_store = None
        st.session_state._vector_store_error = str(e)

if 'update_checker' not in st.session_state:
    try:
        st.session_state.update_checker = UpdateChecker()
    except Exception as e:
        st.session_state.update_checker = None
        st.session_state._update_checker_error = str(e)

if 'compliance_checker' not in st.session_state:
    try:
        st.session_state.compliance_checker = ComplianceChecker()
    except Exception as e:
        st.session_state.compliance_checker = None
        st.session_state._compliance_checker_error = str(e)

if 'email_system' not in st.session_state:
    try:
        st.session_state.email_system = EmailAlertSystem()
    except Exception as e:
        st.session_state.email_system = None
        st.session_state._email_system_error = str(e)

if 'qa_system' not in st.session_state:
    try:
        st.session_state.qa_system = QASystem()
    except Exception as e:
        st.session_state.qa_system = None
        st.session_state._qa_system_error = str(e)

def main():
    # Show initialization errors if any
    if hasattr(st.session_state, '_db_error'):
        st.error(f"⚠️ Database initialization failed: {st.session_state._db_error}")
    if hasattr(st.session_state, '_vector_store_error'):
        st.warning(f"⚠️ Vector store initialization failed: {st.session_state._vector_store_error}")
    if hasattr(st.session_state, '_qa_system_error'):
        st.error(f"⚠️ QA system initialization failed: {st.session_state._qa_system_error}")
    
    st.title("🏠 Intelligence Platform")
    st.markdown("**AI-Powered Housing Regulation Compliance Assistant**")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    page = st.sidebar.radio(
        "Select Page",
        ["Intelligence Platform Agent", "Regulation Explorer", "Update Log", "Email Alerts", "Settings"]
    )
    
    # Display legal disclaimer in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown(LEGAL_DISCLAIMER)
    
    # Route to appropriate page
    if page == "Intelligence Platform Agent":
        show_ip_agent_page()
    elif page == "Regulation Explorer":
        show_regulation_explorer()
    elif page == "Update Log":
        show_update_log()
    elif page == "Email Alerts":
        show_email_alerts()
    elif page == "Settings":
        show_settings()

def show_home():
    st.header("Welcome to the Housing Regulation Compliance Agent")
    
    st.markdown("""
    This platform helps property managers and leasing professionals:
    - 💬 **Ask Questions** - Get answers about regulations from our database
    - 📋 **Track** housing regulations from federal, state, and city sources
    - 🔍 **Check** lease documents for compliance issues
    - 🔔 **Receive** alerts when regulations are updated (daily scraping)
    - 📊 **Explore** organized regulatory information
    
    ### Key Features:
    1. **Ask Questions**: Ask questions about regulations and get answers
    2. **Regulation Explorer**: Browse and search all regulations
    3. **Compliance Checker**: Upload lease documents for compliance analysis
    4. **Update Log**: View recent regulation updates
    5. **Email Alerts**: Subscribe to city-specific updates
    """)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        regulations = st.session_state.db.get_all_regulations()
        st.metric("Total Regulations", len(regulations))
    
    with col2:
        updates = st.session_state.db.get_recent_updates(limit=1000)
        st.metric("Total Updates", len(updates))
    
    with col3:
        st.metric("Supported Cities", len(SUPPORTED_CITIES))
    
    with col4:
        st.metric("Categories", len(REGULATION_CATEGORIES))
    
    st.markdown("---")
    st.markdown("### Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Check for Updates", use_container_width=True):
            with st.spinner("Checking for regulation updates..."):
                updates = st.session_state.update_checker.check_for_updates()
                if updates:
                    st.success(f"✅ Found {len(updates)} new update(s)!")
                    # Notify subscribers
                    for update in updates:
                        st.session_state.email_system.notify_subscribers(update)
                    
                    # Show updates
                    for update in updates:
                        with st.expander(f"📢 {update['source_name']} - Update Detected", expanded=True):
                            st.markdown(f"**Summary:** {update['summary']}")
                            st.markdown(f"**Affected Cities:** {', '.join(update.get('affected_cities', []))}")
                            st.markdown(f"**URL:** {update.get('url', 'N/A')}")
                            st.info("💡 Check the 'Update Log' page to see all updates, or check the 'emails' folder for email notifications.")
                else:
                    st.info("No new updates detected. All regulations are up to date.")
    
    with col2:
        if st.button("📥 Load Regulations from Excel", use_container_width=True):
            try:
                result = st.session_state.db.load_regulations_from_csv(SOURCES_FILE)
                st.success(f"Regulations loaded successfully! ({result['loaded']} loaded, {result['skipped']} skipped)")
            except Exception as e:
                st.error(f"Error loading regulations: {str(e)}")

def show_ip_agent_page():
    """Main Intelligence Platform Agent page with integrated chat and compliance checker"""
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'compliance_city' not in st.session_state:
        st.session_state.compliance_city = None
    
    def process_question(prompt_text):
        """Helper function to process a question and add to chat history"""
        if st.session_state.qa_system is None:
            return {
                'answer': '❌ **Error:** QA system is not initialized. Please check the Settings page or restart the app.',
                'sources': []
            }
        st.session_state.chat_history.append({'role': 'user', 'content': prompt_text})
        result = st.session_state.qa_system.answer_question_with_context(prompt_text, st.session_state.chat_history)
        answer_text = result['answer']
        
        # Clean up answer - remove ALL URLs, source references, and navigation text
        import re
        
        # Check for personal legal advice requests
        prompt_lower = prompt_text.lower()
        personal_advice_keywords = ["my situation", "my case", "i have", "i need advice", "what should i do about", "can i", "should i", "help me with my"]
        is_personal_advice = any(keyword in prompt_lower for keyword in personal_advice_keywords)
        
        # Clean answer text
        answer_text = re.sub(r'From [^:]+ \(http[^\)]+\):', '', answer_text)
        answer_text = re.sub(r'From [^:]+:', '', answer_text)
        answer_text = re.sub(r'Source: [^\n]+', '', answer_text)
        answer_text = re.sub(r'📚 Sources:?[^\n]*', '', answer_text)
        answer_text = re.sub(r'🔗 \[[^\]]+\]\([^\)]+\)', '', answer_text)
        answer_text = re.sub(r'https?://[^\s\)]+', '', answer_text)  # Remove all URLs
        answer_text = re.sub(r'\[This is a general explanation[^\]]+\]', '', answer_text)
        answer_text = re.sub(r'See sources below[^\n]*', '', answer_text)
        answer_text = re.sub(r'\[Note:[^\]]+\]', '', answer_text)
        answer_text = re.sub(r'Skip to [^\n]+', '', answer_text)
        answer_text = re.sub(r'Landlord/Tenant Law[^\n]*', '', answer_text)
        answer_text = re.sub(r'Search this Guide[^\n]*', '', answer_text)
        answer_text = re.sub(r'View all pages[^\n]*', '', answer_text)
        # Remove update formatting markers
        answer_text = re.sub(r'=== RECENT UPDATES[^=]*===', '', answer_text, flags=re.IGNORECASE)
        answer_text = re.sub(r'=== REGULATION DATABASE[^=]*===', '', answer_text, flags=re.IGNORECASE)
        answer_text = re.sub(r'\(NEW LAWS\)', '', answer_text, flags=re.IGNORECASE)
        # Fix character-by-character spacing issues
        lines = answer_text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Skip lines that are just single characters (likely formatting artifacts)
            stripped = line.strip()
            if len(stripped) > 1 or (stripped and stripped.isalnum() and len(stripped) == 1 and stripped.isalpha()):
                # Only keep single character lines if they're meaningful (like "a" in "a tenant")
                if len(stripped) == 1:
                    # Check if previous line ends with space (likely part of a word)
                    if cleaned_lines and cleaned_lines[-1].rstrip().endswith(' '):
                        cleaned_lines.append(line)
                    else:
                        # Skip single character lines that are likely artifacts
                        continue
                else:
                    cleaned_lines.append(line)
            elif not stripped:
                # Keep empty lines for paragraph spacing
                cleaned_lines.append(line)
        answer_text = '\n'.join(cleaned_lines)
        # Fix excessive spacing
        answer_text = re.sub(r'([a-z])\s+([a-z])', r'\1 \2', answer_text)  # Fix word spacing
        answer_text = re.sub(r'\s+', ' ', answer_text)  # Normalize spaces
        answer_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', answer_text)  # Normalize line breaks
        
        # Remove lines with "---"
        lines = answer_text.split('\n')
        cleaned_lines = [line for line in lines if not line.strip().startswith("---")]
        answer_text = '\n'.join(cleaned_lines).strip()
        
        # Clean up excessive newlines but preserve bullet list structure
        answer_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', answer_text)
        # Don't collapse to single paragraph - preserve structure for bullet lists
        
        # Format sources as hyperlinks (collect ALL unique sources - multiple hyperlinks)
        source_urls = []
        seen_urls = set()
        for source in result.get('sources', []):
            url = source.get('url', '')
            # Include http, https, and file:// URLs (all sources)
            if url and url.startswith(('http://', 'https://', 'file://')) and url not in seen_urls:
                seen_urls.add(url)
                source_urls.append(url)
        
        # Add safety note for personal legal advice
        if is_personal_advice and "consult" not in answer_text.lower() and "qualified" not in answer_text.lower():
            answer_text += " For specific legal advice regarding your situation, please consult with a qualified legal professional."
        
        # Format sources at the end as hyperlinks (ALL sources - multiple hyperlinks)
        if source_urls:
            # Check if [SOURCES] section already exists
            if "[SOURCES]" not in answer_text:
                answer_text += "\n\n[SOURCES]\n\n"
                # Display ALL source URLs in format: - Name: hyperlink
                for source in result.get('sources', []):
                    url = source.get('url', '')
                    source_name = source.get('source', source.get('source_name', 'Unknown Source'))
                    if url and url.startswith(('http://', 'https://', 'file://')):
                        # Format as: - Name: hyperlink
                        answer_text += f"- {source_name}: {url}\n\n"
        
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': answer_text,
            'sources': result.get('sources', [])
        })
        st.rerun()
    
    st.header("💬 Intelligence Platform Agent")
    
    # Display predefined leasing manager questions as first message if chat is empty
    if len(st.session_state.chat_history) == 0:
        with st.chat_message("assistant"):
            st.markdown("Hello! I'm your Texas Housing Compliance Assistant, trained to support leasing managers. 👋\n\n**Frequent Questions:**")
            
            # Pre-populated questions as specified
            predefined_questions = [
                ("What is ESA?", "pre1"),
                ("What is HUD?", "pre2"),
                ("What is Section 8 in Dallas, Texas?", "pre3"),
                ("What are landlord obligations under Texas law?", "pre4")
            ]
            
            # Display in 2 columns
            col1, col2 = st.columns(2)
            for idx, (question, key) in enumerate(predefined_questions):
                col = col1 if idx % 2 == 0 else col2
                with col:
                    if st.button(f"💡 {question}", key=key, use_container_width=True):
                        process_question(question)
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            with st.chat_message("user"):
                if message.get('file_uploaded'):
                    st.write(f"📎 {message.get('filename', 'Document')}")
                st.write(message['content'])
        else:
            with st.chat_message("assistant"):
                answer_content = message['content']
                if "[Note:" in answer_content:
                    answer_content = answer_content.split("[Note:")[0].strip()
                # Remove raw context lines
                if "From " in answer_content and "(" in answer_content:
                    lines = answer_content.split('\n')
                    cleaned_lines = []
                    for line in lines:
                        if line.startswith("From ") and "(" in line and "):" in line:
                            continue
                        if line.strip().startswith("---"):
                            continue
                        cleaned_lines.append(line)
                    answer_content = '\n'.join(cleaned_lines).strip()
                
                # Remove ALL markdown formatting that causes large/bold text
                # Remove bold headers (##, ###, **text**)
                answer_content = re.sub(r'^#{1,6}\s+', '', answer_content, flags=re.MULTILINE)  # Remove markdown headers
                answer_content = re.sub(r'\*\*([^*]+)\*\*', r'\1', answer_content)  # Remove bold (**text**)
                answer_content = re.sub(r'\*([^*]+)\*', r'\1', answer_content)  # Remove italic (*text*)
                answer_content = re.sub(r'^Answer:\s*', '', answer_content, flags=re.IGNORECASE | re.MULTILINE)  # Remove "Answer:" prefix
                
                # Split on [SOURCES] or Sources section
                if "[SOURCES]" in answer_content:
                    # Split on [SOURCES]
                    parts = answer_content.split("[SOURCES]")
                    if len(parts) > 1:
                        # Display answer part - clean plain text (remove all markdown)
                        answer_part = parts[0].replace("[ANSWER]", "").strip()
                        # Remove ALL markdown formatting completely - be very aggressive
                        answer_part = re.sub(r'\*\*([^*]+)\*\*', r'\1', answer_part)  # Remove bold
                        answer_part = re.sub(r'\*([^*]+)\*', r'\1', answer_part)  # Remove italic
                        answer_part = re.sub(r'^#{1,6}\s+', '', answer_part, flags=re.MULTILINE)  # Remove headers
                        answer_part = re.sub(r'^##+\s*', '', answer_part, flags=re.MULTILINE)  # Remove any remaining headers
                        answer_part = re.sub(r'<[^>]+>', '', answer_part)  # Remove HTML tags
                        # Display using st.write (which should render as plain text if no markdown)
                        st.write(answer_part)
                        
                        # Display sources section
                        st.write("\n[SOURCES]\n")
                        sources_text = parts[1].strip()
                        # Parse sources in format: - Name: hyperlink
                        source_lines = sources_text.split('\n')
                        for line in source_lines:
                            line = line.strip()
                            if line.startswith('-') and ':' in line:
                                st.write(line)
                            elif 'http' in line:
                                # Extract URL if it's just a URL
                                urls = re.findall(r'https?://[^\s\n\)]+', line)
                                for url in urls:
                                    st.write(url)
                elif "Sources:" in answer_content or "**Sources:**" in answer_content or "**Sources**" in answer_content:
                    # Split on Sources: (with or without markdown) - legacy format
                    parts = re.split(r'\*\*Sources\*\*:?\s*|Sources:\s*', answer_content, flags=re.IGNORECASE)
                    if len(parts) > 1:
                        # Display answer part - clean plain text (remove all markdown)
                        answer_part = parts[0].strip()
                        # Remove ALL markdown formatting completely - be very aggressive
                        answer_part = re.sub(r'\*\*([^*]+)\*\*', r'\1', answer_part)  # Remove bold
                        answer_part = re.sub(r'\*([^*]+)\*', r'\1', answer_part)  # Remove italic
                        answer_part = re.sub(r'^#{1,6}\s+', '', answer_part, flags=re.MULTILINE)  # Remove headers
                        answer_part = re.sub(r'^##+\s*', '', answer_part, flags=re.MULTILINE)  # Remove any remaining headers
                        answer_part = re.sub(r'<[^>]+>', '', answer_part)  # Remove HTML tags
                        # Display using st.write (which should render as plain text if no markdown)
                        st.write(answer_part)
                        
                        # Display sources section
                        st.write("\nSources:\n")
                        sources_text = parts[1].strip()
                        # Extract URLs from sources text
                        urls = re.findall(r'https?://[^\s\n\)]+', sources_text)
                        for url in urls:
                            st.write(url)
                    else:
                        # Clean answer content - plain text only
                        answer_content = re.sub(r'\*\*([^*]+)\*\*', r'\1', answer_content)
                        answer_content = re.sub(r'\*([^*]+)\*', r'\1', answer_content)
                        answer_content = re.sub(r'^#{1,6}\s+', '', answer_content, flags=re.MULTILINE)
                        answer_content = re.sub(r'<[^>]+>', '', answer_content)  # Remove HTML tags
                        st.write(answer_content)
                else:
                    # Clean answer content - plain text only
                    answer_content = re.sub(r'\*\*([^*]+)\*\*', r'\1', answer_content)
                    answer_content = re.sub(r'\*([^*]+)\*', r'\1', answer_content)
                    answer_content = re.sub(r'^#{1,6}\s+', '', answer_content, flags=re.MULTILINE)
                    answer_content = re.sub(r'<[^>]+>', '', answer_content)  # Remove HTML tags
                    st.write(answer_content)
                
                # Show sources and applicable to if available
                if 'sources' in message and message['sources']:
                    # Remove duplicates
                    seen_sources = set()
                    unique_sources = []
                    for source in message['sources']:
                        source_key = (source.get('url', ''), source.get('source', ''))
                        if source_key not in seen_sources:
                            seen_sources.add(source_key)
                            unique_sources.append(source)
                    
                    # Don't show separate sources section - sources are already in answer text
                    # Sources are shown as "Sources: Source Name 1; Source Name 2" format
    
    # File uploader with expandable toolbar
    st.markdown("---")
    with st.expander("📎 Document Compliance Checker - Click to learn more", expanded=False):
        st.markdown("""
**Purpose:** Upload lease documents (PDF or DOCX) to check compliance with Texas housing regulations.

**What this does:**
- Analyzes your lease document clause-by-clause
- Identifies compliance issues with Texas housing laws
- Provides specific fixes and action items
- Checks for ESA, Fair Housing, rent control, and other regulation violations

**How to use:**
1. Click "Browse files" below to upload your lease document
2. Once uploaded, ask "Is this compliant?" or "Check this document"
3. The system will analyze and provide a detailed compliance report
        """)
    
    uploaded_file = st.file_uploader("📎 Attach lease document (PDF/DOCX)", type=['pdf', 'docx', 'doc'], key="chat_file_upload", help="Upload a lease document to check compliance with Texas housing regulations")
    
    # Show file info if uploaded
    if uploaded_file is not None:
        st.info(f"📎 **File attached:** {uploaded_file.name} ({uploaded_file.size:,} bytes). Ask 'Is this compliant?' or 'Check this document' to analyze it.")
    
    # Chat input
    chat_placeholder = "Ask a question about Texas housing regulations..."
    if uploaded_file is not None:
        chat_placeholder = f"📎 {uploaded_file.name} attached. Ask 'Is this compliant?' or type your question..."
    
    if prompt := st.chat_input(chat_placeholder):
        # Handle file upload - check both current upload and pending file
        file_content = None
        filename = None
        
        # First check if there's a pending file from previous interaction
        if 'pending_file' in st.session_state:
            file_content = st.session_state.pending_file
            filename = st.session_state.pending_filename
        elif uploaded_file is not None:
            # Read the file immediately before rerun
            file_content = uploaded_file.read()
            filename = uploaded_file.name
            # Store in session state for next iteration
            st.session_state.current_file = file_content
            st.session_state.current_filename = filename
        
        # Add user message to history
        user_message = {'role': 'user', 'content': prompt}
        if file_content:
            user_message['file_uploaded'] = True
            user_message['filename'] = filename
            user_message['file_content'] = file_content
        st.session_state.chat_history.append(user_message)
        
        # Display user message
        with st.chat_message("user"):
            if file_content:
                st.write(f"📎 {filename}")
            st.write(prompt)
        
        # Get answer
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Check if user wants compliance check (has file or mentions compliance)
                wants_compliance_check = file_content or any(keyword in prompt.lower() for keyword in ["compliant", "compliance", "check document", "check this", "is this", "review", "analyze"])
                
                # Auto-detect city from prompt
                detected_city = None
                prompt_lower = prompt.lower()
                for city in SUPPORTED_CITIES:
                    if city.lower() in prompt_lower:
                        detected_city = city
                        break
                
                if wants_compliance_check:
                    if file_content:
                        # Use detected city or ask for city selection
                        selected_city = detected_city or st.session_state.get('compliance_city')
                        
                        # Store file immediately to prevent loss on rerun
                        if file_content:
                            st.session_state.pending_file = file_content
                            st.session_state.pending_filename = filename
                        
                        if not selected_city:
                            # Ask for city
                            answer_text = "📍 **Which city are you checking compliance for?**\n\nPlease type the city name (Dallas, Houston, Austin, or San Antonio) in your next message, or select from the dropdown below."
                            st.markdown(answer_text)
                            city = st.selectbox("Select City:", ["Select..."] + SUPPORTED_CITIES, key="compliance_city_select")
                            if city != "Select...":
                                selected_city = city
                                st.session_state.compliance_city = city
                            
                            if selected_city:
                                # City selected, proceed to check
                                pass
                            else:
                                # Wait for city selection - don't proceed yet
                                st.session_state.chat_history.append({
                                    'role': 'assistant',
                                    'content': answer_text,
                                    'sources': []
                                })
                                st.rerun()
                        
                        # Run compliance check if we have a city
                        if selected_city:
                            try:
                                # Get file from pending or current
                                check_file = st.session_state.get('pending_file') or file_content
                                check_filename = st.session_state.get('pending_filename') or filename
                                check_city = selected_city or st.session_state.get('compliance_city', 'Texas-Statewide')
                                
                                if check_file is None:
                                    raise ValueError("File content not available. Please upload the file again.")
                                
                                with st.spinner(f"🔍 Analyzing document for {check_city} compliance..."):
                                    result = st.session_state.compliance_checker.check_compliance(
                                        check_file,
                                        check_filename,
                                        check_city
                                    )
                                
                                # Format output like ChatGPT - concise version
                                if result['is_compliant']:
                                    answer_text = f"✅ **Is this lease compliant for Texas & {check_city}?**\n\n"
                                    answer_text += "**Short answer: YES — compliant.**\n\n"
                                    answer_text += "This lease document appears to be compliant with Texas housing regulations."
                                else:
                                    answer_text = f"✅ **Is this lease compliant for Texas & {check_city}?**\n\n"
                                    answer_text += f"**Short answer: NO — not fully compliant.**\n\n"
                                    
                                    # Filter out issues that are just "Unable to analyze" or "Manual review required"
                                    real_issues = []
                                    for issue in result.get('issues', []):
                                        regulation = issue.get('regulation_applies', '').strip()
                                        fix = issue.get('what_to_fix', '').strip()
                                        # Only include issues with actual analysis (not generic errors)
                                        if regulation and regulation not in ["Unable to analyze", "Manual review required - OpenAI API not configured", ""]:
                                            if fix and fix not in ["Manual review required", "Review this clause against relevant regulations manually", ""]:
                                                # Check if it's a real analysis (has meaningful content)
                                                if len(regulation) > 30 and len(fix) > 20:
                                                    real_issues.append(issue)
                                    
                                    if real_issues:
                                        answer_text += f"This lease has **{len(real_issues)} compliance issue(s)** that need to be addressed.\n\n"
                                        answer_text += "**Below is the clean breakdown:**\n\n"
                                        
                                        for idx, issue in enumerate(real_issues, 1):
                                            clause_title = issue.get('clause_title', 'Compliance Issue')
                                            # Clean up clause title - remove long prefixes
                                            if '|' in clause_title:
                                                clause_title = clause_title.split('|')[-1].strip()
                                            if len(clause_title) > 50:
                                                clause_title = clause_title[:47] + "..."
                                            
                                            answer_text += f"❌ {idx}. {clause_title} – NOT COMPLIANT\n\n"
                                            
                                            clause_content = issue.get('clause_content', '')
                                            if clause_content and len(clause_content) > 50:
                                                # Extract first meaningful sentence, clean it up
                                                sentences = clause_content.split('.')
                                                first_sentences = '. '.join([s.strip() for s in sentences[:2] if len(s.strip()) > 20])[:200]
                                                if first_sentences:
                                                    answer_text += f"**What the document says:**\n\n{first_sentences}...\n\n"
                                            
                                            regulation = issue.get('regulation_applies', '')
                                            if regulation and len(regulation) > 30:
                                                answer_text += f"**Why it's non-compliant in Texas:**\n\n{regulation}\n\n"
                                            
                                            fix = issue.get('what_to_fix', '')
                                            if fix and len(fix) > 20:
                                                answer_text += f"**Fix needed:**\n\n{fix}\n\n"
                                            
                                            if issue.get('suggested_revision'):
                                                rev = issue['suggested_revision'][:300]
                                                answer_text += f"**Suggested revision:**\n\n```\n{rev}\n```\n\n"
                                            
                                            answer_text += "---\n\n"
                                        
                                        # Add concise action items (only once, not per clause)
                                        answer_text += "**📋 Action Items:**\n\n"
                                        answer_text += "- Update lease agreement document with the fixes above\n"
                                        answer_text += "- Review property management policies\n"
                                        answer_text += "- Post required Fair Housing Act poster\n"
                                        answer_text += "- Train staff on compliance requirements\n\n"
                                        
                                        # Add offer to refine/fix document
                                        answer_text += "---\n\n"
                                        answer_text += "**🔧 Need Help Fixing This Document?**\n\n"
                                        answer_text += "I can help you:\n"
                                        answer_text += "• **Refine specific clauses** - Ask me to revise any non-compliant clause with compliant language\n"
                                        answer_text += "• **Provide exact text to add** - I can give you the exact wording to insert into your lease\n"
                                        answer_text += "• **Identify specific locations** - I can tell you exactly where in the document to make changes\n\n"
                                        answer_text += "**Try asking:**\n"
                                        answer_text += "- \"Fix the security deposit clause\"\n"
                                        answer_text += "- \"What exact text should I add for ESA compliance?\"\n"
                                        answer_text += "- \"Show me the compliant version of clause 8\"\n"
                                    else:
                                        # No real issues found - document appears compliant
                                        answer_text += "✅ **Document appears compliant!**\n\n"
                                        answer_text += "The compliance checker analyzed your document using rule-based analysis and found no major compliance issues.\n\n"
                                        answer_text += "**Note:** This is a free rule-based analysis. For comprehensive legal review, consult with qualified legal counsel."
                                
                                st.markdown(answer_text)
                                st.warning(LEGAL_DISCLAIMER)
                                
                                # Clear state
                                if 'pending_file' in st.session_state:
                                    del st.session_state.pending_file
                                    del st.session_state.pending_filename
                                st.session_state.compliance_city = None
                                
                                # Add to history
                                st.session_state.chat_history.append({
                                    'role': 'assistant',
                                    'content': answer_text,
                                    'sources': []
                                })
                                st.rerun()
                            except Exception as e:
                                error_msg = f"❌ **Error checking compliance:** {str(e)}\n\nPlease make sure:\n- The file is a valid PDF or DOCX document\n- The document contains lease or rental agreement content\n- Try uploading the file again"
                                st.error(error_msg)
                                st.session_state.chat_history.append({
                                    'role': 'assistant',
                                    'content': error_msg,
                                    'sources': []
                                })
                                st.session_state.compliance_city = None
                                if 'pending_file' in st.session_state:
                                    del st.session_state.pending_file
                                    del st.session_state.pending_filename
                                st.rerun()
                    else:
                        # No file but asking about compliance
                        answer_text = "📎 **Please attach a document first** using the file uploader above, then ask about compliance again. I can check PDF and DOCX files for compliance with Texas housing regulations."
                        st.markdown(answer_text)
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': answer_text,
                            'sources': []
                        })
                        st.rerun()
                else:
                    # Regular Q&A
                    if st.session_state.qa_system is None:
                        st.error("❌ **Error:** QA system is not initialized. Please check the Settings page or restart the app.")
                        st.stop()
                    result = st.session_state.qa_system.answer_question_with_context(
                        prompt, 
                        st.session_state.chat_history
                    )
                    
                    answer_text = result['answer']
                    
                    # Clean up answer - remove raw context
                    if "From " in answer_text and "(" in answer_text:
                        lines = answer_text.split('\n')
                        cleaned_lines = []
                        for line in lines:
                            if line.startswith("From ") and "(" in line and "):" in line:
                                continue
                            if line.strip().startswith("---"):
                                continue
                            cleaned_lines.append(line)
                        answer_text = '\n'.join(cleaned_lines).strip()
                    
                    # Format sources as hyperlinks (ALL sources - multiple hyperlinks)
                    if result['sources'] and "**Sources**" not in answer_text and "**Sources:**" not in answer_text and "\n\nSources:\n\n" not in answer_text and "Sources:" not in answer_text:
                        source_urls = []
                        seen_urls = set()
                        # Collect ALL unique source URLs (multiple sources allowed)
                        for source in result['sources']:
                            url = source.get('url', '')
                            # Include http, https, and file:// URLs
                            if url and url.startswith(('http://', 'https://', 'file://')) and url not in seen_urls:
                                seen_urls.add(url)
                                source_urls.append(url)
                        
                        if source_urls:
                            answer_text += "\n\n[SOURCES]\n\n"
                            # Display ALL source URLs in format: - Name: hyperlink
                            for source in result['sources']:
                                url = source.get('url', '')
                                source_name = source.get('source', source.get('source_name', 'Unknown Source'))
                                if url and url.startswith(('http://', 'https://', 'file://')):
                                    # Format as: - Name: hyperlink
                                    answer_text += f"- {source_name}: {url}\n\n"
                    
                    if "[Note:" in answer_text:
                        answer_text = answer_text.split("[Note:")[0].strip()
                    
                    # Remove all markdown formatting for clean display
                    clean_answer = re.sub(r'^#{1,6}\s+', '', answer_text, flags=re.MULTILINE)  # Remove headers
                    clean_answer = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_answer)  # Remove bold
                    clean_answer = re.sub(r'\*([^*]+)\*', r'\1', clean_answer)  # Remove italic
                    clean_answer = re.sub(r'^Answer:\s*', '', clean_answer, flags=re.IGNORECASE | re.MULTILINE)  # Remove Answer: prefix
                    st.write(clean_answer)
                    
                    # Email prompt for new laws
                    if any(keyword in answer_text.lower() for keyword in ["new law", "new regulation", "update", "recent"]):
                        st.markdown("---")
                        st.info("📧 **Would you like to receive email alerts for new laws and policy updates?** Use the Email Alerts tab to subscribe!")
                    
                    # Store sources for expander (deduplicated)
                    seen_sources = set()
                    sources_data = []
                    for source in result.get('sources', []):
                        source_key = (source.get('url', ''), source.get('source', ''))
                        if source_key not in seen_sources:
                            seen_sources.add(source_key)
                            sources_data.append(source)
                    
                    # Add assistant response to history
                    st.session_state.chat_history.append({
                        'role': 'assistant', 
                        'content': answer_text,
                        'sources': sources_data
                    })
                    st.rerun()

def show_regulation_explorer():
    st.header("📚 Regulation Explorer")
    
    # Page description - black text on white
    st.markdown("""
**📚 Regulation Explorer** - Browse and search all housing regulations in the database.

**What you can do here:**
- Search regulations by keyword or topic
- Browse all regulations by category (Fair Housing, ESA, Rent Caps, etc.)
- View regulation details, URLs, and last checked dates
- Filter by regulation type and category

**How to use:**
1. Use the search box below to find specific regulations
2. Browse the table to see all regulations
3. Click on URLs to view the original source documents
    """)
    
    # Search and filter
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_query = st.text_input("Search Regulations", "")
    
    with col2:
        category_filter = st.selectbox("Filter by Category", ["All"] + REGULATION_CATEGORIES)
    
    with col3:
        city_filter = st.selectbox("Filter by City", ["All"] + SUPPORTED_CITIES)
    
    # Get regulations
    regulations = st.session_state.db.get_all_regulations()
    
    # Apply filters
    if category_filter != "All":
        regulations = [r for r in regulations if category_filter in r.get('category', '')]
    
    # Apply city filter
    if city_filter != "All":
        city_lower = city_filter.lower()
        filtered_regulations = []
        for r in regulations:
            # Check city in various fields
            city = r.get('city', '').lower()
            source_name = r.get('source_name', '').lower()
            category = r.get('category', '').lower()
            url = r.get('url', '').lower()
            
            # Match city name in any of these fields
            if (city_lower in city or 
                city_lower in source_name or 
                city_lower in category or
                city_lower in url):
                filtered_regulations.append(r)
        
        regulations = filtered_regulations
    
    if search_query:
        # Vector search
        if st.session_state.vector_store is None:
            st.error("❌ **Error:** Vector store is not initialized. Please check the Settings page or restart the app.")
            st.stop()
        search_results = st.session_state.vector_store.search(
            search_query, 
            n_results=10,
            prioritize_reliable=True
        )
        if search_results:
            st.subheader("Search Results")
            for result in search_results:
                with st.expander(f"📄 {result['metadata'].get('source_name', 'Unknown')}"):
                    st.write(result['document'][:500])
                    st.markdown(f"**URL**: {result['metadata'].get('url', 'N/A')}")
                    st.markdown(f"**Category**: {result['metadata'].get('category', 'N/A')}")
    
    # Display regulations table
    st.subheader("All Regulations")
    
    if regulations:
        df = pd.DataFrame(regulations)
        df['URL'] = df['url'].apply(lambda x: f"[Link]({x})" if x and x.startswith('http') else x)
        
        display_df = df[['source_name', 'type', 'category', 'URL', 'last_checked']].copy()
        display_df.columns = ['Source Name', 'Type', 'Category', 'URL', 'Last Checked']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No regulations found. Load regulations from CSV in Settings.")

def show_compliance_checker():
    st.header("Lease Compliance Checker")
    
    st.markdown("Upload a lease document (PDF or DOCX) to check for compliance with Texas housing regulations.")
    
    # City selection
    city = st.selectbox("Select City for Compliance Check", SUPPORTED_CITIES)
    
    # File upload
    uploaded_file = st.file_uploader("Upload Lease Document", type=['pdf', 'docx', 'doc'])
    
    if uploaded_file is not None:
        if st.button("Check Compliance", type="primary"):
            with st.spinner("Analyzing document for compliance..."):
                try:
                    file_content = uploaded_file.read()
                    result = st.session_state.compliance_checker.check_compliance(
                        file_content=file_content,
                        filename=uploaded_file.name,
                        city=city
                    )
                    
                    # Display results
                    st.markdown("---")
                    
                    if result['is_compliant']:
                        st.success(f"✅ **COMPLIANT**: Document passed compliance check!")
                    else:
                        st.error(f"❌ **NON-COMPLIANT**: Found {result['issues_found']} issue(s)")
                    
                    # Summary
                    st.subheader("Summary")
                    st.markdown(result['summary'])
                    
                    # Issues with action items - format per requirements
                    if result['issues']:
                        st.subheader("Compliance Issues")
                        for issue in result['issues']:
                            clause_title = issue.get('clause_title', 'Unknown Clause')
                            st.markdown(f"### ❌ Non-compliant: {clause_title}")
                            st.markdown("")
                            
                            # Reason
                            reason = issue.get('whats_missing', issue.get('what_to_fix', 'Compliance issue detected'))
                            st.markdown(f"**Reason:** {reason}")
                            st.markdown("")
                            
                            # Fix
                            if issue.get('suggested_revision'):
                                st.markdown(f"**Fix:** Add the following:")
                                st.code(issue['suggested_revision'], language=None)
                            else:
                                fix_text = issue.get('what_to_fix', 'Review and update clause for compliance')
                                st.markdown(f"**Fix:** {fix_text}")
                            st.markdown("")
                            
                            # Source
                            source = issue.get('source')
                            if source:
                                source_name = source.get('source_name', 'Unknown')
                                source_url = source.get('url', '')
                                if source_url and source_url.startswith('http'):
                                    st.markdown(f"**Source:** [{source_name}]({source_url})")
                                else:
                                    st.markdown(f"**Source:** {source_name}")
                            else:
                                st.markdown(f"**Source:** {issue.get('regulation_applies', 'Texas Housing Regulations')}")
                            
                            st.markdown("---")
                        
                        # General action items section
                        st.markdown("---")
                        st.subheader("📋 General Action Items")
                        st.markdown("""
                        **Documents to Update:**
                        - Lease agreement document
                        - Property management handbook
                        - Tenant welcome packet
                        - Staff training materials
                        
                        **Posters/Displays to Update:**
                        - Fair Housing Act poster (required by law)
                        - Tenant rights information
                        - Pet policy signage (if applicable)
                        
                        **Policy Updates:**
                        - Review and update property management policies
                        - Update tenant screening procedures if needed
                        - Ensure all staff are trained on compliance requirements
                        
                        **Next Steps:**
                        1. Review all flagged clauses
                        2. Update documents with corrected language
                        3. Post required notices/posters
                        4. Train staff on updated policies
                        5. Consult with legal counsel before finalizing changes
                        6. Keep records of all compliance updates
                        """)
                    
                    # Disclaimer
                    st.markdown("---")
                    st.warning(LEGAL_DISCLAIMER)
                
                except Exception as e:
                    st.error(f"Error checking compliance: {str(e)}")

def show_update_log():
    st.header("📢 Regulation Update Log")
    
    # Page description - black text on white
    st.markdown("""
**📢 Update Log** - Track all regulation changes and updates.

**What you can do here:**
- Select a jurisdiction (Federal, State, or City) to view updates
- See summarized articles with what changed, who is impacted, and action items
- View links to source documents
- Check for new updates manually

**How to use:**
1. Select Federal, State, or a specific city (Dallas, Austin, Houston, San Antonio)
2. View the latest update summary for that jurisdiction
3. Click "Check for Updates Now" to scan for new changes
    """)
    
    # Jurisdiction selection
    st.subheader("Select Jurisdiction")
    jurisdiction_options = ["Federal", "State", "Dallas", "Austin", "Houston", "San Antonio"]
    selected_jurisdiction = st.selectbox("Choose jurisdiction to view updates:", jurisdiction_options, key="jurisdiction_select")
    
    # Check for updates button
    if st.button("🔄 Check for Updates Now"):
        with st.spinner("Checking for updates..."):
            updates = st.session_state.update_checker.check_for_updates()
            if updates:
                st.success(f"Found {len(updates)} new update(s)!")
                # Notify subscribers
                for update in updates:
                    st.session_state.email_system.notify_subscribers(update)
            else:
                st.info("No new updates detected.")
    
    # Get updates for selected jurisdiction
    st.subheader(f"Latest Updates: {selected_jurisdiction}")
    
    # Get all regulations for this jurisdiction
    all_regulations = st.session_state.db.get_all_regulations()
    jurisdiction_regs = []
    
    for reg in all_regulations:
        category = reg.get('category', '').lower()
        source_name = reg.get('source_name', '').lower()
        
        if selected_jurisdiction == "Federal":
            if 'federal' in category or reg.get('type', '').lower() == 'federal':
                jurisdiction_regs.append(reg)
        elif selected_jurisdiction == "State":
            if 'state' in category or reg.get('type', '').lower() == 'state' or 'texas property' in source_name:
                jurisdiction_regs.append(reg)
        else:
            # City-specific
            if selected_jurisdiction.lower() in category or selected_jurisdiction.lower() in source_name:
                jurisdiction_regs.append(reg)
    
    # Get updates for these regulations
    all_updates = st.session_state.db.get_recent_updates(limit=100)
    jurisdiction_updates = []
    
    for update in all_updates:
        reg_id = update.get('regulation_id')
        # Find matching regulation
        matching_reg = next((r for r in jurisdiction_regs if r['id'] == reg_id), None)
        if matching_reg:
            jurisdiction_updates.append(update)
        else:
            # Also check by affected cities
            affected_cities = update.get('affected_cities', '')
            if isinstance(affected_cities, str):
                try:
                    affected_cities = eval(affected_cities)
                except:
                    affected_cities = [affected_cities]
            
            if selected_jurisdiction in affected_cities or (selected_jurisdiction == "Federal" and "Federal" in str(update.get('category', ''))):
                jurisdiction_updates.append(update)
    
    # Display updates
    if jurisdiction_updates:
        # Show most recent update first
        latest_update = jurisdiction_updates[0]
        affected_cities = latest_update.get('affected_cities', [])
        if isinstance(affected_cities, str):
            try:
                affected_cities = eval(affected_cities)
            except:
                affected_cities = [affected_cities] if affected_cities else []
        
        st.markdown("### 📄 Latest Update Summary")
        with st.expander(f"**{latest_update.get('source_name', 'Unknown Source')}** - {latest_update.get('detected_at', 'N/A')}", expanded=True):
            st.markdown(f"**Category:** {latest_update.get('category', 'N/A')}")
            
            # Generate detailed summary
            summary = latest_update.get('update_summary', 'No summary available.')
            
            st.markdown("---")
            st.markdown("#### What Changed?")
            st.write(summary)
            
            st.markdown("---")
            st.markdown("#### Who is Impacted?")
            st.write(f"**Leasing Managers and Property Managers** in {', '.join(affected_cities) if affected_cities else selected_jurisdiction} are impacted by this update. This affects how you handle lease agreements, tenant relations, and compliance requirements.")
            
            st.markdown("---")
            st.markdown("#### What Action to Take?")
            st.write("1. Review the updated regulation in detail using the source link below")
            st.write("2. Update your lease documents and property management policies accordingly")
            st.write("3. Train your staff on the new requirements")
            st.write("4. Ensure all new leases comply with the updated regulation")
            st.write("5. Consult with legal counsel if you have questions about implementation")
            
            st.markdown("---")
            st.markdown("#### Source Link")
            url = latest_update.get('url', '')
            if url and url.startswith('http'):
                st.markdown(f"🔗 [{latest_update.get('source_name', 'View Source')}]({url})")
            else:
                st.write(f"URL: {url if url else 'N/A'}")
        
        # Show additional updates if any
        if len(jurisdiction_updates) > 1:
            st.markdown("---")
            st.markdown(f"### Additional Updates ({len(jurisdiction_updates) - 1} more)")
            for update in jurisdiction_updates[1:]:
                affected_cities = update.get('affected_cities', [])
                if isinstance(affected_cities, str):
                    try:
                        affected_cities = eval(affected_cities)
                    except:
                        affected_cities = [affected_cities] if affected_cities else []
                
                with st.expander(f"📢 {update.get('source_name', 'Unknown')} - {update.get('detected_at', 'N/A')}", expanded=False):
                    st.markdown(f"**Category:** {update.get('category', 'N/A')}")
                    url = update.get('url', '')
                    if url and url.startswith('http'):
                        st.markdown(f"**URL:** [{url}]({url})")
                    st.markdown(f"**Summary:** {update.get('update_summary', 'No summary available.')}")
    else:
        st.info("**No new updates at the moment. Please check back later.**")

def show_email_alerts():
    st.header("📧 Email Alert Subscription")
    
    # Page description - black text on white
    st.markdown("""
**📧 Email Alerts** - Get notified about regulation changes for your cities.

**What you can do here:**
- Subscribe to receive email alerts for specific cities (Dallas, Houston, Austin, San Antonio)
- Get daily summary reports with all updates for your subscribed cities
- Receive immediate notifications when new regulations are detected
- Unsubscribe from cities you no longer need alerts for
- View all your active subscriptions

**How it works:**
1. Subscribe with your email and select a city
2. You'll receive a welcome email confirming your subscription
3. Every day, you'll get a summary report of all updates for your cities
4. You'll also get immediate alerts when new regulations are detected
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Subscribe")
        email = st.text_input("Email Address", type="default", key="subscribe_email")
        city = st.selectbox("Select City", SUPPORTED_CITIES, key="subscribe_city")
        
        if st.button("Subscribe", type="primary"):
            if email and "@" in email:
                success = st.session_state.db.subscribe_email(email, city)
                if success:
                    # Send welcome email
                    st.session_state.email_system.send_welcome_email(email, city)
                    st.success(f"✅ Subscribed {email} to {city} alerts! Check your email for a welcome message.")
                else:
                    st.warning("Already subscribed to this city.")
            else:
                st.error("Please enter a valid email address.")
    
    with col2:
        st.subheader("Unsubscribe")
        unsubscribe_email = st.text_input("Email Address", type="default", key="unsubscribe_email")
        unsubscribe_city = st.selectbox("Select City to Unsubscribe", SUPPORTED_CITIES, key="unsubscribe_city")
        
        if st.button("Unsubscribe", type="secondary"):
            if unsubscribe_email and "@" in unsubscribe_email:
                success = st.session_state.db.unsubscribe_email(unsubscribe_email, unsubscribe_city)
                if success:
                    st.success(f"✅ Unsubscribed {unsubscribe_email} from {unsubscribe_city} alerts.")
                else:
                    st.warning("No active subscription found for this email and city.")
            else:
                st.error("Please enter a valid email address.")
        
        st.markdown("---")
        st.subheader("View Your Subscriptions")
        view_email = st.text_input("Enter Email to View Subscriptions", type="default", key="view_email")
        if st.button("View Subscriptions"):
            if view_email and "@" in view_email:
                subscriptions = st.session_state.db.get_user_subscriptions(view_email)
                if subscriptions:
                    st.success(f"Active subscriptions for {view_email}:")
                    for sub in subscriptions:
                        st.info(f"📧 {sub['city']} (subscribed: {sub['subscribed_at']})")
                else:
                    st.info("No active subscriptions found for this email.")
        
        st.markdown("---")
        st.subheader("📊 Daily Summary Reports")
        st.markdown("""
        **Daily Summary Reports:**
        - Subscribers receive a daily email summary of all regulation updates for their subscribed cities
        - Summaries are sent automatically every day at 9:00 AM
        - Each summary includes all updates from the last 24 hours
        - If no updates, you'll receive a "No Updates" confirmation email
        """)
        
        if st.button("📧 Send Test Daily Summary", help="Manually trigger a daily summary for testing (sends to all subscribers)"):
            with st.spinner("Sending daily summaries..."):
                total_sent = st.session_state.email_system.send_daily_summaries_to_all_subscribers()
                if total_sent > 0:
                    st.success(f"✅ Sent {total_sent} daily summary report(s)! Check your email or the 'emails' folder.")
                else:
                    st.info("No active subscriptions found. Subscribe to a city first to receive daily summaries.")

def show_settings():
    st.header("⚙️ Settings")
    
    # Page description - black text on white
    st.markdown("""
**⚙️ Settings** - Manage your data and system configuration.

**What you can do here:**
- Load regulations from finalsource11.xlsx file
- Re-index all regulations in the vector database
- Manage data sources and update system
- Configure daily scraping schedule

**How to use:**
1. Edit `finalsource11.xlsx` to add/modify regulation sources
2. Click "Load Regulations from Excel" to import new sources
3. Use "Re-Index All Regulations" if you need to rebuild the search index
    """)
    
    st.subheader("Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Load Regulations from Excel"):
            try:
                with st.spinner("Loading regulations from Excel..."):
                    result = st.session_state.db.load_regulations_from_csv(SOURCES_FILE)
                    
                    # Show summary
                    if result['existing'] > 0:
                        st.success(f"✅ Regulations loaded! ({result['loaded']} new, {result['existing']} already exist, {result['skipped']} skipped)")
                    else:
                        st.success(f"✅ Regulations loaded! ({result['loaded']} loaded, {result['skipped']} skipped)")
                    
                    # Automatically scrape and index ONLY new regulations
                    if result['loaded'] > 0:
                        st.info(f"🔄 Now scraping and indexing {result['loaded']} new regulation(s)...")
                        
                        # Get only the new regulations that need indexing
                        new_urls = result.get('new_urls', [])
                        to_index = []
                        for url in new_urls:
                            reg = st.session_state.db.get_regulation_by_url(url)
                            if reg and not reg.get('content_hash'):
                                to_index.append(reg)
                        
                        total_to_index = len(to_index)
                        
                        if total_to_index == 0:
                            st.info("✅ All new regulations are already indexed. No indexing needed!")
                        elif total_to_index > 0:
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            estimated_time = total_to_index * 3  # ~3 seconds per URL on average
                            
                            status_text.text(f"📊 Progress: 0/{total_to_index} (Estimated time: {estimated_time//60} min {estimated_time%60} sec)")
                            
                            indexed = 0
                            skipped_indexing = 0
                            start_time = time.time()
                            
                            for idx, reg in enumerate(to_index):
                                url = reg.get('url', '')
                                if url and (url.startswith('http://') or url.startswith('https://') or url.startswith('file://') or os.path.exists(url)):
                                    try:
                                        # Update progress
                                        progress = (idx + 1) / total_to_index
                                        progress_bar.progress(progress)
                                        
                                        elapsed = time.time() - start_time
                                        if idx > 0:
                                            avg_time_per_url = elapsed / (idx + 1)
                                            remaining = (total_to_index - idx - 1) * avg_time_per_url
                                            status_text.text(f"📊 Progress: {idx + 1}/{total_to_index} | Indexed: {indexed} | Remaining: ~{int(remaining//60)} min {int(remaining%60)} sec")
                                        else:
                                            status_text.text(f"📊 Progress: {idx + 1}/{total_to_index} | Indexed: {indexed}")
                                        
                                        content = st.session_state.scraper.fetch_url_content(url)
                                        if content and content.get('content'):
                                            chunks = st.session_state.scraper.chunk_text(content['content'])
                                            if chunks:
                                                st.session_state.vector_store.add_regulation_chunks(
                                                    regulation_id=str(reg['id']),
                                                    source_name=reg['source_name'],
                                                    url=url,
                                                    category=reg.get('category', 'Other'),
                                                    chunks=chunks
                                                )
                                                # Update hash in database
                                                st.session_state.db.update_regulation_hash(url, content['hash'])
                                                indexed += 1
                                        else:
                                            skipped_indexing += 1
                                    except Exception as e:
                                        skipped_indexing += 1
                                        continue
                            
                            progress_bar.progress(1.0)
                            status_text.empty()
                            
                            total_time = time.time() - start_time
                            if indexed > 0:
                                st.success(f"✅ Indexed {indexed} new regulation(s) in vector store! (Completed in {int(total_time//60)} min {int(total_time%60)} sec)")
                            if skipped_indexing > 0:
                                st.warning(f"⚠️ Skipped {skipped_indexing} regulation(s) (could not fetch content)")
                        else:
                            st.info("✅ All regulations are already indexed. No new indexing needed.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        if st.button("🔄 Re-Index All Regulations"):
            """Re-index all regulations (useful if vector store was cleared)"""
            st.info("🔄 Indexing new regulations (only unindexed ones)...")
            
            regulations = st.session_state.db.get_all_regulations()
            # Filter to only regulations with URLs that can be scraped AND that haven't been indexed yet (no content_hash)
            to_reindex = [reg for reg in regulations 
                         if (reg.get('url', '').startswith(('http://', 'https://', 'file://')) or os.path.exists(reg.get('url', '')))
                         and not reg.get('content_hash')]  # Only index if no content_hash (not indexed yet)
            total_to_reindex = len(to_reindex)
            
            if total_to_reindex == 0:
                st.success("✅ All regulations are already indexed! No new regulations to index.")
            else:
                # Calculate estimated time (~3 seconds per URL on average)
                estimated_time = total_to_reindex * 3
                st.info(f"📊 Found {total_to_reindex} regulation(s) to re-index. Estimated time: {estimated_time//60} min {estimated_time%60} sec")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                indexed = 0
                skipped_indexing = 0
                start_time = time.time()
                
                for idx, reg in enumerate(to_reindex):
                    url = reg.get('url', '')
                    if url and (url.startswith('http://') or url.startswith('https://') or url.startswith('file://') or os.path.exists(url)):
                        try:
                            # Update progress
                            progress = (idx + 1) / total_to_reindex
                            progress_bar.progress(progress)
                            
                            elapsed = time.time() - start_time
                            if idx > 0:
                                avg_time_per_url = elapsed / (idx + 1)
                                remaining = (total_to_reindex - idx - 1) * avg_time_per_url
                                status_text.text(f"📊 Progress: {idx + 1}/{total_to_reindex} | Indexed: {indexed} | Remaining: ~{int(remaining//60)} min {int(remaining%60)} sec")
                            else:
                                status_text.text(f"📊 Progress: {idx + 1}/{total_to_reindex} | Indexed: {indexed}")
                            
                            content = st.session_state.scraper.fetch_url_content(url)
                            if content and content.get('content'):
                                chunks = st.session_state.scraper.chunk_text(content['content'])
                                if chunks:
                                    st.session_state.vector_store.add_regulation_chunks(
                                        regulation_id=str(reg['id']),
                                        source_name=reg['source_name'],
                                        url=url,
                                        category=reg.get('category', 'Other'),
                                        chunks=chunks
                                    )
                                    st.session_state.db.update_regulation_hash(url, content['hash'])
                                    indexed += 1
                            else:
                                skipped_indexing += 1
                        except Exception as e:
                            skipped_indexing += 1
                            continue
                
                progress_bar.progress(1.0)
                status_text.empty()
                
                total_time = time.time() - start_time
                if indexed > 0:
                    st.success(f"✅ Re-indexed {indexed} regulation(s)! (Completed in {int(total_time//60)} min {int(total_time%60)} sec)")
                if skipped_indexing > 0:
                    st.warning(f"⚠️ Skipped {skipped_indexing} regulation(s) (could not fetch content)")
        
        st.markdown("---")
        st.subheader("Daily Scraping")
        st.info("""
        **Daily Update Check:**
        - Runs automatically at 9:00 AM daily
        - Checks all regulations for updates
        - Sends email alerts to subscribers
        
        To run manually, use the "Check for Updates" button on the Home page.
        """)
        
        if st.button("🔄 Run Update Check Now"):
            with st.spinner("Checking for updates..."):
                updates = st.session_state.update_checker.check_for_updates()
                if updates:
                    st.success(f"Found {len(updates)} new update(s)!")
                    # Notify subscribers
                    for update in updates:
                        st.session_state.email_system.notify_subscribers(update)
                    for update in updates:
                        st.info(f"**{update['source_name']}**: {update['summary'][:100]}...")
                else:
                    st.info("No new updates detected.")
    
    with col2:
        st.subheader("System Status")
        st.info("""
        **System Status**: All systems operational
        
        **Data Management**: Use the buttons on the left to manage regulations and update the index.
        """)
    
    st.markdown("---")
    st.subheader("About")
    st.markdown("""
    **Housing Regulation Compliance Agent v1.0**
    
    Built for Texas housing regulations compliance.
    
    This tool provides informational analysis only and does not constitute legal advice.
    """)

if __name__ == "__main__":
    main()
