from django import forms

from .models import Order, PaymentProof, ShippingZone


class CheckoutForm(forms.ModelForm):
    shipping_zone = forms.ModelChoiceField(
        queryset=ShippingZone.objects.filter(is_active=True),
        empty_label="Select a delivery region",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Order
        fields = [
            "full_name", "email", "phone",
            "address", "city", "state", "country",
            "shipping_zone", "customer_notes",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Full name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email address"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone number"}),
            "address": forms.TextInput(attrs={"class": "form-control", "placeholder": "Delivery address"}),
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "City"}),
            "state": forms.TextInput(attrs={"class": "form-control", "placeholder": "State"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "customer_notes": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Anything we should know? (optional)"}),
        }


class PaymentProofForm(forms.ModelForm):
    class Meta:
        model = PaymentProof
        fields = ["image", "amount_paid", "note"]
        widgets = {
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "amount_paid": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Amount you paid (\u20a6)"}),
            "note": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. transfer reference (optional)"}),
        }
