from django.contrib import messages
from django.shortcuts import redirect, render

from catalog.models import Category, Product

from .forms import ContactForm


def home(request):
    featured_products = Product.objects.filter(
        status=Product.Status.PUBLISHED, is_featured=True,
    ).prefetch_related("images", "variants")[:8]

    if not featured_products:
        featured_products = Product.objects.filter(status=Product.Status.PUBLISHED).prefetch_related("images", "variants")[:8]

    categories = Category.objects.filter(is_active=True)[:6]

    return render(request, "pages/home.html", {
        "featured_products": featured_products,
        "categories": categories,
    })


def about(request):
    return render(request, "pages/about.html")


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for reaching out — we'll get back to you soon!")
            return redirect("pages:contact")
    else:
        form = ContactForm()
    return render(request, "pages/contact.html", {"form": form})
