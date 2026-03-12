from django.contrib import admin
from .models import Category, Product, Subscriber, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon", "count", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "tag", "order")
    list_filter = ("tag", "category")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "subscribed_at")
    search_fields = ("email",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ("product_name", "price", "quantity", "line_total")
    readonly_fields = ("line_total",)
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "full_name", "email", "total", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order_number", "email", "first_name", "last_name")
    readonly_fields = ("order_number", "user", "subtotal", "shipping", "total", "created_at", "updated_at")
    inlines = [OrderItemInline]

    @admin.display(description="Customer")
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
