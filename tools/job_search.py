"""
tools/job_search.py
====================
LangChain tool that searches for Indian jobs.

Strategy (in order):
  1. Adzuna Jobs API – real Indian job listings (primary, reliable)
  2. Fall back to a rich curated mock dataset for demo stability

Adzuna API docs: https://developer.adzuna.com/
India endpoint:  https://api.adzuna.com/v1/api/jobs/in/search/{page}

The tool accepts a JSON string with keys:
  - query       : job title / keywords
  - location    : city or "Any / Remote"
  - experience  : experience label
  - salary      : salary-range label (e.g. "6–10 LPA")
  - wfh         : "true" / "false"
  - notice      : notice period string
"""

import json
import os
import time
import requests
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Adzuna config
# ---------------------------------------------------------------------------
ADZUNA_APP_ID  = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY", "")
ADZUNA_BASE    = "https://api.adzuna.com/v1/api/jobs/in/search"

# ---------------------------------------------------------------------------
# Mock / fallback dataset (so the demo always has data)
# ---------------------------------------------------------------------------
_MOCK_JOBS = [
    {
        "title": "Software Engineer – Python",
        "company": "Infosys",
        "location": "Bangalore",
        "salary": "8–12 LPA",
        "experience": "2–4 years",
        "description": "Work on backend systems using Python, FastAPI, and PostgreSQL. Collaborate with cross-functional teams to build scalable microservices.",
        "url": "https://www.infosys.com/careers",
        "wfh": False,
        "notice": "30 days",
    },
    {
        "title": "Data Scientist",
        "company": "Wipro",
        "location": "Hyderabad",
        "salary": "10–16 LPA",
        "experience": "3–5 years",
        "description": "Build ML models for prediction and classification tasks using Python, Scikit-learn, and TensorFlow. Strong analytical skills required.",
        "url": "https://careers.wipro.com",
        "wfh": True,
        "notice": "60 days",
    },
    {
        "title": "Full Stack Developer (React + Node)",
        "company": "TCS",
        "location": "Mumbai",
        "salary": "7–11 LPA",
        "experience": "2–5 years",
        "description": "Develop and maintain web applications using React.js (frontend) and Node.js (backend). Experience with REST APIs required.",
        "url": "https://ibegin.tcs.com",
        "wfh": True,
        "notice": "30 days",
    },
    {
        "title": "DevOps Engineer",
        "company": "HCL Technologies",
        "location": "Noida",
        "salary": "9–14 LPA",
        "experience": "3–6 years",
        "description": "Manage CI/CD pipelines, Kubernetes clusters on AWS. Experience with Terraform and Ansible preferred.",
        "url": "https://www.hcltech.com/careers",
        "wfh": False,
        "notice": "45 days",
    },
    {
        "title": "UI/UX Designer",
        "company": "Swiggy",
        "location": "Bangalore",
        "salary": "12–18 LPA",
        "experience": "3–5 years",
        "description": "Design intuitive user interfaces for mobile and web apps. Proficiency in Figma and user research methodologies required.",
        "url": "https://careers.swiggy.com",
        "wfh": False,
        "notice": "Immediate",
    },
    {
        "title": "Product Manager",
        "company": "Razorpay",
        "location": "Bangalore",
        "salary": "20–35 LPA",
        "experience": "4–7 years",
        "description": "Lead product strategy for payments infrastructure. MBA or equivalent experience preferred. Strong stakeholder management skills.",
        "url": "https://razorpay.com/jobs",
        "wfh": True,
        "notice": "30 days",
    },
    {
        "title": "Business Analyst",
        "company": "Accenture",
        "location": "Pune",
        "salary": "6–10 LPA",
        "experience": "2–4 years",
        "description": "Gather and document business requirements, perform process analysis, and liaise between tech and business teams.",
        "url": "https://www.accenture.com/in-en/careers",
        "wfh": False,
        "notice": "60 days",
    },
    {
        "title": "Machine Learning Engineer",
        "company": "Flipkart",
        "location": "Bangalore",
        "salary": "18–30 LPA",
        "experience": "3–6 years",
        "description": "Build and deploy recommendation systems and search ranking models at scale. Strong Python + ML fundamentals required.",
        "url": "https://www.flipkartcareers.com",
        "wfh": False,
        "notice": "90 days",
    },
    {
        "title": "Cloud Architect (AWS/Azure)",
        "company": "Tech Mahindra",
        "location": "Hyderabad",
        "salary": "22–38 LPA",
        "experience": "7–12 years",
        "description": "Design multi-cloud solutions for enterprise clients. Certifications in AWS or Azure preferred.",
        "url": "https://careers.techmahindra.com",
        "wfh": True,
        "notice": "90 days",
    },
    {
        "title": "Android Developer (Kotlin)",
        "company": "Paytm",
        "location": "Noida",
        "salary": "10–16 LPA",
        "experience": "2–5 years",
        "description": "Develop feature-rich Android applications for fintech. Experience with Retrofit, Coroutines, and MVVM required.",
        "url": "https://paytm.com/careers",
        "wfh": False,
        "notice": "30 days",
    },
    {
        "title": "Fresher – Software Trainee",
        "company": "Cognizant",
        "location": "Chennai",
        "salary": "3.5–5 LPA",
        "experience": "Fresher",
        "description": "6-month training program for fresh graduates in Java, SQL, and Agile. B.E./B.Tech in CS/IT required.",
        "url": "https://careers.cognizant.com",
        "wfh": False,
        "notice": "Immediate",
    },
    {
        "title": "Digital Marketing Manager",
        "company": "Nykaa",
        "location": "Mumbai",
        "salary": "8–14 LPA",
        "experience": "3–6 years",
        "description": "Lead paid media campaigns (Google, Meta), SEO strategy, and influencer marketing. Strong analytical skills required.",
        "url": "https://careers.nykaa.com",
        "wfh": True,
        "notice": "30 days",
    },
    {
        "title": "HR Business Partner",
        "company": "Zomato",
        "location": "Gurugram",
        "salary": "9–15 LPA",
        "experience": "4–7 years",
        "description": "Partner with business leaders to implement HR strategies, manage talent pipelines, and drive employee engagement initiatives.",
        "url": "https://www.zomato.com/careers",
        "wfh": False,
        "notice": "45 days",
    },
    {
        "title": "Cybersecurity Analyst",
        "company": "Wipro",
        "location": "Pune",
        "salary": "8–13 LPA",
        "experience": "2–4 years",
        "description": "Monitor security events, conduct vulnerability assessments, and respond to incidents. CISSP or CEH certification preferred.",
        "url": "https://careers.wipro.com",
        "wfh": True,
        "notice": "60 days",
    },
    {
        "title": "Java Backend Developer",
        "company": "Capgemini",
        "location": "Bangalore",
        "salary": "6–10 LPA",
        "experience": "1–3 years",
        "description": "Develop RESTful APIs using Spring Boot and Java 11+. Experience with microservices and Docker is a plus.",
        "url": "https://www.capgemini.com/in-en/careers",
        "wfh": False,
        "notice": "30 days",
    },
]


