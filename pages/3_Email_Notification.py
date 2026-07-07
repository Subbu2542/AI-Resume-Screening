import sqlite3
import streamlit as st

from utils.email_sender import generate_interview_email

st.set_page_config(
    page_title="Email Notification",
    page_icon="📧",
    layout="wide"
)

st.title("📧 Interview Email Generator")

DB = "database/candidates.db"

conn = sqlite3.connect(DB)

cursor = conn.cursor()

cursor.execute("""
SELECT
candidate_id,
interview_date,
interview_time,
interviewer,
mode,
meeting_link
FROM interviews
""")

interviews = cursor.fetchall()

conn.close()

if not interviews:

    st.warning("No Interviews Scheduled.")

    st.stop()

candidate = st.selectbox(

    "Select Candidate",

    interviews,

    format_func=lambda x: f"Candidate ID : {x[0]}"

)

candidate_id = candidate[0]

date = candidate[1]

time = candidate[2]

interviewer = candidate[3]

mode = candidate[4]

link = candidate[5]

name = st.text_input("Candidate Name")

if st.button("Generate Email"):

    subject, body = generate_interview_email(

        name,

        date,

        time,

        interviewer,

        mode,

        link

    )

    st.subheader("Subject")

    st.code(subject)

    st.subheader("Email")

    st.text_area(

        "",

        body,

        height=350

    )