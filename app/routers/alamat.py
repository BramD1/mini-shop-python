from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.deps import get_current_user
from app.schemas.alamat import AlamatCreate, AlamatResponse
from app.services import alamat_service
from app.core.response import success

router=APIRouter(prefix="/api/v1/user/alamat", tags=["alamat"])

@router.get("")
def get_my_alamat(user=Depends(get_current_user), db: Session=Depends(get_db)):
    alamat=alamat_service.get_my(db, user.id)
    return success("Alamat Successfully GET", [AlamatResponse.model_validate(a) for a in alamat])

@router.get("/{id}")
def get_alamat_id(id:int,user=Depends(get_current_user), db: Session=Depends(get_db)):
    try:
        alamat=alamat_service.get_by_id(db,id,user.id)
        return success("Alamat Successfully GET", AlamatResponse.model_validate(alamat))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("")
def create_alamat(payload:AlamatCreate, user=Depends(get_current_user),db: Session=Depends(get_db)):
    alamat=alamat_service.create(db,payload,user.id)
    return success("Alamat Successfully POST", AlamatResponse.model_validate(alamat))

@router.put("/{id}")
def update_alamat(id: int,payload:AlamatCreate, user=Depends(get_current_user), db: Session=Depends(get_db)):
    try:
        alamat=alamat_service.update(db,id,payload,user.id)
        return success("Alamat Successfully PUT", AlamatResponse.model_validate(alamat))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{id}")
def delete_alamat(id:int, user=Depends(get_current_user), db: Session=Depends(get_db)):
    try:
        alamat=alamat_service.delete(db,id,user.id)
        return success("Alamat Successfully DELETE", AlamatResponse.model_validate(alamat))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
