from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.urls import reverse
from django.utils.safestring import mark_safe
from django import forms
from django.forms import widgets
import json
from .models import Category, Brand, Product, Order, OrderItem
from .admin_site import ComputerStoreAdminSite


# Create custom admin site instance
admin_site = ComputerStoreAdminSite(name='computerstore_admin')

# Customize Admin Site Headers
admin.site.site_header = "💻 ComputerStore Admin"
admin.site.site_title = "ComputerStore Admin"
admin.site.index_title = "Quản lý cửa hàng máy tính"


class KeyValueWidget(widgets.Widget):
    """Custom widget for editing key-value pairs (specs)"""
    # Point to template inside the store app templates for proper discovery
    template_name = 'admin/widgets/key_value_widget.html'
    
    def __init__(self, attrs=None):
        super().__init__(attrs)
        
    def format_value(self, value):
        """Convert dict to list of tuples for rendering"""
        if value is None or value == '':
            return []
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return []
        if isinstance(value, dict):
            return list(value.items())
        return []
    
    def value_from_datadict(self, data, files, name):
        """Convert form data back to dict"""
        keys = data.getlist(f'{name}_key')
        values = data.getlist(f'{name}_value')
        result = {}
        for k, v in zip(keys, values):
            if k.strip():  # Only add non-empty keys
                result[k.strip()] = v.strip()
        return result
    
    class Media:
        css = {
            'all': ('admin/css/specs_widget.css',)
        }
        js = ('admin/js/specs_widget.js',)


