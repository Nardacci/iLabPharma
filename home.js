function renderHome(){
  document.body.classList.remove('journey-mode','journey-intro-mode');
  document.body.classList.add('home-mode');
  setCrumbs('iLabPharma','');
  const modules=[
    {title:'PRODUÇÃO',cls:'module-1',icon:'gear'},
    {title:'CQ',cls:'module-2',icon:'flask'},
    {title:'GQ',cls:'module-3',icon:'shield'},
    {title:'DOCUMENTOS',cls:'module-4',icon:'document'},
    {title:'RASTREABILIDADE',cls:'module-5',icon:'trace'},
    {title:'COMERCIAL',cls:'module-6',icon:'cart'},
    {title:'ESTOQUE',cls:'module-7',icon:'box'},
    {title:'PATRIMÔNIO',cls:'module-8',icon:'asset'}
  ];
  const icons={
    gear:'<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M13 4h6l1 4 3 2 4-1 3 5-3 3v4l3 3-3 5-4-1-3 2-1 4h-6l-1-4-3-2-4 1-3-5 3-3v-4l-3-3 3-5 4 1 3-2 1-4z"/><circle cx="16" cy="19" r="5"/></svg>',
    box:'<svg viewBox="0 0 32 32" aria-hidden="true"><path d="m16 4 11 6-11 6L5 10 16 4zM5 10v12l11 6 11-6V10M16 16v12"/></svg>',
    flask:'<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M12 4h8M14 4v8l-8 14c-.7 1.2.2 2 1.5 2h17c1.3 0 2.2-.8 1.5-2l-8-14V4M9 22h14"/></svg>',
    shield:'<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16 3l11 4v8c0 7-4.5 11.5-11 14C9.5 26.5 5 22 5 15V7l11-4z"/><path d="m11 16 3 3 7-8"/></svg>',
    document:'<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M8 3h13l4 4v22H8zM21 3v5h5M12 14h9M12 19h9M12 24h6"/></svg>',
    trace:'<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="8" cy="8" r="3"/><circle cx="24" cy="16" r="3"/><circle cx="8" cy="25" r="3"/><path d="M11 8h7l3 5M21 19l-10 4M11 25h7"/></svg>',
    cart:'<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M4 6h4l3 15h13l4-11H9M13 27a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0m13 0a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0"/></svg>',
    asset:'<svg viewBox="0 0 32 32" aria-hidden="true"><rect x="7" y="4" width="18" height="24" rx="2"/><path d="M12 9h8M12 14h8M12 19h3m4 0h1M12 24h8"/></svg>'
  };
  app.innerHTML=`
    <section class="home-screen">
      <header class="home-header">
        <button class="home-brand" onclick="renderHome()" aria-label="Página inicial">
          <img src="assets/ilabpharma-logo.svg" alt="iLabPharma">
          <span>INTELIGÊNCIA APLICADA</span>
        </button>
      </header>

      <div class="home-main">
        <div class="home-copy">
          <div class="home-kicker"><span></span> ILABPHARMA</div>
          <h1>Inteligência aplicada<br>à gestão da <em>produção<br>laboratorial de<br>medicamentos e vacinas.</em></h1>
          <p>Uma visão conectada dos processos, da qualidade e da produção para uma operação mais inteligente, segura e eficiente.</p>
          <button class="home-cta" onclick="renderJourneyIntro()"><strong>▶</strong><span>Iniciar jornada</span><b>→</b></button>
          <div class="home-values">
            <div><strong>Especialização</strong><span>para a indústria farmacêutica</span></div>
            <div><strong>Processos</strong><span>integrados e conectados</span></div>
            <div><strong>Visão</strong><span>do processo ao todo</span></div>
          </div>
        </div>

        <div class="home-orbit" aria-label="Ecossistema de módulos">
          <div class="orbit-glow"></div>
          <div class="orbit-ring ring-outer"></div><div class="orbit-ring ring-middle"></div><div class="orbit-ring ring-inner"></div>
          <div class="orbit-cross cross-v"></div><div class="orbit-cross cross-h"></div>
          <div class="orbit-core"><img src="assets/ilabpharma-logo.svg" alt="iLabPharma"></div>
          ${modules.map(m=>`<div class="orbit-module ${m.cls}"><div class="module-icon">${icons[m.icon]}</div><b class="module-label">${m.title}</b></div>`).join('')}
        </div>
      </div>
    </section>`;
}

