import os
import resend
from db.models import EmailVerification as EmailVerificationModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import secrets
from datetime import datetime, timedelta

load_dotenv()


def generate_verification_code():
    code = secrets.randbelow(1000000)
    verify_code = str(code).zfill(6)

    return verify_code


def send_verification_code(email: str, code: str):
    resend.api_key = os.getenv("RESEND_API_KEY")

    resend.Emails.send(
        {
            "from": "onboarding@resend.dev",
            "to": email,
            "subject": "Verify your email",
            "html": f"<p>Your verification code is: <strong>{code}</strong></p>",
        }
    )


def save_verification_code(db: Session, user_id: int, code: str):
    expires_at = datetime.utcnow() + timedelta(minutes=15)

    verification_entry = EmailVerificationModel(
        user_id=user_id, code=code, expires_at=expires_at, is_used=False
    )

    db.add(verification_entry)
    db.commit()
    db.refresh(verification_entry)


