function renderStageFlow(stageIndex=journeyIndex){
  const idx=Math.max(0,Math.min(stageIndex,journeyStages.length-1));
  if(idx!==0){ renderJourney(idx); return; }
  journeyIndex=0; journeySelected=0; closeGeneralFlow();
  document.body.classList.remove('home-mode','journey-intro-mode','journey-stage1-mode');
  document.body.classList.add('journey-mode','journey-flow-mode');
  setCrumbs('Jornada','Indústria · Fluxo');
  document.querySelectorAll('.nav-item').forEach(x=>x.classList.remove('active'));

  const groups=[
    {id:'cad',num:'01',title:'Cadastro e Parametrização',sub:'A base estrutural do iLabPharma',items:[
      {title:'Organização e Empresas',desc:'Pessoa Jurídica · Estrutura Organizacional · Centro de Custo · Conta Contábil / Gerencial'},
      {title:'Usuários e Perfis',desc:'Profissional · Conta de Usuário · Perfil / Grupo de Usuários · Funções Profissionais'},
      {title:'Estrutura Física e Recursos',desc:'Ambientes / Local Físico · Equipamentos · Instrumentos / Utensílios · Pontos de Água / Utilidades'},
      {title:'Tabelas e Parâmetros',desc:'Grau de Contaminação · Configurações de Notificação · Microservices · Notificações do Sistema'}
    ]},
    {id:'control',num:'02',title:'Validação e Controle',sub:'Controles apresentados na estrutura do módulo',items:[
      {title:'Regras de negócio',desc:'Elementos de validação e parametrização apresentados na visão do Módulo Principal.'},
      {title:'Permissões e perfis',desc:'Controles associados aos usuários, perfis e níveis de acesso apresentados no módulo.'},
      {title:'Audit Trail',desc:'Elemento de controle apresentado na visão do Módulo Principal.'}
    ]},
    {id:'master',num:'03',title:'Disponibilização de Dados Mestres',sub:'Dados estruturados para os módulos dependentes',items:[
      {title:'Dados mestres',desc:'A base cadastral estruturada pelo Módulo Principal é apresentada como fundamento para os processos dependentes.'}
    ]}
  ];

  const dependent=['Produção','Estoque','Controle da Qualidade','Garantia da Qualidade','Controle de Documentos','Rastreabilidade'];

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
            <div><span class="journey-flow-kicker"><i></i> FLUXO DO MÓDULO PRINCIPAL</span><h1>Como a base estrutura a operação?</h1><p>Explore, por etapas, o fluxo apresentado para o Módulo Principal.</p></div>
            <div class="journey-flow-legend"><span><i class="start"></i>Início</span><span><i class="end"></i>Resultado</span><span><b>→</b> Sequência</span></div>
          </div>

          <section class="principal-flow-canvas">
            <div class="principal-flow-intro">
              <div><span>FLUXO EXPLORÁVEL</span><h2>Comece pelo Módulo Principal</h2><p>O fluxo aparece conforme você explora cada etapa.</p></div>
              <div class="principal-flow-progress"><i class="active"></i><i></i><i></i><span>01 / 03</span></div>
            </div>
            <div class="principal-flow-core" id="principal-flow-core">
              <button class="principal-flow-core-node" onclick="window.revealPrincipalFlow('cad')"><span>01</span><strong>Módulo Principal</strong><small>Cadastro e parametrização</small><em>Explorar →</em></button>
              <div class="principal-flow-core-line"></div>
              <div class="principal-flow-hint">Clique para revelar a primeira etapa</div>
            </div>
            <div class="principal-flow-reveal" id="principal-flow-reveal" aria-live="polite"></div>
            <div class="principal-flow-dependent collapsed" id="principal-flow-dependent">
              <button class="dependent-toggle" onclick="window.togglePrincipalDependents()"><span>MÓDULOS DEPENDENTES</span><strong>Ver onde essa base é utilizada</strong><em>+</em></button>
              <div class="dependent-list">${dependent.map((x,i)=>`<span><b>${String(i+1).padStart(2,'0')}</b>${x}</span>`).join('')}</div>
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

  window.revealPrincipalFlow=function(id){
    const group=groups.find(g=>g.id===id); if(!group) return;
    const order=['cad','control','master']; const pos=order.indexOf(id);
    document.querySelector('.principal-flow-core').innerHTML=`<div class="principal-flow-expanded"><div class="expanded-head"><span>${group.num}</span><div><small>ETAPA REVELADA</small><h2>${group.title}</h2><p>${group.sub}</p></div></div><div class="expanded-path">${group.items.map((it,i)=>`<button onclick="window.showPrincipalFlowDetail('${id}',${i})"><span>${String(i+1).padStart(2,'0')}</span><strong>${it.title}</strong><small>${it.desc}</small><em>+</em></button>`).join('')}</div></div>`;
    document.getElementById('principal-flow-reveal').innerHTML=`<div class="principal-flow-next"><span>PRÓXIMA ETAPA</span><strong>${pos<2?groups[pos+1].title:'Dados disponíveis aos processos dependentes'}</strong><button onclick="${pos<2?`window.revealPrincipalFlow('${order[pos+1]}')`:'window.togglePrincipalDependents()'}">${pos<2?'Revelar →':'Explorar →'}</button></div>`;
    const dots=document.querySelectorAll('.principal-flow-progress i'); dots.forEach((d,i)=>d.classList.toggle('active',i<=pos));
  };
  window.showPrincipalFlowDetail=function(id,i){
    const group=groups.find(g=>g.id===id), item=group&&group.items[i]; if(!item) return;
    document.querySelectorAll('.expanded-path button').forEach((b,n)=>b.classList.toggle('selected',n===i));
    const box=document.getElementById('principal-flow-reveal');
    box.innerHTML=`<div class="principal-flow-evidence-card"><div><span>DETALHE DO FLUXO</span><h3>${item.title}</h3><p>${item.desc}</p></div><b>i</b></div>`;
  };
  window.togglePrincipalDependents=function(){
    const box=document.getElementById('principal-flow-dependent'); if(box) box.classList.toggle('collapsed');
  };
}