"""Biblioteca do portal: classificação dos documentos (tipo, público, visão) e página de busca com filtros.

**Fonte única dos metadados:** `homologacao/biblioteca-metadados.csv` (repositório de homologação). O portal LÊ esse
arquivo e nunca o reescreve na geração normal. Quem edita é a pessoa responsável; o que ela corrigir persiste.
Documento novo, sem linha no arquivo, aparece com a classificação automática marcada como "auto" e entra na lista
de pendências do relatório. Para acrescentar as linhas que faltam (sem tocar nas existentes):

    python3 ferramentas/gerar_portal.py --origem <homol> --destino <pasta> --atualizar-metadados

Regra de dúvida: quando nenhuma regra reconhece o documento, o valor é "a classificar" (nunca um palpite).
"""
import csv
import html
import json
import re
import subprocess
from pathlib import Path

CAMPOS = ["chave", "modulo", "titulo", "tipo", "publico", "visao", "classificacao", "regra", "revisado", "observacao"]
A_CLASSIFICAR = "a classificar"
VISOES = ["legado", "novo", "ideal", "geral"]
PUBLICOS = ["diretoria", "áreas", "GQ", "desenvolvimento", "todos"]

# (padrão no título, tipo, nome da regra). A primeira que casar vale.
REGRAS_TIPO = [
    (r"ata da reuni", "ata", "titulo:ata"),
    (r"situação na versão nova", "teste", "titulo:situação-na-versão-nova"),
    (r"cadastros de apoio", "regras", "titulo:cadastros-de-apoio"),
    (r"telas a criar|tela a criar", "tela a criar", "titulo:tela-a-criar"),
    (r"como usar esta seção|visão geral por menu", "guia de leitura", "titulo:guia-de-leitura"),
    (r"aderência ao edital|diagnóstico de conformidade", "diagnóstico", "titulo:diagnóstico"),
    (r"mapa do processo fabril|mapa de integra|repetidos entre|onde a corrente", "visão entre módulos", "titulo:entre-módulos"),
    (r"\bideal\b|entre os módulos|qualidade entre", "ideal", "titulo:ideal"),
    (r"resumo do módulo|resumo executivo", "resumo", "titulo:resumo"),
    (r"passo a passo|roteiro de testes", "roteiro de teste", "titulo:roteiro-de-teste"),
    (r"parecer|não está apto|por que .* não está apto", "parecer", "titulo:parecer"),
    (r"dossiê", "dossiê", "titulo:dossiê"),
    (r"manual", "manual", "titulo:manual"),
    (r"regras de negócio", "regras", "titulo:regras"),
    (r"matriz de permiss", "permissões e acessos", "titulo:permissões-e-acessos"),
    (r"requisitos", "requisitos", "titulo:requisitos"),
    (r"conformidade|análise de risco|matriz de rastreabilidade", "conformidade e risco", "titulo:conformidade-risco"),
    (r"plano de testes|plano de regressão|relatório de testes|resultado da rodada|resumo dos testes|usuários de teste", "teste", "titulo:teste"),
    (r"defeitos", "defeitos", "titulo:defeitos"),
    (r"modelo de dados|comparação|integra", "dados e integração", "titulo:dados-integração"),
    (r"resumo geral|: resumo", "tela testada", "titulo:tela-testada"),
    (r"inventário|reconhecimento", "reconhecimento", "titulo:reconhecimento"),
]
PUBLICO_POR_TIPO = {
    "resumo": ["diretoria", "áreas"], "parecer": ["diretoria", "GQ"], "diagnóstico": ["diretoria", "GQ"], "dossiê": ["GQ"],
    "manual": ["áreas"], "fluxo": ["áreas", "GQ"], "regras": ["áreas", "GQ", "desenvolvimento"], "requisitos": ["desenvolvimento"],
    "conformidade e risco": ["GQ"], "teste": ["GQ", "desenvolvimento"], "roteiro de teste": ["GQ", "desenvolvimento"],
    "defeitos": ["desenvolvimento"], "dados e integração": ["desenvolvimento"], "ideal": ["GQ", "desenvolvimento"],
    "tela a criar": ["desenvolvimento", "GQ"], "tela testada": ["GQ", "desenvolvimento"], "reconhecimento": ["GQ", "desenvolvimento"],
    "visão entre módulos": ["diretoria", "GQ"], "permissões e acessos": ["GQ", "desenvolvimento"], "guia de leitura": ["todos"],
}  # "ata" fica de fora de propósito: o público é "a classificar"


