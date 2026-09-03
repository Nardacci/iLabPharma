(function(){
  const industryItems=()=> (journeyStages[0].purposes||journeyStages[0].items).filter(item=>item.name!=='Gestão Documental');

  function setFlowMode(){
    journeyIndex=0;
    journeySelected=0;
    if(typeof closeGeneralFlow==='function')closeGeneralFlow();
    document.body.classList.remove('home-mode','journey-intro-mode');
    document.body.classList.add('journey-mode','journey-flow-mode','principal-flow-only-mode','journey-stage1-mode');
    document.querySelectorAll('.nav-item').forEach(x=>x.classList.remove('active'));
  }

  function flowHeader(title,description){
    return `<header class="principal-flow-v4-header"><button class="principal-flow-v4-brand" onclick="renderHome()" aria-label="Voltar para Home"><img src="assets/ilabpharma-logo.svg" alt="iLabPharma"></button><div class="principal-flow-v4-header-divider"></div><div class="principal-flow-v4-header-title"><strong>${title}</strong><span>${description}</span></div><div class="principal-flow-v4-actions"><button onclick="renderHome()" aria-label="Voltar para Home" title="Voltar para Home">⌂</button></div></header>`;
  }

  function sideBar(){
    const items=industryItems();
    return `<aside class="principal-flow-v4-sidebar"><div class="flow-v4-side-title"><span>01</span><div><strong>Indústria</strong><small>Quem irá fabricar o medicamento?</small></div></div><div class="flow-v4-side-label">NESTA ETAPA</div><nav class="flow-v4-side-nav">${items.map((item,i)=>`<button onclick="renderJourney(0,${i})"><span>${String(i+1).padStart(2,'0')}</span><strong>${item.name}</strong><em>›</em></button>`).join('')}<button class="flow-v4-side-nav-active"><span>◎</span><strong>Fluxo</strong><em>›</em></button></nav><div class="flow-v4-side-result"><span>AO FINAL DESTA ETAPA</span><strong>A indústria estará<br>estruturada no<br>iLabPharma.</strong></div></aside>`;
  }

  function renderIndustryFlowList(){
    setFlowMode();
    setCrumbs('Jornada','Indústria · Fluxos');
    app.innerHTML=`<section class="principal-flow-v4-screen">${flowHeader('Fluxos da Indústria','Processos representados para a etapa de Indústria.')}<div class="principal-flow-v4-layout">${sideBar()}<main class="principal-flow-v4-main principal-flow-list-main"><div class="principal-flow-v4-title"><span><i></i> FLUXOS DA INDÚSTRIA</span></div><div class="principal-flow-list"><button class="principal-flow-list-card" onclick="window.open('fluxo-modulo-principal.html','_blank','noopener,noreferrer')"><span class="principal-flow-list-number">01</span><div><strong>Módulo Principal</strong><p>Como os módulos utilizam os cadastros do Módulo Principal.</p></div><em>›</em></button><button class="principal-flow-list-card" onclick="window.open('fluxo-arquitetura-funcional.html','_blank','noopener,noreferrer')"><span class="principal-flow-list-number">02</span><div><strong>Arquitetura funcional</strong><p>Visão funcional do Módulo Principal e sua relação com os demais módulos.</p></div><em>›</em></button></div><div class="principal-flow-v4-bottom"><button class="flow-v4-ghost" onclick="renderJourney(0)">← Voltar para Indústria</button><div><span>VOCÊ ESTÁ AQUI</span><strong>01 · Indústria · Fluxos</strong></div><button class="flow-v4-primary" onclick="renderJourney(1)">Continuar →</button></div></main></div></section>`;
  }

  function renderIndustryPrincipalFlow(){
    window.open('fluxo-modulo-principal.html','_blank','noopener,noreferrer');
  }

  function renderIndustryArchitectureFlow(){
    window.open('fluxo-arquitetura-funcional.html','_blank','noopener,noreferrer');
  }

  window.renderIndustryFlowList=renderIndustryFlowList;
  window.renderIndustryPrincipalFlow=renderIndustryPrincipalFlow;
  window.renderIndustryArchitectureFlow=renderIndustryArchitectureFlow;

  function renderStageFlowV4(stageIndex=journeyIndex){
    if(stageIndex!==0){renderJourney(stageIndex);return;}
    renderIndustryFlowList();
  }
  window.renderStageFlow=renderStageFlowV4;
})();
