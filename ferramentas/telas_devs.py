"""Página "Devs/QA": o portal por módulo, menu e tela, com os cinco documentos de cada tela
(manual, regras de negócio, fluxos, análise e Anvisa).

Fontes:
  - as telas e a situação de cada uma vêm do inventário de telas do módulo (homologacao/<módulo>/11-inventario-de-telas.md);
  - os documentos por tela vêm das páginas já geradas (Controle de Desvios: cinco páginas por tela; Principal: o manual,
    na seção da tela) e, quando só existe o documento do módulo, ele aparece marcado "do módulo";
  - o que não existe aparece apagado ("ainda não feito"), para o desenvolvimento ver o que falta.
Nada daqui lê a seção de segurança: só nomes de tela, situação e endereços das páginas do portal."""
import html
import re
import unicodedata
from pathlib import Path

DOCS = [("manual", "Manual"), ("regras", "Regras de negócio"), ("fluxos", "Fluxos"), ("analise", "Análise"), ("anvisa", "Anvisa")]
DIRS = {"principal": "1.principal", "producao": "2.producao", "estoque": "3.estoque", "controle-qualidade": "4.controle_qualidade", "garantia-qualidade": "5.garantia_qualidade",
        "controle-documentos": "6.controle_documento", "comercial": "7.comercial", "rastreabilidade": "8.rastreabilidade", "ope": "9.ope"}
# página do módulo que serve de documento "do módulo" quando a tela não tem o dela
DO_MODULO = {
    "manual": ["manual-do-usuario"],
    "regras": ["regras-de-negocio"],
    "analise": ["reconhecimento-do-modulo"],
    "anvisa": ["conformidade-regulatoria", "conformidade-com-a-rdc-658-2022"],
    "fluxos": [],
}
# nomes do manual do Principal que diferem do nome da tela no inventário
SINONIMOS_MANUAL = {"Login": "Entrar no sistema", "Troca de senha": "Trocar a senha", "Sair": "Sair do sistema"}
# documentos que valem para o módulo inteiro (mostrados uma vez por módulo, não repetidos em cada tela)
DOCS_MODULO = [
    ("Resumo do módulo", ["resumo-do-modulo"]), ("Reconhecimento", ["reconhecimento-do-modulo"]), ("Inventário de telas", ["inventario-de-telas-e-situacao"]),
    ("Manual do usuário", ["manual-do-usuario"]), ("Regras de negócio", ["regras-de-negocio"]),
    ("Conformidade com a ANVISA", ["conformidade-regulatoria", "conformidade-com-a-rdc-658-2022", "conformidade-regulatoria-sncm-e-rdc-658-2022"]),
    ("Plano de testes", ["plano-de-testes"]), ("Relatório de testes", ["relatorio-de-testes"]), ("Defeitos para correção", ["defeitos-para-correcao"]),
    ("Modelo de dados", ["modelo-de-dados-e-integracoes"]), ("Análise de requisitos", ["analise-de-requisitos"]), ("Dossiê de homologação", ["dossie-de-homologacao"]),
]
SITUACOES = ["Funciona com falhas", "Falha grave", "Funciona", "Não testada", "Protótipo", "Não abre"]


def _norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9]+", " ", "".join(c for c in s if unicodedata.category(c) != "Mn")).strip()


