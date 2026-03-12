// ===== Foey — E-Commerce Landing Page JS =====

document.addEventListener('DOMContentLoaded', () => {

  // ---- CSRF token for AJAX ----
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';

  function postJSON(url, body) {
    return fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify(body),
    }).then(r => r.json());
  }

  // ---- Navbar Scroll Effect ----
  const navbar = document.getElementById('navbar');
  const onScroll = () => {
    navbar.classList.toggle('scrolled', window.scrollY > 40);
  };
  window.addEventListener('scroll', onScroll, { passive: true });

  // ---- User Dropdown Toggle ----
  const userBtn = document.querySelector('.nav-user-btn');
  const userDropdown = document.getElementById('user-dropdown');
  if (userBtn && userDropdown) {
    userBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      userDropdown.classList.toggle('open');
    });
    document.addEventListener('click', () => {
      userDropdown.classList.remove('open');
    });
  }

  // ---- Mobile Menu Toggle ----
  const menuToggle = document.getElementById('menu-toggle');
  const navLinks = document.getElementById('nav-links');
  if (menuToggle) {
    menuToggle.addEventListener('click', () => {
      const open = navLinks.style.display === 'flex';
      navLinks.style.display = open ? 'none' : 'flex';
      navLinks.style.position = open ? '' : 'absolute';
      navLinks.style.top = open ? '' : '72px';
      navLinks.style.left = open ? '' : '0';
      navLinks.style.width = open ? '' : '100%';
      navLinks.style.flexDirection = open ? '' : 'column';
      navLinks.style.alignItems = open ? '' : 'center';
      navLinks.style.gap = open ? '' : '20px';
      navLinks.style.padding = open ? '' : '24px 0';
      navLinks.style.background = open ? '' : 'rgba(10,10,15,0.95)';
      navLinks.style.backdropFilter = open ? '' : 'blur(20px)';
      navLinks.style.borderBottom = open ? '' : '1px solid rgba(255,255,255,0.06)';
    });
  }

  // ---- Scroll Reveal (Intersection Observer) ----
  const revealEls = document.querySelectorAll('.reveal');
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  revealEls.forEach(el => revealObserver.observe(el));

  // ---- Product Tab Filtering ----
  const tabBtns = document.querySelectorAll('.tab-btn');
  const productCards = document.querySelectorAll('.product-card');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const filter = btn.dataset.filter;

      productCards.forEach(card => {
        const tag = card.dataset.tag;
        if (filter === 'all' || tag === filter) {
          card.style.display = '';
          requestAnimationFrame(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
          });
        } else {
          card.style.opacity = '0';
          card.style.transform = 'translateY(20px)';
          setTimeout(() => { card.style.display = 'none'; }, 350);
        }
      });
    });
  });

  // ---- Countdown Timer ----
  const deadline = new Date();
  deadline.setDate(deadline.getDate() + 2);
  deadline.setHours(deadline.getHours() + 14);
  deadline.setMinutes(deadline.getMinutes() + 36);

  function updateTimer() {
    const now = new Date();
    let diff = deadline - now;
    if (diff < 0) diff = 0;

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
    const minutes = Math.floor((diff / (1000 * 60)) % 60);
    const seconds = Math.floor((diff / 1000) % 60);

    const pad = n => String(n).padStart(2, '0');
    document.getElementById('timer-days').textContent = pad(days);
    document.getElementById('timer-hours').textContent = pad(hours);
    document.getElementById('timer-minutes').textContent = pad(minutes);
    document.getElementById('timer-seconds').textContent = pad(seconds);
  }
  updateTimer();
  setInterval(updateTimer, 1000);

  // ---- Newsletter Form ----
  const form = document.getElementById('newsletter-form');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const input = document.getElementById('newsletter-email');
      const btn = document.getElementById('newsletter-submit');
      btn.textContent = '✓ Subscribed!';
      btn.style.pointerEvents = 'none';
      input.value = '';
      setTimeout(() => {
        btn.textContent = 'Subscribe';
        btn.style.pointerEvents = '';
      }, 3000);
    });
  }

  // ---- Wishlist Toggle ----
  document.querySelectorAll('.product-wishlist').forEach(btn => {
    btn.addEventListener('click', () => {
      const icon = btn.querySelector('i');
      const isFilled = icon.classList.contains('fa-solid');
      icon.classList.toggle('fa-regular', isFilled);
      icon.classList.toggle('fa-solid', !isFilled);
      btn.style.color = isFilled ? '' : '#dc3c3c';
      btn.style.background = isFilled ? '' : 'rgba(220,60,60,0.15)';
      btn.style.borderColor = isFilled ? '' : 'rgba(220,60,60,0.3)';
    });
  });

  // ---- Smooth scroll for anchor links ----
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        if (window.innerWidth <= 768 && navLinks) {
          navLinks.style.display = 'none';
        }
        // Close cart drawer if open
        closeCartDrawer();
      }
    });
  });

  // =================================================================
  //  CART DRAWER
  // =================================================================
  const cartOverlay   = document.getElementById('cart-overlay');
  const cartDrawer    = document.getElementById('cart-drawer');
  const cartDrawerBody = document.getElementById('cart-drawer-body');
  const cartDrawerFooter = document.getElementById('cart-drawer-footer');
  const cartEmpty     = document.getElementById('cart-empty');
  const cartSubtotal  = document.getElementById('cart-subtotal');
  const cartBadge     = document.querySelector('.cart-count');
  const cartBtn       = document.getElementById('cart-btn');
  const cartCloseBtn  = document.getElementById('cart-drawer-close');
  const cartShopLink  = document.getElementById('cart-shop-link');

  function openCartDrawer() {
    cartOverlay.classList.add('open');
    cartDrawer.classList.add('open');
    document.body.style.overflow = 'hidden';
    refreshCart();
  }

  function closeCartDrawer() {
    cartOverlay.classList.remove('open');
    cartDrawer.classList.remove('open');
    document.body.style.overflow = '';
  }

  cartBtn.addEventListener('click', openCartDrawer);
  cartCloseBtn.addEventListener('click', closeCartDrawer);
  cartOverlay.addEventListener('click', closeCartDrawer);

  if (cartShopLink) {
    cartShopLink.addEventListener('click', () => closeCartDrawer());
  }

  // Checkout button
  const checkoutBtn = document.getElementById('cart-checkout-btn');
  if (checkoutBtn) {
    checkoutBtn.addEventListener('click', () => {
      window.location.href = '/checkout/';
    });
  }

  // Close drawer on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeCartDrawer();
  });

  // ---- Update badge count ----
  function updateBadge(count) {
    cartBadge.textContent = count;
    cartBadge.style.display = count > 0 ? 'flex' : 'none';
    // Pulse animation
    cartBadge.style.transform = 'scale(1.4)';
    setTimeout(() => { cartBadge.style.transform = 'scale(1)'; }, 200);
  }

  // ---- Toast notification ----
  function showToast(message) {
    // Remove existing toasts
    document.querySelectorAll('.cart-toast').forEach(t => t.remove());

    const toast = document.createElement('div');
    toast.className = 'cart-toast';
    toast.innerHTML = `
      <div class="cart-toast-icon"><i class="fa-solid fa-check"></i></div>
      <span class="cart-toast-text">${message}</span>
    `;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('hiding');
      setTimeout(() => toast.remove(), 300);
    }, 2200);
  }

  // ---- Render cart items ----
  function renderCart(data) {
    const { items, subtotal, item_count } = data;
    updateBadge(item_count);

    // Remove old cart items (keep the empty state element)
    cartDrawerBody.querySelectorAll('.cart-item').forEach(el => el.remove());

    if (items.length === 0) {
      cartEmpty.style.display = 'flex';
      cartDrawerFooter.style.display = 'none';
      return;
    }

    cartEmpty.style.display = 'none';
    cartDrawerFooter.style.display = '';

    items.forEach((item, i) => {
      const el = document.createElement('div');
      el.className = 'cart-item';
      el.style.animationDelay = `${i * 0.06}s`;
      el.innerHTML = `
        <div class="cart-item-image">
          <img src="/static/${item.product.image}" alt="${item.product.name}">
        </div>
        <div class="cart-item-details">
          <div class="cart-item-name">${item.product.name}</div>
          <div class="cart-item-category">${item.product.category}</div>
          <div class="cart-item-bottom">
            <span class="cart-item-price">$${item.line_total}</span>
            <div class="cart-qty-controls">
              <button class="cart-qty-btn qty-minus" data-id="${item.product.id}" aria-label="Decrease quantity"><i class="fa-solid fa-minus"></i></button>
              <span class="cart-qty-value">${item.quantity}</span>
              <button class="cart-qty-btn qty-plus" data-id="${item.product.id}" aria-label="Increase quantity"><i class="fa-solid fa-plus"></i></button>
            </div>
          </div>
        </div>
        <button class="cart-item-remove" data-id="${item.product.id}" aria-label="Remove item"><i class="fa-solid fa-trash-can"></i></button>
      `;
      cartDrawerBody.insertBefore(el, cartEmpty);
    });

    cartSubtotal.textContent = `$${subtotal}`;

    // Bind quantity and remove buttons
    cartDrawerBody.querySelectorAll('.qty-minus').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.id;
        const qtyEl = btn.parentElement.querySelector('.cart-qty-value');
        const newQty = parseInt(qtyEl.textContent) - 1;
        if (newQty <= 0) {
          removeFromCart(id);
        } else {
          updateCartQty(id, newQty);
        }
      });
    });

    cartDrawerBody.querySelectorAll('.qty-plus').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.id;
        const qtyEl = btn.parentElement.querySelector('.cart-qty-value');
        const newQty = parseInt(qtyEl.textContent) + 1;
        updateCartQty(id, newQty);
      });
    });

    cartDrawerBody.querySelectorAll('.cart-item-remove').forEach(btn => {
      btn.addEventListener('click', () => {
        removeFromCart(btn.dataset.id);
      });
    });
  }

  // ---- Cart API calls ----
  function refreshCart() {
    fetch('/cart/').then(r => r.json()).then(data => {
      renderCart(data.cart);
    });
  }

  function addToCart(productId) {
    postJSON('/cart/add/', { product_id: productId }).then(data => {
      if (data.success) {
        updateBadge(data.cart_count);
        showToast(`${data.product.name} added to cart`);
        // If drawer is open, refresh it
        if (cartDrawer.classList.contains('open')) {
          refreshCart();
        }
      }
    });
  }

  function updateCartQty(productId, quantity) {
    postJSON('/cart/update/', { product_id: productId, quantity }).then(data => {
      if (data.success) {
        renderCart(data.cart);
      }
    });
  }

  function removeFromCart(productId) {
    postJSON('/cart/remove/', { product_id: productId }).then(data => {
      if (data.success) {
        renderCart(data.cart);
        showToast('Item removed from cart');
      }
    });
  }

  // ---- Add to Cart buttons on product cards ----
  document.querySelectorAll('.quick-add-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const productId = parseInt(btn.dataset.productId);
      if (!productId) return;

      // Button feedback
      const original = btn.textContent;
      btn.textContent = '✓ Added!';
      btn.style.background = '#2ecc71';
      setTimeout(() => {
        btn.textContent = original;
        btn.style.background = '';
      }, 1200);

      addToCart(productId);
    });
  });

  // ---- Initialize: load cart state on page load ----
  fetch('/cart/').then(r => r.json()).then(data => {
    updateBadge(data.cart_count);
  });

});
