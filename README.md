# iLabMedSys — portal da documentação

A página inicial (`index.html`) é o **portal iLabMedSys** (novo nome do LabMedSys): a documentação da homologação do sistema, por módulo, com fluxos ilustrados, busca e documentos em Word para baixar. A apresentação do iLabPharma continua disponível, sem mudanças, em `apresentacao.html`.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `index.html` | Página inicial do portal (gerada) |
| `apresentacao.html` e arquivos `journey-*`, `home.*`, `app.js`, `styles.css` | Apresentação iLabPharma (antigo `index.html`) |
| `documentacao/<módulo>/` | Páginas dos módulos e dos documentos (geradas) |
| `documentacao/arquivos/`, `documentacao/img/` | Word para baixar, fluxogramas e capturas (gerados) |
| `portal/` | Visual (`portal.css`), busca e tema (`portal.js`), índice de busca (`busca.json`, gerado) |
| `ferramentas/gerar_portal.py` | Gerador do portal |

## Como atualizar

Os documentos vêm do repositório privado `LabMedsys_homol` (pasta `homologacao/`). Depois de qualquer mudança lá:

```
pip install markdown
python3 ferramentas/gerar_portal.py --origem ../LabMedsys_homol --destino . --relatorio /tmp/retirado.md
```

Para incluir um documento ou um módulo novo, edite o catálogo `MODULOS` no início do gerador.

**O site é público.** O gerador retira o conteúdo de segurança: os arquivos `03-achados-de-seguranca`, as seções com "segurança" no título, os blocos confidenciais, as linhas com achados `SEG-` e as frases que descrevem como explorar uma falha. Os Word dos documentos limpos são gerados de novo a partir do texto limpo. O relatório indicado em `--relatorio` lista tudo o que foi retirado e **não deve ser publicado**.

---

# iLabPharma — Process Intelligence

Experiência web interativa para apresentação e exploração de processos da indústria farmacêutica.

## Conceito

O projeto não apresenta o ERP como produto. O foco é tornar os **processos** visualmente compreensíveis, navegáveis e conectados.

Cada etapa do fluxo pode ser explorada para revelar objetivo, regras, responsabilidades, pontos de atenção e relações com outros módulos.

## MVP atual

- Identidade visual inspirada no material institucional do iLabPharma.
- Mapa inicial de processos.
- Fluxo interativo de **Recebimento de Materiais**.
- Fluxo interativo de **Quarentena de Materiais e Produtos**.
- Painel contextual das etapas.
- Busca por processo/etapa.
- Visão clara das áreas/módulos envolvidos.
- Modo claro/escuro.
- Layout responsivo.

## Próximos módulos

- Principal
- Estoque
- Controle da Qualidade
- Garantia da Qualidade
- Controle de Documentos

## Próxima evolução

1. Refinar a linguagem visual dos fluxos.
2. Transformar todos os processos documentados em experiências interativas.
3. Criar exceções e decisões como caminhos visuais.
4. Adicionar indicadores, entradas, saídas, responsáveis e documentos relacionados.
5. Criar novos fluxos a partir das especificações funcionais.
6. Publicar a experiência com GitHub Pages.

> Conteúdo do MVP baseado nas especificações funcionais de processos fornecidas para o projeto.
