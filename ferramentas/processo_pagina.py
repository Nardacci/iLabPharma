"""Página interativa de um processo (processo-<id>.html), a partir de homologacao/transversal/processos/<id>.json.

O processo aparece como etapas em sequência, por fase, coloridas pela situação na versão nova. Ao clicar em uma etapa: como deve ser (ideal), regras e
norma (o que o sistema precisa garantir e o que o código novo faz hoje), telas, situação e erros da versão nova (com link para a ficha do erro e as
evidências), perguntas ao desenvolvimento e, recolhido, como era no legado. As referências a arquivo e linha do código não entram. Não altera outra página."""
import html
import json
import re
from pathlib import Path

import higiene

E = html.escape
STATUS = {"tela": ("Testada pelas telas", "t"), "api": ("Testada só pela API (telas provisórias)", "a"), "parcial": ("Parcial: parte testada, parte provisória", "p"),
          "provisoria": ("Provisória (por construir)", "v"), "nao-testado": ("Ainda não testada", "n")}
CSS = """
.pp{max-width:1200px;margin:0 auto;padding:1.5rem 1.25rem}
.pp-leg{display:flex;flex-wrap:wrap;gap:.5rem 1.1rem;margin:.8rem 0 1.2rem;font-size:.9rem}
.pp-leg span{display:inline-flex;align-items:center;gap:.4rem}
.pp-leg i{width:.9rem;height:.9rem;border-radius:3px;display:inline-block;border:2px solid var(--c)}
.pp-fase{margin:1.2rem 0}.pp-fase h2{font-size:1.05rem;margin:0 0 .5rem}
.pp-fila{display:flex;flex-wrap:wrap;align-items:stretch;gap:.35rem}
.pp-seta{align-self:center;opacity:.5;font-size:1.1rem}
.pp-et{all:unset;box-sizing:border-box;cursor:pointer;width:210px;padding:.6rem .7rem;border:2px solid var(--c);border-left-width:7px;border-radius:10px;font-size:.9rem;line-height:1.25}
.pp-et:hover,.pp-et:focus-visible{box-shadow:0 0 0 3px var(--c)}
.pp-et[aria-pressed=true]{background:color-mix(in srgb,var(--c) 14%,transparent)}
.pp-et b{display:block;margin-bottom:.2rem}.pp-et small{display:block;opacity:.8;font-size:.78rem}
.c-t{--c:#2e9b4f}.c-a{--c:#1f6aa5}.c-p{--c:#b26a00}.c-v{--c:#5b6472}.c-n{--c:#8a94a6;}.c-n{border-style:dashed}
.pp-painel{margin:1.6rem 0;padding:1.1rem 1.3rem;border:2px solid var(--c,#8a94a6);border-radius:12px}
.pp-painel h2{margin:.1rem 0 .3rem}.pp-painel h3{margin:1.1rem 0 .3rem;font-size:1rem}
.pp-tab{width:100%;border-collapse:collapse;font-size:.92rem}
.pp-tab th,.pp-tab td{padding:.4rem .55rem;border-bottom:1px solid var(--borda,#d9dee6);text-align:left;vertical-align:top}
.pp-cl{white-space:nowrap;font-weight:600}
.pp-lista{margin:.2rem 0;padding-left:1.2rem}
.pp-vazio{opacity:.7}
.pp-voltar{margin:.3rem 0 .6rem}
.pp-trilha{margin:.3rem 0 .6rem;font-size:.92rem}
.pp-linha{display:flex;flex-wrap:wrap;align-items:center;gap:.35rem;margin:.6rem 0}
.pp-pilha{display:flex;flex-direction:column;gap:.35rem}
.pp-param{width:100%;max-width:720px}
.pp-dec{border-style:dashed;border-radius:24px}
.pp-dec b::before{content:"◇ ";}
.pp-abre{display:block;margin-top:.3rem;font-weight:600;color:#f57c00}
a.pp-et{text-decoration:none;color:inherit}
.pp-res{width:210px;padding:.6rem .7rem;border:2px dashed #2e9b4f;border-radius:10px;font-size:.9rem;line-height:1.3}
.pp-res b{display:block;margin-bottom:.2rem}
.pp-saida{margin:.2rem 0}
"""
JS = """
(function(){
var d=JSON.parse(document.getElementById('pp-dados').textContent),p=document.getElementById('pp-painel');
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function lista(a){return a.length?'<ul class="pp-lista">'+a.map(function(x){return '<li>'+x+'</li>';}).join('')+'</ul>':'';}
function abrir(id,rolar){var x=d.etapas.filter(function(a){return a.id===id})[0];if(!x)return;
document.querySelectorAll('.pp-et').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.id===id?'true':'false');});
var h='<h2>'+esc(x.nome)+'</h2><p><b>Quem:</b> '+esc(x.quem)+'</p>';
h+='<h3>Como deve ser (ideal)</h3><p>'+esc(x.ideal)+'</p>';
h+='<h3>Regras e norma</h3>';
if(x.regras.length){h+='<div class="tabela"><table class="pp-tab"><thead><tr><th>O que o sistema precisa garantir</th><th>O que o código novo faz hoje</th><th>Situação</th></tr></thead><tbody>'+x.regras.map(function(r){return '<tr><td>'+esc(r.ideal)+'</td><td>'+esc(r.hoje)+'</td><td class="pp-cl">'+esc(r.classe)+'</td></tr>';}).join('')+'</tbody></table></div>';}
else h+='<p class="pp-vazio">Nenhuma regra específica levantada para esta etapa.</p>';
h+=x.norma?'<p><b>Norma:</b> '+esc(x.norma)+'</p>':'<p class="pp-vazio">Norma a definir com a Qualidade.</p>';
if(x.saidas&&x.saidas.length)h+='<h3>Saídas</h3>'+lista(x.saidas.map(function(o){return '<b>'+esc(o.rotulo)+'</b> → '+esc(o.vai);}));
if(x.link_roteiro)h+='<p><a class="botao" href="'+esc(x.link_roteiro.href)+'">Ver o roteiro: '+esc(x.link_roteiro.titulo.replace('Roteiro de execução: ',''))+'</a></p>';
if(x.telas.length)h+='<h3>Telas</h3>'+lista(x.telas.map(esc));
h+='<h3>Versão nova hoje</h3><p><b>'+esc(x.status_txt)+'.</b> '+esc(x.nota_novo)+'</p>';
if(x.fichas.length)h+='<p><b>Erros encontrados:</b></p>'+lista(x.fichas.map(function(f){return '<a href="'+esc(f.href)+'">'+esc(f.id)+'</a> ('+esc(f.grav)+'): '+esc(f.titulo);}));
if(x.perguntas.length)h+='<h3>Perguntas ao desenvolvimento</h3>'+lista(x.perguntas.map(esc));
if(x.legado.length)h+='<details><summary>Como era no legado</summary>'+lista(x.legado.map(esc))+'</details>';
p.innerHTML=h;p.hidden=false;p.className='pp-painel c-'+x.cod;history.replaceState(null,'','#'+id);if(rolar)p.scrollIntoView({behavior:'smooth',block:'nearest'});}
document.querySelectorAll('.pp-et').forEach(function(b){b.addEventListener('click',function(){abrir(b.dataset.id,true);});});
if(location.hash.length>1)abrir(location.hash.slice(1),false);
})();
"""


