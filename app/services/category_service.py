from sqlalchemy.orm import Session
from app.models.category import Category
from datetime import datetime

def get_all(db:Session):
    return db.query(Category).filter(Category.deleted_at.is_(None)).all()

def get_by_id(db:Session,id):
    result=db.query(Category).filter(Category.id==id, Category.deleted_at.is_(None)).first()
    if result is None:
        raise ValueError ("Category tidak ditemukan")
    return result

def create(db:Session,data):
    category=Category(nama_category=data.nama_category)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def update(db:Session,id,data):
    category=get_by_id(db,id)
    category.nama_category=data.nama_category
    db.commit()
    return category

def delete(db:Session,id):
    category=get_by_id(db,id)
    category.deleted_at=datetime.now()
    db.commit()
    return category