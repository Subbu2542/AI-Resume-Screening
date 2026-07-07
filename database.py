import sqlite3
from datetime import datetime

DB_PATH = "database/candidates.db"


def create_database():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT,

        email TEXT,

        phone TEXT,

        location TEXT,

        experience TEXT,

        score INTEGER,

        recommendation TEXT,

        ai_summary TEXT,

        resume_path TEXT,

        created_at TEXT

    )
    """)

    # Backward-compatible schema migration (if DB already exists without ai_summary)
    cursor.execute("PRAGMA table_info(candidates)")
    cols = {row[1] for row in cursor.fetchall()}
    if "ai_summary" not in cols:
        cursor.execute("ALTER TABLE candidates ADD COLUMN ai_summary TEXT")

    conn.commit()

    # If older rows have the AI text stored inside `recommendation`, migrate them
    # so that `recommendation` becomes one of: Shortlisted/Manual Review/Rejected.
    # We detect “bad recommendation” by checking if it is not one of the expected labels.
    cursor.execute(
        "SELECT id, score, recommendation FROM candidates"
    )
    rows = cursor.fetchall()

    for row in rows:
        candidate_id, score, rec = row
        rec = rec or ""
        if rec in ("Shortlisted", "Manual Review", "Rejected"):
            continue

        # compute correct decision from score
        score_int = int(score or 0)
        if score_int >= 80:
            new_rec = "Shortlisted"
        elif score_int >= 60:
            new_rec = "Manual Review"
        else:
            new_rec = "Rejected"

        # Move old AI text into ai_summary if it looks like text
        # (and we don't already have ai_summary populated)
        cursor.execute(
            "UPDATE candidates SET ai_summary = COALESCE(ai_summary, ?), recommendation = ? WHERE id = ?",
            (str(rec), new_rec, candidate_id)
        )

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interviews (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        candidate_id INTEGER NOT NULL,

        interview_date TEXT NOT NULL,

        interview_time TEXT NOT NULL,

        interviewer TEXT,

        mode TEXT,

        meeting_link TEXT,

        notes TEXT,

        status TEXT DEFAULT 'Scheduled',

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(candidate_id) REFERENCES candidates(id)
    )
    """)

    conn.commit()

    conn.close()
    
    
   


def save_candidate(
    candidate,
    match_result,
    resume_path
):
    
    print("=" * 50)
    print("SAVE_CANDIDATE CALLED")
    print(candidate)
    print(match_result)

    # DEBUG ONLY: helps confirm this function is reached and params are valid
    try:
        # Keep logging import local to avoid circular imports if any
        import logging
        logging.info("save_candidate() called")
    except Exception:
        pass

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()


    # Recommendation must be driven ONLY by match_score
    score = int(match_result.get("match_score", 0))
    print("Score =", score)
    recommendation = match_result.get("recommendation")

    print(recommendation)
    if score >= 80:
        recommendation = "Shortlisted"
    elif score >= 60:
        recommendation = "Manual Review"
    else:
        recommendation = "Rejected"

    # Store the AI explanation separately (if your matcher uses that key)
    # Keep backward compatibility with older keys.
    # IMPORTANT: do NOT overwrite the DB `recommendation` column with the AI text.
    ai_summary = (
        match_result.get("ai_summary")
        or match_result.get("explanation")
        or match_result.get("summary")
        or ""
    )

    email = (candidate.get("email") or "").strip()

    # Always INSERT a new screening record.
    # Even if the email is the same, each screening/run should be tracked separately.
    cursor.execute(
        """
        INSERT INTO candidates(
            name,
            email,
            phone,
            location,
            experience,
            score,
            recommendation,
            ai_summary,
            resume_path,
            created_at
        )
        VALUES(?,?,?,?,?,?,?,?,?,?)
        """,
        (
            candidate.get("candidate_name"),
            email,
            candidate.get("phone"),
            candidate.get("location"),
            candidate.get("experience"),
            score,
            recommendation,
            ai_summary,
            resume_path,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )


    conn.commit()
    
    print("Database Saved Successfully")

    conn.close()






def get_all_candidates():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""

    SELECT *

    FROM candidates

    ORDER BY id DESC

    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def delete_candidate(candidate_id):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(

        "DELETE FROM candidates WHERE id=?",

        (candidate_id,)

    )

    conn.commit()

    conn.close()


def search_candidate(keyword):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""

    SELECT *

    FROM candidates

    WHERE

    name LIKE ?

    OR

    email LIKE ?

    """,

    (

        f"%{keyword}%",

        f"%{keyword}%"

    )

    )

    rows = cursor.fetchall()

    conn.close()

    return rows