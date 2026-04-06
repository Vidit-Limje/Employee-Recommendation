# =====================================================
# AUTH ROUTES (JWT + OAUTH2 COMPATIBLE)
# =====================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from database.database import get_db
from models.user_account import UserAccount
from models.employee import Employee
from utils.auth import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth", tags=["Auth"])


# -----------------------------------------------------
# SIGNUP
# -----------------------------------------------------

@router.post("/signup")
def signup(
    email: str,
    password: str,
    firstname: str,
    db: Session = Depends(get_db)
):
    # 🔍 Check if user already exists
    existing_user = db.query(UserAccount).filter(UserAccount.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # 🔐 Create user
    user = UserAccount(
        email=email,
        password_hash=hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 👤 Create linked employee
    employee = Employee(
        firstname=firstname,
        user_id=user.user_id
    )
    db.add(employee)
    db.commit()

    return {"message": "User created successfully"}


# -----------------------------------------------------
# LOGIN (OAUTH2 COMPATIBLE)
# -----------------------------------------------------

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # ⚠️ Swagger sends "username" → we treat it as email
    user = db.query(UserAccount).filter(
        UserAccount.email == form_data.username
    ).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # 🔗 Get employee
    employee = db.query(Employee).filter(
        Employee.user_id == user.user_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    # 🎟️ Create JWT
    token = create_token(user, employee)

    return {
        "access_token": token,
        "token_type": "bearer"
    }