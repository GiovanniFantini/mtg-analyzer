'use strict';
(() => {
 const mode=document.getElementById('pick-environment'),stats=document.getElementById('pick-show-stats');
 function update(){
  document.getElementById('pick-policy-arena').hidden=mode.value!=='arena';
  document.getElementById('pick-policy-pod').hidden=mode.value!=='pod';
  document.querySelectorAll('#pick-guide [data-pick-stat]').forEach(el=>el.hidden=!stats.checked);
 }
 mode.addEventListener('change',update);stats.addEventListener('change',update);update();
 document.querySelectorAll('[data-decisions]').forEach(button=>button.addEventListener('click',()=>{
  document.querySelectorAll('#pick-decisions .pick-decision').forEach(item=>item.open=button.dataset.decisions==='open');
 }));
})();
