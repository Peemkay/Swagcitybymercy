from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Product

SORT_OPTIONS = {
    "newest": "-created_at",
    "price_low": "base_price",
    "price_high": "-base_price",
    "name": "name",
}
DEFAULT_SORT = "newest"


def _apply_sort(products, sort_key):
    return products.order_by(SORT_OPTIONS.get(sort_key, SORT_OPTIONS[DEFAULT_SORT]))


def shop(request):
    products = Product.objects.filter(status=Product.Status.PUBLISHED).select_related("category").prefetch_related("images", "variants")
    categories = Category.objects.filter(is_active=True)

    category_slug = request.GET.get("category")
    if category_slug:
        products = products.filter(category__slug=category_slug)

    query = request.GET.get("q")
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    in_stock_only = request.GET.get("in_stock") == "1"
    if in_stock_only:
        products = products.filter(variants__stock_quantity__gt=0).distinct()

    sort_key = request.GET.get("sort", DEFAULT_SORT)
    if sort_key not in SORT_OPTIONS:
        sort_key = DEFAULT_SORT
    products = _apply_sort(products, sort_key)

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "catalog/shop.html", {
        "page_obj": page_obj,
        "categories": categories,
        "active_category": category_slug,
        "query": query or "",
        "in_stock_only": in_stock_only,
        "sort_key": sort_key,
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(status=Product.Status.PUBLISHED, category=category).prefetch_related("images", "variants")

    in_stock_only = request.GET.get("in_stock") == "1"
    if in_stock_only:
        products = products.filter(variants__stock_quantity__gt=0).distinct()

    sort_key = request.GET.get("sort", DEFAULT_SORT)
    if sort_key not in SORT_OPTIONS:
        sort_key = DEFAULT_SORT
    products = _apply_sort(products, sort_key)

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    categories = Category.objects.filter(is_active=True)

    return render(request, "catalog/shop.html", {
        "page_obj": page_obj,
        "categories": categories,
        "active_category": slug,
        "current_category_obj": category,
        "query": "",
        "in_stock_only": in_stock_only,
        "sort_key": sort_key,
    })


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("images", "variants__size"),
        slug=slug, status=Product.Status.PUBLISHED,
    )
    related = Product.objects.filter(
        status=Product.Status.PUBLISHED, category=product.category,
    ).exclude(pk=product.pk)[:4]

    return render(request, "catalog/product_detail.html", {
        "product": product,
        "related_products": related,
    })