def tipo_automatico(titulo, cat):
    """Devolve (tipo, regra). Sem regra que case, (a classificar, sem-regra)."""
    t = titulo.lower()
    if cat == "fluxos":
        return ("roteiro de teste", "categoria:roteiro") if "passo a passo" in t or "roteiro de testes" in t else ("fluxo", "categoria:fluxos")
    for padrao, tipo, regra in REGRAS_TIPO:
        if re.search(padrao, t):
            return tipo, regra
    return A_CLASSIFICAR, "sem-regra"


def publico_automatico(tipo):
    if tipo in PUBLICO_POR_TIPO:
        return PUBLICO_POR_TIPO[tipo], "público-por-tipo"
    return [A_CLASSIFICAR], "sem-regra"


def visao_automatica(p, mod):
    """Visão da página: pela seção do roteiro do módulo; o que está em Sobre o módulo ou em Visão entre módulos é geral."""
    sit = p.get("sit")
    if sit in ("legado", "novo", "ideal"):
        return sit, f"seção:{sit}"
    return "geral", "seção:geral"


def datas_de_atualizacao(origem):
    """Data do último commit de cada arquivo do repositório de homologação (uma passada só)."""
    saida = subprocess.run(["git", "-C", str(origem), "log", "--name-only", "--format=@@%cs"], capture_output=True, text=True).stdout
    mapa, atual = {}, ""
    for linha in saida.splitlines():
        if linha.startswith("@@"):
            atual = linha[2:]
        elif linha.strip() and linha not in mapa:
            mapa[linha] = atual
    return mapa


def montar_entradas(modulos, origem, nomes_modulos):
    """Uma entrada por documento publicado, com a classificação automática e a data."""
    datas = datas_de_atualizacao(origem)
    entradas = []
    for mod in modulos:
        for p in mod["paginas"]:
            tipo, r_tipo = tipo_automatico(p["titulo"], p.get("cat"))
            pub, r_pub = publico_automatico(tipo)
            vis, r_vis = visao_automatica(p, mod)
            entre = mod["id"] == "visao-geral"
            if entre:
                # "Visão entre módulos" não é um módulo: vira tipo na Biblioteca (decisão do responsável, 20/10/2026)
                tipo, r_tipo = "visão entre módulos", "módulo:visão-geral"
                if re.search(r"diagnóstico|mapa|aderência|qualidade entre|integra|onde a corrente", p["titulo"].lower()):
                    pub, r_pub = ["diretoria", "GQ"], "entre-módulos:título"
                else:
                    pub, r_pub = [A_CLASSIFICAR], "sem-regra"
            entradas.append({
                "chave": f"{mod['id']}:{p['arq']}",
                "modulo": "entre-módulos" if entre else mod["id"],
                "titulo": p["titulo"],
                "tipo": tipo,
                "publico": "|".join(pub),
                "visao": vis,
                "classificacao": "auto",
                "regra": f"tipo={r_tipo}; público={r_pub}; visão={r_vis}",
                "revisado": "",
                "observacao": "",
                "_url": f"documentacao/{mod['id']}/{p['slug']}.html",
                "_word": (f"documentacao/arquivos/{mod['id']}/{Path(p['word']).name}" if p.get("word") else ""),
                "_data": datas.get(f"homologacao/{p['arq']}", datas.get(p["arq"], "")),
                "_modulo_nome": "Entre módulos" if entre else nomes_modulos.get(mod["id"], mod["id"]),
                "_ordem": 0,
            })
    return entradas


def ler_metadados(arq):
    if not Path(arq).exists():
        return {}
    with open(arq, newline="", encoding="utf-8-sig") as fh:
        return {r["chave"]: r for r in csv.DictReader(fh, delimiter=";")}


