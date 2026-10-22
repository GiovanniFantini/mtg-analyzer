'use strict';
(() => {
  const search = document.getElementById('combo-search');
  if (!search) return;
  const colors = document.getElementById('combo-colors');
  const role = document.getElementById('combo-role');
  const count = document.getElementById('combo-count');
  const packages = [...document.querySelectorAll('.draft-package')];
  const normalize = s => s.normalize('NFD').replace(/\p{M}/gu, '').replace(/’/g, "'").toLowerCase();
  function update() {
    const words = normalize(search.value).trim().split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const item of packages) {
      const fitsColors = !colors.value || [...item.dataset.colors].every(c => colors.value.includes(c));
      const fitsRole = !role.value || item.dataset.role.toLowerCase().includes(role.value.toLowerCase());
      item.hidden = !(fitsColors && fitsRole && words.every(w => normalize(item.dataset.search).includes(w)));
      if (!item.hidden) visible++;
    }
    count.textContent = visible ? `${visible} pacchetti su ${packages.length}` : 'Nessun pacchetto con questi filtri. Prova a togliere un filtro o cerca una singola carta.';
  }
  search.addEventListener('input', update);
  colors.addEventListener('change', update);
  role.addEventListener('change', update);
  document.getElementById('combo-reset').addEventListener('click', () => {
    search.value = ''; colors.value = ''; role.value = ''; update();
  });
  update();
})();
