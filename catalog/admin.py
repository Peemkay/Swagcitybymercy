from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product, ProductImage, ProductVariant, Size


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "order", "product_count")
    list_editable = ("is_active", "order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Products"


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("label", "order")
    list_editable = ("order",)


class ProductVariantInline(admin.TabularInline):
    """Lets admin manage stock quantity and per-size pricing inline on the product page."""
    model = ProductVariant
    extra = 1
    fields = ("size", "sku", "price_override", "stock_quantity", "low_stock_threshold")
    readonly_fields = ()


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "is_primary", "order")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name", "category", "base_price", "status", "is_featured",
        "stock_status", "created_at",
    )
    list_filter = ("status", "category", "is_featured")
    list_editable = ("base_price", "status", "is_featured")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductVariantInline, ProductImageInline]
    fieldsets = (
        (None, {"fields": ("category", "name", "slug", "description")}),
        ("Pricing & visibility", {"fields": ("base_price", "status", "is_featured")}),
    )

    def stock_status(self, obj):
        total = obj.total_stock
        if total == 0:
            color, label = "#c0392b", "Out of stock"
        elif obj.variants.filter(stock_quantity__lte=3, stock_quantity__gt=0).exists():
            color, label = "#e67e22", f"{total} left (low)"
        else:
            color, label = "#27ae60", f"{total} in stock"
        return format_html('<b style="color:{}">{}</b>', color, label)
    stock_status.short_description = "Stock"


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """Dedicated view for fast, catalog-wide stock and price edits."""
    list_display = ("product", "size", "sku", "effective_price", "stock_quantity", "low_stock_threshold", "stock_flag")
    list_editable = ("stock_quantity", "low_stock_threshold")
    list_filter = ("product__category", "size")
    search_fields = ("product__name", "sku")
    autocomplete_fields = ("product",)

    def stock_flag(self, obj):
        if obj.is_out_of_stock:
            return format_html('<b style="color:#c0392b">{}</b>', "Out of stock")
        if obj.is_low_stock:
            return format_html('<b style="color:#e67e22">{}</b>', "Low")
        return format_html('<span style="color:#27ae60">{}</span>', "OK")
    stock_flag.short_description = "Status"


admin.site.site_header = "Swagcitybymercy Admin"
admin.site.site_title = "Swagcitybymercy Admin"
admin.site.index_title = "Store Management"
