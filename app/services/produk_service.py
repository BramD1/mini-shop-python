from sqlalchemy.orm import Session
from app.models.produk import Produk
from app.models.toko import Toko
from datetime import datetime


def get_all(db: Session, limit, offset, nama, category_id, toko_id, max_harga, min_harga):
    q=db.query(Produk).filter(Produk.deleted_at.is_(None))
    if nama: q = q.filter(Produk.nama_produk.like(f"%{nama}%"))
    if category_id: q = q.filter(Produk.category_id == category_id)
    if toko_id: q = q.filter(Produk.toko_id == toko_id)
    if min_harga: q = q.filter(Produk.harga_konsumen >= min_harga)
    if max_harga: q = q.filter(Produk.harga_konsumen <= max_harga)
    return q.limit(limit).offset(offset).all()

def get_by_id(db: Session, id):
    q=db.query(Produk).filter(Produk.id==id, Produk.deleted_at.is_(None)).first()
    if q is None:
        raise ValueError("Produk not found")
    return q

def create(db: Session, data, user_id):
    toko=db.query(Toko).filter(Toko.user_id == user_id).first()
    if toko is None:
        raise ValueError("Toko not found")
    produk=Produk(
        nama_produk=data.nama_produk, 
        slug=data.nama_produk.lower().replace(" ","-"),
        harga_seller=data.harga_seller,
        harga_konsumen=data.harga_konsumen, 
        stok=data.stok, 
        deskripsi=data.deskripsi, 
        toko_id=toko.id, 
        category_id=data.category_id)
    db.add(produk)
    db.commit()
    db.refresh(produk)
    return produk

def update(db: Session, id, user_id, data):
    produk=get_by_id(db,id)
    toko=db.query(Toko).filter(Toko.user_id==user_id).first()
    if toko is None or produk.toko_id != toko.id:
        raise ValueError("unauthorized")
    produk.nama_produk=data.nama_produk
    produk.slug=data.nama_produk.lower().replace(" ","-")
    produk.harga_seller=data.harga_seller
    produk.harga_konsumen=data.harga_konsumen
    produk.stok=data.stok
    produk.deskripsi=data.deskripsi
    produk.category_id=data.category_id
    db.commit()
    return produk

def delete(db:Session,id,user_id):
    produk=get_by_id(db,id)
    toko=db.query(Toko).filter(Toko.user_id==user_id).first()
    if toko is None or produk.toko_id != toko.id:
        raise ValueError("unauthorized")
    produk.deleted_at=datetime.now()
    db.commit()
    return produk