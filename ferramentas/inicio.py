"""Página inicial do portal (index.html): um menu que chama cada parte, inclusive o dashboard (a página principal de antes, agora dashboard.html).

Os endereços antigos continuam valendo: os links `index.html#modulos` e `index.html#publicos` (que estão em todas as páginas) são redirecionados
para o dashboard pelo próprio script desta página."""
import html

E = html.escape
ITENS = [
    ("Dashboard", "dashboard.html", "A situação de cada módulo, o que precisa de você agora e as portas de entrada do portal (a página principal de antes).", True),
    ("Mapa dos processos", "processos.html", "A cadeia de um sistema industrial de medicamentos em blocos clicáveis: do fornecedor à distribuição, com a norma e os fluxos.", False),
    ("Erros", "erros-novo.html", "Todos os erros encontrados na versão nova, módulo a módulo, com passo a passo, evidências e Word.", False),
    ("Módulos", "dashboard.html#modulos", "Os nove módulos, cada um com legado, novo e ideal.", False),
    ("Biblioteca", "biblioteca.html", "Todos os documentos do portal, por tipo, público e módulo.", False),
    ("Devs/QA", "telas.html", "As telas de cada módulo, com análise, manual, fluxos, regras e erros.", False),
    ("Por público", "dashboard.html#publicos", "O que ler primeiro, conforme quem você é: diretoria, Qualidade, desenvolvimento.", False),
    ("ANVISA", "anvisa.html", "As normas (RDC 658/2022 e Guia 33/2020) e como cada módulo as atende.", False),
    ("Cronograma", "cronograma.html", "As fases de cada módulo, o que foi feito e o que falta.", False),
    ("Apresentação", "apresentacao.html", "A apresentação visual do projeto.", False),
]
CSS = """
.ini{max-width:1100px;margin:0 auto;padding:1.5rem 1.25rem}
.ini h1{margin:.2rem 0 .3rem}
.ini-grade{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem;margin:1.5rem 0}
.ini-card{display:block;padding:1.1rem 1.2rem;border:1px solid var(--borda,#d9dee6);border-radius:12px;color:inherit;text-decoration:none;min-height:7.5rem}
.ini-card:hover,.ini-card:focus-visible{border-color:#f57c00;box-shadow:0 0 0 3px color-mix(in srgb,#f57c00 25%,transparent)}
.ini-card b{display:block;font-size:1.15rem;margin-bottom:.35rem}
.ini-card span{opacity:.8;font-size:.92rem;line-height:1.4}
.ini-card.principal{border-width:2px;border-color:#f57c00}
"""
JS = """
(function(){var h=location.hash;if(h.length>1){location.replace('dashboard.html'+h);}})();
"""


def pagina(cabecalho, rodape):
    cards = "".join(f'<a class="ini-card{" principal" if destaque else ""}" href="{E(href)}"><b>{E(nome)}</b><span>{E(desc)}</span></a>' for nome, href, desc, destaque in ITENS)
    corpo = (f'<main class="ini" id="conteudo"><h1>iLabMedSys</h1>'
             f'<p>Documentação da homologação do LabMedSys: o sistema entregue (legado), a versão nova e o ideal, módulo a módulo. Escolha por onde começar.</p>'
             f'<nav class="ini-grade" aria-label="Menu do portal">{cards}</nav></main>')
    return (cabecalho("iLabMedSys: início", "").replace("</head>", f"<style>{CSS}</style><script>{JS}</script></head>") + corpo + rodape(""))
