"""Catálogo dos menus da Garantia da Qualidade documentados tela a tela (Assuntos Regulatórios, Controle de Mudanças e Autoinspeção e Auditoria).

Lê homologacao/5.garantia_qualidade/<pasta>/paginas/NN-<slug>/<aba>.md, que a ferramenta dividir_telas.py gera a partir de telas/NN-*.md,
e monta as entradas do catálogo do portal no mesmo formato das do Controle de Desvios (que continuam escritas à mão em gerar_portal.py).
O resumo de cada tela vem de telas/resumos.json ({"01": "uma frase"}); sem ele, a página aparece sem a frase.
Só cataloga o que existe: se a pasta não existe, devolve lista vazia."""
import json
import re
from pathlib import Path

ABAS = [("analise", "Análise"), ("manual", "Manual do usuário"), ("fluxos", "Fluxos"), ("regras", "Regras de negócio"), ("anvisa", "Anvisa")]
MENUS = [
    {"modulo": "estoque", "base": "3.estoque", "pasta": "menu-estoque", "grupo": "Menu Estoque", "prefixo_word": "LabMedSys - Modulo Estoque - Menu Estoque"},
    {"modulo": "estoque", "base": "3.estoque", "pasta": "menu-cadastros", "grupo": "Menu Cadastros", "prefixo_word": "LabMedSys - Modulo Estoque - Menu Cadastros"},
    {"modulo": "estoque", "base": "3.estoque", "pasta": "menu-inventario", "grupo": "Menu Inventário", "prefixo_word": "LabMedSys - Modulo Estoque - Menu Inventário"},
    {"modulo": "estoque", "base": "3.estoque", "pasta": "menu-gestao-analitica", "grupo": "Menu Gestão Analítica", "prefixo_word": "LabMedSys - Modulo Estoque - Menu Gestão Analítica"},
    {"modulo": "estoque", "base": "3.estoque", "pasta": "menu-relatorios", "grupo": "Menu Relatórios", "prefixo_word": "LabMedSys - Modulo Estoque - Menu Relatórios"},
    {"modulo": "estoque", "base": "3.estoque", "pasta": "menu-kits", "grupo": "Menu Kits", "prefixo_word": "LabMedSys - Modulo Estoque - Menu Kits"},
    {"modulo": "estoque", "base": "3.estoque", "pasta": "menu-regulatorio", "grupo": "Menu Regulatório", "prefixo_word": "LabMedSys - Modulo Estoque - Menu Regulatório"},
    {"modulo": "principal", "base": "1.principal", "pasta": "menu-acesso", "grupo": "Acesso ao sistema", "prefixo_word": "LabMedSys - Modulo Principal - Acesso ao sistema"},
    {"modulo": "principal", "base": "1.principal", "pasta": "menu-administracao", "grupo": "Administração", "prefixo_word": "LabMedSys - Modulo Principal - Administração"},
    {"modulo": "principal", "base": "1.principal", "pasta": "menu-cadastros", "grupo": "Cadastros e tabelas de apoio", "prefixo_word": "LabMedSys - Modulo Principal - Cadastros e tabelas de apoio"},
    {"modulo": "controle-qualidade", "base": "4.controle_qualidade", "pasta": "menu-solicitacao", "grupo": "Solicitação de Análise", "prefixo_word": "LabMedSys - Modulo Controle da Qualidade - Solicitação de Análise"},
    {"modulo": "controle-qualidade", "base": "4.controle_qualidade", "pasta": "menu-amostragem", "grupo": "Amostragem", "prefixo_word": "LabMedSys - Modulo Controle da Qualidade - Amostragem"},
    {"modulo": "controle-qualidade", "base": "4.controle_qualidade", "pasta": "menu-analise-laudo", "grupo": "Análise e Laudo", "prefixo_word": "LabMedSys - Modulo Controle da Qualidade - Análise e Laudo"},
    {"modulo": "controle-qualidade", "base": "4.controle_qualidade", "pasta": "menu-apoio-regulatorio", "grupo": "Tabelas de Apoio e Regulatório", "prefixo_word": "LabMedSys - Modulo Controle da Qualidade - Tabelas de Apoio e Regulatório"},
    {"modulo": "controle-qualidade", "base": "4.controle_qualidade", "pasta": "fora-do-menu", "grupo": "Fora do menu", "prefixo_word": "LabMedSys - Modulo Controle da Qualidade - Fora do menu"},
    {"pasta": "treinamento", "grupo": "Treinamento Técnico", "prefixo_word": "LabMedSys - Modulo Garantia da Qualidade - Treinamento Técnico"},
    {"pasta": "configuracao", "grupo": "Configuração", "prefixo_word": "LabMedSys - Modulo Garantia da Qualidade - Configuração"},
    {"pasta": "assuntos-regulatorios", "grupo": "Assuntos Regulatórios", "prefixo_word": "LabMedSys - Modulo Garantia da Qualidade - Assuntos Regulatórios"},
    {"pasta": "mudancas", "grupo": "Controle de Mudanças", "prefixo_word": "LabMedSys - Modulo Garantia da Qualidade - Controle de Mudanças"},
    {"pasta": "autoinspecao", "grupo": "Autoinspeção e Auditoria", "prefixo_word": "LabMedSys - Modulo Garantia da Qualidade - Autoinspeção e Auditoria"},
]


