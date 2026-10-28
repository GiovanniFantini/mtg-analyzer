'use strict';
(() => {
  const nav = document.querySelector('.draft-workspace-nav');
  if (!nav) return;
  const panels = new Map([
    ['assistant', document.getElementById('draft-assistant')],
    ['guide', document.querySelector('[data-draft-panel="guide"]')],
    ['pool', document.getElementById('draft-pool')],
    ['data', document.querySelector('[data-draft-panel="data"]')]
  ]);
  const links = [...nav.querySelectorAll('[data-draft-view]')];
  const textField = field => field?.matches('textarea,input:not([type]),input:is([type="text"],[type="search"],[type="email"],[type="url"],[type="tel"],[type="number"],[type="password"])') && field.closest('main');
  const keepFocusedFieldVisible = () => {
    const field = document.activeElement;
    if (!textField(field) || (window.visualViewport && window.visualViewport.scale !== 1)) return;
    const viewport = window.visualViewport;
    const rect = field.getBoundingClientRect();
    const navRect = nav.getBoundingClientRect();
    const barBottom = document.querySelector('.site-bar')?.getBoundingClientRect().bottom || 0;
    const top = Math.max(viewport?.offsetTop || 0, barBottom,
      getComputedStyle(nav).position === 'sticky' ? navRect.bottom : 0) + 12;
    const bottom = (viewport?.offsetTop || 0) + (viewport?.height || innerHeight) - 12;
    const delta = rect.top < top || rect.height > bottom - top ? rect.top - top :
      rect.bottom > bottom ? rect.bottom - bottom : 0;
    if (Math.abs(delta) > 1) window.scrollBy({top:delta, behavior:'instant'});
  };
  const updateScrollOffset = () => {
    const short = (window.visualViewport?.height ?? innerHeight) < 550;
    document.body.classList.toggle('draft-short-viewport', short);
    const barHeight = document.querySelector('.site-bar')?.getBoundingClientRect().height || 0;
    const stickyHeight = getComputedStyle(nav).position === 'sticky' ? nav.getBoundingClientRect().height : 0;
    document.documentElement.style.setProperty('--draft-scroll-top', Math.ceil(barHeight + stickyHeight + 16) + 'px');
  };
  const sizes = new ResizeObserver(updateScrollOffset);
  sizes.observe(nav);
  const bar = document.querySelector('.site-bar');
  if (bar) sizes.observe(bar);
  let viewportHeight = window.visualViewport?.height ?? innerHeight;
  const updateViewport = event => {
    const height = window.visualViewport?.height ?? innerHeight;
    const keyboardShrink = viewportHeight - height > 80;
    viewportHeight = height;
    // Keep the mobile nav out of the way until navigation, including through a tap's click event.
    if (textField(document.activeElement) && (matchMedia('(max-width:700px)').matches || height < 550)) {
      document.body.classList.add('draft-editing');
    }
    updateScrollOffset();
    if (event?.type === 'focusin' || keyboardShrink) requestAnimationFrame(keepFocusedFieldVisible);
  };
  addEventListener('resize', updateViewport);
  window.visualViewport?.addEventListener('resize', updateViewport);
  document.addEventListener('focusin', updateViewport);
  document.addEventListener('focusout', () => requestAnimationFrame(updateScrollOffset));
  new MutationObserver(updateScrollOffset).observe(document.body, {attributes:true, attributeFilter:['class']});
  updateScrollOffset();
  const report = document.getElementById('draft-report');
  let reportWasOpen = null;
  addEventListener('beforeprint', () => {
    if (reportWasOpen === null) reportWasOpen = report.open;
    report.open = true;
  });
  addEventListener('afterprint', () => {
    if (reportWasOpen !== null) report.open = reportWasOpen;
    reportWasOpen = null;
  });
  function reveal(target, moveFocus = false) {
    const view = [...panels].find(([, panel]) => panel === target || panel.contains(target))?.[0];
    if (!view) return;
    document.body.classList.remove('da-focused', 'draft-editing');
    const focusButton = document.getElementById('da-focus');
    focusButton.dataset.selected = 'false';
    focusButton.textContent = 'Solo assistente';
    for (const [name, panel] of panels) panel.hidden = name !== view;
    for (const link of links) {
      if (link.dataset.draftView === view) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    }
    for (let node = target; node && node !== document.body; node = node.parentElement) {
      if (node.tagName === 'DETAILS') node.open = true;
    }
    if (moveFocus) {
      if (!target.hasAttribute('tabindex')) target.tabIndex = -1;
      target.focus({preventScroll: true});
    }
  }
  const hashTarget = () => {
    try { return document.getElementById(decodeURIComponent(location.hash.slice(1))); }
    catch { return null; }
  };
  // Ordinary links remain usable without scripts; existing section URLs open their view.
  const initial = hashTarget();
  reveal(initial && [...panels.values()].some(panel => panel.contains(initial)) ? initial : panels.get('assistant'));
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href]');
    if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const url = new URL(link.href);
    if (url.origin !== location.origin || url.pathname !== location.pathname || !url.hash) return;
    let target;
    try { target = document.getElementById(decodeURIComponent(url.hash.slice(1))); }
    catch { return; }
    if (target) reveal(target, true);
  });
  addEventListener('hashchange', () => {
    const target = hashTarget() || (!location.hash ? panels.get('assistant') : null);
    if (target) {
      const active = document.activeElement;
      const focusHidden = active === document.body || [...panels.values()].some(panel => panel.contains(active) && !panel.contains(target));
      reveal(target, focusHidden);
      target.scrollIntoView({block: 'start'});
    }
  });
})();
