# =====================================================
# AUTH UTILS (JWT + PASSWORD HANDLING)
# =====================================================

from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

# 🔐 Secret (move to env later)
SECRET_KEY = "supersecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 1

# 🔑 Password hashing (bcrypt OR argon2)
pwd_context = CryptContext(
    schemes=["bcrypt"],  # or switch to "argon2"
    deprecated="auto"
)


# -----------------------------------------------------
# PASSWORD FUNCTIONS
# -----------------------------------------------------

def hash_password(password: str):
    if not password:
        raise ValueError("Password cannot be empty")

    # bcrypt max limit fix
    return pwd_context.hash(password[:72])


def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain[:72], hashed)


# -----------------------------------------------------
# JWT TOKEN CREATION
# -----------------------------------------------------

def create_token(user, employee):
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user.user_id),   # keep for JWT standard
        "user_id": user.user_id,    # 🔥 ADD THIS (required for your system)
        "eid": employee.eid,
        "role": user.role,
        "iat": now,
        "exp": now + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# -----------------------------------------------------
# JWT TOKEN DECODE
# -----------------------------------------------------

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except JWTError:
        return None