# ---------------------------------------------------------------------------
# Salary conversion helpers (₹ → approximate LPA)
# ---------------------------------------------------------------------------
def _salary_to_lpa(min_salary: float | None, max_salary: float | None) -> str:
    """Convert Adzuna's annual INR salary to LPA string."""
    if not min_salary and not max_salary:
        return "Not disclosed"
    # Adzuna returns annual salary in INR
    # 1 LPA = 100,000 INR
    if min_salary and max_salary:
        lo = round(min_salary / 100000, 1)
        hi = round(max_salary / 100000, 1)
        return f"{lo}–{hi} LPA"
    val = min_salary or max_salary
    return f"{round(val / 100000, 1)} LPA"


# ---------------------------------------------------------------------------
# Adzuna live API
# ---------------------------------------------------------------------------
def _fetch_adzuna(query: str, location: str, results: int = 10) -> list[dict]:
    """
    Fetch live jobs from Adzuna India API.
    Returns [] on any error (network, auth, parsing).
    """
    if not ADZUNA_APP_ID or not ADZUNA_API_KEY:
        return []

    loc = "" if location in ("Any / Remote", "Any", "") else location

    params = {
        "app_id":          ADZUNA_APP_ID,
        "app_key":         ADZUNA_API_KEY,
        "results_per_page": results,
        "what":            query,
        "content-type":    "application/json",
    }
    if loc:
        params["where"] = loc

    try:
        resp = requests.get(
            f"{ADZUNA_BASE}/1",
            params=params,
            timeout=12,
        )
        resp.raise_for_status()
        data = resp.json()
        raw_jobs = data.get("results", [])

        jobs = []
        for j in raw_jobs:
            company = j.get("company", {}).get("display_name", "N/A")
            loc_data = j.get("location", {})
            loc_display = loc_data.get("display_name", location or "India")
            salary = _salary_to_lpa(
                j.get("salary_min"),
                j.get("salary_max"),
            )
            jobs.append({
                "title":       j.get("title", "N/A"),
                "company":     company,
                "location":    loc_display,
                "salary":      salary,
                "experience":  "Check listing",
                "description": j.get("description", "")[:300],
                "url":         j.get("redirect_url", "https://www.adzuna.in"),
                "wfh":         "remote" in j.get("title", "").lower()
                               or "remote" in j.get("description", "").lower(),
                "notice":      "Not specified",
                "source":      "Adzuna (Live)",
            })
        return jobs
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Mock fallback filter
# ---------------------------------------------------------------------------
def _filter_mock(query: str, location: str, wfh: bool | None) -> list[dict]:
    q = query.lower()
    results = []
    for job in _MOCK_JOBS:
        text = f"{job['title']} {job['description']}".lower()
        if q and not any(word in text for word in q.split()):
            continue
        if location and location not in ("Any / Remote", "Any"):
            if location.lower() not in job["location"].lower():
                continue
        if wfh is True and not job["wfh"]:
            continue
        results.append({**job, "source": "Demo Data"})
    return results[:8]


# ---------------------------------------------------------------------------
# LangChain tool
# ---------------------------------------------------------------------------
@tool
def search_jobs_tool(input_json: str) -> str:
    """
    Search for jobs in the Indian job market using the Adzuna API.
    Input must be a JSON string with keys:
      query (str), location (str), experience (str),
      salary (str), wfh (bool), notice (str).
    Returns a JSON list of matching jobs.
    """
    try:
        params = json.loads(input_json)
    except Exception:
        params = {"query": str(input_json)}

    query    = params.get("query", "software engineer")
    location = params.get("location", "")
    wfh      = params.get("wfh", None)
    if isinstance(wfh, str):
        wfh = wfh.lower() == "true"

    # If WFH requested, append "remote" to query
    search_query = query
    if wfh:
        search_query = f"{query} remote"

    # 1️⃣ Try Adzuna live API
    jobs = _fetch_adzuna(search_query, location)

    # 2️⃣ Fall back to mock data
    if not jobs:
        jobs = _filter_mock(query, location, wfh)

    # 3️⃣ Final fallback – return sample mock if nothing matched
    if not jobs:
        import random
        jobs = [{**j, "source": "Demo Data"} for j in random.sample(_MOCK_JOBS, min(6, len(_MOCK_JOBS)))]

    return json.dumps(jobs, ensure_ascii=False)
