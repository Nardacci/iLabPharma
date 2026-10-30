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


def situacoes(hom):
    """{(módulo, nome da tela normalizado): situação}, lida dos inventários de telas (para mostrar a situação na página da própria tela)."""
    out = {}
    for mid, d in DIRS.items():
        for menu, nome, sit in ler_inventario(Path(hom) / d / "11-inventario-de-telas.md"):
            out[(mid, _norm(re.sub(r"\s*\(.*?\)", "", nome)))] = sit
    return out


def selo_situacao(sit):
    """Linha "Situação da tela" para a página de documento da tela (estilo embutido, para não mexer no CSS do portal)."""
    cor = {"Funciona": "#2e7d32", "Funciona com falhas": "#b26a00", "Falha grave": "#b3261e", "Não testada": "#6b7785", "Protótipo": "#3f6aa0", "Não abre": "#b3261e"}.get(sit, "#6b7785")
    return (f'<p class="sit-tela" style="margin:10px 0 0;font-size:.92rem"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:{cor};margin-right:6px"></span>'
            f'Situação da tela: <strong>{html.escape(sit)}</strong> <span style="opacity:.75">(a partir do inventário de telas do módulo)</span></p>')


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
            propria = next((docs[k][1] for k in ("analise", "manual", "regras", "fluxos", "anvisa") if docs[k][0] == "tela"), "")
            inv_url = f"documentacao/{mid}/inventario-de-telas-e-situacao.html" if (pasta / "inventario-de-telas-e-situacao.html").exists() else ""
            menus.setdefault(menu, []).append({"nome": nome, "situacao": sit, "docs": docs, "href": propria or inv_url, "propria": bool(propria)})
        doc_modulo = []
        for rot, slugs in DOCS_MODULO:
            for s in slugs:
                if (pasta / f"{s}.html").exists():
                    doc_modulo.append((rot, f"documentacao/{mid}/{s}.html"))
                    break
        out.append({"id": mid, "nome": mod["nome"], "menus": list(menus.items()), "doc_modulo": doc_modulo})
    return out


COR_SIT = {"Funciona": "ok", "Funciona com falhas": "falhas", "Falha grave": "grave", "Não testada": "nao", "Protótipo": "proto", "Não abre": "grave"}


