"""Auditoria dos artefatos da VERSÃO NOVA no portal (rodar depois de gerar_portal.py). Mostra, por módulo, o que está publicado e o que falta.
Decisão do responsável (17/11/2026): os artefatos do portal são atualizados a cada entrega dos robôs; esta tabela mostra se isso aconteceu.
Uso: python3 ferramentas/auditar_artefatos_novo.py <pasta do LabMedsys_homol>"""
import glob
import re
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]
MODS = {"principal": "1.principal", "estoque": "3.estoque", "controle-qualidade": "4.controle_qualidade",
        "garantia-qualidade": "5.garantia_qualidade", "controle-documentos": "6.controle_documento"}


def texto(f):
    t = Path(f).read_text(encoding="utf-8")
    m = re.search(r"<main.*?</main>", t, re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(0) if m else t))


def main():
    hom = Path(sys.argv[1]) / "homologacao" if len(sys.argv) > 1 else None
    print(f"{'Módulo':22} {'Páginas de tela':>15} {'Manual conferido':>17} {'Manual escrito':>15} {'Sem manual':>11} {'Manuais no git':>15} {'Fichas no git':>14} {'Páginas de erro':>16} {'Word Dossiê/Resumo':>19}")
    for mid, pasta in MODS.items():
        man = sorted(glob.glob(str(R / "documentacao/novo" / mid / "*-manual-do-usuario.html")))
        conf = escr = sem = 0
        for f in man:
            t = texto(f)
            if "Conferida por robô" in t:
                conf += 1
            elif "Manual escrito" in t:
                escr += 1
            else:
                sem += 1
        n_man = n_fic = "?"
        if hom:
            n_man = len(glob.glob(str(hom / "versao-nova" / pasta / "paginas/*/*/manual.md")))
            n_fic = len(glob.glob(str(hom / "versao-nova" / pasta / "defeitos/DV-*-N-*.md")))
        pag_erro = len(glob.glob(str(R / "erros-novo" / f"dv-{ {'principal':'pri','estoque':'est','controle-qualidade':'cq','garantia-qualidade':'gq','controle-documentos':'doc'}[mid] }-n-*.html")))
        words = len(glob.glob(str(R / "documentacao/arquivos" / mid / "*Versao Nova.docx")))
        print(f"{mid:22} {len(man):>15} {conf:>17} {escr:>15} {sem:>11} {str(n_man):>15} {str(n_fic):>14} {pag_erro:>16} {words:>19}")
    print("\nLeitura: 'Manual escrito' + 'Manual conferido' deve ser igual a 'Manuais no git'; 'Páginas de erro' deve ser igual a 'Fichas no git'; 'Sem manual' são telas do inventário sem manual da versão nova (provisórias ou ainda não testadas).")


if __name__ == "__main__":
    main()