class ProductAdminForm(forms.ModelForm):
    """Custom form for Product admin"""
    specs = forms.JSONField(
        required=False,
        widget=KeyValueWidget(),
        label="Thông số kỹ thuật",
        help_text="Nhập các thông số kỹ thuật của sản phẩm"
    )
    
    class Meta:
        model = Product
        fields = '__all__'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "product_count", "created_badge")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "slug"]
    list_per_page = 20
    
    def product_count(self, obj):
        count = obj.products.count()
        url = reverse('admin:store_product_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">{} sản phẩm</a>', url, count)
    product_count.short_description = "Số sản phẩm"
    
    def created_badge(self, obj):
        return format_html(
            '<span style="background: #10b981; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px;">✓ Active</span>'
        )
    created_badge.short_description = "Trạng thái"


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "product_count", "status_badge")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "slug"]
    list_per_page = 20
    
    def product_count(self, obj):
        count = obj.products.count()
        url = reverse('admin:store_product_changelist') + f'?brand__id__exact={obj.id}'
        return format_html('<a href="{}">{} sản phẩm</a>', url, count)
    product_count.short_description = "Số sản phẩm"
    
    def status_badge(self, obj):
        return format_html(
            '<span style="background: #6366f1; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px;">Active</span>'
        )
    status_badge.short_description = "Trạng thái"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = (
        "image_preview", "name", "brand", "category", 
        "price_display", "stock_status", "badges", "created_at"
    )
    list_filter = ("brand", "category", "is_featured", "is_deal", "is_hot", "created_at")
    search_fields = ("name", "short_description", "brand__name", "category__name")
    prepopulated_fields = {"slug": ("name",)}
    list_per_page = 25
    readonly_fields = ("image_preview_large", "created_at")
    date_hierarchy = "created_at"
    list_select_related = ("brand", "category")
    save_on_top = True
    
    # Add filters by stock levels
    class StockFilter(admin.SimpleListFilter):
        title = 'Tình trạng kho'
        parameter_name = 'stock_level'
        
        def lookups(self, request, model_admin):
            return (
                ('in_stock', 'Còn hàng'),
                ('low_stock', 'Sắp hết (< 5)'),
                ('out_of_stock', 'Hết hàng'),
            )
        
        def queryset(self, request, queryset):
            if self.value() == 'in_stock':
                return queryset.filter(stock__gt=5)
            if self.value() == 'low_stock':
                return queryset.filter(stock__gt=0, stock__lte=5)
            if self.value() == 'out_of_stock':
                return queryset.filter(stock=0)
    
    list_filter = (
        "brand", "category", StockFilter,
        "is_featured", "is_deal", "is_hot", "created_at"
    )
    
    fieldsets = (
        ("Thông tin cơ bản", {
            "fields": ("name", "slug", "brand", "category")
        }),
        ("Hình ảnh", {
            "fields": ("image", "image_preview_large")
        }),
        ("Mô tả", {
            "fields": ("short_description", "description")
        }),
        ("Giá & Kho", {
            "fields": ("price", "stock"),
            "classes": ("wide",)
        }),
        ("Thông số kỹ thuật", {
            "fields": ("specs",),
        }),
        ("Flags", {
            "fields": ("is_featured", "is_deal", "is_hot"),
            "classes": ("wide",)
        }),
        ("Thông tin khác", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return format_html('<div style="width: 60px; height: 60px; background: #e5e7eb; border-radius: 8px; display: flex; align-items: center; justify-content: center;">📷</div>')
    image_preview.short_description = "Hình ảnh"
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 400px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return "Chưa có hình ảnh"
    image_preview_large.short_description = "Xem trước hình ảnh"
    
    def price_display(self, obj):
        return format_html(
            '<span style="color: #10b981; font-weight: 700;">{} ₫</span>',
            f'{float(obj.price):,.0f}'
        )
    price_display.short_description = "Giá"
    price_display.admin_order_field = "price"
    
    def stock_status(self, obj):
        if obj.stock == 0:
            return format_html(
                '<span style="background: #dc2626; color: white; padding: 4px 12px; border-radius: 4px; font-size: 11px;">❌ Hết hàng</span>'
            )
        elif obj.stock < 5:
            return format_html(
                '<span style="background: #f59e0b; color: white; padding: 4px 12px; border-radius: 4px; font-size: 11px;">⚠️ Còn {} SP</span>',
                obj.stock
            )
        else:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 4px 12px; border-radius: 4px; font-size: 11px;">✅ Còn {} SP</span>',
                obj.stock
            )
    stock_status.short_description = "Tồn kho"
    stock_status.admin_order_field = "stock"
    
    def badges(self, obj):
        badges = []
        if obj.is_featured:
            badges.append('<span style="background: #6366f1; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; margin-right: 4px;">⭐ Featured</span>')
        if obj.is_deal:
            badges.append('<span style="background: #ec4899; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; margin-right: 4px;">🔥 Deal</span>')
        if obj.is_hot:
            badges.append('<span style="background: #f59e0b; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; margin-right: 4px;">⚡ Hot</span>')
        return format_html(''.join(badges)) if badges else "-"
    badges.short_description = "Nhãn"
    
    actions = [
        "mark_as_featured", "mark_as_deal", "mark_as_hot", 
        "remove_all_badges", "duplicate_products", "export_to_csv"
    ]
    
    def duplicate_products(self, request, queryset):
        """Duplicate selected products"""
        count = 0
        for product in queryset:
            product.pk = None
            product.name = f"{product.name} (Copy)"
            product.slug = f"{product.slug}-copy"
            product.save()
            count += 1
        self.message_user(request, f"Đã nhân bản {count} sản phẩm")
    duplicate_products.short_description = "📋 Nhân bản sản phẩm"
    
    def export_to_csv(self, request, queryset):
        """Export products to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'Brand', 'Category', 'Price', 'Stock', 'Created'])
        
        for product in queryset:
            writer.writerow([
                product.id, product.name, product.brand.name, 
                product.category.name, product.price, product.stock,
                product.created_at.strftime('%Y-%m-%d')
            ])
        
        return response
    export_to_csv.short_description = "📥 Export sang CSV"
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"Đã đánh dấu {updated} sản phẩm là Featured")
    mark_as_featured.short_description = "⭐ Đánh dấu là Featured"
    
    def mark_as_deal(self, request, queryset):
        updated = queryset.update(is_deal=True)
        self.message_user(request, f"Đã đánh dấu {updated} sản phẩm là Deal")
    mark_as_deal.short_description = "🔥 Đánh dấu là Deal"
    
    def mark_as_hot(self, request, queryset):
        updated = queryset.update(is_hot=True)
        self.message_user(request, f"Đã đánh dấu {updated} sản phẩm là Hot")
    mark_as_hot.short_description = "⚡ Đánh dấu là Hot"
    
    def remove_all_badges(self, request, queryset):
        updated = queryset.update(is_featured=False, is_deal=False, is_hot=False)
        self.message_user(request, f"Đã xóa tất cả nhãn của {updated} sản phẩm")
    remove_all_badges.short_description = "🗑️ Xóa tất cả nhãn"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_link", "quantity", "price", "line_total_display")
    can_delete = False
    fields = ("product_link", "quantity", "price", "line_total_display")
    
    def product_link(self, obj):
        url = reverse('admin:store_product_change', args=[obj.product.id])
        return format_html('<a href="{}" target="_blank">{}</a>', url, obj.product.name)
    product_link.short_description = "Sản phẩm"
    
    def line_total_display(self, obj):
        return format_html(
            '<span style="color: #10b981; font-weight: 700;">{} ₫</span>',
            f'{float(obj.line_total()):,.0f}'
        )
    line_total_display.short_description = "Thành tiền"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_id_display", "full_name", "email", "phone", 
        "total_amount_display", "items_count", "status_badge", "created_at"
    )
    list_filter = ("created_at",)
    search_fields = ("id", "full_name", "email", "phone", "address")
    readonly_fields = (
        "user", "full_name", "email", "phone", "address", "note",
        "total_amount", "created_at", "order_summary"
    )
    inlines = [OrderItemInline]
    list_per_page = 25
    date_hierarchy = "created_at"
    list_select_related = ("user",)
    save_on_top = True
    actions = ["export_orders_csv"]
    
    fieldsets = (
        ("Thông tin đơn hàng", {
            "fields": ("user", "created_at")
        }),
        ("Thông tin khách hàng", {
            "fields": ("full_name", "email", "phone", "address", "note")
        }),
        ("Tổng quan đơn hàng", {
            "fields": ("order_summary", "total_amount")
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with prefetch_related"""
        qs = super().get_queryset(request)
        return qs.select_related('user').prefetch_related('items__product')
    
    def export_orders_csv(self, request, queryset):
        """Export orders to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Customer', 'Email', 'Phone', 'Total', 'Date'])
        
        for order in queryset:
            writer.writerow([
                order.id, order.full_name, order.email, 
                order.phone, order.total_amount,
                order.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response
    export_orders_csv.short_description = "📥 Export đơn hàng sang CSV"
    
    def order_id_display(self, obj):
        return format_html(
            '<span style="background: #6366f1; color: white; padding: 4px 12px; border-radius: 4px; font-weight: 700;">#{}</span>',
            obj.id
        )
    order_id_display.short_description = "Mã ĐH"
    order_id_display.admin_order_field = "id"
    
    def total_amount_display(self, obj):
        return format_html(
            '<span style="color: #10b981; font-weight: 700; font-size: 14px;">{} ₫</span>',
            f'{float(obj.total_amount):,.0f}'
        )
    total_amount_display.short_description = "Tổng tiền"
    total_amount_display.admin_order_field = "total_amount"
    
    def items_count(self, obj):
        count = obj.items.count()
        return format_html(
            '<span style="background: #e5e7eb; color: #1f2937; padding: 4px 10px; border-radius: 4px; font-weight: 600;">{} SP</span>',
            count
        )
    items_count.short_description = "Số SP"
    
    def status_badge(self, obj):
        return format_html(
            '<span style="background: #10b981; color: white; padding: 6px 12px; border-radius: 4px; font-weight: 600;">✅ Hoàn thành</span>'
        )
    status_badge.short_description = "Trạng thái"
    
    def order_summary(self, obj):
        items_html = ""
        for item in obj.items.all():
            items_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{item.product.name}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; text-align: center;">{item.quantity}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; text-align: right;">{item.price:,.0f} ₫</td>
                <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; text-align: right; font-weight: 700; color: #10b981;">{item.line_total():,.0f} ₫</td>
            </tr>
            """
        
        return format_html(
            """
            <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <thead>
                    <tr style="background: #f3f4f6;">
                        <th style="padding: 12px 8px; text-align: left; font-weight: 600;">Sản phẩm</th>
                        <th style="padding: 12px 8px; text-align: center; font-weight: 600;">SL</th>
                        <th style="padding: 12px 8px; text-align: right; font-weight: 600;">Đơn giá</th>
                        <th style="padding: 12px 8px; text-align: right; font-weight: 600;">Thành tiền</th>
                    </tr>
                </thead>
                <tbody>
                    {}
                </tbody>
            </table>
            """,
            mark_safe(items_html)
        )
    order_summary.short_description = "Chi tiết đơn hàng"
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