def pagina(dados, cabecalho, rodape, arvore_novo="", total_validadas=0, total_novo=0):
    E = html.escape
    corpo = []
    for m in dados:
        telas = [t for _, ts in m["menus"] for t in ts]
        dossie = next((u for r, u in m["doc_modulo"] if r.startswith("Dossiê")), "")
        link_d = (f'<ul class="td-lista td-dossie"><li class="td-item"><span class="td-ico td-i-tela" aria-hidden="true"></span>'
                  f'<a href="{E(dossie)}">Dossiê de homologação</a></li></ul>') if dossie else ""
        h = [f'<details class="td-mod" id="m-{m["id"]}" data-modulo="{m["id"]}"><summary><span class="td-ico td-i-mod" aria-hidden="true"></span>'
             f'<span class="td-mod-nome">{E(m["nome"])}</span><span class="td-mod-n">{len(telas)} telas</span></summary>{link_d}']
        if not telas:
            h.append('<p class="td-vazio">Este módulo ainda não tem o inventário de telas.</p>')
        for menu, ts in m["menus"]:
            h.append(f'<details class="td-menu"><summary><span class="td-ico td-i-pasta" aria-hidden="true"></span>{E(menu)} <span class="td-mod-n">{len(ts)}</span></summary><ul class="td-lista">')
            for t in ts:
                tem = any(v[0] == "tela" for v in t["docs"].values())
                dica = "" if t["propria"] else ' title="Ainda sem página própria: abre o inventário de telas do módulo"'
                nome = E(t["nome"])
                alvo = f'<a href="{E(t["href"])}"{dica}>{nome}</a>' if t["href"] else f'<span>{nome}</span>'
                h.append(f'<li class="td-tela{"" if t["propria"] else " td-sem"}" data-nome="{E(_norm(t["nome"]))}" data-tem="{"1" if tem else "0"}" data-sit="{E(t["situacao"])}">'
                         f'<span class="td-ico td-i-tela" aria-hidden="true"></span>{alvo}</li>')
            h.append("</ul></details>")
        h.append("</details>")
        corpo.append("".join(h))
    opcoes_mod = "".join(f'<option value="{m["id"]}">{E(m["nome"])}</option>' for m in dados if m["menus"])
    opcoes_sit = "".join(f'<option>{s}</option>' for s in ["Funciona", "Funciona com falhas", "Falha grave", "Não testada", "Protótipo", "Não abre"])
    opcoes_sit_n = "".join(f'<option>{s}</option>' for s in ["Validada nesta versão", "Ainda não validada"])
    return (cabecalho("Documentação por módulo · iLabMedSys", "", "telas").replace("</head>", '<link rel="stylesheet" href="portal/telas.css"><link rel="stylesheet" href="portal/versao.css"></head>', 1) + f"""
<main class="td-pagina">
  <h1>Documentação por módulo</h1>
  <div class="td-vs">
    <div class="versao-seletor" role="group" aria-label="Versão do sistema"><span class="vs-rotulo">Versão:</span>
      <button type="button" class="vs-btn" data-set-versao="legado" aria-pressed="true">Legado</button>
      <button type="button" class="vs-btn" data-set-versao="novo" aria-pressed="false">Novo</button></div>
    <p class="td-vs-desc" data-so-versao="legado">Legado: o sistema entregue pelo fornecedor, analisado e testado. A escolha acompanha você nas páginas das telas.</p>
    <p class="td-vs-desc" data-so-versao="novo" hidden>Novo: a versão nova (o mesmo sistema com ferramentas atualizadas). {total_validadas} de {total_novo} telas já têm conteúdo validado; as demais aparecem como “ainda não validada nesta versão”. O ideal é um só e vale para as duas versões.</p>
  </div>
  <div class="td-filtros" role="search">
    <label class="td-f"><span>Buscar tela</span><input id="td-busca" type="search" placeholder="Nome da tela" autocomplete="off"></label>
    <label class="td-f"><span>Módulo</span><select id="td-mod"><option value="">Todos</option>{opcoes_mod}</select></label>
    <label class="td-f" data-so-versao="legado"><span>Situação</span><select id="td-sit"><option value="">Todas</option>{opcoes_sit}</select></label>
    <label class="td-f" data-so-versao="novo" hidden><span>Situação</span><select id="td-sitn"><option value="">Todas</option>{opcoes_sit_n}</select></label>
    <label class="td-so"><input id="td-so" type="checkbox"> <span data-so-versao="legado">Só telas com página própria</span><span data-so-versao="novo" hidden>Só telas com conteúdo validado</span></label>
    <span class="td-acoes"><button type="button" id="td-abrir">Abrir tudo</button><button type="button" id="td-fechar">Fechar tudo</button></span>
  </div>
  <p id="td-nada" hidden>Nenhuma tela encontrada com esses filtros.</p>
  <div class="td-arvore" data-so-versao="legado">{"".join(corpo)}</div>
  <div class="td-arvore" data-so-versao="novo" hidden>{arvore_novo or '<p class="td-vazio">A versão nova ainda não tem telas listadas.</p>'}</div>
</main>
<script src="portal/versao.js"></script>
<script>
(function(){{
  var b=document.getElementById('td-busca'),s=document.getElementById('td-so'),sm=document.getElementById('td-mod'),ss=document.getElementById('td-sit'),ssn=document.getElementById('td-sitn'),nada=document.getElementById('td-nada');
  function ativa(){{return document.querySelector('.td-arvore:not([hidden])');}}
  function versao(){{return window.ilmsVersao?window.ilmsVersao.atual():'legado';}}
  function norm(x){{return x.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();}}
  function filtrar(){{
    var A=ativa(); if(!A)return;
    var q=norm(b.value),so=s.checked,mod=sm.value,sit=(versao()==='novo'?ssn:ss).value,total=0,filtro=!!(q||so||mod||sit);
    document.querySelectorAll('.td-arvore').forEach(function(ar){{ar.querySelectorAll('.td-tela,.td-menu,.td-mod').forEach(function(x){{if(ar!==A)x.hidden=false;}});}});
    A.querySelectorAll('.td-tela').forEach(function(li){{
      var ok=(!q||li.dataset.nome.indexOf(q)>=0)&&(!so||li.dataset.tem==='1')&&(!sit||li.dataset.sit===sit)&&(!mod||li.closest('.td-mod').dataset.modulo===mod);
      li.hidden=!ok; if(ok)total++;
    }});
    A.querySelectorAll('.td-menu').forEach(function(d){{var vis=d.querySelectorAll('.td-tela:not([hidden])').length; d.hidden=filtro&&!vis; if(filtro&&vis)d.open=true;}});
    A.querySelectorAll('.td-mod').forEach(function(d){{var vis=d.querySelectorAll('.td-tela:not([hidden])').length; d.hidden=filtro&&!vis; if(filtro&&vis)d.open=true;}});
    nada.hidden=!filtro||total>0;
  }}
  [b,sm,ss,ssn].forEach(function(e){{e.addEventListener('input',filtrar);}}); s.addEventListener('change',filtrar);
  document.addEventListener('ilms-versao',function(){{abrirHash();filtrar();}});
  function todos(v){{ativa().querySelectorAll('.td-mod,.td-menu').forEach(function(d){{if(!d.hidden)d.open=v;}});}}
  document.getElementById('td-abrir').addEventListener('click',function(){{todos(true);}});
  document.getElementById('td-fechar').addEventListener('click',function(){{todos(false);}});
  function abrirHash(){{
    var h=location.hash; if(!h)return;
    var id=h.slice(1).replace(/^mn?-/,''), a=document.getElementById((versao()==='novo'?'mn-':'m-')+id);
    if(a&&a.tagName==='DETAILS')a.open=true;
  }}
  abrirHash(); filtrar();
}})();
</script>
""" + rodape(""))


