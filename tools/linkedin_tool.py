"""
LangChain tool that retrieves and parses LinkedIn profile data using RapidAPI's LinkedIn Data API.
"""

import os
import json
import requests
from langchain.tools import tool

@tool
def linkedin_profile_tool(linkedin_url: str) -> str:
    """
    Given a LinkedIn Profile URL, this tool returns the person's professional history,
    skills, education, and summary as a JSON string.
    
    Example input: "https://www.linkedin.com/in/williamhgates"
    """
    api_key = os.getenv("RAPIDAPI_KEY", "")
    if not api_key:
        return json.dumps({
            "error": "RAPIDAPI_KEY is not configured in the environment variables. "
                     "Please add it to the Hugging Face Space Secrets or local .env file."
        })

    # The RapidAPI endpoint for fetching a person's profile
    api_endpoint = 'https://linkedin-data-api.p.rapidapi.com/get-profile-data-by-url'
    
    headers = {
        'x-rapidapi-host': 'linkedin-data-api.p.rapidapi.com',
        'x-rapidapi-key': api_key
    }
    
    params = {
        'url': linkedin_url
    }

    try:
        response = requests.get(api_endpoint, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # The API might encapsulate the data under a distinct key. Try to flatten.
            # Assuming the standard structure for this specific rapidapi provider.
            
            profile_summary = {
                "full_name": data.get("firstName", "") + " " + data.get("lastName", ""),
                "headline": data.get("headline"),
                "summary": data.get("summary"),
                "location": data.get("locationName"),
                "experiences": [],
                "education": [],
            }
            
            # Extract up to top 3 experiences
            for exp in data.get("experience", [])[:3]:
                profile_summary["experiences"].append({
                    "companyName": exp.get("companyName"),
                    "title": exp.get("title"),
                    "duration": exp.get("timePeriod"),
                    "description": exp.get("description"),
                })
                
            # Extract up to top 3 education
            for edu in data.get("education", [])[:3]:
                profile_summary["education"].append({
                    "schoolName": edu.get("schoolName"),
                    "degreeName": edu.get("degreeName"),
                    "fieldOfStudy": edu.get("fieldOfStudy"),
                })
                
            return json.dumps(profile_summary, indent=2)
            
        elif response.status_code == 404:
            return json.dumps({"error": "Profile not found or is private."})
        elif response.status_code in [401, 403]:
            return json.dumps({"error": "RapidAPI Key is invalid, unauthorized, or quota exceeded."})
        else:
            return json.dumps({"error": f"API returned status code: {response.status_code}", "message": response.text[:200]})
            
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Failed to connect to LinkedIn extraction service: {str(e)}"})
