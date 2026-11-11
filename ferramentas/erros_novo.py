"""Páginas avulsas "Erros" e "Erros da versão nova".

  erros.html        página de entrada, com o botão "Erros"
  erros-novo.html   todos os erros encontrados na versão nova, módulo a módulo, numa página só (Abrir tudo / Fechar tudo, Word),
                    com o link de cada erro para a página "Erros desta tela" (passos e evidências)

Não altera nenhuma outra página nem o menu do alto. Fonte: homologacao/versao-nova/<módulo>/defeitos/DV-<sigla>-N-*.md.
Só entra o que é informação do erro: gravidade, tipo, tela, classe, passos, esperado, obtido, impacto. Defeito descartado não entra."""
import glob
import html
import re
import shutil
from pathlib import Path

import markdown

import higiene

E = html.escape
MODS = [("principal", "Principal", "1.principal", "PRI"), ("estoque", "Estoque", "3.estoque", "EST"),
        ("garantia-qualidade", "Garantia da Qualidade", "5.garantia_qualidade", "GQ"), ("controle-documentos", "Controle de Documentos", "6.controle_documento", "DOC")]
ORDEM = {"Crítica": 0, "Alta": 1, "Média": 2, "Baixa": 3, "A confirmar": 4}
COR = {"Crítica": "#7a1020", "Alta": "#b3261e", "Média": "#b26a00", "Baixa": "#3f6aa0", "A confirmar": "#5b6472"}
CAMPOS = ["Tipo", "Tela", "Classe na versão nova", "Rodada"]
SECOES = ("Passos para reproduzir", "Passos observados", "Esperado", "Obtido", "Impacto", "Onde ver o caso")
WORD = "LabMedSys - Defeitos Encontrados na Versao Nova.docx"
CSS = """
main.conteudo{max-width:1100px;margin:0 auto;padding:1.5rem 1.25rem}
.en-card{color:inherit;text-decoration:none}
.en-card:hover{border-color:#f57c00}
.en-topo{display:flex;gap:.75rem;flex-wrap:wrap;align-items:center;margin:1rem 0}
.en-mod{margin:1.2rem 0;border:1px solid var(--borda,#d9dee6);border-radius:12px;background:var(--cartao,transparent)}
.en-mod>summary{cursor:pointer;padding:.9rem 1.1rem;font-weight:700;font-size:1.15rem;list-style:none}
.en-mod>summary small{font-weight:500;opacity:.75;margin-left:.5rem}
.en-corpo{padding:0 1.1rem 1rem}
.en-tab{width:100%;border-collapse:collapse;margin:.5rem 0 1rem;font-size:.92rem}
.en-tab th,.en-tab td{padding:.4rem .55rem;border-bottom:1px solid var(--borda,#d9dee6);text-align:left;vertical-align:top}
.en-ficha{border:1px solid var(--borda,#d9dee6);border-radius:10px;margin:.5rem 0}
.en-ficha>summary{cursor:pointer;padding:.65rem .9rem;font-weight:600;list-style:none}
.en-ficha .en-in{padding:0 .9rem .9rem}
.en-grav{display:inline-block;padding:.05rem .5rem;border-radius:999px;color:#fff;font-size:.78rem;margin-right:.4rem;background:var(--cor)}
.en-meta{font-size:.88rem;opacity:.85;margin:.2rem 0 .6rem}
.en-rot{font-weight:700;margin:.8rem 0 .2rem}
.en-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:.9rem;margin:1.2rem 0}
.en-card{border:1px solid var(--borda,#d9dee6);border-radius:12px;padding:1rem}
.en-card b{font-size:1.6rem;display:block}
.en-grande{font-size:1.15rem;padding:.9rem 2rem}
"""
JS = """
document.querySelectorAll('[data-abrir]').forEach(function(b){b.addEventListener('click',function(){
 var v=b.getAttribute('data-abrir')==='1';document.querySelectorAll('details.en-mod').forEach(function(d){d.open=v;});});});
"""


def grav(txt):
    t = (txt or "").strip().strip("*").strip().lower()
    for k in ("Crítica", "Alta", "Média", "Baixa", "Descartada"):
        if t.startswith(k.lower()):
            return k
    return "A confirmar"


def md(txt):
    return markdown.markdown(higiene.redigir(txt), extensions=["tables", "sane_lists"]).replace("<table>", '<div class="tabela"><table>').replace("</table>", "</table></div>")


def ler(f):
    t = Path(f).read_text(encoding="utf-8")
    m = re.match(r"#\s*(DV-[A-Z]+-N-\d+)\s*[:—-]?\s*(.*)", t)
    if not m:
        return None
    cab = {}
    for k in ["Gravidade"] + CAMPOS:
        x = re.search(r"\*\*%s\*\*\s*\|\s*(.*?)\s*\|\s*$" % re.escape(k), t, re.M)
        cab[k] = x.group(1).strip() if x else ""
    sec = []
    for p in re.split(r"^## ", t, flags=re.M)[1:]:
        tit, _, corpo = p.partition("\n")
        if tit.strip().startswith(SECOES) and corpo.strip():
            sec.append((tit.strip(), corpo.strip()))
    return dict(id=m.group(1), titulo=m.group(2).strip(), grav=grav(cab["Gravidade"]), cab=cab, sec=sec)


def carregar(hom):
    out = []
    for mid, nome, pasta, sigla in MODS:
        itens = [x for x in (ler(f) for f in sorted(glob.glob(str(Path(hom) / "versao-nova" / pasta / "defeitos" / f"DV-{sigla}-N-*.md")))) if x and x["grav"] != "Descartada"]
        itens.sort(key=lambda r: (ORDEM[r["grav"]], r["id"]))
        out.append((mid, nome, itens))
    return out


