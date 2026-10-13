#!/usr/bin/env python3
"""Gera o portal iLabMedSys (documentação da homologação do LabMedSys) a partir do repositório LabMedsys_homol.

O que faz:
  1. Lê os documentos em Markdown de <origem>/homologacao, conforme o CATÁLOGO abaixo.
  2. Retira o conteúdo de segurança (o site é público): arquivos 03-achados-de-seguranca, seções com
     "segurança" no título, blocos confidenciais, linhas com achados SEG-XXX-nn e frases que descrevem
     como explorar uma falha. Tudo o que foi retirado vai para um relatório local (fora do site).
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

HOJE = datetime.date.today().strftime("%d/%m/%Y")

# ---------------------------------------------------------------------------------------------
# Catálogo: o que entra no portal. "arq" é relativo a homologacao/. "word" é o .docx original.
# Categorias: inicio (comece por aqui), ideal (como deve ser), defeitos (para os devs), fluxos, negocio, qualidade, tecnico, testes.
# ---------------------------------------------------------------------------------------------
CATEGORIAS = {
    "inicio": ("Comece por aqui", "Visão geral e resumos para quem quer entender rápido."),
    "ideal": ("O ideal", "Como o módulo deve trabalhar para atender à ANVISA: funções, comportamento, integrações com os outros módulos e papéis. Não descreve o legado; mostra o que manter, corrigir e construir."),
    "fluxos": ("Fluxos do processo", "Como o trabalho anda no sistema, etapa por etapa, com fluxograma."),
    "negocio": ("Regras e uso", "Regras de negócio, telas e manual para quem usa o sistema."),
    "qualidade": ("Qualidade e ANVISA", "Conformidade com a RDC 658/2022, riscos e rastreabilidade."),
    "tecnico": ("Requisitos e dados", "Para a equipe de desenvolvimento da nova versão."),
    "defeitos": ("Defeitos para correção", "Para a equipe de desenvolvimento: cada defeito encontrado nos testes, com o passo a passo para reproduzir, as capturas, o trecho do código e uma sugestão de correção."),
    "testes": ("Testes", "Plano de testes, resultados e evidências."),
}

# Áreas que não são módulos do sistema: ficam fora dos cartões e das contagens de módulos.
ESPECIAIS = {"visao-geral"}

MODULOS = [
    {
        "id": "visao-geral", "nome": "Visão entre módulos", "icone": "◎", "cor": "#2563eb",
        "situacao": "Em andamento", "nivel": 2,
        "resumo": "Como os módulos se encadeiam, do recebimento de material à liberação do lote, e onde a corrente está quebrada. Telas repetidas entre módulos.",
        "docs": [
            ("transversal/04-mapa-de-integracoes.md", "Mapa de integrações entre os módulos", "inicio", "transversal/LabMedSys - Mapa de Integracoes entre Modulos.docx"),
            ("transversal/03-diagnostico-conformidade.md", "Diagnóstico de conformidade com a ANVISA", "inicio", "transversal/LabMedSys - Diagnostico de Conformidade ANVISA.docx"),
            ("transversal/02-mapa-do-processo-fabril.md", "Mapa do processo fabril", "inicio", "transversal/LabMedSys - Mapa do Processo Fabril.docx"),
            ("transversal/01-telas-repetidas.md", "Telas, tabelas e código repetidos entre os módulos", "tecnico", "transversal/LabMedSys - Telas Tabelas e Codigo Repetidos.docx"),
            ("modelo-ideal/01-qualidade-entre-modulos.md", "Qualidade entre os módulos: situação do lote e travas", "ideal", "modelo-ideal/entregaveis/LabMedSys - Modelo Ideal - Qualidade entre os Modulos.docx"),
        ],
    },
    {
        "id": "principal", "nome": "Principal", "icone": "⌂", "cor": "#f57c00",
        "situacao": "Homologado: não apto", "nivel": 4,
        "resumo": "Porta de entrada dos nove módulos: login, usuários, perfis, permissões, cadastros gerais e a base da trilha de auditoria. Analisado, testado em duas rodadas (78 casos) e com todos os entregáveis.",
        "docs": [
            ("1.principal/entregaveis/fonte/resumo-executivo.md", "Resumo executivo", "inicio", "1.principal/entregaveis/LabMedSys - Modulo Principal - Resumo Executivo.docx"),
            ("1.principal/entregaveis/fonte/dossie-de-homologacao.md", "Dossiê de homologação", "inicio", "1.principal/entregaveis/LabMedSys - Modulo Principal - Dossie de Homologacao.docx"),
            ("1.principal/11-inventario-de-telas.md", "Inventário de telas e situação", "inicio", None),
            ("1.principal/entregaveis/fonte/regras-de-negocio.md", "Regras de negócio", "negocio", "1.principal/entregaveis/LabMedSys - Modulo Principal - Regras de Negocio.docx"),
            ("1.principal/entregaveis/fonte/manual-do-usuario.md", "Manual do usuário", "negocio", "1.principal/entregaveis/LabMedSys - Modulo Principal - Manual do Usuario.docx"),
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
        ],
    },
    {
        "id": "estoque", "nome": "Estoque", "icone": "▦", "cor": "#2e9b4f",
        "situacao": "Em testes", "nivel": 3,
        "resumo": "Recebimento, quarentena, endereçamento, movimentação, atendimento à produção, devolução, remessa, inventário e kits. Dez fluxos documentados. Testes de tela: 5 rodadas (07, 08 e 12 a 13/10/2026), 42 desvios. Confirmado na tela: o Endereçamento mostra sucesso e não grava, e o lote não chega à quarentena por esse caminho (a causa está no banco e aguarda o DBA); pelas entradas de material (produção e outras) o lote entra em quarentena e abre a análise no CQ; o laudo reprovado bloqueia o lote, mas o Estoque só sabe quando alguém atualiza a análise; a avaliação do fornecedor não qualifica nem bloqueia ninguém; a entrada de produto acabado aceita lote inventado e vencido; o histórico do lote não mostra usuário, análise nem laudo. Pacote de documentos: inventário das 98 telas do menu, conformidade (14 temas), risco (24 riscos, 18 de prioridade alta), plano de testes (162 casos, 69 executados) modelo de dados e matriz de permissões, mais \"O ideal\": o Estoque como dono da situação única do lote. Os defeitos para correção chegam a 30.",
        "docs": [
            ("3.estoque/00-reconhecimento.md", "Reconhecimento do módulo", "inicio", None),
            ("3.estoque/ideal/est-ideal.md", "O Estoque ideal", "ideal", "3.estoque/ideal/LabMedSys - Modulo Estoque - O Ideal.docx"),
            ("3.estoque/ideal/est-entre-modulos.md", "O Estoque entre os módulos: as travas", "ideal", "3.estoque/ideal/LabMedSys - Modulo Estoque - Entre os Modulos.docx"),
            ("3.estoque/11-inventario-de-telas.md", "Inventário de telas e situação", "inicio", None),
            ("3.estoque/04-conformidade-regulatoria.md", "Conformidade com a RDC 658/2022", "qualidade", None),
            ("3.estoque/07-analise-de-risco.md", "Análise de risco", "qualidade", None),
            ("3.estoque/06-modelo-de-dados.md", "Modelo de dados e integrações", "tecnico", None),
            ("3.estoque/02-matriz-de-permissoes.md", "Matriz de permissões", "negocio", None),
            ("3.estoque/08-plano-de-testes.md", "Plano de testes", "testes", None),
            ("3.estoque/entregaveis/fonte/relatorio-de-testes.md", "Relatório de testes", "inicio", "3.estoque/entregaveis/LabMedSys - Modulo Estoque - Relatorio de Testes.docx"),
            ("3.estoque/entregaveis/fonte/regras-de-negocio.md", "Regras de negócio", "negocio", "3.estoque/entregaveis/LabMedSys - Modulo Estoque - Regras de Negocio.docx"),
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
        "situacao": "Em testes", "nivel": 2,
        "resumo": "Desvios e CAPA, controle de mudanças, autoinspeção e auditoria, treinamento e assuntos regulatórios. Reconhecimento, mapa de conformidade com a RDC 658/2022, os cinco fluxos (desvios e CAPA, controle de mudanças, autoinspeção, treinamento e assuntos regulatórios), as regras de negócio, o inventário das 67 telas, a matriz de permissões, o modelo de dados, a análise de risco e o plano de testes prontos. Testes de tela: rodada 1 em 12/10/2026, com 12 casos de prioridade Alta (1 passou, 10 falharam, 1 bloqueado). Confirmados na tela: plano corretivo aprovado com ação pendente; mudança liberada sem parecer das áreas e aprovada apesar de área que não aceitou; plano de mudança finalizado sem a ação executada; cancelamento do desvio e aprovação final do produto fora do histórico. Ponto bom: a data de abertura do desvio é a do servidor. O efeito de um desvio sobre o lote não pôde ser testado (a busca de produto no desvio não devolve nada no ambiente).",
        "docs": [
            ("5.garantia_qualidade/00-reconhecimento.md", "Reconhecimento do módulo", "inicio", None),
            ("5.garantia_qualidade/ideal/gq-ideal.md", "A Garantia da Qualidade ideal", "ideal", "5.garantia_qualidade/ideal/LabMedSys - Modulo Garantia da Qualidade - O Ideal.docx"),
            ("5.garantia_qualidade/ideal/gq-entre-modulos.md", "A Garantia da Qualidade entre os módulos: as travas", "ideal", "5.garantia_qualidade/ideal/LabMedSys - Modulo Garantia da Qualidade - Entre os Modulos.docx"),
            ("5.garantia_qualidade/11-inventario-de-telas.md", "Inventário de telas e situação", "inicio", None),
            ("5.garantia_qualidade/01-regras-de-negocio.md", "Regras de negócio", "negocio", None),
            ("5.garantia_qualidade/02-matriz-de-permissoes.md", "Matriz de permissões", "negocio", None),
            ("5.garantia_qualidade/08-plano-de-testes.md", "Plano de testes", "testes", None),
            ("5.garantia_qualidade/roteiros/controle-mudancas.md", "Roteiro de execução: Controle de mudanças (passo a passo)", "testes", "5.garantia_qualidade/roteiros/LabMedSys - Modulo Garantia da Qualidade - Roteiro de Testes Controle de Mudancas.docx"),
            ("5.garantia_qualidade/roteiros/desvios-capa.md", "Roteiro de execução: Desvios e CAPA (passo a passo)", "testes", "5.garantia_qualidade/roteiros/LabMedSys - Modulo Garantia da Qualidade - Roteiro de Testes Desvios e CAPA.docx"),
            ("5.garantia_qualidade/roteiros/autoinspecao-auditoria.md", "Roteiro de execução: Autoinspeção e auditoria (passo a passo)", "testes", "5.garantia_qualidade/roteiros/LabMedSys - Modulo Garantia da Qualidade - Roteiro de Testes Autoinspecao e Auditoria.docx"),
            ("5.garantia_qualidade/04-conformidade-regulatoria.md", "Conformidade com a RDC 658/2022", "qualidade", None),
            ("5.garantia_qualidade/07-analise-de-risco.md", "Análise de risco", "qualidade", None),
            ("5.garantia_qualidade/06-modelo-de-dados.md", "Modelo de dados e integrações", "tecnico", None),
            ("5.garantia_qualidade/fluxos/desvios-capa.md", "Desvios e CAPA", "fluxos", "5.garantia_qualidade/fluxos/LabMedSys - Modulo Garantia da Qualidade - Fluxo Desvios e CAPA.docx"),
            ("5.garantia_qualidade/fluxos/autoinspecao-auditoria.md", "Autoinspeção e auditoria", "fluxos", "5.garantia_qualidade/fluxos/LabMedSys - Modulo Garantia da Qualidade - Fluxo Autoinspecao e Auditoria.docx"),
            ("5.garantia_qualidade/fluxos/treinamento.md", "Treinamento técnico", "fluxos", "5.garantia_qualidade/fluxos/LabMedSys - Modulo Garantia da Qualidade - Fluxo Treinamento.docx"),
            ("5.garantia_qualidade/fluxos/assuntos-regulatorios.md", "Assuntos regulatórios", "fluxos", "5.garantia_qualidade/fluxos/LabMedSys - Modulo Garantia da Qualidade - Fluxo Assuntos Regulatorios.docx"),
            ("5.garantia_qualidade/fluxos/controle-mudancas.md", "Controle de mudanças", "fluxos", "5.garantia_qualidade/fluxos/LabMedSys - Modulo Garantia da Qualidade - Fluxo Controle de Mudancas.docx"),
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
    {"id": "controle-qualidade", "nome": "Controle da Qualidade", "icone": "✧", "cor": "#2e9b4f", "situacao": "Pronto para testes", "nivel": 2,
     "resumo": "Solicitação de análise, amostragem, análise, laudo, etiqueta e estabilidade. Reconhecimento e conformidade com a RDC 658/2022 feitos: 25 telas (22 com lógica, 3 protótipos); dos 16 temas da norma, 8 atendidos em parte e 8 não atendidos. Os quatro fluxos prontos (solicitação ao laudo, regras de amostragem e de análise, estabilidade, água e ambiente), as 119 regras de negócio, o inventário das telas, as permissões, o modelo de dados, a análise de risco e o plano de testes (61 casos). Análise pelo código concluída.",
     "docs": [
         ("4.controle_qualidade/00-reconhecimento.md", "Reconhecimento do módulo", "inicio", None),
         ("4.controle_qualidade/ideal/cq-ideal.md", "O Controle da Qualidade ideal", "ideal", "4.controle_qualidade/ideal/LabMedSys - Modulo Controle da Qualidade - O Ideal.docx"),
         ("4.controle_qualidade/ideal/cq-entre-modulos.md", "O Controle da Qualidade entre os módulos: as travas", "ideal", "4.controle_qualidade/ideal/LabMedSys - Modulo Controle da Qualidade - Entre os Modulos.docx"),
         ("4.controle_qualidade/11-inventario-de-telas.md", "Inventário de telas e situação", "inicio", None),
         ("4.controle_qualidade/01-regras-de-negocio.md", "Regras de negócio", "negocio", None),
         ("4.controle_qualidade/02-matriz-de-permissoes.md", "Matriz de permissões", "negocio", None),
         ("4.controle_qualidade/08-plano-de-testes.md", "Plano de testes", "testes", None),
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
    ("Diretoria", "Situação de cada módulo e decisões.", [("visao-geral", "diagnostico-de-conformidade-com-a-anvisa"), ("visao-geral", "mapa-de-integracoes-entre-os-modulos"), ("principal", "resumo-executivo"), ("visao-geral", "mapa-do-processo-fabril"), ("estoque", "relatorio-de-testes")]),
    ("Usuários das áreas", "Como cada processo funciona nas telas.", [("principal", "manual-do-usuario"), ("estoque", "recebimento-e-quarentena-conferencia"), ("garantia-qualidade", "desvios-e-capa")]),
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
    r"sem nenhuma fun[çc][ãa]o d[oa] [^|]{0,30}abrir|sem acesso [^|]{0,40}pelo endere[çc]o",
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


def limpar(md, nome, retirado):
    """Retira o conteúdo de segurança. Devolve o texto limpo; anota o que saiu em `retirado`."""
    linhas = md.splitlines()
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
        saida.append(linha)
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
    <a href="{raiz}index.html#diretoria">Diretoria</a>
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
  <div>Os documentos descrevem o sistema legado entregue pelo fornecedor. Achados de segurança não são publicados aqui.</div>
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

def gerar(origem, destino, relatorio):
    conv = Conversor(origem, destino)
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
        for arq, titulo, cat, word in mod["docs"]:
            fonte = hom / arq
            original = ler(fonte)
            antes = len(retirado)
            limpo = limpar(original, arq, retirado)
            foi_limpo = len(retirado) > antes
            corpo, toc = conv.converter(limpo, mod["id"], tirar_h1=True)
            s = slug(titulo)
            pagina = {"titulo": titulo, "slug": s, "cat": cat, "arq": arq, "toc": toc, "corpo": corpo,
                      "contagem": contar(limpo), "word": None, "fluxograma": None, "limpo": foi_limpo}
            m = re.search(r'<img src="(\.\./img/[^"]+fluxograma[^"]*)"', corpo)
            if m:
                pagina["fluxograma"] = m.group(1)
            # Word
            if word and (hom / word).exists():
                pasta = doc_dir / "arquivos" / mod["id"]
                pasta.mkdir(parents=True, exist_ok=True)
                nome = Path(word).name
                alvo = pasta / nome
                if foi_limpo:
                    tmp = destino / f".tmp-{s}.md"
                    tmp.write_text(limpo, encoding="utf-8")
                    titulo_doc = f"Fluxo – {titulo}" if cat == "fluxos" else titulo
                    r = subprocess.run([sys.executable, str(gerar_docx), "--modelo", str(conv.modelo_docx), "--fonte", str(tmp),
                                        "--saida", str(alvo), "--titulo", titulo_doc, "--data", HOJE,
                                        "--descricao", "Versão publicada no portal, sem os achados de segurança",
                                        "--modulo", f"Módulo {mod['nome']}"], capture_output=True, text=True)
                    tmp.unlink()
                    if r.returncode != 0:
                        print(r.stderr, file=sys.stderr)
                        raise SystemExit(f"Falha ao gerar o Word de {arq}")
                else:
                    shutil.copy2(hom / word, alvo)
                pagina["word"] = f"../arquivos/{mod['id']}/{nome}"
            mod["paginas"].append(pagina)
            texto = re.sub(r"<[^>]+>", " ", corpo)
            texto = re.sub(r"\s+", " ", html.unescape(texto))
            titulos = [t["name"] for t in toc] + [c["name"] for t in toc for c in t["children"]]
            busca.append({"t": titulo, "m": mod["nome"], "u": f"documentacao/{mod['id']}/{s}.html",
                          "h": titulos[:40], "x": texto[:6000]})

    # Páginas de documento
    for mod in MODULOS:
        if not mod["paginas"]:
            continue
        pasta = doc_dir / mod["id"]
        pasta.mkdir(parents=True, exist_ok=True)
        for p in mod["paginas"]:
            (pasta / f"{p['slug']}.html").write_text(pagina_documento(mod, p), encoding="utf-8")
        (pasta / "index.html").write_text(pagina_modulo(mod), encoding="utf-8")

    (destino / "index.html").write_text(pagina_inicial(origem), encoding="utf-8")
    (destino / "anvisa.html").write_text(pagina_anvisa(origem, busca), encoding="utf-8")
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


def nav_lateral(mod, atual):
    grupos = []
    for cat, (nome_cat, _) in CATEGORIAS.items():
        itens = [p for p in mod["paginas"] if p["cat"] == cat]
        if not itens:
            continue
        li = "".join(f'<li><a href="{p["slug"]}.html"{" aria-current=page" if p is atual else ""}>{E(p["titulo"])}</a></li>' for p in itens)
        grupos.append(f'<div class="lat-grupo"><div class="lat-titulo">{E(nome_cat)}</div><ul>{li}</ul></div>')
    return "".join(grupos)


def toc_html(toc):
    if not toc:
        return ""
    itens = []
    for t in toc:
        filhos = "".join(f'<li class="sub"><a href="#{c["id"]}">{E(html.unescape(c["name"]))}</a></li>' for c in t["children"][:12])
        itens.append(f'<li><a href="#{t["id"]}">{E(html.unescape(t["name"]))}</a></li>{filhos}')
    return f'<nav class="toc" aria-label="Nesta página"><div class="toc-titulo">Nesta página</div><ul>{"".join(itens)}</ul></nav>'


def pagina_documento(mod, p):
    raiz = "../../"
    cat_nome = CATEGORIAS[p["cat"]][0]
    word = f'<a class="botao" href="{p["word"]}" download>⤓ Baixar em Word</a>' if p["word"] else ""
    aviso = '<p class="nota">Versão publicada sem os trechos de segurança, que têm distribuição restrita.</p>' if p["limpo"] else ""
    return (cabecalho(f"{p['titulo']} · {mod['nome']} · iLabMedSys", raiz) + f"""
