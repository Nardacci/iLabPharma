"""Higiene do portal publicado: o que nunca pode sair no site.

Regras (decididas pelo responsável em 21/10/2026):
  R1  endereço IP privado (10.x, 172.16 a 31.x, 192.168.x), com http(s)://, porta e caminho  -> "[endereço omitido]"
  R2  a página "Usuários de teste" não entra no portal (ver o catálogo em gerar_portal.py)
  R5  logins de teste -> "[usuário de teste]"

Os logins NÃO ficam neste arquivo: são lidos, a cada geração, da fonte privada (LOGINS_FONTE, no repositório
da homologação). O código nunca imprime o valor encontrado, só o arquivo e a contagem.
"""
import io
import re
import zipfile
from pathlib import Path

OM_IP = "[endereço omitido]"
OM_LOGIN = "[usuário de teste]"
IPX = re.compile(r"(?:https?://)?(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})"
                 r"(?::\d+)?(?:/[^\s<>\"'`)\]]*)?")
LOGINS_FONTE = "homologacao/versao-nova/1.principal/execucao/2026-10-17-rodada-2/usuarios-de-teste.md"
PASTAS_PROIBIDAS = ("guia-do-responsavel", "prototipo-narrativa", "arquivo-ramos-publicos")

_logins = None   # regex compilado dos logins; None = ainda não carregado


def carregar(origem):
    """Lê os logins de teste da fonte privada. Devolve a quantidade (0 se a fonte não existe)."""
    global _logins
    arq = Path(origem) / LOGINS_FONTE
    nomes = []
    if arq.exists():
        linhas = arq.read_text(encoding="utf-8").splitlines()
        col = None
        for l in linhas:
            if not l.startswith("|"):
                col = None
                continue
            cel = [c.strip() for c in l.strip().strip("|").split("|")]
            if col is None and cel and cel[0].lower().startswith("login"):
                col = 0
                continue
            if col is not None and cel and not set(cel[0]) <= set("-: "):
                v = cel[0].strip("` ")
                if re.fullmatch(r"[A-Za-z0-9_.\-]{3,40}", v):
                    nomes.append(v)
    nomes = sorted(set(nomes), key=len, reverse=True)
    _logins = re.compile(r"(?<![\w.\-/])(?:" + "|".join(re.escape(n) for n in nomes) + r")(?![\w\-])", re.I) if nomes else None
    return len(nomes)


def redigir(texto):
    """R1 e R5 em texto simples (markdown, JSON, HTML)."""
    texto = IPX.sub(OM_IP, texto)
    if _logins is not None:
        texto = _logins.sub(OM_LOGIN, texto)
    return texto


def contar(texto):
    n_ip = len(IPX.findall(texto))
    n_lg = len(_logins.findall(texto)) if _logins is not None else 0
    return n_ip, n_lg


def copiar_word(origem, destino):
    """Copia um Word aplicando R1 e R5 ao texto interno. Devolve o nº de trocas."""
    trocas = 0
    buf = io.BytesIO()
    with zipfile.ZipFile(origem) as zi, zipfile.ZipFile(buf, "w") as zo:
        for it in zi.infolist():
            dados = zi.read(it.filename)
            if it.filename.endswith((".xml", ".rels")):
                t0 = dados.decode("utf-8")
                t1 = redigir(t0)
                if t1 != t0:
                    trocas += sum(contar(t0))
                    dados = t1.encode("utf-8")
            zo.writestr(it, dados, compress_type=it.compress_type)
    Path(destino).write_bytes(buf.getvalue())
    return trocas


def _texto_word(p):
    z = zipfile.ZipFile(p)
    xs = []
    for n in z.namelist():
        if n.endswith((".xml", ".rels")):
            x = z.read(n).decode("utf-8", "ignore")
            xs.append(x)
            xs.append(re.sub(r"<[^>]+>", "", x.replace("</w:p>", "\n")))
    return "\n".join(xs)


def verificar(destino):
    """Procura no portal gerado o que não pode sair. Devolve lista de (arquivo, o que, quantidade). Sem valores."""
    destino = Path(destino)
    achados = []
    for p in sorted(destino.rglob("*")):
        rel_partes = p.relative_to(destino).parts
        if not p.is_file() or ".git" in p.parts or rel_partes[0] in ("ferramentas", ".github"):
            continue
        rel = str(p.relative_to(destino))
        if any(part in PASTAS_PROIBIDAS for part in p.relative_to(destino).parts):
            achados.append((rel, "pasta que não pode ser publicada", 1))
            continue
        if p.suffix.lower() == ".docx":
            t = _texto_word(p)
        elif p.suffix.lower() in (".html", ".json", ".js", ".md", ".css", ".svg", ".csv", ".txt", ".yml"):
            t = p.read_text(encoding="utf-8", errors="ignore")
        else:
            continue
        n_ip, n_lg = contar(t)
        if n_ip:
            achados.append((rel, "endereço IP privado", n_ip))
        if n_lg:
            achados.append((rel, "login de teste", n_lg))
        if "Login (gravado" in t:
            achados.append((rel, "tabela de logins de teste", 1))
    return achados
