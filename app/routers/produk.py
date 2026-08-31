from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.deps import get_current_user
from app.schemas.produk import ProdukResponse
from app.services import produk_service
from app.models.foto_produk import FotoProduk
from app.core.response import success
from types import SimpleNamespace
import time
import os

router = APIRouter(prefix="/api/v1/product", tags=["product"])

@router.get("")
def get_all_produk(page: int = 1, limit: int = 10, nama_produk: str = "",
                   category_id: int = 0, toko_id: int = 0,
                   max_harga: int = 0, min_harga: int = 0,
                   db: Session = Depends(get_db)):
    offset=(page-1)*limit
    items=produk_service.get_all(db, limit, offset, nama_produk, category_id, toko_id, max_harga, min_harga)
    return success("Produk Successfully GET", [ProdukResponse.model_validate(p) for p in items])

@router.get("/{id}")
def get_produk(id: int, db: Session=Depends(get_db)):
    try:
        produk=produk_service.get_by_id(db,id)
        return success("Produk Successfully GET", ProdukResponse.model_validate(produk))
    except ValueError as e:
        raise HTTPException(404, str(e))

@router.post("")
def create_produk(nama_produk: str = Form(...), harga_seller: int = Form(...),
                  harga_konsumen: int = Form(...), stok: int = Form(...),
                  deskripsi: str = Form(...), category_id: int = Form(...),
                  photos: list[UploadFile] = File(default=[]),
                  user=Depends(get_current_user), db: Session = Depends(get_db)):
    data=SimpleNamespace(nama_produk=nama_produk, harga_seller=harga_seller,
                           harga_konsumen=harga_konsumen, stok=stok,
                           deskripsi=deskripsi, category_id=category_id)
    try:
        produk=produk_service.create(db,data,user.id)
    except ValueError as e:
        raise HTTPException(400, str(e))
    os.makedirs("uploads",exist_ok=True)
    for photo in photos:
        fn=f"{int(time.time())}-{photo.filename}"
        with open(f"uploads/{fn}", "wb") as f:
            f.write(photo.file.read())
        db.add(FotoProduk(produk_id=produk.id, url_foto=fn))
    db.commit()
    return success("Produk Successfully POST", ProdukResponse.model_validate(produk))

@router.put("/{id}")
def update_product(id:int, nama_produk: str = Form(...), harga_seller: int = Form(...),
                  harga_konsumen: int = Form(...), stok: int = Form(...),
                  deskripsi: str = Form(...), category_id: int = Form(...),
                  photos: list[UploadFile] = File(default=[]),
                  user=Depends(get_current_user), db: Session = Depends(get_db)):
    data=SimpleNamespace(nama_produk=nama_produk, harga_seller=harga_seller,
                           harga_konsumen=harga_konsumen, stok=stok,
                           deskripsi=deskripsi, category_id=category_id)
    try:
        produk=produk_service.update(db, id, user.id, data)
    except ValueError as e:
            raise HTTPException(400, str(e))
    os.makedirs("uploads",exist_ok=True)
    for photo in photos:
        fn=f"{int(time.time())}-{photo.filename}"
        with open(f"uploads/{fn}", "wb") as f:
            f.write(photo.file.read())
        db.add(FotoProduk(produk_id=produk.id, url_foto=fn))
    db.commit()
    return success("Produk Successfully PUT", ProdukResponse.model_validate(produk))  

@router.delete("/{id}")
def delete_produk(id:int,db: Session=Depends(get_db), user=Depends(get_current_user)):
    try:
        produk=produk_service.delete(db,id,user.id)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return success("Produk Successfully DELETE", ProdukResponse.model_validate(produk)) 
    