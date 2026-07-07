import os
import logging
import streamlit as st

from dotenv import load_dotenv

from utils.pdf_parser import extract_pdf_text
from utils.docx_parser import extract_docx_text
from utils.resume_parser import parse_resume
from utils.jd_matcher import match_resume_with_jd

from database import (
    create_database,
    save_candidate
)
import database



# ==========================================================
# INITIAL SETUP
# ==========================================================

load_dotenv()

logging.basicConfig(
    filename="application.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

os.makedirs("uploads", exist_ok=True)
os.makedirs("uploads/resumes", exist_ok=True)
os.makedirs("uploads/job_descriptions", exist_ok=True)

create_database()

st.set_page_config(
    page_title="AI Resume Screening",
    page_icon="🤖",
    layout="wide"
)

# ==========================================================
# SESSION STATE
# ==========================================================

DEFAULTS = {

    "candidate": None,

    "resume_text": "",

    "jd_text": "",

    "match_result": None,

    "analysis_complete": False,

    "resume_uploaded": False,

    "jd_uploaded": False

}

for key, value in DEFAULTS.items():

    if key not in st.session_state:

        st.session_state[key] = value

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.title("🤖 Recruiter Panel")

    st.divider()

    st.metric(
        "Resume",
        "Uploaded"
        if st.session_state.resume_uploaded
        else "Waiting"
    )

    st.metric(
        "Job Description",
        "Uploaded"
        if st.session_state.jd_uploaded
        else "Waiting"
    )

    st.metric(
        "Analysis",
        "Completed"
        if st.session_state.analysis_complete
        else "Pending"
    )

    st.divider()

    if st.button(
        "♻ Reset Application",
        use_container_width=True
    ):

        for key in DEFAULTS:

            st.session_state[key] = DEFAULTS[key]

        # Also clear uploaded files
        import shutil
        shutil.rmtree("uploads/resumes", ignore_errors=True)
        shutil.rmtree("uploads/job_descriptions", ignore_errors=True)
        os.makedirs("uploads/resumes", exist_ok=True)
        os.makedirs("uploads/job_descriptions", exist_ok=True)

        st.rerun()


# ==========================================================
# HEADER
# ==========================================================

st.title("📄 AI Resume Screening & Interview Scheduling")

st.markdown(
"""
Upload a candidate resume and a Job Description.

### The AI will

- Extract candidate information
- Compare with the Job Description
- Calculate AI Match Score
- Recommend whether to shortlist
"""
)

st.divider()

# ==========================================================
# FILE UPLOAD
# ==========================================================

left, right = st.columns(2)

# ----------------------------------------------------------
# RESUME
# ----------------------------------------------------------

with left:

    st.subheader("📄 Candidate Resume")

    resume_file = st.file_uploader(

        "Upload Resume",

        type=[

            "pdf",

            "docx"

        ]

    )

# ----------------------------------------------------------
# JOB DESCRIPTION
# ----------------------------------------------------------

with right:

    st.subheader("📋 Job Description")

    jd_option = st.radio(

        "Choose Input Method",

        [

            "Upload File",

            "Paste Text"

        ]

    )

    jd_file = None

    jd_text_input = ""

    if jd_option == "Upload File":

        jd_file = st.file_uploader(

            "Upload Job Description",

            type=[

                "pdf",

                "docx",

                "txt"

            ]

        )

    else:

        jd_text_input = st.text_area(

            "Paste Job Description",

            height=250,

            placeholder="Paste complete Job Description here..."

        )

st.divider()

# ==========================================================
# SAVE FILES
# ==========================================================

resume_path = None

jd_path = None

if resume_file:

    # New resume uploaded => reset analysis state to avoid stale results
    st.session_state.analysis_complete = False
    st.session_state.match_result = None
    st.session_state.candidate = None

    from datetime import datetime

    # Use a unique filename to avoid overwriting previous uploads
    filename = (
        datetime.now().strftime("%Y%m%d_%H%M%S")
        + "_"
        + resume_file.name
    )

    resume_path = os.path.join(
        "uploads/resumes",
        filename,
    )


    with open(resume_path, "wb") as file:

        file.write(

            resume_file.getbuffer()

        )

    st.session_state.resume_uploaded = True

if jd_option == "Upload File":

    if jd_file:

        # New JD uploaded => reset analysis state to avoid stale results
        st.session_state.analysis_complete = False
        st.session_state.match_result = None
        st.session_state.candidate = None

        from datetime import datetime

        # Use unique filename to avoid overwriting previous uploads
        filename = (
            datetime.now().strftime("%Y%m%d_%H%M%S")
            + "_"
            + jd_file.name
        )

        jd_path = os.path.join(
            "uploads/job_descriptions",
            filename
        )


        with open(jd_path, "wb") as file:

            file.write(

                jd_file.getbuffer()

            )

        st.session_state.jd_uploaded = True

else:

    if jd_text_input.strip():

        # New JD text entered => reset analysis state to avoid stale results
        st.session_state.analysis_complete = False
        st.session_state.match_result = None
        st.session_state.candidate = None

        st.session_state.jd_text = jd_text_input
        st.session_state.jd_uploaded = True


# ==========================================================
# ANALYZE CANDIDATE
# ==========================================================

ready = (
    st.session_state.resume_uploaded
    and
    st.session_state.jd_uploaded
)

if ready:

    st.success("✅ Resume and Job Description Ready")

    analyze = st.button(
        "🚀 Analyze Candidate",
        use_container_width=True,
        type="primary",
        disabled=st.session_state.analysis_complete
    )


    if analyze:

        progress = st.progress(0)

        # --------------------------------------------------
        # STEP 1 : EXTRACT RESUME
        # --------------------------------------------------

        with st.spinner("📄 Extracting Resume..."):

            try:

                if resume_path.endswith(".pdf"):

                    resume_text = extract_pdf_text(
                        resume_path
                    )

                else:

                    resume_text = extract_docx_text(
                        resume_path
                    )

                st.session_state.resume_text = resume_text

                progress.progress(20)

                logging.info("Resume extracted")

            except Exception as e:

                st.error(f"Resume Extraction Error\n\n{e}")

                st.stop()

        # --------------------------------------------------
        # STEP 2 : EXTRACT JOB DESCRIPTION
        # --------------------------------------------------

        with st.spinner("📋 Reading Job Description..."):

            try:

                if jd_option == "Upload File":

                    if jd_path.endswith(".pdf"):

                        jd_text = extract_pdf_text(
                            jd_path
                        )

                    elif jd_path.endswith(".docx"):

                        jd_text = extract_docx_text(
                            jd_path
                        )

                    else:

                        with open(
                            jd_path,
                            "r",
                            encoding="utf-8"
                        ) as file:

                            jd_text = file.read()

                else:

                    jd_text = jd_text_input

                st.session_state.jd_text = jd_text

                progress.progress(40)

                logging.info("JD extracted")

            except Exception as e:

                st.error(f"JD Extraction Error\n\n{e}")

                st.stop()

        # --------------------------------------------------
        # STEP 3 : RESUME PARSING
        # --------------------------------------------------

        with st.spinner("🤖 Parsing Resume..."):

            try:

                candidate = parse_resume(
                    st.session_state.resume_text
                )

                if not candidate:

                    st.error("Resume Parser returned empty result.")

                    st.stop()

                st.session_state.candidate = candidate

                progress.progress(65)

                logging.info("Resume Parsed")

            except Exception as e:

                st.error(f"Resume Parsing Error\n\n{e}")

                st.stop()

        # --------------------------------------------------
        # STEP 4 : AI JD MATCHING
        # --------------------------------------------------

        with st.spinner("🎯 Matching Resume with JD..."):

            try:

                match_result = match_resume_with_jd(

                    st.session_state.resume_text,

                    st.session_state.jd_text

                )

                if not match_result:

                    st.error("JD Matcher returned empty result.")

                    st.stop()

                st.session_state.match_result = match_result

                progress.progress(90)

                logging.info("JD Matching Complete")

            except Exception as e:

                st.error(f"JD Matching Error\n\n{e}")

                st.stop()

        # --------------------------------------------------
        # STEP 5 : SAVE DATABASE
        # --------------------------------------------------

        try:
            with st.spinner("Saving screening results..."):
                st.write("Saving Candidate...")
                st.write(st.session_state.match_result)
                save_candidate(

                    st.session_state.candidate,


                    st.session_state.match_result,

                    resume_path

                )
                st.session_state.analysis_complete = True

            logging.info("Candidate Saved")

        except Exception as e:

            logging.error(str(e))

        progress.progress(100)

        st.session_state.analysis_complete = True

        st.success("✅ Analysis Completed Successfully")

        
        
# ==========================================================
# CANDIDATE DASHBOARD
# ==========================================================

if (
    st.session_state.analysis_complete
    and
    st.session_state.candidate is not None
    and
    st.session_state.match_result is not None
):

    candidate = st.session_state.candidate
    match = st.session_state.match_result

    st.divider()

    st.header("👤 Candidate Dashboard")

    # ======================================================
    # PERSONAL INFORMATION
    # ======================================================

    left, right = st.columns(2)

    with left:

        st.subheader("👤 Personal Information")

        st.text_input(
            "Candidate Name",
            value=candidate.get("candidate_name", ""),
            disabled=True
        )

        st.text_input(
            "Email",
            value=candidate.get("email", ""),
            disabled=True
        )

        st.text_input(
            "Phone",
            value=candidate.get("phone", ""),
            disabled=True
        )

        st.text_input(
            "Location",
            value=candidate.get("location", ""),
            disabled=True
        )

    with right:

        st.subheader("💼 Professional Information")

        st.text_input(
            "Experience",
            value=candidate.get("experience", ""),
            disabled=True
        )

        st.text_input(
            "Current Role",
            value=candidate.get("current_role", ""),
            disabled=True
        )

        st.text_input(
            "Company",
            value=candidate.get("company", ""),
            disabled=True
        )

        st.text_input(
            "LinkedIn",
            value=candidate.get("linkedin", ""),
            disabled=True
        )

    st.divider()

    # ======================================================
    # SUMMARY
    # ======================================================

    st.subheader("📝 Professional Summary")

    st.info(
        candidate.get(
            "summary",
            "Summary Not Available"
        )
    )

    # ======================================================
    # SKILLS
    # ======================================================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("💻 Technical Skills")

        skills = candidate.get(
            "technical_skills",
            []
        )

        if skills:

            for skill in skills:

                st.success(skill)

        else:

            st.warning("Not Available")


    with col2:

        st.subheader("🤝 Soft Skills")

        soft = candidate.get(
            "soft_skills",
            []
        )

        if soft:

            for skill in soft:

                st.info(skill)

        else:

            st.warning("Not Available")


    st.divider()

    # ======================================================
    # EDUCATION
    # ======================================================

    st.subheader("🎓 Education")

    education = candidate.get(
        "education",
        []
    )

    if education:

        for item in education:

            st.write("•", item)

    else:

        st.write("Not Available")


    # ======================================================
    # PROJECTS
    # ======================================================

    st.subheader("📁 Projects")

    projects = candidate.get(
        "projects",
        []
    )

    if projects:

        for project in projects:

            st.write("•", project)

    else:

        st.write("Not Available")


    # ======================================================
    # CERTIFICATIONS
    # ======================================================

    st.subheader("📜 Certifications")

    certs = candidate.get(
        "certifications",
        []
    )

    if certs:

        for cert in certs:

            st.write("•", cert)

    else:

        st.write("Not Available")


    # ======================================================
    # LANGUAGES
    # ======================================================

    st.subheader("🌍 Languages")

    languages = candidate.get(
        "languages",
        []
    )

    if languages:

        st.write(", ".join(languages))

    else:

        st.write("Not Available")


    st.divider()

    # ======================================================
    # DOCUMENT PREVIEW
    # ======================================================

    left, right = st.columns(2)

    with left:

        st.subheader("📄 Resume Preview")

        st.text_area(
            "Resume Text",
            st.session_state.resume_text,
            height=350
        )

    with right:

        st.subheader("📋 Job Description")

        st.text_area(
            "JD Text",
            st.session_state.jd_text,
            height=350
        )

    st.divider()

    # ======================================================
    # DOWNLOAD JSON
    # ======================================================

    import json

    st.download_button(

        "⬇ Download Candidate JSON",

        data=json.dumps(
            candidate,
            indent=4
        ),

        file_name="candidate_profile.json",

        mime="application/json"

    )
    
# ==========================================================
# AI MATCH RESULTS
# ==========================================================

    st.divider()

    st.header("🎯 AI Match Results")

    score = int(match.get("match_score", 0))

    st.metric(
        "Overall Match Score",
        f"{score}%"
    )

    st.progress(score / 100)

    col1, col2 = st.columns(2)

    # ------------------------------------------------------
    # Matching Skills
    # ------------------------------------------------------

    with col1:

        st.success("✅ Matching Skills")

        matching = match.get(
            "matching_skills",
            []
        )

        if matching:

            for skill in matching:

                st.write(f"• {skill}")

        else:

            st.write("No Matching Skills")

    # ------------------------------------------------------
    # Missing Skills
    # ------------------------------------------------------

    with col2:

        st.error("❌ Missing Skills")

        missing = match.get(
            "missing_skills",
            []
        )

        if missing:

            for skill in missing:

                st.write(f"• {skill}")

        else:

            st.write("No Missing Skills")

    st.divider()

    # ------------------------------------------------------
    # Strengths
    # ------------------------------------------------------

    st.subheader("💪 Candidate Strengths")

    strengths = match.get(
        "strengths",
        []
    )

    if strengths:

        for item in strengths:

            st.success(item)

    else:

        st.info("No strengths available.")

    # ------------------------------------------------------
    # Weaknesses
    # ------------------------------------------------------

    st.subheader("⚠ Areas for Improvement")

    weaknesses = match.get(
        "weaknesses",
        []
    )

    if weaknesses:

        for item in weaknesses:

            st.warning(item)

    else:

        st.info("No weaknesses identified.")

    st.divider()

    # ======================================================
    # RECRUITMENT DECISION
    # ======================================================

    st.header("📋 Recruitment Decision")

    if score >= 80:

        recommendation = "Shortlisted"

        st.success("🎉 Candidate Shortlisted")
        
        st.balloons()

        st.info(
            """
Candidate meets the required AI Match Score.

Recommendation:

✔ Proceed to Interview Scheduling
"""
        )

    elif score >= 60:

        recommendation = "Manual Review"

        st.warning("🟡 Candidate Requires Manual Review")

        st.info(
            """
Candidate partially matches the Job Description.

Recommendation:

✔ Recruiter should review the profile.
"""
        )

    else:

        recommendation = "Rejected"

        st.error("❌ Candidate Rejected")

        st.info(
            """
Candidate does not satisfy the required criteria.

Recommendation:

No interview required.
"""
        )

    st.divider()

    # ======================================================
    # DOWNLOAD REPORT
    # ======================================================

    report = f"""
AI RESUME SCREENING REPORT

Candidate Name:
{candidate.get('candidate_name','')}

Email:
{candidate.get('email','')}

Phone:
{candidate.get('phone','')}

Location:
{candidate.get('location','')}

Experience:
{candidate.get('experience','')}

Overall Match Score:
{score}%

Recruitment Decision:
{recommendation}

----------------------------------------

Matching Skills

{chr(10).join(match.get("matching_skills", []))}

----------------------------------------

Missing Skills

{chr(10).join(match.get("missing_skills", []))}

----------------------------------------

Strengths

{chr(10).join(match.get("strengths", []))}

----------------------------------------

Weaknesses

{chr(10).join(match.get("weaknesses", []))}
"""

    st.download_button(

        "📄 Download Screening Report",

        report,

        file_name="AI_Resume_Screening_Report.txt",

        mime="text/plain"

    )

# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption(
    "Developed by Subba Rami Reddy Janga\n\nPowered by Streamlit • Gemini • LangChain • SQLite"
)

