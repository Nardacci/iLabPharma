(function(){
  const originalRenderJourney=window.renderJourney;
  if(typeof originalRenderJourney!=='function') return;
  window.renderJourney=function(index,selected){
    document.body.classList.remove('journey-intro-fullscreen');
    document.body.classList.add('journey-mode');
    document.documentElement.classList.add('journey-page-scroll');
    document.body.classList.add('journey-page-scroll');
    return originalRenderJourney(index,selected);
  };
})();
