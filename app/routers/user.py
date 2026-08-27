from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.deps import get_current_user
from app.schemas.user import UserUpdate
from app.schemas.auth import UserResponse
from app.services import user_service
from app.core.response import success

router=APIRouter(prefix="/api/v1/user", tags=["user"])

@router.get("")
def get_user(user=Depends(get_current_user)):
    return success("Succeed to GET data", UserResponse.model_validate(user))

@router.put("")
def update_user(payload:UserUpdate, user=Depends(get_current_user), db:Session=Depends(get_db)):
    updated=user_service.update_user(db,user,payload)
    return success("Succeed to PUT data", UserResponse.model_validate(updated))
