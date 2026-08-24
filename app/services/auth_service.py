from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.models.toko import Toko
from app.core.security import hash_password, validate_password, create_access_token

def register(db:Session, data):
    try:
        user = User(
            nama=data.nama, kata_sandi=hash_password(data.kata_sandi),
            no_telp=data.no_telp, email=data.email,
            tanggal_lahir=data.tanggal_lahir, jenis_kelamin=data.jenis_kelamin,
            tentang=data.tentang, pekerjaan=data.pekerjaan,
            provinsi=data.provinsi, kota=data.kota,
        )
        db.add(user)
        db.flush()
        toko=Toko(nama_toko=f"Toko-{user.nama}", user_id=user.id)
        db.add(toko)
        db.commit()
        return user
    except IntegrityError:
        db.rollback()
        raise ValueError("Nomor telepon atau email sudah terdaftar") 

def login(db: Session, no_telp, kata_sandi):
    user = db.query(User).filter( User.no_telp == no_telp, User.deleted_at.is_(None)).first()
    if user is None or not validate_password(kata_sandi, user.kata_sandi):
        raise ValueError("No Telp atau kata sandi salah")
    user.token = create_access_token(user.id, user.email, user.is_admin)
    return user