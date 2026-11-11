"""Páginas de fluxo de processo e de cadastro (processo-<id>.html), a partir de homologacao/transversal/processos/*.json.

Fluxo (recebimento.json, quarentena.json...): a Parametrização (os cadastros necessários, cada um uma caixa que abre o seu fluxo), as entradas, as etapas em
sequência (de cima para baixo), as decisões com saídas e o resultado. Cadastro (cadastros.json): as caixas dos cadastros de que ele depende, que abrem os seus
próprios fluxos, até chegar a um cadastro único (sem dependência). Só o diagrama e uma legenda no fim. Clicar em uma caixa abre o painel (ideal, regras,
norma, versão nova, erros, perguntas); a caixa que tem fluxo próprio abre o fluxo. "**" marca a caixa com erro que contraria a norma da ANVISA
(leitura da homologação, a confirmar com a Qualidade). Sem referência a arquivo e linha do código. Não altera outra página."""
import html
import json
import re
from pathlib import Path

import higiene

E = html.escape
STATUS = {"tela": ("Testada pelas telas", "t"), "api": ("Testada só pela API (telas provisórias)", "a"), "parcial": ("Parcial: parte testada, parte provisória", "p"),
          "provisoria": ("Provisória (por construir)", "v"), "nao-testado": ("Ainda não testada", "n")}
