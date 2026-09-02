(function(){
  const originalRenderJourney=window.renderJourney;
  if(typeof originalRenderJourney!=='function') return;
  window.renderJourney=function(index=0,selected=0){
    if(index!==1){ originalRenderJourney(index,selected); return; }
    const s=journeyStages[1];
    journeyIndex=1;
    journeySelected=Math.max(0,Math.min(selected,s.items.length-1));
    closeGeneralFlow();
    document.body.classList.remove('home-mode','journey-intro-mode');
    document.body.classList.add('journey-mode','journey-stage1-mode');
    setCrumbs('Jornada','Fábrica');
    document.querySelectorAll('.nav-item').forEach(x=>x.classList.remove('active'));
    const items=s.items;
    const selectedItem=items[journeySelected];
    app.innerHTML=`
      <section class="stage1-screen">
        <header class="stage1-header">
          <button class="stage1-brand" onclick="renderHome()" aria-label="Voltar para Home"><img src="assets/ilabpharma-logo.svg" alt="iLabPharma"></button>
          <div class="stage1-actions"><button class="stage1-home-btn" onclick="renderHome()" aria-label="Voltar para Home" title="Voltar para Home">⌂</button><button class="stage1-login" onclick="renderPlaceholder('Acesso')"><span>♙</span> Entrar</button></div>
        </header>
        <div class="stage1-layout">
          <aside class="stage1-sidebar">
            <div class="stage1-side-title"><span>02</span><div><strong>Fábrica</strong><small>Onde o medicamento será produzido?</small></div></div>
            <nav class="stage1-items" aria-label="Elementos da Fábrica">
              ${items.map((item,i)=>`<button class="stage1-item ${i===journeySelected?'selected':''}" onclick="renderJourney(1,${i})"><span>${String(i+1).padStart(2,'0')}</span><strong>${item.name}</strong><em>›</em></button>`).join('')}
              <button class="stage1-item stage1-flow-item" onclick="openGeneralFlow()"><span>◎</span><strong>Fluxo</strong><em>›</em></button>
            </nav>
            <div class="stage1-side-result"><span>AO FINAL DESTA ETAPA</span><strong>A fábrica estará<br>pronta para<br>produzir.</strong></div>
          </aside>
          <main class="stage1-main">
            <div class="stage1-context"><span class="stage1-kicker"><i></i> O AMBIENTE ONDE A OPERAÇÃO ACONTECE</span><h2>É na <em>fábrica</em> que a operação acontece.</h2><p>Com a estrutura organizacional definida, a próxima etapa é representar o ambiente onde a operação acontece. A fábrica reúne os locais e recursos apresentados no processo de produção.</p></div>
            <div class="stage1-detail"><div class="stage1-detail-top"><span class="stage1-detail-number">${String(journeySelected+1).padStart(2,'0')}</span><div><span class="stage1-section-label">ELEMENTO DA ESTRUTURA</span><h3>${selectedItem.name}</h3></div></div><p>${selectedItem.text}</p><div class="stage1-source"><span>FONTE</span><strong>${selectedItem.source}</strong></div></div>
            <div class="stage1-questions"><span class="stage1-section-label">AS PERGUNTAS QUE ESTRUTURAM ESTA ETAPA</span><div class="stage1-question-grid"><button onclick="renderJourney(1,0)"><b>01</b><strong>Onde a operação acontece?</strong><span>Ambientes e localizações</span></button><button onclick="renderJourney(1,2)"><b>02</b><strong>Quais recursos fazem parte da fábrica?</strong><span>Equipamentos e instrumentos</span></button><button onclick="renderJourney(1,4)"><b>03</b><strong>Como a estrutura física é representada?</strong><span>Linhas, centros e localizações</span></button></div></div>
            <div class="stage1-bottom"><button class="ghost-btn" onclick="renderJourney(0)">← Anterior</button><div><span>Você está aqui</span><strong>Fábrica</strong></div><button class="primary-btn" onclick="renderJourney(2)">Continuar →</button></div>
          </main>
        </div>
      </section>`;
  };
})();