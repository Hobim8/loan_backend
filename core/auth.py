from datetime import datetime
from html import escape

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.orm import Session

from core.email import (
    generate_password_reset_token,
    generate_verification_code,
    save_password_reset_token,
    save_verification_code,
    send_password_reset_email,
    send_verification_code,
)
from core.jwt import create_access_token
from core.security import hash_password, verify_password
from db.models import EmailVerification as EmailVerificationModel
from db.models import User as UserModel
from db.session import get_db
from schemas.user import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserCreate,
    verifyEmail,
)

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def _password_reset_form_html(
    *,
    email: str = "",
    token: str = "",
    message: str = "",
    error: str = "",
) -> str:
    email_safe = escape(email or "")
    token_safe = escape(token or "")
    message_block = (
        f'<p style="color:green;">{escape(message)}</p>' if message else ""
    )
    error_block = f'<p style="color:#b00020;">{escape(error)}</p>' if error else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Reset password</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 420px; margin: 3rem auto; padding: 0 1rem; }}
    label {{ display: block; margin-top: 0.75rem; font-weight: 600; }}
    input {{ width: 100%; padding: 0.5rem; margin-top: 0.25rem; box-sizing: border-box; }}
    button {{ margin-top: 1.25rem; padding: 0.6rem 1rem; cursor: pointer; }}
  </style>
</head>
<body>
  <h1>Reset password</h1>
  {message_block}
  {error_block}
  <form method="post" action="/auth/reset-password-form">
    <label>Email
      <input type="email" name="email" value="{email_safe}" required />
    </label>
    <label>Reset token
      <input type="text" name="token" value="{token_safe}" required />
    </label>
    <label>New password
      <input type="password" name="new_password" minlength="8" required />
    </label>
    <label>Confirm new password
      <input type="password" name="confirm_password" minlength="8" required />
    </label>
    <button type="submit">Update password</button>
  </form>
  <p style="color:#555;font-size:0.9rem;margin-top:1.5rem;">
    Token expires after a short time. After success, log in at
    <a href="/docs">/docs</a> with your username <em>or</em> email and new password.
  </p>
</body>
</html>
"""


def _apply_password_reset(
    db: Session, *, email: str, token: str, new_password: str
) -> None:
    """Validate token and set new password. Raises HTTPException on failure."""
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        raise HTTPException(
            status_code=400,
            detail="That reset link is invalid or has expired. Please request a new one.",
        )

    entry = (
        db.query(EmailVerificationModel)
        .filter(
            EmailVerificationModel.user_id == user.id,
            EmailVerificationModel.code == token,
            EmailVerificationModel.is_used == False,  # noqa: E712
            EmailVerificationModel.expires_at > datetime.utcnow(),
        )
        .first()
    )
    if not entry:
        raise HTTPException(
            status_code=400,
            detail="That reset link is invalid or has expired. Please request a new one.",
        )

    user.hashed_password = hash_password(new_password)
    entry.is_used = True

    # Invalidate any other unused codes for this user (verify + prior resets)
    (
        db.query(EmailVerificationModel)
        .filter(
            EmailVerificationModel.user_id == user.id,
            EmailVerificationModel.is_used == False,  # noqa: E712
            EmailVerificationModel.id != entry.id,
        )
        .update({EmailVerificationModel.is_used: True}, synchronize_session=False)
    )

    db.commit()


@auth_router.post("/Signup")
def Signup(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    if db.query(UserModel).filter(UserModel.email == user.email).first():
        raise HTTPException(
            status_code=400, detail="An account with this email already exists."
        )

    if db.query(UserModel).filter(UserModel.username == user.username).first():
        raise HTTPException(
            status_code=400, detail="This username is already taken."
        )

    hashed = hash_password(user.password)

    new_user = UserModel(
        username=user.username, email=user.email, hashed_password=hashed
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    generate_code = generate_verification_code()
    save_verification_code(db, new_user.id, generate_code)
    background_tasks.add_task(send_verification_code, user.email, generate_code)

    return {
        "message": "Account created. Please check your email for a verification code, then verify your account before signing in."
    }


@auth_router.post("/Login")
def Login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Log in with either username or email in the `username` form field
    (OAuth2 password flow always names that field `username`).
    """
    identifier = (form_data.username or "").strip()
    db_user = (
        db.query(UserModel)
        .filter(
            or_(
                UserModel.username == identifier,
                UserModel.email == identifier,
            )
        )
        .first()
    )

    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password. Please try again.",
        )

    if not db_user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Please verify your email before signing in.",
        )

    access_token = create_access_token(
        data={"sub": db_user.username, "user_id": db_user.id}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/verify-email")
def verify(data: verifyEmail, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == data.email).first()

    if not user:
        raise HTTPException(
            status_code=404, detail="No account was found for that email address."
        )

    verification_entry = (
        db.query(EmailVerificationModel)
        .filter(
            EmailVerificationModel.user_id == user.id,
            EmailVerificationModel.code == data.code,
            EmailVerificationModel.is_used == False,  # noqa: E712
            EmailVerificationModel.expires_at > datetime.utcnow(),
        )
        .first()
    )

    if not verification_entry:
        raise HTTPException(
            status_code=400,
            detail="That verification code is invalid or has expired. Please request a new code.",
        )

    user.is_active = True
    verification_entry.is_used = True
    db.commit()

    return {"message": "Your email has been verified. You can sign in now."}


@auth_router.post("/forgot-password")
def forgot_password(
    body: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Request a password-reset email for a registered address."""
    user = db.query(UserModel).filter(UserModel.email == body.email).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="No account was found for that email address.",
        )

    token = generate_password_reset_token()
    save_password_reset_token(db, user.id, token)
    background_tasks.add_task(send_password_reset_email, user.email, token)

    return {
        "message": "If that email is registered, password reset instructions have been sent. Please check your inbox.",
    }


@auth_router.post("/reset-password")
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Set a new password using the token from the reset email (API / Swagger)."""
    _apply_password_reset(
        db,
        email=body.email,
        token=body.token,
        new_password=body.new_password,
    )
    return {"message": "Your password has been updated. You can sign in now."}


@auth_router.get("/reset-password-form", response_class=HTMLResponse)
def reset_password_form_page(
    email: str = Query(default=""),
    token: str = Query(default=""),
):
    """
    Simple page opened from the email link.

    No separate frontend app required for this backend project.
    """
    return HTMLResponse(
        content=_password_reset_form_html(email=email, token=token)
    )


@auth_router.post("/reset-password-form", response_class=HTMLResponse)
def reset_password_form_submit(
    email: str = Form(...),
    token: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Handle the HTML form submit from the email link page."""
    if len(new_password) < 8:
        return HTMLResponse(
            status_code=400,
            content=_password_reset_form_html(
                email=email,
                token=token,
                error="Password must be at least 8 characters.",
            ),
        )

    if new_password != confirm_password:
        return HTMLResponse(
            status_code=400,
            content=_password_reset_form_html(
                email=email,
                token=token,
                error="Passwords do not match.",
            ),
        )

    try:
        _apply_password_reset(
            db, email=email, token=token, new_password=new_password
        )
    except HTTPException as exc:
        detail = (
            exc.detail
            if isinstance(exc.detail, str)
            else "We could not reset your password. Please try again."
        )
        return HTMLResponse(
            status_code=exc.status_code,
            content=_password_reset_form_html(
                email=email, token=token, error=detail
            ),
        )

    return HTMLResponse(
        content=_password_reset_form_html(
            message="Your password has been updated. You can sign in now.",
        )
    )
