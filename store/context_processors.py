from .models import Category
from .cart import CART_SESSION_KEY


def nav_context(request):
    categories = Category.objects.all()[:12]
    cart = request.session.get(CART_SESSION_KEY, {})
    cart_count = sum(item.get("quantity", 0) for item in cart.values())
    return {
        "nav_categories": categories,
        "cart_count": cart_count,
    }


