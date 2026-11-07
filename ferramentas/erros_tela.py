"""Botão "Erros" por tela, no Legado e no Novo.

Liga cada defeito registrado à tela (ou às telas) a que ele se refere e monta a página "Erros desta tela".

Fontes (lidas de homologacao/, nada é copiado à mão):
  legado  <módulo>/defeitos/defeitos-completo.json                 (campo "tela" de cada defeito)
  novo    versao-nova/<módulo>/defeitos/DV-*-N-*.md               (linha "Tela" da tabela do cabeçalho)
  nomes   <módulo>/11-inventario-de-telas.md                       (lista de telas de cada módulo)
  ajustes portal-equivalencia-telas.csv                            (texto do defeito -> tela do inventário)

Como o defeito encontra a tela:
  1. o texto do campo "Tela" (sem o que está entre parênteses) é comparado com o nome de cada tela do inventário;
     um defeito pode citar mais de uma tela ("A e B") e aparece em todas;
  2. o que não casar é procurado no arquivo de equivalência, que a pessoa responsável pode corrigir à mão;
  3. o que continuar sem tela vai para a lista "Sem tela associada" do módulo. Nada é descartado em silêncio.

`--atualizar-equivalencia` só ACRESCENTA ao CSV os textos que ainda não têm linha (com a tela em branco, "a classificar":
na dúvida não há palpite); linha existente nunca é alterada."""
import csv
import html
import json
import re
import shutil
from pathlib import Path

import higiene
import telas_devs

E = html.escape
CSV_NOME = "portal-equivalencia-telas.csv"
CAMPOS = ["versao", "modulo", "texto_do_defeito", "tela_do_inventario", "revisado", "origem"]
PASTAS_NOVO = {"principal": "1.principal", "estoque": "3.estoque", "controle-qualidade": "4.controle_qualidade",
               "garantia-qualidade": "5.garantia_qualidade", "controle-documentos": "6.controle_documento"}
COR_GRAV = {"Crítica": "#7a1020", "Alta": "#b3261e", "Média": "#b26a00", "Baixa": "#3f6aa0"}
ORDEM_GRAV = {"Crítica": 0, "Alta": 1, "Média": 2, "Baixa": 3}


def _norm(s):
    return telas_devs._norm(re.sub(r"\s*\(.*?\)", "", s or ""))


def _segmento(tela):
    """Último trecho de "Menu › Tela" (o que importa para achar a tela)."""
    return (tela or "").split("›")[-1].strip()


def carregar_legado(hom, mid):
    pasta = telas_devs.DIRS.get(mid)
    arq = Path(hom) / pasta / "defeitos" / "defeitos-completo.json" if pasta else None
    if not arq or not arq.exists():
        return []
    out = []
    for d in json.loads(arq.read_text(encoding="utf-8")).get("defeitos", []):
        out.append({"id": d["id"], "titulo": d.get("titulo", ""), "gravidade": d.get("gravidade", ""), "situacao": d.get("situacao") or "Aberto",
                    "tipo": d.get("tipo", ""), "tela_txt": d.get("tela", ""), "resumo": d.get("resumo", ""), "passos": d.get("passos") or [],
                    "esperado": d.get("esperado", ""), "obtido": d.get("obtido", ""), "responsavel": "",
                    "evid": [(e.get("arquivo"), e.get("legenda", "")) if isinstance(e, dict) else (e, "") for e in d.get("evidencias") or []], "pasta": pasta})
    return out


def carregar_novo(hom, mid):
    pasta = PASTAS_NOVO.get(mid)
    if not pasta:
        return []
    out = []
    for arq in sorted((Path(hom) / "versao-nova" / pasta / "defeitos").glob("DV-*.md")):
        t = arq.read_text(encoding="utf-8")
        m = re.match(r"#\s*(DV-[\w-]+):\s*(.+)", t)
        if not m:
            continue
        campos = {k.strip(): v.strip() for k, v in re.findall(r"^\|\s*\*\*(.+?)\*\*\s*\|\s*(.*?)\s*\|\s*$", t, re.M)}

        def secao(nome):
            s = re.search(rf"^##\s*{nome}[^\n]*\n(.*?)(?=^##\s|\Z)", t, re.M | re.S)
            return s.group(1).strip() if s else ""
        out.append({"id": m.group(1), "titulo": m.group(2).strip(), "gravidade": campos.get("Gravidade", ""), "situacao": campos.get("Situação") or "Aberto",
                    "tipo": campos.get("Tipo", ""), "tela_txt": campos.get("Tela", ""), "resumo": "", "passos": [secao("Passos para reproduzir")],
                    "esperado": secao("Esperado"), "obtido": secao("Obtido"), "responsavel": campos.get("Responsável pela correção", ""),
                    "evid": [(n, "") for n in re.findall(r"[\w./\-]+\.(?:png|jpg|jpeg)", campos.get("Evidência", ""))], "pasta": "versao-nova/" + pasta})
    return out


