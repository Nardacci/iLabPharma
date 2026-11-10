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


ALIAS_NOMES = {}  # (módulo, nome COMPLETO normalizado na documentação do legado, com o que está entre parênteses) -> slug da tela no inventário


def carregar_alias(hom):
    """Lê homologacao/portal-equivalencia-nomes-de-tela.csv: telas cujo nome na documentação do legado difere do nome no inventário."""
    import csv
    ALIAS_NOMES.clear()
    arq = Path(hom) / "portal-equivalencia-nomes-de-tela.csv"
    if arq.exists():
        with arq.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if (r.get("slug_da_tela_no_inventario") or "").strip():
                    ALIAS_NOMES[(r["modulo"].strip(), telas_devs._norm(r["nome_na_documentacao"]))] = r["slug_da_tela_no_inventario"].strip()
    return len(ALIAS_NOMES)


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


def preencher_por_manifesto(reg, hom, mid, manifesto, limpar, converter):
    """Lê um manifest.json (uma entrada por tela e aba, com os títulos de seção do legado) e põe o conteúdo nas telas do módulo.
    A tela é achada pelo nome do inventário do legado; o conteúdo substitui o que a aba já tinha."""
    arq_man = Path(hom) / manifesto
    if not arq_man.exists() or mid not in reg:
        return
    por_nome = {_slug(t["nome"]): t for t in reg[mid]["telas"]}  # sem diferença de maiúscula, acento ou pontuação
    for m in json.loads(arq_man.read_text(encoding="utf-8")):
        t = por_nome.get(_slug(m["tela"]))
        if not t or m["aba"] not in t["abas"]:
            continue
        md = limpar((Path(hom) / m["arq"]).read_text(encoding="utf-8"))
        md = re.sub(r"^#(#+ )", r"\1", md, flags=re.M)  # o conversor sobe um nível de título; assim ## sai como h2 e #### como h4, como no legado
        corpo = converter("# x\n" + md)  # o conversor descarta a primeira linha de título
        t["abas"][m["aba"]] = corpo.replace('"../img/', '"../../img/')
    for t in reg[mid]["telas"]:
        t["validada"] = any(t["abas"].values())
        if t["validada"] and not t["situacao"]:
            t["situacao"] = "Testada"


def preencher_estoque(reg, hom, limpar, converter):
    """Estoque novo: abas por tela no modelo do legado (versao-nova/3.estoque/telas/manifest.json)."""
    preencher_por_manifesto(reg, hom, "estoque", "versao-nova/3.estoque/telas-modelo/manifest.json", limpar, converter)


def preencher_principal_modelo(reg, hom, limpar, converter):
    """Principal novo: telas já reescritas no modelo do legado (versao-nova/1.principal/telas-modelo/manifest.json), por cima das abas antigas."""
    preencher_por_manifesto(reg, hom, "principal", "versao-nova/1.principal/telas-modelo/manifest.json", limpar, converter)


SECOES_MODELO_LEGADO = [
    ("conhecer", "Telas e situação", "O que existe na versão nova, como as telas se organizam nos menus e o que os testes mostraram."),
    ("fluxos", "Siga o processo", "Como usar esta documentação, na ordem em que o trabalho acontece."),
    ("menus", "Menus do sistema, tela a tela", "Uma página por tela dos menus do módulo: análise, manual do usuário, fluxos, regras de negócio e Anvisa."),
    ("regras", "Regras e uso", "O que a versão nova faz com cada dado, quem pode fazer o quê e como usar."),
    ("dados", "Dados e integrações", "Comparação com o sistema entregue."),
    ("testes", "Testes e defeitos", "O que foi testado, o resultado de cada rodada e os defeitos encontrados."),
    ("fecho", "Fechamento", "O parecer, o dossiê e o resumo para a diretoria."),
]
MENU_EXIBIDO = {"Cadastros": "Cadastros e tabelas de apoio", "Tabelas de apoio": "Cadastros e tabelas de apoio"}


def _secao_do_documento(titulo):
    t = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode().lower()
    if "inventario de telas" in t or "visao geral por menu" in t:
        return "conhecer"
    if "como usar" in t:
        return "fluxos"
    if "manual" in t:
        return "regras"
    if "comparacao" in t:
        return "dados"
    if "dossie" in t or "resumo executivo" in t or "parecer" in t:
        return "fecho"
    return "testes"


