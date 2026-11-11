"""Página avulsa "Mapa dos processos" (processos.html): a cadeia de um sistema industrial de medicamentos em blocos clicáveis.

Fonte: homologacao/transversal/mapa-processos.json (áreas, processos, ligações quebradas). Cada bloco é colorido pela situação da corrente
(leitura da análise pelo código) e mostra, ao clicar, o resumo, a situação no legado e na versão nova, a norma, as ligações quebradas e os
links para os fluxos já documentados (os links só entram quando a página do fluxo existe no portal). Não altera nenhuma outra página."""
import html
import json
from pathlib import Path

import higiene

E = html.escape
CORRENTE = {"quebra": ("Ligação quebrada apontada", "q"), "sem-quebra": ("Existe, sem quebra apontada", "s"), "prototipo": ("Só protótipo", "p"),
            "nao-existe": ("Não existe no sistema", "n"), "nao-mapeado": ("Ainda não mapeado", "m")}
NOVO = {"tela": "Testada pelas telas", "api": "Testada só pela API (telas provisórias)", "parcial": "Parcial: parte testada, parte provisória",
        "provisoria": "Provisória (por construir)", "nao-testado": "Ainda não testada"}
CSS = """
.mp{max-width:1200px;margin:0 auto;padding:1.5rem 1.25rem}
.mp h1{margin:.2rem 0 .4rem}
.mp-leg{display:flex;flex-wrap:wrap;gap:.5rem 1.1rem;margin:.8rem 0 1.4rem;font-size:.9rem}
.mp-leg span{display:inline-flex;align-items:center;gap:.4rem}
.mp-leg i{width:.9rem;height:.9rem;border-radius:3px;display:inline-block;border:2px solid var(--c)}
.mp-area{margin:1.2rem 0}
.mp-area h2{font-size:1.05rem;margin:0 0 .15rem}
.mp-area p{margin:0 0 .5rem;opacity:.75;font-size:.88rem}
.mp-fila{display:flex;flex-wrap:wrap;align-items:stretch;gap:.35rem}
.mp-seta{align-self:center;opacity:.5;font-size:1.1rem}
.mp-bloco{all:unset;box-sizing:border-box;cursor:pointer;width:200px;padding:.6rem .7rem;border:2px solid var(--c);border-left-width:7px;border-radius:10px;background:var(--fundo,transparent);font-size:.9rem;line-height:1.25}
.mp-bloco:hover,.mp-bloco:focus-visible{box-shadow:0 0 0 3px var(--c)}
.mp-bloco[aria-pressed=true]{background:color-mix(in srgb,var(--c) 14%,transparent)}
.mp-bloco b{display:block;margin-bottom:.25rem}
.mp-bloco small{display:block;opacity:.8;font-size:.78rem}
.c-q{--c:#b3261e}.c-s{--c:#2e9b4f}.c-p{--c:#b26a00}.c-n{--c:#5b6472}.c-m{--c:#8a94a6}
.c-n,.c-m{border-style:dashed}
.mp-painel{margin:1.6rem 0;padding:1.1rem 1.3rem;border:2px solid var(--c,#8a94a6);border-radius:12px}
.mp-painel h2{margin:.1rem 0 .4rem}
.mp-painel h3{margin:1rem 0 .3rem;font-size:1rem}
.mp-lig{margin:.4rem 0;padding:.5rem .7rem;border-left:5px solid #b3261e;background:color-mix(in srgb,#b3261e 8%,transparent);border-radius:6px;font-size:.92rem}
.mp-lig.m{border-left-color:#b26a00;background:color-mix(in srgb,#b26a00 8%,transparent)}
.mp-vazio{opacity:.7}
.mp-fluxos{display:flex;flex-wrap:wrap;gap:.5rem;margin:.3rem 0}
"""
JS = """
(function(){
var d=JSON.parse(document.getElementById('mp-dados').textContent),p=document.getElementById('mp-painel');
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function abrir(id,rolar){var x=d.processos.filter(function(a){return a.id===id})[0];if(!x)return;
document.querySelectorAll('.mp-bloco').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.id===id?'true':'false');});
var h='<h2>'+esc(x.nome)+'</h2><p>'+esc(x.resumo)+'</p>';
h+='<p><b>Situação da corrente (legado):</b> '+esc(x.corrente_txt)+'<br><b>Versão nova:</b> '+esc(x.novo_txt)+(x.nota_novo?' — '+esc(x.nota_novo):'')+'</p>';
if(x.modulos.length)h+='<p><b>Módulos:</b> '+x.modulos.map(esc).join(', ')+'</p>';
if(x.norma)h+='<p><b>Norma:</b> '+esc(x.norma)+'</p>';
h+='<h3>Ligações quebradas</h3>';
if(x.lig.length)h+=x.lig.map(function(l){return '<div class="mp-lig'+(l.gravidade==='Alta'?'':' m')+'"><b>'+esc(l.nome)+'</b> ('+esc(l.gravidade)+'): '+esc(l.texto)+'<br><i>Exigência: '+esc(l.norma)+'</i></div>';}).join('');
else h+='<p class="mp-vazio">Nenhuma ligação quebrada apontada na análise para este processo.</p>';
h+='<h3>Fluxos já documentados</h3>';
if(x.fluxos.length)h+='<div class="mp-fluxos">'+x.fluxos.map(function(f){return '<a class="botao" href="'+esc(f.href)+'">'+esc(f.titulo)+'</a>';}).join('')+'</div>';
else h+='<p class="mp-vazio">Ainda não há fluxo documentado para este processo.</p>';
p.innerHTML=h;p.hidden=false;p.className='mp-painel c-'+x.cod;history.replaceState(null,'','#'+id);if(rolar)p.scrollIntoView({behavior:'smooth',block:'nearest'});}
document.querySelectorAll('.mp-bloco').forEach(function(b){b.addEventListener('click',function(){abrir(b.dataset.id,true);});});
if(location.hash.length>1)abrir(location.hash.slice(1),false);
})();
"""


