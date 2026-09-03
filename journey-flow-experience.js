/* Compatibility loader for the canonical Módulo Principal flow. */
(function(){
  const current='journey-flow.js?v=3.0.3';
  const existing=document.querySelector('script[data-principal-flow-current]');
  if(existing) return;
  const css=document.createElement('link');
  css.rel='stylesheet';
  css.href='journey-flow-v4.css?v=1.0.0';
  css.dataset.principalFlowV4='true';
  document.head.appendChild(css);
  const cssFix=document.createElement('link');
  cssFix.rel='stylesheet';
  cssFix.href='journey-flow-v5.css?v=1.0.0';
  cssFix.dataset.principalFlowV5='true';
  document.head.appendChild(cssFix);
  const script=document.createElement('script');
  script.dataset.principalFlowCurrent='true';
  script.src=current;
  script.onload=function(){
    const override=document.createElement('script');
    override.src='journey-flow-v4.js?v=1.0.0';
    override.dataset.principalFlowV4='true';
    document.head.appendChild(override);
  };
  document.head.appendChild(script);
})();
