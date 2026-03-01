"""
tools/market_trends.py
=======================
LangChain tool that provides insights into Indian hiring trends.
Uses Gemini to synthesize market data for specific regions.
"""

import json
import os
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

@tool
def market_trends_tool(region: str) -> str:
    """
    Get current hiring trends, popular roles, and demand insights for a specific 
    region in India (e.g., Bangalore, Pune, Delhi/NCR).
    Input: region name as a string.
    Returns: A summary of hiring trends.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "API key not set. Please configure Gemini to get market trends."

    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.4, google_api_key=api_key)
        
        prompt = f"""
        Provide a concise analysis of the current hiring trends in the '{region}' job market for India.
        Include:
        1. Top 3 in-demand roles.
        2. Average salary growth sentiment.
        3. Key industries hiring right now.
        4. A 'CareerBot Insight' – a small tip for candidates in this region.
        
        Keep the tone professional, data-driven, and encouraging. 
        Return the result as a well-formatted string.
        """
        
        response = llm.invoke(prompt)
        return response.content.strip()
        
    except Exception as e:
        return f"Could not fetch trends for {region} at this time. Focus on upskilling in GenAI and Cloud for better prospects."
