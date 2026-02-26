"""
tools/company_info.py
======================
LangChain tool that returns basic information about Indian companies.

For demo purposes, we maintain a curated knowledge base of popular
Indian companies. For unknown companies the tool returns a helpful
"not found" message so the agent can still respond gracefully.
"""

import json
from langchain.tools import tool

# ---------------------------------------------------------------------------
# Curated company database (Indian IT & startup ecosystem)
# ---------------------------------------------------------------------------
_COMPANIES: dict[str, dict] = {
    "tcs": {
        "name": "Tata Consultancy Services (TCS)",
        "type": "IT Services & Consulting",
        "hq": "Mumbai",
        "founded": 1968,
        "employees": "600,000+",
        "revenue": "₹2.25 lakh crore (FY24)",
        "ceo": "K. Krithivasan",
        "rating": "3.8/5 (AmbitionBox)",
        "work_life": "Moderate – structured shifts, some flexibility for senior roles",
        "salary_range": "Fresher: 3.5–7 LPA | Senior: 12–25 LPA",
        "pros": ["Job security", "Global exposure", "Learning programs (TCS iON, Fresco Play)", "Brand value"],
        "cons": ["Slow appraisal cycles", "Large org bureaucracy", "Limited startup-style growth"],
        "interview": "2–3 rounds: Online test + TR + HR",
        "notice_period": "90 days (negotiable)",
        "wfh_policy": "Hybrid (role-dependent)",
        "website": "https://www.tcs.com",
    },
    "infosys": {
        "name": "Infosys",
        "type": "IT Services & Consulting",
        "hq": "Bangalore",
        "founded": 1981,
        "employees": "340,000+",
        "revenue": "₹1.57 lakh crore (FY24)",
        "ceo": "Salil Parekh",
        "rating": "3.7/5 (AmbitionBox)",
        "work_life": "Good – structured WLB with defined project timelines",
        "salary_range": "Fresher: 3.6–6.5 LPA | Senior: 12–30 LPA",
        "pros": ["Strong L&D (Infosys Springboard)", "Diverse projects", "Global locations"],
        "cons": ["Variable bench periods", "Appraisal linked to utilisation"],
        "interview": "3 rounds: InfyTQ + Technical + HR",
        "notice_period": "90 days",
        "wfh_policy": "Hybrid",
        "website": "https://www.infosys.com",
    },
    "wipro": {
        "name": "Wipro",
        "type": "IT Services & Consulting",
        "hq": "Bangalore",
        "founded": 1945,
        "employees": "240,000+",
        "revenue": "₹90,000 crore (FY24)",
        "ceo": "Srinivas Pallia",
        "rating": "3.6/5 (AmbitionBox)",
        "work_life": "Moderate",
        "salary_range": "Fresher: 3.5–6 LPA | Senior: 10–28 LPA",
        "pros": ["Diverse service portfolio", "Certification reimbursement", "Good HR support"],
        "cons": ["Frequent project changes", "Growth can be slow"],
        "interview": "3 rounds: NLTH + Technical + HR",
        "notice_period": "90 days",
        "wfh_policy": "Hybrid",
        "website": "https://www.wipro.com",
    },
    "flipkart": {
        "name": "Flipkart",
        "type": "E-commerce",
        "hq": "Bangalore",
        "founded": 2007,
        "employees": "50,000+",
        "revenue": "₹57,000 crore (FY23)",
        "ceo": "Kalyan Krishnamurthy",
        "rating": "3.9/5 (AmbitionBox)",
        "work_life": "Intense during sale seasons, otherwise good",
        "salary_range": "SDE1: 18–25 LPA | SDE2: 28–42 LPA",
        "pros": ["Competitive salaries", "Challenging engineering problems", "ESOPs"],
        "cons": ["High pressure during Big Billion Days", "Work-life balance during peak season"],
        "interview": "4–5 rounds: DSA + System Design + Behavioural + Leadership",
        "notice_period": "60 days",
        "wfh_policy": "Mostly in-office",
        "website": "https://www.flipkartcareers.com",
    },
    "swiggy": {
        "name": "Swiggy",
        "type": "Food Delivery / Quick Commerce",
        "hq": "Bangalore",
        "founded": 2014,
        "employees": "5,000+ (corporate)",
        "revenue": "₹11,247 crore (FY24)",
        "ceo": "Sriharsha Majety",
        "rating": "3.8/5 (AmbitionBox)",
        "work_life": "Fast-paced startup culture",
        "salary_range": "SDE1: 20–28 LPA | SDE2: 32–50 LPA",
        "pros": ["Great pay", "Ownership culture", "Fast career growth"],
        "cons": ["High pressure", "Uncertain market"],
        "interview": "4 rounds: Online coding + Technical + System Design + HR",
        "notice_period": "Immediate to 30 days",
        "wfh_policy": "Hybrid",
        "website": "https://careers.swiggy.com",
    },
    "zomato": {
        "name": "Zomato",
        "type": "Food Delivery / Fintech",
        "hq": "Gurugram",
        "founded": 2008,
        "employees": "3,500+ (corporate)",
        "revenue": "₹12,114 crore (FY24)",
        "ceo": "Deepinder Goyal",
        "rating": "3.7/5 (AmbitionBox)",
        "work_life": "Startup pace, demanding but rewarding",
        "salary_range": "SDE1: 18–25 LPA | PM: 25–45 LPA",
        "pros": ["High growth company", "ESOPs", "Young culture"],
        "cons": ["High attrition", "Pressure during peak times"],
        "interview": "3–4 rounds: Coding + Product/System Design + HR",
        "notice_period": "30–45 days",
        "wfh_policy": "In-office preferred",
        "website": "https://www.zomato.com/careers",
    },
    "razorpay": {
        "name": "Razorpay",
        "type": "Fintech / Payments",
        "hq": "Bangalore",
        "founded": 2014,
        "employees": "2,500+",
        "funding": "$741.5M | Unicorn",
        "ceo": "Harshil Mathur",
        "rating": "4.1/5 (AmbitionBox)",
        "work_life": "Excellent for a high-growth startup",
        "salary_range": "SDE1: 22–32 LPA | SDE2: 35–55 LPA",
        "pros": ["Top-tier salaries", "Fintech domain expertise", "Great culture"],
        "cons": ["Intense expectations", "Product pivots common"],
        "interview": "4–5 rounds: DSA + System Design + Product Sense + Culture Fit",
        "notice_period": "30 days",
        "wfh_policy": "Flexible / hybrid",
        "website": "https://razorpay.com/jobs",
    },
    "paytm": {
        "name": "Paytm (One 97 Communications)",
        "type": "Fintech / Super App",
        "hq": "Noida",
        "founded": 2010,
        "employees": "10,000+",
        "ceo": "Vijay Shekhar Sharma",
        "rating": "3.4/5 (AmbitionBox)",
        "work_life": "Can be intense, especially pre-launch periods",
        "salary_range": "SDE1: 12–20 LPA | Senior: 22–40 LPA",
        "pros": ["Scale exposure", "Fintech domain", "Diverse product portfolio"],
        "cons": ["Regulatory headwinds (RBI)", "Frequent reorgs"],
        "interview": "3 rounds: Coding + Technical + HR",
        "notice_period": "30–60 days",
        "wfh_policy": "Mostly in-office",
        "website": "https://paytm.com/careers",
    },
    "hcl": {
        "name": "HCL Technologies",
        "type": "IT Services",
        "hq": "Noida",
        "founded": 1976,
        "employees": "225,000+",
        "revenue": "₹1.09 lakh crore (FY24)",
        "ceo": "C Vijayakumar",
        "rating": "3.7/5 (AmbitionBox)",
        "work_life": "Good for IT services segment",
        "salary_range": "Fresher: 3.5–7 LPA | Senior: 14–30 LPA",
        "pros": ["Competitive hikes", "Strong product engineering division", "Global exposure"],
        "cons": ["Service side can be monotonous", "Rotation delays"],
        "interview": "2–3 rounds: Aptitude + Technical + HR",
        "notice_period": "90 days",
        "wfh_policy": "Hybrid",
        "website": "https://www.hcltech.com/careers",
    },
}


def _lookup(name: str) -> dict | None:
    key = name.lower().strip()
    # Direct match
    if key in _COMPANIES:
        return _COMPANIES[key]
    # Partial match
    for k, v in _COMPANIES.items():
        if k in key or key in k or key in v["name"].lower():
            return v
    return None


# ---------------------------------------------------------------------------
# LangChain tool
# ---------------------------------------------------------------------------

@tool
def company_info_tool(company_name: str) -> str:
    """
    Get information about an Indian company including culture, salary,
    work-life balance, and interview process.
    Input: company name as a plain string.
    Returns: JSON with company details or a helpful not-found message.
    """
    info = _lookup(company_name)
    if info:
        return json.dumps(info, ensure_ascii=False)
    return json.dumps(
        {
            "message": (
                f"Detailed data for '{company_name}' is not in our curated database. "
                "However, you can check AmbitionBox (https://www.ambitionbox.com) or "
                "Glassdoor for reviews, salary data, and interview tips for this company."
            )
        },
        ensure_ascii=False,
    )
