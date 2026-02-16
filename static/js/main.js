/* ═══════════════════════════════════════════
   DOZO — Main JavaScript
   Global interactions, animations, utilities
═══════════════════════════════════════════ */

(() => {
  'use strict';

  // ── Nav scroll effect ──────────────────────
  const nav = document.getElementById('nav');
  if (nav) {
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 20);
    }, { passive: true });
  }

  // ── Mobile menu ────────────────────────────
  const navToggle  = document.getElementById('navToggle');
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

  // ── Scroll reveal (IntersectionObserver) ───
  // FIX: Use ONE shared observer instead of one per element — dramatically cheaper
  const revealEls = document.querySelectorAll('[data-reveal]');
  if (revealEls.length) {
    const revealObs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const delay = entry.target.dataset.revealDelay || 0;
          setTimeout(() => entry.target.classList.add('revealed'), delay * 1000);
          revealObs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    revealEls.forEach(el => revealObs.observe(el));
  }

  // ── Feature cards reveal — ONE shared observer ─
  // FIX: Was creating a new IntersectionObserver per card; now a single observer handles all
  const cardEls = document.querySelectorAll('.feature-card, .stat-card');
  if (cardEls.length) {
    cardEls.forEach((card, i) => {
      card.style.opacity   = '0';
      card.style.transform = 'translateY(20px)';
    });
    const cardObs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const i = [...cardEls].indexOf(entry.target);
          setTimeout(() => {
            entry.target.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            entry.target.style.opacity    = '1';
            entry.target.style.transform  = 'translateY(0)';
          }, i * 80);
          cardObs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    cardEls.forEach(card => cardObs.observe(card));
  }

  // ── Flash auto-dismiss ─────────────────────
  document.querySelectorAll('.flash').forEach((flash, i) => {
    setTimeout(() => {
      flash.style.transition = 'all 0.4s ease';
      flash.style.opacity    = '0';
      flash.style.transform  = 'translateX(20px)';
      setTimeout(() => flash.remove(), 400);
    }, 4000 + i * 500);
  });

  // ── Persist theme / accent from localStorage ─
  const savedTheme  = localStorage.getItem('theme');
  const savedAccent = localStorage.getItem('accent');
  if (savedTheme)  document.body.dataset.theme = savedTheme;
  if (savedAccent) document.documentElement.style.setProperty('--accent', savedAccent);

  // ── Smooth active nav link on load ─────────
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.href === window.location.href) link.classList.add('active');
  });

  // ── Add task form expand on outside click ──
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
      position: absolute; right: 12px; top: 50%;
      transform: translateY(-50%);
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.65rem; color: var(--text-3);
      pointer-events: none; transition: opacity 0.2s; opacity: 0.6;
    `;
    addInput.parentElement.style.position = 'relative';
    addInput.parentElement.appendChild(hint);
    addInput.addEventListener('focus', () => (hint.style.opacity = '0'));
    addInput.addEventListener('blur',  () => (hint.style.opacity = '0.6'));
  }

  // ── Button click ripple effect ─────────────
  // Inject the keyframe once
  if (!document.getElementById('rippleStyle')) {
    const style = document.createElement('style');
    style.id = 'rippleStyle';
    style.textContent = '@keyframes rippleAnim { to { transform: scale(2.5); opacity: 0; } }';
    document.head.appendChild(style);
  }
  document.querySelectorAll('.btn').forEach(btn => {
    btn.style.position = 'relative';
    btn.style.overflow = 'hidden';
    btn.addEventListener('click', function(e) {
      const ripple = document.createElement('span');
      const rect   = btn.getBoundingClientRect();
      const size   = Math.max(rect.width, rect.height);
      ripple.style.cssText = `
        position: absolute; width: ${size}px; height: ${size}px;
        border-radius: 50%; background: rgba(255,255,255,0.15);
        left: ${e.clientX - rect.left - size / 2}px;
        top: ${e.clientY - rect.top  - size / 2}px;
        transform: scale(0);
        animation: rippleAnim 0.5s ease-out forwards;
        pointer-events: none;
      `;
      btn.appendChild(ripple);
      setTimeout(() => ripple.remove(), 500);
    });
  });

  // ── Sidebar active state highlighting ─────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.sidebar-link[data-href]').forEach(link => {
    if (link.dataset.href === currentPath) link.classList.add('active');
  });

  // ── Page transition on nav links ──────────
  // Only intercepts plain GET navigation links — not forms, anchors, or
  // links with data-no-transition. Sets a sessionStorage flag so the
  // fade-in only plays after a real navigation, NOT on a hard refresh.
  document.querySelectorAll('a[href]').forEach(link => {
    if (
      link.hostname === window.location.hostname &&
      !link.href.includes('#') &&
      !link.target &&
      !link.closest('form') &&
      link.dataset.noTransition === undefined
    ) {
      link.addEventListener('click', e => {
        if (e.ctrlKey || e.metaKey || e.shiftKey) return;
        e.preventDefault();
        sessionStorage.setItem('navigating', '1');
        document.body.style.transition = 'opacity 0.15s ease';
        document.body.style.opacity = '0';
        setTimeout(() => { window.location.href = link.href; }, 150);
      });
    }
  });

  // ── Fade-in on page load ───────────────────
  // Only fade in when arriving via a link click, not on a hard refresh.
  if (sessionStorage.getItem('navigating')) {
    sessionStorage.removeItem('navigating');
    document.body.style.opacity    = '0';
    document.body.style.transition = 'opacity 0.2s ease';
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        document.body.style.opacity = '1';
      });
    });
  }

  // ── Console easter egg ─────────────────────
  console.log('%cDOZO', 'font-family: monospace; font-size: 48px; color: #f59e0b; font-weight: bold;');
  console.log('%cBuilt with Flask + PostgreSQL + Jinja2', 'color: #9a9590; font-size: 12px;');

})();