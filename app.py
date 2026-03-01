"""
app.py – Main Streamlit application
=====================================
CareerBot: AI-powered Indian Job Search Assistant
Track A | Week 1-2 Milestone
"""

import json
import os
import asyncio
import streamlit as st
from dotenv import load_dotenv

import database as db
from utils import (
    ALL_CITIES, EXPERIENCE_LEVELS, NOTICE_PERIODS,
    SALARY_RANGES, JOB_DOMAINS, truncate,
)

load_dotenv()

# ---------------------------------------------------------------------------
# Page config (MUST be first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="CareerBot – AI Job Search for India",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS – modern dark-themed UI
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --primary: #ffffff;
    --primary-glow: rgba(255, 255, 255, 0.2);
    --secondary: #cccccc;
    --accent: #ffffff;
    --bg-dark: #000000;
    --card-bg: #0a0a0a;
    --card-border: #1a1a1a;
    --text-main: #ffffff;
    --text-muted: #888888;
}

html, body, [class*="css"], .stApp {
    font-family: 'Outfit', 'Inter', sans-serif;
    background-color: #000000 !important;
    background-image: none !important;
    color: var(--text-main);
}

/* Glassmorphism containers */
[data-testid="stSidebar"] {
    background-color: #050505 !important;
    border-right: 1px solid var(--card-border);
}