def aplicar_e_relatar(entradas, arq, atualizar=False):
    """Aplica o arquivo de metadados (fonte única) sobre a classificação automática. Devolve (entradas, relatório)."""
    existente = ler_metadados(arq)
    novas, por_chave = [], {e["chave"]: e for e in entradas}
    for e in entradas:
        linha = existente.get(e["chave"])
        if linha:
            for campo in ("modulo", "tipo", "publico", "visao"):
                if linha.get(campo):
                    e[campo] = linha[campo]
            e["classificacao"] = linha.get("classificacao") or "manual"
            e["revisado"] = linha.get("revisado", "")
        else:
            novas.append(e)
    sobrando = [c for c in existente if c not in por_chave]
    if atualizar and novas:
        escrever_cabecalho = not Path(arq).exists()
        with open(arq, "a", newline="", encoding="utf-8-sig" if escrever_cabecalho else "utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=CAMPOS, delimiter=";", extrasaction="ignore")
            if escrever_cabecalho:
                w.writeheader()
            for e in novas:
                w.writerow(e)
    a_classificar = [e for e in entradas if A_CLASSIFICAR in (e["tipo"], e["publico"], e["visao"])]
    rel = {"total": len(entradas), "do_arquivo": len(entradas) - len(novas), "sem_linha": len(novas),
           "linhas_sobrando": sobrando, "a_classificar": len(a_classificar), "revisadas": sum(1 for e in entradas if e["revisado"] == "sim"),
           "acrescentadas": len(novas) if atualizar else 0}
    return entradas, rel


def dados_json(entradas, modulos_ordem):
    ordem = {m: i for i, m in enumerate(modulos_ordem)}
    docs = []
    for e in sorted(entradas, key=lambda x: (ordem.get(x["modulo"], 99), x["tipo"], x["titulo"])):
        docs.append({"t": e["titulo"], "u": e["_url"], "w": e["_word"], "m": e["modulo"], "mn": e["_modulo_nome"], "tp": e["tipo"],
                     "v": e["visao"], "p": [x for x in e["publico"].split("|") if x], "d": e["_data"], "c": e["classificacao"]})
    return docs


JS = r"""
(function(){
  var dados=JSON.parse(document.getElementById('bib-dados').textContent);
  var docs=dados.docs, el={};
  ['q','modulo','tipo','publico','visao','formato','ordem'].forEach(function(k){el[k]=document.getElementById('f-'+k);});
  var lista=document.getElementById('bib-lista'), cont=document.getElementById('bib-cont');
  function opcoes(sel,vals,rot){var h='<option value="">Todos</option>';vals.forEach(function(v){h+='<option value="'+v[0]+'">'+v[1]+'</option>';});sel.innerHTML=h;}
  var mods=[],vistos={};docs.forEach(function(d){if(!vistos[d.m]){vistos[d.m]=1;mods.push([d.m,d.mn]);}});
  opcoes(el.modulo,mods);
  var tipos=Object.keys(docs.reduce(function(a,d){a[d.tp]=1;return a;},{})).sort(function(a,b){return a.localeCompare(b,'pt');});
  opcoes(el.tipo,tipos.map(function(t){return [t,t];}));
  var pubs=dados.publicos.concat(['a classificar']);opcoes(el.publico,pubs.map(function(t){return [t,t];}));
  opcoes(el.visao,dados.visoes.map(function(t){return [t,t];}));
  var qs=new URLSearchParams(location.search);
  ['modulo','tipo','publico','visao','formato','q'].forEach(function(k){if(qs.get(k)&&el[k])el[k].value=qs.get(k);});
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function norm(s){return s.normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();}
  function filtrar(){
    var q=norm(el.q.value.trim()),m=el.modulo.value,t=el.tipo.value,p=el.publico.value,v=el.visao.value,f=el.formato.value;
    var r=docs.filter(function(d){
      if(m&&d.m!==m)return false; if(t&&d.tp!==t)return false; if(v&&d.v!==v)return false;
      if(p&&d.p.indexOf(p)<0&&d.p.indexOf('todos')<0)return false; if(f==='word'&&!d.w)return false;
      if(q&&norm(d.t+' '+d.mn+' '+d.tp).indexOf(q)<0)return false; return true;});
    var o=el.ordem.value;
    if(o==='data')r.sort(function(a,b){return (b.d||'').localeCompare(a.d||'');});
    else if(o==='titulo')r.sort(function(a,b){return a.t.localeCompare(b.t,'pt');});
    cont.textContent=r.length+' de '+docs.length+' documentos'+(r.filter(function(d){return d.w;}).length?' · '+r.filter(function(d){return d.w;}).length+' com Word':'');
    lista.innerHTML=r.map(function(d){
      var pub=d.p.map(function(x){return '<span class="bib-pub">'+esc(x)+'</span>';}).join('');
      var data=d.d?d.d.split('-').reverse().join('/'):'—';
      return '<tr><td><a href="'+esc(d.u)+'">'+esc(d.t)+'</a>'+(d.c==='manual'?'':'')+'</td><td>'+esc(d.mn)+'</td><td>'+esc(d.tp)+'</td><td><span class="bib-vis bib-v-'+esc(d.v)+'">'+esc(d.v)+'</span></td><td>'+pub+'</td><td>'+data+'</td><td>'+(d.w?'<a href="'+esc(d.w)+'" download>Word</a>':'')+'</td></tr>';}).join('')||'<tr><td colspan="7">Nenhum documento com esses filtros.</td></tr>';
    var u=new URLSearchParams();['modulo','tipo','publico','visao','formato','q'].forEach(function(k){if(el[k].value)u.set(k,el[k].value);});
    history.replaceState(null,'',u.toString()?'?'+u.toString():location.pathname);
  }
  Object.keys(el).forEach(function(k){el[k].addEventListener(k==='q'?'input':'change',filtrar);});
  document.getElementById('f-limpar').addEventListener('click',function(){Object.keys(el).forEach(function(k){el[k].value=k==='ordem'?'modulo':'';});filtrar();});
  filtrar();
})();
"""


def pagina_biblioteca(entradas, modulos_ordem, cabecalho, rodape, E):
    docs = dados_json(entradas, modulos_ordem)
    n_word = sum(1 for d in docs if d["w"])
    dados = {"docs": docs, "publicos": PUBLICOS, "visoes": VISOES + [A_CLASSIFICAR]}
    corpo = f"""
<main id="conteudo" class="biblioteca">
  <section class="secao">
    <nav class="trilha" aria-label="Você está em"><a href="index.html">Início</a> › <span>Biblioteca</span></nav>
    <h1>Biblioteca</h1>
    <p class="secao-desc">Todos os {len(docs)} documentos do portal ({n_word} com versão em Word para baixar). Filtre por módulo, tipo, público e visão, ou procure pelo título.</p>
    <form class="bib-filtros" onsubmit="return false">
      <label>Procurar<input id="f-q" type="search" placeholder="título, módulo ou tipo"></label>
      <label>Módulo<select id="f-modulo"></select></label>
      <label>Tipo<select id="f-tipo"></select></label>
      <label>Público<select id="f-publico"></select></label>
      <label>Visão<select id="f-visao"></select></label>
      <label>Formato<select id="f-formato"><option value="">Todos</option><option value="word">Só com Word</option></select></label>
      <label>Ordenar<select id="f-ordem"><option value="modulo">Módulo e tipo</option><option value="data">Mais recentes</option><option value="titulo">Título</option></select></label>
      <button type="button" id="f-limpar" class="botao botao-secundario">Limpar</button>
    </form>
    <p id="bib-cont" class="bib-cont" role="status" aria-live="polite"></p>
    <div class="bib-tabela"><table>
      <thead><tr><th>Documento</th><th>Módulo</th><th>Tipo</th><th>Visão</th><th>Público</th><th>Atualizado</th><th>Word</th></tr></thead>
      <tbody id="bib-lista"></tbody>
    </table></div>
  </section>
</main>
<script type="application/json" id="bib-dados">{json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")}</script>
<script>{JS}</script>
"""
    return cabecalho("Biblioteca · iLabMedSys", "", "biblioteca") + corpo + rodape("")


CSS = """
/* Biblioteca */
.bib-filtros{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;align-items:end;background:var(--painel);border:1px solid var(--linha);border-radius:var(--raio);padding:16px;margin:14px 0 8px}
.bib-filtros label{display:flex;flex-direction:column;gap:4px;font-size:12px;font-weight:700;color:var(--suave);text-transform:uppercase;letter-spacing:.04em}
.bib-filtros input,.bib-filtros select{font:inherit;font-size:14px;padding:8px 10px;border-radius:8px;border:1px solid var(--linha);background:var(--painel);color:var(--tinta);text-transform:none;letter-spacing:0;font-weight:400}
.bib-cont{margin:6px 0 10px;color:var(--suave);font-size:13px}
.bib-tabela{overflow-x:auto;background:var(--painel);border:1px solid var(--linha);border-radius:var(--raio)}
.bib-tabela table{width:100%;border-collapse:collapse;font-size:13.5px}
.bib-tabela th,.bib-tabela td{padding:9px 12px;text-align:left;border-bottom:1px solid var(--linha);vertical-align:top}
.bib-tabela th{position:sticky;top:0;background:var(--painel2);font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--suave)}
.bib-pub{display:inline-block;margin:0 4px 2px 0;padding:1px 8px;border-radius:10px;background:var(--painel2);border:1px solid var(--linha);font-size:11.5px}
.bib-vis{display:inline-block;padding:1px 9px;border-radius:10px;font-size:12px;font-weight:700;color:#fff;background:#6b7a8c}
.bib-v-novo{background:#1f6feb}.bib-v-ideal{background:#7b3fe4}.bib-v-geral{background:#334155}
"""
