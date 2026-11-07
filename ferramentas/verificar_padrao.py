#!/usr/bin/env python3
"""Verificador do padrão do portal (etapa 1 do plano de padronização, 07/11/2026).

Lê as páginas HTML já geradas e confere, para cada tipo de página, a estrutura e os comportamentos que o padrão exige
(documento "Padrão do portal", homologacao/transversal/10-padrao-do-portal.md no repositório da homologação).
Só LÊ: não altera nenhuma página. Mostra, por regra, quantas páginas cumprem e quantas não, com exemplos.

Uso:
    python3 ferramentas/verificar_padrao.py [pasta do portal]            # relatório na tela
    python3 ferramentas/verificar_padrao.py . --saida relatorio.md       # grava o relatório (fora do site)
    python3 ferramentas/verificar_padrao.py . --estrito                  # sai com código 1 se houver divergência

Tipos de página (pelo caminho e pelo conteúdo):
    tela-legado    documentacao/<módulo>/*.html com a faixa de abas da tela (inclui as páginas de Erros do legado)
    doc-legado     documentacao/<módulo>/*.html sem abas (documento de módulo)
    modulo         documentacao/<módulo>/(index|legado|novo|ideal).html
    tela-novo      documentacao/novo/<módulo>/*.html (todas as abas, inclusive Erros)
    sem-tela       página "Sem tela associada" de cada módulo e versão
    raiz           *.html na raiz do portal
    (páginas de redirecionamento de endereço antigo são contadas à parte e não entram nas regras)
"""
import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

ABAS_PADRAO = ["Análise", "Manual do usuário", "Fluxos", "Regras de negócio", "Anvisa", "Erros", "Passo a passo", "Ideal"]


def tipo_da_pagina(rel, html):
    p = rel.as_posix()
    if p.startswith("documentacao/arquivos/") or p.startswith("documentacao/img/") or not p.endswith(".html"):
        return None
    if 'http-equiv="refresh"' in html[:1500]:
        return "redirecionamento"  # endereço antigo que leva à página nova; não é página de conteúdo
    if p.endswith("sem-tela-erros.html") or p.endswith("erros-sem-tela.html"):
        return "sem-tela"
    if p.startswith("documentacao/novo/"):
        return "tela-novo"
    partes = p.split("/")
    if p.startswith("documentacao/") and len(partes) == 3:
        if re.fullmatch(r"(index|legado|novo|ideal)\.html", partes[2]):
            return "modulo"
        if partes[1] == "visao-geral":
            return "doc-legado"
        return "tela-legado" if 'class="abas-tela"' in html else "doc-legado"
    if "/" not in p:
        return "raiz"
    return None


def abas_da_pagina(html):
    m = re.search(r'<nav class="abas-tela".*?</nav>', html, re.S)
    if not m:
        return []
    rot = []
    for x in re.findall(r"<(?:a|span)\b[^>]*>.*?</(?:a|span)>", m.group(0), re.S):
        txt = re.sub(r"\s*\(\d+\)\s*$", "", re.sub(r"<[^>]+>", "", x).strip())
        if txt:
            rot.append(txt)
    return rot


