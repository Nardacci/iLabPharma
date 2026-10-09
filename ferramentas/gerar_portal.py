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
# Categorias: inicio (comece por aqui), fluxos, negocio, qualidade, tecnico, testes.
# ---------------------------------------------------------------------------------------------
CATEGORIAS = {
    "inicio": ("Comece por aqui", "Visão geral e resumos para quem quer entender rápido."),
    "fluxos": ("Fluxos do processo", "Como o trabalho anda no sistema, etapa por etapa, com fluxograma."),
    "negocio": ("Regras e uso", "Regras de negócio, telas e manual para quem usa o sistema."),
    "qualidade": ("Qualidade e ANVISA", "Conformidade com a RDC 658/2022, riscos e rastreabilidade."),
    "tecnico": ("Requisitos e dados", "Para a equipe de desenvolvimento da nova versão."),
    "testes": ("Testes", "Plano de testes, resultados e evidências."),
}

MODULOS = [
    {
        "id": "visao-geral", "nome": "Visão entre módulos", "icone": "◎", "cor": "#2563eb",
        "situacao": "Em andamento", "nivel": 2,
        "resumo": "Como os módulos se encadeiam, do recebimento de material à liberação do lote, e onde a corrente está quebrada. Telas repetidas entre módulos.",
        "docs": [
            ("transversal/02-mapa-do-processo-fabril.md", "Mapa do processo fabril", "inicio", "transversal/LabMedSys - Mapa do Processo Fabril.docx"),
            ("transversal/01-telas-repetidas.md", "Telas repetidas entre módulos", "tecnico", None),
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
        "situacao": "Fluxos prontos, testes pausados", "nivel": 3,
        "resumo": "Recebimento, quarentena, endereçamento, movimentação, atendimento à produção, devolução, remessa, inventário e kits. Dez fluxos documentados; testes de tela parados no Endereçamento, aguardando o DBA.",
        "docs": [
            ("3.estoque/00-reconhecimento.md", "Reconhecimento do módulo", "inicio", None),
            ("3.estoque/entregaveis/fonte/relatorio-de-testes.md", "Relatório de testes", "inicio", "3.estoque/entregaveis/LabMedSys - Modulo Estoque - Relatorio de Testes.docx"),
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
        ],
    },
    {
        "id": "garantia-qualidade", "nome": "Garantia da Qualidade", "icone": "◇", "cor": "#8b1e3f",
        "situacao": "Em análise", "nivel": 2,
        "resumo": "Desvios e CAPA, controle de mudanças, autoinspeção e auditoria, treinamento e assuntos regulatórios. Reconhecimento, mapa de conformidade com a RDC 658/2022 e primeiro fluxo prontos.",
        "docs": [
            ("5.garantia_qualidade/00-reconhecimento.md", "Reconhecimento do módulo", "inicio", None),
            ("5.garantia_qualidade/04-conformidade-regulatoria.md", "Conformidade com a RDC 658/2022", "qualidade", None),
            ("5.garantia_qualidade/fluxos/desvios-capa.md", "Desvios e CAPA", "fluxos", "5.garantia_qualidade/fluxos/LabMedSys - Modulo Garantia da Qualidade - Fluxo Desvios e CAPA.docx"),
        ],
    },
    {"id": "producao", "nome": "Produção", "icone": "⚙", "cor": "#667085", "situacao": "Não iniciado", "nivel": 0,
     "resumo": "Ordens de produção, pesagem e registros de fabricação.", "docs": []},
    {"id": "controle-qualidade", "nome": "Controle da Qualidade", "icone": "✧", "cor": "#667085", "situacao": "Não iniciado", "nivel": 0,
     "resumo": "Análises, especificações, liberação e reprovação de materiais e produtos.", "docs": []},
    {"id": "controle-documentos", "nome": "Controle de Documentos", "icone": "▤", "cor": "#667085", "situacao": "Não iniciado", "nivel": 0,
     "resumo": "Elaboração, revisão, aprovação e distribuição de documentos.", "docs": []},
    {"id": "comercial", "nome": "Comercial", "icone": "◈", "cor": "#667085", "situacao": "Não iniciado", "nivel": 0,
     "resumo": "Pedidos, faturamento e distribuição.", "docs": []},
    {"id": "rastreabilidade", "nome": "Rastreabilidade", "icone": "⟲", "cor": "#667085", "situacao": "Não iniciado", "nivel": 0,
     "resumo": "Serialização e rastreio dos lotes no mercado.", "docs": []},
]

PUBLICOS = [
    ("Diretoria", "Situação de cada módulo e decisões.", [("principal", "resumo-executivo"), ("visao-geral", "mapa-do-processo-fabril"), ("estoque", "relatorio-de-testes")]),
    ("Usuários das áreas", "Como cada processo funciona nas telas.", [("principal", "manual-do-usuario"), ("estoque", "recebimento-e-quarentena-conferencia"), ("garantia-qualidade", "desvios-e-capa")]),
    ("Garantia da Qualidade", "Conformidade, riscos e rastreabilidade.", [("garantia-qualidade", "conformidade-com-a-rdc-658-2022"), ("principal", "conformidade-regulatoria"), ("principal", "dossie-de-homologacao")]),
    ("Desenvolvimento", "Requisitos e dados para a nova versão.", [("principal", "analise-de-requisitos"), ("principal", "modelo-de-dados-e-integracoes"), ("visao-geral", "telas-repetidas-entre-modulos")]),
]

# ---------------------------------------------------------------------------------------------
# Limpeza de segurança
# ---------------------------------------------------------------------------------------------
RE_TITULO_SEG = re.compile(r"seguran[çc]a|achados? de seguran", re.I)
TITULOS_PERMITIDOS = re.compile(r"usu[áa]rios, perfis e permiss|nivel_seguranca", re.I)
RE_CALLOUT_SEG = re.compile(r"seguran[çc]a|confidencial|verifica[çc][ãa]o de acesso", re.I)
RE_LINHA_SEG = re.compile(
    r"SEG-[A-Z]{2,4}-\d+|03-achados-de-seguranca|achados de seguran[çc]a|inje[çc][ãa]o de SQL|SQL injection|"
    r"criptografia revers[íi]vel|chave fixa|credenciais|senhas? (?:podem ser |s[ãa]o )?recuper[áa]ve|"
    r"senhas podem ser recuperadas|digitando o endere[çc]o|sem senha em outro navegador|token de acesso|"
    r"token no endere[çc]o|sem entrar no sistema|janela an[ôo]nima|Nenhum filtro obrigat[óo]rio|"
    r"Quem conhece o endere[çc]o|abre(?:m)? telas? .* pelo endere[çc]o|endere[çc]o da p[áa]gina|\btokens?\b|\bhash\b|localStorage",
    re.I)


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
            return f'<figure><a href="{novo}" target="_blank" rel="noopener"><img src="{novo}" alt="{E(alt)}" loading="lazy"></a><figcaption>{E(alt)}</figcaption></figure>'
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
def cabecalho(titulo, raiz, ativo=""):
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{E(titulo)}</title>
<meta name="description" content="iLabMedSys: documentação da homologação do LabMedSys, por módulo.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{raiz}portal/portal.css">
<script>try{{var t=localStorage.getItem('ilms-tema');if(t)document.documentElement.dataset.theme=t;}}catch(e){{}}</script>
</head>
<body data-raiz="{raiz}">
<header class="topo">
  <a class="marca" href="{raiz}index.html" aria-label="iLabMedSys, página inicial"><img src="{raiz}assets/ilabmedsys-logo.svg" alt="iLabMedSys"></a>
  <nav class="topo-nav" aria-label="Principal">
    <a href="{raiz}index.html#modulos"{' aria-current="page"' if ativo == 'modulos' else ''}>Módulos</a>
    <a href="{raiz}index.html#publicos">Por público</a>
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
              "Em análise": "selo-andamento", "Em andamento": "selo-andamento"}.get(situacao, "selo-neutro")
    return f'<span class="selo {classe}">{E(situacao)}</span>'


