# Mini-Shop: Go → Python FastAPI Recreation Guide

This document analyzes the existing **Go (Gin + GORM + MySQL)** e-commerce API and gives you a complete plan to rebuild it in **Python + FastAPI**. It's an Evermos-style marketplace: users register, each user automatically gets a shop (`toko`), sellers list products, and buyers place transactions that snapshot product prices for historical accuracy.

> **Note:** The project's `README.md` describes a "loan-credit-risk" data-science project. That README does **not** match the code and should be ignored — it looks like a leftover template.

---

## 1. The original architecture

The Go project uses **Clean Architecture** with four layers plus a shared `domain` package that holds both models and interfaces:

```
Request → router → handler → usecase → repository → database
                                ↑
                            domain (structs + interfaces)
```

| Layer | Go folder | Responsibility | FastAPI equivalent |
|-------|-----------|----------------|--------------------|
| Router | `router/` | URL → handler mapping, middleware | `APIRouter` in `routers/` |
| Handler | `handler/` | Parse request, call usecase, format response | Route functions in `routers/` |
| Usecase | `usecase/` | Business logic | `services/` |
| Repository | `repository/` | DB queries (GORM) | `repositories/` or CRUD in `services/` |
| Domain | `domain/` | Models + interfaces | `models/` (SQLAlchemy) + `schemas/` (Pydantic) |
| Middleware | `middleware/` | JWT auth, admin check | FastAPI `Depends()` |
| Utils | `utils/` | JWT, response envelope | `core/security.py`, `core/response.py` |

**Key idea to preserve:** dependency injection. In Go, `main.go` builds each repository, injects it into a usecase, and injects that into the router. In FastAPI you get the same effect with `Depends()` — inject a DB session into a service, and a service into a route.

---

## 2. Data model (9 tables)

All tables use soft-deletes (`deleted_at`) and timestamps. Names are Indonesian.

```
user ──1:1── toko ──1:N── produk ──1:N── foto_produk
 │                          │
 │                          └── belongs to category
 ├──1:N── alamat
 └──1:N── trx ──1:N── detail_trx ──N:1── log_produk
              │
              └── ships to alamat
```

| Table | Fields (core) | Notes |
|-------|---------------|-------|
| `user` | nama, kata_sandi (hashed), no_telp (unique), tanggal_lahir, jenis_kelamin, tentang, pekerjaan, email (unique), provinsi_id, kota_id, is_admin | Login is by `no_telp` |
| `toko` | user_id, nama_toko, url_foto | Auto-created at register |
| `alamat` | user_id, judul_alamat, nama_penerima, no_telp, detail_alamat | Shipping addresses |
| `category` | nama_category | Admin-only writes |
| `produk` | nama_produk, slug, harga_reseller, harga_konsumen, stok, deskripsi, toko_id, category_id | Slug auto-generated |
| `foto_produk` | produk_id, url | Multiple images per product |
| `log_produk` | full copy of produk fields + produk_id | **Price snapshot at purchase** |
| `trx` | user_id, alamat_kirim_id, harga_total, kode_invoice, method_bayar | The order |
| `detail_trx` | trx_id, log_produk_id, toko_id, kuantitas, harga_total | Order line item → points at snapshot |

**Why `log_produk` matters:** when a purchase happens, the product is *copied* into `log_produk`, and the order line (`detail_trx`) references that copy — never the live product. So if the seller later changes the price or deletes the product, the historical order still shows what was actually bought. Replicate this exactly.

---

## 3. Core business logic to replicate

**Register** — hash password (bcrypt) → create user → **auto-create a shop** named `Toko-{nama}` for them. Every user is a seller.

**Login** — find user by `no_telp` → verify bcrypt hash → issue JWT (24h) with claims `{id, email, is_admin}`. Return the *same* generic error for "user not found" and "wrong password".

**Auth** — token comes from a custom `token` header (not `Authorization: Bearer`). Validate, then expose `user_id` and `is_admin` to the handler. Admin-only routes additionally check `is_admin`.

