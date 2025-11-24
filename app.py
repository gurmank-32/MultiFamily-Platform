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

# Page configuration
st.set_page_config(
    page_title="Intelligence Platform",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = RegulationDB()
if 'scraper' not in st.session_state:
    st.session_state.scraper = RegulationScraper()
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = RegulationVectorStore()
if 'update_checker' not in st.session_state:
    st.session_state.update_checker = UpdateChecker()
if 'compliance_checker' not in st.session_state:
    st.session_state.compliance_checker = ComplianceChecker()
if 'email_system' not in st.session_state:
    st.session_state.email_system = EmailAlertSystem()
if 'qa_system' not in st.session_state:
    st.session_state.qa_system = QASystem()

def main():
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
        if st.button("📥 Load Regulations from CSV", use_container_width=True):
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
        st.session_state.chat_history.append({'role': 'user', 'content': prompt_text})
        result = st.session_state.qa_system.answer_question_with_context(prompt_text, st.session_state.chat_history)
        answer_text = result['answer']
        
        # Clean up answer
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
        
        if result['sources'] and "Sources:" not in answer_text:
            seen_sources = set()
            unique_sources = []
            for source in result['sources']:
                source_key = (source.get('url', ''), source.get('source', ''))
                if source_key not in seen_sources:
                    seen_sources.add(source_key)
                    unique_sources.append(source)
            if unique_sources:
                answer_text += "\n\n**📚 Sources:**\n"
                for source in unique_sources:
                    if source.get('url'):
                        if source['url'].startswith('http'):
                            answer_text += f"- 🔗 [{source['source']}]({source['url']})\n"
                        elif os.path.exists(source['url']):
                            answer_text += f"- 📄 {source['source']}\n"
        
        if "[Note:" in answer_text:
            answer_text = answer_text.split("[Note:")[0].strip()
        
        sources_data = []
        seen_sources = set()
        for source in result.get('sources', []):
            source_key = (source.get('url', ''), source.get('source', ''))
            if source_key not in seen_sources:
                seen_sources.add(source_key)
                sources_data.append(source)
        
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': answer_text,
            'sources': sources_data
        })
        st.rerun()
    
    st.header("💬 Intelligence Platform Agent")
    
    # Display example questions as first message if chat is empty
    if len(st.session_state.chat_history) == 0:
        with st.chat_message("assistant"):
            st.markdown("Hello! I'm your Intelligence Platform Agent. 👋\n\n**Try asking:**")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💡 Updated law in Dallas", key="ex1", use_container_width=True):
                    process_question("Updated law in Dallas")
                if st.button("💡 What is ESA?", key="ex2", use_container_width=True):
                    process_question("What is ESA?")
                if st.button("💡 What is ESA law in Austin?", key="ex3", use_container_width=True):
                    process_question("What is ESA law in Austin?")
            with col2:
                if st.button("💡 New rent control law in Dallas", key="ex4", use_container_width=True):
                    process_question("New rent control law in Dallas")
                if st.button("💡 What is rent control?", key="ex5", use_container_width=True):
                    process_question("What is rent control?")
                if st.button("💡 Attach document to check compliance", key="ex6", use_container_width=True):
                    st.info("📎 Please use the file uploader below to attach a document, then ask 'Is this compliant?' or 'Check this document for compliance'")
    
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
                st.markdown(answer_content)
                
                # Show sources if available
                if 'sources' in message and message['sources']:
                    # Remove duplicates
                    seen_sources = set()
                    unique_sources = []
                    for source in message['sources']:
                        source_key = (source.get('url', ''), source.get('source', ''))
                        if source_key not in seen_sources:
                            seen_sources.add(source_key)
                            unique_sources.append(source)
                    
                    if unique_sources:
                        with st.expander("📚 Sources", expanded=False):
                            for source in unique_sources:
                                if source.get('url') and (source['url'].startswith('http') or os.path.exists(source['url'])):
                                    if source['url'].startswith('http'):
                                        st.markdown(f"🔗 [{source['source']}]({source['url']})")
                                    else:
                                        st.markdown(f"📄 {source['source']}")
    
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
                    
                    if result['sources'] and "Sources:" not in answer_text:
                        seen_sources = set()
                        unique_sources = []
                        for source in result['sources']:
                            source_key = (source.get('url', ''), source.get('source', ''))
                            if source_key not in seen_sources:
                                seen_sources.add(source_key)
                                unique_sources.append(source)
                        
                        if unique_sources:
                            answer_text += "\n\n**📚 Sources:**\n"
                            for source in unique_sources:
                                if source.get('url'):
                                    if source['url'].startswith('http'):
                                        answer_text += f"- 🔗 [{source['source']}]({source['url']})\n"
                                    elif os.path.exists(source['url']):
                                        answer_text += f"- 📄 {source['source']}\n"
                    
                    if "[Note:" in answer_text:
                        answer_text = answer_text.split("[Note:")[0].strip()
                    
                    st.markdown(answer_text)
                    
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
    
    if search_query:
        # Vector search
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
                    
                    # Issues with action items
                    if result['issues']:
                        st.subheader("Compliance Issues & Action Items")
                        for issue in result['issues']:
                            with st.expander(f"⚠️ Issue in Clause {issue['clause_number']}: {issue['clause_title'][:50]}"):
                                st.markdown(f"**Clause Content:**")
                                st.text(issue['clause_content'][:500])
                                st.markdown(f"**Regulation Applies:** {issue['regulation_applies']}")
                                st.markdown(f"**What's Missing:** {issue['whats_missing']}")
                                st.markdown(f"**What to Fix:** {issue['what_to_fix']}")
                                
                                # Show action items for this specific issue
                                st.markdown("---")
                                st.markdown("**📋 Action Items for This Issue:**")
                                if 'esa' in issue['what_to_fix'].lower() or 'emotional support' in issue['what_to_fix'].lower():
                                    st.markdown("""
                                    1. Remove pet fees/deposits for ESA animals
                                    2. Update lease document
                                    3. Post Fair Housing Act poster
                                    4. Train staff on ESA requirements
                                    5. Make ESA request forms available
                                    """)
                                elif 'fair housing' in issue['what_to_fix'].lower():
                                    st.markdown("""
                                    1. Update lease language per Fair Housing Act
                                    2. Post Fair Housing poster
                                    3. Update property management policies
                                    4. Train staff on Fair Housing requirements
                                    """)
                                else:
                                    st.markdown("""
                                    1. Review and update clause
                                    2. Update lease document
                                    3. Consult legal counsel if needed
                                    """)
                                
                                if issue['suggested_revision']:
                                    st.markdown("---")
                                    st.markdown(f"**Suggested Revision:**")
                                    st.code(issue['suggested_revision'])
                        
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
- View all regulation updates that have been detected
- See summaries of what changed in each regulation
- Filter updates by city (Dallas, Houston, Austin, San Antonio)
- Check when regulations were last updated
- Manually trigger an update check

