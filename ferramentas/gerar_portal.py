#!/usr/bin/env python3
"""Gera o portal iLabMedSys (documentação da homologação do LabMedSys) a partir do repositório LabMedsys_homol.

O que faz:
  1. Lê os documentos em Markdown de <origem>/homologacao, conforme o CATÁLOGO abaixo.
  2. Segurança: por decisão do responsável (23/10/2026) o portal publica TODOS os defeitos, inclusive os de acesso e
     segurança (documentos 03-achados-de-seguranca, seções de segurança e os registros completos de defeitos).
     Continuam fora senhas, logins, endereços e IPs de servidor e strings de conexão (a higiene redige e o verificador
     bloqueia). Com --sem-seguranca volta o comportamento antigo: retira arquivos 03-achados-de-seguranca, seções com
     "segurança" no título, blocos confidenciais e linhas com achados SEG-XXX-nn; o que sai vai para um relatório local.
  3. Converte para HTML no visual do portal, copia fluxogramas e capturas usadas, e publica os Word.
     Quando um documento foi limpo, o Word é gerado de novo a partir do texto limpo.
  4. Monta a página inicial, as páginas de módulo e o índice de busca.

Uso:
  python3 ferramentas/gerar_portal.py --origem ../labmedsys_homol --destino . [--relatorio /tmp/retirado.md]

Requer: pip install markdown
"""
import argparse
import datetime
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
import unicodedata
import zipfile
from pathlib import Path

import markdown

sys.path.insert(0, str(Path(__file__).resolve().parent))
import biblioteca  # noqa: E402
import higiene  # noqa: E402
import menus_gq  # noqa: E402
import telas_devs  # noqa: E402

HOJE = datetime.date.today().strftime("%d/%m/%Y")

# ---------------------------------------------------------------------------------------------
# Catálogo: o que entra no portal. "arq" é relativo a homologacao/. "word" é o .docx original.
# Categorias: inicio (comece por aqui), ideal (como deve ser), defeitos (para os devs), fluxos, negocio, qualidade, tecnico, testes.
# ---------------------------------------------------------------------------------------------
CATEGORIAS = {
    "inicio": ("Comece por aqui", "Visão geral e resumos para quem quer entender rápido."),
    "ideal": ("O ideal", "Como o módulo deve trabalhar para atender à ANVISA: funções, comportamento, integrações com os outros módulos e papéis. Não descreve o legado; mostra o que manter, corrigir e construir."),
    "fluxos": ("Fluxos do processo", "Como o trabalho anda no sistema, etapa por etapa, com fluxograma. Onde há roteiro, cada tela leva ao passo a passo para quem vai testar."),
    "negocio": ("Regras e uso", "Regras de negócio, telas e manual para quem usa o sistema."),
    "qualidade": ("Qualidade e ANVISA", "Conformidade com a RDC 658/2022, riscos e rastreabilidade."),
    "tecnico": ("Requisitos e dados", "Para a equipe de desenvolvimento da nova versão."),
    "defeitos": ("Defeitos para correção", "Para a equipe de desenvolvimento: cada defeito encontrado nos testes, com o passo a passo para reproduzir, as capturas, o trecho do código e uma sugestão de correção."),
    "testes": ("Testes", "Plano de testes, resultados e evidências."),
    "novo": ("iLabPharma Novo", "Testes da versão nova."),
}

# Roteiro de execução (passo a passo para quem testa) -> fluxo a que pertence. Na página do módulo, cada
# fluxo lista as telas do seu roteiro; o roteiro em si fica na categoria "fluxos", abaixo do fluxo.
ROTEIROS = {
    "5.garantia_qualidade/roteiros/desvios-capa.md": "5.garantia_qualidade/fluxos/desvios-capa.md",
    "5.garantia_qualidade/roteiros/autoinspecao-auditoria.md": "5.garantia_qualidade/fluxos/autoinspecao-auditoria.md",
    "5.garantia_qualidade/roteiros/controle-mudancas.md": "5.garantia_qualidade/fluxos/controle-mudancas.md",
    "5.garantia_qualidade/roteiros/treinamento.md": "5.garantia_qualidade/fluxos/treinamento.md",
    "5.garantia_qualidade/roteiros/assuntos-regulatorios.md": "5.garantia_qualidade/fluxos/assuntos-regulatorios.md",
}
RE_TELA = re.compile(r"^(?:Telas?\s+[\d, e]+|Fora da \w+|Fechamento)\s*·\s*(.+)$")


def telas_do_roteiro(pagina):
    """Lista (nome da tela, âncora) a partir dos títulos 'Tela N · Nome' do roteiro, em qualquer nível."""
    itens = []
    for t in pagina["toc"]:
        for x in [t] + t["children"]:
            nome = html.unescape(x["name"])
            m = RE_TELA.match(nome)
            if m:
                itens.append((re.sub(r"\s*\(.*?\)\s*$", "", m.group(1)).strip(), x["id"]))
    return itens


# Áreas que não são módulos do sistema: ficam fora dos cartões e das contagens de módulos.
ESPECIAIS = {"visao-geral"}

# ---------------------------------------------------------------------------------------------
# Roteiro de leitura: cada módulo vira um caminho com começo, passos numerados e fim. Nenhum
# documento sai do portal; só ganha ordem. O caminho entre os módulos segue o processo do lote.
# ---------------------------------------------------------------------------------------------
CAMINHO = ["visao-geral", "principal", "estoque", "producao", "ope", "controle-qualidade",
           "garantia-qualidade", "controle-documentos", "comercial", "rastreabilidade"]
PASSOS = [
    ("resumo", "Resumo do módulo", "O que é o módulo, em que situação está e o que decidir. Vale para o sistema entregue e para a versão nova."),
    ("fluxos", "Siga o processo", "Como o trabalho anda, etapa por etapa, na ordem em que acontece. Onde há roteiro, ele vem logo depois do fluxo."),
    ("desvios", "Menus do sistema, tela a tela", "Uma página por tela dos menus Controle de Desvios e Controle de Mudanças: manual do usuário, campos, botões, mensagens, regras de negócio, fluxo, falhas e casos de teste, cada uma com o Word para baixar."),
    ("ideal", "O ideal: como deve funcionar", "Como o módulo deve trabalhar para atender à ANVISA: funções, comportamento, integrações com os outros módulos e papéis. Mostra o que manter, corrigir e acrescentar."),
    ("norma", "ANVISA: norma e risco", "O que a ANVISA exige e onde está o risco."),
    ("dados", "Dados e integrações", "Para a equipe de desenvolvimento: modelo de dados e integrações do sistema entregue."),
    ("fecho", "Fechamento", "O parecer do módulo, por que ele está (ou não) apto, e o dossiê que reúne tudo."),
    ("conhecer", "Telas e situação", "O que existe no sistema entregue, como as telas se organizam nos menus e o que funciona."),
    ("regras", "Regras e uso", "O que o sistema entregue faz com cada dado, quem pode fazer o quê e como usar."),
    ("testes", "Testes e defeitos", "O que foi testado nas telas do sistema entregue, o que falhou e como corrigir."),
    ("novo", "iLabPharma Novo", "A versão nova do sistema (as mesmas regras com ferramentas atualizadas): o que foi testado, o que ficou igual, melhorou ou piorou em relação ao sistema entregue."),
    ("novo_parecer", "Parecer e comparação com o legado", "O veredito sobre a versão nova e o que mudou em relação ao sistema entregue."),
    ("requisitos", "Requisitos da versão corrigida", "O que a versão corrigida precisa fazer: requisitos com origem nos achados, para quem desenvolve."),
]
# Seções do roteiro do módulo: cada passo pertence a uma.
SECOES = [
    ("modulo", "Sobre o módulo", "Um resumo só, que situa o módulo nas três situações.", ["resumo"]),
    ("legado", "Legado", "O sistema entregue pelo fornecedor: como é hoje, o que foi testado e o veredito.", ["conhecer", "fluxos", "desvios", "regras", "norma", "dados", "testes", "fecho"]),
    ("novo", "iLabPharma Novo", "A versão nova: testes por menu do sistema, parecer e comparação com o legado.", ["novo", "novo_parecer"]),
    ("ideal", "Ideal", "Como o módulo deve funcionar para atender à ANVISA, e os requisitos da versão corrigida. Vale como definição nos módulos com testes concluídos (Principal e Estoque); nos demais é rascunho até o fim dos testes.", ["ideal", "requisitos"]),
]
PRIORIDADE = {
    "conhecer": ["reconhecimento", "inventário"],
    "regras": ["regras de negócio", "matriz de permiss", "manual", "cadastros"],
    "norma": ["conformidade", "risco", "rastreabilidade"],
    "testes": ["versão nova: o que", "versão nova: situação", "plano", "relatório", "defeitos", "versão nova: resultado"],
    "ideal": ["ideal", "entre os módulos"],
    "dados": ["modelo de dados", "comparação"],
    "requisitos": ["análise de requisitos", "requisitos"],
    "novo_parecer": ["parecer", "comparação", "situação", "o que os testes"],
    "fecho": ["não está apto", "dossiê"],
    "novo": ["resumo dos testes", "situação", "plano", "usuários", "comparação", "rodada 1", "rodada 2", "rodada 4", "rodada 5"],
    "visao": ["processo fabril", "integrações", "diagnóstico", "repetidos", "qualidade entre"],
}
ORDEM_FLUXOS = {
    "estoque": ["compras", "recebimento", "reprovado", "movimenta", "almoxarifado", "inventário", "solicita", "devolu", "remessa", "kits"],
    "producao": ["produto", "prepara", "autoriza", "registro de lote", "terceiriza"],
    "controle-qualidade": ["regras", "solicita", "água", "estabilidade"],
    "garantia-qualidade": ["desvios", "mudan", "autoinspe", "treinamento", "assuntos"],
    "controle-documentos": ["tipo de documento", "ciclo", "cópias", "externo"],
    "comercial": ["cliente", "cotação", "fatura"],
    "rastreabilidade": ["geração", "eventos"],
}


def _pos(chaves, titulo):
    t = titulo.lower()
    for i, c in enumerate(chaves):
        if c in t:
            return i
    return 99


def passo_de(p):
    t, cat = p["titulo"].lower(), p["cat"]
    if p.get("desvios"):
        return "desvios"
    if cat == "novo":
        return "novo"
    if cat == "fluxos" or p.get("roteiro_de"):
        return "fluxos"
    if "requisitos" in t:
        return "requisitos"
    if "versão nova" in t or "nova versão" in t:
        return "novo_parecer"
    if "dossiê" in t or "não está apto" in t or "parecer" in t:
        return "fecho"
    if "regras de negócio" in t:
        return "regras"
    if cat == "inicio":
        if "resumo executivo" in t or "resumo do módulo" in t:
            return "resumo"
        return "testes" if "relatório de testes" in t else "conhecer"
    if cat == "negocio":
        return "regras"
    if cat == "qualidade":
        return "norma"
    if cat in ("testes", "defeitos"):
        return "testes"
    if cat == "ideal":
        return "ideal"
    return "dados"


def _com_seguranca(mod, docs, hom):
    """Com a segurança pública: troca a lista de defeitos pelo registro completo (se existir) e acrescenta os achados de segurança."""
    saida = []
    pasta = None
    for d in docs:
        arq = d[0]
        if arq.endswith("/defeitos/defeitos.md"):
            pasta = arq.rsplit("/defeitos/", 1)[0]
            if (hom / pasta / "defeitos" / "defeitos-completo.md").exists():
                d = (f"{pasta}/defeitos/defeitos-completo.md",) + tuple(d[1:])
        saida.append(d)
    if pasta is None:
        for sub in sorted(p.name for p in hom.iterdir() if p.is_dir()):
            if mod["id"] == "garantia-qualidade" and sub == "5.garantia_qualidade":
                pasta = sub
        if pasta and (hom / pasta / "defeitos" / "defeitos-completo.md").exists():
            saida.append((f"{pasta}/defeitos/defeitos-completo.md", "Defeitos para correção", "defeitos",
                          f"{pasta}/defeitos/LabMedSys - Modulo Garantia da Qualidade - Defeitos para Correcao.docx"))
    base = next((d[0].split("/")[0] for d in saida if "/" in d[0] and d[0][0].isdigit()), None)
    if base and (hom / base / "03-achados-de-seguranca.md").exists() and not any(d[0].endswith("03-achados-de-seguranca.md") for d in saida):
        saida.append((f"{base}/03-achados-de-seguranca.md", "Achados de segurança", "defeitos", None))
    return saida


def docs_com_telas(mod, hom):
    """As telas da versão nova (por menu) vêm de manifestos gerados em homologacao/: no Principal, as telas testadas;
    na Garantia da Qualidade, as telas a criar (Controle de Desvios e de Mudanças)."""
    docs = list(mod["docs"])
    if SEGURANCA_PUBLICA:
        docs = _com_seguranca(mod, docs, hom)
    if mod["id"] == "garantia-qualidade":
        docs += menus_gq.entradas(hom)
    fontes = {"principal": "versao-nova/1.principal/telas/manifest.json",
              "garantia-qualidade": "versao-nova/5.garantia_qualidade/telas-a-criar/manifest.json"}
    if mod["id"] not in fontes:
        return docs
    arq = hom / fontes[mod["id"]]
    if not arq.exists():
        return docs
    man = json.loads(arq.read_text(encoding="utf-8"))
    gerais = [(m["arq"], m["titulo"], "novo", None) for m in man if not m.get("grupo")]
    telas = [(m["arq"], m["titulo"], "novo", None, {k: m[k] for k in ("grupo", "tela", "rotulo", "roteiro_de", "situacao") if k in m}) for m in man if m.get("grupo")]
    velhos = [d for d in docs if d[2] == "novo"]
    resto = [d for d in docs if d[2] != "novo"]
    return resto + gerais + velhos + telas


def _secao_de(chave):
    for sk, sn, sd, chaves in SECOES:
        if chave in chaves:
            return sk, sn, sd
    return "visao", "Visão de ponta a ponta", ""


def organizar_roteiro(mod):
    """Ordena os documentos do módulo em passos e liga cada um ao anterior e ao próximo."""
    mod["roteiro"], mod["seq"] = [], []
    if not mod["paginas"]:
        return
    if mod["id"] in ESPECIAIS:
        pags = sorted(mod["paginas"], key=lambda p: _pos(PRIORIDADE["visao"], p["titulo"]))
        grupos = [("visao", "Visão de ponta a ponta", "Como o processo se encadeia entre os módulos, onde a corrente quebra e o que repete.", pags)]
    else:
        grupos = []
        ordem_passos = [x for sk, sn, sd, chaves in SECOES for c in chaves for x in PASSOS if x[0] == c]
        for chave, nome, desc in ordem_passos:
            pags = [p for p in mod["paginas"] if passo_de(p) == chave]
            if chave == "fluxos":
                fl = sorted([p for p in pags if not p.get("roteiro_de")], key=lambda p: _pos(ORDEM_FLUXOS.get(mod["id"], []), p["titulo"]))
                ro = {p["roteiro_de"]: p for p in pags if p.get("roteiro_de")}
                pags = []
                for p in fl:
                    pags.append(p)
                    if p["arq"] in ro:
                        pags.append(ro[p["arq"]])
            elif chave in ("novo", "resumo"):
                pags = sorted(pags, key=lambda p: p["ordem"])
            else:
                pags = sorted(pags, key=lambda p: _pos(PRIORIDADE.get(chave, []), p["titulo"]))
            if pags:
                grupos.append((chave, nome, desc, pags))
    seq = [p for g in grupos for p in g[3]]
    for i, g in enumerate(grupos, 1):
        for p in g[3]:
            p["passo_n"], p["passo_nome"], p["passo_total"] = i, g[1], len(grupos)
            p["secao_nome"] = _secao_de(g[0])[1]
            p["sit"] = _secao_de(g[0])[0]
    for k, p in enumerate(seq):
        p["n"], p["total"] = k + 1, len(seq)
        p["ant"] = seq[k - 1] if k else None
        p["prox"] = seq[k + 1] if k + 1 < len(seq) else None
    mod["roteiro"], mod["seq"] = grupos, seq


def vizinhos(mod):
    """Módulo anterior e seguinte no caminho do processo (só os que têm documentos)."""
    ids = [m for m in CAMINHO if any(x["id"] == m and x["paginas"] for x in MODULOS)]
    if mod["id"] not in ids:
        return None, None
    i = ids.index(mod["id"])
    por_id = {x["id"]: x for x in MODULOS}
    return (por_id[ids[i - 1]] if i else None), (por_id[ids[i + 1]] if i + 1 < len(ids) else None)

