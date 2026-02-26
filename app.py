"""
app.py – Main Streamlit application
=====================================
CareerBot: AI-powered Indian Job Search Assistant
Track A | Week 1-2 Milestone
"""

import json
import os
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Dark gradient background */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: #e8e8f0;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.05);
    border-right: 1px solid rgba(255,255,255,0.1);
}

/* Header */
.main-header {
    text-align: center;
    padding: 1rem 0 0.5rem;
}
.main-header h1 {
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.main-header p {
    color: #94a3b8;
    font-size: 1rem;
    margin-top: 0.2rem;
}

/* Job card */
.job-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    transition: all 0.25s ease;
    backdrop-filter: blur(10px);
}
.job-card:hover {
    border-color: #a78bfa;
    background: rgba(167,139,250,0.1);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(167,139,250,0.15);
}
.job-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #a78bfa;
    margin-bottom: 0.15rem;
}
.job-company {
    font-size: 0.9rem;
    color: #60a5fa;
    font-weight: 500;
}
.job-meta {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-top: 0.5rem;
    font-size: 0.82rem;
    color: #94a3b8;
}
.badge {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 0.15rem 0.6rem;
    font-size: 0.78rem;
    color: #cbd5e1;
}
.badge-green  { border-color: #34d399; color: #34d399; }
.badge-blue   { border-color: #60a5fa; color: #60a5fa; }
.badge-purple { border-color: #a78bfa; color: #a78bfa; }
.badge-yellow { border-color: #fbbf24; color: #fbbf24; }

/* Chat bubbles */
.chat-user {
    background: rgba(167,139,250,0.15);
    border: 1px solid rgba(167,139,250,0.3);
    border-radius: 12px 12px 4px 12px;
    padding: 0.7rem 1rem;
    margin: 0.4rem 0;
    max-width: 85%;
    margin-left: auto;
    color: #e8e8f0;
    font-size: 0.93rem;
}
.chat-bot {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px 12px 12px 4px;
    padding: 0.7rem 1rem;
    margin: 0.4rem 0;
    max-width: 90%;
    color: #e8e8f0;
    font-size: 0.93rem;
    line-height: 1.6;
}

/* Metric cards */
.metric-box {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}
.metric-box .metric-val {
    font-size: 1.8rem;
    font-weight: 700;
    color: #a78bfa;
}
.metric-box .metric-label {
    font-size: 0.8rem;
    color: #94a3b8;
    margin-top: 0.2rem;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    color: #94a3b8;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    color: #a78bfa !important;
    border-bottom: 2px solid #a78bfa !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #3b82f6);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(124,58,237,0.4);
}

/* Input fields */
.stTextInput > div > div > input,
.stSelectbox > div > div > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #e8e8f0 !important;
    border-radius: 8px !important;
}

/* Chat input */
.stChatInput > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 12px !important;
}

/* Divider */
hr { border-color: rgba(255,255,255,0.08); }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(167,139,250,0.4); border-radius: 3px; }
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
        <p style="color:#cbd5e1; font-size:0.83rem; margin-top:0.6rem; margin-bottom:0.5rem;">
            {truncate(job.get('description', ''), 200)}
        </p>
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
                f'<div class="metric-label">Saved Jobs</div></div>',
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f'<div class="metric-box"><div class="metric-val">{len(history)}</div>'
                f'<div class="metric-label">Searches</div></div>',
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
                '<div class="chat-bot">👋 <strong>Hello!</strong> I\'m CareerBot, your AI job search assistant.<br><br>'
                '🇮🇳 I specialise in the <strong>Indian job market</strong>. I can help you:<br>'
                '• Find jobs by city, experience, salary (LPA), WFH preference<br>'
                '• Research companies – culture, salary ranges, interview tips<br>'
                '• Get career advice tailored to India\'s job market<br><br>'
                'Try asking: <em>"Find Python developer jobs in Bangalore with 3 years experience"</em></div>',
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
            from agent import ask_agent
            response = ask_agent(st.session_state.agent_executor, full_query)

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
    st.caption("Direct job search with filters — no LLM required.")

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
        from tools.job_search import search_jobs_tool

        query_payload = json.dumps({
            "query": keyword or "software engineer",
            "location": filters["location"],
            "experience": filters["experience"],
            "salary": filters["salary"],
            "wfh": filters["wfh"],
        })

        with st.spinner("Fetching jobs…"):
            raw = search_jobs_tool.invoke(query_payload)

        try:
            jobs = json.loads(raw)
        except Exception:
            jobs = []

        if not jobs:
            st.info("No jobs found. Try different keywords or filters.")
            return

        st.markdown(f"### Found **{len(jobs)}** matching jobs")
        st.divider()
        for i, job in enumerate(jobs):
            render_job_card(job, i)

        # Log
        db.log_search(keyword, filters, len(jobs))

    else:
        # Show sample jobs on first load
        from tools.job_search import _MOCK_JOBS
        st.markdown("### 🔥 Featured Indian Job Listings")
        st.caption("Use the search bar above or sidebar filters to find specific roles.")
        st.divider()
        for i, job in enumerate(_MOCK_JOBS[:6]):
            render_job_card(job, i)

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
    st.caption("Look up Indian companies – culture, salaries, interview tips.")

    known_companies = [
        "TCS", "Infosys", "Wipro", "Flipkart", "Swiggy",
        "Zomato", "Razorpay", "Paytm", "HCL Technologies",
    ]

    selected = st.selectbox("Select a company to explore", ["Choose…"] + known_companies)

    if selected and selected != "Choose…":
        from tools.company_info import company_info_tool
        raw = company_info_tool.invoke(selected)
        info = json.loads(raw)

        if "message" in info:
            st.warning(info["message"])
            return

        st.markdown(f"### {info.get('name', selected)}")
        st.caption(f"{info.get('type', '')} · Founded {info.get('founded', 'N/A')} · HQ: {info.get('hq', 'N/A')}")
        st.divider()

        cols = st.columns(4)
        cols[0].metric("Employees", info.get("employees", "N/A"))
        cols[1].metric("Revenue", info.get("revenue", info.get("funding", "N/A")))
        cols[2].metric("Rating", info.get("rating", "N/A"))
        cols[3].markdown(f"**CEO:** {info.get('ceo', 'N/A')}")

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
| **AI Agent** | LangChain + Google Gemini 1.5 Flash |
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
# Main app layout
# ---------------------------------------------------------------------------
def main():
    filters = render_sidebar()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 Chat with CareerBot",
        "💼 Job Listings",
        "💾 Saved Jobs",
        "🏢 Company Research",
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
        tab_about()


if __name__ == "__main__":
    main()
