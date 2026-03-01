---
title: CareerBot
emoji: 🤖
colorFrom: purple
colorTo: indigo
sdk: docker
pinned: false
---

# CareerBot – AI Job Search Assistant (India) 🤖

An AI-powered job search tool built for the Indian market. Made with Streamlit + LangChain + Google Gemini as part of our college project (Track A, Week 1–2).

---

## What it does

- **Chat with an AI** to find jobs in India by city, experience, salary (LPA), WFH preference
- **Browse real job listings** pulled from the Adzuna API
- **Save jobs** you're interested in
- **Research companies** — salaries, culture, interview process for top Indian companies

---

## Screenshots

> Run it locally to see it in action!

---

## Getting Started

### Requirements
- Python 3.10+
- A free Google Gemini API key ([get one here](https://aistudio.google.com))
- Adzuna API credentials ([register here](https://developer.adzuna.com))

### Setup

```bash
git clone https://github.com/Rishiofficial432-432/capable_project.git
cd capable_project

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env and fill in your keys
```

### Run

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## Project structure

```
├── app.py              # Main Streamlit app
├── agent.py            # LangChain agent (Gemini + tools)
├── database.py         # SQLite for saved jobs & history
├── utils.py            # Indian market constants (cities, LPA, etc.)
├── tools/
│   ├── job_search.py   # Adzuna API integration
│   └── company_info.py # Company knowledge base (TCS, Infosys, etc.)
├── requirements.txt
└── .env.example
```

---

## Tech Stack

| What | How |
|------|-----|
| Frontend | Streamlit |
| AI Agent | LangChain + Google Gemini 1.5 Flash |
| Job Data | Adzuna Jobs API (India) |
| Database | SQLite |
| Web Scraping | BeautifulSoup4 (fallback) |

---

## Indian Market Features

- Salaries shown in **LPA** (Lakhs Per Annum)
- **Metro + Tier-2 city** filters (Bangalore, Mumbai, Hyderabad, Pune, Delhi, Noida…)
- **Notice period** filters (Immediate / 15 / 30 / 60 / 90 days)
- **WFH toggle** for remote job search
- Company database: TCS, Infosys, Wipro, Flipkart, Swiggy, Zomato, Razorpay, Paytm, HCL

---

## Week 1–2 Checklist

- [x] GitHub repo setup
- [x] LangChain agent with Gemini
- [x] Adzuna API integration for India
- [x] SQLite database (saved jobs + history)
- [x] Streamlit UI with filters
- [x] Company research tab
- [ ] Deploy to Streamlit Cloud *(coming soon)*

---

## Notes

- API keys go in `.env` — never committed to git
- Job data falls back to a curated mock dataset if API is unavailable
- Adzuna API returns salaries in INR, we convert to LPA format automatically

---

*Track A | Job Search AI Agent Project*