MODULOS = [
    {
        "id": "visao-geral", "nome": "Visão entre módulos", "icone": "◎", "cor": "#2563eb",
        "situacao": "Em andamento", "nivel": 2,
        "resumo": "Como os módulos se encadeiam, do recebimento de material à liberação do lote, e onde a corrente está quebrada. Telas repetidas entre módulos.",
        "docs": [
            ("cliente-ivb/02-aderencia-ao-edital.md", "Aderência ao edital do IVB", "inicio", None),
            ("transversal/04-mapa-de-integracoes.md", "Mapa de integrações entre os módulos", "inicio", "transversal/LabMedSys - Mapa de Integracoes entre Modulos.docx"),
            ("transversal/03-diagnostico-conformidade.md", "Diagnóstico de conformidade com a ANVISA", "inicio", "transversal/LabMedSys - Diagnostico de Conformidade ANVISA.docx"),
            ("transversal/02-mapa-do-processo-fabril.md", "Mapa do processo fabril", "inicio", "transversal/LabMedSys - Mapa do Processo Fabril.docx"),
            ("transversal/01-telas-repetidas.md", "Telas, tabelas e código repetidos entre os módulos", "tecnico", "transversal/LabMedSys - Telas Tabelas e Codigo Repetidos.docx"),
            ("transversal/reunioes/2026-10-13-ata.md", "Ata da reunião de 13/10/2026: por que tantas telas e tabelas", "tecnico", None),
            ("modelo-ideal/01-qualidade-entre-modulos.md", "Qualidade entre os módulos: situação do lote e travas", "ideal", "modelo-ideal/entregaveis/LabMedSys - Modelo Ideal - Qualidade entre os Modulos.docx"),
        ],
    },
    {
        "id": "principal", "nome": "Principal", "icone": "⌂", "cor": "#f57c00",
        "situacao": "Homologado: não apto", "nivel": 4,
        "resumo": "Porta de entrada dos nove módulos: login, usuários, perfis, permissões, cadastros gerais e a base da trilha de auditoria. Analisado, testado em duas rodadas (78 casos) e com todos os entregáveis.",
        "docs": [
            ("1.principal/entregaveis/fonte/resumo-executivo.md", "Resumo do módulo", "inicio", "1.principal/entregaveis/LabMedSys - Modulo Principal - Resumo Executivo.docx"),
            ("1.principal/entregaveis/fonte/por-que-nao-apta.md", "Por que o Principal não está apto", "inicio", "1.principal/entregaveis/LabMedSys - Modulo Principal - Por que nao esta apto.docx"),
            ("1.principal/entregaveis/fonte/parecer-versao-nova.md", "Parecer da versão nova do Principal", "inicio", "1.principal/entregaveis/LabMedSys - Modulo Principal - Parecer da Versao Nova.docx"),
            ("1.principal/entregaveis/fonte/dossie-de-homologacao.md", "Dossiê de homologação", "inicio", "1.principal/entregaveis/LabMedSys - Modulo Principal - Dossie de Homologacao.docx"),
            ("1.principal/11-inventario-de-telas.md", "Inventário de telas e situação", "inicio", None),
            ("1.principal/entregaveis/fonte/regras-de-negocio.md", "Regras de negócio", "negocio", "1.principal/entregaveis/LabMedSys - Modulo Principal - Regras de Negocio.docx"),
            ("1.principal/entregaveis/fonte/manual-do-usuario.md", "Manual do usuário", "negocio", "1.principal/entregaveis/LabMedSys - Modulo Principal - Manual do Usuario.docx"),
            ("1.principal/ideal/pri-ideal.md", "O Principal ideal: o dono do que é global", "ideal", "1.principal/ideal/LabMedSys - Modulo Principal - O Ideal.docx"),
            ("1.principal/02-matriz-de-permissoes.md", "Matriz de permissões", "negocio", None),
            ("1.principal/04-conformidade-regulatoria.md", "Conformidade regulatória", "qualidade", None),
            ("1.principal/07-analise-de-risco.md", "Análise de risco", "qualidade", None),
            ("1.principal/09-matriz-de-rastreabilidade.md", "Matriz de rastreabilidade", "qualidade", None),
            ("1.principal/defeitos/defeitos.md", "Defeitos para correção", "defeitos", "1.principal/defeitos/LabMedSys - Modulo Principal - Defeitos para Correcao.docx"),
            ("1.principal/entregaveis/fonte/analise-de-requisitos.md", "Análise de requisitos", "tecnico", "1.principal/entregaveis/LabMedSys - Modulo Principal - Analise de Requisitos.docx"),
            ("1.principal/05-requisitos.md", "Requisitos da nova versão (rascunho)", "tecnico", None),
            ("1.principal/06-modelo-de-dados.md", "Modelo de dados e integrações", "tecnico", None),
            ("1.principal/10-comparacao-nova-versao.md", "Comparação com a nova versão", "tecnico", None),
            ("1.principal/01-regras-de-negocio.md", "Regras de negócio (rascunho com fontes)", "tecnico", None),
            ("1.principal/08-plano-de-testes.md", "Plano de testes", "testes", None),
            ("versao-nova/1.principal/manual/manual-principal-versao-nova.md", "Manual da versão nova, por tela", "novo", "versao-nova/1.principal/manual/LabMedSys - Modulo Principal - Manual da Versao Nova por Tela.docx"),
            ("versao-nova/1.principal/resumo-versao-nova.md", "Resumo dos testes", "novo", None),
            ("versao-nova/1.principal/plano-de-regressao.md", "Plano de regressão", "novo", None),
            ("versao-nova/COMPARACAO-CODIGO.md", "Comparação do código com o legado", "tecnico", None),
            ("versao-nova/1.principal/execucao/2026-10-17/resultado.md", "Resultado da rodada 1", "novo", None),
            ("versao-nova/1.principal/execucao/2026-10-17-rodada-2/resultado.md", "Resultado da rodada 2", "novo", None),
        ],
    },
    {
        "id": "estoque", "nome": "Estoque", "icone": "▦", "cor": "#2e9b4f",
        "situacao": "Homologado: não apto", "nivel": 4,
        "resumo": "Recebimento, quarentena, endereçamento, movimentação, atendimento à produção, devolução, remessa, inventário e kits. Dez fluxos documentados. Testes de tela por risco: 11 rodadas (07 a 22/10/2026), 149 dos 162 casos conclusivos, 44 dos 46 casos Alta; 76 defeitos para correção, inclusive os de acesso. Confirmado na tela: o Endereçamento mostra sucesso e não grava (causa no banco, aguarda o DBA); pelas entradas de material o lote entra em quarentena e abre a análise no CQ; o laudo reprovado bloqueia o lote, mas o Estoque só sabe quando alguém atualiza a análise; a avaliação do fornecedor não qualifica nem bloqueia ninguém; a entrada de produto acabado aceita lote inventado e vencido; o histórico do lote não mostra usuário, análise nem laudo. Fechado em 14/10/2026 e reencerrado em 23/10/2026, com os sete entregáveis em versão 1.5 (resumo executivo, dossiê, regras de negócio, análise de requisitos, manual do usuário, relatório de testes e \"por que não está apto\"). Reabre só se o DBA, a Produção ou o desenvolvimento resolverem as pendências (2 casos Alta bloqueados; ao banco falta responder duas perguntas, sobre o Endereçamento e a retenção de um lote, e ligar uma função profissional à configuração 19 para o Lote Padrão ser aprovado e a Produção destravar).",
        "docs": [
            ("3.estoque/entregaveis/fonte/por-que-nao-apta.md", "Por que o Estoque não está apto", "inicio", "3.estoque/entregaveis/LabMedSys - Modulo Estoque - Por que nao esta apto.docx"),
            ("3.estoque/entregaveis/fonte/resumo-executivo.md", "Resumo do módulo", "inicio", "3.estoque/entregaveis/LabMedSys - Modulo Estoque - Resumo Executivo.docx"),
            ("3.estoque/entregaveis/fonte/dossie-de-homologacao.md", "Dossiê de homologação", "inicio", "3.estoque/entregaveis/LabMedSys - Modulo Estoque - Dossie de Homologacao.docx"),
            ("3.estoque/00-reconhecimento.md", "Reconhecimento do módulo", "inicio", None),
            ("3.estoque/ideal/est-ideal.md", "O Estoque ideal", "ideal", "3.estoque/ideal/LabMedSys - Modulo Estoque - O Ideal.docx"),
            ("3.estoque/ideal/est-entre-modulos.md", "O Estoque entre os módulos: as travas", "ideal", "3.estoque/ideal/LabMedSys - Modulo Estoque - Entre os Modulos.docx"),
            ("3.estoque/11-inventario-de-telas.md", "Inventário de telas e situação", "inicio", None),
            ("3.estoque/04-conformidade-regulatoria.md", "Conformidade com a RDC 658/2022", "qualidade", None),
            ("3.estoque/07-analise-de-risco.md", "Análise de risco", "qualidade", None),
            ("3.estoque/entregaveis/fonte/analise-de-requisitos.md", "Análise de requisitos", "tecnico", "3.estoque/entregaveis/LabMedSys - Modulo Estoque - Analise de Requisitos.docx"),
            ("3.estoque/05-requisitos.md", "Requisitos da nova versão (rascunho)", "tecnico", None),
            ("3.estoque/06-modelo-de-dados.md", "Modelo de dados e integrações", "tecnico", None),
            ("3.estoque/02-matriz-de-permissoes.md", "Matriz de permissões", "negocio", None),
            ("3.estoque/08-plano-de-testes.md", "Plano de testes", "testes", None),
            ("versao-nova/3.estoque/resumo-versao-nova.md", "Situação na versão nova", "novo", None),
            ("3.estoque/entregaveis/fonte/relatorio-de-testes.md", "Relatório de testes", "inicio", "3.estoque/entregaveis/LabMedSys - Modulo Estoque - Relatorio de Testes.docx"),
            ("3.estoque/entregaveis/fonte/regras-de-negocio.md", "Regras de negócio", "negocio", "3.estoque/entregaveis/LabMedSys - Modulo Estoque - Regras de Negocio.docx"),
            ("3.estoque/entregaveis/fonte/manual-do-usuario.md", "Manual do usuário", "negocio", "3.estoque/entregaveis/LabMedSys - Modulo Estoque - Manual do Usuario.docx"),
            ("3.estoque/fluxos/recebimento-quarentena-conferencia.md", "Recebimento e quarentena (conferência)", "fluxos", "3.estoque/fluxos/LabMedSys - Modulo Estoque - Conferencia dos Fluxos de Recebimento e Quarentena.docx"),
            ("3.estoque/fluxos/movimentacao-interna.md", "Movimentação interna", "fluxos", "3.estoque/fluxos/LabMedSys - Modulo Estoque - Fluxo Movimentacao Interna.docx"),
            ("3.estoque/fluxos/reprovado-reanalise-revalidacao.md", "Reprovado, reanálise e revalidação", "fluxos", "3.estoque/fluxos/LabMedSys - Modulo Estoque - Fluxo Reprovado, Reanalise e Revalidacao.docx"),
            ("3.estoque/fluxos/solicitacao-atendimento-producao.md", "Solicitação e atendimento à produção", "fluxos", "3.estoque/fluxos/LabMedSys - Modulo Estoque - Fluxo Solicitacao, Separacao e Atendimento.docx"),
            ("3.estoque/fluxos/devolucao-entrada-producao.md", "Devolução e entradas da produção", "fluxos", "3.estoque/fluxos/LabMedSys - Modulo Estoque - Fluxo Devolucao e Entradas.docx"),
            ("3.estoque/fluxos/remessa-expedicao.md", "Remessa e expedição", "fluxos", "3.estoque/fluxos/LabMedSys - Modulo Estoque - Fluxo Remessa e Expedicao.docx"),
            ("3.estoque/fluxos/inventario.md", "Inventário", "fluxos", "3.estoque/fluxos/LabMedSys - Modulo Estoque - Fluxo Inventario.docx"),
            ("3.estoque/fluxos/kits.md", "Kits", "fluxos", "3.estoque/fluxos/LabMedSys - Modulo Estoque - Fluxo Kits.docx"),
            ("3.estoque/fluxos/compras-fornecedor.md", "Compras e avaliação do fornecedor", "fluxos", "3.estoque/fluxos/LabMedSys - Modulo Estoque - Fluxo Compras e Avaliacao do Fornecedor.docx"),
            ("3.estoque/fluxos/almoxarifado-cq.md", "Almoxarifado do Controle da Qualidade", "fluxos", "3.estoque/fluxos/LabMedSys - Modulo Estoque - Fluxo Almoxarifado do Controle da Qualidade.docx"),
            ("3.estoque/01-cadastros-de-apoio.md", "Cadastros de apoio", "negocio", None),
            ("3.estoque/defeitos/defeitos.md", "Defeitos para correção", "defeitos", "3.estoque/defeitos/LabMedSys - Modulo Estoque - Defeitos para Correcao.docx"),
        ],
    },
    {
        "id": "garantia-qualidade", "nome": "Garantia da Qualidade", "icone": "◇", "cor": "#8b1e3f",
        "situacao": "Homologado: não apto", "nivel": 4,
        "resumo": "Desvios e CAPA, controle de mudanças, autoinspeção e auditoria, treinamento e assuntos regulatórios. Reconhecimento, mapa de conformidade com a RDC 658/2022, os cinco fluxos (desvios e CAPA, controle de mudanças, autoinspeção, treinamento e assuntos regulatórios), as regras de negócio, o inventário das 67 telas, a matriz de permissões, o modelo de dados, a análise de risco e o plano de testes prontos. Fechado em 23/10/2026 como não apto, com limitações. Testes de tela por risco: 562 linhas nas listas dos menus (Controle de Desvios 14 telas, Controle de Mudanças 8, Assuntos Regulatórios 3 e Autoinspeção e Auditoria 7), 533 conclusivas; 187 defeitos registrados (1 Crítica, 60 Alta), inclusive os de acesso e segurança. Confirmado na tela: desvio finalizado sem verificação final, plano aprovado com ação pendente, cancelamento e avaliação fora do histórico, mudança liberada sem parecer das áreas e plano finalizado sem a ação executada, auditoria \"Não conforme\" que não abre desvio e relatório de planejamento que não lista as programações. Cinco entregáveis emitidos (relatório, resumo executivo, dossiê, regras de negócio, manual e análise de requisitos). Reabre com Treinamento Técnico e Configuração (ainda sem rodada em tela), as respostas da Qualidade e as correções do desenvolvimento.",
        "docs": [
            ("5.garantia_qualidade/00-reconhecimento.md", "Reconhecimento do módulo", "inicio", None),
            ("5.garantia_qualidade/ideal/gq-ideal.md", "A Garantia da Qualidade ideal", "ideal", "5.garantia_qualidade/ideal/LabMedSys - Modulo Garantia da Qualidade - O Ideal.docx"),
            ("5.garantia_qualidade/ideal/gq-entre-modulos.md", "A Garantia da Qualidade entre os módulos: as travas", "ideal", "5.garantia_qualidade/ideal/LabMedSys - Modulo Garantia da Qualidade - Entre os Modulos.docx"),
            ("5.garantia_qualidade/11-inventario-de-telas.md", "Inventário de telas e situação", "inicio", None),
            ("5.garantia_qualidade/01-regras-de-negocio.md", "Regras de negócio", "negocio", None),
            ("5.garantia_qualidade/02-matriz-de-permissoes.md", "Matriz de permissões", "negocio", None),
            ("5.garantia_qualidade/entregaveis/fonte/relatorio-de-testes.md", "Relatório de testes", "inicio", "5.garantia_qualidade/entregaveis/LabMedSys - Modulo Garantia da Qualidade - Relatorio de Testes.docx"),
            ("5.garantia_qualidade/entregaveis/fonte/por-que-nao-apta.md", "Por que a Garantia da Qualidade não está apta", "inicio", "5.garantia_qualidade/entregaveis/LabMedSys - Modulo Garantia da Qualidade - Por que nao esta apto.docx"),
            ("5.garantia_qualidade/entregaveis/fonte/resumo-executivo.md", "Resumo do módulo", "inicio", "5.garantia_qualidade/entregaveis/LabMedSys - Modulo Garantia da Qualidade - Resumo Executivo.docx"),
            ("5.garantia_qualidade/entregaveis/fonte/dossie-de-homologacao.md", "Dossiê de homologação", "inicio", "5.garantia_qualidade/entregaveis/LabMedSys - Modulo Garantia da Qualidade - Dossie de Homologacao.docx"),
            ("5.garantia_qualidade/entregaveis/fonte/regras-de-negocio.md", "Regras de negócio consolidadas", "negocio", "5.garantia_qualidade/entregaveis/LabMedSys - Modulo Garantia da Qualidade - Regras de Negocio.docx"),
            ("5.garantia_qualidade/entregaveis/fonte/manual-do-usuario.md", "Manual do usuário", "negocio", "5.garantia_qualidade/entregaveis/LabMedSys - Modulo Garantia da Qualidade - Manual do Usuario.docx"),
            ("5.garantia_qualidade/entregaveis/fonte/analise-de-requisitos.md", "Análise de requisitos", "tecnico", "5.garantia_qualidade/entregaveis/LabMedSys - Modulo Garantia da Qualidade - Analise de Requisitos.docx"),
            ("5.garantia_qualidade/08-plano-de-testes.md", "Plano de testes", "testes", None),
            ("versao-nova/5.garantia_qualidade/resumo-versao-nova.md", "Resumo dos testes", "novo", None),
            ("versao-nova/5.garantia_qualidade/execucao/2026-10-17/resultado.md", "Resultado da rodada 4", "novo", None),
            ("versao-nova/5.garantia_qualidade/execucao/2026-10-17-rodada-5/resultado.md", "Resultado da rodada 5", "novo", None),
            ("versao-nova/5.garantia_qualidade/execucao/2026-10-18-rodada-6/resultado.md", "Resultado da rodada 6", "novo", None),
            ("versao-nova/5.garantia_qualidade/execucao/2026-10-18-rodada-7/resultado.md", "Resultado da rodada 7", "novo", None),
            ("versao-nova/5.garantia_qualidade/execucao/2026-10-18-rodada-8/resultado.md", "Resultado da rodada 8", "novo", None),
            ("versao-nova/5.garantia_qualidade/execucao/2026-10-18-rodada-9/resultado.md", "Resultado da rodada 9", "novo", None),
            ("5.garantia_qualidade/roteiros/assuntos-regulatorios.md", "Roteiro de execução: Assuntos regulatórios (passo a passo)", "fluxos", "5.garantia_qualidade/roteiros/LabMedSys - Modulo Garantia da Qualidade - Roteiro de Testes Assuntos Regulatorios.docx"),
            ("5.garantia_qualidade/roteiros/treinamento.md", "Roteiro de execução: Treinamento técnico (passo a passo)", "fluxos", "5.garantia_qualidade/roteiros/LabMedSys - Modulo Garantia da Qualidade - Roteiro de Testes Treinamento.docx"),
            ("5.garantia_qualidade/roteiros/controle-mudancas.md", "Roteiro de execução: Controle de mudanças (passo a passo)", "fluxos", "5.garantia_qualidade/roteiros/LabMedSys - Modulo Garantia da Qualidade - Roteiro de Testes Controle de Mudancas.docx"),
            ("5.garantia_qualidade/roteiros/desvios-capa.md", "Roteiro de execução: Desvios e CAPA (passo a passo)", "fluxos", "5.garantia_qualidade/roteiros/LabMedSys - Modulo Garantia da Qualidade - Roteiro de Testes Desvios e CAPA.docx"),
            ("5.garantia_qualidade/roteiros/autoinspecao-auditoria.md", "Roteiro de execução: Autoinspeção e auditoria (passo a passo)", "fluxos", "5.garantia_qualidade/roteiros/LabMedSys - Modulo Garantia da Qualidade - Roteiro de Testes Autoinspecao e Auditoria.docx"),
            ("5.garantia_qualidade/04-conformidade-regulatoria.md", "Conformidade com a RDC 658/2022", "qualidade", None),
            ("5.garantia_qualidade/07-analise-de-risco.md", "Análise de risco", "qualidade", None),
            ("5.garantia_qualidade/06-modelo-de-dados.md", "Modelo de dados e integrações", "tecnico", None),
            ("5.garantia_qualidade/fluxos/desvios-capa.md", "Desvios e CAPA", "fluxos", "5.garantia_qualidade/fluxos/LabMedSys - Modulo Garantia da Qualidade - Fluxo Desvios e CAPA.docx"),
            ("5.garantia_qualidade/fluxos/autoinspecao-auditoria.md", "Autoinspeção e auditoria", "fluxos", "5.garantia_qualidade/fluxos/LabMedSys - Modulo Garantia da Qualidade - Fluxo Autoinspecao e Auditoria.docx"),
            ("5.garantia_qualidade/fluxos/treinamento.md", "Treinamento técnico", "fluxos", "5.garantia_qualidade/fluxos/LabMedSys - Modulo Garantia da Qualidade - Fluxo Treinamento.docx"),
            ("5.garantia_qualidade/fluxos/assuntos-regulatorios.md", "Assuntos regulatórios", "fluxos", "5.garantia_qualidade/fluxos/LabMedSys - Modulo Garantia da Qualidade - Fluxo Assuntos Regulatorios.docx"),
            ("5.garantia_qualidade/fluxos/controle-mudancas.md", "Controle de mudanças", "fluxos", "5.garantia_qualidade/fluxos/LabMedSys - Modulo Garantia da Qualidade - Fluxo Controle de Mudancas.docx"),
            ("5.garantia_qualidade/desvios/telas/00-entenda-o-menu.md", "Controle de Desvios: entenda o menu", "negocio", "5.garantia_qualidade/desvios/telas/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Entenda o Menu.docx", {"desvios": True, "intro": True}),
            ("5.garantia_qualidade/desvios/telas/00-visao-geral.md", "Controle de Desvios: visão geral", "negocio", "5.garantia_qualidade/desvios/telas/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Visao Geral.docx", {"desvios": True, "intro": True}),
            ("5.garantia_qualidade/desvios/paginas/01-relatorio-de-desvios/analise.md", "Relatório de Desvios: Análise", "negocio", "5.garantia_qualidade/desvios/paginas/01-relatorio-de-desvios/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 01 Relatório de Desvios - Análise.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Relatório de Desvios", "rotulo": "Análise", "tela_n": 1, "aba": "analise", "resumo": "Registrar o desvio: o que aconteceu, onde e qual item foi afetado"}),
            ("5.garantia_qualidade/desvios/paginas/01-relatorio-de-desvios/manual.md", "Relatório de Desvios: Manual do usuário", "negocio", "5.garantia_qualidade/desvios/paginas/01-relatorio-de-desvios/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 01 Relatório de Desvios - Manual do usuário.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Relatório de Desvios", "rotulo": "Manual do usuário", "tela_n": 1, "aba": "manual", "resumo": "Registrar o desvio: o que aconteceu, onde e qual item foi afetado"}),
            ("5.garantia_qualidade/desvios/paginas/01-relatorio-de-desvios/fluxos.md", "Relatório de Desvios: Fluxos", "negocio", "5.garantia_qualidade/desvios/paginas/01-relatorio-de-desvios/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 01 Relatório de Desvios - Fluxos.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Relatório de Desvios", "rotulo": "Fluxos", "tela_n": 1, "aba": "fluxos", "resumo": "Registrar o desvio: o que aconteceu, onde e qual item foi afetado"}),
            ("5.garantia_qualidade/desvios/paginas/01-relatorio-de-desvios/regras.md", "Relatório de Desvios: Regras de negócio", "negocio", "5.garantia_qualidade/desvios/paginas/01-relatorio-de-desvios/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 01 Relatório de Desvios - Regras de negócio.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Relatório de Desvios", "rotulo": "Regras de negócio", "tela_n": 1, "aba": "regras", "resumo": "Registrar o desvio: o que aconteceu, onde e qual item foi afetado"}),
            ("5.garantia_qualidade/desvios/paginas/01-relatorio-de-desvios/anvisa.md", "Relatório de Desvios: Anvisa", "negocio", "5.garantia_qualidade/desvios/paginas/01-relatorio-de-desvios/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 01 Relatório de Desvios - Anvisa.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Relatório de Desvios", "rotulo": "Anvisa", "tela_n": 1, "aba": "anvisa", "resumo": "Registrar o desvio: o que aconteceu, onde e qual item foi afetado"}),
            ("5.garantia_qualidade/desvios/paginas/02-registro-acao-corretiva-imediata/analise.md", "Registro Ação Corretiva Imediata: Análise", "negocio", "5.garantia_qualidade/desvios/paginas/02-registro-acao-corretiva-imediata/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 02 Registro Ação Corretiva Imediata - Análise.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Registro Ação Corretiva Imediata", "rotulo": "Análise", "tela_n": 2, "aba": "analise", "resumo": "Registrar a contenção feita na hora"}),
            ("5.garantia_qualidade/desvios/paginas/02-registro-acao-corretiva-imediata/manual.md", "Registro Ação Corretiva Imediata: Manual do usuário", "negocio", "5.garantia_qualidade/desvios/paginas/02-registro-acao-corretiva-imediata/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 02 Registro Ação Corretiva Imediata - Manual do usuário.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Registro Ação Corretiva Imediata", "rotulo": "Manual do usuário", "tela_n": 2, "aba": "manual", "resumo": "Registrar a contenção feita na hora"}),
            ("5.garantia_qualidade/desvios/paginas/02-registro-acao-corretiva-imediata/fluxos.md", "Registro Ação Corretiva Imediata: Fluxos", "negocio", "5.garantia_qualidade/desvios/paginas/02-registro-acao-corretiva-imediata/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 02 Registro Ação Corretiva Imediata - Fluxos.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Registro Ação Corretiva Imediata", "rotulo": "Fluxos", "tela_n": 2, "aba": "fluxos", "resumo": "Registrar a contenção feita na hora"}),
            ("5.garantia_qualidade/desvios/paginas/02-registro-acao-corretiva-imediata/regras.md", "Registro Ação Corretiva Imediata: Regras de negócio", "negocio", "5.garantia_qualidade/desvios/paginas/02-registro-acao-corretiva-imediata/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 02 Registro Ação Corretiva Imediata - Regras de negócio.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Registro Ação Corretiva Imediata", "rotulo": "Regras de negócio", "tela_n": 2, "aba": "regras", "resumo": "Registrar a contenção feita na hora"}),
            ("5.garantia_qualidade/desvios/paginas/02-registro-acao-corretiva-imediata/anvisa.md", "Registro Ação Corretiva Imediata: Anvisa", "negocio", "5.garantia_qualidade/desvios/paginas/02-registro-acao-corretiva-imediata/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 02 Registro Ação Corretiva Imediata - Anvisa.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Registro Ação Corretiva Imediata", "rotulo": "Anvisa", "tela_n": 2, "aba": "anvisa", "resumo": "Registrar a contenção feita na hora"}),
            ("5.garantia_qualidade/desvios/paginas/03-pre-avaliacao-relatorio-desvios/analise.md", "Pré Avaliação Relatório Desvios: Análise", "negocio", "5.garantia_qualidade/desvios/paginas/03-pre-avaliacao-relatorio-desvios/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 03 Pré Avaliação Relatório Desvios - Análise.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Pré Avaliação Relatório Desvios", "rotulo": "Análise", "tela_n": 3, "aba": "analise", "resumo": "Primeira leitura da GQ e escolha das áreas envolvidas"}),
            ("5.garantia_qualidade/desvios/paginas/03-pre-avaliacao-relatorio-desvios/manual.md", "Pré Avaliação Relatório Desvios: Manual do usuário", "negocio", "5.garantia_qualidade/desvios/paginas/03-pre-avaliacao-relatorio-desvios/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 03 Pré Avaliação Relatório Desvios - Manual do usuário.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Pré Avaliação Relatório Desvios", "rotulo": "Manual do usuário", "tela_n": 3, "aba": "manual", "resumo": "Primeira leitura da GQ e escolha das áreas envolvidas"}),
            ("5.garantia_qualidade/desvios/paginas/03-pre-avaliacao-relatorio-desvios/fluxos.md", "Pré Avaliação Relatório Desvios: Fluxos", "negocio", "5.garantia_qualidade/desvios/paginas/03-pre-avaliacao-relatorio-desvios/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 03 Pré Avaliação Relatório Desvios - Fluxos.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Pré Avaliação Relatório Desvios", "rotulo": "Fluxos", "tela_n": 3, "aba": "fluxos", "resumo": "Primeira leitura da GQ e escolha das áreas envolvidas"}),
            ("5.garantia_qualidade/desvios/paginas/03-pre-avaliacao-relatorio-desvios/regras.md", "Pré Avaliação Relatório Desvios: Regras de negócio", "negocio", "5.garantia_qualidade/desvios/paginas/03-pre-avaliacao-relatorio-desvios/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 03 Pré Avaliação Relatório Desvios - Regras de negócio.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Pré Avaliação Relatório Desvios", "rotulo": "Regras de negócio", "tela_n": 3, "aba": "regras", "resumo": "Primeira leitura da GQ e escolha das áreas envolvidas"}),
            ("5.garantia_qualidade/desvios/paginas/03-pre-avaliacao-relatorio-desvios/anvisa.md", "Pré Avaliação Relatório Desvios: Anvisa", "negocio", "5.garantia_qualidade/desvios/paginas/03-pre-avaliacao-relatorio-desvios/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 03 Pré Avaliação Relatório Desvios - Anvisa.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Pré Avaliação Relatório Desvios", "rotulo": "Anvisa", "tela_n": 3, "aba": "anvisa", "resumo": "Primeira leitura da GQ e escolha das áreas envolvidas"}),
            ("5.garantia_qualidade/desvios/paginas/04-avaliacao-area/analise.md", "Avaliação Área: Análise", "negocio", "5.garantia_qualidade/desvios/paginas/04-avaliacao-area/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 04 Avaliação Área - Análise.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Avaliação Área", "rotulo": "Análise", "tela_n": 4, "aba": "analise", "resumo": "Cada área envolvida dá o seu parecer"}),
            ("5.garantia_qualidade/desvios/paginas/04-avaliacao-area/manual.md", "Avaliação Área: Manual do usuário", "negocio", "5.garantia_qualidade/desvios/paginas/04-avaliacao-area/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 04 Avaliação Área - Manual do usuário.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Avaliação Área", "rotulo": "Manual do usuário", "tela_n": 4, "aba": "manual", "resumo": "Cada área envolvida dá o seu parecer"}),
            ("5.garantia_qualidade/desvios/paginas/04-avaliacao-area/fluxos.md", "Avaliação Área: Fluxos", "negocio", "5.garantia_qualidade/desvios/paginas/04-avaliacao-area/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 04 Avaliação Área - Fluxos.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Avaliação Área", "rotulo": "Fluxos", "tela_n": 4, "aba": "fluxos", "resumo": "Cada área envolvida dá o seu parecer"}),
            ("5.garantia_qualidade/desvios/paginas/04-avaliacao-area/regras.md", "Avaliação Área: Regras de negócio", "negocio", "5.garantia_qualidade/desvios/paginas/04-avaliacao-area/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 04 Avaliação Área - Regras de negócio.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Avaliação Área", "rotulo": "Regras de negócio", "tela_n": 4, "aba": "regras", "resumo": "Cada área envolvida dá o seu parecer"}),
            ("5.garantia_qualidade/desvios/paginas/04-avaliacao-area/anvisa.md", "Avaliação Área: Anvisa", "negocio", "5.garantia_qualidade/desvios/paginas/04-avaliacao-area/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 04 Avaliação Área - Anvisa.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Avaliação Área", "rotulo": "Anvisa", "tela_n": 4, "aba": "anvisa", "resumo": "Cada área envolvida dá o seu parecer"}),
            ("5.garantia_qualidade/desvios/paginas/05-avaliacao-relatorio-desvios/analise.md", "Avaliação Relatório Desvios: Análise", "negocio", "5.garantia_qualidade/desvios/paginas/05-avaliacao-relatorio-desvios/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 05 Avaliação Relatório Desvios - Análise.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Avaliação Relatório Desvios", "rotulo": "Análise", "tela_n": 5, "aba": "analise", "resumo": "A GQ conclui a avaliação e decide se abre CAPA"}),
            ("5.garantia_qualidade/desvios/paginas/05-avaliacao-relatorio-desvios/manual.md", "Avaliação Relatório Desvios: Manual do usuário", "negocio", "5.garantia_qualidade/desvios/paginas/05-avaliacao-relatorio-desvios/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 05 Avaliação Relatório Desvios - Manual do usuário.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Avaliação Relatório Desvios", "rotulo": "Manual do usuário", "tela_n": 5, "aba": "manual", "resumo": "A GQ conclui a avaliação e decide se abre CAPA"}),
            ("5.garantia_qualidade/desvios/paginas/05-avaliacao-relatorio-desvios/fluxos.md", "Avaliação Relatório Desvios: Fluxos", "negocio", "5.garantia_qualidade/desvios/paginas/05-avaliacao-relatorio-desvios/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 05 Avaliação Relatório Desvios - Fluxos.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Avaliação Relatório Desvios", "rotulo": "Fluxos", "tela_n": 5, "aba": "fluxos", "resumo": "A GQ conclui a avaliação e decide se abre CAPA"}),
            ("5.garantia_qualidade/desvios/paginas/05-avaliacao-relatorio-desvios/regras.md", "Avaliação Relatório Desvios: Regras de negócio", "negocio", "5.garantia_qualidade/desvios/paginas/05-avaliacao-relatorio-desvios/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 05 Avaliação Relatório Desvios - Regras de negócio.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Avaliação Relatório Desvios", "rotulo": "Regras de negócio", "tela_n": 5, "aba": "regras", "resumo": "A GQ conclui a avaliação e decide se abre CAPA"}),
            ("5.garantia_qualidade/desvios/paginas/05-avaliacao-relatorio-desvios/anvisa.md", "Avaliação Relatório Desvios: Anvisa", "negocio", "5.garantia_qualidade/desvios/paginas/05-avaliacao-relatorio-desvios/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 05 Avaliação Relatório Desvios - Anvisa.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Avaliação Relatório Desvios", "rotulo": "Anvisa", "tela_n": 5, "aba": "anvisa", "resumo": "A GQ conclui a avaliação e decide se abre CAPA"}),
            ("5.garantia_qualidade/desvios/paginas/06-relatorio-de-capa/analise.md", "Relatório de CAPA: Análise", "negocio", "5.garantia_qualidade/desvios/paginas/06-relatorio-de-capa/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 06 Relatório de CAPA - Análise.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Relatório de CAPA", "rotulo": "Análise", "tela_n": 6, "aba": "analise", "resumo": "Investigação da causa, impacto e criticidade"}),
            ("5.garantia_qualidade/desvios/paginas/06-relatorio-de-capa/manual.md", "Relatório de CAPA: Manual do usuário", "negocio", "5.garantia_qualidade/desvios/paginas/06-relatorio-de-capa/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 06 Relatório de CAPA - Manual do usuário.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Relatório de CAPA", "rotulo": "Manual do usuário", "tela_n": 6, "aba": "manual", "resumo": "Investigação da causa, impacto e criticidade"}),
            ("5.garantia_qualidade/desvios/paginas/06-relatorio-de-capa/fluxos.md", "Relatório de CAPA: Fluxos", "negocio", "5.garantia_qualidade/desvios/paginas/06-relatorio-de-capa/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 06 Relatório de CAPA - Fluxos.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Relatório de CAPA", "rotulo": "Fluxos", "tela_n": 6, "aba": "fluxos", "resumo": "Investigação da causa, impacto e criticidade"}),
            ("5.garantia_qualidade/desvios/paginas/06-relatorio-de-capa/regras.md", "Relatório de CAPA: Regras de negócio", "negocio", "5.garantia_qualidade/desvios/paginas/06-relatorio-de-capa/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 06 Relatório de CAPA - Regras de negócio.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Relatório de CAPA", "rotulo": "Regras de negócio", "tela_n": 6, "aba": "regras", "resumo": "Investigação da causa, impacto e criticidade"}),
            ("5.garantia_qualidade/desvios/paginas/06-relatorio-de-capa/anvisa.md", "Relatório de CAPA: Anvisa", "negocio", "5.garantia_qualidade/desvios/paginas/06-relatorio-de-capa/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 06 Relatório de CAPA - Anvisa.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Relatório de CAPA", "rotulo": "Anvisa", "tela_n": 6, "aba": "anvisa", "resumo": "Investigação da causa, impacto e criticidade"}),
            ("5.garantia_qualidade/desvios/paginas/07-plano-de-acao-corretiva/analise.md", "Plano de Ação Corretiva: Análise", "negocio", "5.garantia_qualidade/desvios/paginas/07-plano-de-acao-corretiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 07 Plano de Ação Corretiva - Análise.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Plano de Ação Corretiva", "rotulo": "Análise", "tela_n": 7, "aba": "analise", "resumo": "Definir as ações corretivas, responsáveis e prazos"}),
            ("5.garantia_qualidade/desvios/paginas/07-plano-de-acao-corretiva/manual.md", "Plano de Ação Corretiva: Manual do usuário", "negocio", "5.garantia_qualidade/desvios/paginas/07-plano-de-acao-corretiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 07 Plano de Ação Corretiva - Manual do usuário.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Plano de Ação Corretiva", "rotulo": "Manual do usuário", "tela_n": 7, "aba": "manual", "resumo": "Definir as ações corretivas, responsáveis e prazos"}),
            ("5.garantia_qualidade/desvios/paginas/07-plano-de-acao-corretiva/fluxos.md", "Plano de Ação Corretiva: Fluxos", "negocio", "5.garantia_qualidade/desvios/paginas/07-plano-de-acao-corretiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 07 Plano de Ação Corretiva - Fluxos.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Plano de Ação Corretiva", "rotulo": "Fluxos", "tela_n": 7, "aba": "fluxos", "resumo": "Definir as ações corretivas, responsáveis e prazos"}),
            ("5.garantia_qualidade/desvios/paginas/07-plano-de-acao-corretiva/regras.md", "Plano de Ação Corretiva: Regras de negócio", "negocio", "5.garantia_qualidade/desvios/paginas/07-plano-de-acao-corretiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 07 Plano de Ação Corretiva - Regras de negócio.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Plano de Ação Corretiva", "rotulo": "Regras de negócio", "tela_n": 7, "aba": "regras", "resumo": "Definir as ações corretivas, responsáveis e prazos"}),
            ("5.garantia_qualidade/desvios/paginas/07-plano-de-acao-corretiva/anvisa.md", "Plano de Ação Corretiva: Anvisa", "negocio", "5.garantia_qualidade/desvios/paginas/07-plano-de-acao-corretiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 07 Plano de Ação Corretiva - Anvisa.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Plano de Ação Corretiva", "rotulo": "Anvisa", "tela_n": 7, "aba": "anvisa", "resumo": "Definir as ações corretivas, responsáveis e prazos"}),
            ("5.garantia_qualidade/desvios/paginas/08-execucao-do-plano-de-acao-corretiva/analise.md", "Execução do Plano de Ação Corretiva: Análise", "negocio", "5.garantia_qualidade/desvios/paginas/08-execucao-do-plano-de-acao-corretiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 08 Execução do Plano de Ação Corretiva - Análise.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Execução do Plano de Ação Corretiva", "rotulo": "Análise", "tela_n": 8, "aba": "analise", "resumo": "Cada responsável informa a conclusão da sua ação"}),
            ("5.garantia_qualidade/desvios/paginas/08-execucao-do-plano-de-acao-corretiva/manual.md", "Execução do Plano de Ação Corretiva: Manual do usuário", "negocio", "5.garantia_qualidade/desvios/paginas/08-execucao-do-plano-de-acao-corretiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 08 Execução do Plano de Ação Corretiva - Manual do usuário.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Execução do Plano de Ação Corretiva", "rotulo": "Manual do usuário", "tela_n": 8, "aba": "manual", "resumo": "Cada responsável informa a conclusão da sua ação"}),
            ("5.garantia_qualidade/desvios/paginas/08-execucao-do-plano-de-acao-corretiva/fluxos.md", "Execução do Plano de Ação Corretiva: Fluxos", "negocio", "5.garantia_qualidade/desvios/paginas/08-execucao-do-plano-de-acao-corretiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 08 Execução do Plano de Ação Corretiva - Fluxos.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Execução do Plano de Ação Corretiva", "rotulo": "Fluxos", "tela_n": 8, "aba": "fluxos", "resumo": "Cada responsável informa a conclusão da sua ação"}),
            ("5.garantia_qualidade/desvios/paginas/08-execucao-do-plano-de-acao-corretiva/regras.md", "Execução do Plano de Ação Corretiva: Regras de negócio", "negocio", "5.garantia_qualidade/desvios/paginas/08-execucao-do-plano-de-acao-corretiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 08 Execução do Plano de Ação Corretiva - Regras de negócio.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Execução do Plano de Ação Corretiva", "rotulo": "Regras de negócio", "tela_n": 8, "aba": "regras", "resumo": "Cada responsável informa a conclusão da sua ação"}),
            ("5.garantia_qualidade/desvios/paginas/08-execucao-do-plano-de-acao-corretiva/anvisa.md", "Execução do Plano de Ação Corretiva: Anvisa", "negocio", "5.garantia_qualidade/desvios/paginas/08-execucao-do-plano-de-acao-corretiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 08 Execução do Plano de Ação Corretiva - Anvisa.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Execução do Plano de Ação Corretiva", "rotulo": "Anvisa", "tela_n": 8, "aba": "anvisa", "resumo": "Cada responsável informa a conclusão da sua ação"}),
            ("5.garantia_qualidade/desvios/paginas/09-monitoramento-do-plano-de-acao-corretiva/analise.md", "Monitoramento do Plano de Ação Corretiva: Análise", "negocio", "5.garantia_qualidade/desvios/paginas/09-monitoramento-do-plano-de-acao-corretiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 09 Monitoramento do Plano de Ação Corretiva - Análise.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Monitoramento do Plano de Ação Corretiva", "rotulo": "Análise", "tela_n": 9, "aba": "analise", "resumo": "Verificação final do plano corretivo"}),
            ("5.garantia_qualidade/desvios/paginas/09-monitoramento-do-plano-de-acao-corretiva/manual.md", "Monitoramento do Plano de Ação Corretiva: Manual do usuário", "negocio", "5.garantia_qualidade/desvios/paginas/09-monitoramento-do-plano-de-acao-corretiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 09 Monitoramento do Plano de Ação Corretiva - Manual do usuário.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Monitoramento do Plano de Ação Corretiva", "rotulo": "Manual do usuário", "tela_n": 9, "aba": "manual", "resumo": "Verificação final do plano corretivo"}),
            ("5.garantia_qualidade/desvios/paginas/09-monitoramento-do-plano-de-acao-corretiva/fluxos.md", "Monitoramento do Plano de Ação Corretiva: Fluxos", "negocio", "5.garantia_qualidade/desvios/paginas/09-monitoramento-do-plano-de-acao-corretiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 09 Monitoramento do Plano de Ação Corretiva - Fluxos.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Monitoramento do Plano de Ação Corretiva", "rotulo": "Fluxos", "tela_n": 9, "aba": "fluxos", "resumo": "Verificação final do plano corretivo"}),
            ("5.garantia_qualidade/desvios/paginas/09-monitoramento-do-plano-de-acao-corretiva/regras.md", "Monitoramento do Plano de Ação Corretiva: Regras de negócio", "negocio", "5.garantia_qualidade/desvios/paginas/09-monitoramento-do-plano-de-acao-corretiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 09 Monitoramento do Plano de Ação Corretiva - Regras de negócio.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Monitoramento do Plano de Ação Corretiva", "rotulo": "Regras de negócio", "tela_n": 9, "aba": "regras", "resumo": "Verificação final do plano corretivo"}),
            ("5.garantia_qualidade/desvios/paginas/09-monitoramento-do-plano-de-acao-corretiva/anvisa.md", "Monitoramento do Plano de Ação Corretiva: Anvisa", "negocio", "5.garantia_qualidade/desvios/paginas/09-monitoramento-do-plano-de-acao-corretiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 09 Monitoramento do Plano de Ação Corretiva - Anvisa.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Monitoramento do Plano de Ação Corretiva", "rotulo": "Anvisa", "tela_n": 9, "aba": "anvisa", "resumo": "Verificação final do plano corretivo"}),
            ("5.garantia_qualidade/desvios/paginas/10-plano-de-acao-preventiva/analise.md", "Plano de Ação Preventiva: Análise", "negocio", "5.garantia_qualidade/desvios/paginas/10-plano-de-acao-preventiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 10 Plano de Ação Preventiva - Análise.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Plano de Ação Preventiva", "rotulo": "Análise", "tela_n": 10, "aba": "analise", "resumo": "Definir as ações para o desvio não se repetir"}),
            ("5.garantia_qualidade/desvios/paginas/10-plano-de-acao-preventiva/manual.md", "Plano de Ação Preventiva: Manual do usuário", "negocio", "5.garantia_qualidade/desvios/paginas/10-plano-de-acao-preventiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 10 Plano de Ação Preventiva - Manual do usuário.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Plano de Ação Preventiva", "rotulo": "Manual do usuário", "tela_n": 10, "aba": "manual", "resumo": "Definir as ações para o desvio não se repetir"}),
            ("5.garantia_qualidade/desvios/paginas/10-plano-de-acao-preventiva/fluxos.md", "Plano de Ação Preventiva: Fluxos", "negocio", "5.garantia_qualidade/desvios/paginas/10-plano-de-acao-preventiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 10 Plano de Ação Preventiva - Fluxos.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Plano de Ação Preventiva", "rotulo": "Fluxos", "tela_n": 10, "aba": "fluxos", "resumo": "Definir as ações para o desvio não se repetir"}),
            ("5.garantia_qualidade/desvios/paginas/10-plano-de-acao-preventiva/regras.md", "Plano de Ação Preventiva: Regras de negócio", "negocio", "5.garantia_qualidade/desvios/paginas/10-plano-de-acao-preventiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 10 Plano de Ação Preventiva - Regras de negócio.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Plano de Ação Preventiva", "rotulo": "Regras de negócio", "tela_n": 10, "aba": "regras", "resumo": "Definir as ações para o desvio não se repetir"}),
            ("5.garantia_qualidade/desvios/paginas/10-plano-de-acao-preventiva/anvisa.md", "Plano de Ação Preventiva: Anvisa", "negocio", "5.garantia_qualidade/desvios/paginas/10-plano-de-acao-preventiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 10 Plano de Ação Preventiva - Anvisa.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Plano de Ação Preventiva", "rotulo": "Anvisa", "tela_n": 10, "aba": "anvisa", "resumo": "Definir as ações para o desvio não se repetir"}),
            ("5.garantia_qualidade/desvios/paginas/11-execucao-plano-de-acao-preventiva/analise.md", "Execução Plano de Ação Preventiva: Análise", "negocio", "5.garantia_qualidade/desvios/paginas/11-execucao-plano-de-acao-preventiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 11 Execução Plano de Ação Preventiva - Análise.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Execução Plano de Ação Preventiva", "rotulo": "Análise", "tela_n": 11, "aba": "analise", "resumo": "Cada responsável informa a conclusão da ação preventiva"}),
            ("5.garantia_qualidade/desvios/paginas/11-execucao-plano-de-acao-preventiva/manual.md", "Execução Plano de Ação Preventiva: Manual do usuário", "negocio", "5.garantia_qualidade/desvios/paginas/11-execucao-plano-de-acao-preventiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 11 Execução Plano de Ação Preventiva - Manual do usuário.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Execução Plano de Ação Preventiva", "rotulo": "Manual do usuário", "tela_n": 11, "aba": "manual", "resumo": "Cada responsável informa a conclusão da ação preventiva"}),
            ("5.garantia_qualidade/desvios/paginas/11-execucao-plano-de-acao-preventiva/fluxos.md", "Execução Plano de Ação Preventiva: Fluxos", "negocio", "5.garantia_qualidade/desvios/paginas/11-execucao-plano-de-acao-preventiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 11 Execução Plano de Ação Preventiva - Fluxos.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Execução Plano de Ação Preventiva", "rotulo": "Fluxos", "tela_n": 11, "aba": "fluxos", "resumo": "Cada responsável informa a conclusão da ação preventiva"}),
            ("5.garantia_qualidade/desvios/paginas/11-execucao-plano-de-acao-preventiva/regras.md", "Execução Plano de Ação Preventiva: Regras de negócio", "negocio", "5.garantia_qualidade/desvios/paginas/11-execucao-plano-de-acao-preventiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 11 Execução Plano de Ação Preventiva - Regras de negócio.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Execução Plano de Ação Preventiva", "rotulo": "Regras de negócio", "tela_n": 11, "aba": "regras", "resumo": "Cada responsável informa a conclusão da ação preventiva"}),
            ("5.garantia_qualidade/desvios/paginas/11-execucao-plano-de-acao-preventiva/anvisa.md", "Execução Plano de Ação Preventiva: Anvisa", "negocio", "5.garantia_qualidade/desvios/paginas/11-execucao-plano-de-acao-preventiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 11 Execução Plano de Ação Preventiva - Anvisa.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Execução Plano de Ação Preventiva", "rotulo": "Anvisa", "tela_n": 11, "aba": "anvisa", "resumo": "Cada responsável informa a conclusão da ação preventiva"}),
            ("5.garantia_qualidade/desvios/paginas/12-monitoramento-do-plano-de-acao-preventiva/analise.md", "Monitoramento do Plano de Ação Preventiva: Análise", "negocio", "5.garantia_qualidade/desvios/paginas/12-monitoramento-do-plano-de-acao-preventiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 12 Monitoramento do Plano de Ação Preventiva - Análise.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Monitoramento do Plano de Ação Preventiva", "rotulo": "Análise", "tela_n": 12, "aba": "analise", "resumo": "Verificação final e encerramento do desvio"}),
            ("5.garantia_qualidade/desvios/paginas/12-monitoramento-do-plano-de-acao-preventiva/manual.md", "Monitoramento do Plano de Ação Preventiva: Manual do usuário", "negocio", "5.garantia_qualidade/desvios/paginas/12-monitoramento-do-plano-de-acao-preventiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 12 Monitoramento do Plano de Ação Preventiva - Manual do usuário.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Monitoramento do Plano de Ação Preventiva", "rotulo": "Manual do usuário", "tela_n": 12, "aba": "manual", "resumo": "Verificação final e encerramento do desvio"}),
            ("5.garantia_qualidade/desvios/paginas/12-monitoramento-do-plano-de-acao-preventiva/fluxos.md", "Monitoramento do Plano de Ação Preventiva: Fluxos", "negocio", "5.garantia_qualidade/desvios/paginas/12-monitoramento-do-plano-de-acao-preventiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 12 Monitoramento do Plano de Ação Preventiva - Fluxos.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Monitoramento do Plano de Ação Preventiva", "rotulo": "Fluxos", "tela_n": 12, "aba": "fluxos", "resumo": "Verificação final e encerramento do desvio"}),
            ("5.garantia_qualidade/desvios/paginas/12-monitoramento-do-plano-de-acao-preventiva/regras.md", "Monitoramento do Plano de Ação Preventiva: Regras de negócio", "negocio", "5.garantia_qualidade/desvios/paginas/12-monitoramento-do-plano-de-acao-preventiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 12 Monitoramento do Plano de Ação Preventiva - Regras de negócio.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Monitoramento do Plano de Ação Preventiva", "rotulo": "Regras de negócio", "tela_n": 12, "aba": "regras", "resumo": "Verificação final e encerramento do desvio"}),
            ("5.garantia_qualidade/desvios/paginas/12-monitoramento-do-plano-de-acao-preventiva/anvisa.md", "Monitoramento do Plano de Ação Preventiva: Anvisa", "negocio", "5.garantia_qualidade/desvios/paginas/12-monitoramento-do-plano-de-acao-preventiva/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 12 Monitoramento do Plano de Ação Preventiva - Anvisa.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Monitoramento do Plano de Ação Preventiva", "rotulo": "Anvisa", "tela_n": 12, "aba": "anvisa", "resumo": "Verificação final e encerramento do desvio"}),
            ("5.garantia_qualidade/desvios/paginas/13-acompanhamento-rd/analise.md", "Acompanhamento RD: Análise", "negocio", "5.garantia_qualidade/desvios/paginas/13-acompanhamento-rd/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 13 Acompanhamento RD - Análise.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Acompanhamento RD", "rotulo": "Análise", "tela_n": 13, "aba": "analise", "resumo": "Os desvios por período e situação, para imprimir"}),
            ("5.garantia_qualidade/desvios/paginas/13-acompanhamento-rd/manual.md", "Acompanhamento RD: Manual do usuário", "negocio", "5.garantia_qualidade/desvios/paginas/13-acompanhamento-rd/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 13 Acompanhamento RD - Manual do usuário.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Acompanhamento RD", "rotulo": "Manual do usuário", "tela_n": 13, "aba": "manual", "resumo": "Os desvios por período e situação, para imprimir"}),
            ("5.garantia_qualidade/desvios/paginas/13-acompanhamento-rd/fluxos.md", "Acompanhamento RD: Fluxos", "negocio", "5.garantia_qualidade/desvios/paginas/13-acompanhamento-rd/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 13 Acompanhamento RD - Fluxos.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Acompanhamento RD", "rotulo": "Fluxos", "tela_n": 13, "aba": "fluxos", "resumo": "Os desvios por período e situação, para imprimir"}),
            ("5.garantia_qualidade/desvios/paginas/13-acompanhamento-rd/regras.md", "Acompanhamento RD: Regras de negócio", "negocio", "5.garantia_qualidade/desvios/paginas/13-acompanhamento-rd/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 13 Acompanhamento RD - Regras de negócio.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Acompanhamento RD", "rotulo": "Regras de negócio", "tela_n": 13, "aba": "regras", "resumo": "Os desvios por período e situação, para imprimir"}),
            ("5.garantia_qualidade/desvios/paginas/13-acompanhamento-rd/anvisa.md", "Acompanhamento RD: Anvisa", "negocio", "5.garantia_qualidade/desvios/paginas/13-acompanhamento-rd/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 13 Acompanhamento RD - Anvisa.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Acompanhamento RD", "rotulo": "Anvisa", "tela_n": 13, "aba": "anvisa", "resumo": "Os desvios por período e situação, para imprimir"}),
            ("5.garantia_qualidade/desvios/paginas/14-controle-de-emissao-de-rnc/analise.md", "Controle de Emissão de RNC: Análise", "negocio", "5.garantia_qualidade/desvios/paginas/14-controle-de-emissao-de-rnc/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 14 Controle de Emissão de RNC - Análise.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Controle de Emissão de RNC", "rotulo": "Análise", "tela_n": 14, "aba": "analise", "resumo": "Os relatórios emitidos, por ano, para imprimir"}),
            ("5.garantia_qualidade/desvios/paginas/14-controle-de-emissao-de-rnc/manual.md", "Controle de Emissão de RNC: Manual do usuário", "negocio", "5.garantia_qualidade/desvios/paginas/14-controle-de-emissao-de-rnc/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 14 Controle de Emissão de RNC - Manual do usuário.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Controle de Emissão de RNC", "rotulo": "Manual do usuário", "tela_n": 14, "aba": "manual", "resumo": "Os relatórios emitidos, por ano, para imprimir"}),
            ("5.garantia_qualidade/desvios/paginas/14-controle-de-emissao-de-rnc/fluxos.md", "Controle de Emissão de RNC: Fluxos", "negocio", "5.garantia_qualidade/desvios/paginas/14-controle-de-emissao-de-rnc/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 14 Controle de Emissão de RNC - Fluxos.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Controle de Emissão de RNC", "rotulo": "Fluxos", "tela_n": 14, "aba": "fluxos", "resumo": "Os relatórios emitidos, por ano, para imprimir"}),
            ("5.garantia_qualidade/desvios/paginas/14-controle-de-emissao-de-rnc/regras.md", "Controle de Emissão de RNC: Regras de negócio", "negocio", "5.garantia_qualidade/desvios/paginas/14-controle-de-emissao-de-rnc/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 14 Controle de Emissão de RNC - Regras de negócio.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Controle de Emissão de RNC", "rotulo": "Regras de negócio", "tela_n": 14, "aba": "regras", "resumo": "Os relatórios emitidos, por ano, para imprimir"}),
            ("5.garantia_qualidade/desvios/paginas/14-controle-de-emissao-de-rnc/anvisa.md", "Controle de Emissão de RNC: Anvisa", "negocio", "5.garantia_qualidade/desvios/paginas/14-controle-de-emissao-de-rnc/LabMedSys - Modulo Garantia da Qualidade - Controle de Desvios - Tela 14 Controle de Emissão de RNC - Anvisa.docx", {"desvios": True, "grupo": "Controle de Desvios", "tela": "Controle de Emissão de RNC", "rotulo": "Anvisa", "tela_n": 14, "aba": "anvisa", "resumo": "Os relatórios emitidos, por ano, para imprimir"}),
        ],
    },
    {"id": "producao", "nome": "Produção", "icone": "⚙", "cor": "#b45309", "situacao": "Pronto para testes", "nivel": 2,
     "resumo": "Ordem de produção, autorizações para produzir, pesagem, registro de lote por etapas, preparação (limpeza, calibração, qualificação, manutenção, água e ambiente), final da produção e envio do produto acabado ao Estoque. Reconhecimento feito: 238 páginas, 79 itens de menu em 7 grupos, 137 tabelas; o registro de lote é montado por modelos XML e programado produto a produto. Conformidade com a RDC 658/2022: dos 18 temas, 1 atendido, 12 em parte e 5 não atendidos. Fluxos prontos: autorização, início e final da produção; registro de lote; produto, fórmula e ordem de produção; preparação; terceirização e validade da OPE. As 135 regras de negócio, o inventário das 89 telas, o modelo de dados (conferido com o dicionário de dados) e a análise de risco (26 riscos, 21 de prioridade alta). Análise pelo código concluída: plano de testes com 88 casos, 24 de prioridade alta, e o modelo ideal do módulo.",
     "docs": [
         ("2.producao/00-reconhecimento.md", "Reconhecimento do módulo", "inicio", None),
         ("2.producao/ideal/pro-ideal.md", "A Produção ideal", "ideal", "2.producao/ideal/LabMedSys - Modulo Producao - O Ideal.docx"),
         ("2.producao/ideal/pro-entre-modulos.md", "A Produção entre os módulos: as travas", "ideal", "2.producao/ideal/LabMedSys - Modulo Producao - Entre os Modulos.docx"),
         ("2.producao/11-inventario-de-telas.md", "Inventário de telas e situação", "inicio", None),
         ("2.producao/01-regras-de-negocio.md", "Regras de negócio", "negocio", None),
         ("2.producao/02-matriz-de-permissoes.md", "Matriz de permissões", "negocio", None),
         ("2.producao/08-plano-de-testes.md", "Plano de testes", "testes", None),
         ("2.producao/04-conformidade-regulatoria.md", "Conformidade com a RDC 658/2022", "qualidade", None),
         ("2.producao/07-analise-de-risco.md", "Análise de risco", "qualidade", None),
         ("2.producao/06-modelo-de-dados.md", "Modelo de dados e integrações", "tecnico", None),
         ("2.producao/fluxos/autorizacao-inicio-final.md", "Autorização, início e final da produção", "fluxos", "2.producao/fluxos/LabMedSys - Modulo Producao - Fluxo Autorizacao, Inicio e Final.docx"),
         ("2.producao/fluxos/registro-de-lote.md", "Registro de lote", "fluxos", "2.producao/fluxos/LabMedSys - Modulo Producao - Fluxo Registro de Lote.docx"),
         ("2.producao/fluxos/produto-formula-ordem.md", "Produto, fórmula e ordem de produção", "fluxos", "2.producao/fluxos/LabMedSys - Modulo Producao - Fluxo Produto, Formula e Ordem de Producao.docx"),
         ("2.producao/fluxos/preparacao.md", "Preparação: limpeza, calibração, qualificação, manutenção, água e ambiente", "fluxos", "2.producao/fluxos/LabMedSys - Modulo Producao - Fluxo Preparacao.docx"),
         ("2.producao/fluxos/terceirizacao-validade.md", "Terceirização e validade da OPE", "fluxos", "2.producao/fluxos/LabMedSys - Modulo Producao - Fluxo Terceirizacao e Validade da OPE.docx"),
     ]},
    {"id": "controle-qualidade", "nome": "Controle da Qualidade", "icone": "✧", "cor": "#2e9b4f", "situacao": "Em testes", "nivel": 2,
     "resumo": "Solicitação de análise, amostragem, análise, laudo, etiqueta e estabilidade. Reconhecimento e conformidade com a RDC 658/2022 feitos: 25 telas (22 com lógica, 3 protótipos); dos 16 temas da norma, 8 atendidos em parte e 8 não atendidos. Os quatro fluxos prontos (solicitação ao laudo, regras de amostragem e de análise, estabilidade, água e ambiente), as 119 regras de negócio, o inventário das telas, as permissões, o modelo de dados, a análise de risco e o plano de testes (61 casos). Análise pelo código concluída. Rodada 1 de testes em tela em 23/10/2026 (legado, com massa de dados): dos 61 casos do plano, 17 passaram, 10 com ressalva, 21 falharam e 13 ficaram bloqueados (estabilidade, pelo DV-EST-074 do Estoque, e água, pela falta de uma tabela no banco); 26 defeitos registrados (8 Alta), entre eles qualquer usuário aprova o laudo, o laudo reprovado vale sem ser emitido e aprovar, emitir e corrigir resultado não deixam histórico.",
     "docs": [
         ("4.controle_qualidade/00-reconhecimento.md", "Reconhecimento do módulo", "inicio", None),
         ("4.controle_qualidade/ideal/cq-ideal.md", "O Controle da Qualidade ideal", "ideal", "4.controle_qualidade/ideal/LabMedSys - Modulo Controle da Qualidade - O Ideal.docx"),
         ("4.controle_qualidade/ideal/cq-entre-modulos.md", "O Controle da Qualidade entre os módulos: as travas", "ideal", "4.controle_qualidade/ideal/LabMedSys - Modulo Controle da Qualidade - Entre os Modulos.docx"),
         ("4.controle_qualidade/11-inventario-de-telas.md", "Inventário de telas e situação", "inicio", None),
         ("4.controle_qualidade/01-regras-de-negocio.md", "Regras de negócio", "negocio", None),
         ("4.controle_qualidade/02-matriz-de-permissoes.md", "Matriz de permissões", "negocio", None),
         ("4.controle_qualidade/08-plano-de-testes.md", "Plano de testes", "testes", None),
         ("versao-nova/4.controle_qualidade/resumo-versao-nova.md", "Situação na versão nova", "novo", None),
         ("4.controle_qualidade/entregaveis/fonte/relatorio-de-testes.md", "Relatório de testes", "inicio", "4.controle_qualidade/entregaveis/LabMedSys - Modulo Controle da Qualidade - Relatorio de Testes.docx"),
         ("4.controle_qualidade/defeitos/defeitos.md", "Defeitos para correção", "defeitos", "4.controle_qualidade/defeitos/LabMedSys - Modulo Controle da Qualidade - Defeitos para Correcao.docx"),
         ("4.controle_qualidade/04-conformidade-regulatoria.md", "Conformidade com a RDC 658/2022", "qualidade", None),
         ("4.controle_qualidade/07-analise-de-risco.md", "Análise de risco", "qualidade", None),
         ("4.controle_qualidade/06-modelo-de-dados.md", "Modelo de dados e integrações", "tecnico", None),
         ("4.controle_qualidade/fluxos/solicitacao-analise-laudo.md", "Solicitação, análise e laudo", "fluxos", "4.controle_qualidade/fluxos/LabMedSys - Modulo Controle da Qualidade - Fluxo Solicitacao, Analise e Laudo.docx"),
         ("4.controle_qualidade/fluxos/regras-amostragem-analise.md", "Regras de amostragem e de análise", "fluxos", "4.controle_qualidade/fluxos/LabMedSys - Modulo Controle da Qualidade - Fluxo Regras de Amostragem e de Analise.docx"),
         ("4.controle_qualidade/fluxos/estabilidade.md", "Estabilidade", "fluxos", "4.controle_qualidade/fluxos/LabMedSys - Modulo Controle da Qualidade - Fluxo Estabilidade.docx"),
         ("4.controle_qualidade/fluxos/agua-ambiente.md", "Água e ambiente", "fluxos", "4.controle_qualidade/fluxos/LabMedSys - Modulo Controle da Qualidade - Fluxo Agua e Ambiente.docx"),
     ]},
    {"id": "controle-documentos", "nome": "Controle de Documentos", "icone": "▤", "cor": "#4f6d8f", "situacao": "Pronto para testes", "nivel": 2,
     "resumo": "Ciclo do documento (inclusão, revisão, pré-aprovação, aprovação com senha, vigência, nova revisão, obsolescência), controle de cópias, documentos externos e legados, tipos de documento, arquivos e modelos. Reconhecimento e conformidade com a RDC 658/2022 feitos: 11 pastas de telas, 72 páginas, 10 situações do documento; dos 13 temas da norma, 1 atendido, 8 em parte, 3 não atendidos e 1 a verificar. Os quatro fluxos prontos (ciclo do documento, controle de cópias, documento externo e legado, tipo de documento e arquivos), as 67 regras de negócio, o inventário das 17 telas, o modelo de dados (9 tabelas usadas pelo código fora do projeto de banco) e a análise de risco (22 riscos, 15 de prioridade alta). Análise pelo código concluída: plano de testes com 45 casos, 19 de prioridade alta, e o modelo ideal do módulo.",
     "docs": [
         ("6.controle_documento/00-reconhecimento.md", "Reconhecimento do módulo", "inicio", None),
         ("6.controle_documento/ideal/doc-ideal.md", "O Controle de Documentos ideal", "ideal", "6.controle_documento/ideal/LabMedSys - Modulo Controle de Documentos - O Ideal.docx"),
         ("6.controle_documento/ideal/doc-entre-modulos.md", "Documentos entre os módulos: versão vigente e travas", "ideal", "6.controle_documento/ideal/LabMedSys - Modulo Controle de Documentos - Documentos entre os Modulos.docx"),
         ("6.controle_documento/11-inventario-de-telas.md", "Inventário de telas e situação", "inicio", None),
         ("6.controle_documento/01-regras-de-negocio.md", "Regras de negócio", "negocio", None),
         ("6.controle_documento/04-conformidade-regulatoria.md", "Conformidade com a RDC 658/2022", "qualidade", None),
         ("6.controle_documento/07-analise-de-risco.md", "Análise de risco", "qualidade", None),
         ("6.controle_documento/06-modelo-de-dados.md", "Modelo de dados e integrações", "tecnico", None),
         ("6.controle_documento/08-plano-de-testes.md", "Plano de testes", "testes", None),
         ("versao-nova/6.controle_documento/resumo-versao-nova.md", "Situação na versão nova", "novo", None),
         ("6.controle_documento/fluxos/ciclo-documento.md", "Ciclo do documento", "fluxos", "6.controle_documento/fluxos/LabMedSys - Modulo Controle de Documentos - Fluxo Ciclo do Documento.docx"),
         ("6.controle_documento/fluxos/controle-copias.md", "Controle de cópias", "fluxos", "6.controle_documento/fluxos/LabMedSys - Modulo Controle de Documentos - Fluxo Controle de Copias.docx"),
         ("6.controle_documento/fluxos/externo-legado.md", "Documento externo e documento legado", "fluxos", "6.controle_documento/fluxos/LabMedSys - Modulo Controle de Documentos - Fluxo Documento Externo e Legado.docx"),
         ("6.controle_documento/fluxos/tipo-arquivos-modelos.md", "Tipo de documento, arquivos e modelos", "fluxos", "6.controle_documento/fluxos/LabMedSys - Modulo Controle de Documentos - Fluxo Tipo de Documento, Arquivos e Modelos.docx"),
     ]},
    {"id": "ope", "nome": "OPE (Gerador de OPE)", "icone": "⚒", "cor": "#7c3aed", "situacao": "Pronto para testes", "nivel": 2,
     "resumo": "Ferramenta que monta o modelo do registro de lote de cada produto: etapas, subetapas, campos, cálculos, validações e quem assina cada campo. A Produção usa esse modelo em cada lote. O modelo não tem versão, aprovação nem histórico; cada ajuste regrava o modelo em uso, e ele chega à ordem de produção por arquivo baixado e reenviado. Fluxo pronto, com a análise de por que a ferramenta confunde o usuário. Análise pelo código concluída: 36 regras, 16 telas, conformidade (9 temas: nenhum atendido, 3 em parte, 5 não atendidos), 17 riscos (12 de prioridade alta) e plano de testes com 24 casos. O ideal: o modelo só chega à Produção aprovado, como versão vigente, a partir de uma mudança aprovada na GQ.",
     "docs": [
         ("9.ope/00-reconhecimento.md", "Reconhecimento do módulo", "inicio", None),
         ("9.ope/ideal/ope-ideal.md", "O Gerador de OPE ideal", "ideal", "9.ope/ideal/LabMedSys - Modulo OPE - O Ideal.docx"),
         ("9.ope/ideal/ope-entre-modulos.md", "O Gerador de OPE entre os módulos: as travas", "ideal", "9.ope/ideal/LabMedSys - Modulo OPE - Entre os Modulos.docx"),
         ("9.ope/11-inventario-de-telas.md", "Inventário de telas e situação", "inicio", None),
         ("9.ope/01-regras-de-negocio.md", "Regras de negócio", "negocio", None),
         ("9.ope/02-matriz-de-permissoes.md", "Matriz de permissões", "negocio", None),
         ("9.ope/08-plano-de-testes.md", "Plano de testes", "testes", None),
         ("9.ope/04-conformidade-regulatoria.md", "Conformidade com a RDC 658/2022", "qualidade", None),
         ("9.ope/07-analise-de-risco.md", "Análise de risco", "qualidade", None),
         ("9.ope/06-modelo-de-dados.md", "Modelo de dados e integrações", "tecnico", None),
         ("9.ope/fluxos/montagem-do-modelo.md", "Montagem do modelo do registro de lote", "fluxos", "9.ope/fluxos/LabMedSys - Modulo OPE - Fluxo Montagem do Modelo do Registro de Lote.docx"),
     ]},
    {"id": "comercial", "nome": "Comercial", "icone": "◈", "cor": "#0e7490", "situacao": "Pronto para testes", "nivel": 2,
     "resumo": "Venda do produto acabado: cliente, cotação, requisição de produto acabado com o lote escolhido no Estoque, reserva, fatura e remessa. Reconhecimento feito: o Comercial vende o lote disponível no Estoque (aprovado pelo CQ), não o certificado pela Pessoa Delegada; a situação do lote não é conferida de novo na fatura; cancelar a fatura não desfaz a remessa; não há consulta de para quem foi cada lote. Fluxos prontos: cliente e cadastros (a fatura aponta para o endereço do cadastro, sem cópia: alterar ou excluir o endereço muda o destino das vendas antigas); cotação, requisição e reserva (a reserva que falha no Estoque volta como -1, sem aviso); fatura, remessa e cancelamento (o relatório de produtos faturados por lote, que serve ao recolhimento, está fora do menu e ignora faturas canceladas, embora o cancelamento não desfaça a remessa). Análise pelo código concluída: 73 regras, 16 telas, conformidade (9 temas: nenhum atendido, 3 em parte, 6 não atendidos), 17 riscos (10 de prioridade alta) e plano de testes com 52 casos. O ideal: só lote certificado pela Pessoa Delegada é vendido, e a venda guarda o registro de distribuição que a GQ usa no recolhimento.",
     "docs": [
         ("7.comercial/00-reconhecimento.md", "Reconhecimento do módulo", "inicio", None),
         ("7.comercial/ideal/com-ideal.md", "O Comercial ideal", "ideal", "7.comercial/ideal/LabMedSys - Modulo Comercial - O Ideal.docx"),
         ("7.comercial/ideal/com-entre-modulos.md", "O Comercial entre os módulos: as travas", "ideal", "7.comercial/ideal/LabMedSys - Modulo Comercial - Entre os Modulos.docx"),
         ("7.comercial/11-inventario-de-telas.md", "Inventário de telas e situação", "inicio", None),
         ("7.comercial/01-regras-de-negocio.md", "Regras de negócio", "negocio", None),
         ("7.comercial/02-matriz-de-permissoes.md", "Matriz de permissões", "negocio", None),
         ("7.comercial/08-plano-de-testes.md", "Plano de testes", "testes", None),
         ("7.comercial/04-conformidade-regulatoria.md", "Conformidade com a RDC 658/2022", "qualidade", None),
         ("7.comercial/07-analise-de-risco.md", "Análise de risco", "qualidade", None),
         ("7.comercial/06-modelo-de-dados.md", "Modelo de dados e integrações", "tecnico", None),
         ("7.comercial/fluxos/cliente-cadastros.md", "Cliente e cadastros de venda", "fluxos", "7.comercial/fluxos/LabMedSys - Modulo Comercial - Fluxo Cliente e Cadastros de Venda.docx"),
         ("7.comercial/fluxos/cotacao-requisicao-reserva.md", "Cotação, requisição de PA e reserva no Estoque", "fluxos", "7.comercial/fluxos/LabMedSys - Modulo Comercial - Fluxo Cotacao, Requisicao e Reserva.docx"),
         ("7.comercial/fluxos/fatura-remessa-cancelamento.md", "Fatura, remessa e cancelamento", "fluxos", "7.comercial/fluxos/LabMedSys - Modulo Comercial - Fluxo Fatura, Remessa e Cancelamento.docx"),
     ]},
    {"id": "rastreabilidade", "nome": "Rastreabilidade", "icone": "⟲", "cor": "#475569", "situacao": "Pronto para testes", "nivel": 2,
     "resumo": "Gera o IUM (Identificador Único de Medicamento) de cada embalagem de um lote liberado, monta as agregações e registra os eventos para o Sistema Nacional de Controle de Medicamentos (SNCM) da ANVISA. Reconhecimento feito: o envio à ANVISA é simulado no código, e a tela diz que o envio foi feito com sucesso sem ler a resposta; o número de série pode se repetir; a quantidade de IUM não é limitada ao lote. Fluxos prontos: geração de IUM e agregação (a etiqueta traz dados de outra empresa fixados no código, e o código das caixas usa um prefixo de exemplo); eventos e declaração à ANVISA (a ordem dos eventos não é conferida, e nenhum evento se liga à venda nem à situação do lote). Análise pelo código concluída: 42 regras, 15 telas, conformidade (8 temas: nenhum atendido, 3 em parte, 5 não atendidos), 16 riscos (12 de prioridade alta) e plano de testes com 33 casos. O ideal: IUM só para lote certificado pela Pessoa Delegada, e um evento só vale como enviado com o protocolo da ANVISA.",
     "docs": [
         ("8.rastreabilidade/00-reconhecimento.md", "Reconhecimento do módulo", "inicio", None),
         ("8.rastreabilidade/ideal/ras-ideal.md", "A Rastreabilidade ideal", "ideal", "8.rastreabilidade/ideal/LabMedSys - Modulo Rastreabilidade - O Ideal.docx"),
         ("8.rastreabilidade/ideal/ras-entre-modulos.md", "A Rastreabilidade entre os módulos: as travas", "ideal", "8.rastreabilidade/ideal/LabMedSys - Modulo Rastreabilidade - Entre os Modulos.docx"),
         ("8.rastreabilidade/11-inventario-de-telas.md", "Inventário de telas e situação", "inicio", None),
         ("8.rastreabilidade/01-regras-de-negocio.md", "Regras de negócio", "negocio", None),
         ("8.rastreabilidade/02-matriz-de-permissoes.md", "Matriz de permissões", "negocio", None),
         ("8.rastreabilidade/08-plano-de-testes.md", "Plano de testes", "testes", None),
         ("8.rastreabilidade/04-conformidade-regulatoria.md", "Conformidade regulatória (SNCM e RDC 658/2022)", "qualidade", None),
         ("8.rastreabilidade/07-analise-de-risco.md", "Análise de risco", "qualidade", None),
         ("8.rastreabilidade/06-modelo-de-dados.md", "Modelo de dados e integrações", "tecnico", None),
         ("8.rastreabilidade/fluxos/geracao-ium-agregacao.md", "Geração de IUM e agregação", "fluxos", "8.rastreabilidade/fluxos/LabMedSys - Modulo Rastreabilidade - Fluxo Geracao de IUM e Agregacao.docx"),
         ("8.rastreabilidade/fluxos/eventos-declaracao-anvisa.md", "Eventos e declaração à ANVISA", "fluxos", "8.rastreabilidade/fluxos/LabMedSys - Modulo Rastreabilidade - Fluxo Eventos e Declaracao a ANVISA.docx"),
     ]},
]

