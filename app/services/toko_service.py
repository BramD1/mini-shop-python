from sqlalchemy.orm import Session
from app.models.toko import Toko

def get_all(db: Session, limit, offset, nama):
    q = db.query(Toko).filter(Toko.deleted_at.is_(None))
    if nama:
        q = q.filter(Toko.nama_toko.like(f"%{nama}%"))
    return q.limit(limit).offset(offset).all()

def get_my(db: Session, user_id):
    toko = db.query(Toko).filter(Toko.user_id == user_id, Toko.deleted_at.is_(None)).first()
    if toko is None:
        raise ValueError("Toko not found")
    return toko

def get_by_id(db: Session, id):
    toko = db.query(Toko).filter(Toko.id == id, Toko.deleted_at.is_(None)).first()
    if toko is None:
        raise ValueError("Toko not found")
    return toko

def update_toko(db: Session, id, user_id, nama_toko=None, url_foto=None):
    toko = get_by_id(db, id)
    if toko.user_id != user_id:
        raise ValueError("unauthorized")
    if nama_toko is not None:
        toko.nama_toko = nama_toko
    if url_foto is not None:
        toko.url_foto = url_foto
    db.commit()
    return toko