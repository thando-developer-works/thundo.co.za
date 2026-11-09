/* Progressive enhancement: content and navigation remain available without JS. */
(() => {
  'use strict';
  const header = document.querySelector('.header-inner');
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#primary-nav');
  if (!header || !toggle || !nav) return;

  const mobile = window.matchMedia('(max-width: 800px)');
  const setOpen = (open) => {
    nav.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.innerHTML = open ? 'Close <span aria-hidden="true">×</span>' : 'Menu <span aria-hidden="true">☰</span>';
  };
  const syncViewport = () => {
    toggle.hidden = !mobile.matches;
    setOpen(false);
    // Keep focus reachable if a desktop navigation link was hidden on resize.
    if (mobile.matches && nav.contains(document.activeElement)) toggle.focus();
  };
  header.classList.add('is-enhanced');
  syncViewport();
  mobile.addEventListener('change', syncViewport);
  toggle.addEventListener('click', () => setOpen(toggle.getAttribute('aria-expanded') !== 'true'));
  nav.addEventListener('click', (event) => {
    if (event.target.closest('a') && mobile.matches) {
      setOpen(false);
      if (nav.contains(document.activeElement)) toggle.focus();
    }
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
      setOpen(false);
      toggle.focus();
    }
  });
  document.addEventListener('click', (event) => {
    if (!header.contains(event.target) && toggle.getAttribute('aria-expanded') === 'true') setOpen(false);
  });
  header.addEventListener('focusout', (event) => {
    if (event.relatedTarget && !header.contains(event.relatedTarget) && mobile.matches) setOpen(false);
  });
})();