**Create transaction** (the crown jewel):
1. Verify the shipping address belongs to the buyer.
2. Generate invoice `INV-{unix_timestamp}`.
3. Create the `trx` with `harga_total = 0`.
4. For each item: fetch product → check `stok >= kuantitas` → snapshot into `log_produk` → line total = `harga_konsumen × kuantitas` → create `detail_trx` referencing the snapshot → decrement product stock.
5. Sum line totals into `trx.harga_total` and save.
   *(Wrap steps 3–5 in a DB transaction so a mid-order failure rolls back.)*

**Ownership checks** — products (via `toko_id`), addresses (via `user_id`), and shops (via `user_id`) all verify the logged-in user owns the resource before update/delete.

**Product listing** — dynamic filters: name (LIKE), category_id, toko_id, min/max price, plus `page`/`limit` pagination. Eager-load shop, category, and photos.

**Response envelope** — every response is `{status, message, errors, data}`.

---

## 4. API endpoints (base `/api/v1`)

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/auth/register` | – | Register + auto-shop |
| POST | `/auth/login` | – | Returns JWT |
| GET | `/user` | ✓ | Own profile |
| PUT | `/user` | ✓ | Update own profile |
| GET/POST | `/user/alamat` | ✓ | List / create address |
| GET/PUT/DELETE | `/user/alamat/{id}` | ✓ (owner) | Address by id |
| GET | `/toko` | – | List shops (paginated) |
| GET | `/toko/my` | ✓ | Own shop |
| GET | `/toko/{id}` | – | Shop by id |
| PUT | `/toko/{id}` | ✓ (owner) | Update shop (multipart photo) |
| GET | `/category`, `/category/{id}` | – | List / detail |
| POST/PUT/DELETE | `/category`, `/category/{id}` | ✓ admin | Manage categories |
| GET | `/product`, `/product/{id}` | – | List (filters) / detail |
| POST/PUT/DELETE | `/product`, `/product/{id}` | ✓ (owner) | Manage products (multipart images) |
| GET/POST | `/trx` | ✓ | List / create order |
| GET | `/trx/{id}` | ✓ (owner) | Order detail |

---

## 5. FastAPI project structure

```
mini-shop/
├── main.py                 # FastAPI app, mounts routers, static /uploads
├── requirements.txt
├── .env
├── app/
│   ├── core/
│   │   ├── config.py       # pydantic-settings, reads .env
│   │   ├── database.py     # SQLAlchemy engine + SessionLocal + get_db
│   │   ├── security.py     # bcrypt hashing, JWT create/verify
│   │   └── response.py     # success/error envelope helpers
│   ├── models/             # SQLAlchemy ORM models (one file per table or grouped)
│   │   ├── user.py, toko.py, alamat.py, category.py
│   │   ├── produk.py, foto_produk.py, log_produk.py
│   │   └── trx.py, detail_trx.py
│   ├── schemas/            # Pydantic request/response models
│   │   ├── user.py, auth.py, alamat.py, category.py
│   │   ├── produk.py, toko.py, trx.py
│   ├── deps.py             # Depends(): get_db, get_current_user, require_admin
│   ├── services/           # business logic (= usecase layer)
│   │   ├── auth_service.py, user_service.py, alamat_service.py
│   │   ├── category_service.py, toko_service.py
│   │   ├── produk_service.py, trx_service.py
│   └── routers/            # APIRouters (= handler + router layers)
│       ├── auth.py, user.py, alamat.py, category.py
│       ├── toko.py, produk.py, trx.py
└── uploads/                # served static files
```

### Dependency mapping

| Go | Python |
|----|--------|
| Gin | FastAPI + Uvicorn |
| GORM | SQLAlchemy 2.x |
| `go-sql-driver/mysql` | PyMySQL (`mysql+pymysql://`) |
| `golang-jwt/jwt` | python-jose (or PyJWT) |
| `bcrypt` | passlib[bcrypt] |
| `godotenv` | pydantic-settings |
| GORM AutoMigrate | `Base.metadata.create_all` (or Alembic) |
| Gin middleware | FastAPI `Depends()` |

