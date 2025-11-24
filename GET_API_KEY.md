# How to Get Your OpenAI API Key

## Step-by-Step Instructions

### 1. Create an OpenAI Account (if you don't have one)
- Go to: https://platform.openai.com/
- Click "Sign Up" or "Log In"
- Use your email or Google/Microsoft account

### 2. Navigate to API Keys
- Once logged in, click on your profile icon (top right)
- Select "API keys" from the dropdown menu
- Or go directly to: https://platform.openai.com/api-keys

### 3. Create a New API Key
- Click the "+ Create new secret key" button
- Give it a name (e.g., "Housing Compliance Agent")
- Click "Create secret key"
- **IMPORTANT**: Copy the key immediately - you won't be able to see it again!

### 4. Add Credits to Your Account
- Go to: https://platform.openai.com/settings/organization/billing/overview
- Click "Add payment method" or "Add credits"
- Add at least $5-10 to start (you'll use credits as you use the API)
- The API is pay-as-you-go (very affordable for testing)

### 5. Pricing Information
- GPT-4 Turbo: ~$0.01 per 1K input tokens, ~$0.03 per 1K output tokens
- Embeddings (text-embedding-3-small): ~$0.00002 per 1K tokens
- For this app, expect to use a few dollars per month for regular use

### 6. Add the Key to Your Project
- Open the `.env` file in this project
- Replace `your_openai_api_key_here` with your actual key
- Save the file
- The format should be: `OPENAI_API_KEY=sk-...` (your key starts with "sk-")

## Alternative: Use a Different LLM Provider

If you prefer not to use OpenAI, you can modify the code to use:
- Anthropic Claude (via their API)
- Google Gemini
- Local models (requires more setup)

## Security Note
- Never share your API key publicly
- Don't commit the `.env` file to Git (it's already in .gitignore)
- If your key is exposed, revoke it immediately and create a new one

## Need Help?
- OpenAI Support: https://help.openai.com/
- API Documentation: https://platform.openai.com/docs
