"""Versão nova: rotas próprias, seletor "Legado | Novo" e páginas por tela.

Decisão do responsável: legado e versão nova não aparecem juntos. A versão nova tem as mesmas abas por tela do legado
(Análise, Manual do usuário, Fluxos, Regras de negócio, Anvisa, Passo a passo e Ideal) com conteúdo próprio, em rotas
próprias:

    legado  documentacao/<módulo>/<tela>-<aba>.html          (já publicadas; não mudam)
    novo    documentacao/novo/<módulo>/<tela>-<aba>.html     (este arquivo)

A lista de telas de cada módulo vem do inventário de telas do legado (é o mesmo sistema). Tela que ainda não tem teste nem
documento na versão nova aparece mesmo assim, com o aviso "ainda não validada nesta versão"; nada é copiado do legado.
O Ideal é um só, comum às duas versões: a aba Ideal leva à página do ideal do módulo.

Hoje só o Principal tem conteúdo (homologacao/versao-nova/1.principal/): resumo da tela, passo a passo e o manual por tela
(Manual, Regras de negócio, Integração, Erros, Onde melhorar). O texto passa pelo mesmo filtro das demais páginas
(higiene.redigir): endereços IP, senhas e logins fora da lista não saem."""
import html
import json
import re
import unicodedata
from pathlib import Path

import telas_devs

E = html.escape

# aba (rota) -> (rótulo, aba equivalente no legado)
ABAS = [("analise", "Análise", "analise"), ("manual-do-usuario", "Manual do usuário", "manual"), ("fluxos", "Fluxos", "fluxos"),
        ("regras-de-negocio", "Regras de negócio", "regras"), ("anvisa", "Anvisa", "anvisa"), ("passo-a-passo", "Passo a passo", None)]
ABA_DO_LEGADO = {leg: chave for chave, _r, leg in ABAS if leg}

PRINCIPAL = "versao-nova/1.principal"


def _slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def chave_tela(nome):
    return telas_devs._norm(re.sub(r"\s*\(.*?\)", "", nome))


def registro(hom):
    """{módulo: {"menus": [(menu, [tela])], "telas": [tela]}} a partir dos inventários de telas do legado.
    tela = {nome, menu, slug, chave, abas: {aba: html|None}, validada, situacao}."""
    reg = {}
    for mid, pasta in telas_devs.DIRS.items():
        usados, menus, telas = set(), {}, []
        for menu, nome, _sit in telas_devs.ler_inventario(Path(hom) / pasta / "11-inventario-de-telas.md"):
            s = _slug(nome)
            if s in usados:
                s = f"{s}-{_slug(menu)}"
            usados.add(s)
            t = {"nome": nome, "menu": menu, "slug": s, "chave": chave_tela(nome), "abas": {a[0]: None for a in ABAS}, "validada": False, "situacao": ""}
            menus.setdefault(menu, []).append(t)
            telas.append(t)
        reg[mid] = {"menus": list(menus.items()), "telas": telas}
    return reg


def _manual_por_tela(md):
    """{chave da tela: {1..5: texto}} a partir de '## Tela' e '### N. Rótulo: Tela' do manual da versão nova."""
    out, tela, n, buf = {}, None, None, []

    def fecha():
        if tela and n:
            out.setdefault(tela, {})[n] = "\n".join(buf).strip()
    for l in md.splitlines():
        if re.match(r"^# ", l):
            fecha(); tela, n, buf = None, None, []
            continue
        m = re.match(r"^## (.+?)\s*$", l)
        if m:
            fecha(); tela, n, buf = chave_tela(m.group(1)), None, []
            continue
        m = re.match(r"^### (\d)\. ", l)
        if m and tela:
            fecha(); n, buf = int(m.group(1)), []
            continue
        if n:
            buf.append(l)
    fecha()
    return out