PUBLICOS = [
    ("Diretoria", "Situação de cada módulo e decisões.", [("visao-geral", "diagnostico-de-conformidade-com-a-anvisa"), ("visao-geral", "mapa-de-integracoes-entre-os-modulos"), ("principal", "resumo-do-modulo"), ("visao-geral", "mapa-do-processo-fabril"), ("estoque", "relatorio-de-testes")]),
    ("Usuários das áreas", "Como cada processo funciona nas telas.", [("principal", "manual-do-usuario"), ("estoque", "manual-do-usuario"), ("garantia-qualidade", "desvios-e-capa")]),
    ("Garantia da Qualidade", "Conformidade, riscos e rastreabilidade.", [("garantia-qualidade", "conformidade-com-a-rdc-658-2022"), ("principal", "conformidade-regulatoria"), ("principal", "dossie-de-homologacao")]),
    ("Desenvolvimento", "Requisitos e dados para a nova versão.", [("principal", "analise-de-requisitos"), ("principal", "modelo-de-dados-e-integracoes"), ("visao-geral", "telas-tabelas-e-codigo-repetidos-entre-os-modulos")]),
]

# ---------------------------------------------------------------------------------------------
# Limpeza de segurança
# ---------------------------------------------------------------------------------------------
RE_TITULO_SEG = re.compile(r"seguran[çc]a|achados? de seguran|ações do perfil.*não valem", re.I)
TITULOS_PERMITIDOS = re.compile(r"usu[áa]rios, perfis e permiss|nivel_seguranca", re.I)
RE_CALLOUT_SEG = re.compile(r"seguran[çc]a|confidencial|verifica[çc][ãa]o de acesso", re.I)
RE_LINHA_SEG = re.compile(
    r"BERTIN, FELIPE SILVA|Os auditores dispon[íi]veis no novo|6 contas \(BERTIN|"
    r"1\.507|s[óo] o id 1|perfil espelho|ESPELHO_ADMIN|nenhum perfil criado pela tela|m[óo]dulo Patrim[ôo]nio|a tela de Perfil n[ãa]o governa|causa est[áa] no perfil 1|C[óo]digo da API nova|c[óo]digo da API|id fixo|perfis 1 e 18|perfil 1|perfil 27|Fato: \*\*s[óo]|"
    r"ADMINISTRADOR \(s[óo] leitura\)|tem 5 a[çc][õo]es marcadas|nem a[çc][ãa]o marcada|Retirar a[çc][õo]es at[ée]|Nenhuma combina[çc][ãa]o liberou|Registrado aqui e no confidencial|"
    r"s[óo] o perfil (?:1|ADMINISTRADOR)|perfil 1 \(ADMINISTRADOR\)|MARCOS_ADM|DV-GQ-N-013|\bProfileId\b|perfil 18|`0\.T\.TESTE_GQ_TUDO`|PEDIDO-AO-DESENVOLVIMENTO|"
    r"servidor exija uma a[çc][ãa]o|lia perfis do Principal|perfil 25 tem|Teste proposto: criar um perfil|ADMINISTRADOR, que funciona|"
    r"hip[óo]tese[^.]*Grupo Perfil|GrupoUsuario|\b403\b|a hip[óo]tese que proponho|O `t\.consulta` nunca foi colocado|"
    r"RG-PRI-03[789]|CT-PRI-050|DV-PRI-02[35]\b|senha de teste fixa|senha provis[óo]ria pendente|Senha provis[óo]ria leva|PERMISS[ÃA]O EXCLU[ÍI]DA|dão as permissões|"
    r"N[íi]vel 3 foi tocado|n[ãa]o deixou nenhum registro|DV-GQ-009|usu[áa]rio de consulta.*gravando|recusa quem n[ãa]o tem acesso ao m[óo]dulo|"
    r"API n[ãa]o confere|Math\.random|gerad[ao]s? no navegador|senha provis[óo]ria (?:aparece|e senha de reset)|DV-PRI-N-01[179]\b|\bN-01[179]\b|"
    r"SEG-[A-Z]{2,4}-\d+|03-achados-de-seguranca|achados de seguran[çc]a|inje[çc][ãa]o de SQL|SQL injection|"
    r"criptografia revers[íi]vel|chave fixa|credenciais|senhas? (?:podem ser |s[ãa]o )?recuper[áa]ve|"
    r"senhas podem ser recuperadas|digitando o endere[çc]o|sem senha em outro navegador|token de acesso|"
    r"token no endere[çc]o|sem entrar no sistema|janela an[ôo]nima|Nenhum filtro obrigat[óo]rio|"
    r"Quem conhece o endere[çc]o|abre(?:m)? telas? .* pelo endere[çc]o|endere[çc]o da p[áa]gina|\btokens?\b|\bhash\b|localStorage|"
    r"a si mesmo o n[íi]vel|se colocar no N[íi]vel 03|perfil completo|Sem login exigido|a[çc][õo]es do perfil ignoradas|HSPermission|"
    r"DV-EST-0(?:08|09|28|35|36)|sem a fun[çc][ãa]o|fun[çc][ãa]o 48|n[úu]meros? fixos? de fun|Qualquer usu[áa]rio (?:do sistema|com login|aprova|autoriza)|sem nenhum acesso ao Estoque|"
    r"apagou as a[çc][õo]es|apaga permiss|salvar a conta|acesso pelo endere[çc]o|abrem? sem permiss[ãa]o|abert[ao]s? pelo endere[çc]o|[Aa]bertas? pelo endere[çc]o|por usu[áa]rio sem permiss[ãa]o|DV-EST-00[57]|"
    r"pelo endere[çc]o[^|]{0,80}(?:sem permiss|sem acesso|acesso negado)|sem permiss[ãa]o[^|]{0,80}pelo endere[çc]o|"
    r"troca obrigat[óo]ria[^|]{0,40}(?:contornada|pulada)|senha sem diferenciar|DV-PRI-02[12]|[Aa]cesso direto pelo endere[çc]o|"
    r"sem nenhuma fun[çc][ãa]o d[oa] [^|]{0,30}abrir|sem acesso [^|]{0,40}pelo endere[çc]o|"
    r"prote[çc][ãa]o [ée] s[óo] visual|servidor aceita|se colocou no N[íi]vel|Qualquer usu[áa]rio se torna|usu[áa]rio de consulta incluiu|"
    r"a[çc][õo]es do perfil \(incluir, alterar\)|abre sem login|autopromo[çc][ãa]o|CT-GQ-11[12]",
    re.I)



