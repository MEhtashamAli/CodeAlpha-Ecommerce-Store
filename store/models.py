import uuid
from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=10, help_text="Emoji icon for the category")
    count = models.PositiveIntegerField(default=0, help_text="Number of items in category")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["order"]

    def __str__(self):
        return self.name


class Product(models.Model):
    TAG_CHOICES = [
        ("new", "New"),
        ("best", "Best Seller"),
        ("sale", "On Sale"),
    ]
    BADGE_CLASS_CHOICES = [
        ("new", "New"),
        ("sale", "Sale"),
        ("hot", "Hot"),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=100)
    image = models.CharField(
        max_length=300,
        help_text="Relative path inside static, e.g. store/images/product_watch.png",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    tag = models.CharField(max_length=10, choices=TAG_CHOICES, default="new")
    badge = models.CharField(max_length=20, blank=True, help_text="Badge text, e.g. New, -30%, Hot")
    badge_class = models.CharField(
        max_length=10, choices=BADGE_CLASS_CHOICES, blank=True
    )
    stars = models.CharField(max_length=20, default="★★★★★")
    reviews = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    order_number = models.CharField(max_length=32, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="orders",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Customer info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)

    # Shipping address
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="United States")

    # Totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"FY-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    product_image = models.CharField(max_length=300, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    def save(self, *args, **kwargs):
        self.line_total = self.price * self.quantity
        super().save(*args, **kwargs)