def links(erros, novo):
    """id do defeito -> endereço da página "Erros desta tela" (a partir da raiz do portal)."""
    out = {}
    for (v, mid), d in erros.items():
        if v != "novo" or mid not in novo:
            continue
        for t in novo[mid]["telas"]:
            for x in d["por_tela"].get(t["chave"], []):
                out.setdefault(x["id"], f"documentacao/novo/{mid}/{t['slug']}-erros.html")
        for x in d["sem"]:
            out.setdefault(x["id"], f"documentacao/novo/{mid}/sem-tela-erros.html")
    return out


def corpo_ficha(x, lig):
    a = lig.get(x["id"])
    ver = f'<p><a class="botao" href="../{a}#{x["id"].lower()}">Ver a tela do erro, com as evidências</a></p>' if a else ""
    meta = " · ".join(f"<b>{E(k)}:</b> {E(x['cab'][k])}" for k in CAMPOS if x["cab"].get(k))
    corpo = "".join(f'<p class="en-rot">{E(t)}</p>{md(c)}' for t, c in x["sec"])
    return (f'<p class="en-meta"><span class="en-grav" style="--cor:{COR[x["grav"]]}">{E(x["grav"])}</span> {meta}</p>{ver}{corpo}')


def pagina(hom, destino, erros, novo, cabecalho, rodape):
    """Uma lista só (erros-novo.html, por módulo, com tabela) e uma página por erro (erros-novo/<id>.html) com a ficha e o botão das evidências."""
    dados = carregar(hom)
    lig = links(erros, novo)
    total = sum(len(i) for _, _, i in dados)
    tg = {k: sum(1 for _, _, i in dados for x in i if x["grav"] == k) for k in ORDEM}
    word_src = Path(hom) / "versao-nova/defeitos-encontrados" / WORD
    word = ""
    if word_src.exists():
        d = Path(destino) / "documentacao/arquivos/erros-novo"
        d.mkdir(parents=True, exist_ok=True)
        shutil.copy2(word_src, d / WORD)
        word = f'<a class="botao" href="documentacao/arquivos/erros-novo/{WORD.replace(" ", "%20")}" download>⤓ Baixar em Word</a>'
    pasta = Path(destino) / "erros-novo"
    pasta.mkdir(exist_ok=True)
    secs = []
    for mid, nome, itens in dados:
        c = {k: sum(1 for x in itens if x["grav"] == k) for k in ORDEM}
        resumo = ", ".join(f"{n} {k}" for k, n in c.items() if n)
        tab = ('<table class="en-tab"><thead><tr><th>Defeito</th><th>Gravidade</th><th>Tela</th><th>Título</th></tr></thead><tbody>'
               + "".join(f'<tr><td><a href="erros-novo/{x["id"].lower()}.html">{E(x["id"])}</a></td><td>{E(x["grav"])}</td><td>{E(x["cab"].get("Tela") or "—")}</td><td>{E(x["titulo"])}</td></tr>' for x in itens) + "</tbody></table>")
        secs.append(f'<details class="en-mod" id="{mid}" open><summary>{E(nome)}<small>{len(itens)} erros · {E(resumo)}</small></summary><div class="en-corpo">{tab}</div></details>')
        for x in itens:
            c2 = (f'<main class="conteudo" id="conteudo"><p><a href="../erros-novo.html#{mid}">← Erros: {E(nome)}</a></p><h1>{E(x["id"])}: {E(x["titulo"])}</h1>'
                  f'<p class="en-meta">Versão nova · {E(nome)}</p>{corpo_ficha(x, lig)}</main>')
            (pasta / f'{x["id"].lower()}.html').write_text(
                cabecalho(f'{x["id"]}: {x["titulo"]}', "../").replace("</head>", f"<style>{CSS}</style></head>") + c2 + rodape("../"), encoding="utf-8")
    corpo = (f'<main class="conteudo" id="conteudo"><h1>Erros encontrados na versão nova</h1>'
             f'<p>Todos os erros encontrados nos testes de tela da versão nova (de 17/10 a 11/11/2026), módulo a módulo. O ambiente de teste só tem informação fictícia. Clique no defeito para ver o que fazer para reproduzir, o que era esperado, o que aconteceu e o impacto, e o botão para a tela do erro, com as evidências. Tela provisória (ainda por construir) não é erro.</p>'
             f'<p><b>{total} erros:</b> ' + ", ".join(f"{n} {k}" for k, n in tg.items() if n) + '.</p>'
             f'<div class="en-topo"><button class="botao" type="button" data-abrir="1">Abrir tudo</button><button class="botao" type="button" data-abrir="0">Fechar tudo</button>{word}</div>{"".join(secs)}</main>')
    (Path(destino) / "erros-novo.html").write_text(
        cabecalho("Erros encontrados na versão nova", "").replace("</head>", f"<style>{CSS}</style></head>") + corpo + rodape("").replace("</body>", f"<script>{JS}</script></body>"), encoding="utf-8")
    # a página de entrada antiga (com cartões) só leva à lista, para o endereço publicado continuar funcionando
    (Path(destino) / "erros.html").write_text(
        '<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><meta http-equiv="refresh" content="0; url=erros-novo.html"><title>Erros</title>'
        '<link rel="canonical" href="erros-novo.html"></head><body><p><a href="erros-novo.html">Erros encontrados na versão nova</a></p></body></html>', encoding="utf-8")
    return total
