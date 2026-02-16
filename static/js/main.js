(() => {
  'use strict';

  // ── Nav scroll effect ──────────────────────
  const nav = document.getElementById('nav');
  if (nav) {
    const onScroll = () => {
      nav.classList.toggle('scrolled', window.scrollY > 20);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // ── Mobile menu ────────────────────────────
  const navToggle = document.getElementById('navToggle');
  const mobileMenu = document.getElementById('mobileMenu');
  if (navToggle && mobileMenu) {
    navToggle.addEventListener('click', () => {
      const open = mobileMenu.classList.toggle('open');
      navToggle.querySelectorAll('span').forEach((s, i) => {
        s.style.transform = open
          ? (i === 0 ? 'rotate(45deg) translate(5px, 5px)' : i === 2 ? 'rotate(-45deg) translate(5px, -5px)' : 'scaleX(0)')
          : '';
      });
    });
    document.addEventListener('click', e => {
      if (!navToggle.contains(e.target) && !mobileMenu.contains(e.target)) {
        mobileMenu.classList.remove('open');
      }
    });
  }

  // ── Scroll reveal — single shared observer ─
  // Fires AFTER the CSS pageIn animation completes (0.25s), so reveals
  // feel like a second layer of life rather than competing with the fade.
  const revealEls = document.querySelectorAll('[data-reveal]');
  if (revealEls.length) {
    const revealObs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const delay = parseFloat(entry.target.dataset.revealDelay || 0);
          setTimeout(() => entry.target.classList.add('revealed'), delay * 1000);
          revealObs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    revealEls.forEach(el => revealObs.observe(el));
  }

  // ── Feature / stat card animations — single shared observer ─
  // Cards start hidden via inline style, then animate in with a stagger
  // when they scroll into view. One observer handles all cards.
  const cardEls = document.querySelectorAll('.feature-card, .stat-card');
  if (cardEls.length) {
    // Set initial hidden state
    cardEls.forEach(card => {
      card.style.opacity = '0';
      card.style.transform = 'translateY(24px)';
      card.style.transition = 'none'; // prevent flash on set
    });

    const cardObs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const i = [...cardEls].indexOf(entry.target);
          // Stagger each card by 80ms, offset after CSS pageIn (250ms)
          setTimeout(() => {
            entry.target.style.transition = 'opacity 0.45s ease, transform 0.45s ease';
            entry.target.style.opacity    = '1';
            entry.target.style.transform  = 'translateY(0)';
          }, 250 + i * 80);
          cardObs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    cardEls.forEach(card => cardObs.observe(card));
  }

  // ── Flash auto-dismiss ─────────────────────
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach((flash, i) => {
    setTimeout(() => {
      flash.style.transition = 'all 0.4s ease';
      flash.style.opacity = '0';
      flash.style.transform = 'translateX(20px)';
      setTimeout(() => flash.remove(), 400);
    }, 4000 + i * 500);
  });

  // ── Persist theme / accent from localStorage ─
  const savedTheme  = localStorage.getItem('theme');
  const savedAccent = localStorage.getItem('accent');
  if (savedTheme)  document.body.dataset.theme = savedTheme;
  if (savedAccent) document.documentElement.style.setProperty('--accent', savedAccent);

  // ── Load appearance preferences ─────────────
  if (localStorage.getItem('compact_view') === 'true') {
    document.body.classList.add('compact-view');
  }
  if (localStorage.getItem('animations') === 'false') {
    document.body.classList.add('no-animations');
  }

  // ── Smooth active nav link on load ─────────
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.href === window.location.href) link.classList.add('active');
  });

  // ── Add task form expand ───────────────────
  const addInput  = document.getElementById('addInput');
  const addExtras = document.getElementById('addExtras');
  if (addInput) {
    document.addEventListener('click', e => {
      const bar = document.getElementById('addTaskBar');
      if (bar && !bar.contains(e.target)) {
        addExtras?.classList.remove('visible');
      }
    });
  }

  // ── Keyboard shortcuts ─────────────────────
  document.addEventListener('keydown', e => {
    if ((e.key === '/' || (e.ctrlKey && e.key === 'k')) && !isInputActive()) {
      e.preventDefault();
      document.getElementById('searchInput')?.focus();
    }
    if (e.key === 'n' && !isInputActive()) {
      e.preventDefault();
      addInput?.focus();
      addExtras?.classList.add('visible');
    }
    if (e.key === 'Escape') {
      document.getElementById('editModal')?.classList.remove('open');
      document.getElementById('mobileMenu')?.classList.remove('open');
    }
  });

  function isInputActive() {
    const tag = document.activeElement?.tagName;
    return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT';
  }

  // ── Keyboard shortcut hint ─────────────────
  if (addInput) {
    const hint = document.createElement('span');
    hint.className = 'kb-hint';
    hint.textContent = 'Press N';
    hint.style.cssText = `
      position: absolute;
      right: 12px;
      top: 50%;
      transform: translateY(-50%);
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.65rem;
      color: var(--text-3);
      pointer-events: none;
      transition: opacity 0.2s;
      opacity: 0.6;
    `;
    addInput.parentElement.style.position = 'relative';
    addInput.parentElement.appendChild(hint);
    addInput.addEventListener('focus', () => hint.style.opacity = '0');
    addInput.addEventListener('blur',  () => hint.style.opacity = '0.6');
  }

  // ── Button ripple (event delegation) ──────
  if (!document.getElementById('rippleStyle')) {
    const style = document.createElement('style');
    style.id = 'rippleStyle';
    style.textContent = '@keyframes rippleAnim { to { transform: scale(2.5); opacity: 0; } }';
    document.head.appendChild(style);
  }
  document.body.addEventListener('click', function(e) {
    const btn = e.target.closest('.btn');
    if (!btn) return;
    const ripple = document.createElement('span');
    const rect   = btn.getBoundingClientRect();
    const size   = Math.max(rect.width, rect.height);
    ripple.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      border-radius: 50%;
      background: rgba(255,255,255,0.15);
      left: ${e.clientX - rect.left - size/2}px;
      top: ${e.clientY - rect.top - size/2}px;
      transform: scale(0);
      animation: rippleAnim 0.5s ease-out forwards;
      pointer-events: none;
    `;
    btn.style.position = btn.style.position || 'relative';
    btn.style.overflow = 'hidden';
    btn.appendChild(ripple);
    setTimeout(() => ripple.remove(), 500);
  });

  // ── Sidebar active state highlighting ─────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.sidebar-link[data-href]').forEach(link => {
    if (link.dataset.href === currentPath) link.classList.add('active');
  });

  // ── Stat counters — smooth count-up animation ──
  // Targets any element with data-count="NUMBER".
  // Counts from 0 to the target over 1.2s using easeOutQuart,
  // starting after the CSS pageIn completes (250ms offset).
  // Example usage in HTML: <span data-count="128">128</span>
  function easeOutQuart(t) {
    return 1 - Math.pow(1 - t, 4);
  }

  function animateCounter(el) {
    const target   = parseFloat(el.dataset.count);
    const decimals = (el.dataset.count.includes('.')) ? el.dataset.count.split('.')[1].length : 0;
    const prefix   = el.dataset.countPrefix || '';
    const suffix   = el.dataset.countSuffix || '';
    const duration = 1200; // ms
    const start    = performance.now();

    function tick(now) {
      const elapsed  = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const value    = easeOutQuart(progress) * target;
      el.textContent = prefix + value.toFixed(decimals) + suffix;
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  const counterEls = document.querySelectorAll('[data-count]');
  if (counterEls.length) {
    const counterObs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          // Offset by 250ms to start after CSS pageIn finishes
          setTimeout(() => animateCounter(entry.target), 250);
          counterObs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });
    counterEls.forEach(el => counterObs.observe(el));
  }

  // ── Login / auth form field animation ─────
  // Staggers auth form fields in one by one after page load.
  // Targets .auth-form .form-group elements.
  // Works on login, register, and settings pages automatically.
  const authFields = document.querySelectorAll('.auth-form .form-group');
  if (authFields.length) {
    authFields.forEach((field, i) => {
      field.style.opacity   = '0';
      field.style.transform = 'translateY(16px)';
      field.style.transition = 'none';
      // Stagger after CSS pageIn (250ms) + 80ms per field
      setTimeout(() => {
        field.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        field.style.opacity    = '1';
        field.style.transform  = 'translateY(0)';
      }, 250 + i * 80);
    });
  }

  // ── Console easter egg ─────────────────────
  console.log('%cDOZO', 'font-family: monospace; font-size: 48px; color: #f59e0b; font-weight: bold;');
  console.log('%cBuilt with Flask + PostgreSQL + Jinja2', 'color: #9a9590; font-size: 12px;');

})();