def _ler_csv(hom):
    arq = Path(hom) / CSV_NOME
    if not arq.exists():
        return []
    with arq.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def associar(defeitos, telas, ajustes, versao, mid):
    """telas = [{chave, nome}]. Devolve ({chave: [defeitos]}, [defeitos sem tela], [textos sem tela])."""
    por_tela = {t["chave"]: [] for t in telas}
    ajuste = {}
    for r in ajustes:
        if r["versao"] == versao and r["modulo"] == mid and r["tela_do_inventario"].strip():
            ajuste.setdefault(_norm(r["texto_do_defeito"]), set()).add(_norm(r["tela_do_inventario"]))
    sem, textos = [], set()
    for d in defeitos:
        alvo = _norm(d["tela_txt"])
        padded = f" {alvo} "
        achou = {t["chave"] for t in telas if len(t["chave"]) >= 4 and f" {t['chave']} " in padded}
        if not achou:
            seg = _norm(_segmento(d["tela_txt"]))
            for k in (alvo, seg):
                if k in ajuste:
                    achou |= {x for x in ajuste[k] if x in por_tela}
                    break
        if achou:
            for k in achou:
                por_tela[k].append(d)
        else:
            sem.append(d)
            textos.add(d["tela_txt"])
    return por_tela, sem, sorted(textos)


def carregar_provisorias(hom, mid):
    """Telas provisorias da versao nova (cartao "API conectada" ou "Tela em integracao"): nao sao defeito. Lidas das tabelas das rodadas:
    telas-provisorias.md (coluna "Tela") e, nos resultado.md, as tabelas logo abaixo de um titulo que fala de provisorias."""
    pasta = PASTAS_NOVO.get(mid)
    out = set()
    if not pasta:
        return out
    base = Path(hom) / "versao-nova" / pasta / "execucao"
    for arq in list(base.glob("*/telas-provisorias.md")) + list(base.glob("*/resultado.md")):
        so_titulo_provisoria = arq.name == "resultado.md"
        titulo_ok = not so_titulo_provisoria
        cols = None
        for linha in arq.read_text(encoding="utf-8").splitlines():
            if linha.startswith("#"):
                titulo_ok = (not so_titulo_provisoria) or ("provis" in linha.lower())
                cols = None
                continue
            if not (linha.startswith("|") and titulo_ok):
                if not linha.startswith("|"):
                    cols = None
                continue
            cel = [c.strip() for c in linha.strip().strip("|").split("|")]
            if cols is None:
                cols = [c.lower() for c in cel]
                continue
            if set("".join(cel)) <= set("-: "):
                continue
            if "tela" in cols and cols.index("tela") < len(cel):
                nome = re.sub(r"[*`]", "", cel[cols.index("tela")]).strip()
                if nome:
                    out.add(_norm(nome))
    return out


def montar(hom, registro):
    """{(versao, módulo): {"por_tela": {...}, "sem": [...], "textos_sem": [...], "total": n}} para todos os módulos com telas."""
    ajustes = _ler_csv(hom)
    out = {}
    for mid, rm in registro.items():
        telas = [{"chave": t["chave"], "nome": t["nome"]} for t in rm["telas"]]
        if not telas:
            continue
        for versao, carga in (("legado", carregar_legado), ("novo", carregar_novo)):
            defs = carga(hom, mid)
            por_tela, sem, textos = associar(defs, telas, ajustes, versao, mid)
            out[(versao, mid)] = {"por_tela": por_tela, "sem": sem, "textos_sem": textos, "total": len(defs),
                                  "prov": carregar_provisorias(hom, mid) if versao == "novo" else set()}
    return out