def preencher_principal(reg, hom, limpar, converter):
    """Lê homologacao/versao-nova/1.principal/ e põe o conteúdo nas telas do Principal. `limpar(md)` e `converter(md)` vêm do gerador."""
    base = Path(hom) / PRINCIPAL
    arq_man = base / "telas/manifest.json"
    if not arq_man.exists():
        return
    man = json.loads(arq_man.read_text(encoding="utf-8"))
    manual = {}
    arq_manual = base / "manual/manual-principal-versao-nova.md"
    if arq_manual.exists():
        manual = _manual_por_tela(arq_manual.read_text(encoding="utf-8"))
    por_chave = {t["chave"]: t for t in reg["principal"]["telas"]}

    def html_de(md, tirar_h1=False):
        md = limpar(md)
        if not tirar_h1:
            md = "# x\n" + md  # o conversor descarta a primeira linha de título
        corpo = converter(md)
        # a página fica em documentacao/novo/<módulo>/: as imagens sobem mais um nível
        return corpo.replace('"../img/', '"../../img/')

    for m in man:
        if not m.get("grupo"):
            continue
        t = por_chave.get(chave_tela(m["tela"]))
        if not t:
            continue
        txt = (base.parent.parent / m["arq"]).read_text(encoding="utf-8")
        t["situacao"] = m.get("situacao") or t["situacao"]
        if m.get("rotulo") == "Resumo geral":
            extra = manual.get(t["chave"], {})
            if extra.get(4):
                txt += "\n\n## Erros encontrados\n\n" + extra[4]
            if extra.get(5):
                txt += "\n\n## Onde melhorar\n\n" + extra[5]
            t["abas"]["analise"] = html_de(txt, tirar_h1=True)
        elif m.get("roteiro_de"):
            t["abas"]["passo-a-passo"] = html_de(txt, tirar_h1=True)
    for chave, secoes in manual.items():
        t = por_chave.get(chave)
        if not t:
            continue
        for n, aba in ((1, "manual-do-usuario"), (2, "regras-de-negocio"), (3, "fluxos")):
            if secoes.get(n):
                t["abas"][aba] = html_de(secoes[n])
    for t in reg["principal"]["telas"]:
        t["validada"] = any(t["abas"].values())
        if t["validada"] and not t["situacao"]:
            t["situacao"] = "Testada"


def contagem(reg_mod):
    telas = reg_mod["telas"]
    return len(telas), sum(1 for t in telas if t["validada"])


# ------------------------------------------------------------------------------------------------
# Peças de página
# ------------------------------------------------------------------------------------------------
def seletor(href_legado=None, href_novo=None, ativo=None):
    """Seletor "Versão: Legado | Novo". Sem endereços: botões que o versao.js liga. Com endereços: links para a mesma tela."""
    if href_legado is None:
        return ('<div class="versao-seletor" role="group" aria-label="Versão do sistema"><span class="vs-rotulo">Versão:</span>'
                '<button type="button" class="vs-btn" data-set-versao="legado" aria-pressed="true">Legado</button>'
                '<button type="button" class="vs-btn" data-set-versao="novo" aria-pressed="false">Novo</button></div>')
    a = lambda k, rot, h: (f'<span class="vs-btn" aria-current="true">{rot}</span>' if k == ativo else f'<a class="vs-btn" href="{E(h)}" title="Trocar de versão e abrir esta mesma tela">{rot}</a>')
    return ('<div class="versao-seletor" role="group" aria-label="Versão do sistema"><span class="vs-rotulo">Versão:</span>'
            + a("legado", "Legado", href_legado) + a("novo", "Novo", href_novo) + '</div>')


def barra_pagina(ativo, href_legado, href_novo, nota=""):
    """Faixa no alto da página de uma tela: a versão ativa e o botão para trocar, mantendo a mesma tela."""
    nome = "Legado" if ativo == "legado" else "Novo"
    desc = ("o sistema entregue pelo fornecedor" if ativo == "legado" else "a versão nova (o mesmo sistema com ferramentas atualizadas)")
    return (f'<div class="versao-barra vb-{ativo}">{seletor(href_legado, href_novo, ativo)}'
            f'<span class="vb-texto">Você está na versão <strong>{nome}</strong>: {desc}.{(" " + nota) if nota else ""}</span></div>')


def bloco_modulo(mod, reg_mod, raiz="../../"):
    """Bloco da página do módulo: seletor e acesso à lista de telas da versão escolhida."""
    n, v = contagem(reg_mod) if reg_mod else (0, 0)
    mid = mod["id"]
    if not n:
        return ""
    situacao = (f'<strong>{v}</strong> com conteúdo validado; as demais marcadas “ainda não validada nesta versão”. ' if v
                else 'nenhuma tem conteúdo validado ainda; todas aparecem como “ainda não validada nesta versão”. ')
    return (f'<section class="versao-modulo" aria-label="Documentação por tela">{seletor()}'
            f'<p data-so-versao="legado">Documentação das <strong>{n} telas</strong> do sistema entregue. '
            f'<a href="{raiz}telas.html?versao=legado#m-{mid}">Abrir a lista de telas do legado →</a></p>'
            f'<p data-so-versao="novo" hidden>Documentação das <strong>{n} telas</strong> da versão nova: {situacao}'
            f'<a href="{raiz}telas.html?versao=novo#mn-{mid}">Abrir a lista de telas da versão nova →</a></p>'
            f'<p class="vs-nota">O ideal (como o módulo deve funcionar) é um só e vale para as duas versões.</p></section>')


