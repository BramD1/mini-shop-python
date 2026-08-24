from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from jose import JWTError
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User

def get_current_user(token: str = Header(...), db: Session = Depends(get_db)) -> User:
    try:
        claims=decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user=db.query(User).filter(User.id==claims["user_id"], User.deleted_at.is_(None)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user

def require_admin(user: User = Depends(get_current_user))->User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return user
