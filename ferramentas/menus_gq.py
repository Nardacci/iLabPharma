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
    {"pasta": "assuntos-regulatorios", "grupo": "Assuntos Regulatórios", "prefixo_word": "LabMedSys - Modulo Garantia da Qualidade - Assuntos Regulatórios"},
    {"pasta": "mudancas", "grupo": "Controle de Mudanças", "prefixo_word": "LabMedSys - Modulo Garantia da Qualidade - Controle de Mudanças"},
    {"pasta": "autoinspecao", "grupo": "Autoinspeção e Auditoria", "prefixo_word": "LabMedSys - Modulo Garantia da Qualidade - Autoinspeção e Auditoria"},
]


def entradas(hom):
    base = Path(hom) / "5.garantia_qualidade"
    out = []
    for m in MENUS:
        raiz = base / m["pasta"]
        telas = raiz / "telas"
        if not (raiz / "paginas").exists():
            continue
        rel = f"5.garantia_qualidade/{m['pasta']}"
        for nome_arq, titulo, word in (("00-entenda-o-menu", f"{m['grupo']}: entenda o menu", "Entenda o Menu"),
                                       ("00-visao-geral", f"{m['grupo']}: visão geral", "Visao Geral")):
            if (telas / f"{nome_arq}.md").exists():
                out.append((f"{rel}/telas/{nome_arq}.md", titulo, "negocio", f"{rel}/telas/{m['prefixo_word']} - {word}.docx",
                            {"desvios": True, "intro": True, "menu": m["grupo"]}))
        resumos = json.loads((telas / "resumos.json").read_text(encoding="utf-8")) if (telas / "resumos.json").exists() else {}
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
                            f"{rel}/paginas/{pasta.name}/{m['prefixo_word']} - Tela {n:02d} {nome} - {rot}.docx",
                            {"desvios": True, "grupo": m["grupo"], "tela": nome, "rotulo": rot, "tela_n": n, "aba": aba, "resumo": resumos.get(f"{n:02d}", "")}))
    return out
