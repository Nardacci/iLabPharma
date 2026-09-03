function renderStageFlow(stageIndex=journeyIndex){
  const idx=Math.max(0,Math.min(stageIndex,journeyStages.length-1));
  if(idx!==0){ renderJourney(idx); return; }
  journeyIndex=0; journeySelected=0;
  if(typeof closeGeneralFlow==='function') closeGeneralFlow();
  document.body.classList.remove('home-mode','journey-intro-mode','journey-stage1-mode');
  document.body.classList.add('journey-mode','journey-flow-mode','principal-flow-only-mode');
  setCrumbs('Jornada','Indústria · Fluxo');
  document.querySelectorAll('.nav-item').forEach(x=>x.classList.remove('active'));

  app.innerHTML=`
  <section class="principal-flow-only-screen">
    <header class="principal-flow-only-header">
      <button class="principal-flow-only-brand" onclick="renderHome()" aria-label="Voltar para Home"><img src="assets/ilabpharma-logo.svg" alt="iLabPharma"></button>
      <div class="principal-flow-only-actions">
        <button onclick="renderHome()" aria-label="Voltar para Home">⌂</button>
        <button onclick="renderPlaceholder('Acesso')">♙ Entrar</button>
      </div>
    </header>

    <main class="principal-flow-only-main">
      <div class="principal-flow-only-title">
        <span><i></i> FLUXO DO MÓDULO PRINCIPAL</span>
        <h1>Como os módulos utilizam os cadastros?</h1>
      </div>

      <div class="principal-flow-source-layout">
        <section class="principal-flow-source-left" aria-label="Fluxo do Módulo Principal">
          <div class="source-step source-step-blue">
            <div class="source-step-top">1. Cadastro e Parametrização</div>
            <div class="source-database" aria-hidden="true"><span></span><span></span><span></span></div>
            <div class="source-core-title">Módulo Principal</div>
            <div class="source-core-subtitle">Central de Governança</div>
          </div>

          <div class="source-arrow-down">▼</div>

          <div class="source-step source-step-light">
            <div class="source-step-top">2. Validação e Controle</div>
            <div class="source-controls">
              <div><b>⚙</b><span>Regras de negócio</span></div>
              <div><b>◆</b><span>Permissões e perfis</span></div>
              <div><b>▤</b><span>Audit Trail</span></div>
            </div>
          </div>

          <div class="source-arrow-down">▼</div>

          <div class="source-step source-step-light source-result">
            <div class="source-step-top">3. Disponibilização de Dados Mestres</div>
            <div class="source-result-content">
              <div class="source-database small" aria-hidden="true"><span></span><span></span><span></span></div>
              <strong>Dados disponíveis<br>para os módulos</strong>
            </div>
          </div>
        </section>

        <section class="principal-flow-source-right" aria-label="Como os módulos utilizam os cadastros">
          <div class="source-right-title">Como os módulos utilizam os cadastros?</div>
          <div class="source-module-list">
            <article><b class="module-icon purple">⚙</b><div><strong>Produção</strong><p>Ambientes, equipamentos, instrumentos, OPE, usuários, centros de custo.</p></div></article>
            <article><b class="module-icon orange">▣</b><div><strong>Estoque</strong><p>Locais físicos, fornecedores, pessoas jurídicas, itens, centros de custo.</p></div></article>
            <article><b class="module-icon green">♜</b><div><strong>Controle da Qualidade (CQ)</strong><p>Ambientes, instrumentos, profissionais, setores, usuários.</p></div></article>
            <article><b class="module-icon blue">▤</b><div><strong>Garantia da Qualidade (GQ)</strong><p>Profissionais, estrutura organizacional, documentos, treinamentos.</p></div></article>
            <article><b class="module-icon red">▤</b><div><strong>Controle de Documentos</strong><p>Estrutura organizacional, perfis, aprovadores, vigência.</p></div></article>
            <article><b class="module-icon purple">⌘</b><div><strong>Rastreabilidade</strong><p>Lotes, produtos, insumos, movimentações e eventos.</p></div></article>
          </div>
        </section>
      </div>
    </main>
  </section>

  <style>
    body.principal-flow-only-mode{overflow:hidden}
    body.principal-flow-only-mode .sidebar,body.principal-flow-only-mode .topbar{display:none}
    body.principal-flow-only-mode .app-shell{display:block;min-height:100vh;width:100%}
    body.principal-flow-only-mode .main-content{margin:0;width:100%;min-height:100vh}
    body.principal-flow-only-mode .content{padding:0;max-width:none;width:100%;min-height:100vh}
    .principal-flow-only-screen{min-height:100vh;width:100%;background:#071426;color:#fff;overflow:hidden;position:relative;font-family:inherit}
    .principal-flow-only-header{height:72px;padding:14px 42px;display:flex;align-items:center;justify-content:space-between;position:relative;z-index:3}
    .principal-flow-only-brand{background:none;border:0;padding:0;cursor:pointer}.principal-flow-only-brand img{width:156px;height:auto;display:block}
    .principal-flow-only-actions{display:flex;gap:10px}.principal-flow-only-actions button{border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.05);color:#fff;border-radius:8px;padding:9px 14px;font-weight:700;cursor:pointer}
    .principal-flow-only-main{width:min(1160px,94vw);margin:0 auto;padding:16px 0 42px}
    .principal-flow-only-title{margin-bottom:22px}.principal-flow-only-title span{font-size:11px;letter-spacing:1.8px;font-weight:800;color:#4db5ff}.principal-flow-only-title span i{display:inline-block;width:7px;height:7px;border-radius:50%;background:#ff8a24;margin-right:7px}.principal-flow-only-title h1{font-size:28px;margin:7px 0 0;font-weight:800}
    .principal-flow-source-layout{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(380px,.85fr);gap:22px;align-items:stretch}
    .principal-flow-source-left{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:650px;padding:8px 0}
    .source-step{width:min(620px,100%);border-radius:12px;box-sizing:border-box;text-align:center;position:relative;box-shadow:0 12px 35px rgba(0,0,0,.25)}
    .source-step-blue{height:238px;background:radial-gradient(circle at 50% 42%,#1265aa 0,#063a70 42%,#06294e 100%);border:1px solid rgba(69,176,255,.45);padding:0 30px}
    .source-step-light{background:linear-gradient(180deg,#f7fafc,#dce6ee);color:#12243b;border:1px solid rgba(255,255,255,.8);padding:0 24px}
    .source-step-top{font-size:15px;font-weight:800;padding:11px 14px;border-radius:0 0 8px 8px;letter-spacing:.1px}.source-step-blue .source-step-top{background:#0875cf;color:#fff}.source-step-light .source-step-top{color:#16314d;background:rgba(255,255,255,.2)}
    .source-database{width:72px;height:68px;margin:17px auto 8px;position:relative}.source-database span{display:block;width:72px;height:23px;border:2px solid #72e6ff;border-radius:50%;position:absolute;left:0;background:linear-gradient(180deg,#35c9f5,#0b68ad);box-shadow:0 0 16px rgba(64,214,255,.45)}.source-database span:nth-child(1){top:0}.source-database span:nth-child(2){top:21px}.source-database span:nth-child(3){top:42px}.source-core-title{font-size:23px;font-weight:900;margin-top:3px}.source-core-subtitle{display:inline-block;margin-top:4px;background:#0b82df;border-radius:16px;padding:5px 25px;font-size:12px;font-weight:800}
    .source-arrow-down{height:28px;line-height:28px;color:#1b8de8;font-size:24px;text-shadow:0 0 10px rgba(27,141,232,.7)}
    .source-step-light.source-result{height:116px}.source-controls{display:grid;grid-template-columns:repeat(3,1fr);height:64px;margin:3px 0 0}.source-controls div{display:flex;flex-direction:column;justify-content:center;align-items:center;gap:4px;border-left:1px solid #b6c6d4;font-size:10px;font-weight:800}.source-controls div:first-child{border-left:0}.source-controls b{font-size:23px;color:#17395c}.source-result-content{display:flex;align-items:center;justify-content:center;gap:20px;height:58px}.source-database.small{transform:scale(.58);transform-origin:center;margin:0;width:72px;height:45px}.source-result-content strong{font-size:14px;text-align:left;color:#17395c}
    .principal-flow-source-right{background:linear-gradient(180deg,#f8fbfd,#e6edf3);border-radius:11px;color:#102946;overflow:hidden;border:1px solid rgba(255,255,255,.9);box-shadow:0 15px 38px rgba(0,0,0,.3)}
    .source-right-title{height:52px;background:#0a2746;color:#fff;display:flex;align-items:center;padding:0 18px;font-size:15px;font-weight:900}.source-module-list article{display:grid;grid-template-columns:40px 1fr;gap:10px;padding:9px 14px;border-bottom:1px solid #cad7e2;min-height:74px;box-sizing:border-box}.source-module-list article:last-child{border-bottom:0}.module-icon{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px;font-weight:900;margin-top:1px}.module-icon.purple{background:#6b42b7}.module-icon.orange{background:#f39a14}.module-icon.green{background:#21a875}.module-icon.blue{background:#2274bd}.module-icon.red{background:#d63d45}.source-module-list strong{font-size:13px;display:block;line-height:1.15;margin-bottom:4px}.source-module-list p{font-size:10.5px;line-height:1.3;margin:0;color:#31485e}
    @media(max-width:900px){body.principal-flow-only-mode{overflow:auto}.principal-flow-source-layout{grid-template-columns:1fr}.principal-flow-source-left{min-height:auto}.principal-flow-source-right{margin-bottom:30px}.principal-flow-only-header{padding:12px 20px}.principal-flow-only-main{padding-bottom:30px}.principal-flow-only-title h1{font-size:23px}}
    @media(max-width:600px){.principal-flow-only-header{height:62px;padding:10px 14px}.principal-flow-only-brand img{width:125px}.principal-flow-only-actions button{padding:7px 9px;font-size:11px}.principal-flow-source-left{padding:0 6px}.source-step-blue{height:220px}.source-step-top{font-size:12px}.source-core-title{font-size:19px}.principal-flow-only-title{padding:0 8px}.principal-flow-only-title h1{font-size:20px}.source-module-list article{min-height:auto;padding:8px 10px}.source-module-list p{font-size:10px}}
  </style>`;
}