import os
import logging
import resend
from db.models import EmailVerification as EmailVerificationModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import secrets
from datetime import datetime, timedelta
from urllib.parse import quote

from core.config import (
    EMAIL_BACKEND,
    PASSWORD_RESET_EXPIRE_MINUTES,
    PUBLIC_APP_URL,
)


load_dotenv()

logger = logging.getLogger(__name__)


def generate_verification_code():
    code = secrets.randbelow(1000000)
    verify_code = str(code).zfill(6)

    return verify_code


def generate_password_reset_token() -> str:
    """Long random token for password-reset links (not a 6-digit OTP)."""
    return secrets.token_urlsafe(32)


def _deliver_email(*, to: str, subject: str, html: str, plain_debug: str) -> None:
    """
    Send email via Resend, or print to the server console for local/dev.

    Set EMAIL_BACKEND=console in .env to avoid burning free-tier Resend quota.
    Set EMAIL_BACKEND=resend when you want a real inbox delivery.
    """
    backend = EMAIL_BACKEND or "console"

    if backend == "console":
        logger.warning(
            "\n========== EMAIL (console backend — not sent via Resend) ==========\n"
            "To: %s\n"
            "Subject: %s\n"
            "%s\n"
            "===================================================================\n",
            to,
            subject,
            plain_debug,
        )
        # Also print so it shows clearly in the uvicorn terminal
        print(
            "\n========== EMAIL (console backend — not sent via Resend) ==========\n"
            f"To: {to}\n"
            f"Subject: {subject}\n"
            f"{plain_debug}\n"
            "===================================================================\n",
            flush=True,
        )
        return

    if backend != "resend":
        raise RuntimeError(
            f"Unknown EMAIL_BACKEND={backend!r}. Use 'console' or 'resend'."
        )

    resend.api_key = os.getenv("RESEND_API_KEY")
    if not resend.api_key:
        raise RuntimeError(
            "EMAIL_BACKEND=resend but RESEND_API_KEY is missing in the environment."
        )

    try:
        resend.Emails.send(
            {
                "from": "onboarding@resend.dev",
                "to": to,
                "subject": subject,
                "html": html,
            }
        )
    except Exception:
        logger.exception("Failed to send email to %s", to)
        raise


def send_verification_code(email: str, code: str):
    subject = "Verify your email"
    html = f"<p>Your verification code is: <strong>{code}</strong></p>"
    plain_debug = f"Verification code: {code}\n(expires according to EmailVerification row)"
    _deliver_email(to=email, subject=subject, html=html, plain_debug=plain_debug)


def send_password_reset_email(email: str, token: str) -> None:
    """Send a time-limited reset link (and token) for API/Swagger testing."""
    reset_link = (
        f"{PUBLIC_APP_URL}/auth/reset-password-form"
        f"?email={quote(email)}&token={quote(token)}"
    )
    minutes = PASSWORD_RESET_EXPIRE_MINUTES
    subject = "Reset your password"
    html = f"""
    <p>We received a request to reset your password.</p>
    <p><a href="{reset_link}">Click here to choose a new password</a></p>
    <p>This link expires in <strong>{minutes} minutes</strong>.</p>
    <p>If the link does not work, open this URL:</p>
    <p><code>{reset_link}</code></p>
    <p>You can also call <code>POST /auth/reset-password</code> with your email,
    this token, and a new password (for example from Swagger at <code>/docs</code>).</p>
    <p>If you did not request this, you can ignore this email.</p>
    """
    plain_debug = (
        f"Reset token: {token}\n"
        f"Expires in: {minutes} minutes\n"
        f"Open this link:\n{reset_link}\n"
        f"Or POST /auth/reset-password with email + token + new_password"
    )
    _deliver_email(to=email, subject=subject, html=html, plain_debug=plain_debug)


def save_verification_code(
    db: Session,
    user_id: int,
    code: str,
    *,
    expire_minutes: int = 15,
):
    expires_at = datetime.utcnow() + timedelta(minutes=expire_minutes)

    verification_entry = EmailVerificationModel(
        user_id=user_id, code=code, expires_at=expires_at, is_used=False
    )

    db.add(verification_entry)
    db.commit()
    db.refresh(verification_entry)
    return verification_entry


def save_password_reset_token(db: Session, user_id: int, token: str):
    return save_verification_code(
        db,
        user_id,
        token,
        expire_minutes=PASSWORD_RESET_EXPIRE_MINUTES,
    )
