# Pitch de vendas do iLabPharma

Página única, em `pitch/index.html` (no site: `/pitch/`). Mostra como o iLabPharma funciona, a aderência às normas da ANVISA (RDC 658/2022 e Guia 33/2020) e o que será entregue. A página tem `noindex` (não aparece em buscadores) enquanto está em teste.

Esta pasta é independente do portal de homologação e da apresentação antiga (`apresentacao.html`). Foi desenvolvida no repositório `Nardacci/Apresentacao` e trazida para cá para teste; depois de aprovada, migra para o repositório oficial.

## Regras de conteúdo (decisões do responsável, 15/10/2026)
- Foco no sistema legado. Nada de falhas, defeitos ou limitações.
- Nada de segurança (acesso, senhas, chaves). Temas de acesso, senha e banco de dados ficam fora.
- Nada inventado: tudo vem da documentação de homologação.
- Nenhum ponto da norma aparece como "atende": ou "Base pronta" (a função existe) ou "Será entregue".
- É um pitch de vendas: sem códigos nem termos técnicos de homologação.

## Como o conteúdo é montado
- `ferramentas/conteudo.py`: o texto de venda. Editar aqui.
- `ferramentas/montar_dados.py [pasta homologacao]`: gera `dados/dados.js` com o texto e os títulos das etapas dos fluxos (repositório privado `LabMedsys_homol`).
- `pitch.css` e `pitch.js`: desenham a página, sem conteúdo próprio.
