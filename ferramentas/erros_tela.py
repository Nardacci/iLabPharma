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
                    "esperado": d.get("esperado", ""), "obtido": d.get("obtido", ""), "responsavel": ""})
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
                    "esperado": secao("Esperado"), "obtido": secao("Obtido"), "responsavel": campos.get("Responsável pela correção", "")})
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
            out[(versao, mid)] = {"por_tela": por_tela, "sem": sem, "textos_sem": textos, "total": len(defs)}
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


def botao(href, n, tela_testada=True):
    """Botão ao lado das abas da tela. n = quantidade de erros ligados à tela (None se o módulo não tem registro de defeitos)."""
    if n is None:
        return f'<span class="aba-extra aba-apagada" aria-disabled="true" title="Este módulo ainda não tem defeitos registrados">Erros</span>'
    rot = f"Erros ({n})" if n else "Erros"
    classe = "aba-extra aba-erros" + (" aba-erros-zero" if not n else "")
    return f'<a class="{classe}" href="{href}">{rot}</a>'


def _lista(texto):
    return [x for x in re.split(r"\n+", higiene.redigir(texto)) if x.strip()]


def _cartao(d, versao, href_defeito):
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
    passos = [p for p in d["passos"] if p and p.strip()]
    if passos:
        corpo += "<p class=\"er-rot\">Como reproduzir</p><ol>" + "".join(f"<li>{E(l)}</li>" for p in passos for l in _lista(p)) + "</ol>"
    for rot, k in (("Esperado", "esperado"), ("Obtido", "obtido")):
        if d[k] and d[k].strip():
            corpo += f'<p class="er-rot">{rot}</p>' + "".join(f"<p>{E(l)}</p>" for l in _lista(d[k]))
    return (f'<article class="er-cartao" id="{E(d["id"].lower())}"><header><h3>{E(d["id"])} · {E(higiene.redigir(d["titulo"]))}</h3>'
            f'<p class="er-meta">{" ".join(partes)}{link}</p></header><details{" open" if len(corpo) < 900 else ""}><summary>Detalhes</summary>{corpo}</details></article>')


def pagina(mod, t, versao, dados, cabecalho, rodape, barra, raiz, href_defeitos, href_sem_tela, outra_versao):
    """Página "Erros desta tela". href_defeitos = página do registro completo (só legado); outra_versao = (rótulo, href)."""
    d = dados[(versao, mod["id"])]
    lista = sorted(d["por_tela"].get(t["chave"], []), key=lambda x: (ORDEM_GRAV.get(x["gravidade"], 9), x["id"]))
    rot_v = "legado" if versao == "legado" else "versão nova"
    if lista:
        miolo = "".join(_cartao(x, versao, f"{href_defeitos}#{x['id'].lower()}" if href_defeitos else "") for x in lista)
        resumo = f'<p class="nv-meta">{len(lista)} erro(s) registrado(s) nesta tela, do mais grave ao menos grave.</p>'
    else:
        situ = t.get("situacao") or ""
        if versao == "legado" and situ and situ != "Não testada":
            msg = f'Nenhum erro registrado para esta tela (situação no inventário: {E(situ)}). Isso vale só para o que foi testado.'
        elif versao == "novo" and not t.get("validada"):
            msg = "Esta tela ainda não foi validada na versão nova; por isso não há erros registrados. Não significa que esteja correta."
        else:
            msg = "Nenhum erro registrado para esta tela. Isso vale só para o que foi testado."
        miolo = f'<div class="callout nv-aviso"><p class="callout-titulo">Sem erros registrados</p><p>{msg}</p></div>'
        resumo = ""
    rodape_lista = (f'<p class="nv-meta">Defeitos do módulo que não foram ligados a nenhuma tela: <a href="{href_sem_tela}">{len(d["sem"])}</a>. '
                    f'Total registrado no módulo ({rot_v}): {d["total"]}.</p>')
    titulo = f'Erros · {t["nome"]} · {rot_v} · {mod["nome"]} · iLabMedSys'
    return (cabecalho(titulo, raiz).replace("</head>", f'<link rel="stylesheet" href="{raiz}portal/versao.css"></head>', 1)
            .replace("<body ", f'<body data-versao-pagina="{versao}" ', 1) + f"""
<main class="nv-pagina" id="conteudo">
  <nav class="trilha" aria-label="Você está em"><a href="{raiz}index.html">Início</a> › <a href="{raiz}documentacao/{mod['id']}/index.html">{E(mod['nome'])}</a> › <span>{E(t['nome'])}</span> › <span>Erros</span></nav>
  {barra}
  <header class="doc-cabecalho"><h1>{E(t['nome'])} <span class="sit-sufixo">· erros · {rot_v}</span></h1>{resumo}</header>
  <article class="texto texto-largo">{miolo}{rodape_lista}</article>
</main>
""" + rodape(raiz))


