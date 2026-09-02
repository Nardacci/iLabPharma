function renderStageFlow(stageIndex=journeyIndex){
  const idx=Math.max(0,Math.min(stageIndex,journeyStages.length-1));
  const current=journeyStages[idx];
  journeyIndex=idx;
  journeySelected=0;
  document.body.classList.remove('home-mode','journey-intro-mode','journey-stage1-mode');
  document.body.classList.add('journey-mode','journey-flow-mode');
  setCrumbs('Jornada',current.title+' · Fluxo');
  document.querySelectorAll('.nav-item').forEach(x=>x.classList.remove('active'));

  const flowData={
    0:{title:'Como a indústria começa?',sub:'A estrutura vem antes da operação.',center:'INDÚSTRIA',centerSub:'Base estrutural da jornada',prompt:'Clique no núcleo para revelar como a etapa se organiza.',nodes:[
      {id:'people',title:'Pessoas',label:'Quem participa',icon:'01',text:'Identificar as pessoas que participam da operação e relacioná-las às funções profissionais utilizadas no processo.',source:'Módulo Principal · Cadastros · Funções Profissionais'},
      {id:'access',title:'Acessos',label:'Quem pode acessar',icon:'02',text:'Criar e administrar as contas utilizadas pelos usuários para acessar o sistema, com perfis e permissões associados.',source:'Módulo Principal · Administração'},
      {id:'org',title:'Organização',label:'Como a empresa se organiza',icon:'03',text:'Registrar as pessoas jurídicas e representar a estrutura organizacional da empresa como base para os demais processos.',source:'Módulo Principal · Cadastros · Pessoas Jurídicas / Estrutura Organizacional'},
      {id:'docs',title:'Documentação',label:'Base documental',icon:'04',text:'Compor a documentação associada à etapa de estruturação apresentada no processo de produção.',source:'Processo de Produção · Indústria'}
    ]},
    1:{title:'Onde a operação acontece?',sub:'A estrutura ganha espaço físico e recursos.',center:'FÁBRICA',centerSub:'Ambiente da operação',prompt:'Clique no núcleo para revelar os elementos apresentados para a fábrica.',nodes:[
      {id:'warehouse',title:'Almoxarifados',label:'Materiais e armazenamento',icon:'01',text:'Representação dos almoxarifados que fazem parte da estrutura da fábrica.',source:'Processo de Produção · Fábrica'},
      {id:'rooms',title:'Salas / Setores',label:'Ambientes da operação',icon:'02',text:'Representação dos setores e salas que compõem os ambientes da operação.',source:'Processo de Produção · Fábrica'},
      {id:'equipment',title:'Equipamentos',label:'Recursos da operação',icon:'03',text:'Cadastro dos equipamentos utilizados na estrutura apresentada para a operação.',source:'Módulo Principal · Cadastros · Equipamentos'},
      {id:'instruments',title:'Instrumentos',label:'Recursos de controle',icon:'04',text:'Cadastro dos instrumentos que fazem parte da estrutura da operação.',source:'Módulo Principal · Cadastros · Instrumentos'},
      {id:'locations',title:'Linhas e localizações',label:'Estrutura física',icon:'05',text:'Elementos da estrutura da fábrica apresentados no processo de produção.',source:'Processo de Produção · Fábrica'}
    ]},
    2:{title:'A fábrica está pronta?',sub:'Condições antes da fabricação.',center:'PREPARAÇÃO',centerSub:'Condições apresentadas antes da fabricação',prompt:'Clique no núcleo para revelar as condições desta etapa.',nodes:[
      {id:'qualified',title:'Equipamentos qualificados',label:'Condição do recurso',icon:'01',text:'Condição apresentada para os equipamentos na etapa de Preparação.',source:'Processo de Produção · Preparação'},
      {id:'clean',title:'Equipamentos limpos',label:'Condição de limpeza',icon:'02',text:'Condição de limpeza dos equipamentos apresentada na etapa de Preparação.',source:'Processo de Produção · Preparação'},
      {id:'calibration',title:'Calibrações válidas',label:'Condição de calibração',icon:'03',text:'Condição de calibração apresentada para os recursos na etapa de Preparação.',source:'Processo de Produção · Preparação'},
      {id:'maintenance',title:'Manutenções em dia',label:'Condição de manutenção',icon:'04',text:'Condição de manutenção apresentada na etapa de Preparação.',source:'Processo de Produção · Preparação'},
      {id:'rooms-ready',title:'Salas liberadas',label:'Condição do ambiente',icon:'05',text:'Condição apresentada para as salas antes da fabricação.',source:'Processo de Produção · Preparação'}
    ]}
  };
  const data=flowData[idx]||flowData[0];
  window.flowExplorer={revealed:false,selected:null};

  const rail=journeyStages.map((s,i)=>`<button class="flow-rail-step ${i===idx?'active':''}" onclick="renderStageFlow(${i})"><span>${String(i+1).padStart(2,'0')}</span><strong>${s.title}</strong></button>`).join('<i>→</i>');
  const nodes=data.nodes.map(n=>`<button class="flow-explorer-node node-${n.id}" data-node="${n.id}" onclick="selectFlowNode('${n.id}')"><span>${n.icon}</span><strong>${n.title}</strong><small>${n.label}</small></button>`).join('');

  app.innerHTML=`
    <section class="journey-flow-screen">
      <header class="journey-flow-header">
        <button class="journey-flow-brand" onclick="renderHome()" aria-label="Voltar para Home"><img src="assets/ilabpharma-logo.svg" alt="iLabPharma"></button>
        <div class="journey-flow-actions"><button class="journey-flow-home" onclick="renderHome()" aria-label="Voltar para Home">⌂</button><button class="journey-flow-login" onclick="renderPlaceholder('Acesso')"><span>♙</span> Entrar</button></div>
      </header>
      <div class="journey-flow-layout">
        <aside class="journey-flow-sidebar">
          <div class="journey-flow-side-title"><span>${String(idx+1).padStart(2,'0')}</span><div><strong>${current.title}</strong><small>Explorar o processo</small></div></div>
          <div class="journey-flow-side-label">NESTA ETAPA</div>
          <nav class="journey-flow-side-nav">
            ${(current.purposes||current.items).map((x,i)=>`<button onclick="renderJourney(${idx},${i})"><span>${String(i+1).padStart(2,'0')}</span>${x.name||x}<em>›</em></button>`).join('')}
            <button class="is-flow"><span>◎</span>Fluxo<em>›</em></button>
          </nav>
          <div class="journey-flow-side-note"><span>COMO USAR</span><strong>Clique nos elementos.<br>O processo se revela<br>a cada descoberta.</strong></div>
        </aside>
        <main class="journey-flow-main">
          <div class="journey-flow-title-row">
            <div><span class="journey-flow-kicker"><i></i> EXPLORAÇÃO DO PROCESSO</span><h1>${data.title}</h1><p>${data.sub}</p></div>
            <div class="flow-explorer-progress"><span>ETAPA</span><strong>${String(idx+1).padStart(2,'0')} / 08</strong></div>
          </div>
          <div class="flow-rail" aria-label="Etapas da jornada">${rail}</div>

          <section class="flow-explorer-canvas">
            <div class="flow-canvas-grid"></div>
            <div class="flow-canvas-hint"><span>EXPLORAÇÃO GUIADA</span><strong>${data.prompt}</strong></div>
            <div class="flow-lines flow-lines-before"><i></i><i></i><i></i><i></i></div>
            <button class="flow-explorer-core" onclick="revealFlowNodes()" aria-label="Revelar elementos do processo">
              <span class="core-pulse"></span><span class="core-orbit"></span><b>◎</b><strong>${data.center}</strong><small>${data.centerSub}</small><em>CLIQUE PARA EXPLORAR</em>
            </button>
            <div class="flow-explorer-nodes">${nodes}</div>
            <div class="flow-explorer-detail" id="flowExplorerDetail" aria-live="polite"><div class="detail-empty"><span>+</span><strong>O detalhe aparece aqui</strong><small>Escolha um elemento do processo depois de revelar a etapa.</small></div></div>
          </section>

          <div class="flow-explorer-footer">
            <button class="ghost-btn" onclick="renderJourney(${idx})">← Voltar para ${current.title}</button>
            <div class="flow-footer-status"><span>VOCÊ ESTÁ EXPLORANDO</span><strong>${String(idx+1).padStart(2,'0')} · ${current.title}</strong></div>
            <button class="primary-btn" onclick="${idx===7?'finishJourney()':'renderJourney('+(idx+1)+')'}">${idx===7?'Concluir jornada':'Próxima etapa →'}</button>
          </div>
        </main>
      </div>
    </section>`;
}