def _perguntas(hom):
    arq = Path(hom) / "versao-nova/3.estoque/verificacao-codigo/perguntas.md"
    out = {}
    if arq.exists():
        for l in arq.read_text(encoding="utf-8").splitlines():
            m = re.match(r"(\d+)\.\s+\*\*(.+?)\*\*", l)
            if m:
                out[int(m.group(1))] = m.group(2).strip()
    return out


def _bloco_dados(e, fichas, perg):
    txt, cod = STATUS[e["status_novo"]]
    return {**{k: e.get(k, v) for k, v in (("id", ""), ("nome", ""), ("quem", ""), ("ideal", ""), ("regras", []), ("norma", ""), ("telas", []), ("nota_novo", ""), ("legado", []), ("saidas", []))},
            "status_txt": txt, "cod": cod,
            "fichas": [{"id": i, "titulo": fichas[i]["titulo"], "grav": fichas[i]["grav"], "href": f"erros-novo/{i.lower()}.html"} for i in e.get("fichas", []) if i in fichas],
            "perguntas": [f"{n}. {perg[n]}" for n in e.get("perguntas", []) if n in perg]}


def pagina(hom, destino, arq_json, cabecalho, rodape, fichas, href_fluxo=None, mapa=None):
    """fichas: {id: {titulo, grav}}; href_fluxo(modulo, título) -> endereço do roteiro no portal; mapa: dados do mapa dos processos (para "Sobre este processo")."""
    d = json.loads(higiene.redigir(Path(arq_json).read_text(encoding="utf-8")))
    perg = _perguntas(hom)
    todas = [d["parametrizacao"]] + d["etapas"]
    dados = {"etapas": [_bloco_dados(e, fichas, perg) for e in todas]}
    lr = d["parametrizacao"].get("link_roteiro")
    if lr and href_fluxo and href_fluxo(lr["modulo"], lr["titulo"]):
        dados["etapas"][0]["link_roteiro"] = {"titulo": lr["titulo"], "href": href_fluxo(lr["modulo"], lr["titulo"])}
    por = {x["id"]: x for x in dados["etapas"]}

    def card(e):
        x = por[e["id"]]
        if e.get("abre"):
            return (f'<a class="pp-et c-{x["cod"]}" href="processo-{E(e["abre"])}.html"><b>{E(e["nome"])}</b><small>{E(e["quem"])}</small><small>{E(x["status_txt"])}</small>'
                    f'<span class="pp-abre">↳ abre o fluxo</span></a>')
        cls = " pp-dec" if e.get("tipo") == "decisao" else ""
        return (f'<button type="button" class="pp-et c-{x["cod"]}{cls}" data-id="{E(e["id"])}" aria-pressed="false"><b>{E(e["nome"])}</b>'
                f'<small>{E(e["quem"])}</small><small>{E(x["status_txt"])}</small></button>')

    seta = '<span class="pp-seta" aria-hidden="true">→</span>'
    entradas = [e for e in d["etapas"] if e.get("grupo") == "entrada"]
    fluxo = [e for e in d["etapas"] if e.get("grupo") == "fluxo"]
    ini = (f'<div class="pp-pilha">{"".join(card(e) for e in entradas)}</div>{seta}' if entradas else "")
    linha = ini + seta.join(card(e) for e in fluxo) + seta + f'<div class="pp-res"><b>Resultado</b>{E(d["resultado"])}</div>'
    trilha = '<a href="processos.html">Mapa dos processos</a>' + (f' › <a href="processo-{E(d["pai"]["id"])}.html">{E(d["pai"]["nome"])}</a>' if d.get("pai") else "") + f' › <span>{E(d["titulo"])}</span>'
    sobre = ""
    if mapa:
        itens = []
        for mid in d.get("mapa", []):
            p = mapa["por_id"].get(mid)
            if not p:
                continue
            ligs = "".join(f'<div class="pp-saida"><b>{E(mapa["lig"][i]["nome"])}</b>: {E(mapa["lig"][i]["norma"])}<details><summary>Como era no legado</summary>{E(mapa["lig"][i]["texto"])}</details></div>' for i in p["ligacoes"])
            itens.append(f'<p>{E(p["resumo"])}</p>' + (f'<p><b>Norma:</b> {E(p["norma"])}</p>' if p["norma"] else "") + (f'<h3>O que o sistema precisa garantir entre processos</h3>{ligs}' if ligs else ""))
        if itens:
            sobre = f'<details class="pp-sobre"><summary><b>Sobre este processo</b></summary>{"".join(itens)}</details>'
    cores = {"t": "#2e9b4f", "a": "#1f6aa5", "p": "#b26a00", "v": "#5b6472", "n": "#8a94a6"}
    leg = "".join(f'<span><i style="--c:{cores[c]}"></i>{E(t)}</span>' for t, c in STATUS.values())
    corpo = (f'<main class="pp" id="conteudo"><p class="pp-trilha">{trilha}</p><h1>{E(d["titulo"])}</h1><p>{E(d["intro"])}</p>{sobre}'
             f'<p class="pp-vazio">{E(d["fonte"])}</p><div class="pp-leg" aria-label="Legenda">{leg}</div>'
             f'<section class="pp-fase"><h2>Parametrização</h2><div class="pp-linha">{card(d["parametrizacao"])}</div></section>'
             f'<section class="pp-fase"><h2>Fluxo</h2><div class="pp-linha">{linha}</div></section>'
             f'<section id="pp-painel" class="pp-painel" aria-live="polite" hidden></section>'
             f'<script type="application/json" id="pp-dados">{json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")}</script></main>')
    nome = f'processo-{d["id"]}.html'
    (Path(destino) / nome).write_text(cabecalho(d["titulo"], "").replace("</head>", f"<style>{CSS}</style></head>") + corpo + rodape("").replace("</body>", f"<script>{JS}</script></body>"), encoding="utf-8")
    return nome
