from pydantic import BaseModel, ConfigDict

class ProdukResponse(BaseModel):
    id: int
    nama_produk: str
    slug: str
    harga_seller: int
    harga_konsumen: int
    stok: int
    deskripsi: str
    toko_id: int
    category_id: int
    model_config = ConfigDict(from_attributes=True)