def ler_inventario(arq):
    """(menu, tela, situação) de cada tabela do inventário que tem coluna Situação."""
    if not arq.exists():
        return []
    L = arq.read_text(encoding="utf-8").splitlines()
    out, menu, i = [], None, 0
    while i < len(L):
        m = re.match(r"^##+ (.+?)\s*$", L[i])
        if m:
            menu = re.sub(r"\s*\([^)]*\)\s*$", "", m.group(1)).strip()
            i += 1
            continue
        if L[i].startswith("|") and i + 1 < len(L) and re.match(r"^\|[\s:|-]+\|$", L[i + 1]):
            cols = [x.strip() for x in L[i].strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < len(L) and L[i].startswith("|"):
                rows.append([x.strip() for x in L[i].strip().strip("|").split("|")])
                i += 1
            if ("Situação" in cols and menu and not menu.startswith(("Como ler", "Resultado", "Testes de tela", "Outros", "Próximos"))
                    and cols[0].startswith(("Tela", "Cadastro", "Relatório"))):
                for c in rows:
                    if len(c) != len(cols):
                        c = c[:len(cols) - 1] + [" | ".join(c[len(cols) - 1:])] if len(c) > len(cols) else c
                    if len(c) == len(cols):
                        sit = re.sub(r"\*\*|`", "", c[cols.index("Situação")])
                        sit = next((s for s in SITUACOES if sit.startswith(s)), sit.split(".")[0][:30])
                        out.append((menu, re.sub(r"\*+|`", "", c[0]).strip(), sit))
            continue
        i += 1
    return out


def ancoras(arq):
    """Seções (h2/h3) de uma página gerada: [(texto normalizado, id)]."""
    if not arq.exists():
        return []
    t = arq.read_text(encoding="utf-8")
    return [(_norm(re.sub(r"<[^>]+>", "", x[2])), x[1]) for x in re.findall(r'<h([23]) id="([^"]+)">(.*?)</h', t, re.S)]


def montar(modulos, origem, destino):
    """[{id, nome, menus: [(menu, [tela])]}], com tela = {nome, situacao, docs: {chave: (estado, url)}}.
    Estado: "tela" (documento da própria tela), "modulo" (só o do módulo) ou "falta"."""
    hom = Path(origem) / "homologacao"
    out = []
    ordem = ["principal", "estoque", "producao", "ope", "controle-qualidade", "garantia-qualidade", "controle-documentos", "comercial", "rastreabilidade"]
    modulos = sorted([m for m in modulos if m["id"] in ordem], key=lambda m: ordem.index(m["id"]))
    for mod in modulos:
        mid = mod["id"]
        pasta = Path(destino) / "documentacao" / mid
        modulo_docs = {}
        for k, slugs in DO_MODULO.items():
            for s in slugs:
                if (pasta / f"{s}.html").exists():
                    modulo_docs[k] = f"documentacao/{mid}/{s}.html"
                    break
        inv = ler_inventario(hom / DIRS[mid] / "11-inventario-de-telas.md") if mid in DIRS else []
        manual = ancoras(pasta / "manual-do-usuario.html")
        por_tela = {}
        for p in mod.get("paginas", []):
            if p.get("tela_n") and p.get("aba"):
                por_tela.setdefault(_norm(re.sub(r"\s*\(.*?\)", "", p["tela"])), {})[p["aba"]] = f"documentacao/{mid}/{p['slug']}.html"
        menus = {}
        for menu, nome, sit in inv:
            docs = {}
            for k, _ in DOCS:
                url = por_tela.get(_norm(re.sub(r"\s*\(.*?\)", "", nome)), {}).get(k)
                if url:
                    docs[k] = ("tela", url)
                    continue
                if k == "manual" and mid == "principal":
                    n = _norm(SINONIMOS_MANUAL.get(nome, nome))
                    hit = next((a for t, a in manual if t == n or (len(n) > 3 and (n in t or t in n))), None)
                    if not hit and menu.startswith("Cadastros"):
                        hit = next((a for t, a in manual if t == "demais cadastros"), None)
                    if hit:
                        docs[k] = ("tela", f"documentacao/{mid}/manual-do-usuario.html#{hit}")
                        continue
                docs[k] = ("falta", "")
            menus.setdefault(menu, []).append({"nome": nome, "situacao": sit, "docs": docs})
        doc_modulo = []
        for rot, slugs in DOCS_MODULO:
            for s in slugs:
                if (pasta / f"{s}.html").exists():
                    doc_modulo.append((rot, f"documentacao/{mid}/{s}.html"))
                    break
        out.append({"id": mid, "nome": mod["nome"], "menus": list(menus.items()), "doc_modulo": doc_modulo})
    return out


COR_SIT = {"Funciona": "ok", "Funciona com falhas": "falhas", "Falha grave": "grave", "Não testada": "nao", "Protótipo": "proto", "Não abre": "grave"}


def pagina(dados, cabecalho, rodape):
    E = html.escape
    cards, corpo = [], []
    for m in dados:
        telas = [t for _, ts in m["menus"] for t in ts]
        n = len(telas)
        proprio = sum(1 for t in telas if any(v[0] == "tela" for v in t["docs"].values()))
        cont = {}
        for t in telas:
            cont[t["situacao"]] = cont.get(t["situacao"], 0) + 1
        ordem_sit = ["Funciona", "Funciona com falhas", "Falha grave", "Não testada", "Protótipo", "Não abre"]
        barra = "".join(f'<i class="td-b td-{COR_SIT.get(s, "nao")}" style="flex:{cont[s]}" title="{E(s)}: {cont[s]}"></i>' for s in ordem_sit if s in cont)
        legenda = " · ".join(f"{cont[s]} {E(s.lower())}" for s in ordem_sit if s in cont)
        if n:
            cards.append(f'<a class="td-card" href="#m-{m["id"]}"><span class="td-card-nome">{E(m["nome"])}</span>'
                         f'<span class="td-card-n">{n} telas · {proprio} com documento próprio</span><span class="td-barra" aria-hidden="true">{barra}</span>'
                         f'<span class="td-card-leg">{legenda}</span></a>')
        else:
            cards.append(f'<a class="td-card td-card-vazio" href="#m-{m["id"]}"><span class="td-card-nome">{E(m["nome"])}</span>'
                         f'<span class="td-card-n">inventário de telas ainda não feito</span></a>')
        docs_mod = "".join(f'<a href="{E(u)}">{E(r)}</a>' for r, u in m["doc_modulo"])
        h = [f'<section class="td-mod" id="m-{m["id"]}" data-modulo="{m["id"]}"><header class="td-mod-cab"><h2>{E(m["nome"])}</h2>'
             f'<span class="td-mod-n">{n} telas</span></header>'
             f'<div class="td-docmod"><span>Documentos do módulo inteiro:</span> {docs_mod or "nenhum ainda"} '
             f'<a class="td-todos" href="documentacao/{m["id"]}/index.html">Página do módulo →</a></div>']
        if not telas:
            h.append('<p class="td-vazio">Este módulo ainda não tem o inventário de telas.</p>')
        for menu, ts in m["menus"]:
            h.append(f'<details class="td-menu" open><summary>{E(menu)} <span class="td-mod-n">{len(ts)} telas</span></summary>')
            h.append('<div class="td-tab" role="table"><div class="td-row td-cab" role="row"><span role="columnheader">Tela</span><span role="columnheader">Situação</span>'
                     + "".join(f'<span role="columnheader">{r}</span>' for _, r in DOCS) + '</div>')
            for t in ts:
                cel = []
                for k, rot in DOCS:
                    est, url = t["docs"][k]
                    if est == "tela":
                        cel.append(f'<a class="td-c td-sim" role="cell" data-rot="{rot}" href="{E(url)}" aria-label="{rot} de {E(t["nome"])}" title="{rot}">✓</a>')
                    else:
                        cel.append(f'<span class="td-c td-nao" role="cell" data-rot="{rot}" aria-label="{rot}: ainda não feito">—</span>')
                tem = any(v[0] == "tela" for v in t["docs"].values())
                cs = COR_SIT.get(t["situacao"], "nao")
                h.append(f'<div class="td-row td-tela" role="row" data-nome="{E(_norm(t["nome"]))}" data-tem="{"1" if tem else "0"}" data-sit="{E(t["situacao"])}">'
                         f'<span class="td-nome" role="cell">{E(t["nome"])}</span><span class="td-sit td-s-{cs}" role="cell">{E(t["situacao"])}</span>{"".join(cel)}</div>')
            h.append("</div></details>")
        h.append("</section>")
        corpo.append("".join(h))
    opcoes_mod = "".join(f'<option value="{m["id"]}">{E(m["nome"])}</option>' for m in dados if m["menus"])
    opcoes_sit = "".join(f'<option>{s}</option>' for s in ["Funciona", "Funciona com falhas", "Falha grave", "Não testada", "Protótipo", "Não abre"])
    return (cabecalho("Devs/QA: telas por módulo · iLabMedSys", "", "telas").replace("</head>", '<link rel="stylesheet" href="portal/telas.css"></head>', 1) + f"""
<main class="td-pagina">
  <h1>Devs/QA: as telas por módulo</h1>
  <p class="td-intro">Ache o que existe de cada tela. Escolha o módulo e o menu: cada tela mostra a situação e os cinco documentos <strong>da própria tela</strong> (manual, regras de negócio, fluxos, análise e Anvisa). Traço (—) quer dizer que o documento da tela ainda não foi feito. Os documentos que valem para o módulo inteiro ficam numa faixa no alto de cada módulo, uma vez só.</p>
  <div class="td-cards">{"".join(cards)}</div>
  <div class="td-filtros" role="search">
    <label class="td-f"><span>Buscar tela</span><input id="td-busca" type="search" placeholder="Nome da tela" autocomplete="off"></label>
    <label class="td-f"><span>Módulo</span><select id="td-mod"><option value="">Todos</option>{opcoes_mod}</select></label>
    <label class="td-f"><span>Situação</span><select id="td-sit"><option value="">Todas</option>{opcoes_sit}</select></label>
    <label class="td-so"><input id="td-so" type="checkbox"> Só telas com documento próprio</label>
  </div>
  <p id="td-nada" hidden>Nenhuma tela encontrada com esses filtros.</p>
  {"".join(corpo)}
</main>
<script>
(function(){{
  var b=document.getElementById('td-busca'),s=document.getElementById('td-so'),sm=document.getElementById('td-mod'),ss=document.getElementById('td-sit'),nada=document.getElementById('td-nada');
  function norm(x){{return x.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();}}
  function filtrar(){{
    var q=norm(b.value),so=s.checked,mod=sm.value,sit=ss.value,total=0,filtro=!!(q||so||mod||sit);
    document.querySelectorAll('.td-tela').forEach(function(li){{
      var ok=(!q||li.dataset.nome.indexOf(q)>=0)&&(!so||li.dataset.tem==='1')&&(!sit||li.dataset.sit===sit)&&(!mod||li.closest('.td-mod').dataset.modulo===mod);
      li.hidden=!ok; if(ok)total++;
    }});
    document.querySelectorAll('.td-menu').forEach(function(d){{var vis=d.querySelectorAll('.td-tela:not([hidden])').length; d.hidden=filtro&&!vis;}});
    document.querySelectorAll('.td-mod').forEach(function(d){{var vis=d.querySelectorAll('.td-tela:not([hidden])').length; d.hidden=filtro&&!vis&&(mod||q||so||sit);}});
    nada.hidden=!filtro||total>0;
  }}
  [b,sm,ss].forEach(function(e){{e.addEventListener('input',filtrar);}}); s.addEventListener('change',filtrar);
}})();
</script>
""" + rodape(""))


CSS = """/* Página Devs/QA (telas por módulo). */
.td-pagina{max-width:1180px;margin:0 auto;padding:24px 16px 64px}
.td-pagina h1{font-family:Manrope,Inter,sans-serif;margin:0 0 8px}
.td-intro{max-width:78ch;margin:0 0 18px}
.td-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px;margin:0 0 22px}
.td-card{display:flex;flex-direction:column;gap:6px;padding:12px 14px;border:1px solid #c7ced6;border-radius:12px;text-decoration:none;color:inherit}
.td-card:hover,.td-card:focus-visible{border-color:#1f5f8b}
.td-card-nome{font-weight:700}
.td-card-n,.td-card-leg{font-size:.8rem;opacity:.8}
.td-card-vazio{opacity:.65}
.td-barra{display:flex;height:8px;border-radius:4px;overflow:hidden;background:#e5e9ee}
.td-b{display:block;min-width:3px}
.td-b.td-ok,.td-s-ok{--c:#2e7d32}.td-b.td-falhas,.td-s-falhas{--c:#b26a00}.td-b.td-grave,.td-s-grave{--c:#b3261e}.td-b.td-nao,.td-s-nao{--c:#6b7785}.td-b.td-proto,.td-s-proto{--c:#3f6aa0}
.td-b{background:var(--c)}
.td-filtros{display:flex;flex-wrap:wrap;gap:14px;align-items:end;margin:0 0 18px;position:sticky;top:0;z-index:5;padding:10px 0;background:var(--fundo,#f4f6f9)}
.td-f span{display:block;font-size:.8rem;margin-bottom:3px}
.td-f input,.td-f select{min-width:200px;padding:8px 10px;border:1px solid #c7ced6;border-radius:8px;background:transparent;color:inherit;font:inherit}
.td-so{display:flex;gap:6px;align-items:center;padding-bottom:8px}
.td-mod{margin:0 0 30px;scroll-margin-top:90px}
.td-mod-cab{display:flex;gap:12px;align-items:baseline;border-bottom:2px solid #1f5f8b;padding-bottom:4px}
.td-mod-cab h2{margin:0;font-size:1.3rem}
.td-mod-n{font-weight:400;font-size:.85rem;opacity:.75}
.td-docmod{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;margin:10px 0 12px;font-size:.88rem}
.td-docmod span{font-weight:600}
.td-docmod a{color:#1f5f8b}
.td-docmod .td-todos{margin-left:auto;font-weight:600}
.td-menu{margin:0 0 14px}
.td-menu>summary{cursor:pointer;font-weight:700;padding:6px 0}
.td-tab{border:1px solid #d9dee4;border-radius:10px;overflow:hidden}
.td-row{display:grid;grid-template-columns:minmax(200px,1.8fr) 150px repeat(5,minmax(70px,.7fr));align-items:stretch;gap:0;padding:0}
.td-row>*{padding:9px 10px;border-top:1px solid #e3e7ec;display:flex;align-items:center}
.td-cab{background:#eef1f5;font-size:.74rem;font-weight:700;text-transform:uppercase;letter-spacing:.02em}
.td-cab>*:nth-child(n+3){justify-content:center;text-align:center}
.td-cab>*{border-top:0}
.td-tela[hidden],.td-menu[hidden],.td-mod[hidden]{display:none}
.td-nome{font-weight:600}
.td-sit{font-size:.82rem;font-weight:600;color:var(--c)}
.td-sit::before{content:"";display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--c);margin-right:6px}
.td-c{justify-content:center;font-size:1.05rem;text-decoration:none}
.td-sim{color:#1f5f8b;font-weight:700}
.td-sim:hover,.td-sim:focus-visible{background:#e6f0f7}
.td-nao{color:#8a96a3}
.td-vazio{opacity:.85}
@media (max-width:760px){
 .td-cab{display:none}
 .td-row{grid-template-columns:1fr 1fr;padding:6px 0}
 .td-nome{grid-column:1/-1;border-top:0}
 .td-sit{grid-column:1/-1}
 .td-row>.td-c{justify-content:space-between;font-size:.9rem}
 .td-row>.td-c::before{content:attr(data-rot);font-size:.78rem;opacity:.8;margin-right:6px;font-weight:400}
 .td-docmod .td-todos{margin-left:0}
}
:root[data-theme="dark"] .td-card,:root[data-theme="dark"] .td-f input,:root[data-theme="dark"] .td-f select{border-color:#3b4655}
:root[data-theme="dark"] .td-tab{border-color:#323c49}
:root[data-theme="dark"] .td-row>*{border-top-color:#2c3541}
:root[data-theme="dark"] .td-cab{background:#222b36}
:root[data-theme="dark"] .td-barra{background:#2c3541}
:root[data-theme="dark"] .td-filtros{background:var(--fundo,#101418)}
:root[data-theme="dark"] .td-sim,:root[data-theme="dark"] .td-docmod a{color:#7cbfe6}
:root[data-theme="dark"] .td-sim:hover{background:#1d2d3a}
:root[data-theme="dark"] .td-mod-cab{border-bottom-color:#4a9fd4}
:root[data-theme="dark"] .td-b.td-ok,:root[data-theme="dark"] .td-s-ok{--c:#66bb6a}
:root[data-theme="dark"] .td-b.td-falhas,:root[data-theme="dark"] .td-s-falhas{--c:#ffb74d}
:root[data-theme="dark"] .td-b.td-grave,:root[data-theme="dark"] .td-s-grave{--c:#ef7b73}
:root[data-theme="dark"] .td-b.td-nao,:root[data-theme="dark"] .td-s-nao{--c:#9aa6b3}
:root[data-theme="dark"] .td-b.td-proto,:root[data-theme="dark"] .td-s-proto{--c:#7ea6d9}
@media (prefers-color-scheme:dark){
:root:not([data-theme="light"]) .td-card,:root:not([data-theme="light"]) .td-f input,:root:not([data-theme="light"]) .td-f select{border-color:#3b4655}
:root:not([data-theme="light"]) .td-tab{border-color:#323c49}
:root:not([data-theme="light"]) .td-row>*{border-top-color:#2c3541}
:root:not([data-theme="light"]) .td-cab{background:#222b36}
:root:not([data-theme="light"]) .td-barra{background:#2c3541}
:root:not([data-theme="light"]) .td-filtros{background:var(--fundo,#101418)}
:root:not([data-theme="light"]) .td-sim,:root:not([data-theme="light"]) .td-docmod a{color:#7cbfe6}
:root:not([data-theme="light"]) .td-mod-cab{border-bottom-color:#4a9fd4}
:root:not([data-theme="light"]) .td-b.td-ok,:root:not([data-theme="light"]) .td-s-ok{--c:#66bb6a}
:root:not([data-theme="light"]) .td-b.td-falhas,:root:not([data-theme="light"]) .td-s-falhas{--c:#ffb74d}
:root:not([data-theme="light"]) .td-b.td-grave,:root:not([data-theme="light"]) .td-s-grave{--c:#ef7b73}
:root:not([data-theme="light"]) .td-b.td-nao,:root:not([data-theme="light"]) .td-s-nao{--c:#9aa6b3}
:root:not([data-theme="light"]) .td-b.td-proto,:root:not([data-theme="light"]) .td-s-proto{--c:#7ea6d9}}
"""
