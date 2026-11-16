from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, database
from .mpesa import mpesa_client

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI (title="TechHub E-Commerce")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def seed_products():
    db = database.SessionLocal()
    if db.query(models.Product).count() == 0:
        products = [
        models.Product(name="MacBook Pro M3", description="14-inch, 16GB RAM, 512GB SSD", price=180000, image_url="/static/images/laptop.jpg"),
        models.Product(name="Iphone 15 Pro", description="Titanium 128GB", price=140000, image_url="/static/images/phone.jpg"),
        models.Product(name="Sony WH-1000XM5", description="Noise Cancelling Headphones", price=35000, image_url="/static/images/headphones.jpg"),
        models.Product(name="iPad Air", description="10.9-inch, 64GB, Wi-Fi", price=65000, image_url="/static/images/ipad.jpg")
        ]
        db.add_all(products)
        db.commit()
    db.close()

# HTML ROUTES
@app.get("/", response_class=HTMLResponse)
async def storefront(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/cart", response_class=HTMLResponse)
async def cart_page(request: Request):
    return templates.TemplateResponse(request, "cart.html")

# API ROUTES
@app.get("/api/products", response_model=List[schemas.ProductResponse])
def get_products(db: Session = Depends(database.get_db)):
    return db.query(models.Product).all()

@app.post("/api/cart/add")
def add_to_cart(item: schemas.CartItemAdd, db: Session = Depends(database.get_db)):
    product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart_item = db.query(models.CartItem).filter(models.CartItem.product_id == item.product_id).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = models.CartItem(product_id=item.product_id)
        db.add(cart_item)

    db.commit()
    return {"message": "Added to cart"}

@app.get("/api/cart", response_model=schemas.CartResponse)
def get_cart(db: Session = Depends(database.get_db)):
    cart_items = db.query(models.CartItem).all()
    response_items = []
    cart_total = 0.0

    for item in cart_items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        item_total = product.price * item.quantity
        cart_total += item_total

        response_items.append(schemas.CartItemResponse(
            id=item.id, product_id=product_id, quantity=item.quantity,
            name=product.name, price=product.price, image_url=product.image_url, total=item_total
        ))

    return schemas.CartResponse(items=response_items, cart_total=cart_total)

@app.delete("/api/cart/{item_id}")
def remove_from_cart(item_id: int, db : Session = Depends(database.get_db)):
    item = db.query(models.CartItem).filter(models.CartItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": "Removed"}

# CHECKOUT & MPESA
@app.post("/api/checkout")
def checkout(payload: schemas.CheckoutRequest, db: Session = Depends(database.get_db)):
    cart_items = db.query(models.CartItem).all
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Calculate Total
    total = sum(db.query(models.Product).filter(models.Product.id == i.product_id).first().price * i.quantity for i in cart_items)

    # Create Order
    order = models.Order(total_amount=total, phone_number=payload.phone_number)
    db.add(order)
    db.commit()
    db.refresh(order)

    # Trigger M-Pesa
    mpesa_res = mpesa_client.stk_push(payload.phone_number, total)

    if "CheckoutRequestID" in mpesa_res:
        order.checkout_request_id = mpesa_res["CheckoutRequestID"]
        db.commit()
        return {"status": "success", "message": "STK Push sent. Check your phone."}
    else:
        order.status = "failed"
        db.commit()
        raise HTTPException(status_code=400, detail=mpesa_res.get("error", "M-Pesa failed"))

@app.post("/api/callback")
async def mpesa_callback(request: Request, db: Session = Depends(database.get_db)):
    data = await request.json()
    stk = data.get("Body", {}).get("stkCallback", {})

    checkout_id = stk.get("CheckoutRequestID")
    result_code = stk.get("ResultCode")

    if result_code == 0:
        order = db.query(models.Order).filter(models.Order.checkout_request_id == checkout_id).first()
        if order:
            order.status = "paid"
            # Clear the cart upon successful payment
            db.query(models.CartItem).delete()
            db.commit()

    return JSONResponse(content={"ResultCode": 0, "ResultDesc": "Success"})