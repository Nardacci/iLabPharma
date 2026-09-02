function renderStageFlow(stageIndex=journeyIndex){
  const idx=Math.max(0,Math.min(stageIndex,journeyStages.length-1));
  const current=journeyStages[idx];
  journeyIndex=idx;
  journeySelected=0;
  closeGeneralFlow();
  document.body.classList.remove('home-mode','journey-intro-mode','journey-stage1-mode');
  document.body.classList.add('journey-mode','journey-flow-mode');
  setCrumbs('Jornada','Indústria · Fluxo');
  document.querySelectorAll('.nav-item').forEach(x=>x.classList.remove('active'));

  const groups=[
    {id:'cad',num:'01',title:'Cadastro e Parametrização',sub:'A base estrutural do iLabPharma',color:'blue',items:[
      {title:'Organização e Empresas',desc:'Pessoa Jurídica · Estrutura Organizacional · Centro de Custo · Conta Contábil / Gerencial'},
      {title:'Usuários e Perfis',desc:'Profissional · Conta de Usuário · Perfil / Grupo de Usuários · Funções Profissionais'},
      {title:'Estrutura Física e Recursos',desc:'Ambientes / Local Físico · Equipamentos · Instrumentos / Utensílios · Pontos de Água / Utilidades'},
      {title:'Tabelas e Parâmetros',desc:'Grau de Contaminação · Configurações de Notificação · Microservices · Notificações do Sistema'}
    ]},
    {id:'control',num:'02',title:'Validação e Controle',sub:'Regras e controles que sustentam a operação',color:'violet',items:[
      {title:'Regras de negócio',desc:'Elementos de validação e parametrização que sustentam os processos dependentes.'},
      {title:'Permissões e perfis',desc:'Controles associados aos usuários, perfis e níveis de acesso.'},
      {title:'Audit Trail',desc:'Elemento de controle apresentado na visão do Módulo Principal.'}
    ]},
    {id:'master',num:'03',title:'Disponibilização de Dados Mestres',sub:'Dados estruturados para os módulos dependentes',color:'cyan',items:[
      {title:'Dados mestres',desc:'A base cadastral estruturada pelo Módulo Principal fica disponível como fundamento para os processos que dependem dela.'}
    ]}
  ];

  app.innerHTML=`
    <section class="journey-flow-screen principal-flow-screen">
      <header class="journey-flow-header">
        <button class="journey-flow-brand" onclick="renderHome()" aria-label="Voltar para Home"><img src="assets/ilabpharma-logo.svg" alt="iLabPharma"></button>
        <div class="journey-flow-actions"><button class="journey-flow-home" onclick="renderHome()" aria-label="Voltar para Home">⌂</button><button class="journey-flow-login" onclick="renderPlaceholder('Acesso')"><span>♙</span> Entrar</button></div>
      </header>
      <div class="journey-flow-layout">
        <aside class="journey-flow-sidebar">
          <div class="journey-flow-side-title"><span>01</span><div><strong>Indústria</strong><small>Visão do processo</small></div></div>
          <div class="journey-flow-side-label">NESTA ETAPA</div>
          <nav class="journey-flow-side-nav">
            ${['Profissionais','Contas de Usuários','Perfis e Permissões','Pessoa Jurídica','Estrutura Organizacional'].map((x,i)=>`<button onclick="renderJourney(0,${i})"><span>${String(i+1).padStart(2,'0')}</span>${x}<em>›</em></button>`).join('')}
            <button class="is-flow"><span>◎</span>Fluxo<em>›</em></button>
          </nav>
          <div class="journey-flow-side-note"><span>FOCO</span><strong>Módulo Principal<br>como base da operação.</strong></div>
        </aside>
        <main class="journey-flow-main principal-flow-main">
          <div class="journey-flow-title-row">
            <div><span class="journey-flow-kicker"><i></i> FLUXO DO MÓDULO PRINCIPAL</span><h1>Como os dados estruturam a operação?</h1><p>Explore a base cadastral, os controles e a disponibilização dos dados que sustentam os processos dependentes.</p></div>
            <div class="journey-flow-legend"><span><i class="start"></i>Base</span><span><i class="end"></i>Dependência</span><span><b>→</b> Evolução</span></div>
          </div>
          <section class="principal-flow-canvas">
            <div class="principal-flow-instruction"><span>EXPLORE O FLUXO</span><strong>Clique em uma etapa para revelar seus elementos.</strong></div>
            <div class="principal-flow-stage-grid">
              ${groups.map((g,gi)=>`<button class="principal-flow-stage ${gi===0?'active':''}" data-stage="${g.id}" onclick="window.selectPrincipalFlowStage('${g.id}')"><span>${g.num}</span><div><strong>${g.title}</strong><small>${g.sub}</small></div><em>+</em></button>`).join('')}
            </div>
            <div class="principal-flow-detail" id="principal-flow-detail">
              <div class="principal-flow-detail-head"><span>01</span><div><small>ETAPA SELECIONADA</small><h2>Cadastro e Parametrização</h2></div></div>
              <div class="principal-flow-detail-grid">
                ${groups[0].items.map((it,i)=>`<button onclick="window.showPrincipalFlowDetail(${i})"><span>${String(i+1).padStart(2,'0')}</span><strong>${it.title}</strong><small>${it.desc}</small><em>+</em></button>`).join('')}
              </div>
              <div class="principal-flow-evidence" id="principal-flow-evidence"><span>VISÃO</span><strong>O Módulo Principal organiza a base cadastral e estrutural que sustenta a operação.</strong><p>Selecione um elemento acima para aprofundar.</p></div>
            </div>
            <div class="principal-flow-dependent">
              <span>PROCESSOS DEPENDENTES</span>
              <div><button>Produção</button><button>Estoque</button><button>Controle da Qualidade</button><button>Garantia da Qualidade</button><button>Controle de Documentos</button><button>Rastreabilidade</button></div>
            </div>
          </section>
          <div class="journey-flow-bottom">
            <button class="ghost-btn" onclick="renderJourney(0)">← Voltar para Indústria</button>
            <div><span>VOCÊ ESTÁ AQUI</span><strong>01 · Indústria · Fluxo</strong></div>
            <button class="primary-btn" onclick="renderJourney(1)">Continuar →</button>
          </div>
        </main>
      </div>
    </section>`;

  window.selectPrincipalFlowStage=function(id){
    const group=groups.find(g=>g.id===id); if(!group) return;
    document.querySelectorAll('.principal-flow-stage').forEach(b=>b.classList.toggle('active',b.dataset.stage===id));
    const detail=document.getElementById('principal-flow-detail');
    detail.innerHTML=`<div class="principal-flow-detail-head"><span>${group.num}</span><div><small>ETAPA SELECIONADA</small><h2>${group.title}</h2><p>${group.sub}</p></div></div><div class="principal-flow-detail-grid">${group.items.map((it,i)=>`<button onclick="window.showPrincipalFlowDetail(${i})"><span>${String(i+1).padStart(2,'0')}</span><strong>${it.title}</strong><small>${it.desc}</small><em>+</em></button>`).join('')}</div><div class="principal-flow-evidence" id="principal-flow-evidence"><span>VISÃO</span><strong>${group.title}.</strong><p>Selecione um elemento acima para aprofundar.</p></div>`;
  };
  window.showPrincipalFlowDetail=function(i){
    const active=document.querySelector('.principal-flow-stage.active'); if(!active) return;
    const group=groups.find(g=>g.id===active.dataset.stage); const item=group.items[i]; if(!item) return;
    const box=document.getElementById('principal-flow-evidence');
    box.innerHTML=`<span>DETALHE</span><strong>${item.title}</strong><p>${item.desc}</p><small>Fonte: visão do Módulo Principal</small>`;
    document.querySelectorAll('.principal-flow-detail-grid button').forEach((b,n)=>b.classList.toggle('selected',n===i));
  };
}