def atualizar_equivalencia(hom, dados, registro):
    """Acrescenta ao CSV as linhas que faltam (nunca altera as existentes). Devolve quantas acrescentou."""
    arq = Path(hom) / CSV_NOME
    existentes = _ler_csv(hom)
    tem = {(r["versao"], r["modulo"], _norm(r["texto_do_defeito"])) for r in existentes}
    novas = []
    for (versao, mid), d in sorted(dados.items()):
        nomes = {t["chave"]: t["nome"] for t in registro[mid]["telas"]}
        for txt in d["textos_sem"]:
            if (versao, mid, _norm(txt)) in tem:
                continue
            tem.add((versao, mid, _norm(txt)))
            novas.append({"versao": versao, "modulo": mid, "texto_do_defeito": txt, "tela_do_inventario": "", "revisado": "não", "origem": "a classificar"})
    if novas:
        novo_arquivo = not arq.exists()
        with arq.open("a", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=CAMPOS)
            if novo_arquivo:
                w.writeheader()
            w.writerows(novas)
    return len(novas)


def contagem(dados, versao, mid, chave):
    d = dados.get((versao, mid))
    return None if d is None else len(d["por_tela"].get(chave, []))


def botao(href, n, versao="legado"):
    """Botão ao lado das abas da tela. n = quantidade de erros ligados à tela (None se o módulo não tem registro de defeitos)."""
    if n is None:
        return f'<span class="aba-extra aba-apagada" aria-disabled="true" title="Este módulo ainda não tem defeitos registrados">Erros</span>'
    rot = f"Erros ({n})" if n else "Erros"
    classe = f"aba-extra aba-erros aba-erros-{versao}" + (" aba-erros-zero" if not n else "")
    return f'<a class="{classe}" href="{href}">{rot}</a>'


_EVID_CACHE = {}


def _achar_evidencia(hom, pasta, arquivo):
    """Caminho da captura no repositório da homologação. Legado: relativo a homologacao/<módulo>/. Novo: só o nome do arquivo, procurado em execucao/**/evidencias/."""
    base = Path(hom) / pasta
    direto = base / arquivo
    if direto.exists():
        return direto
    achados = list(base.glob(f"execucao/**/evidencias/{Path(arquivo).name}"))
    return achados[0] if achados else None


def copiar_evidencia(hom, destino, mid, d, i):
    """Copia (reduzida a 1200 px de largura) a i-ésima captura do defeito para documentacao/img/<módulo>/erros/ e devolve o nome do arquivo (ou None)."""
    chave = (d["id"], i)
    if chave in _EVID_CACHE:
        return _EVID_CACHE[chave]
    arq, _leg = d["evid"][i]
    fonte = _achar_evidencia(hom, d["pasta"], arq) if arq else None
    nome = None
    if fonte:
        nome = f'{d["id"].lower()}-{i + 1}.png'
        pasta_dest = Path(destino) / "documentacao/img" / mid / "erros"
        pasta_dest.mkdir(parents=True, exist_ok=True)
        try:
            from PIL import Image
            im = Image.open(fonte)
            if im.width <= 1200:
                shutil.copy2(fonte, pasta_dest / nome)  # já é pequena: copia sem mexer
            else:
                im = im.convert("RGB").resize((1200, round(im.height * 1200 / im.width)))
                im.quantize(colors=256).save(pasta_dest / nome, optimize=True)
        except Exception:
            nome = None
    _EVID_CACHE[chave] = nome
    return nome


def _sem_marcador(linha):
    """Tira o "1.", "1)" ou "-" do começo da linha (a lista numerada do HTML já numera)."""
    return re.sub(r"^\s*(?:\d+[.)]|[-*])\s*", "", linha)


def _lista(texto):
    """Linhas do texto, sem as marcas de formatação do Markdown (** e crases) e já passadas pela higiene."""
    limpo = re.sub(r"\*\*|`", "", higiene.redigir(texto))
    return [x for x in re.split(r"\n+", limpo) if x.strip()]


