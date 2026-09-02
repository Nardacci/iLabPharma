function renderHome(){
  setCrumbs('iLabPharma','');
  app.innerHTML=`
    <section class="home-hero home-hero-focus">
      <div class="home-hero-copy">
        <div class="eyebrow"><span class="eyebrow-dot"></span> EXPERIÊNCIA DE PROCESSOS</div>
        <h1>Entenda a indústria.<br><span>Enxergue o processo.</span></h1>
        <p>Uma experiência visual para percorrer os processos documentados do iLabPharma, do contexto inicial às etapas finais.</p>
        <div class="home-actions">
          <button class="primary-btn home-cta" onclick="renderJourney(0)">Começar a jornada <span>→</span></button>
        </div>
      </div>
      <div class="hero-orbit hero-orbit-modules" aria-label="Módulos do sistema">
        <div class="orbit-ring ring-a"></div><div class="orbit-ring ring-b"></div><div class="orbit-ring ring-c"></div>
        <div class="orbit-core"><span>i</span><strong>LAB</strong><small>PHARMA</small></div>
        <button class="orbit-module module-1" title="Produção"><b>01</b><span>Produção</span></button>
        <button class="orbit-module module-2" title="Estoque"><b>02</b><span>Estoque</span></button>
        <button class="orbit-module module-3" title="Controle da Qualidade"><b>03</b><span>Controle da Qualidade</span></button>
        <button class="orbit-module module-4" title="Garantia da Qualidade"><b>04</b><span>Garantia da Qualidade</span></button>
        <button class="orbit-module module-5" title="Documentos"><b>05</b><span>Documentos</span></button>
        <button class="orbit-module module-6" title="Rastreabilidade"><b>06</b><span>Rastreabilidade</span></button>
        <button class="orbit-module module-7" title="Comercial"><b>07</b><span>Comercial</span></button>
        <button class="orbit-module module-8" title="Patrimônio"><b>08</b><span>Patrimônio</span></button>
      </div>
    </section>`;
}
renderHome();