<div class="doc-layout">
  <aside class="lateral" aria-label="Documentos do módulo">
    <a class="lat-modulo" href="index.html" style="--cor:{mod['cor']}"><span class="icone">{mod['icone']}</span>{E(mod['nome'])}</a>
    {nav_lateral(mod, p)}
  </aside>
  <main class="doc" id="conteudo">
    <nav class="trilha" aria-label="Você está em"><a href="{raiz}index.html">Início</a> › <a href="index.html">{E(mod['nome'])}</a> › <span>{E(cat_nome)}</span></nav>
    <header class="doc-cabecalho">
      <h1>{E(p['titulo'])}</h1>
      <div class="doc-acoes">{word}<button class="botao botao-secundario" type="button" onclick="window.print()">⎙ Imprimir</button></div>
      {aviso}
    </header>
    <article class="texto">
{p['corpo']}
    </article>
  </main>
  {toc_html(p['toc'])}
</div>
""" + rodape(raiz))


def pagina_modulo(mod):
    raiz = "../../"
    soma = {"casos": 0, "regras": 0, "requisitos": 0, "desvios": 0}
    for p in mod["paginas"]:
        for k in soma:
            soma[k] = max(soma[k], p["contagem"][k]) if k != "regras" else soma[k] + p["contagem"][k]
    fluxos = [p for p in mod["paginas"] if p["cat"] == "fluxos"]
    numeros = [(len(mod["paginas"]), "documentos"), (len(fluxos), "fluxos documentados")]
    if soma["casos"]:
        numeros.append((soma["casos"], "casos de teste (maior plano)"))
    if soma["requisitos"]:
        numeros.append((soma["requisitos"], "requisitos para a nova versão"))
    if soma["desvios"]:
        numeros.append((soma["desvios"], "desvios registrados nos testes"))
    num_html = "".join(f'<div class="numero"><strong>{n}</strong><span>{E(r)}</span></div>' for n, r in numeros)

    blocos, submenu = [], []
    for cat, (nome_cat, desc) in CATEGORIAS.items():
        itens = [p for p in mod["paginas"] if p["cat"] == cat]
        if not itens:
            continue
        if cat == "fluxos":
            cards = "".join(
                f'<a class="fluxo-card" href="{p["slug"]}.html">'
                + (f'<img src="{p["fluxograma"]}" alt="" loading="lazy">' if p["fluxograma"] else '<div class="fluxo-sem-img">Fluxo descrito em texto</div>')
                + f'<span>{E(p["titulo"])}</span></a>' for p in itens)
            grade = f'<div class="fluxos">{cards}</div>'
        else:
            cards = "".join(
                f'<a class="doc-card" href="{p["slug"]}.html"><span class="doc-card-titulo">{E(p["titulo"])}</span>'
                f'<span class="doc-card-meta">{"Word disponível" if p["word"] else "Leitura no portal"}</span></a>' for p in itens)
            grade = f'<div class="doc-cards">{cards}</div>'
        classe = "secao secao-ideal" if cat == "ideal" else "secao"
        blocos.append(f'<section class="{classe}" id="sec-{cat}"><h2>{E(nome_cat)}</h2><p class="secao-desc">{E(desc)}</p>{grade}</section>')
        submenu.append(f'<a href="#sec-{cat}"{" class=\"submenu-ideal\"" if cat == "ideal" else ""}>{E(nome_cat)}</a>')
    submenu_html = f'<nav class="submenu" aria-label="Seções do módulo">{"".join(submenu)}</nav>' if len(submenu) > 1 else ""

    return (cabecalho(f"{mod['nome']} · iLabMedSys", raiz, "modulos") + f"""
