// ===== LUXE — E-Commerce Landing Page JS =====

document.addEventListener('DOMContentLoaded', () => {

  // ---- Navbar Scroll Effect ----
  const navbar = document.getElementById('navbar');
  const onScroll = () => {
    navbar.classList.toggle('scrolled', window.scrollY > 40);
  };
  window.addEventListener('scroll', onScroll, { passive: true });

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

  // ---- Add to Cart Animation ----
  document.querySelectorAll('.quick-add-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const original = btn.textContent;
      btn.textContent = '✓ Added!';
      btn.style.background = '#2ecc71';
      setTimeout(() => {
        btn.textContent = original;
        btn.style.background = '';
      }, 1500);
    });
  });

  // ---- Smooth scroll for anchor links ----
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        // Close mobile menu
        if (window.innerWidth <= 768 && navLinks) {
          navLinks.style.display = 'none';
        }
      }
    });
  });

});
