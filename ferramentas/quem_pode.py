"""Quadro "Quem pode fazer o quê" por tela (critério L4 do fechamento do legado, 07/11/2026).

Fonte única: homologacao/portal-quem-pode-por-tela.csv (repositório da homologação). O portal só LÊ o arquivo; correções feitas lá persistem.
Colunas: modulo, slug_da_tela, tela, situacao_do_registro, acao, perfil, resultado, origem, revisado.

O quadro nunca é preenchido por suposição: cada linha vem de um teste de tela por perfil (ou de uma regra lida do código, dita na coluna origem).
Toda página de Manual por tela dos módulos do escopo mostra o quadro, ou o aviso padrão quando a tela ainda não foi levantada.
"""
import csv
import html
from collections import OrderedDict, defaultdict
from pathlib import Path

E = html.escape
ARQUIVO = "portal-quem-pode-por-tela.csv"
MODULOS = {"principal", "estoque", "garantia-qualidade", "controle-qualidade", "controle-documentos"}  # escopo do fechamento do legado
DADOS = defaultdict(list)  # (módulo, slug da tela) -> linhas
ACOES = ["Visualizar", "Editar", "Cancelar", "Imprimir", "Ver histórico"]


def carregar(hom):
    DADOS.clear()
    arq = Path(hom) / ARQUIVO
    if arq.exists():
        with arq.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                DADOS[(r["modulo"].strip(), r["slug_da_tela"].strip())].append(r)
    return sum(len(v) for v in DADOS.values())


def _celula(res):
    classe = "qp-alerta" if res in ("erro de servidor", "volta para a lista") else ("qp-edita" if res == "abre a edição" else "")
    return f'<td class="{classe}">{E(res)}</td>' if classe else f"<td>{E(res)}</td>"


def bloco(mid, slug, nome_tela):
    """HTML do quadro da tela. Devolve "" fora do escopo; o aviso padrão quando a tela ainda não foi levantada."""
    if mid not in MODULOS:
        return ""
    linhas = DADOS.get((mid, slug or ""))
    cab = '<section class="quem-pode" id="quem-pode-fazer-o-que"><h2>Quem pode fazer o quê</h2>'
    if not linhas:
        return (cab + '<div class="callout nv-aviso"><p class="callout-titulo">Ainda não levantado para esta tela</p>'
                '<p>O quadro "Quem pode fazer o quê" é preenchido a partir de testes de tela por perfil (nível, área e etapa do registro), '
                'nunca por suposição. Esta tela ainda não passou por esse levantamento.</p></div></section>')
    por_sit = OrderedDict()
    for r in linhas:
        por_sit.setdefault(r["situacao_do_registro"], []).append(r)
    partes = [cab, '<p class="qp-intro">Mostra, para cada perfil de teste, o que a lista da tela oferece e o que acontece ao clicar. '
                   '<strong>Lido no ambiente de teste, sem salvar:</strong> não prova o que acontece ao gravar nem a separação de funções.</p>']
    for sit, rs in por_sit.items():
        perfis = list(OrderedDict.fromkeys(r["perfil"] for r in rs))
        res = {(r["acao"], r["perfil"]): r["resultado"] for r in rs}
        acoes = [a for a in ACOES if any(a == r["acao"] for r in rs)]
        partes.append(f'<h3>Desvio na situação "{E(sit)}"</h3><div class="tabela"><table class="qp-tabela"><thead><tr><th>Ação</th>'
                      + "".join(f"<th>{E(p)}</th>" for p in perfis) + "</tr></thead><tbody>")
        for a in acoes:
            partes.append(f"<tr><th scope='row'>{E(a)}</th>" + "".join(_celula(res.get((a, p), "não lido")) for p in perfis) + "</tr>")
        partes.append("</tbody></table></div>")
    origens = "; ".join(OrderedDict.fromkeys(r["origem"] for r in linhas))
    nao_rev = any((r.get("revisado") or "").strip().lower() != "sim" for r in linhas)
    partes.append(f'<p class="qp-fonte">Fonte: {E(origens)}.' + (" Ainda <strong>não revisado</strong> pela Qualidade." if nao_rev else "") + "</p></section>")
    return "".join(partes)


CSS = """
.quem-pode{margin:28px 0 8px;padding-top:6px;border-top:1px solid var(--linha,#d9dde3)}
.quem-pode h3{font-size:1rem;margin:16px 0 6px}
.qp-intro,.qp-fonte{font-size:.9rem;opacity:.85}
.qp-tabela{border-collapse:collapse;width:100%;font-size:.88rem}
.qp-tabela th,.qp-tabela td{border:1px solid var(--linha,#d9dde3);padding:6px 8px;text-align:left;vertical-align:top}
.qp-tabela thead th{background:var(--painel,#f4f5f7)}
.qp-edita{font-weight:700}
.qp-alerta{color:#b3261e;font-weight:600}
"""
