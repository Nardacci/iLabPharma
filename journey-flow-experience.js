/* Compatibility loader for the canonical Módulo Principal flow. */
(function(){
  const current='journey-flow.js?v=3.0.3';
  const existing=document.querySelector('script[data-principal-flow-current]');
  if(existing) return;
  const script=document.createElement('script');
  script.dataset.principalFlowCurrent='true';
  script.src=current;
  document.head.appendChild(script);
})();
