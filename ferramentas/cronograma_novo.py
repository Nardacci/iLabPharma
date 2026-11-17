"""Página "Cronograma · Novo" (cronograma-novo.html): o andamento da versão nova (a da equipe de desenvolvimento) nos cinco módulos:
Principal, Estoque, Controle da Qualidade, Garantia da Qualidade e Controle de Documentos.

Fonte: homologacao/versao-nova/cronograma-novo.json, gerado por homologacao/ferramentas/montar_cronograma_novo.py a partir dos
arquivos do repositório (fichas, manuais, imagens, conferência pelos robôs, documentos). Mesmo layout do cronograma do Legado,
só a cor de destaque muda (azul), como nas demais páginas da versão nova."""
import html
import json
import re
from pathlib import Path

import higiene
import versao_nova

E = html.escape
ROT = {"feito": "feito", "andamento": "em andamento", "nao_iniciado": "não iniciado"}


def _inline(md):
    t = E(md)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", t)


def _dbr(iso):
    a, m, d = iso.split("-")
    return f"{d}/{m}/{a}"


def pagina(origem, cabecalho, rodape, cores):
    arq = Path(origem) / "homologacao" / "versao-nova" / "cronograma-novo.json"
    if not arq.exists():
        return ""
    c = json.loads(higiene.redigir(arq.read_text(encoding="utf-8")))
    mods, tot = c["modulos"], c["total"]
    raiz = ""

    def faixa(m):
        p = m["andamento"]
        return (f'<div class="cn-barra-geral" role="img" aria-label="{p}% de avanço"><i style="width:{p}%"></i></div>')

    # 1. Telas por módulo
    soma = lambda k: sum(m["telas"][k] for m in mods)
    linhas = "".join(
        f'<tr><td><a href="documentacao/{m["id"]}/index.html">{E(m["nome"])}</a></td><td>{m["telas"]["total"]}</td><td>{m["telas"]["prontas"]}</td>'
        f'<td>{m["telas"]["provisorias"]}</td><td>{m["telas"]["nao_existem"] or "—"}</td><td>{m["telas"]["testadas"]}</td><td>{m["telas"]["manuais"]}</td><td>{m["telas"]["conferidas"]}</td></tr>'
        for m in mods)
    totais = (f'<tr class="cn-total"><td><strong>Total</strong></td><td><strong>{soma("total")}</strong></td><td><strong>{soma("prontas")}</strong></td><td><strong>{soma("provisorias")}</strong></td>'
              f'<td><strong>{soma("nao_existem")}</strong></td><td><strong>{soma("testadas")}</strong></td><td><strong>{soma("manuais")}</strong></td><td><strong>{soma("conferidas")}</strong></td></tr>')
    tabela_telas = ('<div class="tabela"><table><thead><tr><th>Módulo</th><th>Telas no total</th><th>Prontas (reais)</th><th>Provisórias</th><th>Não existem</th>'
                    f'<th>Testadas</th><th>Manual escrito</th><th>Manual conferido por robô</th></tr></thead><tbody>{linhas}{totais}</tbody></table></div>')
    fontes = "".join(f'<li><strong>{E(m["nome"])}:</strong> {E(m["fonte_telas"])}</li>' for m in mods)

    # 2. Andamento por módulo
    cartoes = []
    for m in mods:
        cor = cores.get(m["id"], "#1f6feb")
        et = "".join(
            f'<div class="cn-etapa"><div class="cn-etapa-topo"><span>{E(e["nome"])}</span><em>{e["feitos"]} de {e["total"]} · {e["pct"]}%</em>'
            f'<span class="cn-selo cn-{e["status"]}">{ROT[e["status"]]}</span></div>'
            f'<div class="cn-trilha"><i style="width:{e["pct"]}%"></i></div>' + (f'<small>{E(e["nota"])}</small>' if e.get("nota") else "") + '</div>'
            for e in m["etapas"])
        falta = "".join(f"<li>{E(x)}</li>" for x in m["falta"])
        cartoes.append(
            f'<details class="cn-modulo" id="cn-{m["id"]}" style="--cor:{cor}" open><summary><span>{E(m["nome"])}</span><em>{m["andamento"]}% de avanço</em></summary>'
            f'<div class="cn-corpo">{faixa(m)}<p class="cn-num"><strong>{m["fichas"]["total"]}</strong> fichas de defeito ({m["fichas"]["alta"]} de gravidade Alta, {m["fichas"]["sem_imagem"]} ainda sem imagem) · '
            f'<strong>{m["manual"]["imagens"]}</strong> imagens nos manuais · <strong>{m["manual"]["prints_que_faltam"]}</strong> prints por fazer</p>'
            f'<div class="cn-etapas">{et}</div><h4>O que falta</h4><ul>{falta}</ul></div></details>')

    # 3. Onde estamos e quanto falta (todas as etapas somadas)
    nomes = [e["nome"] for e in mods[0]["etapas"]]
    linhas_e = ""
    for i, nome in enumerate(nomes):
        f = sum(m["etapas"][i]["feitos"] for m in mods); t = sum(m["etapas"][i]["total"] for m in mods)
        p = round(100 * f / t) if t else 0
        linhas_e += (f'<tr><td>{E(nome)}</td><td>{f} de {t}</td><td><div class="cn-trilha cn-trilha-curta"><i style="width:{p}%"></i></div></td><td>{p}%</td><td>{t - f}</td></tr>')
    tabela_e = ('<div class="tabela"><table><thead><tr><th>Etapa</th><th>Feito</th><th>Andamento</th><th>%</th><th>Falta</th></tr></thead><tbody>' + linhas_e + '</tbody></table></div>')

    premissas = "".join(f"<li>{_inline(x)}</li>" for x in c.get("premissas", []))
    seletor = versao_nova.seletor("cronograma.html", "cronograma-novo.html", "novo")
    return (cabecalho("Cronograma da versão nova · iLabMedSys", raiz, "cronograma-novo").replace("<body ", '<body data-versao-pagina="novo" ', 1) + f"""
<main id="conteudo" class="cronograma cronograma-novo">
  <section class="anv-faixa">
    <div class="anv-faixa-interna">
      <nav class="trilha" aria-label="Você está em"><a href="index.html">Início</a> › <a href="cronograma.html">Cronograma</a> › <span>Novo</span></nav>
      <h1>Cronograma da versão nova</h1>
      <p>A versão nova é o sistema que a equipe de desenvolvimento está fazendo. Aqui: quantas telas existem em cada módulo, quais estão prontas e quais já foram testadas, onde estamos e quanto falta. Cinco módulos: Principal, Estoque, Controle da Qualidade, Garantia da Qualidade e Controle de Documentos. Atualizado em {_dbr(c["atualizado"])}.</p>
      <p class="cn-seletor">{seletor}</p>
    </div>
  </section>
  <div class="cr-conteudo">
    <div class="cr-numeros cn-numeros" aria-label="Números gerais">
      <div class="numero"><strong>{tot["telas"]}</strong><span>telas no total (cinco módulos)</span></div>
      <div class="numero"><strong>{tot["prontas"]}</strong><span>telas prontas (reais)</span></div>
      <div class="numero"><strong>{tot["testadas"]}<small>/{tot["prontas"]}</small></strong><span>telas reais testadas</span></div>
      <div class="numero"><strong>{tot["conferidas"]}<small>/{tot["manuais"]}</small></strong><span>manuais conferidos por robô</span></div>
      <div class="numero"><strong>{tot["fichas"]}</strong><span>fichas de defeito</span></div>
      <div class="numero"><strong>{tot["andamento"]}%</strong><span>avanço geral do fechamento</span></div>
    </div>

    <section class="cr-sec">
      <h2>1. Telas por módulo</h2>
      <p class="cr-sub"><strong>Prontas</strong> são as telas reais (que funcionam e foram desenvolvidas); <strong>provisórias</strong> mostram só um cartão ("API conectada" ou "Tela em integração") e não têm o que testar; <strong>testadas</strong> são as telas reais que já tiveram o passo a passo executado; <strong>manual conferido por robô</strong> é o manual cuja tela foi executada passo a passo, com print de cada passo.</p>
      {tabela_telas}
      <details class="cr-det cn-fonte"><summary><span>De onde vêm os totais de telas</span></summary><div class="cr-det-corpo"><ul>{fontes}</ul></div></details>
    </section>

    <section class="cr-sec">
      <h2>2. Andamento por módulo</h2>
      <p class="cr-sub">O avanço de cada módulo é a média de seis etapas. Clique no módulo para ver cada etapa e o que falta.</p>
      {"".join(cartoes)}
    </section>

    <section class="cr-sec">
      <h2>3. Onde estamos e quanto falta (cinco módulos somados)</h2>
      {tabela_e}
      <p class="cr-nota">Estimativa de esforço (não é data): cerca de <strong>{tot["estimativa_horas_3_janelas"]} horas</strong> de robô, com três janelas ao mesmo tempo, para conferir os manuais que ainda faltam. As datas dependem de quantas janelas ficam abertas e do ambiente de teste.</p>
    </section>

    <section class="cr-sec">
      <h2>Como estes números foram feitos</h2>
      <ul class="cr-premissas">{premissas}</ul>
    </section>
  </div>
</main>
""" + rodape(raiz))


