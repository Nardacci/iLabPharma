(function(){
  const original=window.renderStageFlow;
  if(typeof original!=='function') return;

  const cards=[
    {key:'beneficios',icon:'✓',tone:'green',title:'Benefícios',items:['Processos integrados e consistentes','Redução de retrabalho','Conformidade com ANVISA / BPF','Melhor rastreabilidade','Segurança da informação','Governança de acessos']},
    {key:'riscos',icon:'!',tone:'red',title:'Riscos sem os cadastros',items:['Impossibilidade de executar processos dependentes','Dados inconsistentes','Falhas na rastreabilidade','Não conformidades regulatórias','Atrasos na produção e liberação'],quote:'Sem os cadastros e parâmetros necessários, os processos dependentes não podem ser executados corretamente.'},
    {key:'cadastros',icon:'▦',tone:'blue',title:'Principais Cadastros',groups:[
      {name:'Organização e Empresas',items:['Pessoa Jurídica','Estrutura Organizacional','Centro de Custo','Conta Contábil / Gerencial']},
      {name:'Usuários e Perfis',items:['Profissional','Conta Usuário','Perfil / Grupo de Usuários','Funções Profissionais']},
      {name:'Estrutura Física e Recursos',items:['Ambientes / Local Físico','Equipamentos / Categoria','Instrumentos / Utensílios','Pontos de Água / Utilidades']},
      {name:'Tabelas e Parâmetros',items:['Grau de Contaminação','Configurações de Notificação','Microservices','Notificações do Sistema']}
    ]},
    {key:'dependentes',icon:'⌘',tone:'purple',title:'Módulos Dependentes',items:['Produção · OPE · Lote · Processos','Estoque · Materiais · Lotes · Movimentações','CQ · Amostras · Análises · Laudos','GQ · Desvios · Mudanças · Auditorias','Documentos · Revisões · Aprovações · Vigência','Rastreabilidade · Eventos · Histórico · Serialização']}
  ];

  function modal(){
    let el=document.getElementById('principal-flow-info-modal');
    if(el) return el;
    el=document.createElement('div');
    el.id='principal-flow-info-modal';
    el.className='principal-flow-info-modal';
    el.innerHTML='<div class="pfim-backdrop" data-pfim-close></div><section class="pfim-dialog" role="dialog" aria-modal="true" aria-labelledby="pfim-title"><button class="pfim-close" data-pfim-close aria-label="Fechar">×</button><div id="pfim-body"></div></section>';
    document.body.appendChild(el);
    el.addEventListener('click',e=>{if(e.target.closest('[data-pfim-close]')) el.classList.remove('is-open')});
    return el;
  }

  function openCard(card){
    const m=modal(), body=m.querySelector('#pfim-body');
    let html='<div class="pfim-kicker">MÓDULO PRINCIPAL</div><h2 id="pfim-title">'+card.title+'</h2>';
    if(card.groups){
      html+='<div class="pfim-groups">'+card.groups.map(g=>'<div class="pfim-group"><h3>'+g.name+'</h3><ul>'+g.items.map(x=>'<li>'+x+'</li>').join('')+'</ul></div>').join('')+'</div>';
    }else{
      html+='<ul class="pfim-list">'+card.items.map(x=>'<li><span>'+card.icon+'</span>'+x+'</li>').join('')+'</ul>';
      if(card.quote) html+='<blockquote>'+card.quote+'</blockquote>';
    }
    body.innerHTML=html;
    m.classList.add('is-open');
  }

  function inject(){
    if(!document.body.classList.contains('principal-flow-only-mode')) return;
    const main=document.querySelector('.principal-flow-only-main');
    const bottom=main&&main.querySelector('.principal-flow-only-bottom');
    if(!main||!bottom) return;
    main.querySelector('.principal-flow-info-cards')?.remove();
    const wrap=document.createElement('section');
    wrap.className='principal-flow-info-cards';
    wrap.setAttribute('aria-label','Informações complementares do Módulo Principal');
    wrap.innerHTML='<div class="pfic-label">EXPLORE O MÓDULO PRINCIPAL</div><div class="pfic-grid">'+cards.map((c,i)=>'<button class="pfic-card '+c.tone+'" data-pfic="'+i+'"><span class="pfic-icon">'+c.icon+'</span><span><strong>'+c.title+'</strong><small>Ver detalhes</small></span><b>→</b></button>').join('')+'</div>';
    bottom.before(wrap);
    wrap.querySelectorAll('[data-pfic]').forEach(btn=>btn.addEventListener('click',()=>openCard(cards[Number(btn.dataset.pfic)])));
  }

  window.renderStageFlow=function(stageIndex){
    original(stageIndex);
    requestAnimationFrame(inject);
  };
})();

