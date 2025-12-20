from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, redirect, render

from .cart import Cart
from .forms import CheckoutForm, SignupForm, ProfileForm
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

    featured = Product.objects.filter(is_featured=True)[:8]
    deals = Product.objects.filter(is_deal=True)[:8]
    hot = Product.objects.filter(is_hot=True)[:8]
    ctx = {
        "products": page_obj,
        "featured": featured,
        "deals": deals,
        "hot": hot,
        "categories": Category.objects.all(),
        "brands": Brand.objects.all(),
        "q": query,
        "category_slug": category_slug,
        "brand_slug": brand_slug,
        "price_min": price_min or "",
        "price_max": price_max or "",
    }
    return render(request, "store/home.html", ctx)


def products(request):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category")
    brand_slug = request.GET.get("brand")
    sort = request.GET.get("sort")  # price_asc, price_desc, newest

    products = Product.objects.all()
    if query:
        products = products.filter(Q(name__icontains=query) | Q(short_description__icontains=query))
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)
    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    else:
        products = products.order_by("-created_at")

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
        "sort": sort or "",
    }
    return render(request, "store/products.html", ctx)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    # Lấy sản phẩm liên quan cùng danh mục, loại trừ sản phẩm hiện tại
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:8]
    
    return render(request, "store/product_detail.html", {
        "product": product,
        "related_products": related_products
    })


def cart_detail(request):
    cart = Cart(request)
    if request.GET.get("fragment") == "1":
        return render(request, "store/partials/cart_modal.html", {"cart": cart})
    return render(request, "store/cart.html", {"cart": cart})


def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get("quantity", 1))
    quantity = 1 if quantity < 1 else quantity
    buy_now = request.POST.get("buy_now", "0") == "1"
    
    # Check stock availability
    current_cart_quantity = cart.cart.get(str(product_id), {}).get("quantity", 0)
    total_quantity = current_cart_quantity + quantity
    
    if total_quantity > product.stock:
        error_message = f"Chỉ còn {product.stock} sản phẩm trong kho"
        if request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", ""):
            return JsonResponse({
                "ok": False,
                "message": error_message,
                "cart_count": len(cart),
            })
        messages.error(request, error_message)
        return redirect("product_detail", slug=product.slug)
    
    cart.add(product_id, quantity=quantity)
    
    # Nếu là "Mua ngay", chuyển thẳng đến trang thanh toán
    if buy_now:
        messages.success(request, "Đã thêm vào giỏ hàng. Tiến hành thanh toán.")
        return redirect("checkout")
    
    # AJAX/Fetch request detection
    if request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", ""):
        html = render_to_string("store/partials/cart_modal.html", {"cart": cart}, request=request)
        return JsonResponse({
            "ok": True,
            "message": "Đã thêm sản phẩm vào giỏ hàng!",
            "cart_count": len(cart),
            "modal": html,
        })
    messages.success(request, "Đã thêm vào giỏ hàng")
    return redirect("cart_detail")


def cart_remove(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    if request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", ""):
        html = render_to_string("store/partials/cart_modal.html", {"cart": cart}, request=request)
        return JsonResponse({
            "ok": True,
            "message": "Đã xóa sản phẩm khỏi giỏ hàng!",
            "cart_count": len(cart),
            "modal": html,
        })
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
            # Check stock availability before processing order
            insufficient_stock = []
            for item in cart:
                product = item["product"]
                if product.stock < item["quantity"]:
                    insufficient_stock.append(f"{product.name} (còn {product.stock})")
            
            if insufficient_stock:
                messages.error(request, f"Không đủ hàng: {', '.join(insufficient_stock)}")
                return render(request, "store/checkout.html", {"form": form, "cart": cart})
            
            # Use transaction to ensure atomicity
            try:
                with transaction.atomic():
                    # Create order
                    order: Order = form.save(commit=False)
                    order.user = request.user
                    order.total_amount = cart.total_amount()
                    order.save()
                    
                    # Create order items and reduce stock
                    for item in cart:
                        OrderItem.objects.create(
                            order=order,
                            product=item["product"],
                            quantity=item["quantity"],
                            price=item["price"],
                        )
                        # reduce stock
                        p = item["product"]
                        p.stock -= item["quantity"]
                        p.save(update_fields=["stock"])
                    
                    cart.clear()
                    messages.success(request, "Đặt hàng thành công!")
                    return redirect("home")
            except Exception as e:
                messages.error(request, f"Có lỗi xảy ra khi đặt hàng: {str(e)}")
                return render(request, "store/checkout.html", {"form": form, "cart": cart})
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
        brand_name=F("brand__name"),
        category_name=F("category__name"),
    )
    return JsonResponse({"products": list(products)})


def api_suggest(request):
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse({"results": []})
    items = (
        Product.objects.filter(Q(name__icontains=q) | Q(short_description__icontains=q))
        .values("id", "name", "slug")[:5]
    )
    return JsonResponse({"results": list(items)})


@login_required
def profile(request):
    """View user profile"""
    user = request.user
    # Get user's order statistics
    orders = Order.objects.filter(user=user).order_by('-created_at')
    total_orders = orders.count()
    total_spent = sum(order.total_amount for order in orders)
    
    ctx = {
        'user': user,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'recent_orders': orders[:3],  # 3 most recent orders
    }
    return render(request, 'store/profile.html', ctx)


@login_required
def order_history(request):
    """View user's order history"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')
    
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    ctx = {
        'orders': page_obj,
    }
    return render(request, 'store/order_history.html', ctx)


@login_required
def order_detail(request, order_id):
    """View order detail"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    ctx = {
        'order': order,
    }
    return render(request, 'store/order_detail.html', ctx)


@login_required
def profile_edit(request):
    """Edit user profile information"""
    user = request.user
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật thông tin thành công!")
            return redirect("profile")
        else:
            messages.error(request, "Vui lòng kiểm tra lại thông tin.")
    else:
        form = ProfileForm(instance=user)

    return render(request, "store/profile_edit.html", {"form": form})