ICO_MOD = "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z'/%3E%3Cpath d='M8.5 12l2.5 2.5 4.5-5'/%3E%3C/svg%3E\")"
ICO_PASTA = "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'/%3E%3C/svg%3E\")"
ICO_TELA = "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 3h8l4 4v14H6z'/%3E%3Cpath d='M14 3v4h4M9 12h6M9 16h6'/%3E%3C/svg%3E\")"

CSS = """/* Página Documentação por módulo (telas por módulo). */
.td-pagina{max-width:900px;margin:0 auto;padding:24px 16px 64px}
.td-pagina h1{font-family:Manrope,Inter,sans-serif;margin:0 0 14px}
.td-filtros{display:flex;flex-wrap:wrap;gap:14px;align-items:end;margin:0 0 16px;position:sticky;top:0;z-index:5;padding:10px 0;background:var(--fundo,#f4f6f9)}
.td-f span{display:block;font-size:.8rem;margin-bottom:3px}
.td-f input,.td-f select{min-width:200px;padding:8px 10px;border:1px solid #c7ced6;border-radius:8px;background:transparent;color:inherit;font:inherit}
.td-so{display:flex;gap:6px;align-items:center;padding-bottom:8px}
.td-acoes{display:flex;gap:6px;margin-left:auto;padding-bottom:4px}
.td-acoes button{font:inherit;font-size:.85rem;padding:6px 10px;border:1px solid #c7ced6;border-radius:8px;background:transparent;color:inherit;cursor:pointer}
.td-acoes button:hover{border-color:#1f5f8b}
.td-arvore{border:1px solid #d9dee4;border-radius:12px;padding:6px 8px}
.td-mod,.td-menu{margin:0}
.td-mod>summary,.td-menu>summary{cursor:pointer;list-style:none;display:flex;align-items:center;gap:8px;padding:9px 8px;border-radius:8px}
.td-mod>summary::-webkit-details-marker,.td-menu>summary::-webkit-details-marker{display:none}
.td-mod>summary::after,.td-menu>summary::after{content:"▸";margin-left:auto;font-size:.8em;transition:transform .15s;opacity:.6}
.td-mod[open]>summary::after,.td-menu[open]>summary::after{transform:rotate(90deg)}
.td-mod>summary:hover,.td-menu>summary:hover{background:rgba(128,128,128,.12)}
.td-mod>summary{font-weight:700;font-size:1.02rem}
.td-menu>summary{font-weight:600}
.td-mod-n{font-weight:400;font-size:.8rem;opacity:.7}
.td-mod>.td-dossie{margin:0 0 4px 14px}
.td-mod>.td-menu,.td-mod>.td-vazio{margin-left:14px;border-left:1px solid #d9dee4;padding-left:8px}
.td-lista{list-style:none;margin:0 0 4px 12px;padding:0 0 0 8px;border-left:1px solid #d9dee4}
.td-tela,.td-item{display:flex;align-items:center;gap:8px;padding:5px 8px;border-radius:8px}
.td-tela[hidden],.td-menu[hidden],.td-mod[hidden]{display:none}
.td-tela a,.td-item a,.td-tela span:not(.td-ico){color:inherit;text-decoration:none;font-size:.93rem}
.td-tela a,.td-item a{color:#1f5f8b;font-weight:600}
.td-tela a:hover,.td-tela a:focus-visible,.td-item a:hover{text-decoration:underline}
.td-sem a{color:inherit;font-weight:400;opacity:.8}
.td-ico{display:inline-block;width:18px;height:18px;flex:none;background-color:currentColor;-webkit-mask:var(--ico) center/contain no-repeat;mask:var(--ico) center/contain no-repeat;opacity:.8}
.td-i-mod{--ico:__MOD__;width:20px;height:20px;color:#1f5f8b;opacity:1}
.td-i-pasta{--ico:__PASTA__}
.td-i-tela{--ico:__TELA__;width:16px;height:16px}
.td-vazio{opacity:.85;padding:4px 8px}
@media (max-width:640px){.td-acoes{margin-left:0}}
:root[data-theme="dark"] .td-f input,:root[data-theme="dark"] .td-f select,:root[data-theme="dark"] .td-acoes button{border-color:#3b4655}
:root[data-theme="dark"] .td-arvore{border-color:#323c49}
:root[data-theme="dark"] .td-mod>.td-menu,:root[data-theme="dark"] .td-mod>.td-vazio,:root[data-theme="dark"] .td-lista{border-left-color:#323c49}
:root[data-theme="dark"] .td-filtros{background:var(--fundo,#101418)}
:root[data-theme="dark"] .td-tela a,:root[data-theme="dark"] .td-item a{color:#7cbfe6}
:root[data-theme="dark"] .td-i-mod{color:#7cbfe6}
@media (prefers-color-scheme:dark){
:root:not([data-theme="light"]) .td-f input,:root:not([data-theme="light"]) .td-f select,:root:not([data-theme="light"]) .td-acoes button{border-color:#3b4655}
:root:not([data-theme="light"]) .td-arvore{border-color:#323c49}
:root:not([data-theme="light"]) .td-mod>.td-menu,:root:not([data-theme="light"]) .td-mod>.td-vazio,:root:not([data-theme="light"]) .td-lista{border-left-color:#323c49}
:root:not([data-theme="light"]) .td-filtros{background:var(--fundo,#101418)}
:root:not([data-theme="light"]) .td-tela a,:root:not([data-theme="light"]) .td-item a{color:#7cbfe6}
:root:not([data-theme="light"]) .td-i-mod{color:#7cbfe6}}
""".replace("__MOD__", ICO_MOD).replace("__PASTA__", ICO_PASTA).replace("__TELA__", ICO_TELA)
