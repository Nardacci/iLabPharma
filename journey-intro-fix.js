(function(){
  const originalRenderJourneyIntro=window.renderJourneyIntro;
  if(typeof originalRenderJourneyIntro!=='function') return;
  window.renderJourneyIntro=function(){
    originalRenderJourneyIntro();
    document.body.classList.add('journey-intro-fullscreen');
    const button=document.querySelector('.journey-start-btn span');
    if(button) button.textContent='Seguir';
    const btn=document.querySelector('.journey-start-btn');
    if(btn) btn.setAttribute('aria-label','Seguir para a jornada');

    const visual=document.querySelector('.journey-intro-visual');
    if(!visual || visual.querySelector('.intro-module')) return;
    const modules=[
      ['PRODUÇÃO','gear'],['CQ','flask'],['GQ','shield'],['DOCUMENTOS','document'],
      ['RASTREABILIDADE','trace'],['COMERCIAL','cart'],['ESTOQUE','box'],['PATRIMÔNIO','asset']
    ];
    const icons={
      gear:'<svg viewBox="0 0 32 32"><path d="M13 4h6l1 4 3 2 4-1 3 5-3 3v4l3 3-3 5-4-1-3 2-1 4h-6l-1-4-3-2-4 1-3-5 3-3v-4l-3-3 3-5 4 1 3-2 1-4z"/><circle cx="16" cy="19" r="5"/></svg>',
      flask:'<svg viewBox="0 0 32 32"><path d="M12 4h8M14 4v8l-8 14c-.7 1.2.2 2 1.5 2h17c1.3 0 2.2-.8 1.5-2l-8-14V4M9 22h14"/></svg>',
      shield:'<svg viewBox="0 0 32 32"><path d="M16 3l11 4v8c0 7-4.5 11.5-11 14C9.5 26.5 5 22 5 15V7l11-4z"/><path d="m11 16 3 3 7-8"/></svg>',
      document:'<svg viewBox="0 0 32 32"><path d="M8 3h13l4 4v22H8zM21 3v5h5M12 14h9M12 19h9M12 24h6"/></svg>',
      trace:'<svg viewBox="0 0 32 32"><circle cx="8" cy="8" r="3"/><circle cx="24" cy="16" r="3"/><circle cx="8" cy="25" r="3"/><path d="M11 8h7l3 5M21 19l-10 4M11 25h7"/></svg>',
      cart:'<svg viewBox="0 0 32 32"><path d="M4 6h4l3 15h13l4-11H9M13 27a1.5 1.5 0 1 1-3 0 1.5 1.5 0 1 1 3 0m13 0a1.5 1.5 0 1 1-3 0 1.5 1.5 0 1 1 3 0"/></svg>',
      box:'<svg viewBox="0 0 32 32"><path d="m16 4 11 6-11 6L5 10 16 4zM5 10v12l11 6 11-6V10M16 16v12"/></svg>',
      asset:'<svg viewBox="0 0 32 32"><rect x="7" y="4" width="18" height="24" rx="2"/><path d="M12 9h8M12 14h8M12 19h3m4 0h1M12 24h8"/></svg>'
    };
    modules.forEach((m,i)=>{
      const el=document.createElement('div');
      el.className='intro-module intro-module-'+(i+1);
      el.innerHTML='<div class="intro-module-icon">'+icons[m[1]]+'</div><b>'+m[0]+'</b>';
      visual.appendChild(el);
    });
    if(!document.getElementById('introModuleStyles')){
      const style=document.createElement('style');style.id='introModuleStyles';style.textContent=`
        .journey-intro-visual{z-index:1}
        .intro-module{position:absolute;z-index:4;display:flex;flex-direction:column;align-items:center;gap:5px;transform:translate(-50%,-50%);width:90px;pointer-events:none}
        .intro-module-icon{width:52px;height:52px;border-radius:50%;display:grid;place-items:center;border:1px solid rgba(255,132,0,.5);background:radial-gradient(circle at 50% 38%,#17344a,#07131d 74%);box-shadow:0 0 18px rgba(255,126,0,.12),inset 0 0 15px rgba(255,126,0,.05)}
        .intro-module-icon svg{width:23px;height:23px;fill:none;stroke:#ff8a00;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
        .intro-module b{font:800 7px Inter;color:#aebdc6;letter-spacing:.55px;white-space:nowrap;text-shadow:0 1px 8px #02080e}
        .intro-module-1{left:50%;top:1%}.intro-module-2{left:85%;top:16%}.intro-module-3{left:99%;top:50%}.intro-module-4{left:85%;top:84%}
        .intro-module-5{left:50%;top:99%}.intro-module-6{left:15%;top:84%}.intro-module-7{left:1%;top:50%}.intro-module-8{left:15%;top:16%}
        @media(max-width:900px){.intro-module{width:78px}.intro-module-icon{width:44px;height:44px}.intro-module-icon svg{width:19px;height:19px}.intro-module b{font-size:6px}}
        @media(max-width:600px){.intro-module-icon{width:36px;height:36px}.intro-module-icon svg{width:16px;height:16px}.intro-module b{font-size:5.5px}.intro-module{gap:3px}}
      `;document.head.appendChild(style);
    }
  };
})();