function revealFlowNodes(){
  const canvas=document.querySelector('.flow-explorer-canvas');
  if(!canvas) return;
  window.flowExplorer.revealed=true;
  canvas.classList.add('is-revealed');
  const hint=canvas.querySelector('.flow-canvas-hint');
  if(hint) hint.innerHTML='<span>ETAPA REVELADA</span><strong>Agora explore cada elemento para entender sua função no processo.</strong>';
}

function selectFlowNode(id){
  const canvas=document.querySelector('.flow-explorer-canvas');
  if(!canvas) return;
  if(!window.flowExplorer||!window.flowExplorer.revealed) revealFlowNodes();
  const data={
    people:['Pessoas','Quem participa','Identificar as pessoas que participam da operação e relacioná-las às funções profissionais utilizadas no processo.','Módulo Principal · Cadastros · Funções Profissionais'],
    access:['Acessos','Quem pode acessar','Criar e administrar as contas utilizadas pelos usuários para acessar o sistema, com perfis e permissões associados.','Módulo Principal · Administração'],
    org:['Organização','Como a empresa se organiza','Registrar as pessoas jurídicas e representar a estrutura organizacional da empresa como base para os demais processos.','Módulo Principal · Cadastros · Pessoas Jurídicas / Estrutura Organizacional'],
    docs:['Documentação','Base documental','Compor a documentação associada à etapa de estruturação apresentada no processo de produção.','Processo de Produção · Indústria'],
    warehouse:['Almoxarifados','Materiais e armazenamento','Representação dos almoxarifados que fazem parte da estrutura da fábrica.','Processo de Produção · Fábrica'],
    rooms:['Salas / Setores','Ambientes da operação','Representação dos setores e salas que compõem os ambientes da operação.','Processo de Produção · Fábrica'],
    equipment:['Equipamentos','Recursos da operação','Cadastro dos equipamentos utilizados na estrutura apresentada para a operação.','Módulo Principal · Cadastros · Equipamentos'],
    instruments:['Instrumentos','Recursos de controle','Cadastro dos instrumentos que fazem parte da estrutura da operação.','Módulo Principal · Cadastros · Instrumentos'],
    locations:['Linhas e localizações','Estrutura física','Elementos da estrutura da fábrica apresentados no processo de produção.','Processo de Produção · Fábrica'],
    qualified:['Equipamentos qualificados','Condição do recurso','Condição apresentada para os equipamentos na etapa de Preparação.','Processo de Produção · Preparação'],
    clean:['Equipamentos limpos','Condição de limpeza','Condição de limpeza dos equipamentos apresentada na etapa de Preparação.','Processo de Produção · Preparação'],
    calibration:['Calibrações válidas','Condição de calibração','Condição de calibração apresentada para os recursos na etapa de Preparação.','Processo de Produção · Preparação'],
    maintenance:['Manutenções em dia','Condição de manutenção','Condição de manutenção apresentada na etapa de Preparação.','Processo de Produção · Preparação'],
    'rooms-ready':['Salas liberadas','Condição do ambiente','Condição apresentada para as salas antes da fabricação.','Processo de Produção · Preparação']
  };
  const item=data[id]; if(!item) return;
  document.querySelectorAll('.flow-explorer-node').forEach(x=>x.classList.toggle('selected',x.dataset.node===id));
  const detail=document.getElementById('flowExplorerDetail');
  if(detail) detail.innerHTML=`<div class="flow-detail-card"><div class="flow-detail-head"><span>ELEMENTO DO PROCESSO</span><b>×</b></div><h3>${item[0]}</h3><strong>${item[1]}</strong><p>${item[2]}</p><div class="flow-detail-source"><span>FONTE</span><b>${item[3]}</b></div></div>`;
  canvas.classList.add('has-detail');
}
