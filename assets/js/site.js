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

/* One-time entrances. Content stays visible when motion or browser support is absent. */
(() => {
  'use strict';
  const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (motionPreference.matches || !Element.prototype.animate) return;

  const activeAnimations = new Map();
  let observer;
  const reveal = (element, delay = 0, heading = false) => {
    if (motionPreference.matches || element.contains(document.activeElement)) return;
    const animation = element.animate([
      { opacity: 0, transform: `translateY(${heading ? 20 : 14}px)` },
      { opacity: 1, transform: 'translateY(0)' }
    ], {
      duration: heading ? 750 : 600,
      delay,
      easing: 'cubic-bezier(0.22, 1, 0.36, 1)',
      fill: 'backwards'
    });
    activeAnimations.set(element, animation);
    const cleanup = () => activeAnimations.delete(element);
    animation.finished.then(cleanup, cleanup);
  };

  // Stagger the introduction while preserving the original, readable H1 markup.
  document.querySelectorAll('.hero-copy > .eyebrow, .hero-copy > h1, .hero-description, .hero-copy > .actions, .availability, .hero-showcase')
    .forEach((element, index) => reveal(element, index * 80, element.tagName === 'H1'));

  if ('IntersectionObserver' in window) {
    observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        const siblings = Array.from(entry.target.parentElement.children);
        const delay = entry.target.matches('.project-card, .skill-rows > article')
          ? (siblings.indexOf(entry.target) % 3) * 90 : 0;
        reveal(entry.target, delay, entry.target.tagName === 'H1');
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -24px 0px' });

    document.querySelectorAll([
      '.page-intro > *', '.project-intro > .back-link', '.project-title-row',
      '.project-intro > .tags', '.section-heading', '.project-card',
      '.about-strip > *', '.contact-band > div', '.about-layout > *',
      '.skill-rows > article', '.service-list > article', '.project-cover',
      '.case-study > *', '.contact-layout > *', '.simple-content > *'
    ].join(',')).forEach((element) => observer.observe(element));
  }

  // Keyboard users should never have to wait for a focused control to appear.
  document.addEventListener('focusin', (event) => {
    activeAnimations.forEach((animation, element) => {
      if (element.contains(event.target)) animation.cancel();
    });
  });
  motionPreference.addEventListener('change', (event) => {
    if (!event.matches) return;
    observer?.disconnect();
    activeAnimations.forEach((animation) => animation.cancel());
    activeAnimations.clear();
  });
})();