def barra(nivel):
    etapas = ["Reconhecimento", "Fluxos", "Testes", "Entregáveis"]
    itens = "".join(f'<li class="{"feito" if i < nivel else ""}">{e}</li>' for i, e in enumerate(etapas))
    return f'<ol class="etapas" aria-label="Andamento: {nivel} de 4 etapas">{itens}</ol>'


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

    (destino / "index.html").write_text(pagina_inicial(), encoding="utf-8")
    (destino / "portal/busca.json").write_text(json.dumps(busca, ensure_ascii=False), encoding="utf-8")

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

    blocos = []
    if fluxos:
        cards = "".join(
            f'<a class="fluxo-card" href="{p["slug"]}.html">'
            + (f'<img src="{p["fluxograma"]}" alt="" loading="lazy">' if p["fluxograma"] else '<div class="fluxo-sem-img">Fluxo descrito em texto</div>')
            + f'<span>{E(p["titulo"])}</span></a>' for p in fluxos)
        blocos.append(f'<section class="secao"><h2>{CATEGORIAS["fluxos"][0]}</h2><p class="secao-desc">{CATEGORIAS["fluxos"][1]}</p><div class="fluxos">{cards}</div></section>')
    for cat, (nome_cat, desc) in CATEGORIAS.items():
        if cat == "fluxos":
            continue
        itens = [p for p in mod["paginas"] if p["cat"] == cat]
        if not itens:
            continue
        cards = "".join(
            f'<a class="doc-card" href="{p["slug"]}.html"><span class="doc-card-titulo">{E(p["titulo"])}</span>'
            f'<span class="doc-card-meta">{"Word disponível" if p["word"] else "Leitura no portal"}</span></a>' for p in itens)
        blocos.append(f'<section class="secao"><h2>{E(nome_cat)}</h2><p class="secao-desc">{E(desc)}</p><div class="doc-cards">{cards}</div></section>')

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
  {''.join(blocos)}
