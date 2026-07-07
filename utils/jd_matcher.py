import os
import json

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)


def match_resume_with_jd(resume_text, jd_text):

    prompt = f"""
You are an expert Technical Recruiter.

Compare the following resume with the job description.

Return ONLY valid JSON.

Schema:

{{
    "match_score": 0,
    "matching_skills": [],
    "missing_skills": [],
    "strengths": [],
    "weaknesses": [],
    "recommendation": ""
}}

Resume:
{resume_text}

Job Description:
{jd_text}
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    text = response.content.strip()

    text = text.replace("```json", "")
    text = text.replace("```", "")

    return json.loads(text)