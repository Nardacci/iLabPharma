(function(){
  const baseRenderJourney=window.renderJourney;
  if(typeof baseRenderJourney!=='function')return;
  const stages={
    2:{name:'Preparação',question:'A fábrica está pronta para produzir?',kicker:'CONDIÇÕES ANTES DA FABRICAÇÃO',intro:'Com a fábrica estruturada, chega o momento de preparar as condições apresentadas para a produção.',items:[['Equipamentos qualificados','Condição apresentada para os equipamentos na etapa de Preparação.'],['Equipamentos limpos','Condição de limpeza dos equipamentos apresentada na etapa de Preparação.'],['Calibrações válidas','Condição de calibração apresentada para os recursos na etapa de Preparação.'],['Manutenções em dia','Condição de manutenção apresentada para os recursos na etapa de Preparação.'],['Salas liberadas','Condição apresentada para as salas antes da fabricação.']],result:'O medicamento estará definido tecnicamente',source:'Processo de Produção · Preparação',theme:'prep'},
    3:{name:'Medicamento',question:'O que será produzido?',kicker:'BASE DO MEDICAMENTO',intro:'A etapa organiza os elementos apresentados como base para o medicamento.',items:[['Fornecedores','Elemento apresentado no processo de produção do medicamento.'],['Matérias-Primas','Elemento apresentado no processo de produção do medicamento.'],['Materiais de Embalagens','Elemento apresentado no processo de produção do medicamento.'],['Produtos','Elemento apresentado no processo de produção do medicamento.'],['Fórmulas','Elemento apresentado no processo de produção do medicamento.'],['Especificações','Elemento apresentado no processo de produção do medicamento.'],['Métodos Analíticos','Elemento apresentado no processo de produção do medicamento.']],result:'O medicamento estará definido tecnicamente',source:'Processo de Produção · Medicamento',theme:'med'},
    4:{name:'Produção',question:'Como o medicamento será fabricado?',kicker:'FABRICAÇÃO DO MEDICAMENTO',intro:'A produção apresenta as etapas pelas quais o medicamento passa para ser fabricado.',items:[['Planejamento','Etapa apresentada no processo de produção do medicamento.'],['Ordem de Produção','Etapa apresentada no processo de produção do medicamento.'],['Separação de materiais','Etapa apresentada no processo de produção do medicamento.'],['Pesagem','Etapa apresentada no processo de produção do medicamento.'],['Mistura','Etapa apresentada no processo de produção do medicamento.'],['Granulação','Etapa apresentada no processo de produção do medicamento.'],['Compressão','Etapa apresentada no processo de produção do medicamento.'],['Revestimento','Etapa apresentada no processo de produção do medicamento.'],['Embalagem','Etapa apresentada no processo de produção do medicamento.']],result:'Agora o medicamento deixa de ser uma especificação e passa a existir fisicamente',source:'Processo de Produção · Produção',theme:'prod'},
    5:{name:'CQ',question:'O produto atende às especificações?',kicker:'CONTROLE DA QUALIDADE',intro:'O Controle da Qualidade apresenta as etapas de amostragem, análise, avaliação e liberação para a Garantia da Qualidade.',items:[['Amostragem','Etapa apresentada no processo de Controle da Qualidade.'],['Análises em Processo','Etapa apresentada no processo de Controle da Qualidade.'],['Análises Físico-Químicas','Etapa apresentada no processo de Controle da Qualidade.'],['Aprovação/Reprovação','Resultado apresentado no processo de Controle da Qualidade.'],['Liberação para GQ','Etapa apresentada antes do encaminhamento para a Garantia da Qualidade.']],result:'O CQ garante que cada etapa',source:'Processo de Produção · Controle da Qualidade',theme:'cq'},
    6:{name:'GQ',question:'O lote pode ser liberado?',kicker:'GARANTIA DA QUALIDADE',intro:'A Garantia da Qualidade apresenta as atividades de gestão, revisão, investigação, aprovação e liberação do lote.',items:[['Gestão da Qualidade','Atividade apresentada no processo de Garantia da Qualidade.'],['Revisão documental','Etapa apresentada no processo de Garantia da Qualidade.'],['Investigação de desvio','Atividade apresentada no processo de Garantia da Qualidade.'],['Aprovação do lote','Etapa apresentada no processo de Garantia da Qualidade.'],['Liberação do lote','Etapa apresentada no processo de Garantia da Qualidade.'],['Fechamento da OP','Etapa apresentada no processo de Garantia da Qualidade.'],['Auditorias e CAPA','Atividades apresentadas no processo de Garantia da Qualidade.']],result:'A GQ governa, aprova e autoriza o lote para disponibilização no mercado',source:'Processo de Produção · Garantia da Qualidade',theme:'gq'},
    7:{name:'Produto Acabado',question:'Como o medicamento chega ao cliente?',kicker:'DESTINO DO PRODUTO',intro:'A etapa apresenta o caminho do produto acabado após a liberação do lote, até sua chegada ao cliente e sua rastreabilidade.',items:[['Produto acabado','Elemento apresentado após a fabricação e liberação do lote.'],['Liberação do lote','Etapa apresentada no processo de produto acabado.'],['Estoque','Etapa apresentada no processo de produto acabado.'],['Expedição','Etapa apresentada no processo de produto acabado.'],['Cliente','Destino apresentado no processo de produto acabado.'],['Rastreabilidade','Elemento apresentado no processo de produto acabado.'],['Auditorias e CAPA','Atividades apresentadas no processo de produto acabado.']],result:'Objetivo é entregar um medicamento seguro e confiável ao cliente',source:'Processo de Produção · Produto Acabado',theme:'acabado'}
  };
  const prepDetails=[
    {meaning:'Os equipamentos que participarão do processo produtivo devem estar em condição compatível com sua utilização e com a finalidade para a qual foram qualificados.',example:'Um equipamento destinado a uma determinada operação produtiva deve possuir sua qualificação correspondente antes de ser considerado para utilização nessa etapa.',objective:'demonstrar que o equipamento está apto, sob o ponto de vista de qualificação, para a utilização prevista.'},
    {meaning:'Além de qualificados, os equipamentos precisam estar em condições adequadas de limpeza antes de serem utilizados. A condição de limpeza está diretamente relacionada à prevenção de contaminações e à manutenção das condições necessárias para a fabricação.',example:'Antes da utilização de um equipamento, deve ser possível verificar que sua condição de limpeza está adequada para a operação prevista.',objective:'assegurar que o equipamento esteja disponível para utilização em condição de limpeza adequada.'},
    {meaning:'Os instrumentos utilizados para realizar medições devem possuir calibração válida, quando aplicável. A validade da calibração permite que as medições realizadas durante o processo tenham como referência instrumentos dentro das condições estabelecidas.',example:'Um instrumento utilizado para realizar uma medição durante uma operação produtiva não deve estar com sua calibração vencida.',objective:'assegurar a confiabilidade das medições realizadas durante o processo.'},
    {meaning:'Os equipamentos utilizados na operação devem estar sujeitos às condições de manutenção estabelecidas, evitando que equipamentos com manutenção pendente sejam utilizados inadequadamente.',example:'Se um equipamento possui uma manutenção prevista e essa condição ainda não foi atendida, sua utilização precisa ser avaliada antes de ser considerado disponível para a produção.',objective:'manter os equipamentos em condições adequadas de funcionamento e utilização.'},
    {meaning:'Os ambientes destinados às operações produtivas precisam estar disponíveis e liberados para a utilização prevista. A liberação da sala representa uma condição anterior à utilização daquele ambiente no processo.',example:'Antes de iniciar uma operação em determinado ambiente, deve ser possível identificar que a sala está liberada para utilização.',objective:'assegurar que o ambiente destinado à operação esteja disponível para a atividade prevista.'}
  ];
  function renderStage(index,selected=0){
    const s=stages[index];
    if(!s){baseRenderJourney(index,selected);return}
    const items=s.items;
    const sel=Math.max(0,Math.min(selected,items.length-1));
    journeyIndex=index;journeySelected=sel;closeGeneralFlow();
    document.body.className=document.body.className.replace(/journey-stage[1-8]-mode/g,'');
    document.body.classList.remove('home-mode','journey-intro-mode');
    document.body.classList.add('journey-mode','journey-stage1-mode','journey-stage-'+(index+1)+'-mode');
    setCrumbs('Jornada',s.name);
    document.querySelectorAll('.nav-item').forEach(x=>x.classList.remove('active'));
    const item=items[sel];
    const prep= index===2 ? prepDetails[sel] : null;
    const detailMarkup=prep ? `
      <div class="prep-item-card">
        <div class="prep-item-card-head"><span class="prep-item-number">${String(sel+1).padStart(2,'0')}</span><div><span class="stage1-section-label">CONDIÇÃO DA ETAPA</span><h3>${item[0]}</h3></div></div>
        <div class="prep-item-block"><span>O QUE SIGNIFICA?</span><p>${prep.meaning}</p></div>
        <div class="prep-item-block"><span>EXEMPLO</span><p>${prep.example}</p></div>
        <div class="prep-item-objective"><span>OBJETIVO DA CONDIÇÃO</span><p>${prep.objective}</p></div>
      </div>` : `
      <div class="stage1-detail"><div class="stage1-detail-top"><span class="stage1-detail-number">${String(sel+1).padStart(2,'0')}</span><div><span class="stage1-section-label">ELEMENTO DA ETAPA</span><h3>${item[0]}</h3></div></div><p>${item[1]}</p><div class="stage1-source"><span>FONTE</span><strong>${s.source}</strong></div></div>`;
    app.innerHTML=`
      <section class="stage1-screen">
        <header class="stage1-header">
          <div class="stage1-header-context">
            <button class="stage1-brand" onclick="renderHome()" aria-label="Voltar para Home"><img src="assets/ilabpharma-logo.svg" alt="iLabPharma"></button>
            <div class="stage1-page-title"><strong>${s.question.replace('?', ' <em>?</em>')}</strong><span>${s.intro}</span></div>
          </div>
          <div class="stage1-actions"><button class="stage1-home-btn" onclick="renderHome()" aria-label="Voltar para Home" title="Voltar para Home">⌂</button></div>
        </header>
        <div class="stage1-layout">
          <aside class="stage1-sidebar">
            <div class="stage1-side-title"><span>${String(index+1).padStart(2,'0')}</span><div><strong>${s.name}</strong><small>${s.question}</small></div></div>
            <nav class="stage1-items" aria-label="Elementos da etapa">
              ${items.map((x,i)=>`<button class="stage1-item ${i===sel?'selected':''}" onclick="renderJourney(${index},${i})"><span>${String(i+1).padStart(2,'0')}</span><strong>${x[0]}</strong><em>›</em></button>`).join('')}
              <button class="stage1-item stage1-flow-item" onclick="openGeneralFlow()"><span>◎</span><strong>Fluxo</strong><em>›</em></button>
            </nav>
            <div class="stage1-side-result"><span>AO FINAL DESTA ETAPA</span><strong>${s.result}</strong></div>
          </aside>
          <main class="stage1-main">
            <div class="stage1-context"><span class="stage1-kicker"><i></i> ${s.kicker}</span></div>
            ${detailMarkup}
            <div class="stage1-questions"><span class="stage1-section-label">AS PERGUNTAS QUE ESTRUTURAM ESTA ETAPA</span><div class="stage1-question-grid"><button onclick="renderJourney(${index},0)"><b>01</b><strong>${s.question}</strong><span>${items.slice(0,2).map(x=>x[0]).join(' · ')}</span></button><button onclick="renderJourney(${index},${Math.min(1,items.length-1)})"><b>02</b><strong>Quais elementos fazem parte?</strong><span>${items.slice(2,4).map(x=>x[0]).join(' · ')||items[0][0]}</span></button><button onclick="renderJourney(${index},${Math.min(2,items.length-1)})"><b>03</b><strong>O que acontece nesta etapa?</strong><span>${items[Math.min(2,items.length-1)][0]}</span></button></div></div>
            ${index===3?'<div class="stage1-system-image"><img src="imagens/Sistema%20-%20Medicamento.png?v=1.0.0" alt="Sistema - Medicamento"></div>':''}
            ${index===4?'<div class="stage1-system-image"><img src="imagens/Sistema%20-%20Producao.png?v=1.0.0" alt="Sistema - Producao"></div>':''}
            ${index===5?'<div class="stage1-system-image"><img src="imagens/Sistema%20-%20CQ.png?v=1.0.0" alt="Sistema - CQ"></div>':''}
            ${index===6?'<div class="stage1-system-image"><img src="imagens/Sistema%20-%20GQ.png?v=1.0.0" alt="Sistema - GQ"></div>':''}
            ${index===7?'<div class="stage1-system-image"><img src="imagens/Sistema%20-%20Acabado.png?v=1.0.0" alt="Sistema - Acabado"></div>':''}
            <div class="stage1-bottom"><button class="ghost-btn" onclick="renderJourney(${index-1})">← Voltar</button><div><span>Você está aqui</span><strong>${s.name}</strong></div><button class="primary-btn" onclick="${index===7?'finishJourney()':`renderJourney(${index+1})`}">${index===7?'Concluir jornada →':'Continuar →'}</button></div>
          </main>
        </div>
      </section>`;
  }
  window.renderJourney=function(index=0,selected=0){if(index<2){baseRenderJourney(index,selected);return}renderStage(index,selected)};
})();