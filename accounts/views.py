from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from orders.models import Order

from .forms import SignUpForm


class CustomerLoginView(LoginView):
    template_name = "accounts/login.html"


def signup(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("accounts:dashboard")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


@login_required
def dashboard(request):
    orders = Order.objects.filter(customer=request.user)
    return render(request, "accounts/dashboard.html", {"orders": orders})
