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


def parse_resume(resume_text):

    prompt = f"""
You are an expert HR Resume Parser.

Extract candidate information.

Return ONLY JSON.

Schema:

{{
"candidate_name":"",
"email":"",
"phone":"",
"location":"",
"experience":"",
"education":[],
"technical_skills":[],
"soft_skills":[],
"projects":[],
"certifications":[],
"languages":[],
"linkedin":"",
"summary":""
}}

Resume:

{resume_text}
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    text = response.content.strip()

    text = text.replace("```json", "")
    text = text.replace("```", "")

    return json.loads(text)