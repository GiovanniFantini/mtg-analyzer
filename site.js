'use strict';
(() => {
  const toggle = document.querySelector('.site-menu-toggle');
  const sidebar = document.querySelector('.site-sidebar');
  const backdrop = document.querySelector('.site-backdrop');
  const mobile = matchMedia('(max-width: 1000px)');
  const setMenu = open => {
    toggle.setAttribute('aria-expanded', String(open));
    document.body.classList.toggle('site-menu-open', open);
    backdrop.hidden = !open;
    sidebar.inert = mobile.matches && !open;
  };
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    setMenu(open);
    if (open) (sidebar.querySelector('[aria-current="page"]') || sidebar.querySelector('a')).focus();
  });
  backdrop.addEventListener('click', () => { setMenu(false); toggle.focus(); });
  document.addEventListener('keydown', event => {
    if (toggle.getAttribute('aria-expanded') !== 'true') return;
    if (event.key === 'Escape') { setMenu(false); toggle.focus(); }
    if (event.key === 'Tab') {
      const items = [toggle, ...sidebar.querySelectorAll('a[href]')];
      if (event.shiftKey && document.activeElement === items[0]) { event.preventDefault(); items.at(-1).focus(); }
      else if (!event.shiftKey && document.activeElement === items.at(-1)) { event.preventDefault(); items[0].focus(); }
    }
  });
  sidebar.addEventListener('click', event => {
    const link = event.target.closest('a');
    if (link && mobile.matches) {
      setMenu(false);
      if (new URL(link.href).pathname === location.pathname) document.querySelector('main').focus({preventScroll:true});
    }
  });
  mobile.addEventListener('change', () => setMenu(false));
  setMenu(false);
  const advanced = document.querySelector('.site-catalog-filters');
  if (advanced && matchMedia('(max-width: 700px)').matches) advanced.open = false;
  const sync = () => {
    if (location.hash === '#site-content') return;
    let active = null;
    const path = value => value.replace(/index\.html$/, '');
    const aliases = {proft:'strategy',updates:'strategy',sentiment:'gallery'};
    const section = aliases[location.hash.slice(1)] || location.hash.slice(1) || 'gallery';
    sidebar.querySelectorAll('a[href]').forEach(a => {
      const url = new URL(a.href);
      const matches = path(url.pathname) === path(location.pathname) && (!url.hash || url.hash === '#'+section);
      if (matches) { a.setAttribute('aria-current', 'page'); active = a; }
      else a.removeAttribute('aria-current');
    });
    if (active) document.querySelector('#site-page-label').textContent = active.textContent.replace('⌂ ', '');
  };
  addEventListener('hashchange', sync); sync();
  const search = document.querySelector('#set-search');
  search?.addEventListener('input', () => {
    let n = 0;
    document.querySelectorAll('[data-set]').forEach(card => {
      card.hidden = !card.dataset.set.includes(search.value.trim().toLocaleLowerCase('it'));
      if (!card.hidden) n++;
    });
    document.querySelector('#empty').hidden = n > 0;
  });
  const top = document.querySelector('.site-to-top');
  const updateTop = () => { top.hidden = scrollY < 650; };
  addEventListener('scroll', updateTop, {passive:true}); updateTop();
})();