<main class="pagina-modulo" id="conteudo">
  <nav class="trilha" aria-label="Você está em"><a href="{raiz}index.html">Início</a> › <span>{E(mod['nome'])}</span></nav>
  <header class="mod-cabecalho" style="--cor:{mod['cor']}">
    <div class="mod-icone" aria-hidden="true">{mod['icone']}</div>
    <div>
      <h1>{E(mod['nome'])}</h1>
      <p>{E(mod['resumo'])}</p>
      <div class="mod-status">{selo(mod['situacao'])}{barra(mod['nivel'])}</div>
    </div>
  </header>
  <div class="numeros">{num_html}</div>
  {submenu_html}
  {''.join(blocos)}
</main>
""" + rodape(raiz))


def pagina_inicial(origem):
    raiz = ""
    cards = []
    for mod in MODULOS:
        if mod["id"] in ESPECIAIS:
            continue
        n = len(mod["paginas"])
        inner = (f'<div class="mc-topo"><span class="mc-icone" style="--cor:{mod["cor"]}">{mod["icone"]}</span>{selo(mod["situacao"])}</div>'
                 f'<h3>{E(mod["nome"])}</h3><p>{E(mod["resumo"])}</p>{barra(mod["nivel"])}'
                 f'<div class="mc-rodape">{f"{n} documentos" if n else "Ainda sem documentação"}</div>')
        if n:
            cards.append(f'<a class="modulo-card" href="documentacao/{mod["id"]}/index.html">{inner}</a>')
        else:
            cards.append(f'<div class="modulo-card modulo-futuro" aria-disabled="true">{inner}</div>')

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
    total_fluxos = sum(1 for m in MODULOS for p in m["paginas"] if p["cat"] == "fluxos")
    modulos_com_doc = sum(1 for m in MODULOS if m["paginas"] and m["id"] not in ESPECIAIS)
    total_modulos = len([m for m in MODULOS if m["id"] not in ESPECIAIS])

    diretoria = bloco_diretoria(origem)
    return (cabecalho("iLabMedSys · Documentação do sistema", raiz) + f"""