(function(){
  const css=document.createElement('style');
  css.textContent=`
    .principal-flow-info-cards{margin:24px 0 0;padding-top:18px;border-top:1px solid rgba(104,139,157,.12)}
    .pfic-label{font:800 8px Inter;letter-spacing:1.8px;color:#718896;margin-bottom:10px}
    .pfic-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
    .pfic-card{min-height:72px;border:1px solid rgba(105,141,159,.25);border-radius:12px;background:linear-gradient(145deg,rgba(9,31,45,.96),rgba(5,20,30,.96));color:#eaf1f4;padding:10px 11px;display:grid;grid-template-columns:34px 1fr 16px;align-items:center;gap:9px;text-align:left;cursor:pointer;transition:.2s ease;box-shadow:0 10px 24px rgba(0,0,0,.14)}
    .pfic-card:hover{transform:translateY(-2px);border-color:rgba(255,133,0,.6);background:linear-gradient(145deg,rgba(12,40,57,.98),rgba(6,24,35,.98))}
    .pfic-icon{width:32px;height:32px;border-radius:50%;display:grid;place-items:center;color:#fff;font:900 14px Inter}
    .pfic-card.green .pfic-icon{background:#21a875}.pfic-card.red .pfic-icon{background:#d63d45}.pfic-card.blue .pfic-icon{background:#2274bd}.pfic-card.purple .pfic-icon{background:#6b42b7}
    .pfic-card strong{display:block;font:800 11px/1.15 Manrope}.pfic-card small{display:block;margin-top:4px;color:#7f96a3;font:600 8px Inter}.pfic-card>b{color:#ff8500;font-size:16px}
    .principal-flow-info-cards + .principal-flow-only-bottom{margin-top:18px}
    .principal-flow-info-modal{position:fixed;inset:0;z-index:9999;display:none;align-items:center;justify-content:center;padding:24px;box-sizing:border-box}
    .principal-flow-info-modal.is-open{display:flex}.pfim-backdrop{position:absolute;inset:0;background:rgba(0,7,13,.78);backdrop-filter:blur(5px)}
    .pfim-dialog{position:relative;width:min(760px,92vw);max-height:82vh;overflow:auto;border:1px solid rgba(92,151,190,.45);border-radius:18px;background:linear-gradient(145deg,#081d2b,#04111b);box-shadow:0 30px 90px rgba(0,0,0,.55);padding:30px;color:#e9f1f5}
    .pfim-close{position:absolute;right:15px;top:12px;width:34px;height:34px;border:1px solid rgba(150,170,181,.3);border-radius:50%;background:rgba(255,255,255,.03);color:#fff;font-size:23px;cursor:pointer}.pfim-close:hover{border-color:#ff8500;color:#ff8500}
    .pfim-kicker{font:800 8px Inter;letter-spacing:1.8px;color:#4db5ff}.pfim-dialog h2{margin:7px 40px 20px 0;font:800 27px/1.1 Manrope;letter-spacing:-.5px}.pfim-list{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:8px}.pfim-list li{display:flex;gap:10px;align-items:flex-start;padding:11px 12px;border:1px solid rgba(105,141,159,.2);border-radius:10px;background:rgba(8,28,42,.65);font:500 11px/1.35 Inter}.pfim-list li span{flex:0 0 21px;width:21px;height:21px;border-radius:50%;display:grid;place-items:center;background:#214a65;color:#fff;font-size:10px}.pfim-groups{display:grid;grid-template-columns:1fr 1fr;gap:12px}.pfim-group{border:1px solid rgba(105,141,159,.2);border-radius:12px;padding:14px;background:rgba(8,28,42,.6)}.pfim-group h3{margin:0 0 8px;font:800 11px Inter;color:#fff}.pfim-group ul{margin:0;padding-left:17px;color:#b9c9d1;font:500 10px/1.6 Inter}.pfim-dialog blockquote{margin:18px 0 0;padding:14px 16px;border-left:3px solid #ff8500;background:rgba(255,133,0,.06);border-radius:0 10px 10px 0;color:#dbe5ea;font:600 11px/1.45 Inter}
    @media(max-width:1050px){.pfic-grid{grid-template-columns:1fr 1fr}}
    @media(max-width:700px){.pfic-grid{grid-template-columns:1fr}.pfim-list,.pfim-groups{grid-template-columns:1fr}.pfim-dialog{padding:22px}.principal-flow-info-cards{margin-top:18px}}
  `;
  document.head.appendChild(css);
})();
