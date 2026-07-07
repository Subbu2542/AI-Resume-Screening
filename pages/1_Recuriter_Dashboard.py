import streamlit as st
import pandas as pd

from database import (
    get_all_candidates,
    search_candidate,
    delete_candidate
)

st.set_page_config(
    page_title="Recruiter Dashboard",
    page_icon="👥",
    layout="wide"
)

st.title("👥 Recruiter Dashboard")

st.markdown(
"""
View, Search and Manage all AI-screened candidates.
"""
)

st.divider()

# ============================================
# SEARCH
# ============================================

search = st.text_input(
    "🔍 Search Candidate (Name or Email)"
)

if search:

    candidates = search_candidate(search)

else:

    candidates = get_all_candidates()

# ============================================
# STATISTICS
# ============================================

total = len(candidates)

shortlisted = 0
review = 0
rejected = 0

for row in candidates:
    # Explicit column mapping based on candidates schema
    # (id, name, email, phone, location, experience, score, recommendation, ai_summary, resume_path, created_at)
    status = row[7]

    if status == "Shortlisted":
        shortlisted += 1
    elif status == "Manual Review":
        review += 1
    else:
        rejected += 1

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total", total)
c2.metric("Shortlisted", shortlisted)
c3.metric("Review", review)
c4.metric("Rejected", rejected)

st.divider()

# ============================================
# TABLE
# ============================================

if candidates:

    data = []

    for row in candidates:

        data.append({

            "ID": row[0],

            "Candidate": row[1],

            "Email": row[2],

            "Phone": row[3],

            "Experience": row[5],
            "Score": row[6],
            "Status": row[7]

        })

    df = pd.DataFrame(data)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("No Candidates Found.")
    
st.divider()

st.subheader("🗑 Delete Candidate")

candidate_id = st.number_input(
    "Candidate ID",
    min_value=1,
    step=1
)

if st.button("Delete Candidate"):

    delete_candidate(candidate_id)

    st.success("Candidate Deleted")

    st.rerun()