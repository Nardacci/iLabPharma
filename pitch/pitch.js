(function () {
  'use strict';
  var D = window.DADOS;
  if (!D) { return; }
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var el = function (tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var reduzir = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var CORES = ['#ff7a00', '#3ea6ff', '#38d17a', '#9b7bff', '#ffc545'];

  var atual = 0;
  var tocando = false, timer = null;

  /* ---------- números do hero ---------- */
  var T = D.totais;
  var nums = $('#numeros');
  [[T.modulos, 'módulos integrados'], [T.fluxos, 'fluxos de processo mapeados'], [T.temas, 'pontos da RDC 658/2022 e do Guia 33/2020 avaliados']].forEach(function (n) {
    var d = el('div', null, '<dt data-alvo="' + n[0] + '">0</dt><dd>' + n[1] + '</dd>');
    nums.appendChild(d);
  });

  function contar(e) {
    var alvo = +e.getAttribute('data-alvo');
    if (reduzir) { e.textContent = alvo; return; }
    var t0 = null;
    function passo(t) {
      if (!t0) t0 = t;
      var p = Math.min((t - t0) / 1100, 1);
      e.textContent = Math.round(alvo * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(passo);
    }
    requestAnimationFrame(passo);
  }
  document.querySelectorAll('#numeros dt').forEach(contar);

  /* ---------- trilho do lote (hero) ---------- */
  var trilho = $('#trilho');
  var prog = el('li', 'prog'); prog.setAttribute('aria-hidden', 'true');
  trilho.appendChild(prog);
  D.etapas.forEach(function (e, i) {
    var li = el('li');
    var b = el('button', 'no');
    b.type = 'button';
    b.innerHTML = '<span class="bola">' + e.num + '</span><span class="rot">' + esc(e.nome) + '<small>' + esc(e.modulos.join(' · ')) + '</small></span>';
    b.addEventListener('click', function () { parar(); escolher(i, true); });
    li.appendChild(b);
    trilho.appendChild(li);
  });

  function atualizarTrilho() {
    var nos = trilho.querySelectorAll('.no');
    nos.forEach(function (n, i) {
      n.classList.toggle('ativo', i === atual);
      n.classList.toggle('feito', i < atual);
    });
    var n = D.etapas.length;
    var nos0 = trilho.querySelectorAll('.no');
    var topo0 = nos0[0].offsetTop + 22, alvo0 = nos0[atual].offsetTop + 22;
    prog.style.height = (alvo0 - topo0) + 'px';
    var e = D.etapas[atual];
    $('#trilhoCard').innerHTML = '<span class="mod">' + esc(e.modulos.join(' + ')) + '</span><b>' + esc(e.nome) + '</b><span>' + esc(e.titulo) + '</span>';
  }

  /* ---------- como funciona ---------- */
  var lista = $('#passos');
  D.etapas.forEach(function (e, i) {
    var li = el('li');
    var b = el('button', 'passo');
    b.type = 'button';
    b.innerHTML = '<span class="n">' + e.num + '</span><span class="t"><b>' + esc(e.nome) + '</b><small>' + esc(e.modulos.join(' · ')) + '</small></span>';
    b.addEventListener('click', function () { parar(); escolher(i, false); });
    li.appendChild(b);
    lista.appendChild(li);
  });

  function diagrama(f) {
    var h = '<div class="diagrama">';
    f.fases.forEach(function (fase, i) {
      var cor = CORES[i % CORES.length];
      h += '<div class="fase" style="--cor:' + cor + '"><div class="fase-cab"><i>' + (i + 1) + '</i>' + esc(fase.nome) + '</div><div class="fase-passos">';
      fase.etapas.forEach(function (p) { h += '<div class="fp' + (p.dec ? ' dec' : '') + '">' + esc(p.t) + '</div>'; });
      h += '</div></div>';
    });
    return h + '</div>';
  }

  function painel(i) {
    var e = D.etapas[i];
    var h = '<div class="mods">' + e.modulos.map(function (m) { return '<span class="chip mod">' + esc(m) + '</span>'; }).join('') + '</div>';
    h += '<h3>' + esc(e.titulo) + '</h3>';
    h += '<p class="pergunta">' + esc(e.pergunta) + '</p><p class="texto">' + esc(e.texto) + '</p>';
    h += '<div class="duas"><div class="bloco"><h4>O que o sistema faz</h4><ul class="faz">' + e.faz.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div>';
    h += '<div class="bloco"><h4>Ao final desta etapa</h4><p class="resultado">' + esc(e.resultado) + '</p><h4>Conecta com</h4><ul class="conecta">' + e.conecta.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div></div>';
    h += '<div class="fluxos"><h4>Fluxos do processo' + (e.fluxos.length ? ' · ' + e.fluxos.length : '') + '</h4>';
    if (e.fluxos.length) {
      h += '<div class="fluxo-lista">';
      e.fluxos.forEach(function (f, k) {
        h += '<div class="fcard" data-k="' + k + '"><button class="fcab" type="button" aria-expanded="false"><span class="ft"><b>' + esc(f.nome) + '</b><small>' + esc(f.linha) + '</small></span><span class="seta" aria-hidden="true">⌄</span></button><div class="fcorpo"></div></div>';
      });
      h += '</div>';
    } else {
      h += '<p class="vazio">Os cadastros do Principal sustentam todos os fluxos dos outros módulos.</p>';
    }
    if (e.imagem) h += '<p class="vermais"><a href="' + e.imagem[0] + '" target="_blank" rel="noopener">' + esc(e.imagem[1]) + ' <span aria-hidden="true">↗</span></a></p>';
    h += '</div>';
    h += '<div class="nav-painel">' + (i > 0 ? '<button class="btn" type="button" data-ir="' + (i - 1) + '">← ' + esc(D.etapas[i - 1].nome) + '</button>' : '<span></span>') + (i < D.etapas.length - 1 ? '<button class="btn primario" type="button" data-ir="' + (i + 1) + '">' + esc(D.etapas[i + 1].nome) + ' →</button>' : '<a class="btn primario" href="#anvisa">Ver a aderência à ANVISA →</a>') + '</div>';
    return h;
  }

  function montarPainel() {
    var p = $('#painel');
    var novo = p.cloneNode(false);
    novo.innerHTML = painel(atual);
    p.parentNode.replaceChild(novo, p);
    novo.querySelectorAll('.fcard').forEach(function (c) {
      c.querySelector('.fcab').addEventListener('click', function () {
        parar();
        var abrir = !c.classList.contains('aberto');
        novo.querySelectorAll('.fcard.aberto').forEach(function (o) { o.classList.remove('aberto'); o.querySelector('.fcab').setAttribute('aria-expanded', 'false'); });
        if (abrir) {
          var corpo = c.querySelector('.fcorpo');
          if (!corpo.firstChild) corpo.innerHTML = diagrama(D.etapas[atual].fluxos[+c.getAttribute('data-k')]);
          c.classList.add('aberto'); c.querySelector('.fcab').setAttribute('aria-expanded', 'true');
          var dg = corpo.querySelector('.diagrama');
          if (dg && dg.scrollWidth > dg.clientWidth + 4 && !corpo.querySelector('.dica')) { corpo.appendChild(el('p', 'dica', 'Role para o lado para ver todas as fases →')); }
        }
      });
    });
    novo.querySelectorAll('[data-ir]').forEach(function (b) {
      b.addEventListener('click', function () { parar(); escolher(+b.getAttribute('data-ir'), false); rolarPara('#funciona'); });
    });
  }

  function escolher(i, rolar) {
    atual = i;
    lista.querySelectorAll('.passo').forEach(function (b, k) { b.classList.toggle('ativo', k === i); });
    atualizarTrilho();
    montarPainel();
    if (rolar) rolarPara('#funciona');
  }

  function rolarPara(sel) {
    var alvo = $(sel);
    if (alvo) alvo.scrollIntoView({ behavior: reduzir ? 'auto' : 'smooth', block: 'start' });
  }

  /* ---------- seguir o lote (automático) ---------- */
  var btnTocar = $('#tocar');
  function parar() {
    tocando = false; clearInterval(timer); timer = null;
    btnTocar.setAttribute('aria-pressed', 'false');
    $('#tocarIco').textContent = '▶'; $('#tocarTxt').textContent = 'Seguir o lote';
  }
  function tocar() {
    tocando = true;
    btnTocar.setAttribute('aria-pressed', 'true');
    $('#tocarIco').textContent = '❚❚'; $('#tocarTxt').textContent = 'Pausar';
    timer = setInterval(function () {
      escolher((atual + 1) % D.etapas.length, false);
    }, 5500);
  }
  btnTocar.addEventListener('click', function () {
    if (tocando) { parar(); return; }
    if (atual === D.etapas.length - 1) escolher(0, false);
    tocar();
  });

  /* ---------- normas ---------- */
  var cob = $('#cobertura');
  cob.innerHTML = '<div class="kpi"><b>' + T.temas + '</b><span>pontos da norma avaliados, nos sete grupos abaixo</span></div>' +
    '<div class="kpi b"><b>' + T.base + '</b><span>com base pronta: a função já existe no iLabPharma</span></div>' +
    '<div class="kpi e"><b>' + T.entrega + '</b><span>serão entregues no plano de evolução</span></div>' +
    '<div class="barra" role="img" aria-label="' + T.base + ' pontos com base pronta e ' + T.entrega + ' a entregar"><i class="b" data-w="' + (T.base / T.temas * 100) + '"></i><i class="e" data-w="' + (T.entrega / T.temas * 100) + '"></i></div>';

  var filtroGrupo = -1, filtroNivel = '';
  var fil = $('#filtros');
  var gHtml = '<div class="grupo-chips" role="group" aria-label="Grupo"><button type="button" class="fchip on" data-g="-1">Todos os grupos</button>' +
    D.grupos.map(function (g, i) { return '<button type="button" class="fchip" data-g="' + i + '">' + esc(g) + '</button>'; }).join('') + '</div>';
  var nHtml = '<div class="nivel-chips" role="group" aria-label="Situação"><button type="button" class="fchip on" data-n="">Todos</button><button type="button" class="fchip" data-n="base">Base pronta</button><button type="button" class="fchip" data-n="entrega">Será entregue</button></div>';
  fil.innerHTML = gHtml + nHtml;
  fil.addEventListener('click', function (ev) {
    var b = ev.target.closest('.fchip'); if (!b) return;
    if (b.hasAttribute('data-g')) {
      filtroGrupo = +b.getAttribute('data-g');
      fil.querySelectorAll('[data-g]').forEach(function (x) { x.classList.toggle('on', x === b); });
    } else {
      filtroNivel = b.getAttribute('data-n');
      fil.querySelectorAll('[data-n]').forEach(function (x) { x.classList.toggle('on', x === b); x.classList.remove('b', 'e'); });
      if (filtroNivel) b.classList.add(filtroNivel === 'base' ? 'b' : 'e');
    }
    desenharNormas();
  });

  function desenharNormas() {
    var box = $('#normas'); box.innerHTML = '';
    var qtd = 0;
    D.normas.forEach(function (n) {
      if (filtroGrupo >= 0 && n.g !== filtroGrupo) return;
      if (filtroNivel && n.nivel !== filtroNivel) return;
      qtd++;
      var c = el('article', 'tema ' + (n.nivel === 'base' ? 'b' : 'e'));
      c.id = 'tema-' + n.id;
      c.innerHTML = '<div class="tema-cab"><div><h3>' + esc(n.tema) + '</h3><div class="norma">' + esc(n.norma) + ' · ' + esc(D.grupos[n.g]) + '</div></div><span class="selo">' + (n.nivel === 'base' ? 'Base pronta' : 'Será entregue') + '</span></div>' +
        '<div class="ja"><h5>Já no iLabPharma</h5>' + (n.ja.length ? '<ul>' + n.ja.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>' : '<p class="vazio">Em construção.</p>') + '</div>' +
        '<div class="entrega"><h5>Próxima entrega</h5><ul>' + n.entrega.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul></div>';
      box.appendChild(c);
    });
    if (!qtd) box.appendChild(el('p', 'vazio', 'Nenhum ponto nesta combinação.'));
  }

  /* ---------- evolução ---------- */
  var porId = {}; D.normas.forEach(function (n) { porId[n.id] = n; });
  var fr = $('#frentes');
  D.frentes.forEach(function (f) {
    var li = el('li', 'frente reveal');
    var tags = f.temas.filter(function (t) { return porId[t]; }).map(function (t) {
      return '<a class="tag" href="#tema-' + t + '" data-tema="' + t + '">' + esc(porId[t].tema) + '</a>';
    }).join('');
    li.innerHTML = '<div class="num">' + f.n + '</div><div class="cartao"><h3>' + esc(f.titulo) + '</h3><p>' + esc(f.texto) + '</p><div class="tags">' + tags + '</div></div>';
    fr.appendChild(li);
  });
  fr.addEventListener('click', function (ev) {
    var a = ev.target.closest('[data-tema]'); if (!a) return;
    ev.preventDefault();
    // garante que o card esteja visível, limpando os filtros
    filtroGrupo = -1; filtroNivel = '';
    fil.querySelectorAll('.fchip').forEach(function (x) { x.classList.remove('on', 'b', 'e'); });
    fil.querySelector('[data-g="-1"]').classList.add('on'); fil.querySelector('[data-n=""]').classList.add('on');
    desenharNormas();
    var c = document.getElementById('tema-' + a.getAttribute('data-tema'));
    if (c) {
      c.scrollIntoView({ behavior: reduzir ? 'auto' : 'smooth', block: 'center' });
      c.classList.add('destaque'); setTimeout(function () { c.classList.remove('destaque'); }, 2400);
    }
  });

  /* ---------- revelar ao rolar, topo e menu ---------- */
  var io = ('IntersectionObserver' in window) ? new IntersectionObserver(function (es) {
    es.forEach(function (x) {
      if (x.isIntersecting) {
        x.target.classList.add('vis'); io.unobserve(x.target);
        if (x.target.id === 'cobertura') x.target.querySelectorAll('.barra i').forEach(function (i) { i.style.width = i.getAttribute('data-w') + '%'; });
      }
    });
  }, { threshold: .12 }) : null;
  document.querySelectorAll('.reveal').forEach(function (e) {
    if (io) io.observe(e); else { e.classList.add('vis'); if (e.id === 'cobertura') e.querySelectorAll('.barra i').forEach(function (i) { i.style.width = i.getAttribute('data-w') + '%'; }); }
  });

  var topo = $('#topo');
  window.addEventListener('scroll', function () { topo.classList.toggle('rolou', window.scrollY > 24); }, { passive: true });
  var links = document.querySelectorAll('.topo nav a');
  if (io) {
    var sec = new IntersectionObserver(function (es) {
      es.forEach(function (x) {
        if (x.isIntersecting) links.forEach(function (a) { a.classList.toggle('ativo', a.getAttribute('href') === '#' + x.target.id); });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    ['funciona', 'anvisa', 'evolucao'].forEach(function (id) { sec.observe(document.getElementById(id)); });
  }

  /* ---------- início ---------- */
  escolher(0, false);
  desenharNormas();
  // o trilho do hero anda sozinho até o usuário interagir
  if (!reduzir) {
    var auto = setInterval(function () {
      if (window.scrollY > window.innerHeight * .6 || tocando) { return; }
      escolher((atual + 1) % D.etapas.length, false);
    }, 2800);
    ['click', 'wheel', 'touchstart', 'keydown'].forEach(function (ev) { window.addEventListener(ev, function () { clearInterval(auto); }, { once: true, passive: true }); });
  }
})();
