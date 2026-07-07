import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Recruitment Analytics")

DB = "database/candidates.db"

conn = sqlite3.connect(DB)

df = pd.read_sql_query(
    "SELECT * FROM candidates",
    conn
)

conn.close()

if df.empty:

    st.warning("No candidate data available.")

    st.stop()

total = len(df)

shortlisted = len(
    df[df["recommendation"] == "Shortlisted"]
)

review = len(
    df[df["recommendation"] == "Manual Review"]
)

rejected = len(
    df[df["recommendation"] == "Rejected"]
)

# Harden against NULL/non-numeric scores
df["score"] = pd.to_numeric(df.get("score"), errors="coerce")
average_score = round(df["score"].dropna().mean() if df["score"].notna().any() else 0, 2)


c1, c2, c3, c4 = st.columns(4)

c1.metric("Candidates", total)

c2.metric("Shortlisted", shortlisted)

c3.metric("Manual Review", review)

c4.metric("Rejected", rejected)

st.metric(
    "Average Match Score",
    f"{average_score}%"
)

st.divider()

status_counts = [

    shortlisted,

    review,

    rejected

]

labels = [

    "Shortlisted",

    "Manual Review",

    "Rejected"

]

if sum(status_counts) > 0:

    fig, ax = plt.subplots()

    ax.pie(

        status_counts,

        labels=labels,

        autopct="%1.1f%%"

    )

    st.pyplot(fig)

else:

    st.info("No candidate statistics available.")


st.divider()

st.subheader("Candidate Scores")

fig, ax = plt.subplots()

bar_df = df.copy()
bar_df["name"] = bar_df["name"].fillna("")
bar_df = bar_df[bar_df["score"].notna()]

if not bar_df.empty:
    ax.bar(
        bar_df["name"],
        bar_df["score"],
    )
    ax.set_xticklabels(bar_df["name"], rotation=45, ha="right")
else:
    ax.text(0.5, 0.5, "No score data available", ha="center", va="center")


ax.set_xlabel("Candidate")

ax.set_ylabel("Score")

st.pyplot(fig)

st.divider()

st.subheader("Candidate Database")

st.dataframe(

    df,

    use_container_width=True,

    hide_index=True

)