// iLabMedSys: busca na documentação, tema claro/escuro e destaque do item atual no "Nesta página".
(function () {
  var raiz = document.body.getAttribute('data-raiz') || '';

  // Tema
  var botaoTema = document.getElementById('tema');
  if (botaoTema) {
    botaoTema.addEventListener('click', function () {
      var atual = document.documentElement.dataset.theme ||
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
      var novo = atual === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = novo;
      try { localStorage.setItem('ilms-tema', novo); } catch (e) {}
    });
  }

  // Busca
  var campo = document.getElementById('busca');
  var caixa = document.getElementById('busca-resultados');
  var indice = null, carregando = null, ativo = -1;

  function semAcento(s) { return (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function carregar() {
    if (indice) return Promise.resolve(indice);
    if (!carregando) {
      carregando = fetch(raiz + 'portal/busca.json').then(function (r) { return r.json(); })
        .then(function (d) {
          indice = d.map(function (x) {
            return Object.assign(x, { _t: semAcento(x.t), _h: semAcento(x.h.join(' | ')), _x: semAcento(x.x) });
          });
          return indice;
        });
    }
    return carregando;
  }

  function trecho(doc, termos) {
    var t = semAcento(doc.x), i = -1;
    for (var k = 0; k < termos.length && i < 0; k++) i = t.indexOf(termos[k]);
    if (i < 0) return '';
    var ini = Math.max(0, i - 60), s = doc.x.slice(ini, i + 120);
    var h = esc((ini > 0 ? '…' : '') + s + '…');
    termos.forEach(function (te) {
      if (te.length < 3) return;
      h = h.replace(new RegExp('(' + te.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi'), '<mark>$1</mark>');
    });
    return h;
  }

  function buscar(q) {
    var termos = semAcento(q).split(/\s+/).filter(Boolean);
    if (!termos.length) { caixa.hidden = true; return; }
    carregar().then(function (docs) {
      var res = docs.map(function (d) {
        var p = 0;
        for (var k = 0; k < termos.length; k++) {
          var te = termos[k], pk = 0;
          if (d._t.indexOf(te) >= 0) pk += 10;
          if (d._h.indexOf(te) >= 0) pk += 4;
          if (d._x.indexOf(te) >= 0) pk += 1 + Math.min(3, d._x.split(te).length - 2);
          if (!pk) return null;
          p += pk;
        }
        return { d: d, p: p };
      }).filter(Boolean).sort(function (a, b) { return b.p - a.p; }).slice(0, 12);
      ativo = -1;
      if (!res.length) {
        caixa.innerHTML = '<div class="busca-vazia">Nada encontrado para “' + esc(q) + '”.</div>';
      } else {
        caixa.innerHTML = res.map(function (r) {
          return '<a href="' + raiz + r.d.u + '"><strong>' + esc(r.d.t) + '</strong><small>' + esc(r.d.m) + '</small>' +
            '<div><small>' + trecho(r.d, termos) + '</small></div></a>';
        }).join('');
      }
      caixa.hidden = false;
    });
  }

  if (campo && caixa) {
    var espera;
    campo.addEventListener('input', function () { clearTimeout(espera); espera = setTimeout(function () { buscar(campo.value); }, 120); });
    campo.addEventListener('focus', function () { carregar(); if (campo.value) buscar(campo.value); });
    campo.addEventListener('keydown', function (e) {
      var itens = caixa.querySelectorAll('a');
      if (e.key === 'Escape') { caixa.hidden = true; campo.blur(); }
      else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        if (!itens.length) return;
        e.preventDefault();
        ativo = (ativo + (e.key === 'ArrowDown' ? 1 : -1) + itens.length) % itens.length;
        itens.forEach(function (a, i) { a.classList.toggle('ativo', i === ativo); });
      } else if (e.key === 'Enter' && itens.length) {
        window.location.href = itens[Math.max(ativo, 0)].href;
      }
    });
    document.addEventListener('click', function (e) { if (!caixa.contains(e.target) && e.target !== campo) caixa.hidden = true; });
    document.addEventListener('keydown', function (e) {
      if ((e.key === 'k' && (e.ctrlKey || e.metaKey)) || (e.key === '/' && document.activeElement.tagName !== 'INPUT')) {
        e.preventDefault(); campo.focus();
      }
    });
  }

  // "Nesta página": destaca a seção visível
  var links = document.querySelectorAll('.toc a');
  if (links.length && 'IntersectionObserver' in window) {
    var mapa = {};
    links.forEach(function (a) { mapa[a.getAttribute('href').slice(1)] = a; });
    var obs = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (en) {
        if (en.isIntersecting && mapa[en.target.id]) {
          links.forEach(function (a) { a.classList.remove('ativo'); });
          mapa[en.target.id].classList.add('ativo');
        }
      });
    }, { rootMargin: '-80px 0px -70% 0px' });
    Object.keys(mapa).forEach(function (id) { var el = document.getElementById(id); if (el) obs.observe(el); });
  }
  // Links de tabela para um título da mesma página (ex.: referência da norma no diagnóstico):
  // abrem o conteúdo daquela seção numa janela, sem sair da tabela.
  var refs = document.querySelectorAll('article.texto td a[href^="#tema-"]');
  if (refs.length && typeof HTMLDialogElement === 'function') {
    var janela = document.createElement('dialog');
    janela.className = 'janela-ref';
    janela.innerHTML = '<div class="janela-topo"><strong></strong><button type="button" class="janela-fechar" aria-label="Fechar">×</button></div><div class="janela-corpo"></div><a class="janela-link" href="#">Ver no fim da página</a>';
    document.body.appendChild(janela);
    janela.querySelector('.janela-fechar').addEventListener('click', function () { janela.close(); });
    janela.addEventListener('click', function (e) { if (e.target === janela) janela.close(); });
    janela.querySelector('.janela-link').addEventListener('click', function () { janela.close(); });
    refs.forEach(function (a) {
      var alvo = document.getElementById(a.getAttribute('href').slice(1));
      if (!alvo || !/^H[2-4]$/.test(alvo.tagName)) return;
      a.classList.add('ref-norma');
      a.title = 'Ver o que a norma diz';
      a.addEventListener('click', function (e) {
        e.preventDefault();
        var corpo = janela.querySelector('.janela-corpo');
        corpo.innerHTML = '';
        var nivel = Number(alvo.tagName[1]);
        for (var el = alvo.nextElementSibling; el; el = el.nextElementSibling) {
          if (/^H[1-6]$/.test(el.tagName) && Number(el.tagName[1]) <= nivel) break;
          corpo.appendChild(el.cloneNode(true));
        }
        janela.querySelector('strong').textContent = alvo.textContent;
        janela.querySelector('.janela-link').setAttribute('href', '#' + alvo.id);
        janela.showModal();
      });
    });
  }
})();
