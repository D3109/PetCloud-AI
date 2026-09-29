from sqlalchemy.orm import Session

from app.models.cart import Cart, CartItem
from app.models.product import Product


def get_or_create_cart(db: Session, user_id: int) -> Cart:
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if cart is None:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def add_item(db: Session, user_id: int, product_id: int, quantity: int) -> Cart:
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise ValueError(f"Product {product_id} not found")
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero")

    cart = get_or_create_cart(db, user_id)

    item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id, CartItem.product_id == product_id
    ).first()

    if item:
        item.quantity += quantity
    else:
        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.add(item)

    db.commit()
    db.refresh(cart)
    return cart


def remove_item(db: Session, user_id: int, product_id: int) -> Cart:
    cart = get_or_create_cart(db, user_id)
    item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id, CartItem.product_id == product_id
    ).first()
    if item is None:
        raise ValueError(f"Product {product_id} is not in the cart")

    db.delete(item)
    db.commit()
    db.refresh(cart)
    return cart


def to_out_dict(cart: Cart) -> dict:
    items = []
    total = 0
    for item in cart.items:
        subtotal = item.product.price * item.quantity
        total += subtotal
        items.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": item.product.name,
            "unit_price": item.product.price,
            "quantity": item.quantity,
            "subtotal": subtotal,
        })
    return {"id": cart.id, "items": items, "total": total}
