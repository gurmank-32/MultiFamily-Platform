# Prompt Customization Guide

This guide explains how to fine-tune prompts for specific subjects and get in-depth answers for leasing/legal jargon.

## 📁 File Structure

- **`prompts_config.py`** - Main configuration file for custom prompts
- **`qa_system.py`** - Uses prompts from `prompts_config.py`
- **`compliance_checker.py`** - Uses prompts for compliance analysis

## 🎯 How to Customize Prompts

### 1. Adding Custom Subject Prompts

Edit `prompts_config.py` and add to `SUBJECT_PROMPTS` dictionary:

```python
SUBJECT_PROMPTS: Dict[str, str] = {
    "your_subject": """When explaining [subject], provide detailed information about:
- Point 1
- Point 2
- Point 3
- Examples and scenarios""",
}
```

**Example: Adding "eviction" subject**

```python
"eviction": """When explaining eviction, cover:
- Texas Property Code eviction procedures
- Notice requirements (3-day, 30-day, etc.)
- Grounds for eviction
- Tenant rights during eviction
- Court process
- Illegal eviction practices
- Tenant defenses"""
```

### 2. Customizing Legal Jargon Explanations

Edit `JARGON_EXPLANATION_PROMPT` in `prompts_config.py`:

```python
JARGON_EXPLANATION_PROMPT = """When explaining legal jargon, provide:
1. Simple Definition
2. Legal Context
3. Practical Application
4. Examples
5. Related Terms
6. Common Misconceptions"""
```

### 3. Adding Query Type Prompts

Edit `QUERY_TYPE_PROMPTS` in `prompts_config.py`:

```python
QUERY_TYPE_PROMPTS: Dict[str, str] = {
    "your_query_type": """You are answering a [type] question. Provide:
- Specific guidance
- Examples
- Action items"""
}
```

## 🔧 How It Works

### Automatic Detection

The system automatically detects:
- **Query Type**: definition, compliance, scenario, new_law
- **Subject**: esa, rent_control, security_deposit, fair_housing, late_fees

### Prompt Enhancement

When you ask a question:
1. System detects the subject and query type
2. Loads relevant custom prompts
3. Enhances the base prompt with subject-specific instructions
4. Generates a detailed, in-depth answer

## 📝 Examples

### Example 1: Adding "Lease Termination" Subject

```python
# In prompts_config.py
SUBJECT_PROMPTS["lease_termination"] = """When explaining lease termination, cover:
- Early termination clauses
- Breaking a lease legally
- Penalties and fees
- Notice requirements
- Tenant rights
- Landlord obligations
- Security deposit return upon termination"""
```

### Example 2: Customizing Jargon Explanation

```python
# In prompts_config.py
JARGON_EXPLANATION_PROMPT = """When explaining legal jargon:
1. Start with a simple, one-sentence definition
2. Provide the legal definition from relevant statutes
3. Explain in context of landlord-tenant relationships
4. Give 2-3 real-world examples
5. List related terms and concepts
6. Address common misunderstandings
7. Provide actionable guidance"""
```

### Example 3: Adding "Zoning" Query Type

```python
# In prompts_config.py
QUERY_TYPE_PROMPTS["zoning"] = """You are explaining zoning regulations. Include:
- Zoning classification
- Permitted uses
- Restrictions
- Variance process
- Impact on rental properties
- City-specific zoning rules"""
```

## 🚀 Using Custom Prompts

### Method 1: Direct Question (Automatic)

Just ask your question normally:
- "What does habitable mean?"
- "Explain ESA requirements in detail"
- "What is rent control?"

The system automatically:
- Detects the subject/query type
- Applies custom prompts
- Provides in-depth answer

### Method 2: Explicit Subject Mention

Mention the subject in your question:
- "Tell me about ESA in detail"
- "Explain security deposits thoroughly"
- "What does 'quiet enjoyment' mean in leasing?"

### Method 3: Query Type Keywords

Use keywords that trigger specific query types:
- **Definition**: "What is...", "What does... mean", "Define..."
- **Compliance**: "Is this compliant", "Does this violate", "Legal requirement"
- **Scenario**: "I have a tenant who...", "What if...", "Can I..."
- **New Law**: "New law", "Recent update", "Latest regulation"

## 📚 Current Custom Subjects

- ✅ **ESA** - Emotional Support Animals
- ✅ **Rent Control** - Rent control laws
- ✅ **Security Deposit** - Deposit regulations
- ✅ **Fair Housing** - Fair Housing Act
- ✅ **Late Fees** - Late fee regulations

## 🔍 Testing Your Custom Prompts

1. Add your custom prompt to `prompts_config.py`
2. Restart the Streamlit app
3. Ask a question related to your subject
4. Check if the answer includes all the points from your prompt

## 💡 Tips for Better Prompts

1. **Be Specific**: List exactly what information to include
2. **Use Examples**: Ask for examples in your prompt
3. **Structure**: Use numbered lists or bullet points
4. **Context**: Reference specific regulations or laws
5. **Action Items**: Ask for actionable guidance

## 🛠️ Advanced: Modifying System Prompts

Edit the main system prompts in `prompts_config.py`:

- `QA_SYSTEM_PROMPT` - Main Q&A system prompt
- `COMPLIANCE_ANALYSIS_PROMPT` - Compliance checker prompt

These affect all queries, so be careful with changes.

## 📖 Example: Complete Custom Subject

```python
# In prompts_config.py
SUBJECT_PROMPTS["habitability"] = """When explaining habitability, provide:

1. **Legal Definition**: 
   - Implied warranty of habitability
   - Texas Property Code requirements
   - Minimum standards

2. **What Makes a Unit Habitable**:
   - Working plumbing and electricity
   - Heating and cooling
   - Structural integrity
   - Safety features

3. **Landlord Obligations**:
   - Maintenance requirements
   - Repair timelines
   - Emergency repairs

4. **Tenant Rights**:
   - Right to repairs
   - Rent withholding (when legal)
   - Repair and deduct
   - Breaking lease for habitability issues

5. **Examples**:
   - Scenario 1: No hot water
   - Scenario 2: Broken heating
   - Scenario 3: Mold issues

6. **Common Issues**:
   - What landlords often get wrong
   - Tenant misconceptions
   - Legal remedies"""
```

Then ask: "What does habitability mean?" and get a comprehensive answer!

