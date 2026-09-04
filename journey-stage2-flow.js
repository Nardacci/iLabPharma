(function(){
  function injectStyle(){
    if(document.getElementById('stage2-flow-style'))return;
    const style=document.createElement('style');
    style.id='stage2-flow-style';
    style.textContent=`
      body.journey-stage2-flow-list-mode{overflow:hidden;background:#02080e}
      body.journey-stage2-flow-list-mode .sidebar,body.journey-stage2-flow-list-mode .topbar{display:none}
      body.journey-stage2-flow-list-mode .app-shell{display:block;min-height:100vh}
      body.journey-stage2-flow-list-mode .main-content{margin:0;width:100%;min-height:100vh}
      body.journey-stage2-flow-list-mode .content{padding:0;max-width:none;width:100%;min-height:100vh}
      .stage2-flow-screen{min-height:100vh;width:100%;box-sizing:border-box;background:radial-gradient(circle at 78% 42%,rgba(11,50,72,.25),transparent 34%),linear-gradient(135deg,#02080e,#061725 62%,#071d2c);color:#fff;padding:0 40px;font-family:inherit}
      .stage2-flow-layout{height:100vh;max-width:1400px;margin:0 auto;display:grid;grid-template-columns:253px minmax(0,1fr);gap:28px;box-sizing:border-box}
      .stage2-flow-sidebar{height:100%;min-height:0;border:1px solid rgba(91,143,177,.28);border-radius:15px;background:linear-gradient(180deg,rgba(5,19,30,.94),rgba(3,13,21,.94));padding:14px 12px 12px;display:flex;flex-direction:column;box-sizing:border-box;overflow:hidden}
      .stage2-flow-side-title{display:flex;align-items:center;gap:9px;padding:1px 5px 13px;border-bottom:1px solid rgba(104,139,157,.14);margin-bottom:10px}
      .stage2-flow-side-title>span{width:27px;height:27px;border:1px solid rgba(255,133,0,.7);border-radius:50%;display:grid;place-items:center;background:rgba(255,133,0,.08);color:#ff8500;font:800 9px Inter}
      .stage2-flow-side-title strong{display:block;font:800 15px Manrope}.stage2-flow-side-title small{display:block;margin-top:3px;font:500 7px Inter;color:#8ea1ac}
      .stage2-flow-side-label{color:#718896;font:800 7px Inter;letter-spacing:1.5px;margin:0 5px 8px}
      .stage2-flow-side-nav{display:flex;flex-direction:column;gap:6px}
      .stage2-flow-side-nav button{width:100%;min-height:34px;border:1px solid rgba(105,141,159,.2);border-radius:9px;background:rgba(8,28,42,.7);color:#dce5ea;display:flex;align-items:center;padding:0 9px;cursor:pointer;text-align:left;box-sizing:border-box}
      .stage2-flow-side-nav button:hover,.stage2-flow-side-nav .active{background:rgba(255,133,0,.08);border-color:rgba(255,133,0,.55)}
      .stage2-flow-side-nav button span{width:23px;color:#718b99;font:800 7px Inter}.stage2-flow-side-nav button strong{flex:1;font:600 9px Inter}.stage2-flow-side-nav button em{font-style:normal;color:#ff8500;font-size:14px}
      .stage2-flow-side-nav .active span{font-size:12px!important;color:#ff8500!important}
      .stage2-flow-side-result{margin-top:auto;border:1px solid rgba(255,133,0,.28);border-radius:11px;padding:11px 9px;text-align:center;background:rgba(255,133,0,.045)}
      .stage2-flow-side-result span{display:block;font:800 6px Inter;letter-spacing:1.2px;color:#8499a5;margin-bottom:5px}.stage2-flow-side-result strong{font:700 9px/1.4 Inter;color:#dce6eb}
      .stage2-flow-main{min-width:0;min-height:0;height:100%;display:flex;flex-direction:column;box-sizing:border-box;padding:0;overflow:hidden}
      .stage2-flow-header{height:70px;flex:0 0 70px;border-bottom:1px solid rgba(91,143,177,.13);display:flex;align-items:center;gap:18px;box-sizing:border-box}
      .stage2-flow-brand{background:transparent;border:0;padding:0;cursor:pointer;flex:0 0 auto}.stage2-flow-brand img{width:175px;height:auto;max-height:40px;display:block}
      .stage2-flow-header-divider{width:1px;height:36px;background:rgba(150,170,181,.24);flex:0 0 1px}
      .stage2-flow-header-title{min-width:0;display:flex;flex-direction:column;justify-content:center;gap:3px}.stage2-flow-header-title strong{font:800 16px/1.15 Manrope;color:#fff}.stage2-flow-header-title span{font:500 8px/1.25 Inter;color:#9db0bb}
      .stage2-flow-header-actions{margin-left:auto}.stage2-flow-header-actions button{width:38px;height:38px;border:1px solid rgba(150,170,181,.35);border-radius:50%;background:rgba(4,17,27,.55);color:#fff;cursor:pointer;font-size:16px}
      .stage2-flow-header-actions button:hover{border-color:#ff8500;color:#ff8500}
      .stage2-flow-title{flex:0 0 auto;margin:28px 0 18px;padding:0 0 0 0}.stage2-flow-title span{font:800 8px Inter;letter-spacing:1.7px;color:#4db5ff}.stage2-flow-title span i{display:inline-block;width:6px;height:6px;border-radius:50%;background:#ff8a24;margin-right:6px}
      .stage2-flow-cards{flex:1;min-height:0;display:flex;flex-direction:column;gap:12px;overflow:hidden;padding-bottom:8px}
      .stage2-flow-card{min-height:0;border:1px solid rgba(91,143,177,.3);border-radius:13px;background:linear-gradient(145deg,rgba(8,27,40,.96),rgba(4,16,25,.96));display:grid;grid-template-columns:52px minmax(0,1fr) auto;gap:14px;align-items:center;padding:15px 18px;box-sizing:border-box;box-shadow:0 10px 25px rgba(0,0,0,.16)}
      .stage2-flow-card:hover{border-color:rgba(255,133,0,.42)}
      .stage2-flow-card-num{width:36px;height:36px;border:1px solid rgba(255,133,0,.7);border-radius:50%;display:grid;place-items:center;color:#ff8500;font:800 9px Inter;background:rgba(255,133,0,.06)}
      .stage2-flow-card-copy{min-width:0}.stage2-flow-card-copy .eyebrow{font:800 7px Inter;letter-spacing:1.5px;color:#718896;margin-bottom:5px}.stage2-flow-card-copy h2{font:800 17px Manrope;margin:0 0 4px;color:#fff}.stage2-flow-card-copy p{margin:0;color:#9db0bb;font:500 9px/1.35 Inter}
      .stage2-flow-open{min-width:126px;height:38px;border:1px solid #ff8500;border-radius:22px;background:#ff8500;color:#08131b;font:800 9px Inter;cursor:pointer;padding:0 16px;text-decoration:none;display:inline-flex;align-items:center;justify-content:center}.stage2-flow-open:hover{filter:brightness(1.08)}
      .stage2-flow-bottom{height:40px;flex:0 0 40px;margin-top:7px;padding-top:6px;border-top:1px solid rgba(104,139,157,.12);display:grid;grid-template-columns:1fr auto 1fr;align-items:center}
      .stage2-flow-bottom>div{text-align:center}.stage2-flow-bottom>div span{display:block;font:700 6px Inter;letter-spacing:1px;color:#687f8c;text-transform:uppercase}.stage2-flow-bottom>div strong{font:800 9px Inter;color:#fff}
      .stage2-flow-ghost,.stage2-flow-primary{height:30px;padding:0 13px;border-radius:17px;cursor:pointer;font:700 9px Inter}.stage2-flow-ghost{justify-self:start;border:1px solid rgba(150,170,181,.3);background:transparent;color:#aebdc6}.stage2-flow-primary{justify-self:end;border:1px solid #ff8500;background:#ff8500;color:#fff}
      @media(max-width:900px){.stage2-flow-screen{padding:0 20px}.stage2-flow-layout{grid-template-columns:220px 1fr;gap:18px}.stage2-flow-card{grid-template-columns:42px minmax(0,1fr) auto}.stage2-flow-open{min-width:110px}}
      @media(max-width:700px){body.journey-stage2-flow-list-mode{overflow:auto}.stage2-flow-screen{padding:0 14px}.stage2-flow-layout{height:auto;min-height:100vh;grid-template-columns:1fr;gap:0}.stage2-flow-sidebar{height:auto;min-height:0;margin:12px 0}.stage2-flow-main{height:auto;min-height:0;overflow:visible}.stage2-flow-header{height:62px;flex-basis:62px}.stage2-flow-brand img{width:155px}.stage2-flow-header-title strong{font-size:12px}.stage2-flow-header-title span{font-size:7px}.stage2-flow-title{margin-top:20px}.stage2-flow-cards{overflow:visible}.stage2-flow-card{grid-template-columns:40px 1fr;gap:10px;padding:14px}.stage2-flow-open{grid-column:2;width:100%;margin-top:4px}.stage2-flow-bottom{margin-bottom:15px}}
    `;
    document.head.appendChild(style);
  }

  window.renderStage2FlowList=function(){
    injectStyle();
    journeyIndex=1;journeySelected=-1;
    if(typeof closeGeneralFlow==='function')closeGeneralFlow();
    document.body.classList.remove('home-mode','journey-intro-mode','journey-stage1-mode','journey-stage-2-mode','journey-stage2-flow-viewer-mode');
    document.body.classList.add('journey-mode','journey-stage2-flow-list-mode');
    setCrumbs('Jornada','Fábrica · Fluxos');
    document.querySelectorAll('.nav-item').forEach(x=>x.classList.remove('active'));

    app.innerHTML=`<section class="stage2-flow-screen">
      <div class="stage2-flow-layout">
        <aside class="stage2-flow-sidebar">
          <div class="stage2-flow-side-title"><span>02</span><div><strong>Fábrica</strong><small>O que precisa estar estruturado?</small></div></div>
          <div class="stage2-flow-side-label">NESTA ETAPA</div>
          <nav class="stage2-flow-side-nav">
            <button type="button" onclick="renderJourney(1,0)"><span>01</span><strong>Almoxarifados</strong><em>›</em></button>
            <button type="button" onclick="renderJourney(1,1)"><span>02</span><strong>Setores / Salas</strong><em>›</em></button>
            <button type="button" onclick="renderJourney(1,2)"><span>03</span><strong>Equipamentos</strong><em>›</em></button>
            <button type="button" onclick="renderJourney(1,3)"><span>04</span><strong>Instrumentos</strong><em>›</em></button>
            <button type="button" onclick="renderJourney(1,4)"><span>05</span><strong>Linhas</strong><em>›</em></button>
            <button type="button" onclick="renderJourney(1,5)"><span>06</span><strong>Centro de Trabalhos</strong><em>›</em></button>
            <button type="button" onclick="renderJourney(1,6)"><span>07</span><strong>Localizações</strong><em>›</em></button>
            <button type="button" class="active"><span>✦</span><strong>Fluxos</strong><em>›</em></button>
          </nav>
          <div class="stage2-flow-side-result"><span>AO FINAL DESTA ETAPA</span><strong>A fábrica está estruturada para suportar a operação no iLabPharma.</strong></div>
        </aside>

        <main class="stage2-flow-main">
          <header class="stage2-flow-header">
            <button class="stage2-flow-brand" type="button" onclick="renderHome()"><img src="assets/ilabpharma-logo.svg" alt="iLabPharma"></button>
            <div class="stage2-flow-header-divider"></div>
            <div class="stage2-flow-header-title"><strong>Fluxos da Fábrica</strong><span>Processos representados para a etapa de Fábrica.</span></div>
            <div class="stage2-flow-header-actions"><button type="button" title="Início" onclick="renderHome()">⌂</button></div>
          </header>

          <div class="stage2-flow-title"><span><i></i> FLUXOS DA FÁBRICA</span></div>

          <section class="stage2-flow-cards">
            <article class="stage2-flow-card">
              <div class="stage2-flow-card-num">01</div>
              <div class="stage2-flow-card-copy"><div class="eyebrow">FLUXO 01</div><h2>Recebimento de Material</h2><p>Fluxo relacionado ao recebimento dos materiais na operação da fábrica.</p></div>
              <a class="stage2-flow-open" href="fluxo-recebimento-material.html" target="_blank" rel="noopener noreferrer">Abrir fluxo →</a>
            </article>
            <article class="stage2-flow-card">
              <div class="stage2-flow-card-num">02</div>
              <div class="stage2-flow-card-copy"><div class="eyebrow">FLUXO 02</div><h2>Estoque de Quarentena</h2><p>Fluxo relacionado à gestão dos materiais em quarentena.</p></div>
              <a class="stage2-flow-open" href="fluxo-estoque-quarentena.html" target="_blank" rel="noopener noreferrer">Abrir fluxo →</a>
            </article>
            <article class="stage2-flow-card">
              <div class="stage2-flow-card-num">03</div>
              <div class="stage2-flow-card-copy"><div class="eyebrow">FLUXO 03</div><h2>Estoque Quarentena Produção</h2><p>Fluxo relacionado à quarentena de materiais no contexto da produção.</p></div>
              <a class="stage2-flow-open" href="fluxo-estoque-quarentena-producao.html" target="_blank" rel="noopener noreferrer">Abrir fluxo →</a>
            </article>
          </section>

          <footer class="stage2-flow-bottom">
            <button class="stage2-flow-ghost" type="button" onclick="renderJourney(1,-1)">← Voltar para Fábrica</button>
            <div><span>VOCÊ ESTÁ AQUI</span><strong>02 · Fábrica · Fluxos</strong></div>
            <button class="stage2-flow-primary" type="button" onclick="renderJourney(2,-1)">Continuar →</button>
          </footer>
        </main>
      </div>
    </section>`;
  };
})();