<main id="conteudo">
  <section class="hero">
    <div class="hero-texto">
      <p class="sobretitulo">LabMedSys agora é iLabMedSys</p>
      <h1>Tudo o que sabemos sobre o sistema, em um só lugar.</h1>
      <p class="hero-desc">A homologação do sistema de gestão da fábrica, módulo por módulo: o que existe e funciona, como cada processo anda nas telas, o que a ANVISA exige e onde o sistema falha.</p>
      <div class="hero-acoes">
        <a class="botao botao-grande" href="#diretoria">Diagnóstico para a diretoria</a>
        <a class="botao botao-grande botao-secundario" href="#modulos">Explorar os módulos</a>
        <a class="botao botao-grande botao-secundario" href="apresentacao.html">Ver a apresentação ↗</a>
      </div>
    </div>
    <div class="hero-numeros" aria-label="Números da documentação">
      <div class="numero"><strong>{modulos_com_doc}<small>/{total_modulos}</small></strong><span>módulos com documentação</span></div>
      <div class="numero"><strong>{total_docs}</strong><span>documentos publicados</span></div>
      <div class="numero"><strong>{total_fluxos}</strong><span>fluxos documentados</span></div>
    </div>
  </section>

  {diretoria}

  <section class="secao" id="como-ler">
    <h2>Como a homologação avança</h2>
    <p class="secao-desc">Cada módulo passa pelas mesmas quatro etapas. A barra em cada cartão mostra onde ele está.</p>
    <ol class="jornada">
      <li><strong>Reconhecimento</strong><span>Telas, tabelas e integrações levantadas no código.</span></li>
      <li><strong>Fluxos</strong><span>Cada processo descrito etapa por etapa, com regras e fluxograma.</span></li>
      <li><strong>Testes</strong><span>Casos executados nas telas, com evidências e desvios.</span></li>
      <li><strong>Entregáveis</strong><span>Regras, manual, requisitos, dossiê e resumo para a diretoria.</span></li>
    </ol>
  </section>

  <section class="secao" id="modulos">
    <h2>Módulos</h2>
    <p class="secao-desc">Escolha um módulo para ver seus fluxos, regras, testes e documentos para baixar.</p>
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
    cr = json.loads(arq.read_text(encoding="utf-8"))
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
    a = ap.parse_args()
    gerar(Path(a.origem).resolve(), Path(a.destino).resolve(), a.relatorio)


if __name__ == "__main__":
    main()
