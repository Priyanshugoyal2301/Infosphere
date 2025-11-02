"""
fake_news_verifier.py
A small prototype that "verifies" a news item by checking:
 - local user-submitted news DB (sqlite)
 - a simulated Times of India DB (sqlite)
It uses fuzzy title matching, date proximity, location match, and source checks to compute a score.

Run: python fake_news_verifier.py
"""

import sqlite3
from datetime import datetime, timedelta
from rapidfuzz import fuzz, process
import json
import uuid

# --------- CONFIG / THRESHOLDS ----------
TITLE_SIMILARITY_HIGH = 85   # percent
TITLE_SIMILARITY_MEDIUM = 65
DATE_WINDOW_DAYS = 3         
CREDIBLE_SCORE_THRESHOLD = 70
LIKELY_FAKE_THRESHOLD = 35

# --------- HELPERS ----------
def now_date():
    return datetime.utcnow().date()

def date_from_iso(s):
    return datetime.strptime(s, "%Y-%m-%d").date()

# Normalizes text for matching
def normalize(s):
    return (s or "").strip().lower()

# ---------- DB SETUP ----------
def create_and_populate_dbs(conn):
    cur = conn.cursor()

    # Local user news DB
    cur.execute("""
    CREATE TABLE IF NOT EXISTS local_users (
        id TEXT PRIMARY KEY,
        name TEXT,
        location TEXT,
        email TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS local_news (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        title TEXT,
        body TEXT,
        location TEXT,
        date TEXT,            -- YYYY-MM-DD
        proof_type TEXT,      -- e.g., 'image', 'video', 'link', 'none'
        source_url TEXT,
        verification_status TEXT DEFAULT 'unverified',
        FOREIGN KEY(user_id) REFERENCES local_users(id)
    );
    """)

    # Simulated Times of India DB
    cur.execute("""
    CREATE TABLE IF NOT EXISTS toi_news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        body TEXT,
        location TEXT,
        date TEXT,   -- YYYY-MM-DD
        url TEXT
    );
    """)

    conn.commit()

    # Insert sample users and news (if empty)
    cur.execute("SELECT count(*) FROM local_users;")
    if cur.fetchone()[0] == 0:
        users = [
            (str(uuid.uuid4()), "Asha Sharma", "Jabalpur, India", "asha@example.com"),
            (str(uuid.uuid4()), "Ravi Kumar", "Lucknow, India", "ravi@example.com"),
        ]
        cur.executemany("INSERT INTO local_users(id,name,location,email) VALUES(?,?,?,?);", users)

    cur.execute("SELECT count(*) FROM local_news;")
    if cur.fetchone()[0] == 0:
        # pick user_id from inserted users
        cur.execute("SELECT id FROM local_users LIMIT 1;"); uid = cur.fetchone()[0]
        sample_local_news = [
            (str(uuid.uuid4()),
             uid,
             "Massive fire breaks out in Jabalpur textile market",
             "A large fire broke out at the central textile market; firefighters responding. Multiple shops damaged.",
             "Jabalpur, India",
             (now_date() - timedelta(days=1)).isoformat(),
             "image",
             "http://local/uploader/1",
             "unverified"),
            (str(uuid.uuid4()),
             uid,
             "New metro line in Lucknow inaugurated",
             "State minister inaugurated phase 2 of the metro project today",
             "Lucknow, India",
             now_date().isoformat(),
             "none",
             None,
             "unverified"),
            # a possibly fake/suspicious claim
            (str(uuid.uuid4()),
             uid,
             "Alien spaceship landed near Narmada river",
             "Local villagers reportedly saw unusual lights and a craft landing near the river",
             "Narmada, India",
             (now_date() - timedelta(days=2)).isoformat(),
             "video",
             "http://local/uploader/3",
             "unverified"),
        ]
        cur.executemany("""
            INSERT INTO local_news(id,user_id,title,body,location,date,proof_type,source_url,verification_status)
            VALUES(?,?,?,?,?,?,?,?,?);
        """, sample_local_news)

    cur.execute("SELECT count(*) FROM toi_news;")
    if cur.fetchone()[0] == 0:
        toi_samples = [
            # a matching credible TOI story for Jabalpur fire
            ("Massive fire at Jabalpur textile market damages shops",
             "A major fire gutted several shops at the Jabalpur Textile Market. No casualties reported.", "Jabalpur, India",
             (now_date() - timedelta(days=1)).isoformat(),
             "https://timesofindia.example/toi1"),
            # metro story
            ("Lucknow metro phase 2 inaugurated by state minister",
             "Phase 2 of Lucknow's metro network was inaugurated today in a ceremony attended by ministers.", "Lucknow, India",
             now_date().isoformat(),
             "https://timesofindia.example/toi2"),
            # unrelated/satire
            ("Man claims alien sighting near river, police investigating",
             "Police are investigating reports of strange lights near Narmada river; no evidence yet.", "Narmada, India",
             (now_date() - timedelta(days=1)).isoformat(),
             "https://timesofindia.example/toi3"),
        ]
        cur.executemany("INSERT INTO toi_news(title,body,location,date,url) VALUES(?,?,?,?,?)", toi_samples)

    conn.commit()