</main>
""" + rodape(raiz))


def pagina_inicial():
    raiz = ""
    cards = []
    for mod in MODULOS:
        if mod["id"] == "visao-geral":
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
    modulos_com_doc = sum(1 for m in MODULOS if m["paginas"] and m["id"] != "visao-geral")
    total_modulos = len([m for m in MODULOS if m["id"] != "visao-geral"])

    return (cabecalho("iLabMedSys · Documentação do sistema", raiz) + f"""
<main id="conteudo">
  <section class="hero">
    <div class="hero-texto">
      <p class="sobretitulo">LabMedSys agora é iLabMedSys</p>
      <h1>Tudo o que sabemos sobre o sistema, em um só lugar.</h1>
      <p class="hero-desc">A homologação do sistema de gestão da fábrica, módulo por módulo: o que existe e funciona, como cada processo anda nas telas, o que a ANVISA exige e onde o sistema falha.</p>
      <div class="hero-acoes">
        <a class="botao botao-grande" href="#modulos">Explorar os módulos</a>
        <a class="botao botao-grande botao-secundario" href="apresentacao.html">Ver a apresentação ↗</a>
      </div>
    </div>
    <div class="hero-numeros" aria-label="Números da documentação">
      <div class="numero"><strong>{modulos_com_doc}<small>/{total_modulos}</small></strong><span>módulos com documentação</span></div>
      <div class="numero"><strong>{total_docs}</strong><span>documentos publicados</span></div>
      <div class="numero"><strong>{total_fluxos}</strong><span>fluxos documentados</span></div>
    </div>
  </section>

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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--origem", required=True, help="Pasta do repositório LabMedsys_homol")
    ap.add_argument("--destino", default=".", help="Pasta do repositório iLabPharma")
    ap.add_argument("--relatorio", help="Arquivo (fora do site) para listar o que foi retirado")
    a = ap.parse_args()
    gerar(Path(a.origem).resolve(), Path(a.destino).resolve(), a.relatorio)


if __name__ == "__main__":
    main()
