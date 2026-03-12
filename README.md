# Foey — Trendy Fashion & Lifestyle E-Commerce

A full-stack e-commerce platform built with **Django**. Features a sleek dark-themed UI, session-based shopping cart, user authentication, product details, and a full checkout process.

## Features
- Dynamic Shopping Cart (session-based)
- User Registration & Login
- Product Detail Pages
- Complete Checkout → Order Confirmation Flow
- Admin Dashboard (manage products, orders, users)
- Premium dark-mode UI with animations

## Tech Stack
- **Backend**: Django (Python)
- **Database**: SQLite
- **Frontend**: HTML5, Vanilla CSS, JavaScript
- **Icons**: Font Awesome

## 🚀 Deploy on Railway (Recommended)

1. Go to [railway.app](https://railway.app) and sign in with GitHub.
2. Click **"New Project → Deploy from GitHub repo"**.
3. Select `MEhtashamAli/CodeAlpha-Ecommerce-Store`.
4. Railway auto-detects Django and deploys. ✅
5. In the deployment settings, add environment variable:
   - `SECRET_KEY` → any random string

## Run Locally

```bash
# Clone
git clone https://github.com/MEhtashamAli/CodeAlpha-Ecommerce-Store.git
cd CodeAlpha-Ecommerce-Store

# Install deps
pip install -r requirements.txt

# Migrate & run
python manage.py migrate
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

## License
MIT
