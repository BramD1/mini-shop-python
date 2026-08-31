from pydantic import BaseModel, ConfigDict

class DetailTrxInput(BaseModel):
    product_id: int
    kuantitas: int

class TrxInput(BaseModel):
    method_bayar: str
    alamat_kirim: int
    detail_trx: list[DetailTrxInput]

class TrxResponse(BaseModel):
    id: int
    harga_total: int
    kode_invoice: str
    metode_bayar: str
    model_config = ConfigDict(from_attributes=True)