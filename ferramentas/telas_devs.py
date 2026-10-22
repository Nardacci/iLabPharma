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
                docs[k] = ("modulo", modulo_docs[k]) if k in modulo_docs else ("falta", "")
            menus.setdefault(menu, []).append({"nome": nome, "situacao": sit, "docs": docs})
        out.append({"id": mid, "nome": mod["nome"], "menus": list(menus.items())})
    return out


def pagina(dados, cabecalho, rodape):
    E = html.escape
    corpo = []
    for m in dados:
        telas = [t for _, ts in m["menus"] for t in ts]
        completas = sum(1 for t in telas if all(v[0] == "tela" for v in t["docs"].values()))
        if telas:
            resumo = f"{len(telas)} telas" + (f" · {completas} com os 5 documentos da tela" if completas else "")
        else:
            resumo = "inventário de telas ainda não feito"
        h = [f'<details class="td-mod" data-modulo="{m["id"]}"{" open" if m["id"] == "garantia-qualidade" else ""}><summary><span class="td-mod-nome">{E(m["nome"])}</span><span class="td-mod-n">{E(resumo)}</span></summary>']
        if not telas:
            h.append(f'<p class="td-vazio">Este módulo ainda não tem o inventário de telas. Os documentos do módulo estão na <a href="documentacao/{m["id"]}/index.html">página do módulo</a>.</p>')
        for menu, ts in m["menus"]:
            h.append(f'<details class="td-menu"><summary>{E(menu)} <span class="td-mod-n">{len(ts)} telas</span></summary><ul class="td-telas">')
            for t in ts:
                chips = []
                for k, rot in DOCS:
                    est, url = t["docs"][k]
                    if est == "tela":
                        chips.append(f'<a class="td-chip td-ok" href="{E(url)}">{rot}</a>')
                    elif est == "modulo":
                        chips.append(f'<a class="td-chip td-mod-doc" href="{E(url)}" title="Documento do módulo, não é só desta tela">{rot} <small>do módulo</small></a>')
                    else:
                        chips.append(f'<span class="td-chip td-falta" title="Ainda não feito" aria-disabled="true">{rot} <small>ainda não feito</small></span>')
                tem = any(v[0] == "tela" for v in t["docs"].values())
                h.append(f'<li class="td-tela" data-nome="{E(_norm(t["nome"]))}" data-tem="{"1" if tem else "0"}">'
                         f'<div class="td-tela-cab"><span class="td-nome">{E(t["nome"])}</span><span class="td-sit">{E(t["situacao"])}</span></div>'
                         f'<div class="td-chips">{"".join(chips)}</div></li>')
            h.append("</ul></details>")
        h.append("</details>")
        corpo.append("".join(h))
    leitura = ("<p>Para quem desenvolve ou testa e precisa achar o que existe de cada tela. Escolha o módulo, o menu e a tela. Cada tela tem cinco botões: "
               "<strong>Manual</strong>, <strong>Regras de negócio</strong>, <strong>Fluxos</strong>, <strong>Análise</strong> e <strong>Anvisa</strong>. "
               "Botão cheio: documento da própria tela. Botão com contorno e \"do módulo\": só existe o documento do módulo inteiro. "
               "Botão apagado: ainda não foi feito. As telas e a situação vêm do inventário de telas de cada módulo (sistema legado entregue pelo fornecedor).</p>")
    return (cabecalho("Devs/QA: telas por módulo · iLabMedSys", "", "telas").replace("</head>", '<link rel="stylesheet" href="portal/telas.css"></head>', 1) + f"""
<main class="td-pagina">
  <h1>Devs/QA: as telas por módulo</h1>
  {leitura}
  <div class="td-filtros">
    <label class="td-busca"><span>Buscar tela</span><input id="td-busca" type="search" placeholder="Nome da tela" autocomplete="off"></label>
    <label class="td-so"><input id="td-so" type="checkbox"> Só telas com documento próprio</label>
  </div>
  <p id="td-nada" hidden>Nenhuma tela encontrada.</p>
  {"".join(corpo)}
</main>
<script>
(function(){{
  var b=document.getElementById('td-busca'),s=document.getElementById('td-so'),nada=document.getElementById('td-nada');
  function norm(x){{return x.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();}}
  function filtrar(){{
    var q=norm(b.value),so=s.checked,total=0,filtro=!!q||so;
    document.querySelectorAll('.td-tela').forEach(function(li){{
      var ok=(!q||li.dataset.nome.indexOf(q)>=0)&&(!so||li.dataset.tem==='1');
      li.hidden=!ok; if(ok)total++;
    }});
    document.querySelectorAll('.td-menu,.td-mod').forEach(function(d){{
      var vis=d.querySelectorAll('.td-tela:not([hidden])').length; d.hidden=filtro&&!vis; if(filtro&&vis)d.open=true;
    }});
    nada.hidden=!filtro||total>0;
  }}
  b.addEventListener('input',filtrar); s.addEventListener('change',filtrar);
}})();
</script>
""" + rodape(""))


