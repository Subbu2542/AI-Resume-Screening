# Database Schema

## Overview

The application uses SQLite to store candidate information after AI resume analysis.

Database Name:

database/candidates.db

---

## Table: candidates

| Column | Type | Description |
|---------|------|-------------|
| id | INTEGER | Primary Key |
| name | TEXT | Candidate Name |
| email | TEXT | Candidate Email |
| phone | TEXT | Contact Number |
| location | TEXT | Candidate Location |
| experience | TEXT | Work Experience |
| score | INTEGER | AI Match Score |
| recommendation | TEXT | Shortlisted / Manual Review / Rejected |
| ai_summary | TEXT | AI Recommendation Summary |
| resume_path | TEXT | Uploaded Resume Path |
| created_at | TEXT | Screening Date & Time |

---

## Shortlisting Logic

| Match Score | Status |
|-------------|--------|
| 80–100 | Shortlisted |
| 60–79 | Manual Review |
| Below 60 | Rejected |

---

## Database Operations

The application performs:

- Insert Candidate
- Read Candidate Data
- Search Candidate
- Display Analytics
- Schedule Interviews