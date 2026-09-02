(function(){
  const originalRenderJourney=window.renderJourney;
  if(typeof originalRenderJourney!=='function') return;
  window.renderJourney=function(index=0,selected=0){
    if(index!==0){ originalRenderJourney(index,selected); return; }
    const s=journeyStages[0];
    journeyIndex=0;
    const items=(s.purposes||s.items).filter(item=>item.name!=='Gestão Documental');
    journeySelected=Math.max(0,Math.min(selected,items.length-1));
    closeGeneralFlow();
    document.body.classList.remove('home-mode','journey-intro-mode');
    document.body.classList.add('journey-mode','journey-stage1-mode');
    setCrumbs('Jornada','Indústria');
    document.querySelectorAll('.nav-item').forEach(x=>x.classList.remove('active'));
    const selectedItem=items[journeySelected];
    app.innerHTML=`
      <section class="stage1-screen">
        <header class="stage1-header">
          <button class="stage1-brand" onclick="renderHome()" aria-label="Voltar para Home"><img src="assets/ilabpharma-logo.svg" alt="iLabPharma"></button>
          <div class="stage1-actions"><button class="stage1-home-btn" onclick="renderHome()" aria-label="Voltar para Home" title="Voltar para Home">⌂</button><button class="stage1-login" onclick="renderPlaceholder('Acesso')"><span>♙</span> Entrar</button></div>
        </header>
        <div class="stage1-layout">
          <aside class="stage1-sidebar">
            <div class="stage1-side-title"><span>01</span><div><strong>Indústria</strong><small>Quem irá fabricar o medicamento?</small></div></div>
            <nav class="stage1-items" aria-label="Elementos da Indústria">
              ${items.map((item,i)=>`<button class="stage1-item ${i===journeySelected?'selected':''}" onclick="renderJourney(0,${i})"><span>${String(i+1).padStart(2,'0')}</span><strong>${item.name}</strong><em>›</em></button>`).join('')}
              <button class="stage1-item stage1-flow-item" onclick="renderStageFlow(0)"><span>◎</span><strong>Fluxo</strong><em>›</em></button>
            </nav>
            <div class="stage1-side-result"><span>AO FINAL DESTA ETAPA</span><strong>A indústria estará<br>estruturada no<br>iLabPharma.</strong></div>
          </aside>
          <main class="stage1-main">
            <div class="stage1-context"><span class="stage1-kicker"><i></i> ESTRUTURA ANTES DA OPERAÇÃO</span><h2>Antes de produzir, a indústria precisa <em>existir.</em></h2><p>A operação começa pela definição da organização, das pessoas que participam dos processos e dos níveis de acesso necessários para executar e controlar as atividades.</p></div>
            <div class="stage1-detail"><div class="stage1-detail-top"><span class="stage1-detail-number">${String(journeySelected+1).padStart(2,'0')}</span><div><span class="stage1-section-label">ELEMENTO DA ESTRUTURA</span><h3>${selectedItem.name}</h3></div></div><p>${selectedItem.text}</p><div class="stage1-source"><span>FONTE</span><strong>${selectedItem.source}</strong></div></div>
            <div class="stage1-questions"><span class="stage1-section-label">AS PERGUNTAS QUE ESTRUTURAM ESTA ETAPA</span><div class="stage1-question-grid"><button onclick="renderJourney(0,0)"><b>01</b><strong>Quem participa da operação?</strong><span>Profissionais e funções</span></button><button onclick="renderJourney(0,2)"><b>02</b><strong>Quem pode acessar o sistema?</strong><span>Contas, perfis e permissões</span></button><button onclick="renderJourney(0,4)"><b>03</b><strong>Como a empresa se organiza?</strong><span>Pessoa jurídica e estrutura</span></button></div></div>
            <div class="stage1-bottom"><button class="ghost-btn" onclick="renderJourneyIntro()">← Voltar</button><div><span>Você está aqui</span><strong>Indústria</strong></div><button class="primary-btn" onclick="renderJourney(1)">Continuar →</button></div>
          </main>
        </div>
      </section>`;
  };
  if(!document.querySelector('script[data-flow-experience]')){
    const flowScript=document.createElement('script');
    flowScript.dataset.flowExperience='true';
    flowScript.src='journey-flow-experience.js?v=1.0.0';
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