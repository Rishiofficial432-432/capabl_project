"""
tools/company_info.py
======================
LangChain tool that returns basic information about Indian companies.

This tool queries the Gemini API to dynamically research and synthesize
insights for any requested company.
"""

import json
import os
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

# ---------------------------------------------------------------------------
# LangChain tool
# ---------------------------------------------------------------------------

@tool
def company_info_tool(company_name: str) -> str:
    """
    Get information about an Indian company including culture, salary,
    work-life balance, and interview process.
    Input: company name as a plain string.
    Returns: JSON with company details.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return json.dumps({"message": "API key not set. Please set the Gemini API Key to fetch live company info."})

    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, google_api_key=api_key)
        
        prompt = f"""
        Provide detailed information about the company '{company_name}' in the Indian job market.
        If it's a global company, focus on its Indian operations.
        
        Return pure JSON only (no markdown formatting, no code blocks, just raw JSON).
        The JSON should strictly follow this exact structure:
        {{
            "name": "Full Company Name",
            "type": "Industry/Sector",
            "hq": "Headquarters Location",
            "founded": "Year",
            "employees": "Approximate number of employees",
            "revenue": "Approx revenue or funding",
            "ceo": "CEO Name",
            "rating": "Glassdoor or Ambitionbox rating out of 5",
            "work_life": "Brief description of work-life balance",
            "salary_range": "Approx general salary ranges in LPA",
            "pros": ["Pro 1", "Pro 2", "Pro 3"],
            "cons": ["Con 1", "Con 2", "Con 3"],
            "interview": "Brief description of interview rounds",
            "notice_period": "Standard notice period",
            "wfh_policy": "Current WFH/Hybrid policy",
            "website": "Company career website URL"
        }}
        """
        
        response = llm.invoke(prompt)
        text_response = response.content.strip()
        
        # Clean up possible markdown code blocks if the model ignored instructions
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.startswith("```"):
            text_response = text_response[3:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
            
        data = json.loads(text_response.strip())
        return json.dumps(data, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps(
            {
                "message": (
                    f"Could not automatically research '{company_name}' right now. "
                    "However, you can check AmbitionBox (https://www.ambitionbox.com) or "
                    "Glassdoor for reviews, salary data, and interview tips for this company."
                )
            },
            ensure_ascii=False,
        )
