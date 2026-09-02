function renderHome(){
  document.body.classList.remove('journey-mode');
  document.body.classList.add('home-mode');
  setCrumbs('iLabPharma','');
  const modules=[
    {title:'PRODUÇÃO',desc:'Processo produtivo',cls:'module-1',icon:'gear'},
    {title:'CQ',desc:'Controle da qualidade',cls:'module-2',icon:'flask'},
    {title:'GQ',desc:'Garantia da qualidade',cls:'module-3',icon:'shield'},
    {title:'DOCUMENTOS',desc:'Controle documental',cls:'module-4',icon:'document'},
    {title:'RASTREABILIDADE',desc:'Relação entre processos',cls:'module-5',icon:'trace'},
    {title:'COMERCIAL',desc:'Processos comerciais',cls:'module-6',icon:'cart'},
    {title:'ESTOQUE',desc:'Materiais e movimentações',cls:'module-7',icon:'box'},
    {title:'PATRIMÔNIO',desc:'Gestão de ativos',cls:'module-8',icon:'asset'}
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
    <section class="home-screen">
      <header class="home-header">
        <button class="home-brand" onclick="renderHome()" aria-label="Página inicial">
          <img src="assets/ilabpharma-logo.svg" alt="iLabPharma">
          <span>INTELIGÊNCIA APLICADA</span>
        </button>
        <nav class="home-nav" aria-label="Navegação principal">
          <button onclick="renderJourney(0)">JORNADA</button>
          <button onclick="renderProcessList()">PROCESSOS</button>
          <button onclick="renderProcessList()">MÓDULOS</button>
          <button onclick="renderPlaceholder('Sobre o Projeto')">SOBRE O PROJETO</button>
        </nav>
        <button class="home-login" onclick="renderPlaceholder('Acesso')"><span>♙</span> Entrar</button>
      </header>

      <div class="home-main">
        <div class="home-copy">
          <div class="home-kicker"><span></span> ILABPHARMA</div>
          <h1>Inteligência aplicada<br>à gestão da <em>produção<br>laboratorial de<br>medicamentos e vacinas.</em></h1>
          <p>Uma visão conectada dos processos, da qualidade e da produção para uma operação mais inteligente, segura e eficiente.</p>
          <button class="home-cta" onclick="renderJourney(0)"><strong>▶</strong><span>Iniciar jornada</span><b>→</b></button>
          <div class="home-values">
            <div><strong>Especialização</strong><span>para a indústria farmacêutica</span></div>
            <div><strong>Processos</strong><span>integrados e conectados</span></div>
            <div><strong>Visão</strong><span>do processo ao todo</span></div>
          </div>
        </div>

        <div class="home-orbit" aria-label="Ecossistema de módulos">
          <div class="orbit-glow"></div>
          <div class="orbit-ring ring-outer"></div><div class="orbit-ring ring-middle"></div><div class="orbit-ring ring-inner"></div>
          <div class="orbit-cross cross-v"></div><div class="orbit-cross cross-h"></div>
          <div class="orbit-core"><img src="assets/ilabpharma-logo.svg" alt="iLabPharma"></div>
          ${modules.map(m=>`<div class="orbit-module ${m.cls}"><div class="module-icon">${icons[m.icon]}</div><div class="module-copy"><b>${m.title}</b><span>${m.desc}</span></div></div>`).join('')}
        </div>
      </div>

      <div class="home-scroll"><span class="mouse"></span><span>Role para explorar</span><b>⌄</b></div>
    </section>`;
}
renderHome();