DIAGNOSTICO = "transversal/03-diagnostico-conformidade.md"


def bloco_diretoria(origem):
    """Destaque da página inicial: diagnóstico de conformidade, com a contagem tirada do próprio documento."""
    arq = Path(origem) / "homologacao" / DIAGNOSTICO
    if not arq.exists():
        return ""
    texto = arq.read_text(encoding="utf-8")
    m = re.search(r"\*\*Contagem:\*\* Atende (\d+) · Parcial (\d+).*?Não atende (\d+).*?A verificar (\d+)", texto)
    nums = m.groups() if m else ("?", "?", "?", "?")
    rotulos = (("Atendem", "ok"), ("Atendem em parte", "parcial"), ("Não atendem", "nao"), ("A verificar", "verificar"))
    caixas = "".join(f'<div class="diag-num diag-{c}"><strong>{n}</strong><span>{r}</span></div>' for n, (r, c) in zip(nums, rotulos))
    return f"""<section class="secao diretoria" id="diretoria">
    <div class="diretoria-texto">
      <p class="sobretitulo">Para a diretoria</p>
      <h2>Diagnóstico de conformidade com a ANVISA</h2>
      <p>Principal, Estoque e Garantia da Qualidade, como foram entregues pelo fornecedor, comparados com a RDC 658/2022 e o Guia 33/2020: o que atende, o que não atende, as causas e o que corrigir primeiro.</p>
      <div class="hero-acoes">
        <a class="botao" href="documentacao/visao-geral/diagnostico-de-conformidade-com-a-anvisa.html">Ler o diagnóstico →</a>
        <a class="botao botao-secundario" href="documentacao/arquivos/visao-geral/LabMedSys - Diagnostico de Conformidade ANVISA.docx">Baixar em Word</a>
      </div>
    </div>
    <div class="diag-numeros" aria-label="Temas da norma avaliados">{caixas}</div>
  </section>"""


