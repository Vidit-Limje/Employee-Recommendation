from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from utils.auth import decode_token

# OAuth2 scheme (used in Swagger + auth flow)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """
    Extracts and validates JWT token.
    Also attaches user info to request.state for downstream usage
    (rate limiting, RBAC, logging, etc.)
    """

    # 🔐 Decode JWT
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # 🔐 Validate required fields
    if "role" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: role missing"
        )

    if "user_id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: user_id missing"
        )

    # ✅ Attach user to request (IMPORTANT for rate limiter)
    request.state.user = payload

    return payload