def _cartao(d, versao, href_defeito, imgs=()):
    """imgs = [(url relativo da captura, legenda)]. Passo a passo, esperado, obtido e capturas ficam sempre visíveis."""
    cor = COR_GRAV.get(d["gravidade"], "#6b7785")
    partes = [f'<span class="er-grav" style="--cor:{cor}">{E(d["gravidade"] or "—")}</span>', f'<span class="er-sit">{E(d["situacao"])}</span>']
    if d["tipo"]:
        partes.append(f'<span class="er-tipo">{E(d["tipo"])}</span>')
    if d["responsavel"]:
        partes.append(f'<span class="er-resp">Corrige: {E(higiene.redigir(d["responsavel"]))}</span>')
    link = f' <a class="er-link" href="{href_defeito}">ver o defeito completo</a>' if href_defeito else ""
    corpo = ""
    if d["resumo"]:
        corpo += f'<p>{E(higiene.redigir(d["resumo"]))}</p>'
    passos = [l for p in d["passos"] if p and p.strip() for l in _lista(p)]
    if passos:
        corpo += '<p class="er-rot">Como reproduzir o erro, passo a passo</p><ol class="er-passos">' + "".join("<li>" + E(_sem_marcador(l)) + "</li>" for l in passos) + "</ol>"
    else:
        corpo += '<p class="er-rot">Como reproduzir o erro, passo a passo</p><p class="er-vazio">O passo a passo ainda não foi registrado neste defeito.</p>'
    for rot, k in (("Esperado", "esperado"), ("Obtido", "obtido")):
        if d[k] and d[k].strip():
            corpo += f'<p class="er-rot">{rot}</p>' + "".join(f"<p>{E(l)}</p>" for l in _lista(d[k]))
    if imgs:
        corpo += '<p class="er-rot">Evidência (captura da tela)</p><div class="er-evid">' + "".join(
            f'<figure><a href="{E(u)}" target="_blank" rel="noopener"><img src="{E(u)}" alt="{E(l or "Captura da tela do defeito " + d["id"])}" loading="lazy"></a>'
            + (f"<figcaption>{E(higiene.redigir(l))}</figcaption>" if l else "") + "</figure>" for u, l in imgs) + "</div>"
    else:
        corpo += '<p class="er-vazio">Sem captura de tela registrada para este defeito.</p>'
    return (f'<article class="er-cartao er-v-{versao}" id="{E(d["id"].lower())}"><header><h3>{E(d["id"])} · {E(higiene.redigir(d["titulo"]))}</h3>'
            f'<p class="er-meta">{" ".join(partes)}{link}</p></header>{corpo}</article>')


