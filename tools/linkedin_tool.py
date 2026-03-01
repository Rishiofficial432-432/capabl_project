"""
LangChain tool that retrieves and parses LinkedIn profile data using the Proxycurl API.
"""

import os
from typing import Optional
import json

from langchain.tools import tool
import requests


@tool
def linkedin_profile_tool(linkedin_url: str) -> str:
    """
    Given a LinkedIn Profile URL, this tool returns the person's professional history,
    skills, education, and summary as a JSON string. Uses the Proxycurl API.
    
    Example input: "https://www.linkedin.com/in/williamhgates"
    """
    api_key = os.getenv("PROXYCURL_API_KEY", "")
    if not api_key:
        return json.dumps({
            "error": "PROXYCURL_API_KEY is not configured in the environment variables. "
                     "Please add it to the Hugging Face Space Secrets or local .env file."
        })

    api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
    headers = {'Authorization': f'Bearer {api_key}'}
    params = {
        'url': linkedin_url,
        'fallback_to_cache': 'on-error',
        'use_cache': 'if-present',
        'skills': 'include',
    }

    try:
        response = requests.get(api_endpoint, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            # Extract and clean up only the most relevant fields to avoid overwhelming the LLM
            profile_summary = {
                "full_name": data.get("full_name"),
                "headline": data.get("headline"),
                "summary": data.get("summary"),
                "city": data.get("city"),
                "country": data.get("country"),
                "experiences": [],
                "education": [],
                "skills": data.get("skills", []),
            }
            
            # Limit experiences and education to last 3 entries to save token space
            for exp in data.get("experiences", [])[:3]:
                profile_summary["experiences"].append({
                    "company": exp.get("company"),
                    "title": exp.get("title"),
                    "starts_at": exp.get("starts_at"),
                    "ends_at": exp.get("ends_at"),
                    "description": exp.get("description"),
                })
                
            for edu in data.get("education", [])[:3]:
                profile_summary["education"].append({
                    "school": edu.get("school"),
                    "degree_name": edu.get("degree_name"),
                    "field_of_study": edu.get("field_of_study"),
                })
                
            return json.dumps(profile_summary, indent=2)
            
        elif response.status_code == 404:
            return json.dumps({"error": "Profile not found or is private."})
        elif response.status_code == 401 or response.status_code == 403:
            return json.dumps({"error": "Proxycurl API Key is invalid or unauthorized."})
        else:
            return json.dumps({"error": f"API returned status code: {response.status_code}"})
            
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Failed to connect to LinkedIn extraction service: {str(e)}"})
