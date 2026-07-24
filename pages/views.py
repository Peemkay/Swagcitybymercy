from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Category, Product

from .forms import ContactForm, NewsletterForm
from .models import FAQItem, NewsletterSubscriber, PolicyPage


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


def policy_page(request, kind):
    policy = get_object_or_404(PolicyPage, kind=kind)
    return render(request, "pages/policy_page.html", {"policy": policy})


def faq(request):
    items = FAQItem.objects.filter(is_active=True)
    return render(request, "pages/faq.html", {"items": items})


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


@require_POST
def newsletter_subscribe(request):
    form = NewsletterForm(request.POST)
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

    if form.is_valid():
        email = form.cleaned_data["email"]
        NewsletterSubscriber.objects.get_or_create(email=email, defaults={"is_active": True})
        message = "You're subscribed! Watch your inbox for new arrivals & offers."
        if is_ajax:
            return JsonResponse({"success": True, "message": message})
        messages.success(request, message)
    else:
        message = "Please enter a valid email address."
        if is_ajax:
            return JsonResponse({"success": False, "message": message}, status=400)
        messages.error(request, message)

    return redirect(request.META.get("HTTP_REFERER", "pages:home"))