# Nomes de pessoas reais do ambiente de teste: não vão ao portal.
NOMES_REAIS = re.compile(r"\b(?:FELIPE SILVA|BERTIN|Jean Song|JO[ÃA]O MARCOS(?:\.ADM)?(?: VALERIO)?|MARCOS\.ADM|VALERIO)\b", re.I)


SEGURANCA_PUBLICA = True  # decisão do responsável (23/10/2026); --sem-seguranca volta a retirar o conteúdo de segurança


def limpar(md, nome, retirado):
    """Retira o conteúdo de segurança (se SEGURANCA_PUBLICA for falso). Devolve o texto limpo; anota o que saiu em `retirado`.
    Em qualquer caso, nomes reais, logins e IPs são redigidos."""
    linhas = md.splitlines()
    if SEGURANCA_PUBLICA:
        return "\n".join(higiene.redigir(NOMES_REAIS.sub("(profissional do ambiente)", l)) for l in linhas) + "\n"
    saida = []
    pulando_nivel = None   # nível do título da seção que está sendo retirada
    em_callout = False
    for linha in linhas:
        m = re.match(r"^(#{1,6})\s+(.*)", linha)
        if m:
            nivel = len(m.group(1))
            em_callout = False
            if pulando_nivel is not None and nivel <= pulando_nivel:
                pulando_nivel = None
            if pulando_nivel is None and RE_TITULO_SEG.search(m.group(2)) and not TITULOS_PERMITIDOS.search(m.group(2)):
                pulando_nivel = nivel
                retirado.append((nome, f"Seção inteira: {m.group(2)}"))
                continue
        if pulando_nivel is not None:
            continue
        c = re.match(r"^!!!\s*(.*)", linha)
        if c:
            em_callout = bool(RE_CALLOUT_SEG.search(c.group(1)))
            if em_callout:
                retirado.append((nome, f"Bloco: {c.group(1)}"))
                continue
        if em_callout:
            continue
        if RE_LINHA_SEG.search(linha):
            retirado.append((nome, f"Linha: {linha.strip()[:160]}"))
            continue
        saida.append(higiene.redigir(NOMES_REAIS.sub("(profissional do ambiente)", linha)))
    return "\n".join(saida) + "\n"


# ---------------------------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------------------------
def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def ler(p):
    raw = Path(p).read_bytes()
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", "replace")


E = html.escape


def contar(md):
    return {
        "casos": len(set(re.findall(r"\bCT-[A-Z]{2,4}-\d+", md))),
        "regras": len(set(re.findall(r"\bRN-[A-Z]{2,4}-\d+", md))) or len(re.findall(r"^- RN\d{3}", md, re.M)),
        "requisitos": len(set(re.findall(r"\bRN?F-[A-Z]{2,4}-\d+", md))),
        "desvios": len(set(re.findall(r"\bDV-[A-Z]{2,4}-\d+", md))),
    }


# ---------------------------------------------------------------------------------------------
# Conversão Markdown → HTML
# ---------------------------------------------------------------------------------------------
class Conversor:
    def __init__(self, origem, destino):
        self.origem = origem              # .../labmedsys_homol
        self.destino = destino            # .../ilabpharma
        self.modelo_docx = origem / "homologacao/modelos/LabMedSys - Modulo Principal - analise v1.0.docx"

    def imagem(self, caminho, modulo):
        """Copia a imagem para o site e devolve o caminho a partir da página do documento."""
        pasta = self.destino / "documentacao/img" / modulo
        pasta.mkdir(parents=True, exist_ok=True)
        if caminho.startswith("modelo:"):
            nome = caminho.split(":", 1)[1]
            with zipfile.ZipFile(self.modelo_docx) as z:
                dados = z.read(f"word/media/{nome}")
            alvo = pasta / f"modelo-{nome}"
            alvo.write_bytes(dados)
            return f"../img/{modulo}/modelo-{nome}"
        fonte = self.origem / caminho
        if not fonte.exists():
            return None
        nome = slug(fonte.stem) + fonte.suffix.lower()
        shutil.copy2(fonte, pasta / nome)
        return f"../img/{modulo}/{nome}"

    def converter(self, md, modulo, tirar_h1):
        linhas = md.splitlines()
        if tirar_h1 and linhas and linhas[0].startswith("# ") and not re.match(r"# (Introdução|Objetivo|Resumo|Conclusão)\b", linhas[0]):
            linhas = linhas[1:]
        # Callouts "!!! Rótulo": o bloco vai até o próximo título ou o próximo "!!!".
        saida, aberto = [], False
        for l in linhas:
            m = re.match(r"^!!!\s*(.*)", l)
            if m or (aberto and l.startswith("#")):
                if aberto:
                    saida += ["", "</div>", ""]
                    aberto = False
            if m:
                saida += ["", f'<div class="callout" markdown="1">', "", f'<p class="callout-titulo">{E(m.group(1))}</p>', ""]
                aberto = True
                continue
            # Títulos descem um nível: o título da página é o h1.
            t = re.match(r"^(#{1,5})\s", l)
            if t:
                l = "#" + l
            saida.append(l)
        if aberto:
            saida += ["", "</div>"]
        texto = "\n".join(saida)

        # Imagens
        def troca_img(m):
            alt, cam = m.group(1), m.group(2)
            novo = self.imagem(cam, modulo)
            if not novo:
                return f"*(imagem não publicada: {E(alt)})*"
            return f'<figure><a href="{novo}" target="_blank" rel="noopener"><img src="{novo}" alt="{E(alt)}" loading="lazy"></a><figcaption>{E(alt)} · clique para ampliar</figcaption></figure>'
        texto = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", troca_img, texto)
        # Links para outros .md viram texto (os documentos publicados têm outro endereço)
        texto = re.sub(r"\[([^\]]+)\]\((?!https?:)[^)]+\.md(?:#[^)]*)?\)", r"\1", texto)

        conv = markdown.Markdown(extensions=["tables", "toc", "sane_lists", "md_in_html", "attr_list"],
                                 extension_configs={"toc": {"slugify": lambda v, s: slug(v), "toc_depth": "2-3"}})
        corpo = conv.convert(texto)
        corpo = corpo.replace("<table>", '<div class="tabela"><table>').replace("</table>", "</table></div>")
        return corpo, conv.toc_tokens


# ---------------------------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------------------------
CSS_VERSAO = hashlib.md5((Path(__file__).resolve().parent.parent / "portal/portal.css").read_bytes()).hexdigest()[:8]


def cabecalho(titulo, raiz, ativo=""):
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{E(titulo)}</title>
<meta name="description" content="iLabMedSys: documentação da homologação do LabMedSys, por módulo.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{raiz}portal/portal.css?v={CSS_VERSAO}">
<script>try{{var t=localStorage.getItem('ilms-tema');if(t)document.documentElement.dataset.theme=t;}}catch(e){{}}</script>
</head>
<body data-raiz="{raiz}">
<header class="topo">
  <a class="marca" href="{raiz}index.html" aria-label="iLabMedSys, página inicial"><img src="{raiz}assets/ilabmedsys-logo.svg" alt="iLabMedSys"></a>
  <nav class="topo-nav" aria-label="Principal">
    <a href="{raiz}index.html#modulos"{' aria-current="page"' if ativo == 'modulos' else ''}>Módulos</a>
    <a href="{raiz}biblioteca.html"{' aria-current="page"' if ativo == 'biblioteca' else ''}>Biblioteca</a>
    <a href="{raiz}telas.html"{' aria-current="page"' if ativo == 'telas' else ''}>Devs/QA</a>
    <a href="{raiz}index.html#publicos">Por público</a>
    <a href="{raiz}anvisa.html"{' aria-current="page"' if ativo == 'anvisa' else ''}>ANVISA</a>
    <a href="{raiz}cronograma.html"{' aria-current="page"' if ativo == 'cronograma' else ''}>Cronograma</a>
    <a href="{raiz}apresentacao.html">Apresentação</a>
  </nav>
  <div class="topo-acoes">
    <label class="busca"><span aria-hidden="true">⌕</span><input id="busca" type="search" placeholder="Buscar documento, regra, tela…" aria-label="Buscar na documentação" autocomplete="off"></label>
    <button class="tema" id="tema" type="button" aria-label="Alternar tema claro e escuro">☾</button>
  </div>
  <div class="busca-resultados" id="busca-resultados" role="listbox" hidden></div>
</header>
"""


def rodape(raiz):
    return f"""<footer class="rodape">
  <div><strong>iLabMedSys</strong> · documentação da homologação do LabMedSys · atualizado em {HOJE}</div>
  <div>Os documentos descrevem o sistema legado entregue pelo fornecedor, com todos os defeitos encontrados, inclusive os de acesso e segurança. Senhas, logins e endereços de servidor não são publicados.</div>
</footer>
<script src="{raiz}portal/portal.js"></script>
</body></html>
"""


def selo(situacao):
    classe = {"Homologado: não apto": "selo-alerta", "Fluxos prontos, testes pausados": "selo-andamento",
              "Em análise": "selo-andamento", "Fluxos prontos": "selo-andamento", "Em andamento": "selo-andamento"}.get(situacao, "selo-neutro")
    return f'<span class="selo {classe}">{E(situacao)}</span>'


def barra(nivel):
    etapas = ["Reconhecimento", "Fluxos", "Testes", "Entregáveis"]
    itens = "".join(f'<li class="{"feito" if i < nivel else ""}">{e}</li>' for i, e in enumerate(etapas))
    return f'<ol class="etapas" aria-label="Andamento: {nivel} de 4 etapas">{itens}</ol>'



# ---------------------------------------------------------------------------------------------
# Índice das normas (portal/normas.json): o texto de todo artigo da RDC 658/2022, de toda seção do
# Guia 33/2020 e de cada trava do modelo ideal. O portal.js transforma cada referência ("art. 157",
# "Guia 33, 9.3.2.3", número na coluna "Trava") num link que abre o texto numa janela.
# ---------------------------------------------------------------------------------------------
def _itens_guia(paragrafos):
    itens = []
    for p in paragrafos:
        p = re.sub(r"\s*Guia nº 33/2020 – versão 1, de 26/03/2020\s*", " ", p).strip()
        if not p:
            continue
        for parte in re.split(r"\s*•\s*", p):
            if not parte.strip():
                continue
            continua = parte.lstrip().startswith("✓")
            pedacos = [x.strip() for x in re.split(r"\s*✓\s*", parte)]
            cab, subs = pedacos[0], [x for x in pedacos[1:] if x]
            if continua and itens:
                itens[-1]["subs"] += subs
            else:
                itens.append({"cab": cab, "subs": subs})
    return itens


def indice_normas(origem):
    """Monta o índice; devolve None (com aviso) se os PDFs ou o extrator não estiverem disponíveis."""
    import glob as _glob
    ferr = origem / "homologacao/ferramentas"
    try:
        sys.path.insert(0, str(ferr))
        from extrair_normas import artigos_rdc, secoes_guia  # noqa: E402
        rdc_pdf = origem / "Documentação/Anvisa/RESOLUÇÃO RDC Nº 658 de 2020.pdf"
        guia_pdf = Path(_glob.glob(str(origem / "Documentação/Guia-n*33*.pdf"))[0])
        rdc = {str(n): pars for n, pars in artigos_rdc(rdc_pdf).items()}
        guia = {sec: {"titulo": (t.strip().capitalize() if t.isupper() else t.strip()), "itens": _itens_guia(pars)}
                for sec, (t, pars) in secoes_guia(guia_pdf).items()}
    except Exception as e:  # noqa: BLE001
        print(f"Aviso: índice das normas não gerado ({e})", file=sys.stderr)
        return None
    travas = {}
    doc = origem / "homologacao/modelo-ideal/01-qualidade-entre-modulos.md"
    if doc.exists():
        t = ler(doc)
        titulos = dict(re.findall(r"^\| (\d+) \| ([^|]+?) \| \[", t, re.M))
        ap = t.split("<!-- NORMAS:INICIO -->", 1)[-1].split("<!-- NORMAS:FIM -->", 1)[0]
        for n, corpo in re.findall(r"^## Tema (\d+) · [^\n]*\n(.*?)(?=^## Tema \d+ · |\Z)", ap, re.M | re.S):
            travas[n] = {"titulo": titulos.get(n, "").strip(),
                         "html": markdown.markdown(corpo.strip(), extensions=["sane_lists"])}
    return {"rdc": rdc, "guia": guia, "travas": travas}

def gerar(origem, destino, relatorio, atualizar_metadados=False):
    conv = Conversor(origem, destino)
    n_logins = higiene.carregar(origem)
    print(f"Higiene: {n_logins} logins de teste lidos da fonte privada para redação.")
    if not n_logins:
        print("AVISO: a fonte dos logins de teste não foi encontrada; o login não pode ser redigido nem verificado.", file=sys.stderr)
    hom = origem / "homologacao"
    doc_dir = destino / "documentacao"
    if doc_dir.exists():
        shutil.rmtree(doc_dir)
    (doc_dir / "arquivos").mkdir(parents=True)
    retirado = []
    busca = []
    gerar_docx = hom / "ferramentas/gerar_docx.py"

    for mod in MODULOS:
        mod["paginas"] = []
        mod["docs"] = docs_com_telas(mod, hom)
        for ordem, item in enumerate(mod["docs"]):
            arq, titulo, cat, word = item[:4]
            extra = item[4] if len(item) > 4 else {}
            fonte = hom / arq
            original = ler(fonte)
            antes = len(retirado)
            limpo = limpar(original, arq, retirado)
            foi_limpo = len(retirado) > antes
            corpo, toc = conv.converter(limpo, mod["id"], tirar_h1=True)
            s = slug(titulo)
            pagina = {"titulo": titulo, "slug": s, "cat": cat, "arq": arq, "toc": toc, "corpo": corpo,
                      "contagem": contar(limpo), "word": None, "fluxograma": None, "limpo": foi_limpo,
                      "roteiro_de": ROTEIROS.get(arq) or extra.get("roteiro_de"), "ordem": ordem,
                      "grupo": extra.get("grupo"), "tela": extra.get("tela"), "rotulo": extra.get("rotulo"), "desvios": extra.get("desvios"), "menu": extra.get("menu"), "aba": extra.get("aba"), "resumo_tela": extra.get("resumo"), "tela_n": extra.get("tela_n"), "intro": extra.get("intro"),
                      "situacao_tela": extra.get("situacao")}
            m = re.search(r'<img src="(\.\./img/[^"]+fluxograma[^"]*)"', corpo)
            if m:
                pagina["fluxograma"] = m.group(1)
            # Word
            if word and ((hom / word).exists() or arq.endswith("defeitos-completo.md")):
                pasta = doc_dir / "arquivos" / mod["id"]
                pasta.mkdir(parents=True, exist_ok=True)
                nome = Path(word).name
                alvo = pasta / nome
                if foi_limpo or arq.endswith("defeitos-completo.md"):
                    tmp = destino / f".tmp-{s}.md"
                    tmp.write_text(limpo, encoding="utf-8")
                    titulo_doc = f"Fluxo – {titulo}" if cat == "fluxos" else titulo
                    r = subprocess.run([sys.executable, str(gerar_docx), "--modelo", str(conv.modelo_docx), "--fonte", str(tmp),
                                        "--saida", str(alvo), "--titulo", titulo_doc, "--data", HOJE,
                                        "--descricao", "Versão publicada no portal" + ("" if SEGURANCA_PUBLICA else ", sem os achados de segurança"),
                                        "--modulo", f"Módulo {mod['nome']}"], capture_output=True, text=True)
                    tmp.unlink()
                    if r.returncode != 0:
                        print(r.stderr, file=sys.stderr)
                        raise SystemExit(f"Falha ao gerar o Word de {arq}")
                else:
                    higiene.copiar_word(hom / word, alvo)
                pagina["word"] = f"../arquivos/{mod['id']}/{nome}"
            mod["paginas"].append(pagina)
            texto = re.sub(r"<[^>]+>", " ", corpo)
            texto = re.sub(r"\s+", " ", html.unescape(texto))
            titulos = [t["name"] for t in toc] + [c["name"] for t in toc for c in t["children"]]
            busca.append({"t": titulo, "m": mod["nome"], "u": f"documentacao/{mod['id']}/{s}.html",
                          "h": titulos[:40], "x": texto[:6000]})

    for mod in MODULOS:
        organizar_roteiro(mod)
    hom_ = Path(origem) / "homologacao"
    SITUACAO_TELAS.update(telas_devs.situacoes(hom_))
    if (hom_ / "painel.json").exists() and (hom_ / "cronograma.json").exists():
        DADOS_PAINEL["pn"] = json.loads(higiene.redigir((hom_ / "painel.json").read_text(encoding="utf-8")))
        DADOS_PAINEL["cr"] = {m["id"]: m for m in json.loads(higiene.redigir((hom_ / "cronograma.json").read_text(encoding="utf-8")))["modulos"]}

    # Páginas de documento
    for mod in MODULOS:
        if not mod["paginas"]:
            continue
        pasta = doc_dir / mod["id"]
        pasta.mkdir(parents=True, exist_ok=True)
        for p in mod["paginas"]:
            (pasta / f"{p['slug']}.html").write_text(pagina_documento(mod, p), encoding="utf-8")
        # Endereços antigos das telas do Controle de Desvios (uma página por tela): levam à página de análise da tela
        for p in mod["paginas"]:
            if p.get("tela_n") and p.get("aba") == "analise" and p.get("grupo") == "Controle de Desvios":
                antigo = slug(f"Tela {p['tela_n']} · {p['tela']}")
                if antigo != p["slug"]:
                    (pasta / f"{antigo}.html").write_text(
                        f'<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><title>{E(p["tela"])} · iLabMedSys</title>'
                        f'<meta http-equiv="refresh" content="0; url={p["slug"]}.html"><link rel="canonical" href="{p["slug"]}.html"></head>'
                        f'<body><p>Esta página mudou: <a href="{p["slug"]}.html">{E(p["tela"])}: análise</a>.</p></body></html>', encoding="utf-8")
        for sit in ("index", "legado", "novo", "ideal"):
            (pasta / f"{sit}.html").write_text(pagina_modulo(mod, sit), encoding="utf-8")

    (destino / "index.html").write_text(pagina_inicial(origem), encoding="utf-8")
    (destino / "anvisa.html").write_text(pagina_anvisa(origem, busca), encoding="utf-8")
    # Biblioteca: metadados com fonte única em homologacao/biblioteca-metadados.csv
    nomes = {m["id"]: m["nome"] for m in MODULOS}
    entradas = biblioteca.montar_entradas(MODULOS, origem, nomes)
    entradas, rel_bib = biblioteca.aplicar_e_relatar(entradas, hom_ / "biblioteca-metadados.csv", atualizar_metadados)
    (destino / "biblioteca.html").write_text(
        biblioteca.pagina_biblioteca(entradas, ["principal", "estoque", "producao", "ope", "controle-qualidade", "garantia-qualidade", "controle-documentos", "comercial", "rastreabilidade", "entre-módulos"],
                                     cabecalho, rodape, E), encoding="utf-8")
    print(f"Biblioteca: {rel_bib['total']} documentos; {rel_bib['do_arquivo']} com linha no arquivo de metadados, {rel_bib['sem_linha']} sem linha "
          f"({rel_bib['acrescentadas']} acrescentadas agora); {rel_bib['a_classificar']} com valor a classificar; {rel_bib['revisadas']} revisadas."
)
    if rel_bib["linhas_sobrando"]:
        print(f"AVISO: {len(rel_bib['linhas_sobrando'])} linha(s) do arquivo de metadados sem documento no portal (removido ou renomeado). Nada foi apagado; confira e remova à mão se for o caso:")
        for c in rel_bib["linhas_sobrando"]:
            print(f"  - {c}")
    # Devs/QA: as telas por módulo e menu, com os cinco documentos de cada tela
    dados_telas = telas_devs.montar(MODULOS, origem, destino)
    (destino / "telas.html").write_text(telas_devs.pagina(dados_telas, cabecalho, rodape), encoding="utf-8")
    (destino / "portal/telas.css").write_text(telas_devs.CSS, encoding="utf-8")
    print(f"Devs/QA: {sum(len(ts) for m in dados_telas for _, ts in m['menus'])} telas em {sum(1 for m in dados_telas if m['menus'])} módulos com inventário.")
    cron = pagina_cronograma(origem)
    if cron:
        (destino / "cronograma.html").write_text(cron, encoding="utf-8")
    (destino / "portal/busca.json").write_text(json.dumps(busca, ensure_ascii=False), encoding="utf-8")
    normas = indice_normas(origem)
    if normas:
        (destino / "portal/normas.json").write_text(json.dumps(normas, ensure_ascii=False), encoding="utf-8")
        print(f"Índice das normas: {len(normas['rdc'])} artigos da RDC, {len(normas['guia'])} seções do Guia, {len(normas['travas'])} travas")

    if relatorio:
        linhas = ["# Conteúdo retirado do portal (segurança)", "", f"Gerado em {HOJE}. **Este relatório não é publicado.**", ""]
        atual = None
        for arq, o_que in retirado:
            if arq != atual:
                linhas += ["", f"## {arq}", ""]
                atual = arq
            linhas.append(f"- {o_que}")
        Path(relatorio).write_text("\n".join(linhas) + "\n", encoding="utf-8")
    total = sum(len(m["paginas"]) for m in MODULOS)
    print(f"Portal gerado: {total} documentos, {len(retirado)} trechos de segurança retirados.")
    achados = higiene.verificar(destino)
    if achados:
        for arq, o_que, n in achados:
            print(f"BLOQUEADO: {arq}: {o_que} (x{n})", file=sys.stderr)
        raise SystemExit(f"Higiene: {len(achados)} problema(s) no portal gerado. Nada deve ser publicado.")
    print("Higiene: nenhum endereço privado, login de teste ou pasta proibida no portal gerado.")


def _nav_arvore(pags, roteiros, atual):
    """Menu em árvore (menu do sistema > tela > resumo e passo a passo), com os grupos que abrem e fecham."""
    html = ""
    gerais = [x for x in pags if not x.get("grupo") and not x.get("roteiro_de")]
    if gerais:
        itens = "".join(f'<li><a href="{p["slug"]}.html"{" aria-current=page" if p is atual else ""}>{E(p["titulo"])}</a></li>' for p in gerais)
        html += f'<li><details class="lat-menu-d"{" open" if atual in gerais else ""}><summary>Informações gerais</summary><ul>{itens}</ul></details></li>'
    for g in dict.fromkeys(x["grupo"] for x in pags if x.get("grupo")):
        telas, g_aberto = "", False
        pags_g = [x for x in pags if x.get("grupo") == g and not x.get("roteiro_de")]
        for nome_tela in dict.fromkeys(x["tela"] for x in pags_g):
            paginas = [x for x in pags_g if x["tela"] == nome_tela]
            rots = [roteiros[x["arq"]] for x in paginas if roteiros.get(x["arq"])]
            t_aberto = any(atual is x for x in paginas) or any(atual is r for r in rots)
            g_aberto = g_aberto or t_aberto
            filhos = "".join(f'<li><a href="{x["slug"]}.html"{" aria-current=page" if x is atual else ""}>{E(x.get("rotulo") or "Resumo geral")}</a></li>' for x in paginas)
            filhos += "".join(f'<li><a href="{r["slug"]}.html"{" aria-current=page" if r is atual else ""}>Passo a passo de homologação</a></li>' for r in rots)
            telas += (f'<li><details class="lat-tela"{" open" if t_aberto else ""}><summary>{E(nome_tela)}</summary><ul>{filhos}</ul></details></li>')
        html += f'<li><details class="lat-menu-d"{" open" if g_aberto else ""}><summary>{E(g)}</summary><ul>{telas}</ul></details></li>'
    return html


def nav_lateral(mod, atual):
    grupos = []
    secao_atual = None
    for i, (chave, nome, _desc, pags) in enumerate(mod["roteiro"], 1):
        roteiros = {p["roteiro_de"]: p for p in pags if p.get("roteiro_de")}
        li = ""
        if any(p.get("grupo") for p in pags):
            li = _nav_arvore(pags, roteiros, atual)
        else:
            for p in pags:
                if p.get("roteiro_de"):
                    continue
                li += f'<li><a href="{p["slug"]}.html"{" aria-current=page" if p is atual else ""}>{E(p["titulo"])}</a>'
                r = roteiros.get(p["arq"])
                if r is not None and r is atual:  # o passo a passo agora é um botão na página de cada tela; no menu só aparece quando está aberto
                    li += f'<ul class="lat-sub"><li><a href="{r["slug"]}.html" aria-current=page>Passo a passo para testar</a></li></ul>'
                li += "</li>"
        aberto = " lat-atual" if atual and atual.get("passo_nome") == nome else ""
        sk, sn, _sd = _secao_de(chave)
        if sk != secao_atual and chave != "visao":
            secao_atual = sk
            grupos.append(f'<div class="lat-secao">{E(sn)}</div>')
        if chave in ("novo", "resumo"):
            grupos.append(f'<div class="lat-grupo{aberto}"><ul>{li}</ul></div>')
        else:
            grupos.append(f'<div class="lat-grupo{aberto}"><div class="lat-titulo">{E(nome)}</div><ul>{li}</ul></div>')
    return "".join(grupos)


def toc_html(toc):
    if not toc:
        return ""
    itens = []
    for t in toc:
        filhos = "".join(f'<li class="sub"><a href="#{c["id"]}">{E(html.unescape(c["name"]))}</a></li>' for c in t["children"][:12])
        itens.append(f'<li><a href="#{t["id"]}">{E(html.unescape(t["name"]))}</a></li>{filhos}')
    return f'<nav class="toc" aria-label="Nesta página"><div class="toc-titulo">Nesta página</div><ul>{"".join(itens)}</ul></nav>'


def _cartao_ap(rotulo, titulo, href, lado):
    return f'<a class="ap ap-{lado}" href="{href}"><small>{E(rotulo)}</small><strong>{E(titulo)}</strong></a>'


# Menu do sistema (grupo das páginas por tela) -> roteiro de execução (passo a passo para testar)
GRUPO_ROTEIRO = {
    "Controle de Desvios": "5.garantia_qualidade/roteiros/desvios-capa.md",
    "Controle de Mudanças": "5.garantia_qualidade/roteiros/controle-mudancas.md",
    "Assuntos Regulatórios": "5.garantia_qualidade/roteiros/assuntos-regulatorios.md",
    "Autoinspeção e Auditoria": "5.garantia_qualidade/roteiros/autoinspecao-auditoria.md",
}


def _abas_extras(mod, p):
    """Dois botões ao lado das abas da tela: 'Passo a passo' (roteiro de execução, na seção desta tela) e 'Ideal' (ficha e layout
    da tela a criar). Onde a página ainda não existe, o botão aparece apagado."""
    nome = telas_devs._norm(re.sub(r"\s*\(.*?\)", "", p.get("tela") or ""))
    # Passo a passo
    href = None
    arq_roteiro = GRUPO_ROTEIRO.get(p.get("grupo"))
    rot = next((x for x in mod["paginas"] if x.get("arq") == arq_roteiro), None) if arq_roteiro else None
    if rot:
        href = f'{rot["slug"]}.html'
        melhor = None
        for tn, ancora in telas_do_roteiro(rot):
            n = telas_devs._norm(tn)
            if n == nome or (n and nome and (n in nome or nome in n)):
                melhor = ancora
                if n == nome:
                    break
        if melhor:
            href += f"#{melhor}"
    # Ideal
    ideal = next((x for x in mod["paginas"] if x.get("cat") == "novo" and x.get("grupo") == p.get("grupo")
                  and telas_devs._norm(re.sub(r"\s*\(.*?\)", "", x.get("tela") or "")) == nome), None)
    def botao(rotulo, destino, dica):
        if destino:
            return f'<a class="aba-extra" href="{destino}">{rotulo}</a>'
        return f'<span class="aba-extra aba-apagada" aria-disabled="true" title="{dica}">{rotulo}</span>'
    return ('<span class="aba-sep" aria-hidden="true"></span>'
            + botao("Passo a passo", href, "O roteiro de execução desta tela ainda não foi escrito")
            + botao("Ideal", f'{ideal["slug"]}.html' if ideal else None, "A ficha da tela ideal ainda não foi escrita"))


def pagina_documento(mod, p):
    raiz = "../../"
    word = f'<a class="botao" href="{p["word"]}" download>⤓ Baixar em Word</a>' if p["word"] else ""
    aviso = '<p class="nota">Versão publicada sem os trechos de segurança, que têm distribuição restrita.</p>' if p["limpo"] else ""
    ant_mod, prox_mod = vizinhos(mod)
    if p["ant"]:
        ant = _cartao_ap("← Anterior", p["ant"]["titulo"], f'{p["ant"]["slug"]}.html', "ant")
    elif ant_mod:
        ant = _cartao_ap("← Módulo anterior", ant_mod["nome"], f'../{ant_mod["id"]}/index.html', "ant")
    else:
        ant = _cartao_ap("← Início do roteiro", mod["nome"], "index.html", "ant")
    if p["prox"]:
        prox = _cartao_ap("Próximo →", p["prox"]["titulo"], f'{p["prox"]["slug"]}.html', "prox")
    elif prox_mod:
        prox = _cartao_ap("Fim do módulo · próximo módulo →", prox_mod["nome"], f'../{prox_mod["id"]}/index.html', "prox")
    else:
        prox = _cartao_ap("Fim do roteiro", "Voltar ao início do portal", f"{raiz}index.html", "prox")
    abas = ""
    if p.get("tela_n") and p.get("aba"):
        irmas = sorted([x for x in mod["paginas"] if x.get("tela_n") == p["tela_n"] and x.get("grupo") == p.get("grupo") and x.get("aba")], key=lambda x: ABAS_DESVIOS.index(x["aba"]))
        extras = _abas_extras(mod, p)
        abas = ('<nav class="abas-tela" aria-label="Páginas desta tela">'
                + "".join(f'<a href="{x["slug"]}.html"{" aria-current=page" if x is p else ""}>{E(x["rotulo"])}</a>' for x in irmas) + extras + '</nav>')
        _s = SITUACAO_TELAS.get((mod["id"], telas_devs._norm(re.sub(r"\s*\(.*?\)", "", p.get("tela") or ""))))
        if _s and p.get("desvios"):
            abas += telas_devs.selo_situacao(_s)
    pct = round(p["n"] / p["total"] * 100)
    unico = p["passo_total"] == 1
    sec = p.get("secao_nome") or ""
    onde = (E(p["passo_nome"]) if unico or not sec or sec == "Visão de ponta a ponta"
            else (E(sec) if sec == p["passo_nome"] else f'{E(sec)} · {E(p["passo_nome"])}'))
    _sit = p.get("sit")
    _info = next((x for x in SITUACOES_MOD if x[0] == _sit), None)
    onde_curto = E(p["passo_nome"]) if _info and not unico else onde
    trilha_sit = (f' › <a class="sit-trilha" href="{_sit}.html" style="--cor:{_info[3]}">{E(_info[1])}</a>' if _info else "")
    return (cabecalho(f"{p['titulo']} · {mod['nome']} · iLabMedSys", raiz) + f"""
