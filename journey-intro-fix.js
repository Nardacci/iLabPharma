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
    const visual=document.querySelector('.journey-intro-visual');
    if(!visual) return;
    visual.className='journey-process-visual';
    visual.setAttribute('aria-label','Visual conceitual de processos conectados');
    visual.innerHTML='<img src="assets/journey-process-visual.svg" alt="Processos conectados por fluxos de informação" loading="eager">';
  };
})();