const journeyStages=[
  {n:1,title:'Indústria',kicker:'CAPÍTULO 01',intro:'A jornada começa pela estrutura organizacional e pelos controles de acesso e documentação.',items:['Profissionais','Contas de Usuários','Perfis e Permissões','Pessoa Jurídica','Estrutura Organizacional','Gestão Documental']},
  {n:2,title:'Fábrica',kicker:'CAPÍTULO 02',intro:'Com a estrutura definida, entram os recursos físicos e operacionais da fábrica.',items:['Almoxarifados','Setores / Salas','Equipamentos','Instrumentos','Linhas','Centro de trabalhos','Localizações']},
  {n:3,title:'Preparação',kicker:'CAPÍTULO 03',intro:'Antes da produção, a infraestrutura e os recursos precisam estar preparados conforme os controles apresentados no processo.',items:['Equipamentos qualificados','Equipamentos limpos','Calibrações válidas','Manutenções em dia','Salas liberadas']},
  {n:4,title:'Medicamento',kicker:'CAPÍTULO 04',intro:'A base do medicamento é organizada a partir de fornecedores, materiais, produtos, fórmulas e especificações.',items:['Fornecedores','Matérias-Primas','Materiais de Embalagens','Produtos','Fórmulas','Especificações','Métodos Analíticos']},
  {n:5,title:'Produção',kicker:'CAPÍTULO 05',intro:'A jornada chega à execução da produção, passando pelo planejamento e pelas etapas operacionais descritas no processo.',items:['Planejamento','Ordem de Produção','Separação de materiais','Pesagem','Mistura','Granulação','Compressão','Revestimento','Embalagem']},
  {n:6,title:'Controle da Qualidade',kicker:'CAPÍTULO 06',intro:'O produto passa pelas atividades de amostragem, análises e decisão de qualidade antes de seguir para a Garantia da Qualidade.',items:['Amostragem','Análises em Processo','Análises Físico-Químicas','Aprovação / Reprovação','Liberação para GQ']},
  {n:7,title:'Garantia da Qualidade',kicker:'CAPÍTULO 07',intro:'A qualidade consolida a revisão e as decisões necessárias para a liberação do lote e o encerramento da operação.',items:['Gestão da Qualidade','Revisão documental','Investigação de desvio','Aprovação do lote','Liberação do lote','Fechamento da OP','Auditorias e CAPA']},
  {n:8,title:'Produto Acabado',kicker:'CAPÍTULO 08',intro:'A jornada chega ao produto acabado, estoque, expedição e rastreabilidade.',items:['Produto acabado','Liberação do lote','Estoque','Expedição','Cliente','Rastreabilidade','Auditorias e CAPA']}
];
let journeyIndex=0;
function renderJourney(index=journeyIndex){
  journeyIndex=Math.max(0,Math.min(index,journeyStages.length-1));
  const s=journeyStages[journeyIndex];
  setCrumbs('Jornada',''+s.title);
  document.querySelectorAll('.nav-item').forEach(x=>x.classList.remove('active'));
  const nav=document.querySelector('[data-view="home"]'); if(nav)nav.classList.add('active');
  app.innerHTML=`<section class="journey-shell">
    <div class="journey-head">
      <div><span class="section-kicker">JORNADA GUIADA • ${s.kicker}</span><h1>${s.title}</h1><p>${s.intro}</p></div>
      <div class="journey-counter"><strong>${String(s.n).padStart(2,'0')}</strong><span>/ 08</span></div>
    </div>
    <div class="journey-progress">${journeyStages.map((x,i)=>`<button class="journey-dot ${i===journeyIndex?'current':''} ${i<journeyIndex?'done':''}" onclick="renderJourney(${i})" title="${x.title}"><span>${String(x.n).padStart(2,'0')}</span><b>${x.title}</b></button>`).join('')}</div>
    <div class="journey-stage">
      <div class="journey-stage-main"><div class="stage-number">${String(s.n).padStart(2,'0')}</div><div><span class="section-kicker">${s.kicker}</span><h2>${s.title}</h2><p>${s.intro}</p></div></div>
      <div class="journey-items">${s.items.map((item,i)=>`<div class="journey-item"><span>${String(i+1).padStart(2,'0')}</span><strong>${item}</strong></div>`).join('')}</div>
    </div>
    <div class="journey-nav"><button class="ghost-btn" ${journeyIndex===0?'disabled':''} onclick="renderJourney(${journeyIndex-1})">← Voltar</button><div><span>Você está aqui</span><strong>${s.title}</strong></div><button class="primary-btn" onclick="${journeyIndex===journeyStages.length-1?'finishJourney()':'renderJourney('+ (journeyIndex+1) +')'}">${journeyIndex===journeyStages.length-1?'Concluir jornada':'Continuar →'}</button></div>
  </section>`;
}
function finishJourney(){
  setCrumbs('Jornada','Concluída');
  app.innerHTML=`<section class="journey-finish"><div class="finish-mark">✓</div><span class="section-kicker">JORNADA CONCLUÍDA</span><h1>Você percorreu a história<br><span>de ponta a ponta.</span></h1><p>Da estrutura da indústria ao produto acabado, a jornada apresentou os oito estágios documentados do processo de produção de medicamentos.</p><div class="finish-path">${journeyStages.map(s=>`<span>${String(s.n).padStart(2,'0')} · ${s.title}</span>`).join('')}</div><div class="journey-nav finish-nav"><button class="ghost-btn" onclick="renderJourney(0)">↺ Reiniciar jornada</button><button class="primary-btn" onclick="renderMap()">Explorar mapa de processos →</button></div></section>`;
}
