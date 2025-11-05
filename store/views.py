from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .cart import Cart
from .forms import CheckoutForm, SignupForm
from .models import Brand, Category, Order, OrderItem, Product


def home(request):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category")
    brand_slug = request.GET.get("brand")
    price_min = request.GET.get("min")
    price_max = request.GET.get("max")

    products = Product.objects.all()

    if query:
        products = products.filter(Q(name__icontains=query) | Q(short_description__icontains=query))
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)

    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    ctx = {
        "products": page_obj,
        "categories": Category.objects.all(),
        "brands": Brand.objects.all(),
        "q": query,
        "category_slug": category_slug,
        "brand_slug": brand_slug,
        "price_min": price_min or "",
        "price_max": price_max or "",
    }
    return render(request, "store/home.html", ctx)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, "store/product_detail.html", {"product": product})


def cart_detail(request):
    cart = Cart(request)
    return render(request, "store/cart.html", {"cart": cart})


def cart_add(request, product_id):
    cart = Cart(request)
    quantity = int(request.POST.get("quantity", 1))
    quantity = 1 if quantity < 1 else quantity
    cart.add(product_id, quantity=quantity)
    messages.success(request, "Đã thêm vào giỏ hàng")
    return redirect("cart_detail")


def cart_remove(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    messages.info(request, "Đã xóa khỏi giỏ hàng")
    return redirect("cart_detail")


@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Giỏ hàng trống")
        return redirect("home")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order: Order = form.save(commit=False)
            order.user = request.user
            order.total_amount = cart.total_amount()
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    quantity=item["quantity"],
                    price=item["price"],
                )
                # reduce stock
                p = item["product"]
                if p.stock >= item["quantity"]:
                    p.stock -= item["quantity"]
                    p.save(update_fields=["stock"])
            cart.clear()
            messages.success(request, "Đặt hàng thành công!")
            return redirect("home")
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                "full_name": request.user.get_full_name() or request.user.username,
                "email": request.user.email,
            }
        form = CheckoutForm(initial=initial)

    return render(request, "store/checkout.html", {"form": form, "cart": cart})


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            login(request, user)
            messages.success(request, "Đăng ký thành công!")
            return redirect("home")
    else:
        form = SignupForm()
    return render(request, "registration/signup.html", {"form": form})


def api_products(request):
    products = Product.objects.all().values(
        "id",
        "name",
        "slug",
        "price",
        "stock",
        "short_description",
        brand=models.F("brand__name"),
        category=models.F("category__name"),
    )
    return JsonResponse({"products": list(products)})


