from django import forms

from .models import ContactMessage, NewsletterSubscriber


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Your email"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "How can we help?"}),
        }


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ["email"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Your email address"}),
        }
