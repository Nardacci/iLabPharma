(function(){
  function injectStyle(){
    if(document.getElementById('stage2-flow-style'))return;
    const style=document.createElement('style');
    style.id='stage2-flow-style';
    style.textContent=`
      body.journey-stage2-flow-list-mode{overflow:auto;background:#02080e}
      body.journey-stage2-flow-list-mode .sidebar,body.journey-stage2-flow-list-mode .topbar{display:none}
      body.journey-stage2-flow-list-mode .app-shell{display:block;min-height:100vh}
      body.journey-stage2-flow-list-mode .main-content{margin:0;width:100%;min-height:100vh}
      body.journey-stage2-flow-list-mode .content{padding:0;max-width:none;width:100%;min-height:100vh}
      .stage2-flow-screen{min-height:100vh;width:100%;box-sizing:border-box;background:radial-gradient(circle at 75% 35%,rgba(11,50,72,.28),transparent 35%),linear-gradient(135deg,#02080e,#061725 62%,#071d2c);color:#fff;padding:42px 6vw 48px;font-family:inherit}
      .stage2-flow-head{max-width:1100px;margin:0 auto 34px}
      .stage2-flow-kicker{font:800 10px Inter;letter-spacing:2px;color:#4db5ff;text-transform:uppercase}
      .stage2-flow-kicker i{display:inline-block;width:7px;height:7px;border-radius:50%;background:#ff8a24;margin-right:8px}
      .stage2-flow-head h1{font:800 clamp(30px,4vw,48px)/1.05 Manrope;margin:10px 0 10px;letter-spacing:-1.5px}
      .stage2-flow-head p{margin:0;color:#9db0bb;font:400 14px/1.6 Inter;max-width:760px}
      .stage2-flow-back{border:1px solid rgba(150,170,181,.3);background:rgba(4,17,27,.55);color:#dce5ea;border-radius:22px;padding:10px 17px;font:700 11px Inter;cursor:pointer;margin-bottom:28px}
      .stage2-flow-back:hover{border-color:#ff8500;color:#ff8500}
      .stage2-flow-card{max-width:1100px;margin:0 auto;border:1px solid rgba(91,143,177,.3);border-radius:18px;background:linear-gradient(180deg,rgba(7,27,41,.96),rgba(3,15,24,.96));padding:26px;display:grid;grid-template-columns:1fr auto;gap:26px;align-items:center;box-shadow:0 22px 60px rgba(0,0,0,.22)}
      .stage2-flow-card .eyebrow{font:800 9px Inter;letter-spacing:1.7px;color:#718896;margin-bottom:9px}
      .stage2-flow-card h2{font:800 24px Manrope;margin:0 0 8px}
      .stage2-flow-card p{margin:0;color:#aebdc6;font:400 12px/1.55 Inter;max-width:700px}
      .stage2-flow-open{min-width:150px;height:44px;border:0;border-radius:24px;background:#ff8500;color:#08131b;font:800 11px Inter;cursor:pointer;padding:0 20px}
      .stage2-flow-open:hover{filter:brightness(1.08)}
      .stage2-flow-note{max-width:1100px;margin:16px auto 0;color:#687f8c;font:400 10px/1.5 Inter}
      .stage2-flow-viewer{position:fixed;inset:0;z-index:9999;background:#000;display:flex;align-items:center;justify-content:center;overflow:auto}
      .stage2-flow-viewer img{display:block;width:100%;height:100%;object-fit:contain}
      @media(max-width:700px){.stage2-flow-screen{padding:24px 18px 35px}.stage2-flow-card{grid-template-columns:1fr;padding:20px}.stage2-flow-open{width:100%}}
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
      <div class="stage2-flow-head">
        <button class="stage2-flow-back" type="button" onclick="renderJourney(1,-1)">← Voltar para Fábrica</button>
        <div class="stage2-flow-kicker"><i></i> FLUXOS DA ETAPA 02 · FÁBRICA</div>
        <h1>Fluxos</h1>
        <p>Fluxos relacionados à estrutura e à operação da fábrica que já estão representados no protótipo.</p>
      </div>
      <article class="stage2-flow-card">
        <div><div class="eyebrow">FLUXO 01</div><h2>Gestão da Quarentena</h2><p>Fluxo de recebimento, entrada em quarentena, avaliação pelo Controle da Qualidade e definição do destino do material.</p></div>
        <button class="stage2-flow-open" type="button" onclick="openStage2QuarantineFlow()">Abrir fluxo →</button>
      </article>
      <div class="stage2-flow-note">O conteúdo apresentado segue o fluxo já existente no projeto. Novos fluxos somente serão incluídos após validação.</div>
    </section>`;
  };

  window.openStage2QuarantineFlow=function(){
    injectStyle();
    const viewer=document.createElement('div');
    viewer.className='stage2-flow-viewer';
    viewer.innerHTML='<img src="assets/fluxo-estoque-quarentena.svg?v=1.0.0" alt="Fluxo – Gestão da Quarentena (iLabPharma)">';
    document.body.appendChild(viewer);
    document.body.classList.add('journey-stage2-flow-viewer-mode');
  };
})();