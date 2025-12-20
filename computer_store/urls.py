from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from store.admin_site import ComputerStoreAdminSite

# Use custom admin site
admin_site = ComputerStoreAdminSite(name='admin')

# Copy over all registered models from default admin
from store.admin import CategoryAdmin, BrandAdmin, ProductAdmin, OrderAdmin
from store.models import Category, Brand, Product, Order

admin_site.register(Category, CategoryAdmin)
admin_site.register(Brand, BrandAdmin)
admin_site.register(Product, ProductAdmin)
admin_site.register(Order, OrderAdmin)

# Register auth models
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)

urlpatterns = [
    path("admin/", admin_site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("store.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


