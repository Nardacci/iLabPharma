(function(){
  function renderEnd(){
    if(typeof closeGeneralFlow==='function')closeGeneralFlow();
    document.body.className=document.body.className.replace(/journey-stage[1-8]-mode/g,'');
    document.body.classList.remove('home-mode','journey-intro-mode');
    document.body.classList.add('journey-mode','journey-end-mode');
    if(typeof setCrumbs==='function')setCrumbs('Jornada','Encerramento');
    document.querySelectorAll('.nav-item').forEach(x=>x.classList.remove('active'));
    app.innerHTML=`
      <section class="journey-end-screen">
        <main class="journey-end-main">
          <div class="journey-end-check" aria-hidden="true">✓</div>
          <span class="journey-end-kicker"><i></i> JORNADA CONCLUÍDA</span>
          <h1>Você percorreu a história<br><em>de ponta a ponta.</em></h1>
          <p class="journey-end-intro">Da estrutura da indústria ao produto acabado, a jornada apresentou os oito estágios documentados do<br class="desktop-only"> processo de produção de medicamentos.</p>
          <div class="journey-end-actions-bottom">
            <button class="journey-end-restart" onclick="renderJourney(0)">↻ Reiniciar jornada</button>
            <button class="journey-end-map" onclick="renderHome()">Voltar para a página principal <span>→</span></button>
          </div>
        </main>
      </section>`;
  }
  window.finishJourney=renderEnd;
})();