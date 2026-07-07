import sqlite3
import streamlit as st
from datetime import date, time

st.set_page_config(
    page_title="Interview Scheduler",
    page_icon="📅",
    layout="wide"
)

st.title("📅 Interview Scheduler")

st.markdown("""
Schedule interviews for shortlisted candidates.
""")

DB_PATH = "database/candidates.db"

conn = sqlite3.connect(DB_PATH)

cursor = conn.cursor()

cursor.execute("""
SELECT id,name,email,score,recommendation
FROM candidates
WHERE recommendation='Shortlisted'
ORDER BY score DESC
""")

candidates = cursor.fetchall()

conn.close()

if not candidates:

    st.warning("No shortlisted candidates found.")

    st.stop()

candidate_dict = {
    f"{row[1]} ({row[2]})": row
    for row in candidates
}

selected = st.selectbox(
    "Select Candidate",
    list(candidate_dict.keys())
)

candidate = candidate_dict[selected]

candidate_id = candidate[0]
candidate_name = candidate[1]
candidate_email = candidate[2]
candidate_score = candidate[3]

st.divider()

col1, col2 = st.columns(2)

with col1:

    interview_date = st.date_input(
        "Interview Date",
        min_value=date.today()
    )

    interview_time = st.time_input(
        "Interview Time",
        value=time(10, 0)
    )

with col2:

    interviewer = st.text_input(
        "Interviewer Name"
    )

    mode = st.selectbox(
        "Interview Mode",
        [
            "Online",
            "Offline"
        ]
    )

meeting_link = st.text_input(
    "Meeting Link (if Online)"
)

notes = st.text_area(
    "Recruiter Notes"
)

if st.button(
    "📅 Schedule Interview",
    use_container_width=True
):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interviews(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        candidate_id INTEGER,

        interview_date TEXT,

        interview_time TEXT,

        interviewer TEXT,

        mode TEXT,

        meeting_link TEXT,

        notes TEXT
    )
    """)

    cursor.execute("""
    INSERT INTO interviews(

        candidate_id,

        interview_date,

        interview_time,

        interviewer,

        mode,

        meeting_link,

        notes

    )

    VALUES(?,?,?,?,?,?,?)

    """,

    (

        candidate_id,

        str(interview_date),

        str(interview_time),

        interviewer,

        mode,

        meeting_link,

        notes

    )

    )

    conn.commit()

    conn.close()

    st.success("✅ Interview Scheduled Successfully")