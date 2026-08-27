from pydantic import BaseModel
from datetime import date

class UserUpdate(BaseModel):
    nama: str | None = None
    no_telp: str | None = None
    email: str | None = None
    tanggal_lahir: date | None = None
    jenis_kelamin: str | None = None
    tentang: str | None = None
    pekerjaan: str | None = None
    provinsi: str | None = None
    kota: str | None = None
    kata_sandi: str | None = None
