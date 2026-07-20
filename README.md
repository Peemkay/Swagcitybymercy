# Swagcitybymercy — E-Commerce Website

A production-ready Django website for **Swagcitybymercy**, a Lagos-based
luxury female apparel boutique. Built for Naira bank-transfer payments,
region-based shipping, and full stock/pricing management from the admin
panel.

## What's included

- **Storefront**: home, shop (search + category filter + pagination),
  product detail with size/stock-aware add-to-cart, cart, checkout,
  order confirmation, order tracking, about, contact.
- **Naira payments (manual bank transfer)**: at checkout, customers see
  your bank account details, transfer the amount, then upload a
  screenshot as proof of payment. You confirm the order in the admin
  panel once you've verified the transfer in your bank app.
- **Shipping**: three region types out of the box (Lagos, Other Nigeria,
  International), each with an editable delivery estimate and fee —
  matching Swagcitybymercy's real delivery times.
- **Admin panel** (`/admin/`): manage products, per-size stock and
  pricing, categories, sizes, product photos, shipping fees, bank
  accounts, orders (with a status workflow and bulk actions,
  auto-restocking on cancellation), contact messages, and site-wide
  settings (WhatsApp number, Instagram handle, delivery notes, about
  text) — no code changes needed for day-to-day store management.
- **Accounts**: customer signup/login and an order-history dashboard.
  Checkout also works for guests (no account required).

## Project layout

```
swagcity_project/
├── manage.py
├── config/          # Django settings, root URLs
├── catalog/         # Categories, products, sizes, stock, pricing
├── orders/          # Cart, checkout, orders, shipping, bank accounts
├── accounts/        # Customer signup/login/dashboard
├── pages/           # Home, about, contact, site-wide settings
├── templates/        # All HTML templates
├── static/          # CSS/JS
└── requirements.txt
```

## Local setup

```bash
cd swagcity_project
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser  # create your admin login
python manage.py seed_demo_data   # optional: adds sample categories,
                                   # sizes, products, shipping zones,
                                   # and a placeholder bank account so
                                   # you can see the site populated

python manage.py runserver
```

Visit:
- Storefront: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/

## First things to configure in the admin panel

1. **Orders → Bank accounts** — replace the seeded sample with your
   real Nigerian bank account(s). You can list more than one; the
   store uses the first active one shown at checkout.
2. **Orders → Shipping zones** — confirm/adjust the Lagos, Other
   Nigeria, and International fees and delivery estimates.
3. **Pages → Site settings** — set your WhatsApp number (digits only,
   with country code, e.g. `2348012345678`), Instagram handle, contact
   email/phone, and about text.
4. **Catalog → Categories** and **Catalog → Products** — add your real
   categories (Dresses, Blouse Dresses, Accessories, etc.), then for
   each product set the base price, upload photos, and add a size
   variant row per size with its own stock quantity and (optional)
   price override — handy since your pieces range roughly ₦26,000 to
   ₦95,000 depending on style and size.
5. Delete the demo superuser's sample data via **Catalog → Products**
   and **Orders → Bank accounts** if you ran `seed_demo_data` just to
   explore, or simply edit it in place.

## How stock and pricing work

- Every product has a **base price**. Each size (a `ProductVariant`)
  can optionally **override** that price — so a size that costs more
  fabric can be priced higher without creating a whole new product.
- Stock is tracked **per size**, not per product. The shop
  automatically shows "Sold Out" / "Low Stock" badges and disables
  out-of-stock sizes on the product page.
- Stock is decremented when an order is placed (not just when payment
  is confirmed) to prevent overselling while a bank transfer is in
  progress. If you cancel an order in the admin, stock for its items
  is automatically restored.

## Order status workflow

`Pending payment → Payment proof submitted → Payment confirmed →
Processing → Shipped → Delivered` (or `Cancelled` at any point). Use
the admin's order list bulk actions to move multiple orders through
these stages quickly, or open an order to see the uploaded payment
screenshot and set its status individually.

## Deploying to production

1. Set real environment variables (see `.env.example`):
   `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS`,
   `DJANGO_CSRF_TRUSTED_ORIGINS`.
2. Swap SQLite for Postgres in production for reliability — update
   `DATABASES` in `config/settings.py` (e.g. using
   `dj-database-url` and a `DATABASE_URL` env var), then run
   `python manage.py migrate` again against the new database.
3. Run `python manage.py collectstatic --noinput` — static files are
   served efficiently via WhiteNoise, already wired into
   `MIDDLEWARE`.
4. Run the app with Gunicorn behind Nginx (or a platform like Railway,
   Render, or PythonAnywhere):
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:8000
   ```
5. Point your domain's DNS at your host, get an SSL certificate (e.g.
   Let's Encrypt / Certbot, or your host's built-in HTTPS), and add
   your domain to `DJANGO_ALLOWED_HOSTS` and
   `DJANGO_CSRF_TRUSTED_ORIGINS`.
6. For uploaded media (product photos, payment screenshots) at scale,
   consider pointing `MEDIA_ROOT` at a persistent volume or an object
   storage service (e.g. Cloudinary, AWS S3 via `django-storages`) —
   local disk storage works but won't survive a redeploy on most
   platform-as-a-service hosts.
7. Change the seeded admin password immediately, and remove/replace
   the sample bank account and products before going live.

## Notes on payments

This build uses **manual bank transfer confirmation**, as requested:
no third-party payment gateway or API keys are required. If you later
want automated card/bank payments (e.g. via Paystack or Flutterwave),
that can be added as an additional payment method alongside this flow
without disrupting what's already built.
