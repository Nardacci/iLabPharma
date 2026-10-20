"""Verifica que nenhuma URL já publicada deixou de existir e que os links internos do site continuam resolvendo.

Antes = os arquivos publicados no ramo base (por padrão origin/main). Depois = a pasta de trabalho atual.
Falha (código 1) se algum arquivo publicado antes sumiu, ou se um link interno aponta para um arquivo inexistente.

Uso: python3 ferramentas/verificar_urls.py [--base origin/main]
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

RAIZ = Path(__file__).resolve().parent.parent
PUBLICADOS = (".html", ".docx", ".jpg", ".jpeg", ".png", ".svg", ".webp", ".gif", ".css", ".js", ".json", ".ico", ".md")
IGNORAR = ("ferramentas/", ".git", "node_modules/", "README")


def arquivos_base(ref):
    saida = subprocess.run(["git", "-C", str(RAIZ), "ls-tree", "-r", "--name-only", ref], capture_output=True, text=True, check=True).stdout
    return {p for p in saida.splitlines() if p.endswith(PUBLICADOS) and not p.startswith(IGNORAR)}


def arquivos_atuais():
    return {str(p.relative_to(RAIZ)) for p in RAIZ.rglob("*") if p.is_file() and str(p.relative_to(RAIZ)).endswith(PUBLICADOS)
            and not str(p.relative_to(RAIZ)).startswith(IGNORAR) and ".git/" not in str(p)}


def links_quebrados(atuais):
    ruins = []
    padrao = re.compile(r'(?:href|src)="([^"#?][^"]*)"')
    for rel in sorted(a for a in atuais if a.endswith(".html")):
        base = (RAIZ / rel).parent
        texto = re.sub(r"<script\b.*?</script>", "", (RAIZ / rel).read_text(encoding="utf-8", errors="replace"), flags=re.S | re.I)
        for alvo in padrao.findall(texto):
            if alvo.startswith(("http:", "https:", "mailto:", "tel:", "data:", "javascript:", "//")):
                continue
            caminho = unquote(urlparse(alvo).path)
            if not caminho:
                continue
            destino = (base / caminho).resolve()
            if destino.is_dir():
                destino = destino / "index.html"
            if not destino.exists():
                ruins.append((rel, alvo))
    return ruins


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="origin/main")
    a = ap.parse_args()
    antes, depois = arquivos_base(a.base), arquivos_atuais()
    sumiram = sorted(antes - depois)
    novos = sorted(depois - antes)
    ruins = links_quebrados(depois)
    print(f"Antes ({a.base}): {len(antes)} arquivos publicados")
    print(f"Depois (pasta atual): {len(depois)} arquivos; {len(novos)} novos")
    print(f"Arquivos que existiam e sumiram: {len(sumiram)}")
    for s in sumiram[:30]:
        print("  SUMIU:", s)
    print(f"Links internos quebrados: {len(ruins)}")
    for r in ruins[:30]:
        print("  QUEBRADO:", r[0], "->", r[1])
    sys.exit(1 if (sumiram or ruins) else 0)


if __name__ == "__main__":
    main()
