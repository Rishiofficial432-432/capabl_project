# database.py
# Simple SQLite setup for saving jobs and search history
# Using sqlite3 from stdlib so no extra dependency needed

import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "jobsearch.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables on first run."""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS saved_jobs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                company     TEXT,
                location    TEXT,
                salary      TEXT,
                experience  TEXT,
                url         TEXT,
                description TEXT,
                saved_at    TEXT DEFAULT (datetime('now','localtime'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                query        TEXT NOT NULL,
                filters      TEXT,
                result_count INTEGER DEFAULT 0,
                searched_at  TEXT DEFAULT (datetime('now','localtime'))
            )
        """)
        conn.commit()


# --- Saved jobs ---

def save_job(job):
    """Save a job dict to the DB. Returns True if successful."""
    try:
        with _get_conn() as conn:
            conn.execute(
                """INSERT INTO saved_jobs
                   (title, company, location, salary, experience, url, description)
                   VALUES (:title, :company, :location, :salary, :experience, :url, :description)""",
                {
                    "title":       job.get("title", ""),
                    "company":     job.get("company", ""),
                    "location":    job.get("location", ""),
                    "salary":      job.get("salary", ""),
                    "experience":  job.get("experience", ""),
                    "url":         job.get("url", ""),
                    "description": job.get("description", ""),
                },
            )
            conn.commit()
        return True
    except Exception:
        return False


def get_saved_jobs():
    """Get all saved jobs, newest first."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM saved_jobs ORDER BY saved_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def delete_saved_job(job_id):
    """Remove a saved job by ID."""
    try:
        with _get_conn() as conn:
            conn.execute("DELETE FROM saved_jobs WHERE id = ?", (job_id,))
            conn.commit()
        return True
    except Exception:
        return False


# --- Search history ---

def log_search(query, filters, result_count=0):
    """Log a search query to history."""
    try:
        with _get_conn() as conn:
            conn.execute(
                "INSERT INTO search_history (query, filters, result_count) VALUES (?, ?, ?)",
                (query, json.dumps(filters), result_count),
            )
            conn.commit()
    except Exception:
        pass


def get_search_history(limit=20):
    """Return recent searches."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM search_history ORDER BY searched_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


# Auto-init when imported
init_db()