def arvore_novo(dados_telas, reg, mods_por_id, doc_modulo_novo):
    """Árvore Módulo > Menu > Tela da versão nova, no mesmo desenho da do legado."""
    h = []
    for m in dados_telas:
        mid = m["id"]
        rm = reg.get(mid)
        if not rm or not rm["telas"]:
            continue
        n, v = contagem(rm)
        docs = doc_modulo_novo.get(mid, [])
        lista = "".join(f'<li class="td-item"><span class="td-ico td-i-tela" aria-hidden="true"></span><a href="{E(u)}">{E(r)}</a></li>' for r, u in docs)
        link_d = f'<ul class="td-lista td-dossie">{lista}</ul>' if lista else ""
        h.append(f'<details class="td-mod" id="mn-{mid}" data-modulo="{mid}"><summary><span class="td-ico td-i-mod" aria-hidden="true"></span>'
                 f'<span class="td-mod-nome">{E(m["nome"])}</span><span class="td-mod-n">{v} de {n} telas validadas</span></summary>{link_d}')
        for menu, ts in rm["menus"]:
            ok = sum(1 for t in ts if t["validada"])
            h.append(f'<details class="td-menu"><summary><span class="td-ico td-i-pasta" aria-hidden="true"></span>{E(menu)} <span class="td-mod-n">{ok} de {len(ts)}</span></summary><ul class="td-lista">')
            for t in ts:
                href = f'documentacao/novo/{mid}/{t["slug"]}-analise.html'
                tag = "" if t["validada"] else '<span class="td-tag">ainda não validada nesta versão</span>'
                h.append(f'<li class="td-tela{"" if t["validada"] else " td-sem"}" data-nome="{E(telas_devs._norm(t["nome"]))}" data-tem="{"1" if t["validada"] else "0"}" '
                         f'data-sit="{"Validada nesta versão" if t["validada"] else "Ainda não validada"}"><span class="td-ico td-i-tela" aria-hidden="true"></span>'
                         f'<a href="{E(href)}">{E(t["nome"])}</a>{tag}</li>')
            h.append("</ul></details>")
        h.append("</details>")
    return "".join(h)


AVISO_TELA = ("Esta tela ainda não foi validada nesta versão. Não há teste nem documento dela na versão nova, e o conteúdo do legado não vale "
              "automaticamente para ela: por isso nada foi copiado para cá.")
AVISO_ABA = "Esta aba ainda não foi validada nesta versão."


def pagina_tela(mod, t, aba_atual, cabecalho, rodape, href_legado, href_ideal, raiz="../../../"):
    """Uma página (tela + aba) da versão nova."""
    mid = mod["id"]
    abas = []
    for chave, rot, _leg in ABAS:
        marca = " aria-current=page" if chave == aba_atual else ""
        vazia = ' class="aba-sem"' if not t["abas"][chave] else ""
        abas.append(f'<a href="{t["slug"]}-{chave}.html"{marca}{vazia}>{rot}</a>')
    ideal = (f'<a class="aba-extra" href="../../{mid}/{href_ideal}" title="O ideal é um só, comum às duas versões">Ideal</a>' if href_ideal
             else '<span class="aba-extra aba-apagada" aria-disabled="true" title="A ficha do ideal ainda não foi escrita">Ideal</span>')
    navabas = '<nav class="abas-tela" aria-label="Páginas desta tela">' + "".join(abas) + '<span class="aba-sep" aria-hidden="true"></span>' + ideal + '</nav>'
    rot_aba = next(r for c, r, _l in ABAS if c == aba_atual)
    corpo = t["abas"][aba_atual]
    if corpo:
        miolo = f'<article class="texto texto-largo">{corpo}</article>'
    else:
        aviso = AVISO_ABA if t["validada"] else AVISO_TELA
        miolo = (f'<article class="texto texto-largo"><div class="callout nv-aviso"><p class="callout-titulo">Ainda não validada nesta versão</p>'
                 f'<p>{aviso}</p><p>Para ver como a tela é no sistema entregue, use o botão <strong>Legado</strong> no alto da página.</p></div></article>')
    situacao = (f'Situação na versão nova: <strong>{E(t["situacao"] or "Testada")}</strong>' if t["validada"]
                else 'Situação na versão nova: <strong>ainda não validada</strong>')
    barra = barra_pagina("novo", href_legado, f"{t['slug']}-{aba_atual}.html")
    titulo = f'{t["nome"]} · {rot_aba} · versão nova · {mod["nome"]} · iLabMedSys'
    pagina = (cabecalho(titulo, raiz).replace("</head>", f'<link rel="stylesheet" href="{raiz}portal/versao.css"></head>', 1)
              .replace("<body ", '<body data-versao-pagina="novo" ', 1) + f"""
<main class="nv-pagina" id="conteudo">
  <nav class="trilha" aria-label="Você está em"><a href="{raiz}index.html">Início</a> › <a href="{raiz}telas.html?versao=novo#mn-{mid}">Documentação por módulo · versão nova</a> › <a href="{raiz}documentacao/{mid}/index.html">{E(mod['nome'])}</a> › <span>{E(t['nome'])}</span></nav>
  {barra}
  <header class="doc-cabecalho"><h1>{E(t['nome'])} <span class="sit-sufixo">· versão nova</span></h1>
  <p class="nv-meta">{E(mod['nome'])} · menu {E(t['menu'])} · {situacao}</p></header>
  {navabas}
  {miolo}
</main>
""" + rodape(raiz))
    return pagina.replace("</body></html>", f'<script src="{raiz}portal/versao.js"></script></body></html>')