`requirements.txt`:
```
fastapi
uvicorn[standard]
sqlalchemy
pymysql
passlib[bcrypt]
python-jose[cryptography]
pydantic-settings
python-multipart
```

---

## 6. Key code translations

### 6.1 Config & database (`core/config.py`, `core/database.py`)
```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    JWT_SECRET: str
    SERVER_PORT: int = 8080
    class Config:
        env_file = ".env"

settings = Settings()

# core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

DATABASE_URL = (
    f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4"
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 6.2 A model with soft-delete + timestamps (`models/produk.py`)
```python
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Produk(Base):
    __tablename__ = "produk"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True, index=True)  # soft delete
    nama_produk = Column(String(255))
    slug = Column(String(255))
    harga_reseller = Column(Integer)
    harga_konsumen = Column(Integer)
    stok = Column(Integer)
    deskripsi = Column(String(1000))
    toko_id = Column(Integer, ForeignKey("toko.id"))
    category_id = Column(Integer, ForeignKey("category.id"))
    toko = relationship("Toko")
    category = relationship("Category")
    photos = relationship("FotoProduk", back_populates="produk")
```
> GORM's `gorm.Model` gives you id/created_at/updated_at/deleted_at automatically. In SQLAlchemy, put these four columns on a shared mixin and inherit it everywhere. For soft-delete filtering (GORM does it silently), add `.filter(Model.deleted_at.is_(None))` to every read, or use a SQLAlchemy event/`with_loader_criteria`.

### 6.3 Security (`core/security.py`)
```python
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt
from app.core.config import settings

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p): return pwd.hash(p)
def verify_password(p, h): return pwd.verify(p, h)

