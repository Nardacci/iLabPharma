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
  // Referências às normas. Três origens, uma só janela:
  //  1. links de tabela para um título da mesma página (#tema-N-...): o conteúdo daquela seção;
  //  2. toda menção a um artigo da RDC 658/2022 ("art. 157", "arts. 39 a 46", "art. 8º, XV") ou a um
  //     item do Guia 33/2020 ("Guia 33, 9.3.2.3") no texto: o artigo ou a seção, de portal/normas.json;
  //  3. os números da coluna "Trava" das páginas "O ideal": a trava do modelo ideal, com a norma.
  var area = document.querySelector('article.texto');
  if (area && typeof HTMLDialogElement === 'function') {
    var janela = null, normas = null, carregandoNormas = null;
    function getJanela() {
      if (janela) return janela;
      janela = document.createElement('dialog');
      janela.className = 'janela-ref';
      janela.innerHTML = '<div class="janela-topo"><strong></strong><button type="button" class="janela-fechar" aria-label="Fechar">×</button></div><div class="janela-corpo"></div><a class="janela-link" href="#">Ver no fim da página</a>';
      document.body.appendChild(janela);
      janela.querySelector('.janela-fechar').addEventListener('click', function () { janela.close(); });
      janela.addEventListener('click', function (e) { if (e.target === janela) janela.close(); });
      janela.querySelector('.janela-link').addEventListener('click', function () { janela.close(); });
      return janela;
    }
    function abrir(titulo, corpoNos, href) {
      var j = getJanela(), corpo = j.querySelector('.janela-corpo');
      corpo.innerHTML = '';
      corpoNos.forEach(function (n) { corpo.appendChild(n); });
      j.querySelector('strong').textContent = titulo;
      var link = j.querySelector('.janela-link');
      if (href) { link.hidden = false; link.setAttribute('href', href); } else { link.hidden = true; }
      j.showModal();
      corpo.scrollTop = 0;
      var d = corpo.querySelector('.destaque');
      if (d) d.scrollIntoView({ block: 'center' });
    }
    function el(tag, texto, cls) { var e = document.createElement(tag); if (texto != null) e.textContent = texto; if (cls) e.className = cls; return e; }
    function carregarNormas(cb) {
      if (normas) return cb(normas);
      if (!carregandoNormas) {
        carregandoNormas = fetch(raiz + 'portal/normas.json').then(function (r) { return r.json(); })
          .then(function (d) { normas = d; return d; }).catch(function () { normas = {}; return normas; });
      }
      carregandoNormas.then(cb);
    }
    function mostrarRdc(art, inc) {
      carregarNormas(function (d) {
        var pars = d.rdc && d.rdc[art];
        var titulo = 'RDC 658/2022, art. ' + art + (Number(art) < 10 ? 'º' : '');
        if (!pars) return abrir(titulo, [el('p', 'Texto não encontrado no índice das normas.')], null);
        var incs = (inc || '').split(/\s*(?:,|e)\s*/).filter(Boolean);
        var nos = [];
        pars.forEach(function (p) {
          var bq = document.createElement('blockquote'); bq.appendChild(el('p', p));
          var marca = incs.some(function (x) {
            if (/^§/.test(x)) return new RegExp('^§\\s*' + x.replace(/^§\s*/, '').replace(/[º°]/, '') + '[º°]?').test(p);
            return new RegExp('^' + x + '\\s?-').test(p);
          });
          if (marca) bq.className = 'destaque';
          nos.push(bq);
        });
        if (incs.length) nos.unshift(el('p', 'Em destaque: ' + incs.join(', ') + '.', 'janela-nota'));
        abrir(titulo, nos, null);
      });
    }
    function mostrarGuia(sec) {
      carregarNormas(function (d) {
        var g = d.guia && d.guia[sec];
        var titulo = 'Guia nº 33/2020, item ' + sec + (g && g.titulo ? ' (' + g.titulo + ')' : '');
        if (!g) return abrir(titulo, [el('p', 'Texto não encontrado no índice das normas.')], null);
        var nos = [];
        g.itens.forEach(function (it) {
          var bq = document.createElement('blockquote'); bq.appendChild(el('p', it.cab));
          if (it.subs.length) { var ul = document.createElement('ul'); it.subs.forEach(function (x) { ul.appendChild(el('li', x)); }); bq.appendChild(ul); }
          nos.push(bq);
        });
        abrir(titulo, nos, null);
      });
    }
    function mostrarTrava(n) {
      carregarNormas(function (d) {
        var t = d.travas && d.travas[n];
        var titulo = 'Trava ' + n + (t && t.titulo ? ' · ' + t.titulo : '');
        if (!t) return abrir(titulo, [el('p', 'Trava não encontrada no índice.')], null);
        var div = document.createElement('div'); div.innerHTML = t.html;
        var nos = [el('p', 'Do documento "Qualidade entre os módulos: situação do lote e travas" (Visão entre módulos).', 'janela-nota')];
        Array.prototype.slice.call(div.childNodes).forEach(function (n2) { nos.push(n2); });
        abrir(titulo, nos, null);
      });
    }
    function ligar(a, tipo, valor, extra) {
      a.classList.add('ref-norma');
      a.title = 'Ver o que a norma diz';
      a.setAttribute('href', '#');
      a.addEventListener('click', function (e) {
        e.preventDefault();
        if (tipo === 'rdc') mostrarRdc(valor, extra);
        else if (tipo === 'guia') mostrarGuia(valor);
        else mostrarTrava(valor);
      });
      return a;
    }
    // 1. Links para um título da mesma página
    area.querySelectorAll('td a[href^="#tema-"], td a[href^="#trava-"]').forEach(function (a) {
      var alvo = document.getElementById(a.getAttribute('href').slice(1));
      if (!alvo || !/^H[2-4]$/.test(alvo.tagName)) return;
      a.classList.add('ref-norma');
      a.title = 'Ver o que a norma diz';
      a.addEventListener('click', function (e) {
        e.preventDefault();
        var nivel = Number(alvo.tagName[1]), nos = [];
        for (var x = alvo.nextElementSibling; x; x = x.nextElementSibling) {
          if (/^H[1-6]$/.test(x.tagName) && Number(x.tagName[1]) <= nivel) break;
          nos.push(x.cloneNode(true));
        }
        abrir(alvo.textContent, nos, '#' + alvo.id);
      });
    });
    // 2. Artigos e itens citados no texto
    var reRdc = /\b([Aa]rts?\.\s?)(\d+[º°o]?(?:\s*(?:,|e|a)\s*\d+[º°o]?)*)(,\s*((?:§\s*\d+[º°]?|[IVXLC]+)(?:\s*(?:,|e)\s*(?:§\s*\d+[º°]?|[IVXLC]+))*)(?=[\s,;.)]|$))?/g;
    var reGuia = /\b(Guia(?:\s*n[º°o]?\.?)?\s*33(?:\/2020)?,?\s*(?:ite(?:m|ns)\s*)?)(\d+(?:\.\d+)+(?:\s*(?:,|e)\s*\d+(?:\.\d+)+)*)/g;
    function pedacosGuia(texto, frag) {
      var ult = 0, m;
      reGuia.lastIndex = 0;
      while ((m = reGuia.exec(texto))) {
        frag.appendChild(document.createTextNode(texto.slice(ult, m.index) + m[1]));
        m[2].split(/(\s*(?:,|e)\s*)/).forEach(function (tok) {
          if (/^\d+(\.\d+)+$/.test(tok)) frag.appendChild(ligar(el('a', tok), 'guia', tok));
          else if (tok) frag.appendChild(document.createTextNode(tok));
        });
        ult = m.index + m[0].length;
      }
      frag.appendChild(document.createTextNode(texto.slice(ult)));
    }
    function processar(no) {
      var texto = no.nodeValue;
      reRdc.lastIndex = 0; reGuia.lastIndex = 0;
      if (!reRdc.test(texto) && !reGuia.test(texto)) return;
      var frag = document.createDocumentFragment(), ult = 0, m;
      reRdc.lastIndex = 0;
      while ((m = reRdc.exec(texto))) {
        pedacosGuia(texto.slice(ult, m.index), frag);
        frag.appendChild(document.createTextNode(m[1]));
        var nums = m[2].split(/(\s*(?:,|e|a)\s*)/), inc = m[4] || '';
        var ultimo = -1;
        nums.forEach(function (tok, k) { if (/^\d+[º°o]?$/.test(tok)) ultimo = k; });
        nums.forEach(function (tok, k) {
          if (/^\d+[º°o]?$/.test(tok)) frag.appendChild(ligar(el('a', tok), 'rdc', tok.replace(/[º°o]$/, ''), k === ultimo ? inc : ''));
          else if (tok) frag.appendChild(document.createTextNode(tok));
        });
        if (m[3]) frag.appendChild(document.createTextNode(m[3]));
        ult = m.index + m[0].length;
      }
      pedacosGuia(texto.slice(ult), frag);
      no.parentNode.replaceChild(frag, no);
    }
    var walker = document.createTreeWalker(area, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        var p = n.parentNode;
        if (!p || !n.nodeValue || n.nodeValue.length < 6) return NodeFilter.FILTER_REJECT;
        if (p.closest('a, blockquote, h1, h2, h3, h4, h5, h6, code, pre, dialog, nav')) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var nos = [], n;
    while ((n = walker.nextNode())) nos.push(n);
    nos.forEach(processar);
    // 3. Coluna "Trava" das páginas "O ideal"
    area.querySelectorAll('table').forEach(function (tb) {
      var ths = tb.querySelectorAll('thead th, tr:first-child th');
      ths.forEach(function (th, idx) {
        if (!/^travas?$/i.test(th.textContent.trim())) return;
        tb.querySelectorAll('tbody tr, tr').forEach(function (tr) {
          var td = tr.children[idx];
          if (!td || td.tagName !== 'TD' || td.querySelector('a')) return;
          var texto = td.textContent, frag = document.createDocumentFragment();
          if (!/\d/.test(texto)) return;
          texto.split(/(\d+)/).forEach(function (tok) {
            if (/^\d+$/.test(tok)) frag.appendChild(ligar(el('a', tok), 'trava', tok));
            else if (tok) frag.appendChild(document.createTextNode(tok));
          });
          td.innerHTML = ''; td.appendChild(frag);
        });
      });
    });
  }
})();
