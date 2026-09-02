(function(){
  const originalRenderJourneyIntro=window.renderJourneyIntro;
  if(typeof originalRenderJourneyIntro!=='function') return;

  const processVisual=`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 620" role="img" aria-label="Processos conectados por fluxos de informação">
      <defs>
        <radialGradient id="pvbg" cx="50%" cy="45%" r="65%"><stop offset="0" stop-color="#12344a"/><stop offset="1" stop-color="#020a12"/></radialGradient>
        <linearGradient id="pvblue" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#57c8ff"/><stop offset="1" stop-color="#146c9e"/></linearGradient>
        <linearGradient id="pvorange" x1="0" y1="1" x2="1" y2="0"><stop stop-color="#ff8500"/><stop offset="1" stop-color="#ffb34d"/></linearGradient>
        <filter id="pvglow"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        <pattern id="pvgrid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M28 0H0V28" fill="none" stroke="#6aa0b8" stroke-opacity=".07"/></pattern>
      </defs>
      <rect width="900" height="620" rx="32" fill="url(#pvbg)"/>
      <rect x="28" y="28" width="844" height="564" rx="28" fill="url(#pvgrid)"/>
      <g fill="none" stroke-linecap="round">
        <path d="M70 175 C170 175 190 105 300 105 S390 165 450 165 S570 92 690 120 S760 195 830 195" stroke="url(#pvblue)" stroke-width="5" opacity=".85"/>
        <path d="M70 445 C170 445 185 515 285 515 S380 438 450 438 S565 520 660 475 S750 390 830 390" stroke="url(#pvorange)" stroke-width="5" opacity=".9"/>
        <path d="M100 310H250M650 310H800" stroke="#64bde5" stroke-width="2" stroke-dasharray="5 9" opacity=".35"/>
      </g>
      <g filter="url(#pvglow)" fill="#07131d" stroke="#57c8ff" stroke-width="2"><circle cx="70" cy="175" r="7"/><circle cx="300" cy="105" r="7"/><circle cx="690" cy="120" r="7"/><circle cx="830" cy="195" r="7"/></g>
      <g filter="url(#pvglow)" fill="#101a20" stroke="#ff8500" stroke-width="2"><circle cx="70" cy="445" r="7"/><circle cx="285" cy="515" r="7"/><circle cx="660" cy="475" r="7"/><circle cx="830" cy="390" r="7"/></g>

      <!-- gears -->
      <g fill="#091923" stroke="#d8e7ee" stroke-width="3">
        <g transform="translate(130 55) scale(.72)"><path d="M130 8l12 6 10-7 13 13-7 10 6 12 12 2v18l-12 2-5 12 7 10-13 13-10-7-12 6-2 12H111l-3-12-12-5-10 7-13-13 7-10-6-12-12-2V47l12-2 5-12-7-10L85 10l10 7 12-6 2-12h21z"/><circle cx="120" cy="54" r="22" fill="#102b3a"/></g>
        <g transform="translate(650 45) scale(.68)"><path d="M130 8l12 6 10-7 13 13-7 10 6 12 12 2v18l-12 2-5 12 7 10-13 13-10-7-12 6-2 12H111l-3-12-12-5-10 7-13-13 7-10-6-12-12-2V47l12-2 5-12-7-10L85 10l10 7 12-6 2-12h21z"/><circle cx="120" cy="54" r="22" fill="#102b3a"/></g>
        <g transform="translate(115 365) scale(.62)"><path d="M130 8l12 6 10-7 13 13-7 10 6 12 12 2v18l-12 2-5 12 7 10-13 13-10-7-12 6-2 12H111l-3-12-12-5-10 7-13-13 7-10-6-12-12-2V47l12-2 5-12-7-10L85 10l10 7 12-6 2-12h21z"/><circle cx="120" cy="54" r="22" fill="#102b3a"/></g>
        <g transform="translate(680 350) scale(.58)"><path d="M130 8l12 6 10-7 13 13-7 10 6 12 12 2v18l-12 2-5 12 7 10-13 13-10-7-12 6-2 12H111l-3-12-12-5-10 7-13-13 7-10-6-12-12-2V47l12-2 5-12-7-10L85 10l10 7 12-6 2-12h21z"/><circle cx="120" cy="54" r="22" fill="#102b3a"/></g>
      </g>

      <!-- process core -->
      <circle cx="450" cy="300" r="108" fill="#06131d" stroke="#ff8500" stroke-opacity=".85" stroke-width="2"/>
      <circle cx="450" cy="300" r="88" fill="none" stroke="#4bbfff" stroke-opacity=".25" stroke-dasharray="3 8"/>
      <circle cx="450" cy="300" r="70" fill="none" stroke="#ff8500" stroke-opacity=".22"/>
      <path d="M420 300h58m-25-25 25 25-25 25" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" filter="url(#pvglow)"/>
      <text x="450" y="366" fill="#b9cad4" font-family="Arial,sans-serif" font-size="13" font-weight="700" letter-spacing="3" text-anchor="middle">PROCESSO</text>

      <!-- information panels -->
      <g transform="translate(255 38)"><rect width="160" height="72" rx="12" fill="#071724" stroke="#3e8db4"/><path d="M18 51l24-17 21 9 25-27 39 17" fill="none" stroke="#54bfff" stroke-width="3"/><text x="18" y="20" fill="#a9c0cc" font-family="Arial,sans-serif" font-size="9" font-weight="700" letter-spacing="1.5">DADOS • FLUXO</text></g>
      <g transform="translate(285 500)"><rect width="160" height="70" rx="12" fill="#071724" stroke="#3e8db4"/><rect x="18" y="34" width="18" height="20" rx="2" fill="#287da8"/><rect x="45" y="25" width="18" height="29" rx="2" fill="#4bbfff"/><rect x="72" y="16" width="18" height="38" rx="2" fill="#ff8500"/><path d="M105 52l15-20 14 12 10-17" fill="none" stroke="#d9e8ef" stroke-width="2"/><text x="18" y="16" fill="#a9c0cc" font-family="Arial,sans-serif" font-size="9" font-weight="700" letter-spacing="1.5">CONTROLE</text></g>

      <!-- outcome -->
      <g transform="translate(780 275) rotate(28)"><rect x="-22" y="-48" width="44" height="96" rx="22" fill="#f3f8fb"/><path d="M-22 0h44v26a22 22 0 0 1-44 0z" fill="#1689c8"/><path d="M-22 0h44" stroke="#aac9da" stroke-width="2"/></g>
      <circle cx="785" cy="275" r="45" fill="none" stroke="#4bbfff" stroke-opacity=".2"/>
    </svg>`;

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
    visual.innerHTML=processVisual;
  };
})();