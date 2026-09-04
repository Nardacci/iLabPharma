(function(){
  const originalRenderJourney=window.renderJourney;
  if(typeof originalRenderJourney!=='function') return;
  window.renderJourney=function(index=0,selected=0){
    if(index!==0){ originalRenderJourney(index,selected); return; }
    const s=journeyStages[0];
    journeyIndex=0;
    const items=(s.purposes||s.items).filter(item=>item.name!=='Gestão Documental');
    journeySelected=0;
    closeGeneralFlow();
    document.body.classList.remove('home-mode','journey-intro-mode');
    document.body.classList.add('journey-mode','journey-stage1-mode');
    setCrumbs('Jornada','Indústria');
    document.querySelectorAll('.nav-item').forEach(x=>x.classList.remove('active'));
    app.innerHTML=`
      <section class="stage1-screen">
        <header class="stage1-header">
          <div class="stage1-header-context">
            <button class="stage1-brand" onclick="renderHome()" aria-label="Voltar para Home"><img src="assets/ilabpharma-logo.svg" alt="iLabPharma"></button>
            <div class="stage1-page-title"><strong>Antes de produzir, a indústria precisa <em>existir.</em></strong><span>A operação começa pela definição da organização, das pessoas que participam dos processos e dos níveis de acesso necessários para executar e controlar as atividades.</span></div>
          </div>
          <div class="stage1-actions"><button class="stage1-home-btn" onclick="renderHome()" aria-label="Voltar para Home" title="Voltar para Home">⌂</button></div>
        </header>
        <div class="stage1-layout">
          <aside class="stage1-sidebar">
            <div class="stage1-side-title"><span>01</span><div><strong>Indústria</strong><small>Quem irá fabricar o medicamento?</small></div></div>
            <nav class="stage1-items" aria-label="Elementos da Indústria">
              ${items.map((item,i)=>`<button class="stage1-item ${i===0?'selected':''}" type="button" aria-label="${item.name}"><span>${String(i+1).padStart(2,'0')}</span><strong>${item.name}</strong></button>`).join('')}
              <button class="stage1-item stage1-flow-item" type="button" onclick="renderIndustryFlowList"><span>◎</span><strong>Fluxo</strong><em>›</em></button>
            </nav>
            <div class="stage1-side-result"><span>AO FINAL DESTA ETAPA</span><strong>A indústria estará<br>estruturada no<br>iLabPharma.</strong></div>
          </aside>
          <main class="stage1-main">
            <div class="stage1-questions"><span class="stage1-section-label">AS PERGUNTAS QUE ESTRUTURAM ESTA ETAPA</span><div class="stage1-question-grid"><button type="button"><b>01</b><strong>Quem participa da operação?</strong><span>Profissionais e funções</span></button><button type="button"><b>02</b><strong>Quem pode acessar o sistema?</strong><span>Contas, perfis e permissões</span></button><button type="button"><b>03</b><strong>Como a empresa se organiza?</strong><span>Pessoa jurídica e estrutura</span></button></div></div>
            <div class="stage1-bottom"><button class="ghost-btn" onclick="renderJourneyIntro()">← Voltar</button><div><span>Você está aqui</span><strong>Indústria</strong></div><button class="primary-btn" onclick="renderJourney(1)">Continuar →</button></div>
          </main>
        </div>
      </section>`;
    app.querySelector('.stage1-flow-item').onclick=()=>renderIndustryFlowList();
  };
  if(!document.querySelector('script[data-flow-experience]')){
    const flowScript=document.createElement('script');
    flowScript.dataset.flowExperience='true';
    flowScript.src='journey-flow-experience.js?v=1.0.2';
    document.head.appendChild(flowScript);
  }
  if(!document.querySelector('link[data-flow-v2]')){
    const flowCss=document.createElement('link');
    flowCss.rel='stylesheet';
    flowCss.dataset.flowV2='true';
    flowCss.href='journey-flow-v2.css?v=1.0.0';
    document.head.appendChild(flowCss);
  }
})();