from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Hãng"
        verbose_name_plural = "Hãng"
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=280, unique=True, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products", db_index=True)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="products", db_index=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, db_index=True)
    stock = models.PositiveIntegerField(default=0, db_index=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    specs = models.JSONField(default=dict, blank=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_deal = models.BooleanField(default=False, db_index=True)
    is_hot = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"
        indexes = [
            models.Index(fields=['-created_at', 'stock']),
            models.Index(fields=['category', 'brand']),
            models.Index(fields=['is_featured', 'is_hot', 'is_deal']),
        ]

    def __str__(self) -> str:
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Ảnh sản phẩm"
        verbose_name_plural = "Ảnh sản phẩm"

    def __str__(self) -> str:
        return f"{self.product.name} - Image {self.order}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('confirmed', 'Đã xác nhận'),
        ('processing', 'Đang xử lý'),
        ('shipped', 'Đang giao hàng'),
        ('delivered', 'Đã giao hàng'),
        ('cancelled', 'Đã hủy'),
    ]

    user = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    full_name = models.CharField(max_length=200, db_index=True)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=30, db_index=True)
    address = models.CharField(max_length=300)
    note = models.CharField(max_length=400, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        verbose_name='Trạng thái'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"
        indexes = [
            models.Index(fields=['-created_at', 'user']),
            models.Index(fields=['email', 'phone']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self) -> str:
        return f"Order #{self.id} - {self.full_name}"

    def get_status_display_badge(self):
        """Trả về badge HTML cho status"""
        status_colors = {
            'pending': '#f59e0b',
            'confirmed': '#3b82f6',
            'processing': '#8b5cf6',
            'shipped': '#06b6d4',
            'delivered': '#10b981',
            'cancelled': '#ef4444',
        }
        color = status_colors.get(self.status, '#6b7280')
        return color


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", db_index=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, db_index=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Chi tiết đơn hàng"
        verbose_name_plural = "Chi tiết đơn hàng"
        indexes = [
            models.Index(fields=['order', 'product']),
        ]

    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"

    def line_total(self):
        if self.quantity is None or self.price is None:
            return 0
        return self.quantity * self.price


