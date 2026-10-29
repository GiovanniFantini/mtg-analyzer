'use strict';
(() => {
  const toggle = document.querySelector('.site-menu-toggle');
  const sidebar = document.querySelector('.site-sidebar');
  const backdrop = document.querySelector('.site-backdrop');
  const mobile = matchMedia('(max-width: 1000px)');
  const setMenu = open => {
    const draftActive = document.body.classList.contains('draft-active');
    if (draftActive) open = false;
    toggle.setAttribute('aria-expanded', String(open));
    document.body.classList.toggle('site-menu-open', open);
    backdrop.hidden = !open;
    sidebar.inert = draftActive || mobile.matches && !open;
    const pageBody=document.querySelector('.site-body');
    if(pageBody)pageBody.inert=mobile.matches&&open;
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
  document.addEventListener('draft-table-mode-change', () => setMenu(false));
  setMenu(false);
  const advanced = document.querySelector('.site-catalog-filters');
  if (advanced && matchMedia('(max-width: 700px)').matches) advanced.open = false;
  // The same card query works from every workspace, including links shared by users.
  const applyCardQuery = () => {
    const query = new URLSearchParams(location.search).get('q');
    const input = document.querySelector('#search, #trk-search');
    if (query && input && document.querySelector('#cards, #trk-cards')) {
      input.value = query;
      input.dispatchEvent(new Event('input', {bubbles:true}));
      if (document.querySelector('#gallery')) location.hash = 'gallery';
    }
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', applyCardQuery);
  else applyCardQuery();

  // Long pages get a compact section directory. Editorial content stays visible
  // without JavaScript; this index only adds shortcuts to existing sections.
  const main = document.querySelector('main');
  const sections = [...main.querySelectorAll('section[id], article[id]')].filter(section =>
    section.querySelector(':scope > h2, :scope > div > h2') && !section.closest('[hidden]'));
  if (sections.length >= 4 && !main.querySelector('.draft-workspace-nav')) {
    const directory = document.createElement('details');
    directory.className = 'site-section-directory';
    const summary = document.createElement('summary');
    summary.textContent = 'In questa pagina: scegli una sezione';
    const links = document.createElement('nav');
    links.setAttribute('aria-label', 'Sezioni della pagina');
    for (const section of sections) {
      const heading = section.querySelector(':scope > h2, :scope > div > h2');
      const link = document.createElement('a');
      link.href = '#'+section.id;
      link.textContent = heading.textContent.trim();
      links.append(link);
    }
    directory.append(summary, links);
    const workspace = main.querySelector('.site-workspace-bar');
    if (workspace) workspace.after(directory); else main.prepend(directory);
  }
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
  top.addEventListener('click',event=>{event.preventDefault();window.scrollTo({top:0});document.querySelector('main').focus({preventScroll:true});});
  addEventListener('scroll', updateTop, {passive:true}); updateTop();

  // Prepare offscreen content only; never dim content already painted in view.
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  if ('IntersectionObserver' in window && !reduced.matches) {
    const reveal = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        const item = entry.target;
        const finish = event => {
          if (event.target !== item || event.animationName !== 'site-enter') return;
          item.classList.remove('site-enter', 'site-reveal-pending');
          item.removeEventListener('animationend', finish);
          item.removeEventListener('animationcancel', finish);
        };
        item.addEventListener('animationend', finish);
        item.addEventListener('animationcancel', finish);
        entry.target.classList.add('site-enter');
        reveal.unobserve(entry.target);
      }
    }, {threshold: 0, rootMargin: '0px 0px 64px 0px'});
    document.querySelectorAll('.site-hero,.site-task,.set,main>.report-section,main>.trk-panel,main>.panel').forEach((item, i) => {
      const rect = item.getBoundingClientRect();
      if (rect.width && rect.top < innerHeight && rect.bottom > 0) return;
      item.style.setProperty('--site-delay', `${Math.min(i % 3, 2) * 45}ms`);
      item.classList.add('site-reveal-pending');
      reveal.observe(item);
    });
    reduced.addEventListener('change', () => {
      if (reduced.matches) {
        reveal.disconnect();
        document.querySelectorAll('.site-enter,.site-reveal-pending').forEach(item => item.classList.remove('site-enter', 'site-reveal-pending'));
      }
    });
  }
  // Add keyboard stops only to overflowing regions, including new drilldowns.
  const tableRegions = new Map();
  let tableFrame = 0;
  const tableTitle = (region, table) => {
    const caption = table?.querySelector('caption')?.textContent.trim();
    if (caption) return caption;
    const scope = region.closest('article,section,details,dialog') || document.body;
    const headings = 'h1,h2,h3,h4,h5,h6,summary';
    for (let node = region; node && node !== scope; node = node.parentElement) {
      for (let previous = node.previousElementSibling; previous; previous = previous.previousElementSibling) {
        const heading = previous.matches(headings) ? previous : [...previous.querySelectorAll(headings)].at(-1);
        if (heading?.textContent.trim()) return heading.textContent.trim();
      }
    }
    return [...(table?.querySelectorAll('thead th') || [])].slice(0, 3).map(cell => cell.textContent.trim()).join(', ') || 'Dati';
  };
  const scheduleTables = () => {
    if (!tableFrame) tableFrame = requestAnimationFrame(syncTables);
  };
  const tableResize = 'ResizeObserver' in window ? new ResizeObserver(scheduleTables) : null;
  function syncTables() {
    tableFrame = 0;
    for (const [region, state] of tableRegions) {
      if (region.isConnected) continue;
      tableResize?.unobserve(region);
      if (state.table) tableResize?.unobserve(state.table);
      tableRegions.delete(region);
    }
    document.querySelectorAll('.tablewrap,.trk-table-wrap').forEach(region => {
      if (!tableRegions.has(region)) {
        tableRegions.set(region, {
          original: Object.fromEntries(['tabindex','role','aria-label'].map(name => [name, region.getAttribute(name)])),
          labelled: region.hasAttribute('aria-labelledby'), table: null
        });
        tableResize?.observe(region);
      }
      const state = tableRegions.get(region), table = region.querySelector('table');
      if (state.table !== table) {
        if (state.table) tableResize?.unobserve(state.table);
        if (table) tableResize?.observe(table);
        state.table = table;
      }
      const overflow = region.clientWidth > 0 && region.scrollWidth > region.clientWidth + 1;
      const values = {tabindex: '0', role: 'region', 'aria-label': `${tableTitle(region, table)}, tabella a scorrimento orizzontale`};
      for (const [name, value] of Object.entries(values)) {
        if (state.original[name] !== null || (name === 'aria-label' && state.labelled)) continue;
        if (overflow) region.setAttribute(name, value);
        else region.removeAttribute(name);
      }
    });
  }
  const content = document.body;
  if (content && 'MutationObserver' in window) new MutationObserver(scheduleTables).observe(content, {childList:true, subtree:true});
  addEventListener('resize', scheduleTables, {passive:true});
  syncTables();
})();