def create_token(user_id: int, email: str, is_admin: bool) -> str:
    payload = {
        "id": user_id, "email": email, "is_admin": is_admin,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
```

### 6.4 Auth dependency = middleware (`deps.py`)
```python
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from jose import JWTError
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User

def get_current_user(token: str = Header(...), db: Session = Depends(get_db)) -> User:
    # NOTE: original API reads a custom "token" header, not Authorization: Bearer
    try:
        claims = decode_token(token)
    except JWTError:
        raise HTTPException(401, "Unauthorized")
    user = db.query(User).filter(User.id == claims["id"],
                                 User.deleted_at.is_(None)).first()
    if not user:
        raise HTTPException(401, "Unauthorized")
    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(401, "Unauthorized")
    return user
```

### 6.5 Register with auto-shop (`services/auth_service.py`)
```python
def register(db: Session, data: RegisterSchema):
    user = User(**data.dict(exclude={"kata_sandi"}),
                kata_sandi=hash_password(data.kata_sandi))
    db.add(user); db.flush()                 # get user.id without committing
    db.add(Toko(nama_toko=f"Toko-{user.nama}", user_id=user.id))
    db.commit()
```

### 6.6 Create transaction (`services/trx_service.py`)
```python
def create_trx(db: Session, user: User, payload: TrxInput):
    alamat = db.query(Alamat).filter(Alamat.id == payload.alamat_kirim).first()
    if not alamat or alamat.user_id != user.id:
        raise HTTPException(400, "alamat not found or unauthorized")

    trx = Trx(user_id=user.id, alamat_kirim_id=payload.alamat_kirim,
              method_bayar=payload.method_bayar,
              kode_invoice=f"INV-{int(time.time())}", harga_total=0)
    db.add(trx); db.flush()

    total = 0
    for item in payload.detail_trx:
        produk = db.query(Produk).filter(Produk.id == item.product_id).first()
        if not produk:
            raise HTTPException(400, "product not found")
        if produk.stok < item.kuantitas:
            raise HTTPException(400, "insufficient stock")

        log = LogProduk(produk_id=produk.id, nama_produk=produk.nama_produk,
                        slug=produk.slug, harga_reseller=produk.harga_reseller,
                        harga_konsumen=produk.harga_konsumen, stok=produk.stok,
                        deskripsi=produk.deskripsi, toko_id=produk.toko_id,
                        category_id=produk.category_id)
        db.add(log); db.flush()

        line = produk.harga_konsumen * item.kuantitas
        total += line
        db.add(DetailTrx(trx_id=trx.id, log_produk_id=log.id,
                         toko_id=produk.toko_id, kuantitas=item.kuantitas,
                         harga_total=line))
        produk.stok -= item.kuantitas

    trx.harga_total = total
    db.commit(); db.refresh(trx)
    return trx
```

### 6.7 A router (`routers/produk.py`)
```python
router = APIRouter(prefix="/api/v1/product", tags=["product"])

@router.get("")
def list_produk(page: int = 1, limit: int = 10, nama_produk: str = "",
                category_id: int = 0, toko_id: int = 0,
                max_harga: int = 0, min_harga: int = 0,
                db: Session = Depends(get_db)):
    items = produk_service.find_all(db, page, limit, nama_produk,
                                    category_id, toko_id, max_harga, min_harga)
    return success("Succeed to GET data", {"data": items, "page": page, "limit": limit})

@router.post("")
def create_produk(nama_produk: str = Form(...), harga_konsumen: int = Form(...),
                  # ...other Form fields...
                  photos: list[UploadFile] = File(default=[]),
                  user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    created = produk_service.create(db, user, ...)
    # save each photo to ./uploads/{timestamp}-{filename}, insert FotoProduk
    return success("Succeed to POST data", created.id)
```

### 6.8 Response envelope (`core/response.py`)
```python
def success(message, data=None):
    return {"status": True, "message": message, "errors": None, "data": data}

def error(message, errors=None):
    return {"status": False, "message": message, "errors": errors, "data": None}
```
> For a consistent envelope on validation/HTTP errors too, register a FastAPI exception handler for `RequestValidationError` and `HTTPException` that wraps them in `error(...)`.

### 6.9 App entry (`main.py`)
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.database import Base, engine
from app.routers import auth, user, alamat, category, toko, produk, trx

Base.metadata.create_all(bind=engine)          # like GORM AutoMigrate
app = FastAPI(title="Mini Shop")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
for r in (auth, user, alamat, category, toko, produk, trx):
    app.include_router(r.router)
# run: uvicorn main:app --reload --port 8080
```

---

## 7. Build order (recommended)

1. **Scaffold** — folders, `requirements.txt`, `.env`, `config`, `database`.
2. **Models** — all 9 SQLAlchemy models with the timestamp/soft-delete mixin; run `create_all` and confirm tables appear in MySQL.
3. **Security + response helpers** — hashing, JWT, envelope.
4. **Auth** — register (with auto-shop) + login; test getting a token.
5. **Deps** — `get_current_user`, `require_admin`.
6. **User + Alamat** — CRUD with ownership checks.
7. **Category** — with admin guard.
8. **Toko + Produk** — including multipart file uploads to `/uploads`.
9. **Trx** — the transaction flow with snapshotting, inside a DB transaction.
10. **Polish** — exception handlers for the uniform envelope, pagination, filters.

---

## 8. Things to watch / decisions to make

- **Custom `token` header:** the Go API reads a raw `token` header. FastAPI convention is `Authorization: Bearer`. Decide whether to keep the original (drop-in compatible with any existing client) or modernize. The guide above keeps the original.
- **Soft-delete:** GORM hides deleted rows automatically; SQLAlchemy does not. Add the `deleted_at IS NULL` filter everywhere, or centralize it.
- **DB transaction for orders:** the Go code doesn't wrap the order loop in an explicit transaction, so a failure mid-loop can leave partial data. In FastAPI, do the whole `create_trx` in one session/commit so it rolls back cleanly — a genuine improvement.
- **Password in responses:** never serialize `kata_sandi`. Use a Pydantic response schema that omits it (the Go code maps to a separate `UserResponse` for the same reason).
- **`.env` secrets:** the original `.env` contains a real-looking DB password and JWT secret. Rotate these and never commit the file.
- **Money as int:** prices are stored as integers (whole rupiah). Keep that — avoid floats for currency. (The Go `trx.harga_total` is a float; you can keep it int for cleanliness.)
- **Migrations:** `create_all` is fine to start, but adopt **Alembic** once the schema stabilizes for versioned migrations.
```
