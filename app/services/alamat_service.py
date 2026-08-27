from sqlalchemy.orm import Session
from app.models.alamat import Alamat
from datetime import datetime

def get_my(db:Session, user_id):
    return db.query(Alamat).filter(Alamat.user_id==user_id, Alamat.deleted_at.is_(None)).all()

def get_by_id(db:Session, id:int, user_id):
    result=db.query(Alamat).filter(Alamat.id==id, Alamat.deleted_at.is_(None)).first()
    if result is None:
        raise ValueError("Alamat tidak ditemukan")
    if result.user_id != user_id:
        raise ValueError("unauthorized")
    return result

def create(db:Session,data,user_id):
    alamat=Alamat(judul_alamat=data.judul_alamat, nama_penerima=data.nama_penerima,no_telp=data.no_telp,detail_alamat=data.detail_alamat, user_id=user_id)
    db.add(alamat)
    db.commit()
    db.refresh(alamat)
    return alamat

def update(db: Session, id: int, data, user_id):
    alamat = get_by_id(db, id, user_id)   # fetch + ownership
    alamat.judul_alamat = data.judul_alamat
    alamat.nama_penerima = data.nama_penerima
    alamat.no_telp = data.no_telp
    alamat.detail_alamat = data.detail_alamat
    db.commit()
    return alamat


def delete(db:Session,id:int,user_id):
    alamat=get_by_id(db,id, user_id)
    alamat.deleted_at=datetime.now()
    db.commit()
    return alamat
    