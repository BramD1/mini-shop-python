from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, UserResponse
from app.services import auth_service
from app.core.response import success

router=APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register")
def register(payload: RegisterRequest, db:Session=Depends(get_db)):
    try:
        auth_service.register(db, payload)
        return success("Succeed to POST data", "Register Succeed")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.post("/login")
def login(payload:LoginRequest,db:Session=Depends(get_db)):
    try:
        user=auth_service.login(db, payload.no_telp, payload.kata_sandi)
        return success("Succeed to POST data",UserResponse.model_validate(user))
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))