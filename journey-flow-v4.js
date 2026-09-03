(function(){
  function renderStageFlowV4(stageIndex=journeyIndex){
    const idx=Math.max(0,Math.min(stageIndex,journeyStages.length-1));
    if(idx!==0){ renderJourney(idx); return; }
    journeyIndex=0; journeySelected=0;
    if(typeof closeGeneralFlow==='function') closeGeneralFlow();
    document.body.classList.remove('home-mode','journey-intro-mode','journey-stage1-mode');
    document.body.classList.add('journey-mode','journey-flow-mode','principal-flow-only-mode');
    setCrumbs('Jornada','Indústria · Fluxo');
    document.querySelectorAll('.nav-item').forEach(x=>x.classList.remove('active'));
    const items=(journeyStages[0].purposes||journeyStages[0].items).filter(item=>item.name!=='Gestão Documental');
    app.innerHTML=`
    <section class="principal-flow-v4-screen">
      <header class="principal-flow-v4-header">
        <button class="principal-flow-v4-brand" onclick="renderHome()" aria-label="Voltar para Home"><img src="assets/ilabpharma-logo.svg" alt="iLabPharma"></button>
        <div class="principal-flow-v4-header-title"><strong>Como os módulos utilizam os cadastros?</strong><span>Uma visão resumida do fluxo do Módulo Principal.</span></div>
        <div class="principal-flow-v4-actions"><button onclick="renderHome()" aria-label="Voltar para Home" title="Voltar para Home">⌂</button></div>
      </header>
      <div class="principal-flow-v4-layout">
        <aside class="principal-flow-v4-sidebar">
          <div class="flow-v4-side-title"><span>01</span><div><strong>Indústria</strong><small>Quem irá fabricar o medicamento?</small></div></div>
          <div class="flow-v4-side-label">NESTA ETAPA</div>
          <nav class="flow-v4-side-nav">
            ${items.map((item,i)=>`<button onclick="renderJourney(0,${i})"><span>${String(i+1).padStart(2,'0')}</span><strong>${item.name}</strong><em>›</em></button>`).join('')}
            <button class="flow-v4-side-nav-active"><span>◎</span><strong>Fluxo</strong><em>›</em></button>
          </nav>
          <div class="flow-v4-side-result"><span>AO FINAL DESTA ETAPA</span><strong>A indústria estará<br>estruturada no<br>iLabPharma.</strong></div>
        </aside>
        <main class="principal-flow-v4-main">
          <div class="principal-flow-v4-title"><span><i></i> FLUXO</span></div>
          <div class="principal-flow-v4-content">
            <section class="flow-v4-sequence" aria-label="Fluxo do Módulo Principal">
              <article class="flow-v4-step flow-v4-step-primary"><div class="flow-v4-step-label">01</div><div class="flow-v4-step-copy"><strong>Cadastro e Parametrização</strong><span>Módulo Principal</span><b>Central de Governança</b></div></article>
              <div class="flow-v4-arrow">↓</div>
              <article class="flow-v4-step"><div class="flow-v4-step-label">02</div><div class="flow-v4-step-copy"><strong>Validação e Controle</strong><span>Regras de negócio</span><span>Permissões e perfis</span><span>Audit Trail</span></div></article>
              <div class="flow-v4-arrow">↓</div>
              <article class="flow-v4-step flow-v4-result"><div class="flow-v4-step-label">03</div><div class="flow-v4-step-copy"><strong>Disponibilização de Dados Mestres</strong><span>Dados disponíveis para os módulos</span></div></article>
            </section>
            <section class="flow-v4-impact-grid" aria-label="Benefícios e riscos">
              <article class="flow-v4-impact flow-v4-benefits"><header><span>✓</span><strong>Benefícios</strong></header><ul><li>Processos integrados e consistentes</li><li>Redução de retrabalho</li><li>Conformidade com ANVISA / BPF</li><li>Melhor rastreabilidade</li><li>Segurança da informação</li><li>Governança de acessos</li></ul></article>
              <article class="flow-v4-impact flow-v4-risks"><header><span>!</span><strong>Riscos sem os cadastros</strong></header><ul><li>Impossibilidade de executar processos dependentes</li><li>Dados inconsistentes</li><li>Falhas na rastreabilidade</li><li>Não conformidades regulatórias</li><li>Atrasos na produção e liberação</li></ul><blockquote>Sem os cadastros e parâmetros necessários, os processos dependentes não podem ser executados corretamente.</blockquote></article>
            </section>
          </div>
          <div class="principal-flow-v4-bottom"><button class="flow-v4-ghost" onclick="renderJourney(0)">← Voltar para Indústria</button><div><span>VOCÊ ESTÁ AQUI</span><strong>01 · Indústria · Fluxo</strong></div><button class="flow-v4-primary" onclick="renderJourney(1)">Continuar →</button></div>
        </main>
      </div>
    </section>`;
  }
  window.renderStageFlow=renderStageFlowV4;
})();