CSS = """
/* Cronograma da versão nova: mesmo layout do Legado, cor de destaque azul */
.cn-seletor{margin:14px 0 0}
.cn-numeros{grid-template-columns:repeat(3,1fr)}
.cn-numeros .numero strong{color:#1f6feb}
.cn-total td{background:var(--painel2)}
.cn-modulo{border:1px solid var(--linha);border-left:5px solid var(--cor,#1f6feb);border-radius:var(--raio);background:var(--painel);margin:12px 0}
.cn-modulo summary{cursor:pointer;display:flex;justify-content:space-between;gap:12px;align-items:center;padding:12px 16px;font-weight:700}
.cn-modulo summary em{font-style:normal;font-weight:600;color:var(--suave)}
.cn-corpo{padding:0 16px 14px}
.cn-barra-geral,.cn-trilha{height:12px;border-radius:999px;background:var(--linha);overflow:hidden}
.cn-barra-geral i,.cn-trilha i{display:block;height:100%;background:#1f6feb;border-radius:999px}
.cn-trilha-curta{min-width:140px}
.cn-num{margin:10px 0}
.cn-etapas{display:grid;gap:10px;margin:12px 0}
.cn-etapa-topo{display:flex;flex-wrap:wrap;gap:6px 12px;align-items:baseline;margin-bottom:4px}
.cn-etapa-topo span:first-child{font-weight:600}
.cn-etapa-topo em{font-style:normal;color:var(--suave);font-size:.9rem}
.cn-etapa small{display:block;margin-top:3px;color:var(--suave)}
.cn-selo{font-size:.74rem;font-weight:700;padding:1px 9px;border-radius:999px;border:1px solid var(--linha)}
.cn-feito{background:#1f6feb;color:#fff;border-color:#1f6feb}
.cn-andamento{border-color:#1f6feb;color:#1f6feb}
.cn-nao_iniciado{color:var(--suave)}
@media (max-width:760px){.cn-numeros{grid-template-columns:repeat(2,1fr)}}
"""
