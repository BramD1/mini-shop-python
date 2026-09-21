# Project Title: Mini Shop Python

## Overview
This is my first backend project using mostly the FastAPI framework from python. Every user who register in this backend service will automatically have a store created for them.

## 🔧 Technologies Used
**Programming Language:** Python

**Framework:** FastAPI (Uvicorn ASGI server)

**Libraries:** SQLAlchemy, PyMySQL, Pydantic / pydantic-settings, python-jose (JWT), passlib[bcrypt]

**Database:** MySQL 8 (utf8mb4)

### 1️⃣ Prerequisites & Setup
Before running the API, the following must be ready:
1. Python 3.10+ environment with dependencies installed
   (`pip install fastapi uvicorn sqlalchemy pymysql pydantic-settings python-jose passlib[bcrypt] python-multipart`)
2. A running MySQL server with an empty database created (e.g. `toko_python_db`)
3. A `.env` file in the project root:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=toko_python_db
   JWT_SECRET=your_secret
   SERVER_PORT=8080
   ```
4. Create all tables:
   ```bash
   python init_db.py
   ```
5. Run the API:
   ```bash
   uvicorn main:app --reload
   ```
   Interactive docs are then available at `http://localhost:8000/docs`.

### 2️⃣ Architecture
The app follows a strict 4-layer pattern, repeated for every feature:

```
Router (HTTP)  →  Service (business logic)  →  Model (SQLAlchemy table)
                          ↑
                   Schema (Pydantic validation/serialization)
```

- **`app/core/`** — shared foundation: `config.py` (env settings), `database.py` (engine + `get_db` session), `security.py` (bcrypt + JWT), `response.py` (uniform JSON envelope)
- **`app/deps.py`** — auth guards: `get_current_user` (validates the `token` header) and `require_admin`
- **`app/models/`** — 9 database tables
- **`app/schemas/`** — request/response models
- **`app/services/`** — business logic (raise `ValueError` on failure)
- **`app/routers/`** — thin HTTP layer (convert errors to `HTTPException`, wrap results in `success(...)`)
- **`main.py`** — mounts all routers under `/api/v1/...` and serves uploaded images from `/uploads`

### 3️⃣ Database Design
A relational schema of 9 tables, all with `created_at`, `updated_at`, and a `deleted_at` **soft-delete** column:

- **user** — account + profile; `is_admin` flag; passwords hashed (`kata_sandi`)
- **toko** — a store, one auto-created per user at registration
- **category** — product categories (admin-managed)
- **produk** — a product (belongs to a toko + category; has stock and seller/consumer prices)
- **foto_produk** — product photos (files saved to `/uploads`)
- **alamat** — a user's shipping addresses
- **trx** — an order (invoice code, total, payment method, shipping address)
- **detail_trx** — order line items
- **log_produk** — a **snapshot** of a product at purchase time, so historical orders keep the price/details that applied when they were placed

### 4️⃣ Key Flows
- **Registration** — creates the `User` (password hashed), then in the same transaction auto-creates a `Toko` named `Toko-{nama}`.
- **Login** — verifies password, returns the user with a signed **JWT** (`user_id`, `email`, `is_admin`, 24h expiry). The token is sent back in later requests via the `token` header.
- **Create transaction** — verifies the shipping address belongs to the buyer, then for each item: checks stock, snapshots the product into `log_produk`, creates a `detail_trx` line, decrements stock, and accumulates the total before committing.

### 5️⃣ API Endpoints
All routes are prefixed with `/api/v1`.

**Auth** (public)
- `POST /auth/register` — register a new user (+ auto-store)
- `POST /auth/login` — log in, receive JWT

**User** (auth required)
- `GET /user` — get own profile
- `PUT /user` — update own profile

**Address** (auth required)
- `GET /user/alamat` · `GET /user/alamat/{id}` · `POST /user/alamat` · `PUT /user/alamat/{id}` · `DELETE /user/alamat/{id}`

**Category** (read public, write admin-only)
- `GET /category` · `GET /category/{id}` · `POST /category` · `PUT /category/{id}` · `DELETE /category/{id}`

**Toko / Store**
- `GET /toko` (public list) · `GET /toko/{id}` (public) · `GET /toko/my` (auth) · `PUT /toko/{id}` (auth, supports photo upload)

**Product** (read public, write auth)
- `GET /product` (list with pagination + filters: `nama_produk`, `category_id`, `toko_id`, `min_harga`, `max_harga`)
- `GET /product/{id}` · `POST /product` (multipart, photo upload) · `PUT /product/{id}` · `DELETE /product/{id}` (soft delete)

**Transaction** (auth required)
- `GET /trx` · `GET /trx/{id}` · `POST /trx`

Every response uses the shape: `{ "status": bool, "message": str, "errors": any, "data": any }`.

### 6️⃣ Conclusion & Suggestions
This backend project will provide repeatable architecture that will be used for later projects. For deployment, I usually do it with GCP, so containerize it with docker is the most necessary step. Before deployment however, end to end security testing will be required to avoid security attacks.