def pagina(hom, destino, cabecalho, rodape, href_fluxo):
    """href_fluxo(modulo_id, titulo) -> endereço da página do fluxo no portal, ou None se não existir."""
    d = json.loads(higiene.redigir((Path(hom) / "transversal/mapa-processos.json").read_text(encoding="utf-8")))
    lig = d["ligacoes"]
    dados = []
    for p in d["processos"]:
        txt, cod = CORRENTE[p["corrente"]]
        fl = []
        for f in p["fluxos"]:
            h = href_fluxo(f["modulo"], f["titulo"])
            if h:
                fl.append({"titulo": f["titulo"], "href": h})
        dados.append({**{k: p[k] for k in ("id", "nome", "resumo", "modulos", "norma", "nota_novo")}, "corrente_txt": txt, "cod": cod, "novo_txt": NOVO[p["novo"]],
                      "lig": [lig[i] for i in p["ligacoes"]], "fluxos": fl})
    por_id = {x["id"]: x for x in dados}
    areas = []
    for a in d["areas"]:
        blocos = [p for p in d["processos"] if p["area"] == a["id"]]
        fila = '<span class="mp-seta" aria-hidden="true">→</span>'.join(
            f'<button type="button" class="mp-bloco c-{por_id[p["id"]]["cod"]}" data-id="{E(p["id"])}" aria-pressed="false"><b>{E(p["nome"])}</b>'
            f'<small>{E(por_id[p["id"]]["corrente_txt"])}</small><small>Novo: {E(por_id[p["id"]]["novo_txt"])}</small></button>' for p in blocos)
        areas.append(f'<section class="mp-area"><h2>{E(a["nome"])}</h2><p>{E(a["descricao"])}</p><div class="mp-fila">{fila}</div></section>')
    leg = "".join(f'<span><i style="--c:var(--lc-{c})"></i>{E(t)}</span>' for t, c in CORRENTE.values())
    css = CSS + ":root{--lc-q:#b3261e;--lc-s:#2e9b4f;--lc-p:#b26a00;--lc-n:#5b6472;--lc-m:#8a94a6}"
    corpo = (f'<main class="mp" id="conteudo"><h1>{E(d["titulo"])}</h1>'
             f'<p>A cadeia de um sistema industrial de medicamentos, do fornecedor à distribuição, com o sistema da qualidade que a sustenta. Clique em um bloco para ver o que ele é, o que a norma exige, onde a corrente está quebrada e abrir o fluxo já documentado.</p>'
             f'<p class="mp-vazio">{E(d["fonte"])}</p><div class="mp-leg" aria-label="Legenda">{leg}</div>{"".join(areas)}'
             f'<section id="mp-painel" class="mp-painel" aria-live="polite" hidden></section>'
             f'<script type="application/json" id="mp-dados">{json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")}</script></main>')
    (Path(destino) / "processos.html").write_text(
        cabecalho("Mapa dos processos", "").replace("</head>", f"<style>{css}</style></head>") + corpo + rodape("").replace("</body>", f"<script>{JS}</script></body>"), encoding="utf-8")
    return len(dados), sum(len(x["fluxos"]) for x in dados)
