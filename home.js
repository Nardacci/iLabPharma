function renderHome(){
  setCrumbs('iLabPharma','Visão geral');
  app.innerHTML=`
    <section class="home-hero">
      <div class="home-hero-copy">
        <div class="eyebrow"><span class="eyebrow-dot"></span> EXPERIÊNCIA DE PROCESSOS</div>
        <h1>Entenda a indústria.<br><span>Enxergue o processo.</span></h1>
        <p>O iLabPharma conecta pessoas, estruturas, materiais, produção e qualidade em uma visão única da operação farmacêutica.</p>
        <div class="home-actions">
          <button class="primary-btn home-cta" onclick="renderMap()">Explorar o mapa de processos <span>→</span></button>
          <button class="ghost-btn" onclick="renderProcessList()">Ver processos disponíveis</button>
        </div>
      </div>
      <div class="hero-orbit" aria-hidden="true">
        <div class="orbit-ring ring-a"></div><div class="orbit-ring ring-b"></div><div class="orbit-ring ring-c"></div>
        <div class="orbit-core"><span>i</span><strong>LAB</strong><small>PHARMA</small></div>
        <div class="orbit-node node-1"><b>01</b><span>Estrutura</span></div>
        <div class="orbit-node node-2"><b>02</b><span>Materiais</span></div>
        <div class="orbit-node node-3"><b>03</b><span>Produção</span></div>
        <div class="orbit-node node-4"><b>04</b><span>Qualidade</span></div>
      </div>
    </section>

    <section class="home-intro">
      <div><span class="section-kicker">O QUE É O ILABPHARMA</span><h2>Mais do que módulos.<br><span>Uma visão conectada da operação.</span></h2></div>
      <p>Esta experiência foi criada para mostrar como os processos se conectam de ponta a ponta. Em vez de navegar por telas isoladas, você acompanha a história da operação e aprofunda cada etapa quando quiser.</p>
    </section>

    <section class="home-principles">
      <article><div class="principle-icon orange">↗</div><div><strong>O fluxo mostra</strong><p>A sequência e a relação entre as etapas.</p></div></article>
      <article><div class="principle-icon blue">⌁</div><div><strong>A interação explica</strong><p>Clique em uma etapa e veja seu contexto.</p></div></article>
      <article><div class="principle-icon green">◈</div><div><strong>O detalhe aprofunda</strong><p>Regras, responsáveis, entradas e saídas sob demanda.</p></div></article>
    </section>

    <section class="module-section">
      <div class="section-head"><div><span class="section-kicker">ARQUITETURA DA EXPERIÊNCIA</span><h2>Processos atravessando módulos</h2></div><button class="text-btn" onclick="renderMap()">Ver mapa completo →</button></div>
      <div class="module-track">
        <button class="module-card principal" onclick="renderPlaceholder('Principal')"><span>01</span><i>Principal</i><strong>Governança e estrutura</strong><em>Explorar →</em></button>
        <button class="module-card estoque" onclick="renderProcess('recebimento')"><span>02</span><i>Estoque</i><strong>Materiais e movimentações</strong><em>Explorar →</em></button>
        <button class="module-card cq" onclick="renderProcess('quarentena')"><span>03</span><i>Controle da Qualidade</i><strong>Análises e resultados</strong><em>Explorar →</em></button>
        <button class="module-card gq" onclick="renderPlaceholder('Garantia da Qualidade')"><span>04</span><i>Garantia da Qualidade</i><strong>Governança da qualidade</strong><em>Explorar →</em></button>
        <button class="module-card docs" onclick="renderPlaceholder('Controle de Documentos')"><span>05</span><i>Controle de Documentos</i><strong>Documentação e controle</strong><em>Explorar →</em></button>
      </div>
    </section>

    <section class="story-card">
      <div class="story-copy"><span class="section-kicker">UMA HISTÓRIA DE PONTA A PONTA</span><h2>Da estrutura da indústria ao produto acabado.</h2><p>Um processo farmacêutico não acontece dentro de um único módulo. Ele atravessa diferentes áreas, controles e decisões até chegar ao resultado final.</p><button class="primary-btn" onclick="renderMap()">Ver a jornada →</button></div>
      <div class="story-flow">
        <div class="story-step"><span>01</span><strong>Indústria</strong></div><div class="story-step"><span>02</span><strong>Fábrica</strong></div><div class="story-step"><span>03</span><strong>Preparação</strong></div><div class="story-step"><span>04</span><strong>Medicamento</strong></div><div class="story-step"><span>05</span><strong>Produção</strong></div><div class="story-step"><span>06</span><strong>CQ</strong></div><div class="story-step"><span>07</span><strong>GQ</strong></div><div class="story-step"><span>08</span><strong>Produto acabado</strong></div>
      </div>
    </section>`;
}

renderHome();