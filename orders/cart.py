from decimal import Decimal

from catalog.models import ProductVariant

CART_SESSION_KEY = "cart"


class Cart:
    """A simple session-backed cart. Keys are ProductVariant IDs (as strings)."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, variant: ProductVariant, quantity: int = 1, replace: bool = False):
        variant_id = str(variant.id)
        if variant_id not in self.cart:
            self.cart[variant_id] = {"quantity": 0}

        if replace:
            self.cart[variant_id]["quantity"] = quantity
        else:
            self.cart[variant_id]["quantity"] += quantity

        # never let the cart request more than what's in stock
        max_qty = variant.stock_quantity
        if self.cart[variant_id]["quantity"] > max_qty:
            self.cart[variant_id]["quantity"] = max_qty
        if self.cart[variant_id]["quantity"] <= 0:
            del self.cart[variant_id]

        self.save()

    def remove(self, variant_id):
        variant_id = str(variant_id)
        if variant_id in self.cart:
            del self.cart[variant_id]
            self.save()

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        variant_ids = self.cart.keys()
        variants = ProductVariant.objects.select_related("product", "size").filter(id__in=variant_ids)
        variants_by_id = {str(v.id): v for v in variants}

        for variant_id, item in self.cart.items():
            variant = variants_by_id.get(variant_id)
            if not variant:
                continue
            unit_price = variant.effective_price
            yield {
                "variant": variant,
                "quantity": item["quantity"],
                "unit_price": unit_price,
                "line_total": unit_price * item["quantity"],
            }

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    @property
    def subtotal(self):
        return sum((entry["line_total"] for entry in self), Decimal("0"))
