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

    visual.className='journey-intro-visual home-orbit';
    visual.setAttribute('aria-label','Ecossistema de módulos');
    visual.innerHTML=`
      <div class="orbit-glow"></div>
      <div class="orbit-ring ring-outer"></div>
      <div class="orbit-ring ring-middle"></div>
      <div class="orbit-ring ring-inner"></div>
      <div class="orbit-cross cross-v"></div>
      <div class="orbit-cross cross-h"></div>
      <div class="orbit-core"><img src="assets/ilabpharma-logo.svg" alt="iLabPharma"></div>
      <div class="orbit-module module-1"><div class="module-icon"><svg viewBox="0 0 32 32" aria-hidden="true"><path d="M13 4h6l1 4 3 2 4-1 3 5-3 3v4l3 3-3 5-4-1-3 2-1 4h-6l-1-4-3-2-4 1-3-5 3-3v-4l-3-3 3-5 4 1 3-2 1-4z"/><circle cx="16" cy="19" r="5"/></svg></div><b class="module-label">PRODUÇÃO</b></div>
      <div class="orbit-module module-2"><div class="module-icon"><svg viewBox="0 0 32 32" aria-hidden="true"><path d="M12 4h8M14 4v8l-8 14c-.7 1.2.2 2 1.5 2h17c1.3 0 2.2-.8 1.5-2l-8-14V4M9 22h14"/></svg></div><b class="module-label">CQ</b></div>
      <div class="orbit-module module-3"><div class="module-icon"><svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16 3l11 4v8c0 7-4.5 11.5-11 14C9.5 26.5 5 22 5 15V7l11-4z"/><path d="m11 16 3 3 7-8"/></svg></div><b class="module-label">GQ</b></div>
      <div class="orbit-module module-4"><div class="module-icon"><svg viewBox="0 0 32 32" aria-hidden="true"><path d="M8 3h13l4 4v22H8zM21 3v5h5M12 14h9M12 19h9M12 24h6"/></svg></div><b class="module-label">DOCUMENTOS</b></div>
      <div class="orbit-module module-5"><div class="module-icon"><svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="8" cy="8" r="3"/><circle cx="24" cy="16" r="3"/><circle cx="8" cy="25" r="3"/><path d="M11 8h7l3 5M21 19l-10 4M11 25h7"/></svg></div><b class="module-label">RASTREABILIDADE</b></div>
      <div class="orbit-module module-6"><div class="module-icon"><svg viewBox="0 0 32 32" aria-hidden="true"><path d="M4 6h4l3 15h13l4-11H9M13 27a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0m13 0a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0"/></svg></div><b class="module-label">COMERCIAL</b></div>
      <div class="orbit-module module-7"><div class="module-icon"><svg viewBox="0 0 32 32" aria-hidden="true"><path d="m16 4 11 6-11 6L5 10 16 4zM5 10v12l11 6 11-6V10M16 16v12"/></svg></div><b class="module-label">ESTOQUE</b></div>
      <div class="orbit-module module-8"><div class="module-icon"><svg viewBox="0 0 32 32" aria-hidden="true"><rect x="7" y="4" width="18" height="24" rx="2"/><path d="M12 9h8M12 14h8M12 19h3m4 0h1M12 24h8"/></svg></div><b class="module-label">PATRIMÔNIO</b></div>`;
  };
})();