<div class="doc-layout">
  <aside class="lateral" aria-label="Roteiro do módulo">
    <a class="lat-modulo" href="index.html" style="--cor:{mod['cor']}"><span class="icone">{mod['icone']}</span>{E(mod['nome'])}</a>
    {nav_lateral(mod, p)}
  </aside>
  <main class="doc" id="conteudo">
    <nav class="trilha" aria-label="Você está em"><a href="{raiz}index.html">Início</a> › <a href="index.html">{E(mod['nome'])}</a>{trilha_sit} › <span>{onde_curto}</span></nav>
    <div class="onde-estou" aria-label="Onde você está no roteiro"><span>{onde}</span><span>documento {p["n"]} de {p["total"]}</span><div class="prog-doc"><i style="width:{pct}%"></i></div></div>
    <header class="doc-cabecalho">
      <h1>{E(p['titulo'])}</h1>
      <div class="doc-acoes">{word}<button class="botao botao-secundario" type="button" onclick="window.print()">⎙ Imprimir</button></div>
      {aviso}
    </header>
    {abas}
    <article class="texto{' texto-largo' if p.get('aba') else ''}">
{p['corpo']}
    </article>
    <nav class="anterior-proximo" aria-label="Anterior e próximo">{ant}{prox}</nav>
  </main>
  {toc_html(p['toc'])}
</div>
""" + rodape(raiz))


SITUACOES_MOD = [
    ("legado", "Legado", "o sistema entregue pelo fornecedor", "#6b7a8c"),
    ("novo", "Novo", "a versão nova, em teste", "#1f6feb"),
    ("ideal", "Ideal", "como deve funcionar para cumprir a ANVISA", "#7b3fe4"),
]
DADOS_PAINEL = {"pn": {}, "cr": {}}


def estado_situacoes(mod):
    """Veredito e descrição de cada situação do módulo, com base no cronograma.json e no painel.json."""
    pn, cr = DADOS_PAINEL["pn"], DADOS_PAINEL["cr"]
    c = cr.get(mod["id"], {})
    t = c.get("testes") or {}
    sit = c.get("situacao", "")
    if sit.startswith("Fechado"):
        leg = ("nao", "Não apto")
    elif sit.startswith("Em testes"):
        leg = ("parcial", "Em testes")
    else:
        leg = ("vazio", "Só análise de código")
    nv = pn.get("modulos_novo", {}).get(mod["id"])
    nov = (nv[0], nv[1]) if nv else ("vazio", "Não iniciado")
    ideal_ok = sit.startswith("Fechado") and any(p["cat"] == "ideal" for p in mod["paginas"])
    ide = ("ideal", "Definido (testes concluídos)") if ideal_ok else ("vazio", "Rascunho: aguarda os testes")
    desc_nov = pn.get("descricao_novo", {}).get(mod["id"]) or "Ainda não testado na versão nova. Quando os testes começarem, os resultados aparecem aqui."
    desc_ide = ("Como o módulo deve funcionar para atender à ANVISA, a partir dos testes de código e de tela já concluídos." if ideal_ok
                else "Rascunho. O ideal só é dado como definido depois do fim dos testes do módulo.")
    num_nov = [tuple(x) for x in pn.get("numeros_novo", {}).get(mod["id"], [])]
    return {
        "legado": {"chip": leg, "desc": mod["resumo"], "casos": (t.get("conclusivos", 0), t.get("planejados", 0))},
        "novo": {"chip": nov, "desc": desc_nov, "numeros": num_nov},
        "ideal": {"chip": ide, "desc": desc_ide},
    }


def troca_situacao(atual, mod):
    """Barra que deixa claro em qual situação (Legado, Novo ou Ideal) o leitor está e leva às outras."""
    itens = [("index", "← Página do módulo", "#334155")] + [(k, n, c) for k, n, _d, c in SITUACOES_MOD]
    return ('<nav class="sit-troca" aria-label="Situação do módulo">'
            + "".join(f'<a href="{k}.html" style="--cor:{c}"{" aria-current=page" if k == atual else ""}>{E(n)}</a>' for k, n, c in itens) + '</nav>')


def intro_modulo(mod):
    """Primeira frase do resumo: o que o módulo é, valendo para as três situações."""
    t = mod["resumo"].strip()
    m = re.match(r"(.+?[.!?])(\s|$)", t)
    return m.group(1) if m else t


MENUS_GQ_DESC = {
    "Controle de Desvios": "Onde a Garantia da Qualidade registra o que saiu do combinado na fábrica, investiga a causa, corrige e confere. É o processo que a ANVISA mais olha numa inspeção.",
    "Assuntos Regulatórios": "Onde a empresa acompanha os processos regulatórios dos seus produtos junto à ANVISA: o que foi pedido, o que está programado e o que está em andamento.",
    "Controle de Mudanças": "Onde a empresa pede, avalia, aprova, executa e confere qualquer mudança que possa afetar a qualidade do medicamento: processo, equipamento, material, documento, sistema.",
    "Autoinspeção e Auditoria": "Onde a empresa confere, por conta própria, se cumpre as Boas Práticas: escreve os roteiros de perguntas, programa a verificação, registra o que encontrou e avalia o resultado.",
}
SITUACAO_TELAS = {}  # preenchido em main() a partir dos inventários de telas
ABAS_DESVIOS = ["analise", "manual", "fluxos", "regras", "anvisa"]


def _menu_de(p):
    return p.get("grupo") or p.get("menu") or "Controle de Desvios"


def _cartoes_um_menu(pags):
    apoio = [p for p in pags if p.get("intro")]
    h = '<div class="doc-cards">' + "".join(
        f'<a class="doc-card" href="{p["slug"]}.html"><span class="doc-card-titulo">{E(p["titulo"])}</span><span class="doc-card-meta">Comece por aqui</span></a>' for p in apoio) + "</div>"
    cart = ""
    for n in sorted({p["tela_n"] for p in pags if p.get("tela_n")}):
        irmas = sorted([p for p in pags if p.get("tela_n") == n], key=lambda x: ABAS_DESVIOS.index(x["aba"]))
        pa = irmas[0]
        links = " · ".join(f'<a href="{x["slug"]}.html">{E(x["rotulo"])}</a>' for x in irmas)
        cart += (f'<div class="doc-card tela-card"><a class="doc-card-titulo" href="{pa["slug"]}.html"><span class="doc-n">{n}</span>{E(pa["tela"])}</a>'
                 f'<span class="doc-card-meta">{E(pa.get("resumo_tela") or "")}</span><span class="tela-links">{links}</span></div>')
    return h + f'<div class="doc-cards">{cart}</div>'


def cartoes_desvios(pags):
    """Cartões dos menus tela a tela (Controle de Desvios e Controle de Mudanças): as páginas de apoio e uma por tela, com o que cada tela faz e as cinco páginas dela.
    Com mais de um menu, cada um ganha o seu título."""
    menus = list(dict.fromkeys(_menu_de(p) for p in pags))
    if len(menus) <= 1:
        return _cartoes_um_menu(pags)
    return "".join(f'<h3 class="novo-menu">{E(m)}</h3>' + _cartoes_um_menu([p for p in pags if _menu_de(p) == m]) for m in menus)



def pagina_modulo(mod, sit="index"):
    """Visão geral do módulo (sit='index') ou uma das três situações: 'legado', 'novo', 'ideal'."""
    raiz = "../../"
    estados = estado_situacoes(mod)
    ant_mod, prox_mod = vizinhos(mod)
    fim = (f'<section class="fim-roteiro"><p class="comece-rotulo">Fim do roteiro deste módulo</p>'
           + (f'<p>Segue o caminho do processo: <a class="botao" href="../{prox_mod["id"]}/index.html">Próximo módulo: {E(prox_mod["nome"])} →</a></p>' if prox_mod
              else '<p>Este é o último módulo do caminho. <a class="botao" href="../../index.html">Voltar ao início do portal</a></p>')
           + (f'<p class="fim-ant">Antes deste: <a href="../{ant_mod["id"]}/index.html">{E(ant_mod["nome"])}</a></p>' if ant_mod else "") + '</section>')

    if sit == "index":
        resumo = [g for g in mod["roteiro"] if _secao_de(g[0])[0] == "modulo"]
        cartoes = []
        for k, nome, curta, cor in SITUACOES_MOD:
            est = estados[k]
            cl, rot = est["chip"]
            pags = [p for g in mod["roteiro"] if _secao_de(g[0])[0] == k for p in g[3]]
            if k == "legado":
                nums = [(len(pags), "documentos"), (f'{est["casos"][0]}/{est["casos"][1]}', "casos de teste")]
            elif k == "novo":
                nums = [(len(pags), "documentos")] + est["numeros"][:2]
            else:
                req = max([p["contagem"]["requisitos"] for p in pags] + [0])
                nums = [(len(pags), "documentos")] + ([(req, "requisitos")] if req else [])
            nums_h = "".join(f'<div><b>{E(str(a))}</b><span>{E(b)}</span></div>' for a, b in nums)
            cartoes.append(f'<a class="sit-card" href="{k}.html" style="--cor:{cor}"><span class="sit-tag">{E(nome)}</span><span class="sit-curta">{E(curta)}</span>'
                           f'<span class="pn-v pn-{cl}">{E(rot)}</span><span class="sit-desc">{E(est["desc"])}</span>'
                           f'<span class="pn-nums">{nums_h}</span><span class="sit-ir">Abrir o {E(nome)} →</span></a>')
        blocos_resumo = ""
        for chave, nome, desc, pags in resumo:
            blocos_resumo = "".join(f'<a class="doc-card" href="{p["slug"]}.html"><span class="doc-card-titulo"><span class="doc-n">{p["n"]}</span>{E(p["titulo"])}</span>'
                                    f'<span class="doc-card-meta">{"Word disponível" if p["word"] else "Leitura no portal"}</span></a>' for p in pags)
        dv = [p for g in mod["roteiro"] for p in g[3] if p.get("desvios")]
        bloco_menus = ""
        if dv:
            bloco_menus = ('<h2 class="secao-titulo">Menus do sistema, tela a tela</h2>'
                           '<p class="secao-desc">Cada menu do sistema entregue tem uma página por tela, com o manual do usuário, os campos, as regras, o fluxo e os casos de teste, e o Word para baixar.</p>')
            for m in dict.fromkeys(_menu_de(p) for p in dv):
                pm = [p for p in dv if _menu_de(p) == m]
                entenda = next(p for p in pm if p.get("intro"))
                n_telas = len({p["tela_n"] for p in pm if p.get("tela_n")})
                bloco_menus += (f'<h3 class="novo-menu">{E(m)} ({n_telas} telas)</h3>'
                                f'<p class="secao-desc">{MENUS_GQ_DESC.get(m, "")} '
                                f'<a href="{entenda["slug"]}.html">Entenda o menu: o que faz e por que importa</a>.</p>' + _cartoes_um_menu(pm))
        return (cabecalho(f"{mod['nome']} · iLabMedSys", raiz, "modulos") + f"""
<main class="pagina-modulo" id="conteudo">
  <nav class="trilha" aria-label="Você está em"><a href="{raiz}index.html">Início</a> › <span>{E(mod['nome'])}</span></nav>
  <header class="mod-cabecalho" style="--cor:{mod['cor']}">
    <div class="mod-icone" aria-hidden="true">{mod['icone']}</div>
    <div>
      <p class="sit-etiqueta" style="--cor:#334155">Visão geral do módulo</p>
      <h1>{E(mod['nome'])}</h1>
      <p>{E(intro_modulo(mod))}</p>
    </div>
  </header>
  <h2 class="secao-titulo">Escolha uma situação</h2>
  <p class="secao-desc">O módulo é o mesmo. O que muda é o retrato: o sistema entregue, a versão nova ou o que deve ser.</p>
  <div class="sit-cards">{"".join(cartoes)}</div>
  <h2 class="secao-titulo">Resumo do módulo</h2>
  <p class="secao-desc">Um resumo só, que situa o módulo nas três situações.</p>
  <div class="doc-cards">{blocos_resumo}</div>{bloco_menus}
  {fim}
