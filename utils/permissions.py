from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from utils.dependencies import get_current_user
from sqlalchemy import text

def require_permission(permission_name: str):

    def checker(
        user=Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        role = user["role"]

        result = db.execute(text("""
            SELECT 1
            FROM role_permission rp
            JOIN permission p ON rp.permission_id = p.permission_id
            WHERE rp.role_name = :role AND p.name = :perm
        """), {"role": role, "perm": permission_name}).fetchone()

        if not result:
            raise HTTPException(status_code=403, detail="Permission denied")

        return user

    return checker