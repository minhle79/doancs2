from django.contrib.admin import AdminSite
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import timedelta
from store.models import Product, Order, Category
import json


class ComputerStoreAdminSite(AdminSite):
    site_header = "💻 ComputerStore Admin"
    site_title = "ComputerStore Admin"
    index_title = "Chào mừng đến với ComputerStore Admin"
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Current time
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Thống kê sản phẩm
        total_products = Product.objects.count()
        in_stock = Product.objects.filter(stock__gt=0).count()
        low_stock = Product.objects.filter(Q(stock__gt=0) & Q(stock__lt=5)).count()
        new_products = Product.objects.filter(created_at__gte=week_ago).count()
        
        extra_context['total_products'] = total_products
        extra_context['in_stock_products'] = in_stock
        extra_context['low_stock_products'] = low_stock
        extra_context['new_products_week'] = new_products
        
        # Tính phần trăm sản phẩm còn hàng
        if total_products > 0:
            extra_context['stock_percent'] = round((in_stock / total_products) * 100, 1)
        else:
            extra_context['stock_percent'] = 0
        
        # Thống kê đơn hàng
        total_orders = Order.objects.count()
        orders_today = Order.objects.filter(created_at__gte=today_start).count()
        
        # Tổng doanh thu
        total_revenue = Order.objects.filter(
            status__in=['confirmed', 'processing', 'shipped', 'delivered']
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Thống kê theo trạng thái đơn hàng
        pending_orders = Order.objects.filter(status='pending').count()
        processing_orders = Order.objects.filter(status__in=['confirmed', 'processing']).count()
        shipped_orders = Order.objects.filter(status='shipped').count()
        delivered_orders = Order.objects.filter(status='delivered').count()
        
        extra_context['total_orders'] = total_orders
        extra_context['orders_today'] = orders_today
        extra_context['total_revenue'] = total_revenue
        extra_context['pending_orders'] = pending_orders
        extra_context['processing_orders'] = processing_orders
        extra_context['shipped_orders'] = shipped_orders
        extra_context['delivered_orders'] = delivered_orders
        
        # Doanh thu 7 ngày qua (biểu đồ)
        revenue_data = []
        labels = []
        for i in range(6, -1, -1):
            day = now - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            day_revenue = Order.objects.filter(
                created_at__gte=day_start,
                created_at__lt=day_end
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            revenue_data.append(float(day_revenue))
            
            # Label theo thứ trong tuần
            day_labels = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']
            labels.append(day_labels[day.weekday()])
        
        extra_context['revenue_chart_data'] = json.dumps({
            'labels': labels,
            'values': revenue_data
        })
        
        # Phân bố danh mục (biểu đồ)
        category_data = Category.objects.annotate(
            product_count=Count('products')
        ).values('name', 'product_count').order_by('-product_count')[:5]
        
        cat_labels = [item['name'] for item in category_data]
        cat_values = [item['product_count'] for item in category_data]
        
        extra_context['category_chart_data'] = json.dumps({
            'labels': cat_labels,
            'values': cat_values
        })
        
        # Đơn hàng gần đây (5 đơn)
        extra_context['recent_orders'] = Order.objects.select_related('user').order_by('-created_at')[:5]
        
        # Sản phẩm sắp hết hàng (chi tiết)
        extra_context['low_stock_products_detail'] = Product.objects.filter(
            Q(stock__gt=0) & Q(stock__lt=5)
        ).order_by('stock')[:5]
        
        return super().index(request, extra_context)