def pagina(mod, t, versao, dados, cabecalho, rodape, barra, raiz, href_defeitos, href_sem_tela, outra_versao, imagens=None, lateral="", abas="", selo=""):
    """Página "Erros desta tela". href_defeitos = página do registro completo (só legado); outra_versao = (rótulo, href)."""
    d = dados[(versao, mod["id"])]
    lista = sorted(d["por_tela"].get(t["chave"], []), key=lambda x: (ORDEM_GRAV.get(x["gravidade"], 9), x["id"]))
    rot_v = "legado" if versao == "legado" else "versão nova"
    if lista:
        miolo = "".join(_cartao(x, versao, f"{href_defeitos}#{x['id'].lower()}" if href_defeitos else "", imagens(x) if imagens else ()) for x in lista)
        resumo = f'<p class="nv-meta">{len(lista)} erro(s) registrado(s) nesta tela, do mais grave ao menos grave.</p>'
    else:
        situ = t.get("situacao") or ""
        if versao == "legado" and situ and situ != "Não testada":
            msg = f'Nenhum erro registrado para esta tela (situação no inventário: {E(situ)}). Isso vale só para o que foi testado.'
        elif versao == "novo" and t["chave"] in d.get("prov", set()):
            msg = ("<strong>Tela provisória (a desenvolver).</strong> A versão nova ainda não construiu esta tela: ela abre só um cartão, sem pesquisa, lista nem botões. "
                   "Isso <strong>não é defeito</strong> e, por isso, não há erros registrados. Quando a tela for desenvolvida, ela entra nos testes.")
        elif versao == "novo" and not t.get("validada"):
            msg = "Esta tela ainda não foi validada na versão nova; por isso não há erros registrados. Não significa que esteja correta."
        else:
            msg = "Nenhum erro registrado para esta tela. Isso vale só para o que foi testado."
        miolo = f'<div class="callout nv-aviso"><p class="callout-titulo">Sem erros registrados</p><p>{msg}</p></div>'
        resumo = ""
    aviso_novo = ('<p class="nv-meta er-aviso-novo">A versão nova ainda está em construção: telas provisórias (só um cartão) não são defeito e não aparecem como erro.</p>'
                  if versao == "novo" else "")
    rodape_lista = (f'<p class="nv-meta">Defeitos do módulo que não foram ligados a nenhuma tela: <a href="{href_sem_tela}">{len(d["sem"])}</a>. '
                    f'Total registrado no módulo ({rot_v}): {d["total"]}.</p>')
    titulo = f'Erros · {t["nome"]} · {rot_v} · {mod["nome"]} · iLabMedSys'
    if lateral:
        return _moldura(mod, titulo, f'{t["nome"]}: Erros', versao, raiz, cabecalho, rodape, lateral, barra, abas, selo,
                        f'<article class="texto texto-largo">{aviso_novo}{resumo}{miolo}{rodape_lista}</article>', t["nome"])
    return (cabecalho(titulo, raiz).replace("</head>", f'<link rel="stylesheet" href="{raiz}portal/versao.css">\n</head>', 1)
            .replace("<body ", f'<body data-versao-pagina="{versao}" ', 1) + f"""
<main class="nv-pagina" id="conteudo">
  <nav class="trilha" aria-label="Você está em"><a href="{raiz}index.html">Início</a> › <a href="{raiz}documentacao/{mod['id']}/index.html">{E(mod['nome'])}</a> › <span>{E(t['nome'])}</span> › <span>Erros</span></nav>
  {barra}
  <header class="doc-cabecalho"><h1>{E(t['nome'])} <span class="sit-sufixo">· erros · {rot_v}</span></h1>{resumo}</header>
  <article class="texto texto-largo">{aviso_novo}{miolo}{rodape_lista}</article>
</main>
""" + rodape(raiz))


def _moldura(mod, titulo, h1, versao, raiz, cabecalho, rodape, lateral, barra, abas, selo, artigo, nome_tela, final="Erros"):
    """Mesma moldura das páginas de documento do portal: barra lateral do módulo, trilha, título, faixa de versão, abas da tela e situação."""
    return (cabecalho(titulo, raiz).replace("</head>", f'<link rel="stylesheet" href="{raiz}portal/versao.css">\n</head>', 1)
            .replace("<body ", f'<body data-versao-pagina="{versao}" ', 1) + f"""
<div class="doc-layout">
  {lateral}
  <main class="doc" id="conteudo">
    <nav class="trilha" aria-label="Você está em"><a href="{raiz}index.html">Início</a> › <a href="{raiz}documentacao/{mod['id']}/index.html">{E(mod['nome'])}</a> › <span>{E(nome_tela)}</span>{(' › <span>' + final + '</span>') if final else ''}</nav>
    <header class="doc-cabecalho"><h1>{E(h1)}</h1></header>
    {barra}{abas}{selo}
    {artigo}
  </main>
</div>
""" + rodape(raiz))