def _primeiro_paragrafo(html_aba):
    m = re.search(r"Para que serve</h\d>\s*<p>(.*?)</p>", html_aba or "", re.S)
    return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else ""


def secoes_novo_modelo_legado(mid, pags, reg_mod):
    """Seções da página Novo do módulo, com a mesma ordem e o mesmo desenho da página Legado."""
    por_chave = {t["chave"]: t for t in reg_mod["telas"]}
    card = lambda p, meta, num=True: (f'<a class="doc-card" href="{E(p["slug"])}.html"><span class="doc-card-titulo">'
                                      + (f'<span class="doc-n">{p["n"]}</span>' if num else "") + f'{E(p["titulo"])}</span><span class="doc-card-meta">{meta}</span></a>')
    eh_menu = lambda p: ": entenda o menu" in p["titulo"] or ": visão geral" in p["titulo"]
    gerais = [p for p in pags if not p.get("grupo") and not eh_menu(p)]
    menu_docs = [p for p in pags if eh_menu(p)]
    # Menus e telas vêm do inventário do Legado (mesma lista e mesma ordem do Legado); só os menus com página "entenda o menu" aparecem.
    por_menu = {}
    for menu, ts in reg_mod["menus"]:
        por_menu.setdefault(MENU_EXIBIDO.get(menu, menu), []).extend(ts)
    out = {}
    for p in gerais:
        out.setdefault(_secao_do_documento(p["titulo"]), []).append(card(p, "Word disponível" if p["word"] else "Leitura no portal"))
    menus = []
    for g, ts in por_menu.items():
        docs = [p for p in menu_docs if p["titulo"].startswith(g + ":")]
        if not docs:
            continue
        h = f'<h3 class="novo-menu">{E(g)}</h3><div class="doc-cards">' + "".join(card(p, "Comece por aqui", False) for p in docs) + "</div>"
        cartas = []
        for i, t in enumerate(ts, 1):
            links = " · ".join(f'<a href="../novo/{mid}/{t["slug"]}-{a}.html">{r}</a>' for a, r in
                               (("analise", "Análise"), ("manual-do-usuario", "Manual do usuário"), ("fluxos", "Fluxos"), ("regras-de-negocio", "Regras de negócio"), ("anvisa", "Anvisa")))
            meta = _primeiro_paragrafo(t["abas"].get("analise"))
            cartas.append(f'<div class="doc-card tela-card"><a class="doc-card-titulo" href="../novo/{mid}/{t["slug"]}-analise.html"><span class="doc-n">{i}</span>{E(t["nome"])}</a>'
                          f'<span class="doc-card-meta">{E(meta)}</span><span class="tela-links">{links}</span></div>')
        menus.append(h + f'<div class="doc-cards">{"".join(cartas)}</div>')
    out["menus"] = "".join(menus)
    html_out, sub = [], []
    for chave, nome, desc in SECOES_MODELO_LEGADO:
        corpo = out.get(chave)
        if not corpo:
            continue
        grade = corpo if chave == "menus" else f'<div class="doc-cards">{"".join(corpo)}</div>'
        html_out.append(f'<section class="secao passo" id="passo-{chave}"><div class="passo-cab"><div><h3>{E(nome)}</h3><p class="secao-desc">{E(desc)}</p></div></div>{grade}</section>')
        sub.append(f'<a href="#passo-{chave}">{E(nome)}</a>')
    return "".join(html_out), '<nav class="submenu" aria-label="Passos do roteiro">' + "".join(sub) + "</nav>"


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
    """Faixa no alto da página de uma tela. Decisão do responsável (08/11/2026): a faixa "Versão: Legado | Novo" e o texto
    "Você está na versão…" saíram das páginas de tela; a versão aparece no selo do cabeçalho e na trilha. Só resta a nota, quando há."""
    if not nota:
        return ""
    return f'<div class="versao-barra vb-{ativo}"><span class="vb-texto">{nota}</span></div>'


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
        # Igual ao legado: abaixo do módulo, só o link "Dossiê de homologação" (a página Novo do módulo, que lista os documentos da versão nova) e as pastas dos menus.
        link_d = ""
        if docs:
            # Igual ao legado: o link abre o próprio documento do dossiê (a versão nova dele, quando existe); sem o dossiê da versão nova, a página Novo do módulo.
            alvo = next((u for r, u in docs if r.startswith("Dossiê de homologação")), docs[0][1])
            link_d = (f'<ul class="td-lista td-dossie"><li class="td-item"><span class="td-ico td-i-tela" aria-hidden="true"></span>'
                      f'<a href="{E(alvo)}">Dossiê de homologação</a></li></ul>')
        h.append(f'<details class="td-mod" id="mn-{mid}" data-modulo="{mid}"><summary><span class="td-ico td-i-mod" aria-hidden="true"></span>'
                 f'<span class="td-mod-nome">{E(m["nome"])}</span><span class="td-mod-n">{n} telas</span></summary>{link_d}')
        for menu, ts in rm["menus"]:
            ok = sum(1 for t in ts if t["validada"])
            h.append(f'<details class="td-menu"><summary><span class="td-ico td-i-pasta" aria-hidden="true"></span>{E(menu)} <span class="td-mod-n">{len(ts)}</span></summary><ul class="td-lista">')
            for t in ts:
                href = f'documentacao/novo/{mid}/{t["slug"]}-analise.html'
                tag = ""  # a tela sem conteúdo validado já aparece esmaecida; o texto "ainda não validada nesta versão" saiu da lista (decisão do responsável, 09/11/2026)
                h.append(f'<li class="td-tela{"" if t["validada"] else " td-sem"}" data-nome="{E(telas_devs._norm(t["nome"]))}" data-tem="{"1" if t["validada"] else "0"}" '
                         f'data-sit="{"Validada nesta versão" if t["validada"] else "Ainda não validada"}"><span class="td-ico td-i-tela" aria-hidden="true"></span>'
                         f'<a href="{E(href)}">{E(t["nome"])}</a>{tag}</li>')
            h.append("</ul></details>")
        h.append("</details>")
    return "".join(h)


