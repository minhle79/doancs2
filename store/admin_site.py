from django.contrib.admin import AdminSite
from django.db.models import Q
from store.models import Product, Order


class ComputerStoreAdminSite(AdminSite):
    site_header = "💻 ComputerStore Admin"
    site_title = "ComputerStore Admin"
    index_title = "Chào mừng đến với ComputerStore Admin"
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Thống kê sản phẩm
        extra_context['total_products'] = Product.objects.count()
        extra_context['in_stock_products'] = Product.objects.filter(stock__gt=0).count()
        extra_context['low_stock_products'] = Product.objects.filter(Q(stock__gt=0) & Q(stock__lt=5)).count()
        
        # Thống kê đơn hàng
        extra_context['total_orders'] = Order.objects.count()
        
        return super().index(request, extra_context)