def entradas(hom, modulo="garantia-qualidade"):
    """Entradas do catálogo dos menus tela a tela do módulo (por padrão, a Garantia da Qualidade)."""
    out = []
    for m in MENUS:
        if m.get("modulo", "garantia-qualidade") != modulo:
            continue
        base = Path(hom) / m.get("base", "5.garantia_qualidade")
        raiz = base / m["pasta"]
        telas = raiz / "telas"
        if not (raiz / "paginas").exists():
            continue
        rel = f"{m.get('base', '5.garantia_qualidade')}/{m['pasta']}"
        for nome_arq, titulo, word in (("00-entenda-o-menu", f"{m['grupo']}: entenda o menu", "Entenda o Menu"),
                                       ("00-visao-geral", f"{m['grupo']}: visão geral", "Visao Geral")):
            if (telas / f"{nome_arq}.md").exists():
                out.append((f"{rel}/telas/{nome_arq}.md", titulo, "negocio", f"{rel}/telas/{m['prefixo_word']} - {word}.docx",
                            {"desvios": True, "intro": True, "menu": m["grupo"]}))
        resumos = json.loads((telas / "resumos.json").read_text(encoding="utf-8")) if (telas / "resumos.json").exists() else {}
        ordem = {f'{o["n"]:02d}': o for o in json.loads((telas / "ordem.json").read_text(encoding="utf-8"))} if (telas / "ordem.json").exists() else {}
        for pasta in sorted((raiz / "paginas").iterdir()):
            mm = re.match(r"^(\d\d)-", pasta.name)
            if not mm or not pasta.is_dir():
                continue
            n = int(mm.group(1))
            fonte = (telas / f"{pasta.name}.md").read_text(encoding="utf-8")
            nome = re.search(r"^## (.+)$", fonte, re.M).group(1).strip()
            for aba, rot in ABAS:
                if not (pasta / f"{aba}.md").exists():
                    continue
                out.append((f"{rel}/paginas/{pasta.name}/{aba}.md", f"{nome}: {rot}", "negocio",
                            f"{rel}/paginas/{pasta.name}/{m['prefixo_word']} - Tela {n:02d} {nome.replace('/', '-')} - {rot}.docx",
                            {"desvios": True, "grupo": m["grupo"], "tela": nome, "rotulo": rot, "tela_n": n, "aba": aba, "resumo": resumos.get(f"{n:02d}", ""), "fluxo": ordem.get(f"{n:02d}", {}).get("fluxo")}))
    return out
