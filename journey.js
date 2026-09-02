const journeyStages=[
  {n:1,title:'Indústria',kicker:'CAPÍTULO 01',contextTitle:'Estrutura antes da operação',intro:'Antes de produzir, a indústria precisa estar estruturada.',context:'A operação começa pela definição da organização, das pessoas que participam dos processos e dos níveis de acesso necessários para executar e controlar as atividades. No módulo Principal, essas informações são administradas como base estrutural para os demais processos.',contextNote:'É aqui que a estrutura administrativa ganha forma: usuários, perfis, organização e cadastros passam a compor uma base compartilhada pelos processos de Produção, Controle da Qualidade, Garantia da Qualidade, Estoque e outros módulos.',flow:['Pessoas','Acessos e Permissões','Organização','Estrutura da Empresa','Documentação'],purposes:[
    {name:'Profissionais',text:'Identificar as pessoas que participam da operação e relacioná-las às funções profissionais utilizadas no processo.',source:'Módulo Principal · Cadastros · Funções Profissionais'},
    {name:'Contas de Usuários',text:'Criar e administrar as contas utilizadas pelos usuários para acessar o sistema.',source:'Módulo Principal · Administração'},
    {name:'Perfis e Permissões',text:'Definir os perfis e as permissões associados aos usuários, determinando os acessos disponibilizados no sistema.',source:'Módulo Principal · Administração'},
    {name:'Pessoa Jurídica',text:'Registrar as pessoas jurídicas que participam dos processos, como fornecedores, clientes, transportadoras e fabricantes.',source:'Módulo Principal · Cadastros · Pessoas Jurídicas'},
    {name:'Estrutura Organizacional',text:'Representar a estrutura organizacional da empresa e disponibilizar essa base para os demais processos.',source:'Módulo Principal · Cadastros · Estrutura Organizacional'},
    {name:'Gestão Documental',text:'Compor a documentação associada à etapa de estruturação apresentada no processo de produção.',source:'Processo de Produção · Indústria'}
  ],items:[
    {name:'Profissionais',text:'Cadastro relacionado às pessoas que participam da operação.',source:'Módulo Principal · Administração · Cadastros'},
    {name:'Contas de Usuários',text:'Administração das contas utilizadas para acesso ao sistema.',source:'Módulo Principal · Administração'},
    {name:'Perfis e Permissões',text:'Definição dos perfis e das permissões associados aos usuários.',source:'Módulo Principal · Administração'},
    {name:'Pessoa Jurídica',text:'Cadastro de pessoas jurídicas utilizadas nos processos da operação.',source:'Módulo Principal · Cadastros'},
    {name:'Estrutura Organizacional',text:'Representação da estrutura organizacional da empresa.',source:'Módulo Principal · Cadastros'},
    {name:'Gestão Documental',text:'Elemento da etapa de estruturação da indústria apresentado no processo de produção.',source:'Processo de Produção · Indústria'}
  ]},
  {n:2,title:'Fábrica',kicker:'CAPÍTULO 02',contextTitle:'O ambiente onde a operação acontece',intro:'Com a estrutura organizacional definida, a próxima etapa é representar o ambiente onde a operação acontece.',context:'É neste ponto da jornada que a estrutura da empresa passa a ser representada fisicamente. A fábrica reúne os locais e recursos apresentados no processo de produção — almoxarifados, setores e salas, equipamentos, instrumentos, linhas, centros de trabalho e localizações. Esses elementos formam o cenário físico e operacional em que as etapas seguintes da produção acontecem.',contextNote:'Depois de definir quem participa da operação e como a organização está estruturada, precisamos saber onde essa operação acontece e quais recursos fazem parte desse ambiente. É essa representação que prepara a história para a etapa seguinte: a preparação da fábrica.',flow:['Almoxarifados','Salas / Setores','Equipamentos','Instrumentos','Linhas','Centros de Trabalho','Localizações'],items:[
    {name:'Almoxarifados',text:'Representação dos almoxarifados que fazem parte da estrutura da fábrica.',source:'Processo de Produção · Fábrica'},
    {name:'Setores / Salas',text:'Representação dos setores e salas que compõem os ambientes da operação.',source:'Processo de Produção · Fábrica'},
    {name:'Equipamentos',text:'Cadastro dos equipamentos utilizados na estrutura apresentada para a operação.',source:'Módulo Principal · Cadastros · Equipamentos'},
    {name:'Instrumentos',text:'Cadastro dos instrumentos que fazem parte da estrutura da operação.',source:'Módulo Principal · Cadastros · Instrumentos'},
    {name:'Linhas',text:'Elemento da estrutura da fábrica apresentado no processo de produção.',source:'Processo de Produção · Fábrica'},
    {name:'Centro de trabalhos',text:'Elemento da estrutura da fábrica apresentado no processo de produção.',source:'Processo de Produção · Fábrica'},
    {name:'Localizações',text:'Representação das localizações físicas utilizadas na estrutura apresentada.',source:'Processo de Produção · Fábrica'}
  ]},
  {n:3,title:'Preparação',kicker:'CAPÍTULO 03',contextTitle:'Condições antes da fabricação',intro:'Com a fábrica estruturada, chega o momento de preparar as condições apresentadas para a produção.',context:'A etapa de Preparação apresenta as condições que antecedem a fabricação: equipamentos qualificados, equipamentos limpos, calibrações válidas, manutenções em dia e salas liberadas.',contextNote:'A jornada passa, neste ponto, pelos recursos e ambientes que aparecem no processo de produção como parte da preparação antes da fabricação. É a transição entre a estrutura da fábrica e a etapa em que o medicamento será produzido.',flow:['Equipamentos qualificados','Equipamentos limpos','Calibrações válidas','Manutenções em dia','Salas liberadas'],items:[
    {name:'Equipamentos qualificados',text:'Condição apresentada para os equipamentos na etapa de Preparação.',source:'Processo de Produção · Preparação'},
    {name:'Equipamentos limpos',text:'Condição de limpeza dos equipamentos apresentada na etapa de Preparação.',source:'Processo de Produção · Preparação'},
    {name:'Calibrações válidas',text:'Condição de calibração apresentada para os recursos na etapa de Preparação.',source:'Processo de Produção · Preparação'},
    {name:'Manutenções em dia',text:'Condição de manutenção apresentada na etapa de Preparação.',source:'Processo de Produção · Preparação'},
    {name:'Salas liberadas',text:'Condição apresentada para as salas antes da fabricação.',source:'Processo de Produção · Preparação'}
  ]},
  {n:4,title:'Medicamento',kicker:'CAPÍTULO 04',contextTitle:'O que será produzido',intro:'O que será produzido?',context:'A etapa organiza os elementos apresentados como base para o medicamento.',flow:['Fornecedores','Matérias-Primas','Materiais de Embalagem','Produto','Fórmula','Especificações','Métodos Analíticos'],items:['Fornecedores','Matérias-Primas','Materiais de Embalagens','Produtos','Fórmulas','Especificações','Métodos Analíticos'].map(name=>({name,text:'Elemento apresentado no processo de produção do medicamento.',source:'Processo de Produção · Medicamento'}))},
  {n:5,title:'Produção',kicker:'CAPÍTULO 05',contextTitle:'A fabricação do medicamento',intro:'Da preparação à fabricação.',context:'A jornada chega à execução da produção, passando pelo planejamento e pelas etapas operacionais descritas no processo.',flow:['Planejamento','Ordem de Produção','Separação','Pesagem','Mistura','Granulação','Compressão','Revestimento','Embalagem'],items:['Planejamento','Ordem de Produção','Separação de materiais','Pesagem','Mistura','Granulação','Compressão','Revestimento','Embalagem'].map(name=>({name,text:'Etapa operacional apresentada no processo de produção.',source:'Processo de Produção · Produção'}))},
  {n:6,title:'Controle da Qualidade',kicker:'CAPÍTULO 06',contextTitle:'Avaliar antes de avançar',intro:'O produto precisa ser avaliado.',context:'O produto passa pelas atividades de amostragem, análises e decisão de qualidade antes de seguir para a Garantia da Qualidade.',flow:['Amostragem','Análises em Processo','Análises Físico-Químicas','Aprovação / Reprovação','Liberação para GQ'],items:['Amostragem','Análises em Processo','Análises Físico-Químicas','Aprovação / Reprovação','Liberação para GQ'].map(name=>({name,text:'Atividade apresentada no processo de produção.',source:'Processo de Produção · Controle da Qualidade'}))},
  {n:7,title:'Garantia da Qualidade',kicker:'CAPÍTULO 07',contextTitle:'A decisão sobre o lote',intro:'A qualidade agora entra na decisão final.',context:'A etapa apresenta revisão, investigação, decisões sobre o lote e fechamento da operação.',flow:['Gestão da Qualidade','Revisão Documental','Investigação de Desvio','Aprovação do Lote','Liberação do Lote','Fechamento da OP'],items:['Gestão da Qualidade','Revisão documental','Investigação de desvio','Aprovação do lote','Liberação do lote','Fechamento da OP','Auditorias e CAPA'].map(name=>({name,text:'Elemento apresentado no processo ou na documentação do módulo de Garantia da Qualidade.',source:'Processo de Produção · Garantia da Qualidade'}))},
  {n:8,title:'Produto Acabado',kicker:'CAPÍTULO 08',contextTitle:'O resultado da jornada',intro:'O produto chegou ao resultado.',context:'A jornada chega ao produto acabado, estoque, expedição e rastreabilidade.',flow:['Produto Acabado','Liberação do Lote','Estoque','Expedição','Cliente'],items:['Produto acabado','Liberação do lote','Estoque','Expedição','Cliente','Rastreabilidade','Auditorias e CAPA'].map(name=>({name,text:'Elemento apresentado no processo de produção.',source:'Processo de Produção · Produto Acabado'}))}
];
let journeyIndex=0;
let journeySelected=0;
function renderJourney(index=journeyIndex,selected=0){
  journeyIndex=Math.max(0,Math.min(index,journeyStages.length-1));
  const s=journeyStages[journeyIndex];
  const detailItems=s.purposes||s.items;
  journeySelected=Math.max(0,Math.min(selected,detailItems.length-1));
  const selectedItem=detailItems[journeySelected];
  closeGeneralFlow();
  document.body.classList.remove('home-mode');
  document.body.classList.add('journey-mode');
  setCrumbs('Jornada',s.title);
  document.querySelectorAll('.nav-item').forEach(x=>x.classList.remove('active'));
  const nav=document.querySelector('[data-view="home"]'); if(nav)nav.classList.add('active');
  app.innerHTML=`<section class="journey-shell">
    <div class="journey-head">
      <div><span class="section-kicker">JORNADA GUIADA • ${s.kicker}</span><h1>${s.title}</h1><p>${s.intro}</p></div>
      <div class="journey-counter"><strong>${String(s.n).padStart(2,'0')}</strong><span>/ 08</span></div>
    </div>
    <div class="journey-progress">${journeyStages.map((x,i)=>`<button class="journey-dot ${i===journeyIndex?'current':''} ${i<journeyIndex?'done':''}" onclick="renderJourney(${i})" title="${x.title}"><span></span><b>${String(x.n).padStart(2,'0')} · ${x.title}</b></button>`).join('')}</div>
    <div class="journey-context"><h3>${s.contextTitle}</h3><p>${s.context}</p>${s.contextNote?`<p class="context-note">${s.contextNote}</p>`:''}</div>
    ${s.purposes?`<div class="journey-purpose"><div class="purpose-heading"><div><h3>Cadastros dentro da estrutura da indústria</h3></div></div><div class="purpose-grid">${s.purposes.map((item,i)=>`<button class="purpose-card ${i===journeySelected?'selected':''}" onclick="renderJourney(${journeyIndex},${i})"><span class="purpose-icon">${String(i+1).padStart(2,'0')}</span><div><strong>${item.name}</strong><p>${item.text}</p></div><em>→</em></button>`).join('')}</div><div class="purpose-actions"><button class="flow-open-btn" onclick="openGeneralFlow()"><span>◎</span><div><strong>Ver fluxo geral da jornada</strong><small>Entenda onde a Indústria se conecta às demais etapas.</small></div><em>→</em></button></div></div>`:`<div class="journey-flow"><div class="flow-label">O FLUXO MOSTRA</div><div class="flow-track">${s.flow.map((x,i)=>`<div class="flow-node"><span>${String(i+1).padStart(2,'0')}</span><strong>${x}</strong></div>${i<s.flow.length-1?'<i>→</i>':''}`).join('')}</div></div>`}
    <div class="journey-nav"><button class="ghost-btn" ${journeyIndex===0?'disabled':''} onclick="renderJourney(${journeyIndex-1})">← Voltar</button><div><span>Você está aqui</span><strong>${s.title}</strong></div><button class="primary-btn" onclick="${journeyIndex===journeyStages.length-1?'finishJourney()':'renderJourney('+ (journeyIndex+1) +')'}">${journeyIndex===journeyStages.length-1?'Concluir jornada':'Continuar →'}</button></div>
  </section>`;
}
function openGeneralFlow(){
  closeGeneralFlow();
  const overlay=document.createElement('div');
  overlay.id='generalFlowOverlay';
  overlay.className='general-flow-overlay';
  overlay.innerHTML=`<div class="general-flow-backdrop" onclick="closeGeneralFlow()"></div><section class="general-flow-modal" role="dialog" aria-modal="true" aria-labelledby="generalFlowTitle">
    <header class="general-flow-header"><div><span class="section-kicker">VISÃO GERAL</span><h2 id="generalFlowTitle">Processo de Produção de Medicamentos</h2><p>Visão resumida da jornada end-to-end</p></div><button class="flow-close" onclick="closeGeneralFlow()" aria-label="Fechar">×</button></header>
    <div class="general-flow-scroll"><div class="general-flow-grid">${journeyStages.map((s,i)=>`<button class="general-stage stage-${i+1} ${i===journeyIndex?'is-current':''}" onclick="renderJourney(${i})"><div class="general-stage-top"><span>${String(s.n).padStart(2,'0')}</span><strong>${s.title}</strong></div><small>${stageQuestion(s.n)}</small><div class="general-stage-items">${s.flow.map(x=>`<span>${x}</span>`).join('')}</div><footer>${stageOutcome(s.n)}</footer></button>${i<journeyStages.length-1?'<div class="general-arrow">→</div>':''}`).join('')}</div>
    <div class="general-flow-path">${journeyStages.map((s,i)=>`<button onclick="renderJourney(${i})" class="${i===journeyIndex?'active':''}">${s.title}</button>${i<journeyStages.length-1?'<span>→</span>':''}`).join('')}</div></div>
    <footer class="general-flow-footer"><span><b>Você está aqui:</b> ${journeyStages[journeyIndex].title}</span><button class="flow-footer-btn" onclick="closeGeneralFlow()">Continuar nesta etapa →</button></footer>
  </section>`;
  document.body.appendChild(overlay);
  document.body.classList.add('flow-modal-open');
  requestAnimationFrame(()=>overlay.classList.add('visible'));
}
function closeGeneralFlow(){
  const overlay=document.getElementById('generalFlowOverlay');
  if(overlay){overlay.classList.remove('visible');setTimeout(()=>overlay.remove(),160)}
  document.body.classList.remove('flow-modal-open');
}
function stageQuestion(n){return ['Quem irá fabricar o medicamento?','Onde o medicamento será produzido?','A fábrica está pronta para produzir?','O que será produzido?','Como o medicamento será fabricado?','O produto atende às especificações?','O lote pode ser liberado?','Como o medicamento chega ao cliente?'][n-1]||''}
function stageOutcome(n){return ['Estrutura da indústria','Estrutura física preparada','Condições antes da fabricação','Medicamento definido','Execução da produção','Avaliação da qualidade','Decisão sobre o lote','Produto acabado e rastreável'][n-1]||''}
function finishJourney(){
  document.body.classList.remove('home-mode');
  document.body.classList.add('journey-mode');
  setCrumbs('Jornada','Concluída');
  app.innerHTML=`<section class="journey-finish"><div class="finish-mark">✓</div><span class="section-kicker">JORNADA CONCLUÍDA</span><h1>Você percorreu a história<br><span>de ponta a ponta.</span></h1><p>Da estrutura da indústria ao produto acabado, a jornada apresentou os oito estágios documentados do processo de produção de medicamentos.</p><div class="finish-path">${journeyStages.map(s=>`<span>${String(s.n).padStart(2,'0')} · ${s.title}</span>`).join('')}</div><div class="journey-nav finish-nav"><button class="ghost-btn" onclick="renderJourney(0)">↺ Reiniciar jornada</button><button class="primary-btn" onclick="renderMap()">Explorar mapa de processos →</button></div></section>`;
}
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeGeneralFlow()});