(function () {
  'use strict';
  var D = window.DADOS;
  if (!D) { return; }
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var el = function (tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var reduzir = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var CORES = ['#ff7a00', '#3ea6ff', '#38d17a', '#9b7bff', '#ffc545'];
  var NE = D.etapas.length;
  var view = 'inicio';
  var views = {};          // ganchos de cada tela: mostrar(passo), proximo(), anterior(), rotulos()
  var zoomAberto = function () { return false; };

  /* ---------- roteiro: do início ao fim, em um só documento ---------- */
  var SEQ = [{ p: 'inicio', cap: 'Início', tit: 'Início' }];
  D.etapas.forEach(function (e) {
    SEQ.push({ p: 'funciona', id: e.id, parte: 'visao', cap: 'Como funciona', tit: e.nome });
    SEQ.push({ p: 'funciona', id: e.id, parte: 'fluxos', cap: 'Como funciona', tit: e.nome + ' · fluxos' });
  });
  D.grupos.forEach(function (g, i) { SEQ.push({ p: 'anvisa', g: i, cap: 'Normas da ANVISA', tit: g }); });
  SEQ.push({ p: 'entrega', cap: 'O que entregamos', tit: 'O que entregamos' });
  var CAPS = ['Início', 'Como funciona', 'Normas da ANVISA', 'O que entregamos'];
  var TITULOS = { inicio: 'iLabPharma · Do insumo ao lote liberado', funciona: 'Como funciona · iLabPharma', anvisa: 'Normas da ANVISA · iLabPharma', entrega: 'O que entregamos · iLabPharma' };
  var atualSeq = 0;

  var hashAtual = function () { return location.hash.replace('#', ''); };
  function hashDe(t) {
    if (t.p === 'inicio') return '';
    if (t.p === 'funciona') return t.id + (t.parte === 'fluxos' ? '-fluxos' : '');
    if (t.p === 'anvisa') return 'g' + t.g;
    return 'entrega';
  }
  function seqDoHash() {
    var h = hashAtual();
    if (!h || h === 'inicio') return 0;
    if (h === 'entrega') return SEQ.length - 1;
    var m = /^g(\d+)$/.exec(h);
    if (m && +m[1] < D.grupos.length) return 1 + 2 * NE + (+m[1]);
    var fl = /-fluxos$/.test(h), id = h.replace(/-fluxos$/, '');
    for (var i = 0; i < NE; i++) if (D.etapas[i].id === id) return 1 + 2 * i + (fl ? 1 : 0);
    return 0;
  }

  function trocarView(v) {
    view = v;
    document.body.setAttribute('data-pag', v);
    $$('.view').forEach(function (x) { x.hidden = x.id !== 'v-' + v; });
    var ativa = $('#v-' + v);
    ativa.classList.remove('entra'); void ativa.offsetWidth; ativa.classList.add('entra');
    $$('.topo nav a').forEach(function (a) { a.classList.toggle('ativo', a.getAttribute('data-view') === v); });
    document.title = TITULOS[v];
    window.scrollTo(0, 0);
  }

  function ir(k, semHistorico) {
    if (k < 0 || k >= SEQ.length) return;
    var t = SEQ[k], mudouView = t.p !== view;
    atualSeq = k;
    if (mudouView) trocarView(t.p);
    if (views[t.p] && views[t.p].mostrar) views[t.p].mostrar(t, mudouView);
    if (!mudouView) window.scrollTo({ top: 0, behavior: reduzir ? 'auto' : 'smooth' });
    var h = hashDe(t);
    if (!semHistorico && hashAtual() !== h && history.pushState) history.pushState(null, '', h ? '#' + h : location.pathname + location.search);
    barra();
  }
  function proximo() {
    var v = views[view];
    if (v && v.proximo && v.proximo()) return;
    if (atualSeq >= SEQ.length - 1) { ir(0); return; }
    ir(atualSeq + 1);
  }
  function anterior() {
    var v = views[view];
    if (v && v.anterior && v.anterior()) return;
    ir(atualSeq - 1);
  }

  function barra() {
    var b = $('#seq');
    if (!b) return;
    if (view === 'inicio') { b.style.display = 'none'; return; }
    b.style.display = '';
    var k = atualSeq, ult = SEQ.length - 1;
    var cap = SEQ[k].cap, capI = CAPS.indexOf(cap);
    var prox = k < ult ? SEQ[k + 1].tit : 'Recomeçar';
    var ant = k > 0 ? SEQ[k - 1].tit : '';
    var dentro = views[view] && views[view].rotulos ? views[view].rotulos() : null;   // "O que entregamos" anda de cena em cena
    var ehFim = k >= ult && !(dentro && dentro.prox);
    if (dentro && dentro.prox) prox = dentro.prox;
    if (dentro && dentro.ant) ant = dentro.ant;
    var doCap = SEQ.filter(function (s) { return s.cap === cap; });
    var pos = doCap.indexOf(SEQ[k]) + 1;
    b.innerHTML =
      '<button type="button" class="seq-bt" id="seqAnt" aria-label="Anterior"' + (k === 0 ? ' disabled' : '') + '><span aria-hidden="true">←</span><span class="seq-rot"><small>Anterior</small>' + esc(ant) + '</span></button>' +
      '<div class="seq-meio"><ol class="seq-caps">' + CAPS.map(function (c, i) { return '<li><button type="button" data-cap="' + i + '" class="' + (i === capI ? 'on' : (i < capI ? 'feito' : '')) + '">' + esc(c) + '</button></li>'; }).join('') + '</ol>' +
      '<div class="seq-prog" role="progressbar" aria-valuemin="0" aria-valuemax="' + ult + '" aria-valuenow="' + k + '"><i style="width:' + (k / ult * 100) + '%"></i></div>' +
      '<small class="seq-pos">' + (doCap.length > 1 ? pos + ' de ' + doCap.length + ' · ' + esc(SEQ[k].tit) : esc(cap)) + '</small></div>' +
      '<button type="button" class="seq-bt prox" id="seqProx" aria-label="Próximo"><span class="seq-rot"><small>' + (ehFim ? 'Fim' : 'Próximo') + '</small>' + esc(prox) + '</span><span aria-hidden="true">' + (ehFim ? '↺' : '→') + '</span></button>';
    $('#seqAnt').addEventListener('click', anterior);
    $('#seqProx').addEventListener('click', proximo);
    $$('[data-cap]', b).forEach(function (x) {
      x.addEventListener('click', function () {
        var c = CAPS[+x.getAttribute('data-cap')];
        for (var i = 0; i < SEQ.length; i++) if (SEQ[i].cap === c) { ir(i); break; }
      });
    });
  }

  /* ---------- teclado e tela cheia ---------- */
  function alternarTelaCheia() {
    var d = document.documentElement;
    if (document.fullscreenElement) { document.exitFullscreen(); }
    else if (d.requestFullscreen) { d.requestFullscreen().catch(function () {}); }
  }
  var btnTela = $('#telaCheia');
  if (btnTela) {
    if (!document.documentElement.requestFullscreen) btnTela.style.display = 'none';
    btnTela.addEventListener('click', alternarTelaCheia);
    document.addEventListener('fullscreenchange', function () { document.body.classList.toggle('em-tela-cheia', !!document.fullscreenElement); });
  }
  document.addEventListener('keydown', function (e) {
    if (zoomAberto() || e.altKey || e.ctrlKey || e.metaKey) return;
    var t = e.target && e.target.tagName;
    if (t === 'INPUT' || t === 'TEXTAREA' || t === 'SELECT') return;
    if (e.key === 'ArrowRight') { e.preventDefault(); if (view === 'inicio') ir(1); else proximo(); }
    else if (e.key === 'ArrowLeft' && view !== 'inicio') { e.preventDefault(); anterior(); }
    else if (e.key === 'f' || e.key === 'F') { e.preventDefault(); alternarTelaCheia(); }
  });
  window.addEventListener('hashchange', function () { var k = seqDoHash(); if (k !== atualSeq) ir(k, true); });

  /* ---------- diagrama de fluxo ---------- */
  function diagrama(f) {
    var h = '<div class="diagrama' + (f.paralelo ? ' paralelo' : '') + '">';
    f.fases.forEach(function (fase, i) {
      var cor = CORES[i % CORES.length];
      h += '<div class="fase" style="--cor:' + cor + '"><div class="fase-cab"><i>' + (i + 1) + '</i>' + esc(fase.nome) + '</div><div class="fase-passos">';
      fase.etapas.forEach(function (p) { h += '<div class="fp' + (p.dec ? ' dec' : '') + '">' + esc(p.t) + '</div>'; });
      h += '</div></div>';
    });
    return h + '</div>';
  }

  /* ---------- ampliação (tela cheia) do fluxo ---------- */
  var zoom = null, zEscala = 1, zUltimoFoco = null;
  zoomAberto = function () { return !!(zoom && zoom.classList.contains('aberto')); };
  function montarZoom() {
    zoom = el('div', 'zoom');
    zoom.setAttribute('role', 'dialog'); zoom.setAttribute('aria-modal', 'true'); zoom.setAttribute('aria-label', 'Fluxo ampliado');
    zoom.innerHTML = '<div class="zoom-barra"><div><h2 id="zTitulo"></h2><small id="zSub"></small></div>' +
      '<div class="zoom-ctl"><button type="button" id="zMenos" aria-label="Diminuir">−</button><output id="zPct">100%</output><button type="button" id="zMais" aria-label="Aumentar">+</button>' +
      '<button type="button" id="zAjusta">Ajustar</button><button type="button" class="fechar" id="zFecha">Fechar ✕</button></div></div>' +
      '<div class="zoom-area" id="zArea"><div class="zoom-caixa" id="zCaixa"><div class="zoom-conteudo" id="zCont"></div></div></div>';
    document.body.appendChild(zoom);
    $('#zFecha').addEventListener('click', fecharZoom);
    $('#zMais').addEventListener('click', function () { escalar(zEscala * 1.2); });
    $('#zMenos').addEventListener('click', function () { escalar(zEscala / 1.2); });
    $('#zAjusta').addEventListener('click', ajustar);
    var area = $('#zArea'), drag = null;
    area.addEventListener('pointerdown', function (e) {
      if (e.pointerType === 'touch') return;
      drag = { x: e.clientX, y: e.clientY, sl: area.scrollLeft, st: area.scrollTop };
      area.classList.add('arrastando');
    });
    window.addEventListener('pointermove', function (e) { if (!drag) return; area.scrollLeft = drag.sl - (e.clientX - drag.x); area.scrollTop = drag.st - (e.clientY - drag.y); });
    window.addEventListener('pointerup', function () { drag = null; area.classList.remove('arrastando'); });
    area.addEventListener('wheel', function (e) { if (e.ctrlKey || e.metaKey) { e.preventDefault(); escalar(zEscala * (e.deltaY < 0 ? 1.1 : 1 / 1.1)); } }, { passive: false });
    document.addEventListener('keydown', function (e) {
      if (!zoomAberto()) return;
      if (e.key === 'Escape') fecharZoom();
      else if (e.key === '+' || e.key === '=') escalar(zEscala * 1.2);
      else if (e.key === '-' || e.key === '_') escalar(zEscala / 1.2);
      else if (e.key === '0') ajustar();
    });
    window.addEventListener('resize', function () { if (zoomAberto()) ajustar(); });
  }
  function escalar(s) {
    zEscala = Math.max(.4, Math.min(3, s));
    var cont = $('#zCont'), caixa = $('#zCaixa');
    cont.style.transform = 'scale(' + zEscala + ')';
    caixa.style.width = (cont.scrollWidth * zEscala) + 'px';
    caixa.style.height = (cont.scrollHeight * zEscala) + 'px';
    $('#zPct').textContent = Math.round(zEscala * 100) + '%';
  }
  function ajustar() {
    var cont = $('#zCont'), area = $('#zArea');
    cont.style.transform = 'scale(1)';
    var w = cont.scrollWidth, h = cont.scrollHeight;
    var cs = getComputedStyle(area);
    var aw = area.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
    var ah = area.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
    escalar(Math.min(aw / w, ah / h, 2.2));
  }
  function abrirZoom(f, sub) {
    if (!zoom) montarZoom();
    zUltimoFoco = document.activeElement;
    $('#zTitulo').textContent = f.nome; $('#zSub').textContent = sub;
    $('#zCont').innerHTML = diagrama(f);
    zoom.classList.add('aberto');
    document.body.style.overflow = 'hidden';
    requestAnimationFrame(ajustar);
    $('#zFecha').focus();
  }
  function fecharZoom() {
    zoom.classList.remove('aberto');
    document.body.style.overflow = '';
    if (zUltimoFoco && zUltimoFoco.focus) zUltimoFoco.focus();
  }

  /* ---------- tela: início ---------- */
  (function initInicio() {
    var trilho = $('#trilho'), atualI = 0;
    var prog = el('li', 'prog'); prog.setAttribute('aria-hidden', 'true'); trilho.appendChild(prog);
    D.etapas.forEach(function (e) {
      var li = el('li'), b = el('a', 'no');
      b.href = '#' + e.id;
      b.innerHTML = '<span class="bola">' + e.num + '</span><span class="rot">' + esc(e.nome) + '<small>' + esc(e.modulos.join(' · ')) + '</small></span>';
      li.appendChild(b); trilho.appendChild(li);
    });
    var marcar = function () {
      var nos = $$('.no', trilho);
      nos.forEach(function (n, i) { n.classList.toggle('ativo', i === atualI); n.classList.toggle('feito', i < atualI); });
      prog.style.height = (nos[atualI].parentNode.offsetTop - nos[0].parentNode.offsetTop) + 'px';
      var e = D.etapas[atualI];
      $('#trilhoCard').innerHTML = '<span class="mod">' + esc(e.modulos.join(' + ')) + '</span><b>' + esc(e.nome) + '</b><span>' + esc(e.titulo) + '</span>';
    };
    views.inicio = { mostrar: marcar };
    marcar();
    if (!reduzir) setInterval(function () { if (view !== 'inicio') return; atualI = (atualI + 1) % NE; marcar(); }, 2800);
  })();

  /* ---------- tela: como funciona ---------- */
  (function initFunciona() {
    var atual = -1;
    var lista = $('#passos');
    D.etapas.forEach(function (e, i) {
      var li = el('li'), b = el('button', 'passo');
      b.type = 'button';
      b.innerHTML = '<span class="n">' + e.num + '</span><span class="t"><b>' + esc(e.nome) + '</b><small>' + esc(e.modulos.join(' · ')) + '</small></span>';
      b.addEventListener('click', function () { ir(1 + 2 * i); });
      li.appendChild(b); lista.appendChild(li);
    });

    var painelHtml = function (i) {
      var e = D.etapas[i];
      var mods = '<div class="mods">' + e.modulos.map(function (m) { return '<span class="chip mod">' + esc(m) + '</span>'; }).join('') + '</div>';
      var h = '<div class="parte parte-visao">' + mods;
      h += '<h3>' + esc(e.titulo) + '</h3><p class="pergunta">' + esc(e.pergunta) + '</p><p class="texto">' + esc(e.texto) + '</p>';
      h += '<div class="duas"><div class="bloco"><h4>O que o sistema faz</h4><ul class="faz">' + e.faz.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div>';
      h += '<div class="bloco"><h4>Ao final desta etapa</h4><p class="resultado">' + esc(e.resultado) + '</p><h4>Conecta com</h4><ul class="conecta">' + e.conecta.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div></div></div>';
      h += '<div class="parte parte-fluxos">' + mods + '<h3>Fluxos do processo · ' + esc(e.nome) + '</h3>';
      h += '<p class="texto">Cada fluxo mostra as fases e as etapas do processo. Use "Ampliar o fluxo" para ver em tela cheia.</p><div class="fluxos">';
      if (e.fluxos.length) {
        var ultimoG = null;
        h += '<div class="fluxo-lista">' + e.fluxos.map(function (f, k) {
          var cab = '';
          if (f.grupo && f.grupo !== ultimoG) { cab = '<p class="grupo-fluxo">' + esc(f.grupo) + '</p>'; ultimoG = f.grupo; }
          return cab + '<div class="fcard" data-k="' + k + '"><button class="fcab" type="button" aria-expanded="false"><span class="ft"><b>' + esc(f.nome) + '</b><small>' + esc(f.linha) + '</small></span><span class="seta" aria-hidden="true">⌄</span></button><div class="fcorpo"></div></div>';
        }).join('') + '</div>';
      } else {
        h += '<p class="vazio">Os cadastros do Principal sustentam todos os fluxos dos outros módulos.</p>';
      }
      if (e.imagem) h += '<p class="vermais"><a href="' + e.imagem[0] + '" target="_blank" rel="noopener">' + esc(e.imagem[1]) + ' <span aria-hidden="true">↗</span></a></p>';
      h += '</div>';
      if (e.ponte) h += '<p class="ponte"><span>Na sequência</span>' + esc(e.ponte) + '</p>';
      return h + '</div>';
    };

    var dicaDe = function (c) {
      var dg = $('.diagrama', c), dica = $('.dica', c);
      if (dg && dica) dica.textContent = (dg.scrollWidth > dg.clientWidth + 4) ? 'Role para o lado ou amplie o fluxo para ver todas as fases.' : '';
    };
    var abrirCard = function (novo, c, abrir) {
      $$('.fcard.aberto', novo).forEach(function (o) { o.classList.remove('aberto'); $('.fcab', o).setAttribute('aria-expanded', 'false'); });
      if (!abrir) return;
      var f = D.etapas[atual].fluxos[+c.getAttribute('data-k')];
      var corpo = $('.fcorpo', c);
      if (!corpo.firstChild) {
        corpo.innerHTML = '<div class="fbarra"><p class="dica"></p><button class="ampliar" type="button">⤢ Ampliar o fluxo</button></div>' + diagrama(f);
        $('.ampliar', corpo).addEventListener('click', function () { abrirZoom(f, D.etapas[atual].nome + ' · ' + f.linha); });
      }
      c.classList.add('aberto'); $('.fcab', c).setAttribute('aria-expanded', 'true');
      dicaDe(c);
    };

    var montarPainel = function () {
      var p = $('#painel'), novo = p.cloneNode(false);
      novo.innerHTML = painelHtml(atual);
      p.parentNode.replaceChild(novo, p);
      $$('.fcard', novo).forEach(function (c) {
        $('.fcab', c).addEventListener('click', function () { abrirCard(novo, c, !c.classList.contains('aberto')); });
      });
      var primeiro = $('.fcard', novo);
      if (primeiro) abrirCard(novo, primeiro, true);   // o primeiro fluxo já vem aberto
    };

    views.funciona = {
      mostrar: function (t) {
        var i = D.etapas.map(function (e) { return e.id; }).indexOf(t.id);
        var mudou = i !== atual;
        atual = i;
        $$('.passo', lista).forEach(function (b, k) { b.classList.toggle('ativo', k === i); });
        if (mudou) montarPainel();
        var p = $('#painel');
        p.classList.toggle('ver-fluxos', t.parte === 'fluxos');
        p.classList.remove('anima'); void p.offsetWidth; p.classList.add('anima');
        $$('.fcard.aberto', p).forEach(dicaDe);
      }
    };
  })();

  /* ---------- tela: normas da ANVISA (uma por grupo) ---------- */
  (function initAnvisa() {
    var T2 = D.totais;
    var fil = $('#filtros');
    fil.innerHTML = D.grupos.map(function (g, i) { return '<button type="button" role="tab" class="fchip" data-g="' + i + '">' + esc(g) + '</button>'; }).join('');
    fil.addEventListener('click', function (ev) {
      var b = ev.target.closest('.fchip'); if (!b) return;
      ir(1 + 2 * NE + (+b.getAttribute('data-g')));
    });
    views.anvisa = {
      mostrar: function (t) {
        var gAtual = t.g;
        $$('.fchip', fil).forEach(function (x) { var on = +x.getAttribute('data-g') === gAtual; x.classList.toggle('on', on); x.setAttribute('aria-selected', on); });
        var cob = $('#cobertura');
        if (gAtual === 0) {
          cob.style.display = '';
          cob.innerHTML = '<div class="kpi"><b>' + T2.temas + '</b><span>exigências da norma, com a resposta do sistema</span></div>' +
            '<div class="kpi"><b>' + T2.grupos + '</b><span>grupos: do sistema computadorizado à rastreabilidade</span></div>' +
            '<div class="kpi"><b>' + T2.modulos + '</b><span>módulos trabalhando juntos</span></div>';
        } else { cob.style.display = 'none'; cob.innerHTML = ''; }
        var qtd = D.normas.filter(function (n) { return n.g === gAtual; }).length;
        $('#anvisaSub').innerHTML = '<b class="fio">' + esc((D.fios || [])[gAtual] || '') + '</b> ' + esc(D.grupos[gAtual]) + ' · ' + qtd + (qtd === 1 ? ' exigência' : ' exigências') + ' da RDC 658/2022 e do Guia 33/2020.';
        var box = $('#normas'); box.innerHTML = '';
        D.normas.forEach(function (n) {
          if (n.g !== gAtual) return;
          var c = el('article', 'tema');
          c.id = 'tema-' + n.id;
          c.innerHTML = '<div><h3>' + esc(n.tema) + '</h3><div class="norma">' + esc(n.norma) + '</div></div>' +
            '<div><h5>Como o iLabPharma responde</h5><ul>' + n.resposta.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div>';
          box.appendChild(c);
        });
      }
    };
  })();

  /* ---------- tela: o que entregamos (cenas) ---------- */
  (function initEntrega() {
    var cenas = [{ intro: true }].concat(D.cenas);
    var box2 = $('#cenas'), pts = $('#pontos');
    var CORES2 = ['#ff7a00', '#3ea6ff', '#38d17a', '#9b7bff', '#ffc545', '#ff7a00', '#3ea6ff'];
    cenas.forEach(function (c, i) {
      var s = el('section', 'cena');
      s.style.setProperty('--cor', CORES2[i % CORES2.length]);
      s.style.setProperty('--gx', (20 + (i * 17) % 60) + '%'); s.style.setProperty('--gy', (30 + (i * 23) % 40) + '%');
      if (c.intro) {
        s.innerHTML = '<p class="kicker"><span class="ponto"></span>O que entregamos</p><div class="a">O que o <em>iLabPharma</em> entrega?</div><div class="apoio">Use <kbd>→</kbd> ou role para descobrir.</div><div class="rolar" aria-hidden="true">↓</div>';
      } else {
        var ultimo = i === cenas.length - 1;
        if (ultimo) s.classList.add('final');
        var contatos = ultimo && D.contatos && D.contatos.length ? '<div class="contatos">' + D.contatos.map(function (p) {
          return '<div class="contato"><b>' + esc(p.nome) + '</b>' + (p.email ? '<a href="mailto:' + esc(p.email) + '">' + esc(p.email) + '</a>' : '') + (p.celular ? '<a href="tel:' + esc(p.celular.replace(/[^\d+]/g, '')) + '">' + esc(p.celular) + '</a>' : '') + '</div>';
        }).join('') + '</div>' : '';
        s.innerHTML = '<div class="a">' + c.a + '</div><div class="b">' + c.b + '</div><p class="apoio">' + esc(c.apoio) + '</p>' +
          '<div class="mods">' + c.modulos.map(function (m2) { return '<span class="chip mod">' + esc(m2) + '</span>'; }).join('') + '</div>' + contatos +
          '<div class="num-cena" aria-hidden="true">' + String(i).padStart(2, '0') + '</div>';
      }
      box2.appendChild(s);
      var d = el('button'); d.type = 'button'; d.setAttribute('aria-label', 'Ir para a cena ' + (i + 1));
      d.addEventListener('click', function () { s.scrollIntoView({ behavior: reduzir ? 'auto' : 'smooth' }); });
      pts.appendChild(d);
    });
    var todas = $$('.cena', box2), bolas = $$('button', pts), cenaAtual = 0;
    var vaiPara = function (k) { todas[k].scrollIntoView({ behavior: reduzir ? 'auto' : 'smooth', block: 'start' }); };
    var marcarCena = function (k) {
      cenaAtual = k;
      todas[k].classList.add('vis');
      bolas.forEach(function (b, j) { b.classList.toggle('on', j === cenaAtual); });
      if (view === 'entrega') barra();
    };
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (x) { if (x.isIntersecting) marcarCena(todas.indexOf(x.target)); });
      }, { threshold: .55 });
      todas.forEach(function (s) { io.observe(s); });
    } else { todas.forEach(function (s) { s.classList.add('vis'); }); }
    views.entrega = {
      mostrar: function (t, mudouView) { if (mudouView) { todas.forEach(function (s) { s.classList.remove('vis'); }); marcarCena(0); } },
      // dentro de "O que entregamos", Próximo e Anterior andam de cena em cena
      proximo: function () { if (cenaAtual < todas.length - 1) { vaiPara(cenaAtual + 1); return true; } return false; },
      anterior: function () { if (cenaAtual > 0) { vaiPara(cenaAtual - 1); return true; } return false; },
      rotulos: function () { return { prox: cenaAtual < todas.length - 1 ? 'Próxima cena' : null, ant: cenaAtual > 0 ? 'Cena anterior' : null }; }
    };
  })();

  /* ---------- início ---------- */
  var k0 = seqDoHash();
  if (k0 === 0) { barra(); } else { ir(k0, true); }
})();
