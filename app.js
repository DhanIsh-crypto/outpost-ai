/* OUTPOST AI - Frontend interactions */
(function() {
  'use strict';

  // ----- Dark mode (persisted) -----
  function getDarkPref() {
    const saved = localStorage.getItem('outpost_dark');
    if (saved !== null) return saved === '1';
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  }
  function applyDark(on) {
    document.body.classList.toggle('dark-mode', on);
    localStorage.setItem('outpost_dark', on ? '1' : '0');
    const lbl = document.querySelector('[data-dark-label]');
    if (lbl) lbl.textContent = on ? 'Light mode' : 'Dark mode';
  }
  document.addEventListener('DOMContentLoaded', function() {
    applyDark(getDarkPref());
    const toggle = document.querySelector('[data-toggle-dark]');
    if (toggle) toggle.addEventListener('click', () => applyDark(!document.body.classList.contains('dark-mode')));

    // Role picker on auth pages
    document.querySelectorAll('.role-option').forEach(opt => {
      const input = opt.querySelector('input');
      if (input && input.checked) opt.classList.add('selected');
      opt.addEventListener('click', () => {
        document.querySelectorAll('.role-option').forEach(o => o.classList.remove('selected'));
        opt.classList.add('selected');
        if (input) input.checked = true;
      });
    });

    // Tabs
    document.querySelectorAll('[data-tabs]').forEach(tabset => {
      const tabs = tabset.querySelectorAll('.tab');
      tabs.forEach(t => t.addEventListener('click', () => {
        tabs.forEach(x => x.classList.remove('active'));
        t.classList.add('active');
        const target = t.getAttribute('data-tab');
        document.querySelectorAll('[data-tab-panel]').forEach(p => {
          p.style.display = p.getAttribute('data-tab-panel') === target ? '' : 'none';
        });
      }));
    });

    // Modals
    document.querySelectorAll('[data-modal-open]').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.getAttribute('data-modal-open');
        const modal = document.getElementById(id);
        if (modal) modal.classList.add('open');
      });
    });
    document.querySelectorAll('.modal-backdrop').forEach(b => {
      b.addEventListener('click', e => { if (e.target === b) b.classList.remove('open'); });
    });
    document.querySelectorAll('.modal-close').forEach(c => {
      c.addEventListener('click', () => {
        c.closest('.modal-backdrop').classList.remove('open');
      });
    });

    // Auto-dismiss flash alerts after 5s
    document.querySelectorAll('.alert').forEach(a => {
      setTimeout(() => { a.style.transition = 'opacity 400ms'; a.style.opacity = '0'; }, 5000);
    });

    // Animate progress bars / funnel fills
    document.querySelectorAll('[data-fill]').forEach(el => {
      const pct = el.getAttribute('data-fill');
      requestAnimationFrame(() => { el.style.width = pct + '%'; });
    });

    // Chart bar heights from data attrs
    document.querySelectorAll('[data-bar]').forEach(el => {
      const v = parseFloat(el.getAttribute('data-bar'));
      const max = parseFloat(el.getAttribute('data-bar-max') || '100');
      const h = Math.max(4, (v / max) * 100);
      requestAnimationFrame(() => { el.style.height = h + '%'; });
    });
  });
})();
