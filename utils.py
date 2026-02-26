# utils.py
# Just some helpers and constants for the Indian job market
# Nothing fancy here, just keeping things organised

# Major Indian cities - metro first, then tier-2
METRO_CITIES = [
    "Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai",
    "Kolkata", "Pune", "Ahmedabad",
]

TIER2_CITIES = [
    "Noida", "Gurugram", "Navi Mumbai", "Thane", "Coimbatore",
    "Indore", "Jaipur", "Lucknow", "Bhopal", "Nagpur",
    "Chandigarh", "Kochi", "Visakhapatnam", "Surat", "Vadodara",
    "Tirupati", "Nashik", "Mysore", "Mangalore",
]

ALL_CITIES = ["Any / Remote"] + METRO_CITIES + sorted(TIER2_CITIES)

# Experience buckets - kept simple
EXPERIENCE_LEVELS = [
    "Fresher (0 yrs)",
    "1–2 years",
    "3–5 years",
    "5–8 years",
    "8+ years",
]

# Notice periods - very common in Indian companies
NOTICE_PERIODS = [
    "Immediate / No notice",
    "15 days",
    "1 month (30 days)",
    "2 months (60 days)",
    "3 months (90 days)",
]

# Salary ranges in LPA (Lakhs Per Annum)
# 1 LPA = Rs 1,00,000 per year
SALARY_RANGES = [
    "Any",
    "0–3 LPA",
    "3–6 LPA",
    "6–10 LPA",
    "10–15 LPA",
    "15–25 LPA",
    "25+ LPA",
]

# Popular job domains/roles in India
JOB_DOMAINS = [
    "Software Engineering",
    "Data Science / ML / AI",
    "Product Management",
    "DevOps / Cloud",
    "UI/UX Design",
    "Business Analyst",
    "Marketing / Digital Marketing",
    "Sales / Business Development",
    "HR / Talent Acquisition",
    "Finance / Accounts",
    "Operations",
    "Customer Support",
    "Fresher / Entry Level",
]


def format_salary_lpa(value_lpa):
    """Format a salary number as LPA string."""
    if value_lpa < 1:
        return f"₹{int(value_lpa * 100)}K per year"
    return f"₹{value_lpa:.1f} LPA"


def parse_salary_range(label):
    """Convert salary range label like '6–10 LPA' to (min, max) tuple."""
    if "Any" in label:
        return (0.0, 9999.0)
    if "25+" in label:
        return (25.0, 9999.0)
    clean = label.replace("LPA", "").replace("₹", "").strip()
    parts = clean.split("–")
    try:
        return (float(parts[0].strip()), float(parts[1].strip()))
    except Exception:
        return (0.0, 9999.0)


def experience_to_years(label):
    """Convert experience label to (min_years, max_years)."""
    if "Fresher" in label:
        return (0, 0)
    if "8+" in label:
        return (8, 30)
    try:
        parts = label.split("–") if "–" in label else label.split("-")
        lo = int(parts[0].strip().split()[0])
        hi = int(parts[1].strip().split()[0])
        return (lo, hi)
    except Exception:
        return (0, 30)


def truncate(text, max_len=180):
    """Trim long strings so they don't overflow cards."""
    if not text:
        return ""
    return text[:max_len] + "…" if len(text) > max_len else text
