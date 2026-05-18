from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..auth import verify_token

from .. import models, schemas
from ..deps import get_db

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.post("/")
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db)
):

    new_product = models.Product(
        name=product.name,
        quantity=product.quantity
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product

@router.get("/")
def get_products(
    db: Session = Depends(get_db)
):

    products = db.query(models.Product).all()

    return products

@router.put("/{product_id}")
def update_product(
    product_id: int,
    product: schemas.ProductUpdate,
    db: Session = Depends(get_db)
):

    db_product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if not db_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db_product.name = product.name
    db_product.quantity = product.quantity

    db.commit()
    db.refresh(db_product)

    return db_product

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):

    db_product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if not db_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(db_product)
    db.commit()

    return {
        "message": "Product deleted"
    }

@router.get("/out-of-stock")
def out_of_stock(
    db: Session = Depends(get_db)
):

    products = db.query(models.Product).filter(
        models.Product.quantity == 0
    ).all()

    return products

@router.get("/low-stock")
def low_stock(
    db: Session = Depends(get_db)
):

    products = db.query(models.Product).filter(
        models.Product.quantity < 5
    ).all()

    return products


@router.patch("/{product_id}/quantity")
def update_quantity(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):

    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    product.quantity = quantity

    db.commit()
    db.refresh(product)

    return product