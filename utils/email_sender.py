from datetime import datetime

def generate_interview_email(
    candidate_name,
    interview_date,
    interview_time,
    interviewer,
    mode,
    meeting_link
):

    subject = "Interview Invitation - AI Engineer"

    body = f"""
Dear {candidate_name},

Congratulations!

Based on your resume screening results, you have been shortlisted for the next stage of our recruitment process.

Interview Details

Date : {interview_date}

Time : {interview_time}

Interviewer : {interviewer}

Mode : {mode}

Meeting Link :
{meeting_link}

Please be available 10 minutes before your scheduled interview.

If you have any questions, feel free to reply to this email.

Regards,

Recruitment Team
"""

    return subject, body