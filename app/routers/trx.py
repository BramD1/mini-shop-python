from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.deps import get_current_user
from app.schemas.trx import TrxInput, TrxResponse
from app.services import trx_service
from app.core.response import success

router = APIRouter(prefix="/api/v1/trx", tags=["trx"])

@router.get("")
def get_all_trx(user=Depends(get_current_user), db: Session = Depends(get_db)):
    trxs = trx_service.get_all(db, user.id)
    return success("Trx Successfully GET", [TrxResponse.model_validate(t) for t in trxs])

@router.get("/{id}")
def get_trx(id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        trx = trx_service.get_by_id(db, id, user.id)
        return success("Trx Successfully GET", TrxResponse.model_validate(trx))
    except ValueError as e:
        raise HTTPException(404, str(e))

@router.post("")
def create_trx(payload: TrxInput, user=Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        trx = trx_service.create_trx(db, payload, user.id)
        return success("Trx Successfully POST", TrxResponse.model_validate(trx))
    except ValueError as e:
        raise HTTPException(400, str(e))