/* Header Aesthetics */
.main-header {
    text-align: center;
    padding: 2.5rem 0 1.5rem;
    animation: fadeInDown 0.8s ease-out;
}
.main-header h1 {
    font-size: 3.5rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #ffffff;
    margin-bottom: 0.5rem;
}
.main-header p {
    color: var(--text-muted);
    font-size: 1.1rem;
    font-weight: 400;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Premium Job Card */
.job-card {
    background-color: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    transition: all 0.3s ease;
}
.job-card:hover {
    transform: translateY(-2px);
    border-color: #333333;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
}
.job-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.company-name {
    color: var(--text-muted);
    font-weight: 500;
    font-size: 1rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.job-meta {
    font-size: 0.9rem;
    color: #aaaaaa;
    display: flex;
    gap: 1.2rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px dashed var(--card-border);
}
.job-apply-btn {
    display: inline-block;
    background-color: #ffffff;
    color: #000000 !important;
    padding: 0.6rem 1.5rem;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.9rem;
    transition: all 0.3s ease;
}
.job-apply-btn:hover {
    background-color: #cccccc;
    transform: scale(1.02);
}

/* Badges */
.badge {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 0.3rem 0.8rem;
    font-size: 0.85rem;
    font-weight: 500;
    color: #f1f5f9;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
}
.badge-green  { background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.3); color: #34d399; }
.badge-blue   { background: rgba(59, 130, 246, 0.1); border-color: rgba(59, 130, 246, 0.3); color: #60a5fa; }
.badge-purple { background: rgba(139, 92, 246, 0.1); border-color: rgba(139, 92, 246, 0.3); color: #a78bfa; }

/* Premium Chat */
.chat-user {
    background-color: #1a1a1a;
    border-radius: 20px 20px 4px 20px;
    padding: 1rem 1.25rem;
    margin: 0.75rem 0;
    max-width: 80%;
    margin-left: auto;
    color: white;
    border: 1px solid #333333;
    font-size: 0.95rem;
    line-height: 1.5;
    animation: slideInRight 0.4s ease-out;
}
.chat-bot {
    background-color: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 20px 20px 20px 4px;
    padding: 1rem 1.25rem;
    margin: 0.75rem 0;
    max-width: 85%;
    color: var(--text-main);
    font-size: 0.95rem;
    line-height: 1.6;
    animation: slideInLeft 0.4s ease-out;
}

.metric-box {
    background-color: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
}
.metric-box:hover {
    border-color: #444444;
}
.metric-box .metric-val {
    font-size: 2.2rem;
    font-weight: 800;
    color: #ffffff;
}

/* UI Elements */
.stButton > button {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: none !important;
    padding: 0.6rem 2rem !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    background-color: #cccccc !important;
    color: #000000 !important;
}

/* Animations */
@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes slideInRight {
    from { opacity: 0; transform: translateX(30px); }
    to { opacity: 1; transform: translateX(0); }
}
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to { opacity: 1; transform: translateX(0); }
}

/* Hide Streamlit components */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* Custom Scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background-color: #000000; }
::-webkit-scrollbar-thumb { 
    background-color: #333333;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent_executor" not in st.session_state:
        st.session_state.agent_executor = None
    if "agent_memory" not in st.session_state:
        st.session_state.agent_memory = None
    if "current_jobs" not in st.session_state:
        st.session_state.current_jobs = []
    if "api_key_set" not in st.session_state:
        st.session_state.api_key_set = bool(os.getenv("GOOGLE_API_KEY"))

init_session()

# ---------------------------------------------------------------------------
# Load agent (cached per session)
# ---------------------------------------------------------------------------
def load_agent():
    if st.session_state.agent_executor is None:
        try:
            from agent import build_agent
            exec_, mem = build_agent(st.session_state.agent_memory)
            st.session_state.agent_executor = exec_
            st.session_state.agent_memory = mem
        except EnvironmentError as e:
            return str(e)
        except Exception as e:
            return f"Failed to load agent: {e}"
    return None

# ---------------------------------------------------------------------------
# Render a job card (HTML)
# ---------------------------------------------------------------------------
def render_job_card(job: dict, idx: int):
    wfh_badge = '<span class="badge badge-green">🏠 WFH</span>' if job.get("wfh") else ""
    salary = job.get("salary", "Not disclosed")
    if salary and "LPA" not in salary.upper() and salary != "Not disclosed":
        salary_disp = salary
    else:
        salary_disp = salary

    card_html = f"""
    <div class="job-card">
        <div class="job-title">{job.get('title', 'N/A')}</div>
        <div class="job-company">🏢 {job.get('company', 'N/A')}</div>
        <div class="job-meta">
            <span class="badge badge-blue">📍 {job.get('location', 'N/A')}</span>
            <span class="badge badge-purple">💰 {salary_disp}</span>
            <span class="badge">🕒 {job.get('experience', 'N/A')}</span>
            {wfh_badge}
        </div>
        <div style="color:var(--text-muted); font-size:0.9rem; margin-top:1rem; line-height:1.5;">
            {truncate(job.get('description', ''), 200)}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    col_a, col_b, _ = st.columns([1, 1, 4])
    with col_a:
        if st.button("💾 Save", key=f"save_{idx}_{job.get('title','')}"):
            ok = db.save_job(job)
            st.toast("✅ Job saved!" if ok else "⚠️ Already saved or error.")
    with col_b:
        st.link_button("🔗 Apply", url=job.get("url", "#"))

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🤖 CareerBot")
        st.markdown("*AI Job Search · Indian Market*")
        st.divider()

        # API Key section
        st.markdown("### 🔑 API Key")
        if not st.session_state.api_key_set:
            api_key_input = st.text_input(
                "Google Gemini API Key",
                type="password",
                placeholder="AIzaSy...",
                help="Get free key at aistudio.google.com",
            )
            if api_key_input:
                os.environ["GOOGLE_API_KEY"] = api_key_input
                st.session_state.api_key_set = True
                st.session_state.agent_executor = None  # reset to rebuild
                st.success("✅ Key set!")
                st.rerun()
            st.caption("[Get free Gemini API key →](https://aistudio.google.com)")
        else:
            st.success("✅ API key configured")
            if st.button("🔄 Change key"):
                os.environ["GOOGLE_API_KEY"] = ""
                st.session_state.api_key_set = False
                st.session_state.agent_executor = None
                st.rerun()

        st.divider()

        # Search Filters
        st.markdown("### 🔍 Search Filters")
        st.caption("These filters are sent to the agent automatically.")

        location = st.selectbox("📍 Location", ALL_CITIES, index=0)
        experience = st.selectbox("🎓 Experience", EXPERIENCE_LEVELS, index=0)
        salary = st.selectbox("💰 Salary Range", SALARY_RANGES, index=0)
        domain = st.selectbox("💼 Domain / Role", ["Any"] + JOB_DOMAINS, index=0)
        wfh = st.checkbox("🏠 Work From Home only", value=False)
        notice = st.selectbox("📅 Max Notice Period", ["Any"] + NOTICE_PERIODS, index=0)

        st.divider()

        # Quick action buttons
        st.markdown("### ⚡ Quick Searches")
        quick_searches = [
            "Python developer jobs in Bangalore",
            "Data Science jobs 10+ LPA",
            "Fresher IT jobs Mumbai",
            "WFH jobs 6–10 LPA",
            "Product Manager Bengaluru",
        ]
        for qs in quick_searches:
            if st.button(qs, use_container_width=True, key=f"qs_{qs}"):
                st.session_state["_quick_query"] = qs

        st.divider()
        st.markdown("### 📊 Your Activity")
        saved = db.get_saved_jobs()
        history = db.get_search_history(5)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f'<div class="metric-box"><div class="metric-val">{len(saved)}</div>'
                f'<div class="metric-label">Saved</div></div>',
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f'<div class="metric-box"><div class="metric-val">{len(history)}</div>'
                f'<div class="metric-label">History</div></div>',
                unsafe_allow_html=True,
            )

    return {
        "location": location,
        "experience": experience,
        "salary": salary,
        "domain": domain,
        "wfh": wfh,
        "notice": notice,
    }

# ---------------------------------------------------------------------------
# Build enriched query from filters
# ---------------------------------------------------------------------------
def build_query(user_input: str, filters: dict) -> str:
    parts = [user_input]
    if filters["location"] != "Any / Remote":
        parts.append(f"in {filters['location']}")
    if filters["experience"] != "Fresher (0 yrs)":
        parts.append(f"with {filters['experience']} experience")
    if filters["salary"] != "Any":
        parts.append(f"paying {filters['salary']}")
    if filters["wfh"]:
        parts.append("work from home")
    if filters["domain"] != "Any":
        parts.append(f"in {filters['domain']} domain")
    return " ".join(parts)

# ---------------------------------------------------------------------------
# Tab: Chat
# ---------------------------------------------------------------------------
def tab_chat(filters: dict):
    st.markdown(
        '<div class="main-header"><h1>🤖 CareerBot</h1>'
        '<p>Your AI-powered Indian Job Search Assistant</p></div>',
        unsafe_allow_html=True,
    )
    st.divider()

    # Check API key
    if not st.session_state.api_key_set:
        st.warning("⚠️ Please enter your **Google Gemini API key** in the sidebar to start chatting.")
        st.info("Get a **free** Gemini API key at [aistudio.google.com](https://aistudio.google.com)")
        return

    # Load agent
    err = load_agent()
    if err:
        st.error(f"❌ {err}")
        return

    # Render chat history
    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            st.markdown(
                '<div class="chat-bot">🚀 <strong>Welcome to CareerBot!</strong><br><br>'
                'I\'m your high-performance AI recruiter dedicated to the <strong>Indian market</strong>. How can I help you level up today?<br><br>'
                '• <strong>Smart Search:</strong> Find roles by city, CTC (LPA), or WFH.<br>'
                '• <strong>Company Intel:</strong> Get the inside scoop on culture & rounds.<br>'
                '• <strong>Strategic Advice:</strong> Tailored tips for the Indian landscape.<br><br>'
                '<em>Try: "Find Senior React roles in Bangalore with 5+ years experience"</em></div>',
                unsafe_allow_html=True,
            )
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="chat-user">🧑 {msg["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="chat-bot">🤖 {msg["content"]}</div>',
                    unsafe_allow_html=True,
                )

    # Handle quick search buttons from sidebar
    quick_query = st.session_state.pop("_quick_query", None)

    # Chat input
    user_input = st.chat_input("Ask about jobs, companies, salaries in India…") or quick_query
    if user_input:
        # Enrich with sidebar filters
        full_query = build_query(user_input, filters)

        # Show user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("🔍 Searching the Indian job market…"):
            from agent import ask_agent_async
            response = asyncio.run(ask_agent_async(st.session_state.agent_executor, full_query, st.session_state.messages))

        st.session_state.messages.append({"role": "assistant", "content": response})

        # Log search
        db.log_search(user_input, filters)

        # Try to parse job results from agent response if JSON is embedded
        # (Agent sometimes returns raw JSON from tool output)
        try:
            if "[{" in response:
                start = response.index("[{")
                end = response.rindex("}]") + 2
                jobs_json = response[start:end]
                st.session_state.current_jobs = json.loads(jobs_json)
            else:
                st.session_state.current_jobs = []
        except Exception:
            st.session_state.current_jobs = []

        st.rerun()

# ---------------------------------------------------------------------------
# Tab: Job Listings (direct search, no agent overhead)
# ---------------------------------------------------------------------------
def tab_jobs(filters: dict):
    st.markdown("## 💼 Browse Job Listings")
    st.caption("Parallel AI Search across multiple APIs (Adzuna + Jooble Aggregator) for max coverage.")

    col_q, col_btn = st.columns([4, 1])
    with col_q:
        keyword = st.text_input(
            "Search keywords",
            placeholder="e.g. Python, Data Scientist, Product Manager",
            label_visibility="collapsed",
        )
    with col_btn:
        search_clicked = st.button("🔍 Search", use_container_width=True)

    if search_clicked or keyword:
        # Load agent if not loaded
        err = load_agent()
        if err:
            st.error(f"❌ {err}")
            return

        query_payload = json.dumps({
            "query": keyword or "software engineer",
            "location": filters["location"],
            "experience": filters["experience"],
            "salary": filters["salary"],
            "wfh": filters["wfh"],
        })
        
        agent_query = f"I am using the Job Listings tab. Please find jobs with these exact parameters and return the results as JSON: {query_payload}"

        with st.spinner("Agent is searching the market…"):
            from agent import ask_agent_async
            response = asyncio.run(ask_agent_async(st.session_state.agent_executor, agent_query))

        try:
            # Try to extract JSON from agent response
            if "[{" in response:
                start = response.index("[{")
                end = response.rindex("}]") + 2
                jobs_json = response[start:end]
                jobs = json.loads(jobs_json)
            else:
                jobs = []
        except Exception:
            jobs = []

        if not jobs:
            st.info("CareerBot couldn't find matches for those specifics. Try broader keywords.")
            if response:
                with st.expander("Agent Reasoning"):
                    st.write(response)
            return

        st.markdown(f"### Found **{len(jobs)}** matching jobs")
        st.divider()
        for i, job in enumerate(jobs):
            render_job_card(job, i)

        # Log
        db.log_search(keyword, filters, len(jobs))

    else:
        st.markdown("### 🔥 Trending Indian Job Listings")
        st.caption("AI Agent is fetching live trending data dynamically...")
        
        # Load agent if not loaded
        err = load_agent()
        if err: return

        agent_query = "Fetch 6 high-quality 'Software Engineer' jobs in India as JSON."
        
        with st.spinner("Agent is fetching featured jobs…"):
            from agent import ask_agent_async
            response = asyncio.run(ask_agent_async(st.session_state.agent_executor, agent_query))
            
        try:
            if "[{" in response:
                start = response.index("[{")
                end = response.rindex("}]") + 2
                jobs = json.loads(response[start:end])
            else:
                jobs = []
        except Exception:
            jobs = []
            
        for i, job in enumerate(jobs[:6]):
            render_job_card(job, i)
        
        if not jobs:
            st.info("No jobs found for this exact query. Try a different search above, or wait a minute if you just hit the API speed limit!")

# ---------------------------------------------------------------------------
# Tab: Saved Jobs
# ---------------------------------------------------------------------------
def tab_saved():
    st.markdown("## 💾 Saved Jobs")

    saved = db.get_saved_jobs()
    if not saved:
        st.info("📭 No saved jobs yet. Browse the **Job Listings** tab and click **Save** to bookmark jobs.")
        return

    st.markdown(f"You have saved **{len(saved)}** jobs.")
    st.divider()
    for job in saved:
        with st.expander(f"📌 {job['title']} @ {job['company']}", expanded=False):
            col1, col2, col3 = st.columns(3)
            col1.metric("Location", job.get("location", "N/A"))
            col2.metric("Salary", job.get("salary", "N/A"))
            col3.metric("Experience", job.get("experience", "N/A"))
            if job.get("description"):
                st.caption(truncate(job["description"], 300))
            if job.get("url"):
                st.link_button("🔗 Apply Now", url=job["url"])

            if st.button("🗑️ Remove", key=f"del_{job['id']}"):
                db.delete_saved_job(job["id"])
                st.success("Removed.")
                st.rerun()

# ---------------------------------------------------------------------------
# Tab: Company Research
# ---------------------------------------------------------------------------
def tab_company():
    st.markdown("## 🏢 Company Research")
    st.caption("AI-powered deep research into Indian companies – culture, salaries, and interview tips.")

    selected = st.text_input("Enter a company name (e.g., TCS, Flipkart, Zerodha)")

    if selected:
        # Load agent if not loaded
        err = load_agent()
        if err:
            st.error(f"❌ {err}")
            return

        agent_query = f"Research the company '{selected}' in the Indian market and return the full details as JSON."

        with st.spinner(f"Agent is researching {selected}…"):
            from agent import ask_agent_async
            response = asyncio.run(ask_agent_async(st.session_state.agent_executor, agent_query))
            
        try:
            # Extract JSON from agent response
            if "{" in response:
                start = response.index("{")
                end = response.rindex("}") + 1
                info_json = response[start:end]
                info = json.loads(info_json)
            else:
                info = {"message": "CareerBot couldn't find structured data for this company."}
        except Exception:
            info = {"message": "Error parsing company data from agent reasoning."}

        if "message" in info:
            st.warning(info["message"])
            with st.expander("Agent Reasoning"):
                st.write(response)
            return

        st.markdown(f"### {info.get('name', selected)}")
        st.caption(f"{info.get('type', '')} · Founded {info.get('founded', 'N/A')} · HQ: {info.get('hq', 'N/A')}")
        st.divider()

        cols = st.columns(4)
        with cols[0]:
            st.markdown(f'<div class="metric-box"><div class="metric-val" style="font-size:1.2rem;">{info.get("employees", "N/A")}</div><div class="metric-label">Employees</div></div>', unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f'<div class="metric-box"><div class="metric-val" style="font-size:1.2rem;">{info.get("revenue", info.get("funding", "N/A"))}</div><div class="metric-label">Revenue/Funding</div></div>', unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f'<div class="metric-box"><div class="metric-val" style="font-size:1.2rem;">{info.get("rating", "N/A")} ★</div><div class="metric-label">Rating</div></div>', unsafe_allow_html=True)
        with cols[3]:
            st.markdown(f'<div class="metric-box"><div class="metric-val" style="font-size:1.2rem;">{info.get("ceo", "N/A")}</div><div class="metric-label">CEO</div></div>', unsafe_allow_html=True)

        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### 💰 Salary Range")
            st.info(info.get("salary_range", "N/A"))
            st.markdown("#### ⏰ Notice Period")
            st.write(info.get("notice_period", "N/A"))
            st.markdown("#### 🏠 WFH Policy")
            st.write(info.get("wfh_policy", "N/A"))
        with col_b:
            st.markdown("#### ✅ Pros")
            for p in info.get("pros", []):
                st.success(f"✓ {p}")
            st.markdown("#### ⚠️ Cons")
            for c in info.get("cons", []):
                st.warning(f"• {c}")

        st.divider()
        st.markdown("#### 🎯 Interview Process")
        st.write(info.get("interview", "N/A"))
        st.markdown("#### ⚖️ Work-Life Balance")
        st.write(info.get("work_life", "N/A"))
        if info.get("website"):
            st.link_button("🌐 Visit Careers Page", url=info["website"])

# ---------------------------------------------------------------------------
# Tab: LinkedIn Profile Analyzer
# ---------------------------------------------------------------------------
def tab_linkedin():
    st.markdown("## 👤 LinkedIn Profile Analyzer")
    st.caption("AI-powered summary of any LinkedIn profile using RapidAPI's extractor tool.")

    selected_url = st.text_input("Enter a LinkedIn Profile URL (e.g., https://www.linkedin.com/in/satyanadella)")

    if selected_url:
        err = load_agent()
        if err:
            st.error(f"❌ {err}")
            return

        agent_query = (
            f"Please extract the LinkedIn profile context for '{selected_url}' and act as an expert career coach. "
            "Using the extracted data (experience, education, certifications, projects), provide a deep profile analysis including: "
            "1. **Executive Summary** of their professional identity. "
            "2. **Plus Points** (Core strengths & unique skills). "
            "3. **Minus Points / Gaps** (Areas for improvement or missing elements). "
            "4. **Best Job Roles** (3-4 specific career trajectory recommendations). "
            "5. **Where to Apply** (Types of companies or specific Indian companies that fit this profile). "
            "Make sure to append the RAW JSON API data at the bottom of your response."
        )

        with st.spinner("Agent is scanning LinkedIn profile…"):
            from agent import ask_agent_async
            response = asyncio.run(ask_agent_async(st.session_state.agent_executor, agent_query))
            
        st.markdown(response)

# ---------------------------------------------------------------------------
# Tab: About / How to Use
# ---------------------------------------------------------------------------
def tab_about():
    st.markdown("""
## 🤖 About CareerBot

CareerBot is an **AI-powered job search assistant** built for the **Indian job market** as part of a college AI agent project (Track A – Week 1 milestone).

---

### 🛠️ Tech Stack
| Layer | Technology |
|-------|------------|
| **Frontend** | Streamlit |
| **AI Agent** | LangChain + Google Gemini 2.5 Flash |
| **Job Data** | Indeed India scraper + curated mock dataset |
| **Database** | SQLite (saved jobs & search history) |
| **Language** | Python 3.11+ |

---

### 🇮🇳 Indian Market Features
- **Salary in LPA** (Lakhs Per Annum) format
- **Metro + Tier-2 city** filtering (Bangalore, Mumbai, Hyderabad, Pune, Delhi/NCR…)
- **Notice period** awareness (Immediate / 15 / 30 / 60 / 90 days)
- **WFH / Hybrid** preference filtering
- **Fresher-friendly** search (0 years experience)
- Company database: **TCS, Infosys, Wipro, Flipkart, Swiggy, Zomato, Razorpay, Paytm, HCL**

---

### 🚀 How to Use
1. **Enter your Gemini API key** in the sidebar (free at [aistudio.google.com](https://aistudio.google.com))
2. **Set filters** – location, experience, salary range, WFH preference
3. **Chat** with CareerBot or use the **Job Listings** tab for direct search
4. **Save** interesting jobs for later
5. **Research** companies before applying

---

### 📁 Project Structure
```
capbl/
├── app.py          ← You are here (Streamlit UI)
├── agent.py        ← LangChain + Gemini agent
├── database.py     ← SQLite persistence
├── utils.py        ← Indian market constants & helpers
├── tools/
│   ├── job_search.py   ← Indeed scraper + mock data
│   └── company_info.py ← Company knowledge base
└── requirements.txt
```

---
*Built for Week 1–2 milestone of the Job Search AI Agent project.*
""")

# ---------------------------------------------------------------------------
# Tab: Market Intelligence
# ---------------------------------------------------------------------------
def tab_intelligence():
    st.markdown("## 📈 Market Intelligence")
    st.caption("AI Agent analysis of live hiring trends across Indian tech hubs.")

    city = st.selectbox("Select City", ["Bangalore", "Mumbai", "Hyderabad", "Pune", "Delhi/NCR", "Chennai"])
    
    if st.button("🔍 Analyze Market", use_container_width=True):
        err = load_agent()
        if err: return
        
        agent_query = f"Analysis of current hiring trends in {city} for tech roles."
        
        with st.spinner(f"Agent is analyzing {city} market…"):
            from agent import ask_agent_async
            response = asyncio.run(ask_agent_async(st.session_state.agent_executor, agent_query))
            
        st.markdown(f"### Reasoning for {city}")
        st.info(response)

# ---------------------------------------------------------------------------
# Main app layout
# ---------------------------------------------------------------------------
def main():
    filters = render_sidebar()

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "💬 Chat",
        "💼 Job Listings",
        "💾 Saved Jobs",
        "🏢 Company",
        "👤 LinkedIn Profile",
        "📈 Intelligence",
        "ℹ️ About",
    ])

    with tab1:
        tab_chat(filters)
    with tab2:
        tab_jobs(filters)
    with tab3:
        tab_saved()
    with tab4:
        tab_company()
    with tab5:
        tab_linkedin()
    with tab6:
        tab_intelligence()
    with tab7:
        tab_about()


if __name__ == "__main__":
    main()