</main>
""" + rodape(raiz))

    nome_sit, curta, cor = next((n, c, k) for kk, n, c, k in SITUACOES_MOD if kk == sit)
    est = estados[sit]
    grupos = [g for g in mod["roteiro"] if _secao_de(g[0])[0] == sit]
    pags_sit = [p for g in grupos for p in g[3]]
    soma = {"casos": 0, "regras": 0, "requisitos": 0, "desvios": 0}
    for p in pags_sit:
        for k in soma:
            soma[k] = max(soma[k], p["contagem"][k]) if k != "regras" else soma[k] + p["contagem"][k]
    fluxos = [p for p in pags_sit if p["cat"] == "fluxos" and not p.get("roteiro_de")]
    numeros = [(len(pags_sit), "documentos")]
    if sit == "legado":
        if fluxos:
            numeros.append((len(fluxos), "fluxos documentados"))
        c, pl = est["casos"]
        if pl:
            numeros.append((f"{c}/{pl}", "casos de teste executados"))
        if soma["desvios"]:
            numeros.append((soma["desvios"], "desvios registrados nos testes"))
    elif sit == "novo":
        numeros += est["numeros"]
    else:
        if soma["requisitos"]:
            numeros.append((soma["requisitos"], "requisitos para a versão corrigida"))
    num_html = "".join(f'<div class="numero"><strong>{E(str(n))}</strong><span>{E(r)}</span></div>' for n, r in numeros)

    blocos, submenu = [], []
    secao_atual = None
    for i, (chave, nome, desc, pags) in enumerate(grupos, 1):
        if chave == "fluxos":
            roteiros = {p["roteiro_de"]: p for p in pags if p.get("roteiro_de")}
            cards = []
            for p in pags:
                if p.get("roteiro_de"):
                    continue
                card = (f'<a class="fluxo-card" href="{p["slug"]}.html"><span class="fluxo-n">{p["n"]}</span>'
                        + (f'<img src="{p["fluxograma"]}" alt="" loading="lazy">' if p["fluxograma"] else '<div class="fluxo-sem-img">Fluxo descrito em texto</div>')
                        + f'<span>{E(p["titulo"])}</span></a>')
                r = roteiros.get(p["arq"])
                if r:
                    telas = telas_do_roteiro(r)
                    li = "".join(f'<li><a href="{r["slug"]}.html#{a}">{E(n)}</a></li>' for n, a in telas)
                    word = f' · <a href="{r["word"]}" download>Word</a>' if r["word"] else ""
                    card = (f'<div class="fluxo-bloco">{card}<details class="fluxo-roteiro" open><summary>Passo a passo para testar ({len(telas)} telas)</summary>'
                            f'<ol>{li}</ol><p class="fluxo-roteiro-tudo"><a href="{r["slug"]}.html">Abrir o roteiro completo</a>{word}</p></details></div>')
                cards.append(card)
            grade = f'<div class="fluxos">{"".join(cards)}</div>'
        elif chave == "desvios":
            grade = cartoes_desvios(pags)
        elif chave == "novo" and any(p.get("grupo") for p in pags):
            def _card(p):
                return (f'<a class="doc-card" href="{p["slug"]}.html"><span class="doc-card-titulo"><span class="doc-n">{p["n"]}</span>{E(p["titulo"])}</span>'
                        f'<span class="doc-card-meta">Leitura no portal</span></a>')
            partes = [f'<h3 class="novo-menu">Informações gerais</h3><div class="doc-cards">{"".join(_card(p) for p in pags if not p.get("grupo"))}</div>']
            roteiros = {p["roteiro_de"]: p for p in pags if p.get("roteiro_de")}
            for g in dict.fromkeys(p["grupo"] for p in pags if p.get("grupo")):
                cartoes = ""
                for p in [x for x in pags if x.get("grupo") == g and not x.get("roteiro_de")]:
                    r = roteiros.get(p["arq"])
                    cartoes += (f'<div class="doc-card tela-card"><a class="doc-card-titulo" href="{p["slug"]}.html"><span class="doc-n">{p["n"]}</span>{E(p["tela"])}</a>'
                                f'<span class="doc-card-meta">{E(p.get("situacao_tela") or "")}</span>'
                                f'<span class="tela-links"><a href="{p["slug"]}.html">{E(p.get("rotulo") or "Resumo geral")}</a>'
                                + (f' · <a href="{r["slug"]}.html">Passo a passo</a>' if r else "") + '</span></div>')
                partes.append(f'<h3 class="novo-menu">{E(g)}</h3><div class="doc-cards">{cartoes}</div>')
            grade = "".join(partes)
        else:
            cards = "".join(
                f'<a class="doc-card" href="{p["slug"]}.html"><span class="doc-card-titulo"><span class="doc-n">{p["n"]}</span>{E(p["titulo"])}</span>'
                f'<span class="doc-card-meta">{"Word disponível" if p["word"] else "Leitura no portal"}</span></a>' for p in pags)
            grade = f'<div class="doc-cards">{cards}</div>'
        classe = "secao passo secao-ideal" if chave == "ideal" else "secao passo"
        sk, sn, sd = _secao_de(chave)
        if chave in ("novo", "resumo"):
            blocos.append(f'<section class="{classe}" id="passo-{chave}">{grade}</section>')
        else:
            blocos.append(f'<section class="{classe}" id="passo-{chave}"><div class="passo-cab"><div><h3>{E(nome)}</h3><p class="secao-desc">{E(desc)}</p></div></div>{grade}</section>')
            submenu.append(f'<a href="#passo-{chave}"{" class=\"submenu-ideal\"" if chave == "ideal" else ""}>{E(nome)}</a>')
    submenu_html = f'<nav class="submenu" aria-label="Passos do roteiro">{"".join(submenu)}</nav>' if len(submenu) > 1 else ""
    if not pags_sit:
        blocos = ['<p class="secao-desc sit-vazio">Ainda não há documentos nesta situação. Eles aparecem aqui quando existirem.</p>']

    _apto = next((p for p in pags_sit if "não está apto" in p["titulo"].lower()), None)
    cl, rot = est["chip"]
    selo_sit = (f'<a class="selo-link" href="{_apto["slug"]}.html" title="Por que não está apto"><span class="pn-v pn-{cl}">{E(rot)}</span><span class="selo-saiba">Por quê? →</span></a>'
                if _apto else f'<span class="pn-v pn-{cl}">{E(rot)}</span>')
    comece = ""
    if pags_sit:
        primeiro, ultimo = pags_sit[0], pags_sit[-1]
        comece = (f'<section class="comece" style="border-color:{cor}"><div><p class="comece-rotulo" style="color:{cor}">Comece aqui</p>'
                  f'<p>Esta parte tem <strong>{len(pags_sit)} documentos</strong>, do primeiro ({E(primeiro["titulo"])}) ao último ({E(ultimo["titulo"])}). Leia na ordem: cada documento leva ao próximo.</p></div>'
                  f'<a class="botao botao-grande" href="{primeiro["slug"]}.html">Iniciar o roteiro →</a></section>')

    return (cabecalho(f"{mod['nome']} · {nome_sit} · iLabMedSys", raiz, "modulos") + f"""
<main class="pagina-modulo" id="conteudo">
  <nav class="trilha" aria-label="Você está em"><a href="{raiz}index.html">Início</a> › <a href="index.html">{E(mod['nome'])}</a> › <span>{E(nome_sit)}</span></nav>
  <header class="mod-cabecalho mod-sit" style="--cor:{cor}">
    <div class="mod-icone" aria-hidden="true">{mod['icone']}</div>
    <div>
      <p class="sit-etiqueta" style="--cor:{cor}">{E(nome_sit)} · {E(curta)}</p>
      <h1>{E(mod['nome'])} <span class="sit-sufixo">· {E(nome_sit)}</span></h1>
      <p>{E(est["desc"])}</p>
      <div class="mod-status">{selo_sit}</div>
    </div>
  </header>
  {troca_situacao(sit, mod)}
  <div class="numeros">{num_html}</div>
  {comece}
  {submenu_html}
  {''.join(blocos)}
  {fim if sit == "legado" else ""}
</main>
""" + rodape(raiz))


def bloco_painel(origem, ordem):
    """Painel da página inicial: veredito, três situações (Legado, Novo, Ideal), mapa do lote, quebras e ANVISA.
    Números de casos vêm do cronograma.json; o restante, do painel.json."""
    hom = Path(origem) / "homologacao"
    if not (hom / "painel.json").exists() or not (hom / "cronograma.json").exists():
        return ""
    pn = json.loads(higiene.redigir((hom / "painel.json").read_text(encoding="utf-8")))
    cr = {m["id"]: m for m in json.loads(higiene.redigir((hom / "cronograma.json").read_text(encoding="utf-8")))["modulos"]}
    total_plan = sum(c["testes"]["planejados"] for c in cr.values() if c.get("testes"))
    total_conc = sum(c["testes"]["conclusivos"] for c in cr.values() if c.get("testes"))
    alta_pend = sum(c["testes"]["alta_pendentes"] for c in cr.values() if c.get("testes"))
    n_mod = len(ordem)

    # Aderência à ANVISA no legado (contagem do próprio diagnóstico)
    arq = hom / DIAGNOSTICO
    nums = ("0", "0", "0", "0")
    if arq.exists():
        m = re.search(r"\*\*Contagem:\*\* Atende (\d+) · Parcial (\d+).*?Não atende (\d+).*?A verificar (\d+)", arq.read_text(encoding="utf-8"))
        if m:
            nums = m.groups()
    ok, parc, nao, ver = (int(x) for x in nums)
    total_temas = ok + parc + nao + ver

    def chip(classe, rotulo):
        return f'<span class="pn-v pn-{classe}">{E(rotulo)}</span>'

    def nums_html(itens):
        return "".join(f'<div><b>{E(a)}</b><span>{E(b)}</span></div>' for a, b in itens)

    leg, nov, ide = pn["legado"], pn["novo"], pn["ideal"]
    leg_nums = [(f'{leg["modulos_homologados"]} de {n_mod}', "módulos homologados (testados e com parecer)"),
                (str(total_conc), f"casos executados, de {total_plan} planejados"),
                (f"{ok} / {parc} / {nao}", "temas da RDC: atende / em parte / não atende"),
                (str(alta_pend), "casos de prioridade Alta ainda sem resultado")]
    def ideal_pronto(m):
        """O ideal só representa a verdade onde os testes de código e de tela terminaram (situação Fechado)."""
        return any(p["cat"] == "ideal" for p in m["paginas"]) and cr.get(m["id"], {}).get("situacao", "").startswith("Fechado")

    n_ideal = sum(1 for m in ordem if ideal_pronto(m))
    ide_nums = [(f"{n_ideal} de {n_mod}", "módulos com o ideal definido (testes concluídos)")] + [tuple(x) for x in ide["numeros"]]

    def cartao(classe, titulo, dado, numeros, destino=""):
        rotulo, cl = dado["veredito"]
        return (f'<div class="pn-card pn-{classe}"><h3>{titulo}</h3><p class="pn-q">{E(dado["pergunta"])}</p>{chip(cl, rotulo)}'
                f'<div class="pn-nums">{nums_html(numeros)}</div><p class="pn-prox"><em>Para destravar:</em> {E(dado["trava"])}</p></div>')

    # --- bloco de atenção
    atencao = "".join(f'<div class="pn-k"><b>{a["n"]}</b><span>{E(a["titulo"])}<small>{E(a["sub"])}</small></span></div>' for a in pn.get("atencao", []))

    # --- roscas: uma por situação
    def rosca(partes, centro, sub):
        tot = sum(v for _, v, _ in partes) or 1
        r, c, off, arcos = 52, 2 * 3.14159265 * 52, 0.0, ""
        for nome, v, k in partes:
            if not v:
                continue
            l = c * v / tot
            arcos += (f'<circle r="{r}" cx="70" cy="70" fill="none" class="pn-arco pn-c-{k}" stroke-width="16" '
                      f'stroke-dasharray="{max(l - 2, 0.1):.1f} {c - l + 2:.1f}" stroke-dashoffset="{-off:.1f}" transform="rotate(-90 70 70)"><title>{E(nome)}: {v}</title></circle>')
            off += l
        leg = "".join(f'<li><i class="pn-c-{k}"></i><span>{E(n)}</span><b>{v}</b></li>' for n, v, k in partes)
        return (f'<div class="pn-rosca"><svg width="140" height="140" viewBox="0 0 140 140" role="img" aria-label="{E(sub)}"><circle r="{r}" cx="70" cy="70" fill="none" class="pn-fundo" stroke-width="16"/>'
                f'{arcos}<text x="70" y="72" text-anchor="middle" class="pn-rc-n">{E(centro)}</text><text x="70" y="90" text-anchor="middle" class="pn-rc-s">{E(sub)}</text></svg><ul class="pn-lg">{leg}</ul></div>')

    def conta(cels):
        return [("nao", "Não apto"), ("parcial", "Em testes"), ("vazio", "Só código")] if cels is None else cels
    n_leg = {"nao": 0, "parcial": 0, "vazio": 0}
    n_nov = {"nao": 0, "parcial": 0, "vazio": 0}
    for m in ordem:
        sit = cr.get(m["id"], {}).get("situacao", "")
        n_leg["nao" if sit.startswith("Fechado") else "parcial" if sit.startswith("Em testes") else "vazio"] += 1
        nv = pn["modulos_novo"].get(m["id"])
        n_nov[nv[0] if nv else "vazio"] += 1
    r_leg = rosca([("Não apto", n_leg["nao"], "nao"), ("Em testes", n_leg["parcial"], "parcial"), ("Só código", n_leg["vazio"], "vazio")], str(n_mod), "módulos")
    r_nov = rosca([("Não apto", n_nov["nao"], "nao"), ("Em testes", n_nov["parcial"], "parcial"), ("Não iniciado", n_nov["vazio"], "vazio")], str(n_mod), "módulos")
    r_ide = rosca([("Definido", n_ideal, "ideal"), ("Rascunho", n_mod - n_ideal, "vazio")], f"{n_ideal} de {n_mod}", "definidos")
    roscas = (f'<div class="pn-cd pn-cd-leg"><h3>Legado</h3><p>Módulos pelo veredito do sistema entregue</p>{r_leg}</div>'
              f'<div class="pn-cd pn-cd-nov"><h3>Novo</h3><p>Módulos pela situação na versão nova</p>{r_nov}</div>'
              f'<div class="pn-cd pn-cd-ide"><h3>Ideal</h3><p>Módulos com o ideal definido (testes concluídos)</p>{r_ide}</div>')

    # --- casos por módulo
    def _t(m):
        return cr.get(m["id"], {}).get("testes") or {}
    barras = "".join(
        f'<a class="pn-br" href="documentacao/{m["id"]}/index.html" title="Abrir {E(m["nome"])}"><span>{E(m["nome"])}</span>'
        f'<div class="pn-trilho"><i style="width:{round(100 * _t(m).get("conclusivos", 0) / max(_t(m).get("planejados", 1), 1))}%"></i></div>'
        f'<b>{_t(m).get("conclusivos", 0)}/{_t(m).get("planejados", 0)}</b></a>' for m in ordem)

    # --- detalhe do módulo, com seletor
    def detalhe(m):
        c = cr.get(m["id"], {})
        t = c.get("testes") or {}
        sit = c.get("situacao", "")
        lcl, lrot = ("nao", "Não apto") if sit.startswith("Fechado") else ("parcial", "Em testes") if sit.startswith("Em testes") else ("vazio", "Só análise de código")
        nv = pn["modulos_novo"].get(m["id"])
        ncl, nrot = (nv[0], nv[1]) if nv else ("vazio", "Não iniciado")
        icl, irot = ("ideal", "Definido") if ideal_pronto(m) else ("vazio", "Rascunho")
        cn = pn.get("classes_novo", {}).get(m["id"])
        if cn:
            tot = sum(v for _, v, _ in cn["classes"]) or 1
            seg = "".join(f'<div class="pn-seg pn-c-{k}" style="width:{100 * v / tot:.1f}%" title="{E(n)}: {v}"></div>' for n, v, k in cn["classes"])
            lg = "".join(f'<li><i class="pn-c-{k}"></i><span>{E(n)}</span><b>{v}</b></li>' for n, v, k in cn["classes"])
            corpo = f'<div class="pn-emp">{seg}</div><ul class="pn-lg">{lg}</ul><p class="pn-nota">{E(cn["nota"])}</p>'
        else:
            corpo = '<p class="pn-nota">Ainda não testado na versão nova. Quando os testes começarem, a comparação com o legado aparece aqui.</p>'
        return (f'<div class="pn-det" data-m="{m["id"]}"{"" if m is ordem[0] else " hidden"}>'
                f'<p class="pn-det-nome"><a href="documentacao/{m["id"]}/index.html">Abrir a página de {E(m["nome"])} →</a></p><ul class="pn-tres-linhas"><li><em>Legado</em>{chip(lcl, lrot)}<small>{t.get("conclusivos", 0)} de {t.get("planejados", 0)} casos</small></li>'
                f'<li><em>Novo</em>{chip(ncl, nrot)}</li><li><em>Ideal</em>{chip(icl, irot)}</li></ul>'
                f'<h4>Versão nova × legado</h4>{corpo}'
                f'<p class="pn-det-links"><a href="documentacao/{m["id"]}/legado.html">Legado</a> · <a href="documentacao/{m["id"]}/novo.html">Novo</a> · <a href="documentacao/{m["id"]}/ideal.html">Ideal</a></p></div>')
    opcoes = "".join(f'<option value="{m["id"]}">{E(m["nome"])}</option>' for m in ordem)
    detalhes = "".join(detalhe(m) for m in ordem)

    # mapa do lote
    cab = "".join(f'<a class="pn-h" href="documentacao/{m["id"]}/index.html" title="Abrir {E(m["nome"])}"><span>{k}</span>{E(m["nome"])}</a>' for k, m in enumerate(ordem, 1))
    cel_leg, cel_nov, cel_ide = [], [], []
    for m in ordem:
        c = cr.get(m["id"], {})
        t = c.get("testes") or {}
        plan, conc = t.get("planejados", 0), t.get("conclusivos", 0)
        sit = c.get("situacao", "")
        href = f'documentacao/{m["id"]}/index.html'
        if sit.startswith("Fechado"):
            cl, rot = "nao", "Não apto"
        elif sit.startswith("Em testes"):
            cl, rot = "parcial", "Em testes"
        else:
            cl, rot = "vazio", "Só código"
        cel_leg.append(f'<a class="pn-n pn-{cl}" href="documentacao/{m["id"]}/legado.html">{rot}<small>{conc}/{plan} casos</small></a>')
        nv = pn["modulos_novo"].get(m["id"])
        if nv:
            cel_nov.append(f'<a class="pn-n pn-{nv[0]}" href="documentacao/{m["id"]}/novo.html">{E(nv[1])}<small>{E(nv[2])}</small></a>')
        else:
            cel_nov.append(f'<a class="pn-n pn-vazio" href="documentacao/{m["id"]}/novo.html">Não iniciado</a>')
        if ideal_pronto(m):
            cel_ide.append(f'<a class="pn-n pn-ideal" href="documentacao/{m["id"]}/ideal.html">Ideal definido<small>testes concluídos</small></a>')
        else:
            cel_ide.append(f'<a class="pn-n pn-vazio" href="documentacao/{m["id"]}/ideal.html">Aguarda os testes<small>rascunho</small></a>')

    def raia(classe, nome, cels):
        return f'<div class="pn-raia"><div class="pn-lane pn-l-{classe}">{nome}</div>{"".join(cels)}</div>'

    mapa = f"""<div class="pn-mapa" role="region" aria-label="Situação de cada módulo, nas três situações">
      <div class="pn-raia pn-cab"><div></div>{cab}</div>
      {raia("leg", "Legado", cel_leg)}{raia("nov", "Novo", cel_nov)}{raia("ide", "Ideal", cel_ide)}
      <p class="pn-legenda"><i class="pn-nao"></i>Não apto <i class="pn-parcial"></i>Em testes <i class="pn-ideal"></i>Ideal definido <i class="pn-vazio"></i>Ainda sem resultado</p>
    </div>"""

    quebras = "".join(f'<div class="pn-quebra"><b>{E(a)}</b>{E(b)}<span>Fonte: {E(c)}</span></div>' for a, b, c in pn["quebras"])

    def barra_anv(rotulo, partes):
        seg = "".join(f'<div class="pn-seg pn-{cl}" style="width:{pct}%">{E(txt)}</div>' for pct, cl, txt in partes if pct)
        return f'<p class="pn-bl">{rotulo}</p><div class="pn-bar">{seg}</div>'

    pct = lambda n: round(100 * n / total_temas) if total_temas else 0
    anvisa_barra = barra_anv("Legado", [(pct(ok), "ok", ""), (pct(parc), "parcial", ""), (pct(nao), "nao", ""), (pct(ver), "vazio", "")]).replace('<p class="pn-bl">Legado</p>', "")

    return f"""<section class="pn-topo">
    <div class="pn-topo-in">
      <p class="sobretitulo">LabMedSys agora é iLabMedSys · situação em {E(pn["atualizado"])}</p>
      <h1>{E(pn["veredito"]["titulo"])}</h1>
      <p class="pn-sub">{E(pn["veredito"]["sub"])}</p>
      <div class="pn-escada" aria-label="Três situações do sistema">
        <div class="pn-deg pn-d-leg"><b>Legado</b><span>o que o fornecedor entregou</span></div><span class="pn-seta">corrigir falhas →</span>
        <div class="pn-deg pn-d-nov"><b>Novo</b><span>o que o desenvolvimento entrega</span></div><span class="pn-seta">fechar as lacunas →</span>
        <div class="pn-deg pn-d-ide"><b>Ideal</b><span>o que a ANVISA exige</span></div>
      </div>
    </div>
  </section>
  <section class="secao" id="atencao">
    <div class="pn-pre"><h2>🔔 Precisa de você agora</h2><p>Itens que travam o avanço e dependem de pessoas.</p><div class="pn-g4">{atencao}</div></div>
  </section>
  <section class="secao" id="situacao">
    <h2>Os módulos nas três situações</h2>
    <p class="secao-desc">Cada rosca conta os {n_mod} módulos em uma situação do sistema.</p>
    <div class="pn-tres">{roscas}</div>
  </section>
  <section class="secao" id="indicadores">
    <div class="pn-tres pn-tres-ind">
      <div class="pn-cd"><h3>Casos de teste por módulo</h3><p>{total_conc} executados de {total_plan} planejados, no legado</p>{barras}</div>
      <div class="pn-cd" id="diretoria"><h3>Aderência à ANVISA</h3><p>{total_temas} temas da RDC 658/2022 e do Guia 33/2020, no legado</p>
        <div class="pn-grande"><div><b class="pn-t-ok">{ok}</b><span>atendem</span></div><div><b class="pn-t-parcial">{parc}</b><span>em parte</span></div><div><b class="pn-t-nao">{nao}</b><span>não atendem</span></div></div>
        {anvisa_barra}
        <p class="pn-nota">Na versão nova a medida entra tema a tema, conforme os testes avançam.</p>
        <p class="pn-det-links"><a href="documentacao/visao-geral/diagnostico-de-conformidade-com-a-anvisa.html">Ler o diagnóstico →</a> · <a href="documentacao/arquivos/visao-geral/LabMedSys - Diagnostico de Conformidade ANVISA.docx">Word</a></p></div>
      <div class="pn-cd"><h3>Detalhe de um módulo</h3><p><label for="pn-sel">Módulo: </label><select id="pn-sel" class="pn-sel">{opcoes}</select></p>{detalhes}</div>
    </div>
  </section>
  <section class="secao" id="mapa">
    <h2>O lote pelos {n_mod} módulos, nas três situações</h2>
    <p class="secao-desc">É o processo fabril, do recebimento à rastreabilidade. Cada raia é uma situação; a cor diz se o elo segura. Clique num módulo para abrir a página dele.</p>
    {mapa}
  </section>
  <section class="secao" id="quebras">
    <h2>Onde a corrente quebra (legado)</h2>
    <p class="secao-desc">Pontos em que um módulo não conversa direito com o outro, já confirmados no código ou nas telas.</p>
    <div class="pn-quebras">{quebras}</div>
  </section>
  <script>(function(){{var s=document.getElementById('pn-sel');if(!s)return;s.addEventListener('change',function(){{document.querySelectorAll('.pn-det').forEach(function(e){{e.hidden=e.getAttribute('data-m')!==s.value;}});}});}})();</script>"""


def pagina_inicial(origem):
    raiz = ""
    cards = []
    por_id = {m["id"]: m for m in MODULOS}
    ordem = [por_id[i] for i in CAMINHO if i in por_id and i not in ESPECIAIS]
    ordem += [m for m in MODULOS if m["id"] not in ESPECIAIS and m not in ordem]
    for k, mod in enumerate(ordem, 1):
        n = len(mod["paginas"])
        inner = (f'<div class="mc-topo"><span class="mc-icone" style="--cor:{mod["cor"]}">{mod["icone"]}</span><span class="mc-n" title="Posição no caminho do lote">{k}</span>{selo(mod["situacao"])}</div>'
                 f'<h3>{E(mod["nome"])}</h3><p>{E(mod["resumo"])}</p>{barra(mod["nivel"])}'
                 f'<div class="mc-rodape">{f"{n} documentos" if n else "Ainda sem documentação"}</div>')
        if n:
            cards.append(f'<a class="modulo-card" href="documentacao/{mod["id"]}/index.html">{inner}</a>')
        else:
            cards.append(f'<div class="modulo-card modulo-futuro" aria-disabled="true">{inner}</div>')

    passos_caminho = "".join(
        f'<li><a href="documentacao/{m["id"]}/index.html" style="--cor:{m["cor"]}"><span class="cam-n">{k}</span><span class="cam-nome">{E(m["nome"])}</span></a></li>'
        for k, m in enumerate(ordem, 1) if m["paginas"])
    vg0 = por_id["visao-geral"]
    caminho = (f'''<section class="secao" id="caminho">
    <h2>O caminho do lote pelos módulos</h2>
    <p class="secao-desc">A documentação segue o processo: começa no cadastro-base e termina na rastreabilidade do medicamento. Dentro de cada módulo há um roteiro com começo, passos numerados e fim, e o último documento leva ao módulo seguinte.</p>
    <div class="caminho-marcos"><span><b>Começa em</b> {E(ordem[0]["nome"])}</span><span><b>Termina em</b> {E(ordem[-1]["nome"])}</span>
      <a class="botao botao-secundario" href="documentacao/visao-geral/index.html">Antes de começar: a visão de ponta a ponta →</a></div>
    <ol class="caminho">{passos_caminho}</ol>
  </section>''')

    def link(mid, s):
        mod = next(m for m in MODULOS if m["id"] == mid)
        p = next((p for p in mod["paginas"] if p["slug"] == s), None)
        if not p:
            raise SystemExit(f"Atalho por público aponta para documento inexistente: {mid}/{s}")
        return f'<li><a href="documentacao/{mid}/{s}.html">{E(p["titulo"])}</a> <small>{E(mod["nome"])}</small></li>'

    publicos = "".join(
        f'<div class="publico"><h3>{E(nome)}</h3><p>{E(desc)}</p><ul>{"".join(link(m, s) for m, s in itens)}</ul></div>'
        for nome, desc, itens in PUBLICOS)

    vg = next(m for m in MODULOS if m["id"] == "visao-geral")
    total_docs = sum(len(m["paginas"]) for m in MODULOS)
    total_fluxos = sum(1 for m in MODULOS for p in m["paginas"] if p["cat"] == "fluxos" and not p.get("roteiro_de"))
    modulos_com_doc = sum(1 for m in MODULOS if m["paginas"] and m["id"] not in ESPECIAIS)
    total_modulos = len([m for m in MODULOS if m["id"] not in ESPECIAIS])

    painel = bloco_painel(origem, ordem)
    return (cabecalho("iLabMedSys · Documentação do sistema", raiz) + f"""
