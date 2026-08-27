from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.deps import require_admin
from app.schemas.category import CategoryCreate, CategoryResponse
from app.services import category_service
from app.core.response import success

router = APIRouter(prefix="/api/v1/category", tags=["category"])

@router.get("")
def get_all_category(db: Session = Depends(get_db)):
    categories = category_service.get_all(db)
    return success("Category Successfully GET", [CategoryResponse.model_validate(c) for c in categories])

@router.get("/{id}")
def get_category(id: int, db: Session = Depends(get_db)):
    try:
        category = category_service.get_by_id(db, id)
        return success("Category Successfully GET", CategoryResponse.model_validate(category))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("")
def create_category(payload: CategoryCreate, admin=Depends(require_admin),db=Depends(get_db)):
    category=category_service.create(db,payload)
    return success("Category Successfully POST", CategoryResponse.model_validate(category))

@router.put("/{id}")
def update_category(id: int, payload: CategoryCreate, admin=Depends(require_admin), db: Session = Depends(get_db)):
    try:
        category = category_service.update(db, id, payload)
        return success("Category Successfully PUT", CategoryResponse.model_validate(category))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{id}")
def delete_category(id: int, admin=Depends(require_admin), db: Session = Depends(get_db)):
    try:
        category = category_service.delete(db, id)
        return success("Category Successfully DELETE", CategoryResponse.model_validate(category))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))