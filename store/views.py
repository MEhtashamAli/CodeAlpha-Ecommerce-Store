import json
from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .models import Category, Product, Subscriber, Order, OrderItem


# ---------------------------------------------------------------------------
# Cart helpers — session-based
# ---------------------------------------------------------------------------

def _get_cart(request):
    """Return the cart dict from session: {product_id_str: quantity}."""
    return request.session.get("cart", {})


def _save_cart(request, cart):
    """Persist the cart dict to session."""
    request.session["cart"] = cart
    request.session.modified = True


def _cart_count(request):
    """Total number of items in the cart."""
    return sum(_get_cart(request).values())


# Fallback product catalogue used when DB is empty
FALLBACK_PRODUCTS = [
    {
        "id": 1, "slug": "sneakers", "name": "Aria Minimal Sneakers",
        "category": "Footwear", "image": "store/images/hero_sneakers.png",
        "price": "189.00", "original_price": None,
        "tag": "new", "badge": "New", "badge_class": "new",
        "stars": "★★★★★", "reviews": 124,
    },
    {
        "id": 2, "slug": "watch", "name": "Noir Chronograph Watch",
        "category": "Watches", "image": "store/images/product_watch.png",
        "price": "349.00", "original_price": None,
        "tag": "best", "badge": "Hot", "badge_class": "hot",
        "stars": "★★★★★", "reviews": 98,
    },
    {
        "id": 3, "slug": "bag", "name": "Velvet Crossbody Bag",
        "category": "Bags", "image": "store/images/product_bag.png",
        "price": "139.00", "original_price": "199.00",
        "tag": "sale", "badge": "-30%", "badge_class": "sale",
        "stars": "★★★★☆", "reviews": 76,
    },
    {
        "id": 4, "slug": "headphones", "name": "Eclipse Pro Headphones",
        "category": "Audio", "image": "store/images/product_headphones.png",
        "price": "279.00", "original_price": None,
        "tag": "new", "badge": "New", "badge_class": "new",
        "stars": "★★★★★", "reviews": 213,
    },
    {
        "id": 5, "slug": "sunglasses", "name": "Soleil Aviator Shades",
        "category": "Accessories", "image": "store/images/product_sunglasses.png",
        "price": "159.00", "original_price": None,
        "tag": "best", "badge": "", "badge_class": "",
        "stars": "★★★★★", "reviews": 156,
    },
    {
        "id": 6, "slug": "jacket", "name": "Atlas Bomber Jacket",
        "category": "Apparel", "image": "store/images/product_jacket.png",
        "price": "224.00", "original_price": "299.00",
        "tag": "sale", "badge": "-25%", "badge_class": "sale",
        "stars": "★★★★☆", "reviews": 89,
    },
]

FALLBACK_CATEGORIES = [
    {"slug": "footwear", "icon": "👟", "name": "Footwear", "count": "1,240"},
    {"slug": "watches", "icon": "⌚", "name": "Watches", "count": "860"},
    {"slug": "bags", "icon": "👜", "name": "Bags", "count": "940"},
    {"slug": "accessories", "icon": "🕶️", "name": "Accessories", "count": "2,100"},
]


def _lookup_product(product_id):
    """Return product data (dict) by id, checking DB first then fallback."""
    try:
        p = Product.objects.get(pk=product_id)
        return {
            "id": p.id,
            "name": p.name,
            "price": str(p.price),
            "image": p.image,
            "category": p.category,
        }
    except Product.DoesNotExist:
        for p in FALLBACK_PRODUCTS:
            if p["id"] == product_id:
                return {
                    "id": p["id"],
                    "name": p["name"],
                    "price": p["price"],
                    "image": p["image"],
                    "category": p["category"],
                }
    return None


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

def home(request):
    """Render the Foey landing page with all sections."""
    categories = Category.objects.all()
    products = Product.objects.all()

    if not categories.exists():
        categories = FALLBACK_CATEGORIES

    if not products.exists():
        products = FALLBACK_PRODUCTS

    context = {
        "categories": categories,
        "products": products,
        "cart_count": _cart_count(request),
        "featured_product": {"price": "189.00"},
        "stats": {
            "products": "12K+",
            "satisfaction": "98%",
            "brands": "150+",
        },
        "subscribed": request.GET.get("subscribed") == "1",
    }
    return render(request, "store/index.html", context)


