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

  function imageFlowScreen(title,description,crumb,imageSrc,imageAlt){
    setFlowMode();
    setCrumbs('Jornada',crumb);
    app.innerHTML=`<section class="principal-flow-v4-screen principal-flow-image-screen">${flowHeader(title,description)}<button class="principal-flow-close" onclick="renderIndustryFlowList()" aria-label="Fechar fluxo" title="Fechar fluxo">×</button><div style="position:absolute;inset:70px 0 0;display:flex;align-items:center;justify-content:center;padding:8px 24px 18px;box-sizing:border-box;background:#fff"><img src="${imageSrc}" alt="${imageAlt}" style="width:100%;height:100%;object-fit:contain;display:block"></div></section>`;
  }

  function renderIndustryFlowList(){
    setFlowMode();
    setCrumbs('Jornada','Indústria · Fluxos');
    app.innerHTML=`<section class="principal-flow-v4-screen">${flowHeader('Fluxos da Indústria','Processos representados para a etapa de Indústria.')}<div class="principal-flow-v4-layout">${sideBar()}<main class="principal-flow-v4-main principal-flow-list-main"><div class="principal-flow-v4-title"><span><i></i> FLUXOS DA INDÚSTRIA</span></div><div class="principal-flow-list"><button class="principal-flow-list-card" onclick="renderIndustryPrincipalFlow()"><span class="principal-flow-list-number">01</span><div><strong>Módulo Principal</strong><p>Como os módulos utilizam os cadastros do Módulo Principal.</p></div><em>›</em></button><button class="principal-flow-list-card" onclick="renderIndustryArchitectureFlow()"><span class="principal-flow-list-number">02</span><div><strong>Arquitetura funcional</strong><p>Visão funcional do Módulo Principal e sua relação com os demais módulos.</p></div><em>›</em></button></div><div class="principal-flow-v4-bottom"><button class="flow-v4-ghost" onclick="renderJourney(0)">← Voltar para Indústria</button><div><span>VOCÊ ESTÁ AQUI</span><strong>01 · Indústria · Fluxos</strong></div><button class="flow-v4-primary" onclick="renderJourney(1)">Continuar →</button></div></main></div></section>`;
  }

  function renderIndustryPrincipalFlow(){
    imageFlowScreen('Módulo Principal','Como os módulos utilizam os cadastros do Módulo Principal.','Indústria · Fluxo do Módulo Principal','assets/fluxo-modulo-principal.svg?v=3.0.0','Fluxo do Módulo Principal');
  }

  function renderIndustryArchitectureFlow(){
    imageFlowScreen('Arquitetura funcional','Visão funcional do Módulo Principal e sua relação com os demais módulos.','Indústria · Arquitetura funcional','assets/arquitetura-funcional.svg?v=3.0.0','Arquitetura funcional do iLabPharma');
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
