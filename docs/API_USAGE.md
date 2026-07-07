# API Usage

## AI Model

Google Gemini 2.5 Flash

---

## Purpose

The Gemini API is used for:

- Resume Parsing
- Candidate Information Extraction
- Resume and Job Description Matching
- AI Recommendation Generation

---

## Environment Variable

Create a `.env` file.

Example:

GOOGLE_API_KEY=YOUR_API_KEY

---

## Required Packages

google-generativeai

python-dotenv

---

## Note

The application requires an active Gemini API key with available quota.

If the quota is exceeded, AI analysis will not run until the quota resets or a new API key with available quota is used.