AVISO_TELA = ("Esta tela ainda não foi validada nesta versão. Não há teste nem documento dela na versão nova, e o conteúdo do legado não vale "
              "automaticamente para ela: por isso nada foi copiado para cá.")
AVISO_ABA = "Esta aba ainda não foi validada nesta versão."


ABAS_PRINCIPAIS = ["analise", "manual-do-usuario", "fluxos", "regras-de-negocio", "anvisa"]
# ordem única do portal (igual à do legado): cinco abas, separador, Erros, Passo a passo, Ideal
SEQUENCIA_ABAS = ABAS_PRINCIPAIS + ["erros", "passo-a-passo"]
ROTULO_ABA = {**{c: r for c, r, _l in ABAS}, "erros": "Erros"}


def navegacao_abas(mid, t, aba_atual, href_ideal, erros=""):
    """Faixa de abas da tela na versão nova, na mesma ordem do legado. aba_atual = chave de ABAS ou "erros" (a aba marcada)."""
    abas = []
    for chave in ABAS_PRINCIPAIS:
        marca = " aria-current=page" if chave == aba_atual else ""
        vazia = ' class="aba-sem"' if not t["abas"][chave] else ""
        abas.append(f'<a href="{t["slug"]}-{chave}.html"{marca}{vazia}>{ROTULO_ABA[chave]}</a>')
    passo = (f'<a class="aba-extra{" aba-sem" if not t["abas"]["passo-a-passo"] else ""}" href="{t["slug"]}-passo-a-passo.html"'
             f'{" aria-current=page" if aba_atual == "passo-a-passo" else ""}>Passo a passo</a>')
    ideal = (f'<a class="aba-extra" href="../../{mid}/{href_ideal}" title="O ideal é um só, comum às duas versões">Ideal</a>' if href_ideal
             else '<span class="aba-extra aba-apagada" aria-disabled="true" title="A ficha do ideal ainda não foi escrita">Ideal</span>')
    if aba_atual == "erros" and erros:
        erros = erros.replace('<a class="', '<a aria-current="page" class="', 1)
    return '<nav class="abas-tela" aria-label="Páginas desta tela">' + "".join(abas) + '<span class="aba-sep" aria-hidden="true"></span>' + erros + passo + ideal + '</nav>'


