/* Seletor de versão: Legado | Novo. A escolha vem da URL (?versao=novo), depois da última escolha (localStorage, opcional) e, por padrão, Legado. */
(function(){
  var V=['legado','novo'];
  function daUrl(){try{var q=new URLSearchParams(location.search).get('versao');return V.indexOf(q)>=0?q:null;}catch(e){return null;}}
  function salva(){try{var s=localStorage.getItem('ilms-versao');return V.indexOf(s)>=0?s:null;}catch(e){return null;}}
  function guarda(v){try{localStorage.setItem('ilms-versao',v);}catch(e){}}
  var url=daUrl(), pag=document.body.getAttribute('data-versao-pagina');
  var atual=pag||url||salva()||'legado';
  if(pag||url)guarda(atual);
  function aplicar(){
    document.querySelectorAll('[data-so-versao]').forEach(function(el){el.hidden=el.getAttribute('data-so-versao')!==atual;});
    document.querySelectorAll('[data-set-versao]').forEach(function(b){b.setAttribute('aria-pressed',b.getAttribute('data-set-versao')===atual?'true':'false');});
    document.dispatchEvent(new CustomEvent('ilms-versao',{detail:atual}));
  }
  document.addEventListener('click',function(e){
    var b=e.target.closest&&e.target.closest('[data-set-versao]'); if(!b)return;
    atual=b.getAttribute('data-set-versao'); guarda(atual);
    try{var u=new URL(location.href);u.searchParams.set('versao',atual);history.replaceState(null,'',u);}catch(x){}
    aplicar();
  });
  window.ilmsVersao={atual:function(){return atual;}};
  aplicar();
})();
