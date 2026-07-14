from fastapi import APIRouter,  HTTPException, Depends
from db.session import get_db
from schemas.user import UserCreate, verifyEmail 
from core.email import generate_verification_code, send_verification_code, save_verification_code
from db.models import User as UserModel
from db.models import EmailVerification as EmailVerificationModel
from sqlalchemy.orm import Session
from core.jwt import create_access_token
from core.security import hash_password
from core.security import verify_password
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/Signup")
def Signup(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(UserModel).filter(UserModel.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    if db.query(UserModel).filter(UserModel.username == user.username).first():
        raise HTTPException(status_code=400, detail="username already exists")

    hashed = hash_password(user.password)

    new_user = UserModel(
        username=user.username, email=user.email, hashed_password=hashed
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    generate_code = generate_verification_code()
    send_verification_code(user.email, generate_code)
    save_verification_code(db, new_user.id, generate_code)


    return {"message": "User created successfully. Please check your email to verify your account."}

    

@auth_router.post("/Login")
def Login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):

    db_user = (
        db.query(UserModel).filter(UserModel.username == form_data.username).first()
    )

    if not db_user.is_active:
        raise HTTPException(status_code=403, detail="Please verify your email before logging in")
    
    if not db_user:
        raise HTTPException(status_code=401, detail="invaild credentials")

    if not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="invaild credentials")

    access_token = create_access_token(
        data={"sub": db_user.username, "user_id": db_user.id}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/verify-email")
def verify(data: verifyEmail, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    verification_entry = (
        db.query(EmailVerificationModel).filter(
            EmailVerificationModel.user_id == user.id,
            EmailVerificationModel.code == data.code,
            EmailVerificationModel.is_used == False,
            EmailVerificationModel.expires_at > datetime.utcnow(),
    )).first() 
    
    if not verification_entry:
        raise HTTPException(status_code=400, detail="Invaild or expired verification code")
    
    if verification_entry.is_used:
        raise HTTPException(status_code=400, detail="verification code has already been used")
    
    user.is_active = True
    verification_entry.is_used = True
    db.commit()

    return {"message": "Email verified successfully."}


    