def pagina_tela(mod, t, aba_atual, cabecalho, rodape, href_legado, href_ideal, raiz="../../../", erros="", lateral="", ap="", toc_fn=None, n=None, total=None):
    """Uma página (tela + aba) da versão nova."""
    mid = mod["id"]
    navabas = navegacao_abas(mid, t, aba_atual, href_ideal, erros)
    rot_aba = next(r for c, r, _l in ABAS if c == aba_atual)
    corpo = t["abas"][aba_atual]
    toc = ""
    if corpo and toc_fn:
        corpo, toc = toc_fn(corpo)
    if corpo:
        miolo = f'<article class="texto texto-largo">{corpo}</article>'
    else:
        aviso = AVISO_ABA if t["validada"] else AVISO_TELA
        miolo = (f'<article class="texto texto-largo"><div class="callout nv-aviso"><p class="callout-titulo">Ainda não validada nesta versão</p>'
                 f'<p>{aviso}</p><p>Para ver como a tela é no sistema entregue, <a href="{E(href_legado)}">abra a página do Legado</a>.</p></div></article>')
    _sit_txt = (t["situacao"] or "Testada") if t["validada"] else "ainda não validada"
    _cor = {"Testada": "#2e7d32", "Validada nesta versão": "#2e7d32"}.get(_sit_txt, "#6b7785")
    situacao = (f'<p class="sit-tela" style="margin:10px 0 0;font-size:.92rem"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:{_cor};margin-right:6px"></span>'
                f'Situação da tela na versão nova: <strong>{E(_sit_txt)}</strong> <span style="opacity:.75">(a partir dos testes da versão nova)</span></p>')
    _onde = f'Novo · menu {E(t["menu"])}'
    _onde_estou = (f'<div class="onde-estou" aria-label="Onde você está no roteiro"><span>{_onde}</span>'
                   + (f'<span>documento {n} de {total}</span><div class="prog-doc"><i style="width:{round(n / total * 100)}%"></i></div>' if n and total else '') + '</div>')
    barra = barra_pagina("novo", href_legado, f"{t['slug']}-{aba_atual}.html")
    titulo = f'{t["nome"]} · {rot_aba} · versão nova · {mod["nome"]} · iLabMedSys'
    abre = ('<div class="doc-layout">\n  ' + lateral + '\n  <main class="doc" id="conteudo">') if lateral else '<main class="nv-pagina" id="conteudo">'
    fecha = ('</main>\n  ' + toc + '\n</div>') if lateral else '</main>'
    pagina = (cabecalho(titulo, raiz).replace("</head>", f'<link rel="stylesheet" href="{raiz}portal/versao.css"></head>', 1)
              .replace("<body ", '<body data-versao-pagina="novo" ', 1) + f"""
{abre}
  <nav class="trilha" aria-label="Você está em"><a href="{raiz}index.html">Início</a> › <a href="{raiz}documentacao/{mid}/index.html">{E(mod['nome'])}</a> › <a class="sit-trilha" href="{raiz}documentacao/{mid}/novo.html" style="--cor:#1f6feb">Novo</a> › <span>{E(t['nome'])}</span></nav>
  {_onde_estou}
  <header class="doc-cabecalho"><h1>{E(t['nome'])}: {rot_aba}</h1>
  <div class="doc-acoes"><button class="botao botao-secundario" type="button" onclick="window.print()">⎙ Imprimir</button></div></header>
  {barra}{navabas}{situacao}
  {miolo}
  {ap}
{fecha}
""" + rodape(raiz))
    return pagina.replace("</body></html>", f'<script src="{raiz}portal/versao.js"></script></body></html>')


def com_versao(texto, raiz):
    """Acrescenta a uma página existente o estilo e o script do seletor de versão."""
    texto = texto.replace("</head>", f'<link rel="stylesheet" href="{raiz}portal/versao.css"></head>', 1)
    return texto.replace("</body></html>", f'<script src="{raiz}portal/versao.js"></script></body></html>')


CSS = """/* Seletor de versão (Legado | Novo) e páginas da versão nova. */
[data-so-versao][hidden]{display:none!important}
/* Decisão do responsável (08/11/2026): a versão nova tem a mesma estrutura e o mesmo layout do legado, só a cor de destaque muda (azul). */
[data-versao-pagina="novo"] .doc-layout{--laranja:#1f6feb;--laranja2:#5b9bff}
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