def com_versao(texto, raiz):
    """Acrescenta a uma página existente o estilo e o script do seletor de versão."""
    texto = texto.replace("</head>", f'<link rel="stylesheet" href="{raiz}portal/versao.css"></head>', 1)
    return texto.replace("</body></html>", f'<script src="{raiz}portal/versao.js"></script></body></html>')


CSS = """/* Seletor de versão (Legado | Novo) e páginas da versão nova. */
[data-so-versao][hidden]{display:none!important}
.versao-seletor{display:inline-flex;align-items:center;gap:0;border:1px solid var(--linha);border-radius:999px;overflow:hidden;background:var(--painel);font-size:.9rem}
.versao-seletor .vs-rotulo{padding:6px 10px 6px 14px;color:var(--suave);font-weight:600}
.vs-btn{font:inherit;font-weight:700;padding:6px 16px;border:0;border-left:1px solid var(--linha);background:transparent;color:var(--tinta);text-decoration:none;cursor:pointer;display:inline-block}
a.vs-btn:hover{background:var(--painel2)}
.vs-btn[aria-pressed=true],.vs-btn[aria-current=true]{background:var(--laranja);color:#fff;cursor:default}
.versao-barra{display:flex;flex-wrap:wrap;align-items:center;gap:10px 16px;margin:0 0 16px;padding:10px 14px;border:1px solid var(--linha);border-left:5px solid #6b7a8c;border-radius:10px;background:var(--painel)}
.versao-barra.vb-novo{border-left-color:#1f6feb}
.versao-barra .vb-texto{font-size:.88rem;color:var(--suave)}
.versao-modulo{margin:0 0 18px;padding:12px 14px;border:1px solid var(--linha);border-radius:10px;background:var(--painel)}
.versao-modulo p{margin:10px 0 0}
.versao-modulo .vs-nota{font-size:.85rem;color:var(--suave)}
.nv-pagina{max-width:980px;margin:0 auto;padding:22px 16px 56px}
.nv-pagina .sit-sufixo{font-weight:500;color:var(--suave);font-size:.6em}
.nv-meta{margin:6px 0 14px;color:var(--suave);font-size:.92rem}
.abas-tela a.aba-sem:not([aria-current=page]){opacity:.6;border-style:dashed}
.nv-aviso{border-left-color:#b26a00}
.td-tag{margin-left:8px;font-size:.74rem;padding:1px 8px;border:1px dashed #b26a00;border-radius:999px;color:#b26a00;white-space:nowrap}
.td-vs{margin:0 0 14px}
.td-vs-desc{margin:8px 0 0;font-size:.9rem;opacity:.85}
@media (max-width:640px){.versao-seletor{font-size:.85rem}.vs-btn{padding:6px 12px}.nv-pagina{padding:16px 16px 40px}.td-tag{display:block;margin:2px 0 0 0;white-space:normal}.td-tela{flex-wrap:wrap}}
:root[data-theme="dark"] .td-tag,:root:not([data-theme="light"]) .td-tag{color:#e0a43a;border-color:#e0a43a}
@media (prefers-color-scheme:light){:root:not([data-theme="dark"]) .td-tag{color:#b26a00;border-color:#b26a00}}
"""

JS = """/* Seletor de versão: Legado | Novo. A escolha vem da URL (?versao=novo), depois da última escolha (localStorage, opcional) e, por padrão, Legado. */
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
"""
