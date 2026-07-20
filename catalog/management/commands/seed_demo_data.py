from django.core.management.base import BaseCommand

from catalog.models import Category, Product, ProductVariant, Size
from orders.models import BankAccount, ShippingZone
from pages.models import SiteSettings


class Command(BaseCommand):
    help = "Seed the database with starter categories, sizes, sample products, shipping zones and site settings."

    def handle(self, *args, **options):
        settings_obj = SiteSettings.load()
        settings_obj.site_name = "Swagcitybymercy"
        settings_obj.tagline = "Quality, luxury female apparel — Lagos, Nigeria."
        settings_obj.about_text = (
            "Swagcitybymercy is a Lagos-based online fashion boutique specializing in quality, "
            "luxury female apparel. Our catalog includes chic dresses, blouse dresses, and "
            "accessories for the modern woman."
        )
        settings_obj.instagram_handle = "swagcitybymercy"
        settings_obj.lagos_delivery_note = "1-2 working days within Lagos"
        settings_obj.other_regions_delivery_note = "5-7 working days for other regions"
        settings_obj.international_delivery_note = "5-6 working days for international orders"
        settings_obj.save()
        self.stdout.write(self.style.SUCCESS("Site settings ready."))

        sizes = {}
        for i, label in enumerate(["XS", "S", "M", "L", "XL"]):
            size, _ = Size.objects.get_or_create(label=label, defaults={"order": i})
            sizes[label] = size
        self.stdout.write(self.style.SUCCESS("Sizes ready."))

        zones = [
            ("Lagos", "1-2 working days", 2500),
            ("Other Nigeria", "5-7 working days", 4500),
            ("International", "5-6 working days", 25000),
        ]
        for i, (name, estimate, fee) in enumerate(zones):
            ShippingZone.objects.get_or_create(
                name=name, defaults={"delivery_estimate": estimate, "fee": fee, "order": i},
            )
        self.stdout.write(self.style.SUCCESS("Shipping zones ready."))

        BankAccount.objects.get_or_create(
            account_number="0123456789",
            defaults={
                "bank_name": "Guaranty Trust Bank",
                "account_name": "Swagcitybymercy Ltd",
                "is_active": True,
            },
        )
        self.stdout.write(self.style.SUCCESS("Sample bank account ready — update this in the admin with your real account."))

        categories_data = [
            ("Dresses", "Chic dresses for every occasion."),
            ("Blouse Dresses", "Effortless blouse dresses."),
            ("Accessories", "Finishing touches for your look."),
        ]
        categories = {}
        for i, (name, desc) in enumerate(categories_data):
            cat, _ = Category.objects.get_or_create(name=name, defaults={"description": desc, "order": i})
            categories[name] = cat
        self.stdout.write(self.style.SUCCESS("Categories ready."))

        sample_products = [
            ("Emerald Wrap Dress", "Dresses", 45000, "A flattering wrap silhouette in rich emerald green."),
            ("Ivory Blouse Dress", "Blouse Dresses", 38000, "Soft ivory blouse dress with a relaxed, elegant fit."),
            ("Statement Gold Earrings", "Accessories", 26000, "Bold gold-tone earrings to complete any outfit."),
            ("Midnight Satin Gown", "Dresses", 95000, "Floor-length satin gown for special occasions."),
        ]
        for name, cat_name, price, desc in sample_products:
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    "category": categories[cat_name],
                    "base_price": price,
                    "description": desc,
                    "is_featured": True,
                },
            )
            if created:
                for label in ["S", "M", "L"]:
                    ProductVariant.objects.get_or_create(
                        product=product, size=sizes[label], defaults={"stock_quantity": 5},
                    )
        self.stdout.write(self.style.SUCCESS("Sample products ready."))

        self.stdout.write(self.style.SUCCESS(
            "\nSeed complete. Remember to:\n"
            "  1. Update the bank account details in the admin (Orders > Bank accounts).\n"
            "  2. Upload real product photos (Catalog > Products > edit > add images).\n"
            "  3. Set your WhatsApp number and contact info (Pages > Site settings)."
        ))