def pagina_sem_tela(mod, versao, dados, cabecalho, rodape, barra, raiz, href_defeitos, imagens=None, lateral="", abas="", selo=""):
    d = dados[(versao, mod["id"])]
    rot_v = "legado" if versao == "legado" else "versão nova"
    lista = sorted(d["sem"], key=lambda x: (ORDEM_GRAV.get(x["gravidade"], 9), x["id"]))
    linhas = "".join(f'<tr><td>{E(x["id"])}</td><td>{E(x["gravidade"])}</td><td>{E(x["situacao"])}</td><td>{E(higiene.redigir(x["titulo"]))}</td><td>{E(higiene.redigir(x["tela_txt"]))}</td></tr>' for x in lista)
    corpo = (f'<table class="tabela"><thead><tr><th>Defeito</th><th>Gravidade</th><th>Situação</th><th>Título</th><th>Tela citada no defeito</th></tr></thead><tbody>{linhas}</tbody></table>'
             if lista else "<p>Todos os defeitos deste módulo estão ligados a uma tela.</p>")
    cartoes = "".join(_cartao(x, versao, f"{href_defeitos}#{x['id'].lower()}" if href_defeitos else "", imagens(x) if imagens else ()) for x in lista)
    cartoes = f'<h2>Cada defeito, com o passo a passo e as capturas</h2>{cartoes}' if cartoes else ""
    titulo = f'Defeitos sem tela associada · {rot_v} · {mod["nome"]} · iLabMedSys'
    if lateral:
        explica = ('<p class="nv-meta">São defeitos cujo campo "Tela" não bate com nenhuma tela do inventário (por exemplo, citam mais de uma tela com outro nome). '
                   'Nada foi descartado: eles estão aqui até alguém indicar a tela no arquivo de equivalência.</p>')
        return _moldura(mod, titulo, "Defeitos sem tela associada", versao, raiz, cabecalho, rodape, lateral, barra, abas, selo,
                        f'<article class="texto texto-largo">{explica}{corpo}{cartoes}</article>', "Sem tela associada", final="")
    return (cabecalho(titulo, raiz).replace("</head>", f'<link rel="stylesheet" href="{raiz}portal/versao.css"></head>', 1)
            .replace("<body ", f'<body data-versao-pagina="{versao}" ', 1) + f"""
<main class="nv-pagina" id="conteudo">
  <nav class="trilha" aria-label="Você está em"><a href="{raiz}index.html">Início</a> › <a href="{raiz}documentacao/{mod['id']}/index.html">{E(mod['nome'])}</a> › <span>Sem tela associada</span></nav>
  {barra}
  <header class="doc-cabecalho"><h1>Defeitos sem tela associada <span class="sit-sufixo">· {rot_v}</span></h1>
  <p class="nv-meta">São defeitos cujo campo "Tela" não bate com nenhuma tela do inventário (por exemplo, citam mais de uma tela com outro nome). Nada foi descartado: eles estão aqui até alguém indicar a tela no arquivo de equivalência.</p></header>
  <article class="texto texto-largo">{corpo}{cartoes}</article>
</main>
""" + rodape(raiz))


CSS = """
.aba-erros{font-weight:700}
.aba-erros-legado{border-color:#b3261e!important;color:#b3261e!important}
.aba-erros-novo{border-color:#1769aa!important;color:#1769aa!important}
.abas-tela a.aba-erros[aria-current=page]{color:#fff!important;border-style:solid!important}
.abas-tela a.aba-erros-legado[aria-current=page]{background:#b3261e!important;border-color:#b3261e!important}
.abas-tela a.aba-erros-novo[aria-current=page]{background:#1769aa!important;border-color:#1769aa!important}
.aba-erros-zero{border-color:var(--laranja2)!important;color:var(--tinta)!important;font-weight:600}
.er-cartao{border:1px solid var(--linha,#d9dde3);border-radius:10px;padding:12px 16px;margin:12px 0;background:var(--painel,#fff)}
.er-cartao h3{margin:0 0 6px;font-size:1rem}
.er-v-legado{border-left:6px solid #b3261e}
.er-v-novo{border-left:6px solid #1769aa}
.er-aviso-novo{border-left:4px solid #1769aa;padding-left:10px}
.er-meta{margin:0;display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:.88rem}
.er-grav{background:var(--cor);color:#fff;border-radius:999px;padding:2px 10px;font-weight:700}
.er-sit,.er-tipo,.er-resp{border:1px solid var(--linha,#d9dde3);border-radius:999px;padding:2px 10px}
.er-rot{font-weight:700;margin:10px 0 2px}
.er-passos{margin:4px 0 8px 1.2em;padding:0}.er-passos li{margin:3px 0}
.er-vazio{opacity:.7;font-style:italic;margin:6px 0}
.er-evid{display:flex;flex-wrap:wrap;gap:12px;margin:6px 0}
.er-evid figure{margin:0;max-width:340px}.er-evid img{width:100%;height:auto;border:1px solid var(--linha,#d9dde3);border-radius:6px;display:block}
.er-evid figcaption{font-size:.82rem;opacity:.8;margin-top:3px}
"""
