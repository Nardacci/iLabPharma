function renderHome(){
  setCrumbs('iLabPharma','Visão geral');
  app.innerHTML=`
    <section class="home-hero">
      <div class="home-hero-copy">
        <div class="eyebrow"><span class="eyebrow-dot"></span> EXPERIÊNCIA DE PROCESSOS</div>
        <h1>Entenda a indústria.<br><span>Enxergue o processo.</span></h1>
        <p>Uma experiência visual para percorrer os processos documentados do iLabPharma, do contexto inicial às etapas finais.</p>
        <div class="home-actions">
          <button class="primary-btn home-cta" onclick="renderJourney(0)">Começar a jornada <span>→</span></button>
          <button class="ghost-btn" onclick="renderMap()">Explorar o mapa de processos</button>
        </div>
      </div>
      <div class="hero-orbit" aria-hidden="true">
        <div class="orbit-ring ring-a"></div><div class="orbit-ring ring-b"></div><div class="orbit-ring ring-c"></div>
        <div class="orbit-core"><span>i</span><strong>LAB</strong><small>PHARMA</small></div>
        <div class="orbit-node node-1"><b>01</b><span>Estrutura</span></div><div class="orbit-node node-2"><b>02</b><span>Materiais</span></div><div class="orbit-node node-3"><b>03</b><span>Produção</span></div><div class="orbit-node node-4"><b>04</b><span>Qualidade</span></div>
      </div>
    </section>
    <section class="home-intro"><div><span class="section-kicker">COMO FUNCIONA</span><h2>A jornada conduz.<br><span>O fluxo mostra.</span></h2></div><p>Você pode seguir a narrativa de ponta a ponta ou explorar livremente o mapa e os processos disponíveis. Cada etapa pode ser aprofundada quando houver informação documentada para apresentar.</p></section>
    <section class="home-principles"><article><div class="principle-icon orange">↗</div><div><strong>A jornada conduz</strong><p>Avance do início ao fim sem perder o contexto.</p></div></article><article><div class="principle-icon blue">⌁</div><div><strong>O fluxo mostra</strong><p>Veja a sequência e a relação entre as etapas.</p></div></article><article><div class="principle-icon green">◈</div><div><strong>O detalhe aprofunda</strong><p>Consulte contexto e informações sob demanda.</p></div></article></section>
    <section class="module-section"><div class="section-head"><div><span class="section-kicker">EXPLORAÇÃO LIVRE</span><h2>Processos disponíveis</h2></div><button class="text-btn" onclick="renderMap()">Ver mapa completo →</button></div><div class="module-track"><button class="module-card principal" onclick="renderPlaceholder('Principal')"><span>01</span><i>Principal</i><strong>Governança e estrutura</strong><em>Explorar →</em></button><button class="module-card estoque" onclick="renderProcess('recebimento')"><span>02</span><i>Estoque</i><strong>Recebimento de materiais</strong><em>Explorar →</em></button><button class="module-card cq" onclick="renderProcess('quarentena')"><span>03</span><i>Controle da Qualidade</i><strong>Quarentena e análise</strong><em>Explorar →</em></button><button class="module-card gq" onclick="renderPlaceholder('Garantia da Qualidade')"><span>04</span><i>Garantia da Qualidade</i><strong>Processos documentados em evolução</strong><em>Explorar →</em></button><button class="module-card docs" onclick="renderPlaceholder('Controle de Documentos')"><span>05</span><i>Controle de Documentos</i><strong>Processos documentados em evolução</strong><em>Explorar →</em></button></div></section>
    <section class="story-card"><div class="story-copy"><span class="section-kicker">UMA HISTÓRIA DE PONTA A PONTA</span><h2>Da estrutura da indústria ao produto acabado.</h2><p>Esta jornada apresenta os oito estágios documentados no processo de produção de medicamentos.</p><button class="primary-btn" onclick="renderJourney(0)">Iniciar jornada →</button></div><div class="story-flow">${['Indústria','Fábrica','Preparação','Medicamento','Produção','CQ','GQ','Produto acabado'].map((x,i)=>`<div class="story-step"><span>${String(i+1).padStart(2,'0')}</span><strong>${x}</strong></div>`).join('')}</div></section>`;
}
renderHome();