def pagina_sem_tela(mod, versao, dados, cabecalho, rodape, barra, raiz, href_defeitos):
    d = dados[(versao, mod["id"])]
    rot_v = "legado" if versao == "legado" else "versão nova"
    lista = sorted(d["sem"], key=lambda x: (ORDEM_GRAV.get(x["gravidade"], 9), x["id"]))
    linhas = "".join(f'<tr><td>{E(x["id"])}</td><td>{E(x["gravidade"])}</td><td>{E(x["situacao"])}</td><td>{E(higiene.redigir(x["titulo"]))}</td><td>{E(higiene.redigir(x["tela_txt"]))}</td></tr>' for x in lista)
    corpo = (f'<table class="tabela"><thead><tr><th>Defeito</th><th>Gravidade</th><th>Situação</th><th>Título</th><th>Tela citada no defeito</th></tr></thead><tbody>{linhas}</tbody></table>'
             if lista else "<p>Todos os defeitos deste módulo estão ligados a uma tela.</p>")
    titulo = f'Defeitos sem tela associada · {rot_v} · {mod["nome"]} · iLabMedSys'
    return (cabecalho(titulo, raiz).replace("</head>", f'<link rel="stylesheet" href="{raiz}portal/versao.css"></head>', 1)
            .replace("<body ", f'<body data-versao-pagina="{versao}" ', 1) + f"""
<main class="nv-pagina" id="conteudo">
  <nav class="trilha" aria-label="Você está em"><a href="{raiz}index.html">Início</a> › <a href="{raiz}documentacao/{mod['id']}/index.html">{E(mod['nome'])}</a> › <span>Sem tela associada</span></nav>
  {barra}
  <header class="doc-cabecalho"><h1>Defeitos sem tela associada <span class="sit-sufixo">· {rot_v}</span></h1>
  <p class="nv-meta">São defeitos cujo campo "Tela" não bate com nenhuma tela do inventário (por exemplo, citam mais de uma tela com outro nome). Nada foi descartado: eles estão aqui até alguém indicar a tela no arquivo de equivalência.</p></header>
  <article class="texto texto-largo">{corpo}</article>
</main>
""" + rodape(raiz))


CSS = """
.aba-erros{border-color:#b3261e!important;color:#b3261e!important;font-weight:700}
.aba-erros-zero{border-color:var(--laranja2)!important;color:var(--tinta)!important;font-weight:600}
.er-cartao{border:1px solid var(--linha,#d9dde3);border-radius:10px;padding:12px 16px;margin:12px 0;background:var(--painel,#fff)}
.er-cartao h3{margin:0 0 6px;font-size:1rem}
.er-meta{margin:0;display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:.88rem}
.er-grav{background:var(--cor);color:#fff;border-radius:999px;padding:2px 10px;font-weight:700}
.er-sit,.er-tipo,.er-resp{border:1px solid var(--linha,#d9dde3);border-radius:999px;padding:2px 10px}
.er-rot{font-weight:700;margin:10px 0 2px}
.er-cartao details summary{cursor:pointer;margin-top:8px}
"""