CORES = {"t": "#2e9b4f", "a": "#1f6aa5", "p": "#b26a00", "v": "#5b6472", "n": "#8a94a6"}
CSS = """
.fl{max-width:1100px;margin:0 auto;padding:1.5rem 1.25rem}
.fl-topo{display:flex;flex-wrap:wrap;gap:.4rem 1rem;align-items:baseline;margin-bottom:.3rem}
.fl-trilha{font-size:.92rem}
.fl-col{display:flex;flex-direction:column;align-items:center;margin:1rem 0}
.fl-seta{width:2px;height:30px;background:#8a94a6;position:relative;margin:0 auto}
.fl-seta::after{content:"";position:absolute;bottom:-2px;left:-6px;border:7px solid transparent;border-top:10px solid #8a94a6;border-bottom:0}
.fl-linha{display:flex;flex-wrap:wrap;gap:.8rem;justify-content:center;align-items:stretch}
.fl-faixa{width:100%;border:2px solid #1f6aa5;border-radius:14px;padding:.8rem 1rem 1rem;background:color-mix(in srgb,#1f6aa5 5%,transparent)}
.fl-faixa h2{font-size:1rem;margin:0 0 .6rem;text-align:center}
.cx{all:unset;box-sizing:border-box;cursor:pointer;width:290px;padding:.65rem .8rem;border:2px solid var(--c);border-left-width:8px;border-radius:10px;font-size:.92rem;line-height:1.3;background:var(--fundo,transparent);display:block}
.cx:hover,.cx:focus-visible{box-shadow:0 0 0 3px var(--c)}
.cx[aria-pressed=true]{background:color-mix(in srgb,var(--c) 14%,transparent)}
.cx b{display:block;margin-bottom:.2rem}.cx small{display:block;opacity:.8;font-size:.78rem}
a.cx{text-decoration:none;color:inherit}
.cx-abre{display:block;margin-top:.3rem;font-weight:600;color:#f57c00;font-size:.82rem}
.cx-dec{border-style:dashed;border-radius:26px;text-align:center}
.cx-dec b::before{content:"◇ "}
.cx-res{cursor:default;border-style:dashed;border-left-width:2px;--c:#2e9b4f}
.c-t{--c:#2e9b4f}.c-a{--c:#1f6aa5}.c-p{--c:#b26a00}.c-v{--c:#5b6472}.c-n{--c:#8a94a6;border-style:dashed}
.ast{color:#b3261e;font-weight:800;margin-left:.25rem}
.fl-dec{position:relative;display:flex;flex-direction:column;align-items:center}
.fl-lado{position:absolute;left:calc(100% + 1.4rem);top:0;display:flex;align-items:flex-start;gap:.4rem;width:300px}
.fl-lado .fl-chip{margin-top:0}.fl-h{align-self:center;opacity:.6;font-size:1.2rem}
.fl-ramos{display:flex;gap:2rem;justify-content:center;flex-wrap:wrap}
.fl-ramo{display:flex;flex-direction:column;align-items:center}
.fl-chip{font-size:.8rem;font-weight:700;padding:.1rem .6rem;border-radius:999px;border:1px solid #8a94a6;margin-bottom:.2rem}
.fl-leg{display:flex;flex-wrap:wrap;gap:.3rem 1rem;margin:1.5rem 0 .4rem;font-size:.82rem;opacity:.9;justify-content:center}
.fl-leg span{display:inline-flex;align-items:center;gap:.35rem}.fl-leg i{width:.8rem;height:.8rem;border-radius:3px;display:inline-block;border:2px solid var(--c)}
.fl-nota{text-align:center;font-size:.85rem;margin:.2rem 0 1rem}
.pp-painel{margin:1.4rem 0;padding:1.1rem 1.3rem;border:2px solid var(--c,#8a94a6);border-radius:12px}
.pp-painel h2{margin:.1rem 0 .3rem}.pp-painel h3{margin:1.1rem 0 .3rem;font-size:1rem}
.pp-tab{width:100%;border-collapse:collapse;font-size:.92rem}
.pp-tab th,.pp-tab td{padding:.4rem .55rem;border-bottom:1px solid var(--borda,#d9dee6);text-align:left;vertical-align:top}
.pp-cl{white-space:nowrap;font-weight:600}.pp-lista{margin:.2rem 0;padding-left:1.2rem}.pp-vazio{opacity:.7}
"""
JS = """
(function(){
var d=JSON.parse(document.getElementById('pp-dados').textContent),p=document.getElementById('pp-painel');
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function lista(a){return a.length?'<ul class="pp-lista">'+a.map(function(x){return '<li>'+x+'</li>';}).join('')+'</ul>':'';}
function abrir(id,rolar){var x=d.etapas.filter(function(a){return a.id===id})[0];if(!x)return;
document.querySelectorAll('button.cx').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.id===id?'true':'false');});
var h='<h2>'+esc(x.nome)+(x.fora?'<span class="ast">**</span>':'')+'</h2>'+(x.quem?'<p><b>Quem:</b> '+esc(x.quem)+'</p>':'');
h+='<h3>Como deve ser (ideal)</h3><p>'+esc(x.ideal)+'</p>';
if(x.obrigatorios)h+='<p><b>O que preencher:</b> '+esc(x.obrigatorios)+'</p>';
if(x.regra)h+='<p><b>Regra:</b> '+esc(x.regra)+'</p>';
if(x.depende&&x.depende.length)h+='<p><b>Depende de:</b> '+x.depende.map(function(a){return '<a href="'+esc(a.href)+'">'+esc(a.nome)+'</a>';}).join(', ')+'</p>';
if(x.regras&&x.regras.length){h+='<h3>Regras e norma</h3><div class="tabela"><table class="pp-tab"><thead><tr><th>O que o sistema precisa garantir</th><th>O que o código novo faz hoje</th><th>Situação</th></tr></thead><tbody>'+x.regras.map(function(r){return '<tr><td>'+esc(r.ideal)+'</td><td>'+esc(r.hoje)+'</td><td class="pp-cl">'+esc(r.classe)+'</td></tr>';}).join('')+'</tbody></table></div>';}
if(x.norma)h+='<p><b>Norma:</b> '+esc(x.norma)+'</p>';
if(x.saidas&&x.saidas.length)h+='<h3>Saídas</h3>'+lista(x.saidas.map(function(o){return '<b>'+esc(o.rotulo)+'</b> → '+esc(o.vai);}));
if(x.telas&&x.telas.length)h+='<h3>Telas</h3>'+lista(x.telas.map(esc));
h+='<h3>Versão nova hoje</h3><p><b>'+esc(x.status_txt)+'.</b> '+esc(x.nota_novo||'')+'</p>';
if(x.fichas.length)h+='<p><b>Erros encontrados:</b></p>'+lista(x.fichas.map(function(f){return '<a href="'+esc(f.href)+'">'+esc(f.id)+'</a> ('+esc(f.grav)+'): '+esc(f.titulo)+(f.fora?'<span class="ast">**</span>':'');}));
if(x.perguntas&&x.perguntas.length)h+='<h3>Perguntas ao desenvolvimento</h3>'+lista(x.perguntas.map(esc));
if(x.legado&&x.legado.length)h+='<details><summary>Como era no legado</summary>'+lista(x.legado.map(esc))+'</details>';
p.innerHTML=h;p.hidden=false;p.className='pp-painel c-'+x.cod;if(rolar)p.scrollIntoView({behavior:'smooth',block:'nearest'});}
document.querySelectorAll('button.cx').forEach(function(b){b.addEventListener('click',function(){abrir(b.dataset.id,true);history.replaceState(null,'','#'+b.dataset.id);});});
document.querySelectorAll('a.fl-voltar').forEach(function(a){a.addEventListener('click',function(e){if(history.length>1&&document.referrer){e.preventDefault();history.back();}});});
if(location.hash.length>1)abrir(location.hash.slice(1),false);else if(d.abrir)abrir(d.abrir,false);
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


class Gerador:
    def __init__(self, hom, destino, cabecalho, rodape, fichas, classif, href_doc):
        self.hom, self.destino, self.cab, self.rod = Path(hom), Path(destino), cabecalho, rodape
        self.fichas, self.classif, self.href_doc = fichas, classif, href_doc
        self.perg = _perguntas(hom)
        base = self.hom / "transversal/processos"
        self.cad = {}
        arq = base / "cadastros.json"
        if arq.exists():
            for c in json.loads(higiene.redigir(arq.read_text(encoding="utf-8")))["cadastros"]:
                self.cad[c["id"]] = c
        self.fluxos = {}
        for a in sorted(base.glob("*.json")):
            if a.name != "cadastros.json":
                d = json.loads(higiene.redigir(a.read_text(encoding="utf-8")))
                self.fluxos[d["id"]] = d
        self._memo = {}

    # --- marcações ---
    def _fora(self, fid):
        c = self.classif.get(fid)
        return bool(c and c["contraria_norma"] == "Sim")

    def fichas_do_cadastro(self, c):
        nomes = [n.lower() for n in c["telas_fichas"]]
        return [i for i, f in self.fichas.items() if any(n in (f.get("tela") or "").lower() for n in nomes)]

    def fora_cadastro(self, cid, vistos=()):
        if cid in vistos or cid not in self.cad:
            return False
        c = self.cad[cid]
        return any(self._fora(i) for i in self.fichas_do_cadastro(c))

    def fora_fluxo(self, fid, vistos=()):
        if fid in vistos or fid not in self.fluxos:
            return False
        f = self.fluxos[fid]
        for e in f["etapas"]:
            if any(self._fora(i) for i in e.get("fichas", [])) or (e.get("abre") and self.fora_fluxo(e["abre"], vistos + (fid,))):
                return True
        return False

    # --- dados do painel ---
    def _fichas(self, ids):
        return [{"id": i, "titulo": self.fichas[i]["titulo"], "grav": self.fichas[i]["grav"], "fora": self._fora(i), "href": f"erros-novo/{i.lower()}.html"} for i in ids if i in self.fichas]

    def dados_etapa(self, e):
        txt, cod = STATUS[e["status_novo"]]
        d = {k: e.get(k, v) for k, v in (("id", ""), ("nome", ""), ("quem", ""), ("ideal", ""), ("regras", []), ("norma", ""), ("telas", []), ("nota_novo", ""), ("legado", []), ("saidas", []))}
        d.update(status_txt=txt, cod=cod, fichas=self._fichas(e.get("fichas", [])), perguntas=[f"{n}. {self.perg[n]}" for n in e.get("perguntas", []) if n in self.perg],
                 fora=any(self._fora(i) for i in e.get("fichas", [])) or bool(e.get("abre") and self.fora_fluxo(e["abre"])))
        for s in d["saidas"]:
            s.setdefault("vai", (s.get("caixa") or {}).get("nome", "próxima etapa"))
        return d

    def dados_cadastro(self, c):
        txt, cod = STATUS[c["status_novo"]]
        ids = self.fichas_do_cadastro(c)
        return dict(id=c["id"], nome=c["nome"], quem="", ideal=c["para"], obrigatorios=c["obrigatorios"], regra=c["regra"], regras=[], norma="", telas=[], nota_novo="", legado=[], saidas=[],
                    depende=[{"nome": self.cad[d]["nome"], "href": f"processo-cad-{d}.html"} for d in c["depende"]], status_txt=txt, cod=cod, fichas=self._fichas(ids), perguntas=[],
                    fora=self.fora_cadastro(c["id"]))

    # --- peças visuais ---
    @staticmethod
    def seta():
        return '<div class="fl-seta" aria-hidden="true"></div>'

    def caixa_cadastro(self, cid):
        c = self.cad[cid]
        txt, cod = STATUS[c["status_novo"]]
        ast = '<span class="ast" title="Fora das normas da Anvisa">**</span>' if self.fora_cadastro(cid) else ""
        sub = f'<small>Depende de {len(c["depende"])} cadastro(s)</small>' if c["depende"] else "<small>Cadastro único</small>"
        return f'<a class="cx c-{cod}" href="processo-cad-{E(cid)}.html"><b>{E(c["nome"])}{ast}</b>{sub}<small>{E(txt)}</small><span class="cx-abre">↳ abre o fluxo</span></a>'

    def caixa_etapa(self, e):
        x = self.dados_etapa(e)
        ast = '<span class="ast" title="Fora das normas da Anvisa">**</span>' if x["fora"] else ""
        corpo = f'<b>{E(e["nome"])}{ast}</b>' + (f'<small>{E(e["quem"])}</small>' if e.get("quem") else "") + f'<small>{E(x["status_txt"])}</small>'
        if e.get("abre"):
            return f'<a class="cx c-{x["cod"]}" href="processo-{E(e["abre"])}.html">{corpo}<span class="cx-abre">↳ abre o fluxo</span></a>'
        cls = " cx-dec" if e.get("tipo") == "decisao" else ""
        return f'<button type="button" class="cx c-{x["cod"]}{cls}" data-id="{E(e["id"])}" aria-pressed="false">{corpo}</button>'

    def decisao(self, e, proximo):
        """O ramo que segue (por exemplo, Aprovado) continua na linha principal; os outros saem ao lado, como caixas de outro processo."""
        lado = []
        for s in e["saidas"]:
            if s.get("proximo"):
                chip = s["rotulo"]
                continue
            cx = s["caixa"]
            href = self.href_doc(cx["abre_doc"]["modulo"], cx["abre_doc"]["titulo"]) if cx.get("abre_doc") else None
            corpo = f'<b>{E(cx["nome"])}</b><small>Fluxo documentado</small>'
            caixa = (f'<a class="cx c-n" href="{E(href)}">{corpo}<span class="cx-abre">↳ abre o roteiro</span></a>' if href else f'<div class="cx c-n" style="cursor:default">{corpo}</div>')
            lado.append(f'<div class="fl-lado"><span class="fl-chip">{E(s["rotulo"])}</span><span class="fl-h" aria-hidden="true">→</span>{caixa}</div>')
        chip = next((s["rotulo"] for s in e["saidas"] if s.get("proximo")), "")
        return f'<div class="fl-dec"><span class="fl-chip">{E(chip)}</span>{self.seta()}{self.caixa_etapa(proximo)}{"".join(lado)}</div>'

    def ramos(self, e, tem_proximo):
        itens = []
        for s in e["saidas"]:
            if s.get("caixa"):
                cx = s["caixa"]
                href = self.href_doc(cx["abre_doc"]["modulo"], cx["abre_doc"]["titulo"]) if cx.get("abre_doc") else None
                corpo = f'<b>{E(cx["nome"])}</b><small>Fluxo documentado</small>'
                caixa = (f'<a class="cx c-n" href="{E(href)}">{corpo}<span class="cx-abre">↳ abre o roteiro</span></a>' if href else f'<div class="cx c-n" style="cursor:default">{corpo}</div>')
                itens.append(f'<div class="fl-ramo"><span class="fl-chip">{E(s["rotulo"])}</span>{self.seta()}{caixa}</div>')
            else:
                itens.append(f'<div class="fl-ramo"><span class="fl-chip">{E(s["rotulo"])}</span>' + (self.seta() if tem_proximo else "") + "</div>")
        return f'<div class="fl-ramos">{"".join(itens)}</div>'

    def legenda(self, tem_ast):
        leg = "".join(f'<span><i style="--c:{CORES[c]}"></i>{E(t)}</span>' for t, c in STATUS.values())
        nota = '<p class="fl-nota"><span class="ast">**</span> Fora das normas da Anvisa (leitura da homologação, a confirmar com a Qualidade)</p>' if tem_ast else ""
        return f'<div class="fl-leg" aria-label="Legenda">{leg}</div>{nota}'

    def moldura(self, titulo, trilha, conteudo, dados, abrir=""):
        dados["abrir"] = abrir
        corpo = (f'<main class="fl" id="conteudo"><div class="fl-topo"><a class="fl-voltar" href="processos.html">← Voltar</a><span class="fl-trilha">{trilha}</span></div>'
                 f'<h1>{E(titulo)}</h1><div class="fl-col">{conteudo}</div>'
                 f'<section id="pp-painel" class="pp-painel" aria-live="polite" hidden></section>'
                 f'<script type="application/json" id="pp-dados">{json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")}</script></main>')
        return self.cab(titulo, "").replace("</head>", f"<style>{CSS}</style></head>") + corpo + self.rod("").replace("</body>", f"<script>{JS}</script></body>")

    # --- páginas ---
    def pagina_fluxo(self, fid):
        d = self.fluxos[fid]
        etapas = d["etapas"]
        entradas = [e for e in etapas if e.get("grupo") == "entrada"]
        fluxo = [e for e in etapas if e.get("grupo") == "fluxo"]
        cads = d["parametrizacao"].get("cadastros", [])
        partes = []
        if cads:
            partes.append(f'<div class="fl-faixa"><h2>Parametrização: cadastros necessários</h2><div class="fl-linha">{"".join(self.caixa_cadastro(c) for c in cads if c in self.cad)}</div></div>' + self.seta())
        if entradas:
            partes.append(f'<div class="fl-linha">{"".join(self.caixa_etapa(e) for e in entradas)}</div>' + self.seta())
        i = 0
        while i < len(fluxo):
            e = fluxo[i]
            partes.append(self.caixa_etapa(e))
            partes.append(self.seta())
            if e.get("tipo") == "decisao" and e.get("saidas") and i + 1 < len(fluxo):
                partes.append(self.decisao(e, fluxo[i + 1]))
                partes.append(self.seta())
                i += 2
                continue
            i += 1
        partes.append(f'<div class="cx cx-res"><b>Resultado</b>{E(d["resultado"])}</div>')
        partes.append(self.legenda(self.fora_fluxo(fid)))
        dados = {"etapas": [self.dados_etapa(e) for e in etapas]}
        trilha = '<a href="processos.html">Mapa dos processos</a>' + (f' › <a href="processo-{E(d["pai"]["id"])}.html">{E(d["pai"]["nome"])}</a>' if d.get("pai") else "") + f' › {E(d["titulo"])}'
        nome = f"processo-{fid}.html"
        (self.destino / nome).write_text(self.moldura(d["titulo"], trilha, "".join(partes), dados), encoding="utf-8")
        return nome

    def pagina_cadastro(self, cid):
        c = self.cad[cid]
        ant = "".join(self.caixa_cadastro(x) for x in c["depende"])
        partes = []
        if c["depende"]:
            partes.append(f'<div class="fl-faixa"><h2>Antes de cadastrar: cadastros de que ele depende</h2><div class="fl-linha">{ant}</div></div>' + self.seta())
        else:
            partes.append('<div class="fl-faixa"><h2>Sem dependência: é um cadastro único</h2></div>' + self.seta())
        x = self.dados_cadastro(c)
        ast = '<span class="ast">**</span>' if x["fora"] else ""
        partes.append(f'<button type="button" class="cx c-{x["cod"]}" data-id="{E(cid)}" aria-pressed="false"><b>Cadastrar: {E(c["nome"])}{ast}</b><small>{E(x["status_txt"])}</small></button>')
        partes.append(self.seta())
        partes.append(f'<div class="cx cx-res"><b>Resultado</b>{E(c["nome"])} cadastrado e ativo, pronto para ser usado.</div>')
        partes.append(self.legenda(x["fora"]))
        nome = f"processo-cad-{cid}.html"
        (self.destino / nome).write_text(self.moldura(f'Cadastro: {c["nome"]}', f'<a href="processos.html">Mapa dos processos</a> › Cadastro › {E(c["nome"])}', "".join(partes), {"etapas": [x]}, abrir=cid), encoding="utf-8")
        return nome

    def gerar(self):
        nomes = [self.pagina_fluxo(f) for f in self.fluxos] + [self.pagina_cadastro(c) for c in self.cad]
        return nomes