**How to use:**
1. Click "Check for Updates Now" to scan for new changes
2. Use the filters to find updates for specific cities
3. Expand any update to see detailed summary and affected cities
    """)
    
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
    
    # Display recent updates
    st.subheader("Recent Updates")
    
    # Show count
    updates = st.session_state.db.get_recent_updates(limit=50)
    if updates:
        st.metric("Total Updates", len(updates))
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        city_filter = st.selectbox("Filter by City", ["All"] + SUPPORTED_CITIES, key="update_city_filter")
    with col2:
        show_count = st.slider("Show Updates", 1, 50, 10, key="update_count")
    
    # Apply filter
    filtered_updates = updates
    if city_filter != "All":
        filtered_updates = [
            u for u in updates 
            if city_filter in str(u.get('affected_cities', ''))
        ]
    
    if filtered_updates:
        st.markdown(f"**Showing {len(filtered_updates[:show_count])} of {len(filtered_updates)} updates**")
        for update in filtered_updates[:show_count]:
            affected_cities = eval(update.get('affected_cities', '[]')) if isinstance(update.get('affected_cities'), str) else update.get('affected_cities', [])
            with st.expander(f"📢 {update['source_name']} - {update['detected_at']}", expanded=False):
                st.markdown(f"**Category:** {update.get('category', 'N/A')}")
                if update.get('url') and update['url'].startswith('http'):
                    st.markdown(f"**URL:** [{update['url']}]({update['url']})")
                else:
                    st.markdown(f"**URL:** {update.get('url', 'N/A')}")
                st.markdown(f"**Affected Cities:** {', '.join(affected_cities) if affected_cities else 'Texas-Statewide'}")
                st.markdown("---")
                st.markdown("**Update Summary:**")
                st.write(update['update_summary'])
                
                # Show if email was sent
                st.markdown("---")
                st.info("📧 Email notifications saved to 'emails' folder (if SMTP not configured)")
    else:
        if city_filter != "All":
            st.warning(f"No updates found for {city_filter}. Try 'All' or check other cities.")
        else:
            st.info("No updates recorded yet. Click 'Check for Updates' on the Home page to scan for changes.")

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
- Load regulations from sources.csv file
- Re-index all regulations in the vector database
- Manage data sources and update system
- Configure daily scraping schedule

**How to use:**
1. Edit `sources.csv` to add/modify regulation sources
2. Click "Load Regulations from CSV" to import new sources
3. Use "Re-Index All Regulations" if you need to rebuild the search index
    """)
    
    st.subheader("Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Load Regulations from CSV"):
            try:
                with st.spinner("Loading regulations from CSV..."):
                    result = st.session_state.db.load_regulations_from_csv(SOURCES_FILE)
                    st.success(f"✅ Regulations loaded! ({result['loaded']} loaded, {result['skipped']} skipped)")
                    
                    # Automatically scrape and index new regulations
                    if result['loaded'] > 0:
                        st.info("🔄 Now scraping content and indexing in vector store...")
                        with st.spinner("Scraping and indexing regulations (this may take a few minutes)..."):
                            regulations = st.session_state.db.get_all_regulations()
                            indexed = 0
                            skipped_indexing = 0
                            
                            for reg in regulations:
                                # Check if already indexed (has content_hash means it was scraped)
                                if reg.get('content_hash'):
                                    continue  # Skip already indexed regulations
                                
                                url = reg.get('url', '')
                                if url and (url.startswith('http://') or url.startswith('https://') or url.startswith('file://') or os.path.exists(url)):
                                    try:
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
                            
                            if indexed > 0:
                                st.success(f"✅ Indexed {indexed} new regulation(s) in vector store!")
                            if skipped_indexing > 0:
                                st.warning(f"⚠️ Skipped {skipped_indexing} regulation(s) (could not fetch content)")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        if st.button("🔄 Re-Index All Regulations"):
            """Re-index all regulations (useful if vector store was cleared)"""
            with st.spinner("Re-indexing all regulations (this may take several minutes)..."):
                regulations = st.session_state.db.get_all_regulations()
                indexed = 0
                for reg in regulations:
                    url = reg.get('url', '')
                    if url and (url.startswith('http://') or url.startswith('https://') or url.startswith('file://') or os.path.exists(url)):
                        try:
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
                        except Exception as e:
                            continue
                st.success(f"✅ Re-indexed {indexed} regulations!")
        
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
        st.subheader("Configuration")
        st.info("""
        **OpenAI API Key**: Set in .env file or environment variable
        
        **Email Settings**: Configure SMTP in .env file for email alerts
        
        **Database**: SQLite database at regulations.db
        
        **Vector Store**: ChromaDB at ./chroma_db
        
        **Daily Scraper**: Run `python daily_scraper.py` to start daily updates
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