<main id="conteudo">
  {painel}

  <section class="secao" id="modulos">
    <h2>Módulos</h2>
    <p class="secao-desc">Na ordem do caminho do lote. Escolha um para ver o roteiro dele: fluxos, regras, testes e documentos para baixar. O primeiro passo de cada módulo traz o resumo completo.</p>
    <div class="modulos">{''.join(cards)}</div>
  </section>

  <section class="secao destaque" style="--cor:{vg['cor']}">
    <div>
      <h2>Visão entre módulos</h2>
      <p>{E(vg['resumo'])}</p>
    </div>
    <a class="botao" href="documentacao/visao-geral/index.html">Ver o mapa do processo fabril →</a>
  </section>

  <section class="secao" id="publicos">
    <h2>Por onde começar</h2>
    <p class="secao-desc">Atalhos para cada público.</p>
    <div class="publicos">{publicos}</div>
  </section>

  <section class="secao apresentacao-chamada">
    <div>
      <h2>Apresentação do iLabPharma</h2>
      <p>A experiência visual dos processos farmacêuticos continua disponível, sem mudanças.</p>
    </div>
    <a class="botao botao-secundario" href="apresentacao.html">Abrir a apresentação ↗</a>
  </section>
</main>
""" + rodape(raiz))


# ---------------------------------------------------------------------------------------------
# Página ANVISA: o que a norma pede, por módulo
# ---------------------------------------------------------------------------------------------
# Fonte de cada módulo: (documento com o quadro de temas e o apêndice da norma, JSON dos trechos,
# coluna da situação no quadro; None = 4ª coluna, como nas conformidades de módulo).
FONTES_ANVISA = {
    "principal": [(DIAGNOSTICO, "transversal/03-diagnostico-normas.json", "Principal")],
    "estoque": [("3.estoque/04-conformidade-regulatoria.md", "3.estoque/04-conformidade-normas.json", None)],
    "garantia-qualidade": [(DIAGNOSTICO, "transversal/03-diagnostico-normas.json", "GQ")],
    "controle-qualidade": [("4.controle_qualidade/04-conformidade-regulatoria.md", "4.controle_qualidade/04-conformidade-normas.json", None)],
    "controle-documentos": [("6.controle_documento/04-conformidade-regulatoria.md", "6.controle_documento/04-conformidade-normas.json", None)],
    "producao": [("2.producao/04-conformidade-regulatoria.md", "2.producao/04-conformidade-normas.json", None)],
    "ope": [("9.ope/04-conformidade-regulatoria.md", "9.ope/04-conformidade-normas.json", None)],
    "comercial": [("7.comercial/04-conformidade-regulatoria.md", "7.comercial/04-conformidade-normas.json", None)],
    "rastreabilidade": [("8.rastreabilidade/04-conformidade-regulatoria.md", "8.rastreabilidade/04-conformidade-normas.json", None)],
}
# Detalhe da situação que toca acesso, senha ou login não é publicado: fica só o selo.
RE_DETALHE_RESTRITO = re.compile(r"permiss|senha|login|acesso|autoriza|perfil|endere[çc]o", re.I)
SITUACOES = (("Não atende", "Não atende", "nao"), ("Não existe", "Não atende", "nao"), ("Protótipo", "Protótipo", "nao"),
             ("Atende em parte", "Parcial", "parcial"), ("Parcial", "Parcial", "parcial"), ("Atende", "Atende", "ok"),
             ("A verificar", "A verificar", "verificar"))


def _celulas(linha):
    return [c.strip() for c in linha.strip().strip("|").split("|")]


def _texto_simples(md):
    md = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", md)
    return re.sub(r"\*\*|\*|`", "", md).strip()


def _situacao(txt):
    for inicio, rotulo, classe in SITUACOES:
        if txt.lower().startswith(inicio.lower()):
            return rotulo, classe
    return "Ver o detalhe", "verificar"


def temas_anvisa(hom, arq, col):
    """Temas do quadro (só as linhas com link para o apêndice) e o texto da norma de cada um."""
    texto = ler(hom / arq)
    temas, cab = [], None
    for linha in texto.splitlines():
        if linha.startswith("| # |"):
            cab = _celulas(linha)
            continue
        m = re.match(r"^\| (\d+) \|", linha)
        if not m or "](#tema-" not in linha or not cab:
            continue
        c = _celulas(linha)
        if col is None:
            sit = c[3] if len(c) > 3 else ""
        elif col in cab and cab.index(col) < len(c):
            sit = c[cab.index(col)]
        else:
            continue
        sit = _texto_simples(sit)
        if not sit or sit in ("—", "-"):
            continue
        i = cab.index(col) if col in cab else 0
        while sit == "Idem" and i > 3:                        # repete a coluna anterior
            i -= 1
            sit = _texto_simples(c[i])
        rot, classe = _situacao(sit)
        if sit.startswith("Usa o Principal"):
            rot, classe = "Usa o Principal", "verificar"
        elif rot == "Ver o detalhe" and "Situação geral" in cab and cab.index("Situação geral") < len(c):
            rot, classe = _situacao(_texto_simples(c[cab.index("Situação geral")]))   # situação geral da linha
        detalhe = re.sub(r"^(Não atende|Atende em parte|Atende|Parcial|Protótipos?|A verificar|Não existe)\s*(\([^)]*\))?\s*[:;,]?\s*",
                         "", sit, flags=re.I)
        detalhe = detalhe[:1].upper() + detalhe[1:]
        nome = _texto_simples(c[1])
        if RE_LINHA_SEG.search(linha) or RE_DETALHE_RESTRITO.search(nome + " " + detalhe):
            detalhe = ""
        temas.append({"n": m.group(1), "nome": nome, "ref": _texto_simples(c[2]), "rot": rot, "classe": classe,
                      "detalhe": detalhe})
    # Apêndice: "## Tema N · título" até o próximo tema ou o fim do bloco
    ap = texto.split("<!-- NORMAS:INICIO -->", 1)[-1].split("<!-- NORMAS:FIM -->", 1)[0]
    blocos = dict(re.findall(r"^## Tema (\d+) · [^\n]*\n(.*?)(?=^## Tema \d+ · |\Z)", ap, re.M | re.S))
    for tm in temas:
        tm["norma"] = markdown.markdown(blocos.get(tm["n"], "*Texto da norma não encontrado.*").strip(),
                                        extensions=["sane_lists"])
    return temas


def _chave_norma(item):
    if item[0] == "rdc":
        n = int(item[1])
        return (0, (n,), f"RDC 658/2022, art. {n}º" if n < 10 else f"RDC 658/2022, art. {n}")
    if item[0] == "guia":
        return (1, tuple(int(x) for x in re.findall(r"\d+", str(item[1]))), f"Guia 33/2020, item {item[1]}")
    return None

ANV_JS = """<script>
(function(){
  var campo=document.getElementById("anv-busca"), info=document.getElementById("anv-info");
  function norm(s){return s.normalize("NFD").replace(/[\\u0300-\\u036f]/g,"").toLowerCase().replace(/\\bn\\.?\\s?[o\\u00ba]\\b/g," ");}
  var temas=[].slice.call(document.querySelectorAll(".anv-tema")).map(function(e){return {e:e,t:norm(e.textContent)};});
  var linhas=[].slice.call(document.querySelectorAll(".anv-indice tbody tr")).map(function(e){return {e:e,t:norm(e.textContent)};});
  function filtrar(){
    var q=norm(campo.value).split(/[^a-z0-9]+/).filter(Boolean), n=0, vm={}, nl=0;
    temas.forEach(function(x){var ok=q.every(function(w){return x.t.indexOf(w)>=0;});x.e.hidden=!ok;if(ok){n++;vm[x.e.dataset.mod]=1;}});
    linhas.forEach(function(x){var ok=q.every(function(w){return x.t.indexOf(w)>=0;});x.e.hidden=!ok;if(ok)nl++;});
    info.innerHTML=n?"<strong>"+n+"</strong> tema(s) em <strong>"+Object.keys(vm).length+"</strong> m\\u00f3dulo(s)"+(q.length?"":" \\u00b7 digite acima para filtrar"):"Nada encontrado.";
    document.getElementById("anv-indice-info").textContent=nl+" artigo(s) ou item(ns)";
    try{history.replaceState(null,"",q.length?"#busca="+encodeURIComponent(campo.value):location.pathname);}catch(e){}
  }
  campo.addEventListener("input",filtrar);
  function abrir(){var h=decodeURIComponent(location.hash.slice(1));var m=h.match(/^busca=(.*)$/);
    if(m){campo.value=m[1];filtrar();return;}
    var e=document.getElementById(h); if(e&&e.tagName==="DETAILS"){e.hidden=false;e.open=true;e.scrollIntoView();}}
  addEventListener("hashchange",abrir); filtrar(); abrir();
})();
</script>"""


def pagina_anvisa(origem, busca):
    hom = origem / "homologacao"
    raiz = ""
    itens, indice, futuros = [], {}, []
    for mod in MODULOS:
        if mod["id"] in ESPECIAIS:
            continue
        fontes = FONTES_ANVISA.get(mod["id"])
        if not fontes:
            futuros.append(mod["nome"])
            continue
        for arq, js, col in fontes:
            normas = json.loads((hom / js).read_text(encoding="utf-8")) if (hom / js).exists() else {}
            for tm in temas_anvisa(hom, arq, col):
                anc = f"{mod['id']}-tema-{tm['n']}"
                for item in normas.get(tm["n"], []):
                    k = _chave_norma(item)
                    if k:
                        indice.setdefault(k[:2], [k[2], []])[1].append((mod, tm, anc))
                det = f'<p class="anv-detalhe"><strong>No sistema hoje:</strong> {E(tm["detalhe"])}</p>' if tm["detalhe"] else ""
                itens.append(
                    f'<details class="anv-tema" id="{anc}" style="--cor:{mod["cor"]}" data-mod="{mod["id"]}">'
                    f'<summary><span class="anv-nome"><span class="anv-mod">{E(mod["nome"])}</span>{E(tm["nome"])}'
                    f'<small>{E(tm["ref"])}</small></span>'
                    f'<span class="anv-sit anv-{tm["classe"]}">{E(tm["rot"])}</span></summary>'
                    f'<div class="anv-corpo">{det}<div class="texto">{tm["norma"]}</div>'
                    f'<p class="anv-link"><a href="documentacao/{mod["id"]}/index.html">Abrir o módulo {E(mod["nome"])} →</a></p></div></details>')
                busca.append({"t": f"ANVISA · {tm['nome']}", "m": mod["nome"], "u": f"anvisa.html#{anc}",
                              "h": [tm["ref"]], "x": re.sub(r"<[^>]+>", " ", tm["norma"])[:1500]})

    linhas = []
    for k in sorted(indice):
        nome, usos = indice[k]
        vistos, links = set(), []
        for mod, tm, anc in usos:
            if anc not in vistos:
                vistos.add(anc)
                links.append(f'<a href="#{anc}" class="anv-uso" style="--cor:{mod["cor"]}">{E(mod["nome"])}: {E(tm["nome"])}</a>')
        linhas.append(f'<tr><th scope="row">{E(nome)}</th><td>{"".join(links)}</td></tr>')
    nota_futuros = f" Ainda não analisados: {E(', '.join(futuros))}." if futuros else ""

    return (cabecalho("ANVISA por módulo · iLabMedSys", raiz, "anvisa") + f"""
<main id="conteudo" class="anvisa">
  <section class="anv-faixa">
    <div class="anv-faixa-interna">
      <nav class="trilha" aria-label="Você está em"><a href="index.html">Início</a> › <span>ANVISA</span></nav>
      <h1>O que a ANVISA pede, por módulo</h1>
      <p>Os temas da RDC 658/2022 e do Guia 33/2020 que valem para cada módulo, com o texto exato da norma e a situação do sistema entregue pelo fornecedor.</p>
      <label class="busca anv-busca"><span aria-hidden="true">⌕</span><input id="anv-busca" type="search" placeholder="Buscar nas normas: Guia 33/2020, art 121, assinatura…" aria-label="Buscar nas normas" autocomplete="off"></label>
    </div>
  </section>
  <div class="anv-conteudo">
    <div class="anv-cabeca"><p id="anv-info" aria-live="polite"></p><a href="#por-artigo">Índice por artigo ↓</a></div>
    {"".join(itens)}
    <section id="por-artigo" class="anv-indice-sec">
      <h2>Índice por artigo</h2>
      <p class="anv-sub">Cada artigo ou item citado e os temas em que ele aparece, conforme a busca · <span id="anv-indice-info"></span></p>
      <div class="tabela"><table class="anv-indice"><thead><tr><th>Artigo ou item</th><th>Onde aparece</th></tr></thead><tbody>{"".join(linhas)}</tbody></table></div>
    </section>
    <p class="anv-nota">Principal, Estoque e Garantia da Qualidade vêm do diagnóstico de conformidade entre os módulos; Produção, Controle da Qualidade e Controle de Documentos, da conformidade de cada módulo.{nota_futuros} Detalhes de acesso e senha não são publicados.</p>
  </div>
</main>
{ANV_JS}
""" + rodape(raiz))


# ---------------------------------------------------------------------------------------------
# Página Cronograma: andamento da homologação, módulo a módulo, com previsão de término.
# Fonte: homologacao/cronograma.json (mantido a cada rodada, junto com o diário de bordo).
# ---------------------------------------------------------------------------------------------
import datetime as _dt

MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def _dbr(iso):
    d = _dt.date.fromisoformat(iso)
    return f"{d.day:02d}/{d.month:02d}"


def pagina_cronograma(origem):
    arq = Path(origem) / "homologacao" / "cronograma.json"
    if not arq.exists():
        return ""
    cr = json.loads(higiene.redigir(arq.read_text(encoding="utf-8")))
    hoje = _dt.date.today()
    mods = cr["modulos"]
    cores = {m["id"]: m["cor"] for m in MODULOS}
    datas = [_dt.date.fromisoformat(f[k]) for m in mods for f in m["fases"] for k in ("inicio", "fim")]
    datas += [_dt.date.fromisoformat(x["data"]) for x in cr.get("marcos", [])]
    ini = min(datas) - _dt.timedelta(days=(min(datas).weekday()))  # começa na segunda
    fim = max(datas) + _dt.timedelta(days=(6 - max(datas).weekday()))  # termina no domingo
    dias = [ini + _dt.timedelta(days=i) for i in range((fim - ini).days + 1)]
    n = len(dias)
    pct = lambda i: f"{i / n * 100:.3f}%"
    rot = {"feito": "feito", "andamento": "em andamento", "previsto": "previsto"}
    legenda = cr.get("fases_legenda", {})

    # Cabeçalho do gráfico: meses e dias
    meses = []
    i = 0
    while i < n:
        j = i
        while j < n and dias[j].month == dias[i].month:
            j += 1
        rotulo_mes = f"{MESES[dias[i].month - 1]}/{dias[i].year}" if j - i >= 7 else MESES[dias[i].month - 1]
        meses.append(f'<div class="cr-mes" style="left:{pct(i)};width:{pct(j - i)}">{rotulo_mes}</div>')
        i = j
    diasx = "".join(
        f'<div class="cr-dia{" cr-fds" if d.weekday() >= 5 else ""}{" cr-hoje" if d == hoje else ""}" style="left:{pct(k)};width:{pct(1)}"><span>{d.day}</span></div>'
        for k, d in enumerate(dias))
    marcos_html = "".join(
        f'<div class="cr-marco cr-{x["status"]}{" cr-marco-baixo" if k % 2 else ""}" style="left:{pct((_dt.date.fromisoformat(x["data"]) - ini).days + 1)}" title="{E(x["nome"])} ({_dbr(x["data"])})"><span>{_dbr(x["data"])} {E(x["nome"])}</span></div>'
        for k, x in enumerate(cr.get("marcos", [])))

    linhas = []
    for m in mods:
        cor = cores.get(m["id"], "#64748b")
        barras = []
        for f in m["fases"]:
            a = (_dt.date.fromisoformat(f["inicio"]) - ini).days
            b = (_dt.date.fromisoformat(f["fim"]) - ini).days + 1
            titulo = f'{legenda.get(f["tipo"], f["tipo"])}: {_dbr(f["inicio"])} a {_dbr(f["fim"])} ({rot.get(f["status"], f["status"])})'
            if f.get("nota"):
                titulo += f'. {f["nota"]}'
            rotulo = f'<span>{E(legenda.get(f["tipo"], f["tipo"]))}</span>' if b - a >= 5 else ""
            barras.append(f'<div class="cr-barra cr-{f["tipo"]} cr-{f["status"]}" style="left:{pct(a)};width:{pct(b - a)}" title="{E(titulo)}">{rotulo}</div>')
        t = m.get("testes")
        prog = ""
        if t:
            p = round(t["conclusivos"] / t["planejados"] * 100) if t["planejados"] else 0
            prog = f'<div class="cr-prog" title="{t["conclusivos"]} de {t["planejados"]} casos conclusivos"><i style="width:{p}%;--cor:{cor}"></i></div><small>{t["conclusivos"]}/{t["planejados"]} casos</small>'
        href = f'documentacao/{m["id"]}/index.html'
        linhas.append(
            f'<div class="cr-linha"><div class="cr-rotulo"><a href="{href}" style="--cor:{cor}">{E(m["nome"])}</a><em>{E(m["situacao"])}</em>{prog}</div>'
            f'<div class="cr-trilha">{"".join(f"<i class=\"cr-fds-fundo\" style=\"left:{pct(k)};width:{pct(1)}\"></i>" for k, d in enumerate(dias) if d.weekday() >= 5)}'
            f'{f"<i class=\"cr-hoje-linha\" style=\"left:{pct((hoje - ini).days)}\"></i>" if ini <= hoje <= fim else ""}{"".join(barras)}</div></div>')

    # Números gerais
    com_t = [m for m in mods if m.get("testes")]
    planejados = sum(m["testes"]["planejados"] for m in com_t)
    conclusivos = sum(m["testes"]["conclusivos"] for m in com_t)
    alta_pend = sum(m["testes"]["alta_pendentes"] for m in com_t)
    fechados = sum(1 for m in com_t if m["situacao"].lower().startswith("fechado"))
    previstos = [_dt.date.fromisoformat(f["fim"]) for m in mods for f in m["fases"] if f["status"] != "feito"]
    termino = max(previstos) if previstos else max(datas)
    marcos_tab = "".join(f'<tr><td>{_dbr(x["data"])}/{_dt.date.fromisoformat(x["data"]).year}</td><td>{E(x["nome"])}</td><td><span class="cr-selo cr-{x["status"]}">{rot.get(x["status"], x["status"])}</span></td></tr>' for x in cr.get("marcos", []))

    # Detalhe por módulo
    det = []
    for m in mods:
        cor = cores.get(m["id"], "#64748b")
        t = m.get("testes")
        fases = "".join(
            f'<tr><td>{E(legenda.get(f["tipo"], f["tipo"]))}</td><td>{_dbr(f["inicio"])} a {_dbr(f["fim"])}</td>'
            f'<td><span class="cr-selo cr-{f["status"]}">{rot.get(f["status"], f["status"])}</span></td><td>{E(f.get("nota", ""))}</td></tr>'
            for f in m["fases"])
        tnum = ""
        if t:
            tnum = (f'<p class="cr-num"><strong>{t["conclusivos"]}</strong> de {t["planejados"]} casos com resultado · '
                    f'<strong>{t["alta_pendentes"]}</strong> de {t["alta"]} casos de prioridade Alta ainda por testar · '
                    f'{t["rodadas_feitas"]} rodada(s) feita(s)</p>' + (f'<p class="cr-nota">{E(t["nota"])}</p>' if t.get("nota") else ""))
        falta = "".join(f"<li>{E(x)}</li>" for x in m.get("falta", []))
        det.append(f'<details class="cr-det" id="cr-{m["id"]}" style="--cor:{cor}"><summary><span>{E(m["nome"])}</span><em>{E(m["situacao"])}</em></summary>'
                   f'<div class="cr-det-corpo">{tnum}<div class="tabela"><table><thead><tr><th>Fase</th><th>Período</th><th>Situação</th><th>Observação</th></tr></thead><tbody>{fases}</tbody></table></div>'
                   f'<h4>O que falta</h4><ul>{falta}</ul></div></details>')

    premissas = "".join(f"<li>{_inline(x)}</li>" for x in cr.get("premissas", []))
    leg = "".join(f'<span class="cr-leg cr-{k}">{E(v)}</span>' for k, v in legenda.items())
    raiz = ""
    return (cabecalho("Cronograma da homologação · iLabMedSys", raiz, "cronograma") + f"""
<main id="conteudo" class="cronograma">
  <section class="anv-faixa">
    <div class="anv-faixa-interna">
      <nav class="trilha" aria-label="Você está em"><a href="index.html">Início</a> › <span>Cronograma</span></nav>
      <h1>Cronograma da homologação</h1>
      <p>Onde cada módulo está, o que já foi testado e quanto falta para fechar. As datas futuras são previsão. Atualizado em {E(cr.get("atualizado", HOJE))}.</p>
    </div>
  </section>
  <div class="cr-conteudo">
    <div class="cr-numeros" aria-label="Números gerais">
      <div class="numero"><strong>{fechados}<small>/{len(com_t)}</small></strong><span>módulos fechados</span></div>
      <div class="numero"><strong>{conclusivos}<small>/{planejados}</small></strong><span>casos de teste com resultado</span></div>
      <div class="numero"><strong>{alta_pend}</strong><span>casos de prioridade Alta por testar</span></div>
      <div class="numero"><strong>{termino.day:02d}/{termino.month:02d}</strong><span>previsão de término ({termino.year})</span></div>
    </div>

    <section class="cr-sec">
      <h2>Linha do tempo</h2>
      <p class="cr-sub">Uma linha por módulo. Barra cheia: feito. Barra listrada: previsto. A linha vertical marca hoje. Passe o mouse sobre uma barra para ver o detalhe.</p>
      <div class="cr-legenda">{leg}<span class="cr-leg cr-leg-prev">previsto</span></div>
      <div class="cr-rolagem"><div class="cr-gantt" style="--n:{n}">
        <div class="cr-cab"><div class="cr-rotulo"></div><div class="cr-trilha cr-cab-meses">{"".join(meses)}</div></div>
        <div class="cr-cab"><div class="cr-rotulo"></div><div class="cr-trilha cr-cab-dias">{diasx}</div></div>
        {"".join(linhas)}
        <div class="cr-linha cr-marcos"><div class="cr-rotulo"><strong>Marcos</strong></div><div class="cr-trilha">{marcos_html}</div></div>
      </div></div>
    </section>

    <section class="cr-sec">
      <h2>Marcos</h2>
      <div class="tabela"><table><thead><tr><th>Data</th><th>Marco</th><th>Situação</th></tr></thead><tbody>{marcos_tab}</tbody></table></div>
    </section>

    <section class="cr-sec">
      <h2>Módulo a módulo</h2>
      <p class="cr-sub">Clique no módulo para ver as fases, os números dos testes e o que falta.</p>
      {"".join(det)}
    </section>

    <section class="cr-sec">
      <h2>Como a previsão foi feita</h2>
      <ul class="cr-premissas">{premissas}</ul>
    </section>
  </div>
</main>
""" + rodape(raiz))


def _inline(md):
    """Negrito e código do Markdown, só para frases curtas."""
    t = E(md)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    return t


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--origem", required=True, help="Pasta do repositório LabMedsys_homol")
    ap.add_argument("--destino", default=".", help="Pasta do repositório iLabPharma")
    ap.add_argument("--relatorio", help="Arquivo (fora do site) para listar o que foi retirado")
    ap.add_argument("--sem-seguranca", action="store_true", help="Volta ao comportamento antigo: retira do portal o conteúdo de segurança")
    ap.add_argument("--atualizar-metadados", action="store_true", help="Acrescenta ao arquivo de metadados da Biblioteca as linhas que faltam (não altera as existentes)")
    a = ap.parse_args()
    global SEGURANCA_PUBLICA
    SEGURANCA_PUBLICA = not a.sem_seguranca
    gerar(Path(a.origem).resolve(), Path(a.destino).resolve(), a.relatorio, a.atualizar_metadados)


if __name__ == "__main__":
    main()
