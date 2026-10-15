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
  var pag = document.body.getAttribute('data-pag');

  /* ---------- transição entre páginas ---------- */
  document.addEventListener('click', function (ev) {
    var a = ev.target.closest('a[href]');
    if (!a || ev.defaultPrevented || ev.metaKey || ev.ctrlKey || ev.shiftKey || a.target === '_blank') return;
    var h = a.getAttribute('href');
    if (!h || h.charAt(0) === '#' || /^(https?:|mailto:)/.test(h) || reduzir) return;
    ev.preventDefault();
    document.body.classList.add('saindo');
    setTimeout(function () { window.location.href = h; }, 200);
  });
  window.addEventListener('pageshow', function (e) { if (e.persisted) document.body.classList.remove('saindo'); });

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
  function montarZoom() {
    zoom = el('div', 'zoom');
    zoom.setAttribute('role', 'dialog'); zoom.setAttribute('aria-modal', 'true'); zoom.setAttribute('aria-label', 'Fluxo ampliado');
    zoom.innerHTML = '<div class="zoom-barra"><div><h2 id="zTitulo"></h2><small id="zSub"></small></div>' +
      '<div class="zoom-ctl"><button type="button" id="zMenos" aria-label="Diminuir">−</button><output id="zPct">100%</output><button type="button" id="zMais" aria-label="Aumentar">+</button>' +
      '<button type="button" id="zAjusta">Ajustar</button><button type="button" id="zTela">Tela cheia</button><button type="button" class="fechar" id="zFecha">Fechar ✕</button></div></div>' +
      '<div class="zoom-area" id="zArea"><div class="zoom-caixa" id="zCaixa"><div class="zoom-conteudo" id="zCont"></div></div></div>';
    document.body.appendChild(zoom);
    $('#zFecha').addEventListener('click', fecharZoom);
    $('#zMais').addEventListener('click', function () { escalar(zEscala * 1.2); });
    $('#zMenos').addEventListener('click', function () { escalar(zEscala / 1.2); });
    $('#zAjusta').addEventListener('click', ajustar);
    $('#zTela').addEventListener('click', function () {
      if (document.fullscreenElement) { document.exitFullscreen(); }
      else if (zoom.requestFullscreen) { zoom.requestFullscreen().catch(function () {}); }
    });
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
      if (!zoom.classList.contains('aberto')) return;
      if (e.key === 'Escape' && !document.fullscreenElement) fecharZoom();
      else if (e.key === '+' || e.key === '=') escalar(zEscala * 1.2);
      else if (e.key === '-' || e.key === '_') escalar(zEscala / 1.2);
      else if (e.key === '0') ajustar();
    });
    window.addEventListener('resize', function () { if (zoom.classList.contains('aberto')) ajustar(); });
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
    if (document.fullscreenElement) document.exitFullscreen();
    zoom.classList.remove('aberto');
    document.body.style.overflow = '';
    if (zUltimoFoco && zUltimoFoco.focus) zUltimoFoco.focus();
  }

  /* ---------- página: início ---------- */
  if (pag === 'inicio') {
    var T = D.totais;
    var portas = [
      ['funciona.html', 'Entenda como o iLabPharma funciona', 'Sete etapas, ' + T.modulos + ' módulos e ' + T.fluxos + ' fluxos de processo', true],
      ['anvisa.html', 'Dentro das normas da ANVISA', T.temas + ' pontos da RDC 658/2022 e do Guia 33/2020'],
      ['entrega.html', 'O que entregamos', 'Muito além de um sistema']
    ];
    $('#portas').innerHTML = portas.map(function (p, i) {
      return '<a class="porta' + (p[3] ? ' principal' : '') + '" href="' + p[0] + '"><span class="num">' + (i + 1) + '</span><span><b>' + esc(p[1]) + '</b><small>' + esc(p[2]) + '</small></span><span class="seta" aria-hidden="true">→</span></a>';
    }).join('');

    var trilho = $('#trilho'), atualI = 0;
    var prog = el('li', 'prog'); prog.setAttribute('aria-hidden', 'true'); trilho.appendChild(prog);
    D.etapas.forEach(function (e) {
      var li = el('li'), b = el('a', 'no');
      b.href = 'funciona.html#' + e.id;
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
    marcar();
    if (!reduzir) setInterval(function () { atualI = (atualI + 1) % D.etapas.length; marcar(); }, 2800);
  }

  /* ---------- página: como funciona ---------- */
  if (pag === 'funciona') {
    var atual = 0, tocando = false, timer = null;
    var lista = $('#passos');
    D.etapas.forEach(function (e, i) {
      var li = el('li'), b = el('button', 'passo');
      b.type = 'button';
      b.innerHTML = '<span class="n">' + e.num + '</span><span class="t"><b>' + esc(e.nome) + '</b><small>' + esc(e.modulos.join(' · ')) + '</small></span>';
      b.addEventListener('click', function () { parar(); escolher(i); });
      li.appendChild(b); lista.appendChild(li);
    });

    var painelHtml = function (i) {
      var e = D.etapas[i];
      var h = '<div class="mods">' + e.modulos.map(function (m) { return '<span class="chip mod">' + esc(m) + '</span>'; }).join('') + '</div>';
      h += '<h3>' + esc(e.titulo) + '</h3><p class="pergunta">' + esc(e.pergunta) + '</p><p class="texto">' + esc(e.texto) + '</p>';
      h += '<div class="duas"><div class="bloco"><h4>O que o sistema faz</h4><ul class="faz">' + e.faz.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div>';
      h += '<div class="bloco"><h4>Ao final desta etapa</h4><p class="resultado">' + esc(e.resultado) + '</p><h4>Conecta com</h4><ul class="conecta">' + e.conecta.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div></div>';
      h += '<div class="fluxos"><h4>Fluxos do processo' + (e.fluxos.length ? ' · ' + e.fluxos.length : '') + '</h4>';
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
      h += '</div><div class="nav-painel">' +
        (i > 0 ? '<button class="btn" type="button" data-ir="' + (i - 1) + '">← ' + esc(D.etapas[i - 1].nome) + '</button>' : '<span></span>') +
        (i < D.etapas.length - 1 ? '<button class="btn primario" type="button" data-ir="' + (i + 1) + '">' + esc(D.etapas[i + 1].nome) + ' →</button>' : '<a class="btn primario" href="anvisa.html">Dentro das normas da ANVISA →</a>') + '</div>';
      return h;
    };

    var montarPainel = function () {
      var p = $('#painel'), novo = p.cloneNode(false);
      novo.innerHTML = painelHtml(atual);
      p.parentNode.replaceChild(novo, p);
      $$('.fcard', novo).forEach(function (c) {
        $('.fcab', c).addEventListener('click', function () {
          parar();
          var abrir = !c.classList.contains('aberto');
          $$('.fcard.aberto', novo).forEach(function (o) { o.classList.remove('aberto'); $('.fcab', o).setAttribute('aria-expanded', 'false'); });
          if (!abrir) return;
          var f = D.etapas[atual].fluxos[+c.getAttribute('data-k')];
          var corpo = $('.fcorpo', c);
          if (!corpo.firstChild) {
            corpo.innerHTML = '<div class="fbarra"><p class="dica"></p><button class="ampliar" type="button">⤢ Ampliar o fluxo</button></div>' + diagrama(f);
            $('.ampliar', corpo).addEventListener('click', function () { abrirZoom(f, D.etapas[atual].nome + ' · ' + f.linha); });
          }
          c.classList.add('aberto'); $('.fcab', c).setAttribute('aria-expanded', 'true');
          var dg = $('.diagrama', corpo), dica = $('.dica', corpo);
          dica.textContent = (dg.scrollWidth > dg.clientWidth + 4) ? 'Role para o lado ou amplie o fluxo para ver todas as fases.' : '';
        });
      });
      $$('[data-ir]', novo).forEach(function (b) {
        b.addEventListener('click', function () { parar(); escolher(+b.getAttribute('data-ir')); window.scrollTo({ top: 0, behavior: reduzir ? 'auto' : 'smooth' }); });
      });
    };

    var escolher = function (i) {
      atual = i;
      $$('.passo', lista).forEach(function (b, k) { b.classList.toggle('ativo', k === i); });
      montarPainel();
      if (history.replaceState) history.replaceState(null, '', '#' + D.etapas[i].id);
    };

    var btnTocar = $('#tocar');
    var parar = function () {
      tocando = false; clearInterval(timer); timer = null;
      btnTocar.setAttribute('aria-pressed', 'false'); $('#tocarIco').textContent = '▶'; $('#tocarTxt').textContent = 'Seguir o lote';
    };
    btnTocar.addEventListener('click', function () {
      if (tocando) { parar(); return; }
      if (atual === D.etapas.length - 1) escolher(0);
      tocando = true; btnTocar.setAttribute('aria-pressed', 'true'); $('#tocarIco').textContent = '❚❚'; $('#tocarTxt').textContent = 'Pausar';
      timer = setInterval(function () { escolher((atual + 1) % D.etapas.length); }, 5500);
    });

    var ini = 0, hash = location.hash.replace('#', '');
    D.etapas.forEach(function (e, i) { if (e.id === hash) ini = i; });
    escolher(ini);
  }

  /* ---------- página: normas da ANVISA ---------- */
  if (pag === 'anvisa') {
    var T2 = D.totais;
    $('#cobertura').innerHTML = '<div class="kpi"><b>' + T2.temas + '</b><span>exigências da norma, com a resposta do sistema</span></div>' +
      '<div class="kpi"><b>' + T2.grupos + '</b><span>grupos: do sistema computadorizado à rastreabilidade</span></div>' +
      '<div class="kpi"><b>' + T2.modulos + '</b><span>módulos trabalhando juntos</span></div>';
    var fg = -1, fil = $('#filtros');
    fil.innerHTML = '<button type="button" class="fchip on" data-g="-1">Todas</button>' + D.grupos.map(function (g, i) { return '<button type="button" class="fchip" data-g="' + i + '">' + esc(g) + '</button>'; }).join('');
    fil.addEventListener('click', function (ev) {
      var b = ev.target.closest('.fchip'); if (!b) return;
      fg = +b.getAttribute('data-g');
      $$('.fchip', fil).forEach(function (x) { x.classList.toggle('on', x === b); });
      desenhar();
    });
    var desenhar = function () {
      var box = $('#normas'); box.innerHTML = '';
      D.normas.forEach(function (n) {
        if (fg >= 0 && n.g !== fg) return;
        var c = el('article', 'tema');
        c.id = 'tema-' + n.id;
        c.innerHTML = '<div><h3>' + esc(n.tema) + '</h3><div class="norma">' + esc(n.norma) + ' · ' + esc(D.grupos[n.g]) + '</div></div>' +
          '<div><h5>Como o iLabPharma responde</h5><ul>' + n.resposta.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div>';
        box.appendChild(c);
      });
    };
    desenhar();
  }

  /* ---------- página: o que entregamos ---------- */
  if (pag === 'entrega') {
    var cenas = [{ intro: true }].concat(D.cenas);
    var box2 = $('#cenas'), pts = $('#pontos');
    var CORES2 = ['#ff7a00', '#3ea6ff', '#38d17a', '#9b7bff', '#ffc545', '#ff7a00', '#3ea6ff'];
    cenas.forEach(function (c, i) {
      var s = el('section', 'cena');
      s.style.setProperty('--cor', CORES2[i % CORES2.length]);
      s.style.setProperty('--gx', (20 + (i * 17) % 60) + '%'); s.style.setProperty('--gy', (30 + (i * 23) % 40) + '%');
      if (c.intro) {
        s.innerHTML = '<p class="kicker"><span class="ponto"></span>O que entregamos</p><div class="a">O que o <em>iLabPharma</em> entrega?</div><div class="apoio">Role para descobrir.</div><div class="rolar" aria-hidden="true">↓</div>';
      } else {
        var ultimo = i === cenas.length - 1;
        if (ultimo) s.classList.add('final');
        s.innerHTML = '<div class="a">' + c.a + '</div><div class="b">' + c.b + '</div><p class="apoio">' + esc(c.apoio) + '</p>' +
          '<div class="mods">' + c.modulos.map(function (m) { return '<span class="chip mod">' + esc(m) + '</span>'; }).join('') + '</div>' +
          (ultimo ? '<div class="mods"><a class="btn primario" href="funciona.html">Ver como funciona →</a><a class="btn" href="anvisa.html">Dentro das normas da ANVISA</a></div>' : '') +
          '<div class="num-cena" aria-hidden="true">' + String(i).padStart(2, '0') + '</div>';
      }
      box2.appendChild(s);
      var d = el('button'); d.type = 'button'; d.setAttribute('aria-label', 'Ir para a cena ' + (i + 1));
      d.addEventListener('click', function () { s.scrollIntoView({ behavior: reduzir ? 'auto' : 'smooth' }); });
      pts.appendChild(d);
    });
    var todas = $$('.cena'), bolas = $$('button', pts);
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (x) {
          if (x.isIntersecting) {
            x.target.classList.add('vis');
            var k = todas.indexOf(x.target);
            bolas.forEach(function (b, j) { b.classList.toggle('on', j === k); });
          }
        });
      }, { threshold: .55 });
      todas.forEach(function (s) { io.observe(s); });
    } else { todas.forEach(function (s) { s.classList.add('vis'); }); }
    todas[0].classList.add('vis'); bolas[0].classList.add('on');
  }
})();