# ---------- FETCH FUNCTIONS ----------
def fetch_local_news(conn):
    cur = conn.cursor()
    cur.execute("SELECT id,user_id,title,body,location,date,proof_type,source_url,verification_status FROM local_news;")
    rows = cur.fetchall()
    keys = ["id","user_id","title","body","location","date","proof_type","source_url","verification_status"]
    return [dict(zip(keys, r)) for r in rows]

def fetch_toi_news(conn):
    cur = conn.cursor()
    cur.execute("SELECT id,title,body,location,date,url FROM toi_news;")
    rows = cur.fetchall()
    keys = ["id","title","body","location","date","url"]
    return [dict(zip(keys, r)) for r in rows]

# ---------- VERIFICATION ALGORITHM ----------
def score_by_title_similarity(local_title, toi_title):
    # use token_set_ratio-style similarity
    return fuzz.token_set_ratio(local_title, toi_title)

def date_match_score(date_a_iso, date_b_iso):
    try:
        da = date_from_iso(date_a_iso)
        db = date_from_iso(date_b_iso)
    except Exception:
        return 0
    delta = abs((da - db).days)
    if delta <= DATE_WINDOW_DAYS:
        return max(0, 30 - 5*delta)  # closer => bigger
    return 0

def location_score(loc_a, loc_b):
    a = normalize(loc_a or "")
    b = normalize(loc_b or "")
    if a == "" or b == "":
        return 0
    # simple heuristic: any overlapping token counts
    tokens_a = set([t.strip() for t in a.replace(",", " ").split()])
    tokens_b = set([t.strip() for t in b.replace(",", " ").split()])
    if tokens_a & tokens_b:
        return 20
    return 0

def source_presence_score(proof_type, source_url):
    score = 0
    if proof_type and proof_type.lower() in ("image","video","link"):
        score += 10
    if source_url:
        score += 15
    return score

def compute_verification_score(local_item, toi_matches):
    """
    Computes a final score based on best TOI match and heuristics.
    """
    best_match = None
    best_score = 0
    for t in toi_matches:
        title_sim = score_by_title_similarity(local_item["title"], t["title"])
        dscore = date_match_score(local_item["date"], t["date"])
        lscore = location_score(local_item["location"], t["location"])
        sscore = source_presence_score(local_item["proof_type"], local_item["source_url"])

        # Weighted combination
        # title sim mapped 0-40, date 0-30, loc 0-20, source 0-10
        title_component = (title_sim / 100.0) * 40
        total = title_component + dscore + lscore + sscore
        if total > best_score:
            best_score = total
            best_match = {
                "toi_id": t["id"],
                "toi_title": t["title"],
                "toi_url": t["url"],
                "title_similarity": title_sim,
                "date_score": dscore,
                "location_score": lscore,
                "source_score": sscore,
                "total": total
            }
    # If no TOI matches, evaluate local-only heuristics
    if not best_match:
        sscore = source_presence_score(local_item["proof_type"], local_item["source_url"])
        # base small score for local-only: if has proof, some points
        base = 10 + sscore
        best_score = base
    return best_score, best_match

def verdict_from_score(score):
    if score >= CREDIBLE_SCORE_THRESHOLD:
        return "credible"
    elif score <= LIKELY_FAKE_THRESHOLD:
        return "likely-fake"
    else:
        return "unverified"

# ---------- MAIN VERIFY FUNCTION ----------
def verify_news_item(conn, local_item):
    toi_news = fetch_toi_news(conn)
    # quick filter list of candidate TOI articles by token overlap on location or title tokens
    candidates = toi_news  # small DB so all
    score, best_match = compute_verification_score(local_item, candidates)
    verdict = verdict_from_score(score)
    result = {
        "local_id": local_item["id"],
        "local_title": local_item["title"],
        "score": round(score, 2),
        "verdict": verdict,
        "best_match": best_match
    }
    return result

# ---------- DEMO / USAGE ----------
def demo_run():
    conn = sqlite3.connect(":memory:")   # in-memory DB for demo; swap to file for persistence
    create_and_populate_dbs(conn)

    local_news = fetch_local_news(conn)
    print("Local news items found:", len(local_news))
    results = []
    for item in local_news:
        out = verify_news_item(conn, item)
        results.append(out)
        print("\n--- Verification result ---")
        print(f"Title: {out['local_title']}")
        print(f"Score: {out['score']}  Verdict: {out['verdict']}")
        if out["best_match"]:
            bm = out["best_match"]
            print("Best TOI match:", bm["toi_title"])
            print("TOI URL:", bm["toi_url"])
            print("Title similarity:", bm["title_similarity"])
            print("Date score:", bm["date_score"])
            print("Location score:", bm["location_score"])
            print("Source score:", bm["source_score"])
        else:
            print("No TOI match found. Relying on local evidence.")

    # For further use, return results JSON
    print("\nSummary JSON:")
    print(json.dumps(results, indent=2))

if _name_ == "_main_":
    demo_run()