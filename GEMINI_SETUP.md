# Google Gemini API Setup Guide

## Get Your Free Gemini API Key

1. **Visit Google AI Studio**
   - Go to: https://makersuite.google.com/app/apikey
   - Or: https://aistudio.google.com/apikey

2. **Sign in with your Google Account**
   - Use any Google account (Gmail, Workspace, etc.)

3. **Create API Key**
   - Click "Create API Key" button
   - Select "Create API key in new project" (or use existing project)
   - Copy your API key (starts with "AIza...")

4. **Add to Your Project**
   - Open `backend/.env` file
   - Replace `your_gemini_api_key_here` with your actual API key:
   ```
   GEMINI_API_KEY=AIzaSy...your_actual_key_here
   ```

5. **Save and Restart**
   - Save the `.env` file
   - The backend will automatically use Gemini for intelligent responses

## Free Tier Limits

- **60 requests per minute**
- **1,500 requests per day**
- **1 million tokens per minute**

Perfect for personal projects and testing!

## Features with Gemini

With Gemini enabled, the chatbot can:
- ✅ Understand complex natural language questions
- ✅ Provide contextual financial insights
- ✅ Automatically determine the best chart type
- ✅ Give more detailed and accurate responses
- ✅ Handle ambiguous queries intelligently

## Without Gemini

If you don't add an API key, the app still works with:
- Basic keyword matching
- Standard chart displays
- All core functionality

But responses will be simpler and less intelligent.

## Troubleshooting

**Error: "API key not valid"**
- Make sure you copied the entire key
- Check for extra spaces in the `.env` file
- Verify the key is active in Google AI Studio

**Error: "Quota exceeded"**
- You've hit the free tier limit
- Wait for the quota to reset (per minute/day)
- Or upgrade to a paid plan

## Security Note

⚠️ **Never commit your `.env` file to Git!**
- The `.env` file is already in `.gitignore`
- Keep your API key private
- Don't share it publicly
