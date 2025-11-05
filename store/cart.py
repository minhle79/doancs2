from decimal import Decimal
from typing import Dict

from .models import Product


CART_SESSION_KEY = "cart"


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if not cart:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart: Dict[str, dict] = cart

    def add(self, product_id: int, quantity: int = 1, override: bool = False):
        pid = str(product_id)
        product = Product.objects.get(id=product_id)
        if pid not in self.cart:
            self.cart[pid] = {"quantity": 0, "price": str(product.price)}
        if override:
            self.cart[pid]["quantity"] = quantity
        else:
            self.cart[pid]["quantity"] += quantity
        self.save()

    def remove(self, product_id: int):
        pid = str(product_id)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.session.modified = True

    def save(self):
        self.session[CART_SESSION_KEY] = self.cart
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            item = self.cart[str(product.id)]
            item_data = {
                "product": product,
                "quantity": item["quantity"],
                "price": Decimal(item["price"]),
                "total": Decimal(item["price"]) * item["quantity"],
            }
            yield item_data

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def total_amount(self):
        return sum(Decimal(item["price"]) * item["quantity"] for item in self.cart.values())