def subscribe(request):
    """Handle newsletter email subscription."""
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        if email:
            Subscriber.objects.get_or_create(email=email)
        return redirect("store:home")
    return redirect("store:home")


def product_detail(request, slug):
    """Render the product detail page."""
    product = None
    related = []

    # Try DB first
    try:
        p = Product.objects.get(slug=slug)
        product = {
            "id": p.id, "slug": p.slug, "name": p.name,
            "category": p.category, "image": p.image,
            "price": str(p.price),
            "original_price": str(p.original_price) if p.original_price else None,
            "tag": p.tag, "badge": p.badge, "badge_class": p.badge_class,
            "stars": p.stars, "reviews": p.reviews,
        }
        db_related = Product.objects.exclude(pk=p.pk)[:3]
        if db_related.exists():
            related = [
                {
                    "id": rp.id, "slug": rp.slug, "name": rp.name,
                    "category": rp.category, "image": rp.image,
                    "price": str(rp.price),
                    "original_price": str(rp.original_price) if rp.original_price else None,
                    "tag": rp.tag, "badge": rp.badge, "badge_class": rp.badge_class,
                    "stars": rp.stars, "reviews": rp.reviews,
                }
                for rp in db_related
            ]
    except Product.DoesNotExist:
        pass

    # Fallback
    if not product:
        for fp in FALLBACK_PRODUCTS:
            if fp["slug"] == slug:
                product = fp
                break

    if not product:
        from django.http import Http404
        raise Http404("Product not found")

    if not related:
        related = [fp for fp in FALLBACK_PRODUCTS if fp["slug"] != slug][:3]

    # Calculate savings
    savings = None
    if product.get("original_price"):
        from decimal import Decimal
        savings = str(
            Decimal(product["original_price"]) - Decimal(product["price"])
        )

    context = {
        "product": product,
        "related_products": related,
        "savings": savings,
        "cart_count": _cart_count(request),
    }
    return render(request, "store/product_detail.html", context)


# ---------------------------------------------------------------------------
# Cart API (JSON)
# ---------------------------------------------------------------------------

@require_POST
def cart_add(request):
    """Add a product to the cart or increment its quantity."""
    try:
        data = json.loads(request.body)
        product_id = int(data.get("product_id", 0))
        quantity = int(data.get("quantity", 1))
        if quantity < 1:
            quantity = 1
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({"error": "Invalid request"}, status=400)

    product = _lookup_product(product_id)
    if not product:
        return JsonResponse({"error": "Product not found"}, status=404)

    cart = _get_cart(request)
    key = str(product_id)
    cart[key] = cart.get(key, 0) + quantity
    _save_cart(request, cart)

    return JsonResponse({
        "success": True,
        "cart_count": _cart_count(request),
        "item_qty": cart[key],
        "product": product,
    })


@require_POST
def cart_update(request):
    """Set the quantity of a cart item."""
    try:
        data = json.loads(request.body)
        product_id = str(int(data.get("product_id", 0)))
        quantity = int(data.get("quantity", 1))
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({"error": "Invalid request"}, status=400)

    cart = _get_cart(request)
    if product_id not in cart:
        return JsonResponse({"error": "Item not in cart"}, status=404)

    if quantity <= 0:
        del cart[product_id]
    else:
        cart[product_id] = quantity

    _save_cart(request, cart)

    return JsonResponse({
        "success": True,
        "cart_count": _cart_count(request),
        "cart": _build_cart_detail(cart),
    })


@require_POST
def cart_remove(request):
    """Remove a product from the cart entirely."""
    try:
        data = json.loads(request.body)
        product_id = str(int(data.get("product_id", 0)))
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({"error": "Invalid request"}, status=400)

    cart = _get_cart(request)
    if product_id in cart:
        del cart[product_id]
    _save_cart(request, cart)

    return JsonResponse({
        "success": True,
        "cart_count": _cart_count(request),
        "cart": _build_cart_detail(cart),
    })


def cart_detail(request):
    """Return full cart contents as JSON."""
    cart = _get_cart(request)
    return JsonResponse({
        "cart_count": _cart_count(request),
        "cart": _build_cart_detail(cart),
    })


def _build_cart_detail(cart):
    """Build a list of cart item dicts with totals."""
    items = []
    subtotal = Decimal("0.00")
    for pid_str, qty in cart.items():
        product = _lookup_product(int(pid_str))
        if product:
            line_total = Decimal(product["price"]) * qty
            subtotal += line_total
            items.append({
                "product": product,
                "quantity": qty,
                "line_total": str(line_total),
            })
    return {
        "items": items,
        "subtotal": str(subtotal),
        "item_count": sum(cart.values()),
    }


