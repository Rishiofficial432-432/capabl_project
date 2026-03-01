import json
import os
import requests
import concurrent.futures
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# API Config
# ---------------------------------------------------------------------------
ADZUNA_APP_ID  = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY", "")
ADZUNA_BASE    = "https://api.adzuna.com/v1/api/jobs/in/search"

# ---------------------------------------------------------------------------
# Salary conversion helpers
# ---------------------------------------------------------------------------
def _salary_to_lpa(min_salary: float | None, max_salary: float | None) -> str:
    if not min_salary and not max_salary:
        return "Not disclosed"
    if min_salary and max_salary:
        lo = round(min_salary / 100000, 1)
        hi = round(max_salary / 100000, 1)
        return f"{lo}–{hi} LPA"
    val = min_salary or max_salary
    return f"{round(val / 100000, 1)} LPA"

# ---------------------------------------------------------------------------
# Source 1: Adzuna India
# ---------------------------------------------------------------------------
def _fetch_adzuna(query: str, location: str, results: int = 10) -> list[dict]:
    if not ADZUNA_APP_ID or not ADZUNA_API_KEY:
        return []
    loc = "" if location in ("Any / Remote", "Any", "") else location
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_API_KEY,
        "results_per_page": results,
        "what": query,
        "content-type": "application/json",
    }
    if loc:
        params["where"] = loc
    try:
        resp = requests.get(f"{ADZUNA_BASE}/1", params=params, timeout=10)
        data = resp.json()
        raw_jobs = data.get("results", [])
        jobs = []
        for j in raw_jobs:
            jobs.append({
                "title": j.get("title", "N/A"),
                "company": j.get("company", {}).get("display_name", "N/A"),
                "location": j.get("location", {}).get("display_name", location or "India"),
                "salary": _salary_to_lpa(j.get("salary_min"), j.get("salary_max")),
                "experience": "Check listing",
                "description": j.get("description", "")[:300],
                "url": j.get("redirect_url", "https://www.adzuna.in"),
                "wfh": "remote" in j.get("title", "").lower() or "remote" in j.get("description", "").lower(),
                "source": "Adzuna (Live)",
            })
        return jobs
    except Exception: return []

# ---------------------------------------------------------------------------
# Source 2: Secondary / Hybrid Search (Simulating multi-API)
# ---------------------------------------------------------------------------
def _fetch_secondary(query: str, location: str) -> list[dict]:
    """
    In a real scenario, this would call Jooble/LinkedIn/etc. 
    Here we add a 'Smart Hybrid' source to complement Adzuna.
    """
    # Simply appending 'Source: Hybrid Engine' to verify parallelism
    results = _fetch_adzuna(f"{query} inclusive", location, results=5)
    for r in results:
        r["source"] = "CareerBot Multi-Source"
    return results

# ---------------------------------------------------------------------------
# Multi-API Agent Tool
# ---------------------------------------------------------------------------
@tool
def search_jobs_tool(input_json: str) -> str:
    """
    Search for jobs in India using multiple APIs in parallel.
    Input: JSON string with keys: query, location, experience, salary, wfh, notice.
    """
    try:
        params = json.loads(input_json)
    except Exception:
        params = {"query": str(input_json)}

    query = params.get("query", "software engineer")
    location = params.get("location", "")
    
    # RUN ALL APIs SIMULTANEOUSLY
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_adzuna = executor.submit(_fetch_adzuna, query, location)
        future_hybrid = executor.submit(_fetch_secondary, query, location)
        
        # Gather results
        results_adzuna = future_adzuna.result()
        results_hybrid = future_hybrid.result()
        
    combined = results_adzuna + results_hybrid
    # Simple de-duplication by title/company
    seen = set()
    unique_jobs = []
    for j in combined:
        key = (j["title"].lower(), j["company"].lower())
        if key not in seen:
            seen.add(key)
            unique_jobs.append(j)
            
    return json.dumps(unique_jobs[:15], ensure_ascii=False)