function renderJourneyIntro(){
  document.body.classList.remove('home-mode');
  document.body.classList.add('journey-mode','journey-intro-mode');
  setCrumbs('Jornada','');
  document.querySelectorAll('.nav-item').forEach(x=>x.classList.remove('active'));
  app.innerHTML=`<section class="journey-intro">
    <header class="journey-intro-header">
      <button class="journey-intro-brand" onclick="renderHome()" aria-label="Voltar para a página inicial"><img src="assets/ilabpharma-logo.svg" alt="iLabPharma"></button>
      <div class="journey-intro-actions">
        <button class="journey-home-btn" onclick="renderHome()" aria-label="Voltar para Home" title="Voltar para Home">⌂</button>
      </div>
    </header>
    <main class="journey-intro-main">
      <div class="journey-intro-copy">
        <span class="journey-intro-kicker"><i></i> A JORNADA</span>
        <h1>Do processo ao <em>todo.</em></h1>
        <p>O iLabPharma apresenta uma visão conectada dos processos que estruturam e sustentam a operação farmacêutica.</p>
        <p>Nesta jornada, você acompanha essa operação desde a estruturação da indústria e da fábrica, passando pela preparação, medicamento, produção, Controle da Qualidade e Garantia da Qualidade, até chegar ao produto acabado.</p>
        <button class="journey-start-btn" onclick="renderJourney(0)"><strong>▶</strong><span>Iniciar jornada</span><b>→</b></button>
      </div>
      <div class="journey-intro-visual" aria-hidden="true">
        <div class="intro-orbit-glow"></div><div class="intro-ring intro-ring-1"></div><div class="intro-ring intro-ring-2"></div><div class="intro-ring intro-ring-3"></div><div class="intro-cross intro-cross-v"></div><div class="intro-cross intro-cross-h"></div><div class="intro-core"><img src="assets/ilabpharma-logo.svg" alt=""></div>
      </div>
    </main>
  </section>`;
  if(!document.getElementById('journeyIntroStyles')){
    const style=document.createElement('style');style.id='journeyIntroStyles';style.textContent=`
      .journey-intro{min-height:calc(100vh - 28px);margin:0;border:1px solid rgba(91,143,177,.28);border-radius:18px;overflow:hidden;position:relative;background:radial-gradient(circle at 72% 45%,rgba(255,126,0,.055),transparent 24%),radial-gradient(circle at 88% 75%,rgba(0,104,170,.12),transparent 31%),linear-gradient(135deg,#02080e 0%,#04131f 54%,#061b2a 100%);color:#fff}.journey-intro:before{content:'';position:absolute;inset:0;pointer-events:none;background:linear-gradient(90deg,rgba(0,0,0,.12),transparent 54%),radial-gradient(circle at 10% 90%,rgba(255,126,0,.14),transparent 22%)}.journey-intro-header{height:70px;display:flex;align-items:center;justify-content:space-between;padding:0 34px;position:relative;z-index:5}.journey-intro-brand{border:0;background:transparent;padding:0;cursor:pointer}.journey-intro-brand img{width:190px;height:auto;max-height:40px;object-fit:contain;object-position:left center}.journey-intro-actions{display:flex;align-items:center;gap:10px}.journey-home-btn{height:38px;width:38px;border-radius:22px;background:transparent;color:#fff;cursor:pointer;border:1px solid rgba(255,255,255,.28);font-size:20px;line-height:1}.journey-home-btn:hover{border-color:#ff8500;color:#ff8500}.journey-intro-main{position:relative;z-index:2;min-height:calc(100vh - 98px);display:flex;align-items:center;padding:20px 7% 54px}.journey-intro-copy{width:47%;max-width:650px}.journey-intro-kicker{display:flex;align-items:center;gap:9px;color:#aebcc6;font-size:10px;font-weight:800;letter-spacing:2px;margin-bottom:18px}.journey-intro-kicker i{width:7px;height:7px;border-radius:50%;background:#ff8200;box-shadow:0 0 14px rgba(255,130,0,.75)}.journey-intro-copy h1{font:800 clamp(40px,4vw,58px)/1.02 Manrope;letter-spacing:-2.4px;margin:0 0 22px}.journey-intro-copy h1 em{font-style:normal;color:#ff8500}.journey-intro-copy p{max-width:620px;color:#c6d2da;font-size:14px;line-height:1.65;margin:0 0 12px}.journey-start-btn{width:270px;height:54px;margin-top:18px;border:0;border-radius:10px;background:linear-gradient(135deg,#ff8a00,#f47700);color:#fff;display:flex;align-items:center;gap:14px;padding:0 17px;cursor:pointer;box-shadow:0 12px 28px rgba(255,126,0,.22);font:700 14px Inter}.journey-start-btn strong{width:34px;height:34px;border-radius:50%;display:grid;place-items:center;background:#101820;color:#ff8500;font-size:13px}.journey-start-btn span{flex:1;text-align:left}.journey-start-btn b{font-size:21px;font-weight:400}.journey-start-btn:hover{transform:translateY(-1px);box-shadow:0 15px 34px rgba(255,126,0,.3)}.journey-intro-visual{position:absolute;width:min(500px,42vw);height:min(500px,42vw);right:5%;top:50%;transform:translateY(-48%)}.intro-orbit-glow{position:absolute;inset:12%;border-radius:50%;background:radial-gradient(circle,rgba(255,126,0,.11),transparent 58%);filter:blur(7px)}.intro-ring{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);border-radius:50%;border:1px solid rgba(87,143,176,.2)}.intro-ring-1{width:100%;height:100%}.intro-ring-2{width:73%;height:73%;border-color:rgba(255,130,0,.28)}.intro-ring-3{width:48%;height:48%;border-style:dashed;border-color:rgba(92,150,183,.22)}.intro-cross{position:absolute;background:rgba(87,151,190,.16);left:50%;top:50%}.intro-cross-v{width:1px;height:100%;transform:translate(-50%,-50%)}.intro-cross-h{height:1px;width:100%;transform:translate(-50%,-50%)}.intro-core{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:150px;height:150px;border-radius:50%;display:grid;place-items:center;background:radial-gradient(circle at 50% 40%,#10283a,#030c14 72%);border:1.5px solid #ff8500;box-shadow:0 0 0 1px rgba(255,130,0,.13),0 0 45px rgba(255,130,0,.16),inset 0 0 35px rgba(255,130,0,.06)}.intro-core:before{content:'';position:absolute;inset:10px;border-radius:50%;border:1px solid rgba(255,130,0,.12)}.intro-core img{width:112px;position:relative;z-index:2}@media(max-width:900px){.journey-intro-header{padding:0 20px}.journey-intro-main{align-items:flex-start;padding:100px 28px 250px}.journey-intro-copy{width:100%}.journey-intro-visual{width:390px;height:390px;right:50%;top:auto;bottom:-140px;transform:translateX(50%)}.journey-intro-copy h1{font-size:43px}}@media(max-width:600px){.journey-intro{border-radius:14px;min-height:calc(100vh - 16px)}.journey-intro-header{height:62px;padding:0 14px}.journey-intro-brand img{width:150px}.journey-intro-main{min-height:calc(100vh - 16px);padding:80px 20px 210px}.journey-intro-copy h1{font-size:34px;letter-spacing:-1.5px}.journey-intro-copy p{font-size:12px;line-height:1.55}.journey-start-btn{width:100%;height:50px}.journey-intro-visual{width:300px;height:300px;bottom:-88px}.intro-core{width:92px;height:92px}.intro-core img{width:72px}.journey-home-btn{width:36px;height:36px}}
    `;document.head.appendChild(style);
  }
}

renderHome();