# ---------------------------------------------------------------------------
# Checkout & Order
# ---------------------------------------------------------------------------

def checkout(request):
    """Display checkout form (GET) or process order (POST)."""
    cart = _get_cart(request)
    if not cart:
        return redirect("store:home")

    cart_data = _build_cart_detail(cart)
    # Shipping: free over $100
    subtotal = Decimal(cart_data["subtotal"])
    shipping = Decimal("0.00") if subtotal >= 100 else Decimal("9.99")
    total = subtotal + shipping

    if request.method == "POST":
        # Gather form data
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        zip_code = request.POST.get("zip_code", "").strip()
        country = request.POST.get("country", "").strip() or "United States"
        note = request.POST.get("note", "").strip()

        errors = []
        if not first_name:
            errors.append("First name is required.")
        if not last_name:
            errors.append("Last name is required.")
        if not email:
            errors.append("Email is required.")
        if not address:
            errors.append("Address is required.")
        if not city:
            errors.append("City is required.")
        if not zip_code:
            errors.append("ZIP code is required.")

        if errors:
            context = {
                "cart_items": cart_data["items"],
                "subtotal": str(subtotal),
                "shipping": str(shipping),
                "total": str(total),
                "cart_count": _cart_count(request),
                "errors": errors,
                "form": request.POST,
            }
            return render(request, "store/checkout.html", context)

        # Create order
        order_kwargs = dict(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            country=country,
            note=note,
            subtotal=subtotal,
            shipping=shipping,
            total=total,
        )
        if request.user.is_authenticated:
            order_kwargs["user"] = request.user
        order = Order.objects.create(**order_kwargs)

        # Create order items
        for item in cart_data["items"]:
            OrderItem.objects.create(
                order=order,
                product_name=item["product"]["name"],
                product_image=item["product"].get("image", ""),
                price=Decimal(item["product"]["price"]),
                quantity=item["quantity"],
            )

        # Clear cart
        _save_cart(request, {})

        return redirect("store:order_confirmation", order_number=order.order_number)

    # GET — pre-fill form for logged-in users
    form_data = {}
    if request.user.is_authenticated:
        form_data = {
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
        }
    context = {
        "cart_items": cart_data["items"],
        "subtotal": str(subtotal),
        "shipping": str(shipping),
        "total": str(total),
        "cart_count": _cart_count(request),
        "form": form_data,
    }
    return render(request, "store/checkout.html", context)


def order_confirmation(request, order_number):
    """Display the order confirmation page."""
    try:
        order = Order.objects.prefetch_related("items").get(order_number=order_number)
    except Order.DoesNotExist:
        from django.http import Http404
        raise Http404("Order not found")

    context = {
        "order": order,
        "cart_count": _cart_count(request),
    }
    return render(request, "store/order_confirmation.html", context)


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def user_register(request):
    """User registration page."""
    if request.user.is_authenticated:
        return redirect("store:home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()

        errors = []
        if not username:
            errors.append("Username is required.")
        if not email:
            errors.append("Email is required.")
        if not password:
            errors.append("Password is required.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != password2:
            errors.append("Passwords do not match.")
        if User.objects.filter(username=username).exists():
            errors.append("Username is already taken.")
        if User.objects.filter(email=email).exists():
            errors.append("Email is already registered.")

        if errors:
            return render(request, "store/register.html", {
                "errors": errors,
                "form": request.POST,
                "cart_count": _cart_count(request),
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        login(request, user)
        return redirect("store:home")

    return render(request, "store/register.html", {
        "cart_count": _cart_count(request),
    })


def user_login(request):
    """User login page."""
    if request.user.is_authenticated:
        return redirect("store:home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        next_url = request.POST.get("next", "")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(next_url if next_url else "store:home")
        else:
            return render(request, "store/login.html", {
                "errors": ["Invalid username or password."],
                "form": request.POST,
                "cart_count": _cart_count(request),
            })

    return render(request, "store/login.html", {
        "cart_count": _cart_count(request),
        "next": request.GET.get("next", ""),
    })


def user_logout(request):
    """Log the user out."""
    logout(request)
    return redirect("store:home")
