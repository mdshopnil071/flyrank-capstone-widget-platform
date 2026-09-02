from app.config import settings

def send_owner_notification(email: str, submission_id: str):
    # Isolated side effect wrapper with guaranteed error catching
    try:
        if settings.NOTIFICATION_FAIL:
            raise RuntimeError("configured notification failure")
        # Simulated email integration side effect (e.g., Mailpit/SMTP log)
        print(f"[SIDE EFFECT SUCCESS] Sent notification to {email} for submission {submission_id}")
    except Exception as e:
        print(f"[SIDE EFFECT FAILED] Failed sending email: {str(e)}. Submission process remains unaffected.")