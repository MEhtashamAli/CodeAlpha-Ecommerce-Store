from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.home, name="home"),
    path("subscribe/", views.subscribe, name="subscribe"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("checkout/", views.checkout, name="checkout"),
    path("order/<str:order_number>/", views.order_confirmation, name="order_confirmation"),
    path("register/", views.user_register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/", views.cart_add, name="cart_add"),
    path("cart/remove/", views.cart_remove, name="cart_remove"),
    path("cart/update/", views.cart_update, name="cart_update"),
]
