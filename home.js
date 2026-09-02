function renderHome(){
  document.body.classList.add('home-mode');
  setCrumbs('iLabPharma','');
  const modules=[
    {n:'01',title:'PRODUÇÃO',desc:'Planejamento, ordens de produção e execução industrial.',cls:'module-1',icon:'gear'},
    {n:'02',title:'ESTOQUE',desc:'Recebimento, armazenamento, movimentações e inventário.',cls:'module-2',icon:'box'},
    {n:'03',title:'CQ',desc:'Ensaios, resultados, especificações e laudos.',cls:'module-3',icon:'flask'},
    {n:'04',title:'GQ',desc:'CAPA, desvios, mudanças e treinamentos.',cls:'module-4',icon:'shield'},
    {n:'05',title:'DOCUMENTOS',desc:'Gestão eletrônica de documentos e registros.',cls:'module-5',icon:'document'},
    {n:'06',title:'RASTREABILIDADE',desc:'Rastreabilidade completa de lotes, séries e genealogia.',cls:'module-6',icon:'trace'},
    {n:'07',title:'COMERCIAL',desc:'Pedidos, cotações, faturamento e contratos.',cls:'module-7',icon:'cart'},
    {n:'08',title:'PATRIMÔNIO',desc:'Gestão de ativos, manutenções e calibrações.',cls:'module-8',icon:'asset'}
  ];
  const icons={
    gear:'<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M13 4h6l1 4 3 2 4-1 3 5-3 3v4l3 3-3 5-4-1-3 2-1 4h-6l-1-4-3-2-4 1-3-5 3-3v-4l-3-3 3-5 4 1 3-2 1-4z"/><circle cx="16" cy="19" r="5"/></svg>',
    box:'<svg viewBox="0 0 32 32" aria-hidden="true"><path d="m16 4 11 6-11 6L5 10 16 4zM5 10v12l11 6 11-6V10M16 16v12"/></svg>',
    flask:'<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M12 4h8M14 4v8l-8 14c-.7 1.2.2 2 1.5 2h17c1.3 0 2.2-.8 1.5-2l-8-14V4M9 22h14"/></svg>',
    shield:'<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16 3l11 4v8c0 7-4.5 11.5-11 14C9.5 26.5 5 22 5 15V7l11-4z"/><path d="m11 16 3 3 7-8"/></svg>',
    document:'<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M8 3h13l4 4v22H8zM21 3v5h5M12 14h9M12 19h9M12 24h6"/></svg>',
    trace:'<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="8" cy="8" r="3"/><circle cx="24" cy="16" r="3"/><circle cx="8" cy="25" r="3"/><path d="M11 8h7l3 5M21 19l-10 4M11 25h7"/></svg>',
    cart:'<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M4 6h4l3 15h13l4-11H9M13 27a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0m13 0a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0"/></svg>',
    asset:'<svg viewBox="0 0 32 32" aria-hidden="true"><rect x="7" y="4" width="18" height="24" rx="2"/><path d="M12 9h8M12 14h8M12 19h3m4 0h1M12 24h8"/></svg>'
  };
  app.innerHTML=`
    <section class="home-hero home-hero-focus">
      <div class="home-hero-copy">
        <div class="eyebrow"><span class="eyebrow-dot"></span> EXPERIÊNCIA DE PROCESSOS</div>
        <h1>Entenda a indústria.<br><span>Enxergue o processo.</span></h1>
        <p>Uma experiência visual para percorrer os processos documentados do iLabPharma, do contexto inicial às etapas finais.</p>
        <div class="home-actions">
          <button class="primary-btn home-cta" onclick="document.body.classList.remove('home-mode');renderJourney(0)">Começar a jornada <span>→</span></button>
        </div>
      </div>
      <div class="hero-orbit hero-orbit-modules" aria-label="Módulos do sistema">
        <div class="orbit-connection connection-v"></div><div class="orbit-connection connection-h"></div>
        <div class="orbit-ring ring-a"></div><div class="orbit-ring ring-b"></div><div class="orbit-ring ring-c"></div>
        <div class="orbit-core"><span>i</span><strong>LAB</strong><small>PHARMA</small></div>
        ${modules.map(m=>`<div class="orbit-module ${m.cls}"><div class="module-icon">${icons[m.icon]}</div><div class="module-copy"><b>${m.title}</b><span>${m.desc}</span></div></div>`).join('')}
      </div>
    </section>`;
}
renderHome();