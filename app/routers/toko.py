from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.deps import get_current_user
from app.schemas.toko import TokoResponse
from app.services import toko_service
from app.core.response import success
import os, time

router = APIRouter(prefix="/api/v1/toko", tags=["toko"])

@router.get("/my")
def get_my_toko(user=Depends(get_current_user), db:Session= Depends(get_db)):
    try:
        toko=toko_service.get_my(db,user.id)
        return success("Toko Successfully GET", TokoResponse.model_validate(toko))
    except ValueError as e:
        raise HTTPException(404, detail=str(e))

@router.get("")
def get_all_toko(page: int = 1, limit: int = 10, nama: str = "", db: Session = Depends(get_db)):
    offset = (page - 1) * limit
    tokos = toko_service.get_all(db, limit, offset, nama)
    return success("Toko Successfully GET", [TokoResponse.model_validate(t) for t in tokos])

@router.get("/{id}")
def get_toko(id: int, db: Session = Depends(get_db)):
    try:
        toko = toko_service.get_by_id(db, id)
        return success("Toko Successfully GET", TokoResponse.model_validate(toko))
    except ValueError as e:
        raise HTTPException(404, str(e))

@router.put("/{id}")
def update_toko(id: int, nama_toko: str = Form(...), photo: UploadFile = File(None),user=Depends(get_current_user), db: Session = Depends(get_db)):
    url=None
    if photo:
        os.makedirs("uploads",exist_ok=True)
        url=f"{int(time.time())}-{photo.filename}"
        with open(f"uploads/{url}","wb") as f:
            f.write(photo.file.read())
    try:
        toko=toko_service.update_toko(db,id,user.id,nama_toko,url)
        return success("Toko Successfully PUT", TokoResponse.model_validate(toko))
    except ValueError as e:
        raise HTTPException(404, str(e))
    