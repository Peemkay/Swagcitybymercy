from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first in the shop menu.")

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:category_detail", args=[self.slug])


class Size(models.Model):
    """Reusable size labels, e.g. XS, S, M, L, XL, or numeric UK sizes."""
    label = models.CharField(max_length=20, unique=True)
    order = models.PositiveIntegerField(default=0, help_text="Controls display order (e.g. S before M).")

    class Meta:
        ordering = ["order", "label"]

    def __str__(self):
        return self.label


class Product(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft (hidden from shop)"
        PUBLISHED = "published", "Published (visible in shop)"

    category = models.ForeignKey(Category, related_name="products", on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Default price in Naira. Individual sizes can override this.",
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PUBLISHED)
    is_featured = models.BooleanField(default=False, help_text="Show on the homepage highlights.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            i = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base_slug}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:product_detail", args=[self.slug])

    @property
    def is_in_stock(self):
        return self.variants.filter(stock_quantity__gt=0).exists()

    @property
    def total_stock(self):
        return sum(v.stock_quantity for v in self.variants.all())

    @property
    def price_range(self):
        prices = [v.effective_price for v in self.variants.all()]
        if not prices:
            return self.base_price, self.base_price
        return min(prices), max(prices)

    @property
    def primary_image(self):
        img = self.images.filter(is_primary=True).first()
        return img or self.images.first()


class ProductVariant(models.Model):
    """A specific size of a product — this is the sellable, stock-tracked unit."""
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    size = models.ForeignKey(Size, related_name="variants", on_delete=models.PROTECT)
    sku = models.CharField(max_length=64, unique=True, blank=True, help_text="Leave blank to auto-generate.")
    price_override = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Leave blank to use the product's base price for this size.",
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(
        default=3, help_text="Admin dashboard flags this variant when stock falls at/below this number.",
    )

    class Meta:
        unique_together = ("product", "size")
        ordering = ["size__order"]

    def __str__(self):
        return f"{self.product.name} - {self.size.label}"

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"SCM-{slugify(self.product.name)[:20].upper()}-{self.size.label.upper()}"
        super().save(*args, **kwargs)

    @property
    def effective_price(self):
        return self.price_override if self.price_override is not None else self.product.base_price

    @property
    def is_low_stock(self):
        return 0 < self.stock_quantity <= self.low_stock_threshold

    @property
    def is_out_of_stock(self):
        return self.stock_quantity <= 0


def product_image_path(instance, filename):
    return f"products/{instance.product.slug}/{filename}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=product_image_path)
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_primary:
            ProductImage.objects.filter(product=self.product).exclude(pk=self.pk).update(is_primary=False)