def link_da_outra_versao(html, tela_nova):
    """Destino do botão da outra versão na faixa "Versão: Legado | Novo" (Legado se a página é da versão nova, e o inverso)."""
    i = html.find('class="versao-seletor"')
    if i < 0:
        return None
    trecho = html[i:i + 1200]
    alvo = "Legado" if tela_nova else "Novo"
    for href, txt in re.findall(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', trecho, re.S):
        if re.sub(r"<[^>]+>", "", txt).strip() == alvo:
            return href
    return ""


# cada regra: (código, descrição, tipos a que se aplica, função(html, rel) -> True se cumpre)
def _tem(padrao):
    return lambda h, r: re.search(padrao, h) is not None


REGRAS = [
    ("E1", "Barra lateral do módulo", ("tela-legado", "tela-novo", "modulo", "doc-legado", "sem-tela"), _tem(r'<aside class="lateral"')),
    ("E2", "Trilha (onde estou)", ("tela-legado", "tela-novo", "modulo", "doc-legado", "sem-tela", "raiz"), _tem(r'class="trilha"')),
    ("E3", "Faixa de versão (Legado | Novo)", ("tela-legado", "tela-novo"), _tem(r'class="versao-seletor"')),
    ("E4", "Abas da tela", ("tela-legado", "tela-novo"), _tem(r'class="abas-tela"')),
    ("C2", "As 8 abas padrão, na mesma ordem", ("tela-legado", "tela-novo"), lambda h, r: abas_da_pagina(h) == ABAS_PADRAO),
    ("C3b", "Botão Imprimir", ("tela-legado", "tela-novo", "doc-legado"), _tem(r"window\.print")),
    ("C3c", "Anterior/Próximo", ("tela-legado", "tela-novo", "doc-legado"), _tem(r'class="anterior-proximo"')),
    # índice lateral: exigido quando a página tem pelo menos dois títulos (h2 ou h3) no conteúdo
    ("C3d", "Índice lateral (Nesta página), quando há 2 ou mais títulos", ("tela-legado", "tela-novo", "doc-legado"),
     lambda h, r: re.search(r'class="toc"', h) is not None or len(re.findall(r"<h[23][\s>]", h.split("</header>", 1)[-1])) < 2),
    ("C6", "A barra lateral destaca o item atual", ("tela-legado", "tela-novo", "doc-legado"),
     lambda h, r: re.search(r'<aside class="lateral".*?aria-current', h, re.S) is not None),
]


def regra_c1(html, rel, tipo):
    """C1: o botão da outra versão leva a uma tela (arquivo .html de tela), nunca à lista de telas, a '#' ou a lugar nenhum.
    Na página da própria versão o botão atual tem '#'; só se confere o destino da OUTRA versão."""
    alvo = link_da_outra_versao(html, tipo == "tela-novo")
    if alvo is None:
        return None
    return bool(alvo) and alvo != "#" and "telas.html" not in alvo


def verificar(raiz):
    raiz = Path(raiz)
    por_regra = defaultdict(lambda: {"ok": 0, "falha": [], "n": 0, "desc": ""})
    por_tipo = defaultdict(int)
    for f in sorted(list(raiz.glob("*.html")) + list((raiz / "documentacao").rglob("*.html"))):
        rel = f.relative_to(raiz)
        html = f.read_text(encoding="utf-8", errors="ignore")
        tipo = tipo_da_pagina(rel, html)
        if not tipo:
            continue
        por_tipo[tipo] += 1
        if tipo == "redirecionamento":
            continue
        for cod, desc, tipos, fn in REGRAS:
            if tipo not in tipos:
                continue
            r = por_regra[(cod, tipo)]
            r["desc"] = desc
            r["n"] += 1
            if fn(html, rel):
                r["ok"] += 1
            else:
                r["falha"].append(rel.as_posix())
        if tipo in ("tela-legado", "tela-novo"):
            ok = regra_c1(html, rel, tipo)
            if ok is not None:
                r = por_regra[("C1", tipo)]
                r["desc"] = "Trocar de versão leva à mesma tela (não à lista)"
                r["n"] += 1
                if ok:
                    r["ok"] += 1
                else:
                    r["falha"].append(rel.as_posix())
    return por_tipo, por_regra


def relatorio(por_tipo, por_regra, exemplos=3):
    linhas = ["# Padrão do portal: divergências encontradas", "",
              "Páginas por tipo: " + ", ".join(f"{t} {n}" for t, n in sorted(por_tipo.items())), "",
              "| Regra | Tipo de página | O que confere | Cumprem | Divergem | Exemplos de divergência |", "|---|---|---|---|---|---|"]
    total_div = 0
    for (cod, tipo), r in sorted(por_regra.items()):
        div = len(r["falha"])
        total_div += div
        ex = "; ".join(r["falha"][:exemplos]) if div else ""
        linhas.append(f"| {cod} | {tipo} | {r['desc']} | {r['ok']} de {r['n']} | {div} | {ex} |")
    linhas += ["", f"Total de divergências (soma por regra): {total_div}."]
    return "\n".join(linhas), total_div


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pasta", nargs="?", default=".", help="Pasta do portal gerado")
    ap.add_argument("--saida", help="Arquivo (fora do site) para gravar o relatório")
    ap.add_argument("--estrito", action="store_true", help="Sai com código 1 se houver divergência")
    a = ap.parse_args()
    por_tipo, por_regra = verificar(a.pasta)
    texto, total = relatorio(por_tipo, por_regra)
    print(texto)
    if a.saida:
        Path(a.saida).write_text(texto + "\n", encoding="utf-8")
    if a.estrito and total:
        sys.exit(1)


if __name__ == "__main__":
    main()
