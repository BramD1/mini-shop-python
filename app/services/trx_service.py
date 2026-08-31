from sqlalchemy.orm import Session
from app.models.trx import Trx
from app.models.detail_trx import DetailTrx
from app.models.log_produk import LogProduk
from app.models.produk import Produk
from app.models.alamat import Alamat
from datetime import datetime

def get_all(db: Session, user_id):
    return db.query(Trx).filter(Trx.user_id==user_id, Trx.deleted_at.is_(None)).all()

def get_by_id(db: Session, id, user_id):
    trx=db.query(Trx).filter(Trx.id==id, Trx.deleted_at.is_(None)).first()
    if trx is None or trx.user_id!=user_id:
        raise ValueError("unauthorized")
    return trx

def create_trx(db: Session, data, user_id):
    # 1) verify address ownership
    alamat = db.query(Alamat).filter(Alamat.id == data.alamat_kirim, Alamat.deleted_at.is_(None)).first()
    if alamat is None or alamat.user_id != user_id:
        raise ValueError("alamat not found or unauthorized")

    # 2) create the trx (empty total), flush to get its id
    trx = Trx(user_id=user_id, alamat_kirim_id=data.alamat_kirim,
            metode_bayar=data.method_bayar,
            kode_invoice=f"INV-{int(datetime.now().timestamp())}", harga_total=0)
    db.add(trx); db.flush()

    # 3) loop items
    total = 0
    for item in data.detail_trx:
        produk = db.query(Produk).filter(Produk.id == item.product_id, Produk.deleted_at.is_(None)).first()
        if produk is None:
            raise ValueError("product not found")
        if produk.stok < item.kuantitas:
            raise ValueError("stok tidak cukup")

        log = LogProduk(produk_id=produk.id, nama_produk=produk.nama_produk, slug=produk.slug,
                      harga_seller=produk.harga_seller, harga_konsumen=produk.harga_konsumen,
                      stok=produk.stok, deskripsi=produk.deskripsi,
                      toko_id=produk.toko_id, category_id=produk.category_id)
        db.add(log); db.flush()

        total += produk.harga_konsumen * item.kuantitas
        db.add(DetailTrx(trx_id=trx.id, log_produk_id=log.id, toko_id=produk.toko_id,
                       kuantitas=item.kuantitas, harga_satuan=produk.harga_konsumen))
        produk.stok -= item.kuantitas

    # 4) finalize
    trx.harga_total = total
    db.commit(); db.refresh(trx)
    return trx