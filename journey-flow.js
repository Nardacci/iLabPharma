function renderStageFlow(stageIndex=journeyIndex){
  const idx=Math.max(0,Math.min(stageIndex,journeyStages.length-1));
  const current=journeyStages[idx];
  journeyIndex=idx;
  journeySelected=0;
  closeGeneralFlow();
  document.body.classList.remove('home-mode','journey-intro-mode','journey-stage1-mode');
  document.body.classList.add('journey-mode','journey-flow-mode');
  setCrumbs('Jornada',current.title+' · Fluxo');
  document.querySelectorAll('.nav-item').forEach(x=>x.classList.remove('active'));

  const core=[
    {n:1,title:'Indústria',sub:'Estrutura da operação',key:0},
    {n:2,title:'Fábrica',sub:'Ambiente e recursos',key:1},
    {n:3,title:'Preparação',sub:'Condições antes da fabricação',key:2},
    {n:4,title:'Medicamento',sub:'Base para produção',key:3},
    {n:5,title:'Produção',sub:'Execução da fabricação',key:4},
    {n:6,title:'Controle da Qualidade',sub:'Avaliação do produto',key:5},
    {n:7,title:'Garantia da Qualidade',sub:'Decisão sobre o lote',key:6},
    {n:8,title:'Produto Acabado',sub:'Resultado da jornada',key:7}
  ];
  const support=[
    {n:'A',title:'Compras',sub:'Processo de apoio'},
    {n:'B',title:'Transporte',sub:'Processo de apoio'},
    {n:'C',title:'Pessoal',sub:'Processo de apoio'},
    {n:'D',title:'Expedição',sub:'Processo de apoio'}
  ];

  app.innerHTML=`
    <section class="journey-flow-screen">
      <header class="journey-flow-header">
        <button class="journey-flow-brand" onclick="renderHome()" aria-label="Voltar para Home"><img src="assets/ilabpharma-logo.svg" alt="iLabPharma"></button>
        <div class="journey-flow-actions"><button class="journey-flow-home" onclick="renderHome()" aria-label="Voltar para Home">⌂</button><button class="journey-flow-login" onclick="renderPlaceholder('Acesso')"><span>♙</span> Entrar</button></div>
      </header>
      <div class="journey-flow-layout">
        <aside class="journey-flow-sidebar">
          <div class="journey-flow-side-title"><span>01</span><div><strong>Indústria</strong><small>Visão do processo</small></div></div>
          <div class="journey-flow-side-label">NESTA ETAPA</div>
          <nav class="journey-flow-side-nav">
            ${['Profissionais','Contas de Usuários','Perfis e Permissões','Pessoa Jurídica','Estrutura Organizacional','Gestão Documental'].map((x,i)=>`<button onclick="renderJourney(0,${i})"><span>${String(i+1).padStart(2,'0')}</span>${x}<em>›</em></button>`).join('')}
            <button class="is-flow"><span>◎</span>Fluxo<em>›</em></button>
          </nav>
          <div class="journey-flow-side-note"><span>VISÃO</span><strong>Onde a Indústria<br>se conecta à jornada.</strong></div>
        </aside>
        <main class="journey-flow-main">
          <div class="journey-flow-title-row">
            <div><span class="journey-flow-kicker"><i></i> VISÃO DO PROCESSO</span><h1>Fluxo do Processo</h1><p>Uma visão resumida e conectada da jornada de produção de medicamentos.</p></div>
            <div class="journey-flow-legend"><span><i class="start"></i>Início</span><span><i class="end"></i>Fim</span><span><b>→</b> Fluxo principal</span><span><b class="dash">⇢</b> Relação</span></div>
          </div>

          <section class="journey-flow-map">
            <div class="journey-flow-map-head"><div><span>PROCESSO PRINCIPAL</span><strong>Da estrutura da indústria ao produto acabado</strong></div><small>01 · 08</small></div>
            <div class="journey-flow-core">
              <div class="flow-start-dot"></div>
              ${core.map((x,i)=>`${i?'<div class="flow-main-arrow">→</div>':''}<button class="flow-core-card ${x.key===idx?'current':''}" onclick="renderJourney(${x.key})"><span class="flow-card-number">${String(x.n).padStart(2,'0')}</span><strong>${x.title}</strong><small>${x.sub}</small></button>`).join('')}
              <div class="flow-end-dot"></div>
            </div>

            <div class="journey-flow-connector"><span>PROCESSOS DE APOIO</span></div>
            <div class="journey-flow-support">
              ${support.map((x,i)=>`<button class="flow-support-card" onclick="void(0)"><span>${x.n}</span><strong>${x.title}</strong><small>${x.sub}</small></button>`).join('')}
            </div>

            <div class="journey-flow-summary">
              <span>VISÃO RESUMIDA · END-TO-END</span>
              <div>${core.map((x,i)=>`${i?'<i>→</i>':''}<button onclick="renderJourney(${x.key})" class="${x.key===idx?'active':''}"><b>${String(x.n).padStart(2,'0')}</b><strong>${x.title}</strong></button>`).join('')}</div>
            </div>
          </section>

          <div class="journey-flow-bottom">
            <button class="ghost-btn" onclick="renderJourney(${idx})">← Voltar para ${current.title}</button>
            <div><span>VOCÊ ESTÁ AQUI</span><strong>01 · Indústria · Fluxo</strong></div>
            <button class="primary-btn" onclick="renderJourney(${idx===7?7:idx+1})">${idx===7?'Concluir jornada':'Continuar →'}</button>
          </div>
        </main>
      </div>
    </section>`;
}
