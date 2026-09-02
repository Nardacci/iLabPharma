(function(){
  const originalRenderJourneyIntro=window.renderJourneyIntro;
  if(typeof originalRenderJourneyIntro!=='function') return;
  window.renderJourneyIntro=function(){
    originalRenderJourneyIntro();
    document.body.classList.add('journey-intro-fullscreen');
    const button=document.querySelector('.journey-start-btn span');
    if(button) button.textContent='Seguir';
    const btn=document.querySelector('.journey-start-btn');
    if(btn) btn.setAttribute('aria-label','Seguir para a jornada');
  };
})();