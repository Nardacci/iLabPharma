#!/usr/bin/env python3
"""Cruza as telas do inventário do legado que ainda não têm manual na versão nova com as rotas do código novo
(`homologacao/versao-nova/codigo-front/INVENTARIO.md`) e grava `homologacao/versao-nova/mapa-telas-inventario.csv`.

Regras (decisão do responsável: nunca palpite): só ACRESCENTA linhas que faltam; linha existente nunca é alterada
(as correções de quem revisa persistem). `decisao`: confirmado (nome igual ou equivalência clara), provável (a conferir),
sem rota (nenhuma rota parecida no código; não prova que não vai existir) e a classificar. O portal só usa 'confirmado' e 'sem rota'.
Uso: python3 ferramentas/gerar_mapa_rotas.py <pasta do LabMedsys_homol>
"""
import csv, difflib, re, sys, unicodedata
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import versao_nova as vn

SEC = {"principal": "Principal", "estoque": "Estoque", "controle-qualidade": "Controle da Qualidade",
       "garantia-qualidade": "Garantia da Qualidade", "controle-documentos": "Controle de Documento"}
# Revisão manual (módulo, início do nome da tela do legado) -> decisão
CONFIRMA = [("estoque", "Inventário - Auditoria/justificativa"), ("estoque", "Insumos Reprovados (RM36)"), ("estoque", "Material Reservado (RM10)"),
            ("garantia-qualidade", "Registro Ação Corretiva Imediata"), ("garantia-qualidade", "Avaliação Área"), ("garantia-qualidade", "Relatório de CAPA"),
            ("garantia-qualidade", "Plano de Ação Preventiva"), ("garantia-qualidade", "Controle de Emissão de RNC"), ("garantia-qualidade", "Pré-Avaliação de Mudanças"),
            ("garantia-qualidade", "Avaliação de Mudanças"), ("garantia-qualidade", "Liberação Avaliação de Mudanças"),
            ("controle-qualidade", "Amostragens Pendentes Visão Administrador")]
PROVAVEL = [("garantia-qualidade", "Plano de Ação"), ("garantia-qualidade", "Execução Plano de Ação"), ("garantia-qualidade", "Liberação Plano de Ação"),
            ("garantia-qualidade", "Controle Mudança Produto"), ("garantia-qualidade", "Programação"), ("garantia-qualidade", "Monitoramento"),
            ("garantia-qualidade", "Solicitação de Registro (antiga)"), ("garantia-qualidade", "Check-List (antigo)"),
            ("controle-qualidade", "Programação de Solicitação de Análise (água"), ("controle-documentos", "Aprovação de Documentos"),
            ("controle-documentos", "Vigência de Documentos"), ("estoque", "Saída de Material (Remessa)")]
NAO_AUTO = [("estoque", "Demonstrativo Financeiro de Movimentação"), ("principal", "Início e menu"), ("principal", "Sair"),
            ("principal", "Sessão expirada"), ("principal", "Notificações do usuário")]
CAMPOS = ["modulo", "menu", "tela_legado", "rota", "nome_na_rota", "situacao_rota", "escore", "decisao", "revisado", "observacao"]


def nk(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s).split())


def casa(lista, mid, nome):
    return any(mid == m and nome.startswith(p) for m, p in lista)


def main(hom_raiz):
    hom = Path(hom_raiz) / "homologacao"
    reg = vn.registro(hom)
    for mid in vn.PASTAS_NOVO:
        vn.preencher_por_paginas(reg, hom, mid, lambda s: s, lambda md: md)
    inv, sec = {}, None
    for l in (hom / "versao-nova/codigo-front/INVENTARIO.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^#### (.+)", l)
        if m:
            sec = m.group(1).strip().split(" (")[0]
            continue
        m = re.match(r"^\| `([^`]+)` \| ([^|]+) \| (pronta|provisória) \|", l)
        if m and sec:
            inv.setdefault(sec, []).append((m.group(1), m.group(2).strip(), m.group(3)))
    saida = hom / "versao-nova/mapa-telas-inventario.csv"
    ja = set()
    linhas = []
    if saida.exists():
        with open(saida, encoding="utf-8", newline="") as f:
            linhas = list(csv.DictReader(f, delimiter=";"))
        ja = {(r["modulo"], r["menu"], r["tela_legado"]) for r in linhas}
    novas = 0
    for mid, s in SEC.items():
        pool = inv.get(s, [])
        for t in reg[mid]["telas"]:
            if t["situacao"].startswith(("Conferida", "Manual escrito")) or (mid, t["menu"], t["nome"]) in ja:
                continue
            cand = []
            for rota, nome, sit in pool:
                seg = rota.split("/")
                ult = seg[-1] if seg[-1] not in ("editar", "edicao", "novo", "edit") else seg[-2]
                sc = max(difflib.SequenceMatcher(None, nk(t["nome"]), nk(nome)).ratio(), difflib.SequenceMatcher(None, nk(t["nome"]), nk(ult)).ratio())
                cand.append((round(sc, 2), -len(rota), rota, nome, sit))
            cand.sort(reverse=True)
            sc, _, rota, nome, sit = cand[0] if cand else (0, 0, "", "", "")
            if casa(NAO_AUTO, mid, t["nome"]):
                dec, obs = "a classificar", "nome parecido com outra tela; conferir"
            elif casa(CONFIRMA, mid, t["nome"]):
                dec, obs = "confirmado", "equivalência conferida pela nuvem (nome e função)"
            elif casa(PROVAVEL, mid, t["nome"]):
                dec, obs = "provável", "equivalência possível; conferir com a área"
            elif sc >= 0.9:
                dec, obs = "confirmado", "nome igual ou quase igual"
            elif sc < 0.6:
                dec, rota, nome, sit, obs = "sem rota", "", "", "", "nenhuma rota parecida no código de 17/11 (não prova que não será criada)"
            else:
                dec, obs = "a classificar", "candidata fraca; conferir"
            linhas.append(dict(modulo=mid, menu=t["menu"], tela_legado=t["nome"], rota=rota if dec != "a classificar" or sc >= 0.6 else "",
                               nome_na_rota=nome, situacao_rota=sit, escore=f"{sc:.2f}" if cand else "", decisao=dec, revisado="não", observacao=obs))
            novas += 1
    with open(saida, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, delimiter=";")
        w.writeheader()
        w.writerows(linhas)
    from collections import Counter
    print(novas, "linhas novas;", Counter((r["decisao"], r["situacao_rota"]) for r in linhas))


if __name__ == "__main__":
    main(sys.argv[1])