CSS = """/* Página Devs/QA (telas por módulo). */
.td-pagina{max-width:1040px;margin:0 auto;padding:24px 16px 64px}
.td-pagina h1{font-family:Manrope,Inter,sans-serif;margin:0 0 8px}
.td-filtros{display:flex;flex-wrap:wrap;gap:16px;align-items:end;margin:16px 0 20px}
.td-busca span{display:block;font-size:.85rem;margin-bottom:4px}
.td-busca input{min-width:260px;padding:8px 10px;border:1px solid #c7ced6;border-radius:8px;background:transparent;color:inherit}
.td-so{display:flex;gap:6px;align-items:center}
.td-mod{border:1px solid #c7ced6;border-radius:12px;margin:12px 0;padding:0 14px}
.td-mod>summary{cursor:pointer;padding:14px 0;display:flex;gap:12px;justify-content:space-between;align-items:baseline;flex-wrap:wrap}
.td-mod-nome{font-weight:700;font-size:1.1rem}
.td-mod-n{font-weight:400;font-size:.85rem;opacity:.75}
.td-menu{margin:6px 0 10px;padding-left:4px}
.td-menu>summary{cursor:pointer;font-weight:600;padding:6px 0}
.td-telas{list-style:none;margin:4px 0 8px;padding:0}
.td-tela{padding:10px 0;border-top:1px solid #d9dee4}
.td-tela[hidden],.td-menu[hidden],.td-mod[hidden]{display:none}
.td-tela-cab{display:flex;gap:12px;justify-content:space-between;align-items:baseline;flex-wrap:wrap;margin-bottom:6px}
.td-nome{font-weight:600}
.td-sit{font-size:.8rem;opacity:.8}
.td-chips{display:flex;flex-wrap:wrap;gap:6px}
.td-chip{display:inline-flex;gap:6px;align-items:baseline;padding:5px 10px;border-radius:999px;font-size:.85rem;text-decoration:none;border:1px solid transparent}
.td-chip small{font-size:.7rem;opacity:.85}
.td-ok{background:#1f5f8b;color:#fff}
.td-ok:hover,.td-ok:focus{background:#174a6d}
.td-mod-doc{border-color:#1f5f8b;color:#1f5f8b;background:transparent}
.td-falta{border:1px dashed #8a96a3;color:#5d6875;opacity:.8;cursor:not-allowed}
:root[data-theme="dark"] .td-mod{border-color:#3b4655}
:root[data-theme="dark"] .td-tela{border-color:#323c49}
:root[data-theme="dark"] .td-ok{background:#4a9fd4;color:#06222f}
:root[data-theme="dark"] .td-mod-doc{border-color:#7cbfe6;color:#7cbfe6}
:root[data-theme="dark"] .td-falta{border-color:#667585;color:#9aa6b3}
@media (prefers-color-scheme:dark){
:root:not([data-theme="light"]) .td-mod{border-color:#3b4655}
:root:not([data-theme="light"]) .td-tela{border-color:#323c49}
:root:not([data-theme="light"]) .td-ok{background:#4a9fd4;color:#06222f}
:root:not([data-theme="light"]) .td-mod-doc{border-color:#7cbfe6;color:#7cbfe6}
:root:not([data-theme="light"]) .td-falta{border-color:#667585;color:#9aa6b3}}
.td-vazio{padding:0 0 14px;opacity:.85}
"""
