window.DADOS={
 "etapas": [
  {
   "id": "industria",
   "num": "01",
   "nome": "Indústria",
   "modulos": [
    "Principal"
   ],
   "pergunta": "Quem irá fabricar o medicamento?",
   "titulo": "Antes de produzir, a indústria precisa existir.",
   "texto": "A operação começa pela definição da organização, das pessoas que participam dos processos e dos níveis de acesso necessários para executar e controlar as atividades.",
   "faz": [
    "Cadastro de profissionais e de suas funções",
    "Contas de usuários, perfis e permissões por função",
    "Estrutura organizacional e locais da empresa",
    "Pessoas jurídicas: fornecedores, clientes e fabricantes",
    "Tabelas de apoio usadas por todos os módulos",
    "Histórico das alterações, campo a campo, na maior parte dos cadastros"
   ],
   "resultado": "A indústria estruturada no iLabPharma: pessoas, acessos e cadastros que sustentam todos os outros módulos.",
   "conecta": [
    "Todos os módulos usam os cadastros do Principal"
   ],
   "imagem": [
    "fluxo-modulo-principal.html",
    "Ver o fluxograma do módulo Principal"
   ],
   "fluxos": []
  },
  {
   "id": "materiais",
   "num": "02",
   "nome": "Materiais e armazenagem",
   "modulos": [
    "Estoque"
   ],
   "pergunta": "Como o material chega, é guardado e chega à produção?",
   "titulo": "Do pedido de compra ao material na mão da produção.",
   "texto": "O Estoque acompanha cada lote desde a compra e o recebimento, passando pela quarentena e pelo endereçamento, até a entrega à produção, ao cliente ou ao laboratório.",
   "faz": [
    "Análise da necessidade de compra, pedido e avaliação do fornecedor em cada entrega",
    "Recebimento com portaria, conferência da nota, quantidade e pesagem",
    "Quarentena: o lote só segue depois do laudo do Controle da Qualidade",
    "Endereçamento e movimentação por rua, coluna, andar e local",
    "Reanálise e revalidação periódica da validade do lote",
    "Solicitação, separação e atendimento à produção, com pesagem quando exigida",
    "Devolução de sobra, entradas avulsas e entrada do produto acabado",
    "Remessa e expedição, inclusive por guia, e inventário com até três contagens",
    "Kits para clientes, com validade mínima, e almoxarifado especial de amostras do CQ"
   ],
   "resultado": "Cada lote com sua situação, seu endereço e seu histórico, do recebimento à saída.",
   "conecta": [
    "Controle da Qualidade (solicitação de análise e laudo)",
    "Produção (solicitação de material e entrada do produto acabado)",
    "Comercial e Rastreabilidade (remessa)"
   ],
   "fluxos": [
    {
     "nome": "Recebimento de materiais",
     "linha": "Da estrutura do almoxarifado à disponibilização do material.",
     "fases": [
      {
       "nome": "Estrutura e cadastros",
       "etapas": [
        {
         "t": "Cadastrar almoxarifado",
         "dec": false
        },
        {
         "t": "Estrutura física",
         "dec": false
        },
        {
         "t": "Cadastro de materiais",
         "dec": false
        },
        {
         "t": "Configurações",
         "dec": false
        }
       ]
      },
      {
       "nome": "Inspeção e aprovação",
       "etapas": [
        {
         "t": "Inspeção (se aplicável)",
         "dec": false
        },
        {
         "t": "Aprovação (se aplicável)",
         "dec": false
        }
       ]
      },
      {
       "nome": "Recebimento e conferência",
       "etapas": [
        {
         "t": "Recebimento",
         "dec": false
        },
        {
         "t": "Conferência",
         "dec": false
        }
       ]
      },
      {
       "nome": "Entrada e disponibilização",
       "etapas": [
        {
         "t": "Entrada no Estoque",
         "dec": false
        },
        {
         "t": "Endereçamento",
         "dec": false
        },
        {
         "t": "Disponibilização",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Quarentena de materiais e produtos",
     "linha": "Do item parametrizado ao material aprovado movimentado para o seu endereço.",
     "fases": [
      {
       "nome": "Parametrização e entrada",
       "etapas": [
        {
         "t": "Parametrizar item",
         "dec": false
        },
        {
         "t": "Entrada em quarentena",
         "dec": false
        }
       ]
      },
      {
       "nome": "Solicitação e amostragem",
       "etapas": [
        {
         "t": "Solicitação de análise",
         "dec": false
        },
        {
         "t": "Programar amostragem",
         "dec": false
        },
        {
         "t": "Pesagem e separação",
         "dec": false
        }
       ]
      },
      {
       "nome": "Análise",
       "etapas": [
        {
         "t": "Programar análise",
         "dec": false
        },
        {
         "t": "Executar análise",
         "dec": false
        }
       ]
      },
      {
       "nome": "Laudo e movimentação",
       "etapas": [
        {
         "t": "Emitir laudo",
         "dec": false
        },
        {
         "t": "Movimentar aprovado",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Compras e avaliação do fornecedor",
     "linha": "Da necessidade de estoque ao pedido, à baixa no recebimento e à avaliação do fornecedor.",
     "fases": [
      {
       "nome": "Análise da necessidade",
       "etapas": [
        {
         "t": "Analisar a Curva ABC",
         "dec": false
        },
        {
         "t": "Analisar o estoque",
         "dec": false
        }
       ]
      },
      {
       "nome": "Pedido de compra",
       "etapas": [
        {
         "t": "Gerar o pedido a partir da análise",
         "dec": false
        },
        {
         "t": "Registrar ou ajustar o pedido de compra",
         "dec": false
        }
       ]
      },
      {
       "nome": "Recebimento e baixa",
       "etapas": [
        {
         "t": "Receber pelo fluxo de Recebimento",
         "dec": false
        },
        {
         "t": "Baixar o pedido (Recebimento do Item)",
         "dec": false
        }
       ]
      },
      {
       "nome": "Avaliação do fornecedor",
       "etapas": [
        {
         "t": "Avaliar o fornecedor na entrega",
         "dec": false
        },
        {
         "t": "O fornecedor está aprovado para entregar?",
         "dec": true
        }
       ]
      }
     ]
    },
    {
     "nome": "Movimentação interna",
     "linha": "Endereçamento e movimentação de lotes, com consulta de saldo e de histórico.",
     "fases": [
      {
       "nome": "Estrutura de endereços",
       "etapas": [
        {
         "t": "Cadastrar endereço do estoque",
         "dec": false
        },
        {
         "t": "Ligar grupo de usuário ao almoxarifado",
         "dec": false
        }
       ]
      },
      {
       "nome": "Endereçamento",
       "etapas": [
        {
         "t": "Endereçar o lote",
         "dec": false
        }
       ]
      },
      {
       "nome": "Movimentação entre endereços",
       "etapas": [
        {
         "t": "Informar tipo de movimentação e item",
         "dec": false
        },
        {
         "t": "Selecionar lote e endereço de origem",
         "dec": false
        },
        {
         "t": "Escolher o destino",
         "dec": false
        },
        {
         "t": "O destino comporta o item?",
         "dec": true
        },
        {
         "t": "Confirmar com justificativa",
         "dec": false
        }
       ]
      },
      {
       "nome": "Consulta e rastreabilidade",
       "etapas": [
        {
         "t": "Consultar disponibilidade e endereços",
         "dec": false
        },
        {
         "t": "Consultar histórico do lote e do item",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Reprovado, reanálise e revalidação",
     "linha": "Destino do lote depois da análise e controle periódico da validade.",
     "fases": [
      {
       "nome": "Resultado da análise",
       "etapas": [
        {
         "t": "Consultar o resultado na Movimentação de Quarentena",
         "dec": false
        },
        {
         "t": "O lote foi aprovado?",
         "dec": true
        },
        {
         "t": "Movimentar o aprovado para armazenamento",
         "dec": false
        },
        {
         "t": "Movimentar o reprovado para o refugo",
         "dec": false
        }
       ]
      },
      {
       "nome": "Reanálise",
       "etapas": [
        {
         "t": "Consultar a Agenda de Reanálise",
         "dec": false
        },
        {
         "t": "Agendar a reanálise (agenda ou avulsa)",
         "dec": false
        },
        {
         "t": "Resultado da reanálise",
         "dec": false
        }
       ]
      },
      {
       "nome": "Revalidação da validade",
       "etapas": [
        {
         "t": "Solicitar a revalidação do lote",
         "dec": false
        },
        {
         "t": "Nova validade definida pelo CQ",
         "dec": false
        }
       ]
      },
      {
       "nome": "Consulta e relatórios",
       "etapas": [
        {
         "t": "Consultar a disponibilidade separada por situação",
         "dec": false
        },
        {
         "t": "Emitir relatórios",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Solicitação e atendimento à produção",
     "linha": "Do pedido de material à entrega pelo Estoque, com pesagem.",
     "fases": [
      {
       "nome": "Solicitação",
       "etapas": [
        {
         "t": "Registrar a solicitação de material",
         "dec": false
        },
        {
         "t": "A solicitação precisa de aprovação?",
         "dec": true
        }
       ]
      },
      {
       "nome": "Separação",
       "etapas": [
        {
         "t": "Separar o material",
         "dec": false
        },
        {
         "t": "Pesar, quando exigido",
         "dec": false
        }
       ]
      },
      {
       "nome": "Atendimento",
       "etapas": [
        {
         "t": "Atender a solicitação",
         "dec": false
        },
        {
         "t": "Encerrar a solicitação",
         "dec": false
        }
       ]
      },
      {
       "nome": "Outras saídas e consultas",
       "etapas": [
        {
         "t": "Registrar saída de material (outras)",
         "dec": false
        },
        {
         "t": "Consultar solicitações e histórico do lote",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Devolução e entradas",
     "linha": "Sobra da produção, devoluções, entradas avulsas e produto acabado.",
     "fases": [
      {
       "nome": "Devolução da produção",
       "etapas": [
        {
         "t": "Registrar a devolução da produção",
         "dec": false
        }
       ]
      },
      {
       "nome": "Devolução e entradas avulsas",
       "etapas": [
        {
         "t": "Registrar a devolução de material",
         "dec": false
        },
        {
         "t": "Registrar entrada de material (outras)",
         "dec": false
        },
        {
         "t": "Endereçar e enviar para análise",
         "dec": false
        }
       ]
      },
      {
       "nome": "Entrada do produto acabado",
       "etapas": [
        {
         "t": "Registrar a entrada de materiais - produção",
         "dec": false
        },
        {
         "t": "Análise de produto acabado",
         "dec": false
        },
        {
         "t": "Entrada de produção (serviços)",
         "dec": false
        }
       ]
      },
      {
       "nome": "Liberação e consulta",
       "etapas": [
        {
         "t": "Liberar ou reprovar pelo CQ",
         "dec": false
        },
        {
         "t": "Consultar histórico do lote",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Remessa e expedição",
     "linha": "Saída de material, por guia ou por nota fiscal, com elo para a rastreabilidade.",
     "fases": [
      {
       "nome": "Montar a remessa",
       "etapas": [
        {
         "t": "Registrar a remessa de material",
         "dec": false
        },
        {
         "t": "Escolher os lotes",
         "dec": false
        },
        {
         "t": "Remessa por guia (GMM), quando aplicável",
         "dec": false
        }
       ]
      },
      {
       "nome": "Confirmar e expedir",
       "etapas": [
        {
         "t": "Confirmar a remessa",
         "dec": false
        },
        {
         "t": "O módulo Rastreabilidade está ativo?",
         "dec": true
        },
        {
         "t": "Saída por nota fiscal",
         "dec": false
        }
       ]
      },
      {
       "nome": "Consulta",
       "etapas": [
        {
         "t": "Consultar remessas e relatório de saída",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Inventário",
     "linha": "Contagem física, comparação com o saldo e ajuste com justificativa.",
     "fases": [
      {
       "nome": "Abertura",
       "etapas": [
        {
         "t": "Gerar o inventário",
         "dec": false
        },
        {
         "t": "Há recebimento ou solicitação pendente?",
         "dec": true
        },
        {
         "t": "Travar os endereços",
         "dec": false
        }
       ]
      },
      {
       "nome": "Contagem",
       "etapas": [
        {
         "t": "Registrar a contagem",
         "dec": false
        },
        {
         "t": "A contagem bate com o sistema?",
         "dec": true
        },
        {
         "t": "Justificar a divergência",
         "dec": false
        }
       ]
      },
      {
       "nome": "Apuração",
       "etapas": [
        {
         "t": "Apurar o inventário",
         "dec": false
        },
        {
         "t": "Cancelar ou reabrir, se necessário",
         "dec": false
        }
       ]
      },
      {
       "nome": "Consulta",
       "etapas": [
        {
         "t": "Relatórios do inventário",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Kits",
     "linha": "Cadastro, planejamento com validade mínima, envio e controle dos kits enviados.",
     "fases": [
      {
       "nome": "Definição do kit",
       "etapas": [
        {
         "t": "Configurar os parâmetros de kit",
         "dec": false
        },
        {
         "t": "Cadastrar o kit",
         "dec": false
        }
       ]
      },
      {
       "nome": "Planejamento",
       "etapas": [
        {
         "t": "Planejar os kits",
         "dec": false
        },
        {
         "t": "Analisar o planejamento",
         "dec": false
        }
       ]
      },
      {
       "nome": "Solicitação e envio",
       "etapas": [
        {
         "t": "Solicitar os kits",
         "dec": false
        },
        {
         "t": "Enviar por guia de movimentação",
         "dec": false
        }
       ]
      },
      {
       "nome": "Controle dos kits enviados",
       "etapas": [
        {
         "t": "Controlar os kits e os lotes dos componentes",
         "dec": false
        },
        {
         "t": "Há lote vencendo ou vencido?",
         "dec": true
        },
        {
         "t": "Relatórios de kits",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Almoxarifado do Controle da Qualidade",
     "linha": "Guarda das amostras de referência, retenção e estabilidade.",
     "fases": [
      {
       "nome": "Estrutura",
       "etapas": [
        {
         "t": "Marcar o almoxarifado como referência, retenção ou estabilidade",
         "dec": false
        }
       ]
      },
      {
       "nome": "Entrada da amostra",
       "etapas": [
        {
         "t": "Registrar a entrada (referência, retenção ou estabilidade)",
         "dec": false
        },
        {
         "t": "A amostra é de estabilidade?",
         "dec": true
        }
       ]
      },
      {
       "nome": "Movimentação e saída",
       "etapas": [
        {
         "t": "Movimentar entre endereços",
         "dec": false
        },
        {
         "t": "Registrar a saída da amostra",
         "dec": false
        }
       ]
      },
      {
       "nome": "Consulta",
       "etapas": [
        {
         "t": "Consultar a disponibilidade",
         "dec": false
        },
        {
         "t": "O prazo de guarda é controlado?",
         "dec": true
        }
       ]
      }
     ]
    }
   ]
  },
  {
   "id": "fabricacao",
   "num": "03",
   "nome": "Medicamento e fabricação",
   "modulos": [
    "Produção",
    "OPE"
   ],
   "pergunta": "Como o medicamento é definido e fabricado?",
   "titulo": "Agora o medicamento deixa de ser uma especificação e passa a existir fisicamente.",
   "texto": "A Produção define o que se fabrica, prepara a área, obtém as autorizações, gera o lote e registra cada etapa. O OPE monta o modelo do registro eletrônico de lote.",
   "faz": [
    "Cadastro de insumos, produto, fórmula e lote padrão",
    "Ordem de produção com aprovação por permissão própria",
    "Preparação da área: limpeza, calibração, qualificação e manutenção de salas, equipamentos e instrumentos",
    "Autorização das áreas antes de produzir e geração do lote",
    "Registro eletrônico do lote: etapas, subetapas e campos por produto, com controle em processo",
    "Reconciliação e liberação ao final da produção",
    "Terceirização de etapas e pedido de nova validade",
    "OPE: gerador do modelo do registro de lote, com etapas, campos, cálculos e assinaturas"
   ],
   "resultado": "O lote fabricado com o registro completo de cada etapa.",
   "conecta": [
    "Estoque (material, entrada do produto acabado)",
    "Controle da Qualidade (análises no processo, água e ambiente)",
    "Garantia da Qualidade (desvios, mudanças)"
   ],
   "imagem": [
    "fluxo-estoque-quarentena-producao.html",
    "Ver o fluxograma Estoque, Quarentena e Produção"
   ],
   "fluxos": [
    {
     "nome": "Produto, fórmula e ordem de produção",
     "linha": "Os cadastros que definem o que se fabrica.",
     "fases": [
      {
       "nome": "Insumos",
       "etapas": [
        {
         "t": "Cadastrar insumos",
         "dec": false
        }
       ]
      },
      {
       "nome": "Produto",
       "etapas": [
        {
         "t": "Cadastrar o produto e a fórmula",
         "dec": false
        },
        {
         "t": "Alterar ou duplicar",
         "dec": false
        }
       ]
      },
      {
       "nome": "Lote padrão",
       "etapas": [
        {
         "t": "Montar o lote padrão",
         "dec": false
        },
        {
         "t": "Aprovar",
         "dec": false
        }
       ]
      },
      {
       "nome": "Ordem de produção",
       "etapas": [
        {
         "t": "Cadastrar a ordem",
         "dec": false
        },
        {
         "t": "Enviar o modelo XML",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Preparação da área",
     "linha": "Programar, registrar e liberar limpeza, calibração, qualificação e manutenção.",
     "fases": [
      {
       "nome": "Programar",
       "etapas": [
        {
         "t": "Programação",
         "dec": false
        }
       ]
      },
      {
       "nome": "Registrar",
       "etapas": [
        {
         "t": "Registro",
         "dec": false
        },
        {
         "t": "Revisão",
         "dec": false
        }
       ]
      },
      {
       "nome": "Liberar",
       "etapas": [
        {
         "t": "Revisado e na validade?",
         "dec": true
        },
        {
         "t": "Autorização da produção",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Autorização, início e final",
     "linha": "Da solicitação de autorizações ao produto acabado no Estoque.",
     "fases": [
      {
       "nome": "Solicitação",
       "etapas": [
        {
         "t": "Solicitar autorizações",
         "dec": false
        }
       ]
      },
      {
       "nome": "Autorizações",
       "etapas": [
        {
         "t": "Estoque",
         "dec": false
        },
        {
         "t": "Ambientes, equipamentos, instrumentos, água",
         "dec": false
        },
        {
         "t": "GQ e CQ",
         "dec": false
        },
        {
         "t": "Todas respondidas?",
         "dec": true
        }
       ]
      },
      {
       "nome": "Lote",
       "etapas": [
        {
         "t": "Autorizar a produção",
         "dec": false
        },
        {
         "t": "Gerar número de lote",
         "dec": false
        }
       ]
      },
      {
       "nome": "Fabricação",
       "etapas": [
        {
         "t": "Registro da produção",
         "dec": false
        }
       ]
      },
      {
       "nome": "Final",
       "etapas": [
        {
         "t": "Final da produção",
         "dec": false
        },
        {
         "t": "Reconciliação",
         "dec": false
        },
        {
         "t": "Liberação da produção",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Registro de lote",
     "linha": "Etapas, subetapas e campos do modelo de cada produto.",
     "fases": [
      {
       "nome": "Abrir",
       "etapas": [
        {
         "t": "Abrir o Registro da Produção",
         "dec": false
        },
        {
         "t": "Campos automáticos",
         "dec": false
        }
       ]
      },
      {
       "nome": "Preencher",
       "etapas": [
        {
         "t": "Digitar os campos",
         "dec": false
        },
        {
         "t": "Assinar",
         "dec": false
        },
        {
         "t": "Salvar",
         "dec": false
        }
       ]
      },
      {
       "nome": "Controles",
       "etapas": [
        {
         "t": "Controle em processo",
         "dec": false
        },
        {
         "t": "Análise do CQ aprovada?",
         "dec": true
        },
        {
         "t": "Liberar a subetapa",
         "dec": false
        }
       ]
      },
      {
       "nome": "Encerrar",
       "etapas": [
        {
         "t": "Última subetapa",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Terceirização e validade",
     "linha": "Etapas terceirizadas e pedido de nova validade do lote.",
     "fases": [
      {
       "nome": "Terceirização",
       "etapas": [
        {
         "t": "Indicar a etapa terceirizada",
         "dec": false
        },
        {
         "t": "Confirmar ou cancelar",
         "dec": false
        }
       ]
      },
      {
       "nome": "Validade da OPE",
       "etapas": [
        {
         "t": "Pedir nova validade",
         "dec": false
        },
        {
         "t": "Confirmação e aprovação final",
         "dec": false
        },
        {
         "t": "Gravar a nova validade",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "OPE: modelo do registro de lote",
     "linha": "Estrutura, conteúdo e entrega do modelo à Produção.",
     "fases": [
      {
       "nome": "Estrutura",
       "etapas": [
        {
         "t": "Criar o modelo do produto",
         "dec": false
        },
        {
         "t": "Etapas e subetapas",
         "dec": false
        }
       ]
      },
      {
       "nome": "Conteúdo",
       "etapas": [
        {
         "t": "Texto e campos",
         "dec": false
        },
        {
         "t": "Configurar campos",
         "dec": false
        },
        {
         "t": "Validações e cálculos",
         "dec": false
        },
        {
         "t": "Controle em processo e final",
         "dec": false
        }
       ]
      },
      {
       "nome": "Para a Produção",
       "etapas": [
        {
         "t": "Conferir e imprimir",
         "dec": false
        },
        {
         "t": "Baixar e enviar na ordem",
         "dec": false
        }
       ]
      }
     ]
    }
   ]
  },
  {
   "id": "cq",
   "num": "04",
   "nome": "Controle da Qualidade",
   "modulos": [
    "Controle da Qualidade"
   ],
   "pergunta": "Como o material e o produto são avaliados?",
   "titulo": "Nenhum lote segue sem a análise do laboratório.",
   "texto": "O Controle da Qualidade recebe a solicitação de análise, orienta a amostragem, registra os resultados e emite o laudo. Cuida também da água, do ambiente e da estabilidade.",
   "faz": [
    "Regras de amostragem e de análise cadastradas por item",
    "Solicitação de análise vinda do Estoque, da Produção ou aberta no próprio laboratório",
    "Amostragem com amostrador e verificador diferentes e checklist",
    "Quantidades separadas para análise, retenção, referência e estabilidade",
    "Resultados conferidos contra os limites cadastrados",
    "Laudo final e etiqueta",
    "Monitoramento de água e de ambiente",
    "Programa de estabilidade com abertura automática pelo Estoque"
   ],
   "resultado": "Laudo emitido e lote com o seu destino definido.",
   "conecta": [
    "Estoque (o laudo decide o destino do lote)",
    "Produção (análises e monitoramento ambiental)"
   ],
   "fluxos": [
    {
     "nome": "Regras de amostragem e de análise",
     "linha": "Do item às regras de amostragem e de análise de cada análise.",
     "fases": [
      {
       "nome": "Item",
       "etapas": [
        {
         "t": "Escolher o item",
         "dec": false
        },
        {
         "t": "O item já existe no CQ?",
         "dec": true
        }
       ]
      },
      {
       "nome": "Amostragem",
       "etapas": [
        {
         "t": "Cadastrar a regra de amostragem",
         "dec": false
        },
        {
         "t": "Itens, utensílios e checklist",
         "dec": false
        }
       ]
      },
      {
       "nome": "Análise",
       "etapas": [
        {
         "t": "Cadastrar as regras de análise",
         "dec": false
        },
        {
         "t": "Alterar a especificação",
         "dec": false
        }
       ]
      },
      {
       "nome": "Uso",
       "etapas": [
        {
         "t": "Abrir a análise",
         "dec": false
        },
        {
         "t": "Digitar e decidir",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Solicitação, análise e laudo",
     "linha": "Da solicitação à amostragem, aos resultados, ao laudo e à etiqueta.",
     "fases": [
      {
       "nome": "Solicitação",
       "etapas": [
        {
         "t": "Receber ou abrir a solicitação",
         "dec": false
        },
        {
         "t": "Tem fase de coleta?",
         "dec": true
        }
       ]
      },
      {
       "nome": "Amostragem",
       "etapas": [
        {
         "t": "Programar a amostragem",
         "dec": false
        },
        {
         "t": "Registrar a amostragem",
         "dec": false
        }
       ]
      },
      {
       "nome": "Análise",
       "etapas": [
        {
         "t": "Programar a análise",
         "dec": false
        },
        {
         "t": "Estoque separou a amostra?",
         "dec": true
        },
        {
         "t": "Digitar os resultados",
         "dec": false
        }
       ]
      },
      {
       "nome": "Laudo",
       "etapas": [
        {
         "t": "Aprovar ou reprovar",
         "dec": false
        },
        {
         "t": "Emitir o laudo",
         "dec": false
        },
        {
         "t": "Estoque atualiza a análise",
         "dec": false
        },
        {
         "t": "Gerar etiqueta",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Água e ambiente",
     "linha": "Agenda de coletas, análise e retorno à Produção.",
     "fases": [
      {
       "nome": "Agenda",
       "etapas": [
        {
         "t": "Agendar a coleta",
         "dec": false
        }
       ]
      },
      {
       "nome": "Coleta e análise",
       "etapas": [
        {
         "t": "Programar e registrar a amostragem",
         "dec": false
        },
        {
         "t": "Programar, digitar e emitir o laudo",
         "dec": false
        }
       ]
      },
      {
       "nome": "Produção",
       "etapas": [
        {
         "t": "O laudo do CQ chega à Produção?",
         "dec": true
        },
        {
         "t": "Autorizar o ponto de água",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Estabilidade",
     "linha": "Do estudo à solicitação de cada tempo e ao relatório final.",
     "fases": [
      {
       "nome": "Regra",
       "etapas": [
        {
         "t": "Cadastrar a regra do produto",
         "dec": false
        }
       ]
      },
      {
       "nome": "Abertura",
       "etapas": [
        {
         "t": "Estoque pede a abertura",
         "dec": false
        },
        {
         "t": "O produto tem regra?",
         "dec": true
        },
        {
         "t": "Abrir o estudo",
         "dec": false
        }
       ]
      },
      {
       "nome": "Execução",
       "etapas": [
        {
         "t": "Gerar a solicitação do tempo",
         "dec": false
        },
        {
         "t": "Amostragem, análise e laudo",
         "dec": false
        }
       ]
      },
      {
       "nome": "Encerramento",
       "etapas": [
        {
         "t": "Interromper?",
         "dec": true
        },
        {
         "t": "Finalizar o estudo",
         "dec": false
        },
        {
         "t": "Imprimir o relatório final",
         "dec": false
        }
       ]
      }
     ]
    }
   ]
  },
  {
   "id": "gq",
   "num": "05",
   "nome": "Garantia da Qualidade",
   "modulos": [
    "Garantia da Qualidade"
   ],
   "pergunta": "Como a qualidade é governada?",
   "titulo": "A qualidade como sistema, não só como análise.",
   "texto": "A Garantia da Qualidade reúne os processos que investigam, corrigem, previnem e demonstram a conformidade da operação.",
   "faz": [
    "Desvios e CAPA, da ação imediata ao monitoramento e encerramento",
    "Controle de mudanças, da solicitação à aprovação do produto",
    "Autoinspeção e auditoria: roteiros, programação, execução e relatório final",
    "Treinamento: matriz, turmas, avaliação e acompanhamento de vigentes, pendentes e vencidos",
    "Assuntos regulatórios: obrigações e registro de produto na ANVISA",
    "Número sequencial, situação de cada etapa e histórico campo a campo"
   ],
   "resultado": "Cada não conformidade investigada, cada mudança avaliada e cada pessoa treinada, com registro.",
   "conecta": [
    "Estoque, Produção e Controle da Qualidade (origem dos desvios)",
    "Controle de Documentos (treinamento por POP)"
   ],
   "fluxos": [
    {
     "nome": "Desvios e CAPA",
     "linha": "Do registro do desvio ao encerramento dos planos corretivo e preventivo.",
     "fases": [
      {
       "nome": "Registro",
       "etapas": [
        {
         "t": "Registrar o Relatório de Desvios",
         "dec": false
        },
        {
         "t": "Registrar a ação corretiva imediata",
         "dec": false
        }
       ]
      },
      {
       "nome": "Triagem",
       "etapas": [
        {
         "t": "Pré-avaliar o desvio",
         "dec": false
        },
        {
         "t": "Envolve outras áreas?",
         "dec": true
        }
       ]
      },
      {
       "nome": "Avaliação",
       "etapas": [
        {
         "t": "Avaliar o Relatório de Desvios",
         "dec": false
        },
        {
         "t": "Necessário abrir CAPA?",
         "dec": true
        }
       ]
      },
      {
       "nome": "CAPA corretiva",
       "etapas": [
        {
         "t": "Elaborar o Relatório de CAPA",
         "dec": false
        },
        {
         "t": "Elaborar e executar o plano corretivo",
         "dec": false
        },
        {
         "t": "Plano corretivo aprovado?",
         "dec": true
        }
       ]
      },
      {
       "nome": "CAPA preventiva",
       "etapas": [
        {
         "t": "Elaborar e executar o plano preventivo",
         "dec": false
        },
        {
         "t": "Monitorar e encerrar",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Controle de mudanças",
     "linha": "Da solicitação à avaliação pelas áreas, ao plano de ação e à aprovação do produto.",
     "fases": [
      {
       "nome": "Solicitação",
       "etapas": [
        {
         "t": "Registrar a solicitação de mudança",
         "dec": false
        }
       ]
      },
      {
       "nome": "Revisão",
       "etapas": [
        {
         "t": "Pré-avaliar (revisar) a solicitação",
         "dec": true
        },
        {
         "t": "Definir as áreas que avaliam",
         "dec": false
        }
       ]
      },
      {
       "nome": "Avaliação",
       "etapas": [
        {
         "t": "Cada área avalia",
         "dec": false
        },
        {
         "t": "Liberar a avaliação?",
         "dec": true
        }
       ]
      },
      {
       "nome": "Implementação",
       "etapas": [
        {
         "t": "Elaborar o plano de ação",
         "dec": false
        },
        {
         "t": "Executar as ações",
         "dec": false
        },
        {
         "t": "Finalizar o plano?",
         "dec": true
        }
       ]
      },
      {
       "nome": "Produto",
       "etapas": [
        {
         "t": "Aprovar no Controle Mudança Produto",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Autoinspeção e auditoria",
     "linha": "Dos cadastros à programação, execução e avaliação.",
     "fases": [
      {
       "nome": "Cadastros",
       "etapas": [
        {
         "t": "Cadastrar roteiros de perguntas",
         "dec": false
        },
        {
         "t": "Cadastrar a autoinspeção ou auditoria",
         "dec": false
        }
       ]
      },
      {
       "nome": "Programação",
       "etapas": [
        {
         "t": "Programar a execução",
         "dec": false
        },
        {
         "t": "Iniciar a programação",
         "dec": false
        }
       ]
      },
      {
       "nome": "Execução",
       "etapas": [
        {
         "t": "Registrar as respostas",
         "dec": false
        },
        {
         "t": "Avançar para avaliação",
         "dec": false
        }
       ]
      },
      {
       "nome": "Avaliação",
       "etapas": [
        {
         "t": "Avaliar e registrar os desvios",
         "dec": false
        },
        {
         "t": "Finalizar ou reabrir?",
         "dec": true
        }
       ]
      }
     ]
    },
    {
     "nome": "Treinamento",
     "linha": "Dos cadastros à turma, à avaliação e ao acompanhamento.",
     "fases": [
      {
       "nome": "Cadastros",
       "etapas": [
        {
         "t": "Cadastrar o treinamento",
         "dec": false
        }
       ]
      },
      {
       "nome": "Demanda e programação",
       "etapas": [
        {
         "t": "Solicitar o treinamento",
         "dec": false
        },
        {
         "t": "Programar a turma",
         "dec": false
        },
        {
         "t": "Alocar os treinandos (matriz)",
         "dec": false
        }
       ]
      },
      {
       "nome": "Execução",
       "etapas": [
        {
         "t": "Iniciar o treinamento",
         "dec": false
        },
        {
         "t": "Concluir com a avaliação",
         "dec": false
        }
       ]
      },
      {
       "nome": "Acompanhamento",
       "etapas": [
        {
         "t": "Acompanhar por pessoa",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Assuntos regulatórios",
     "linha": "Obrigações regulatórias e registro de produto.",
     "fases": [
      {
       "nome": "Obrigações regulatórias",
       "etapas": [
        {
         "t": "Cadastrar o processo regulatório",
         "dec": false
        },
        {
         "t": "Programar a obrigação",
         "dec": false
        },
        {
         "t": "Monitorar e encerrar",
         "dec": false
        }
       ]
      },
      {
       "nome": "Registro de produto",
       "etapas": [
        {
         "t": "Montar o check-list de documentos",
         "dec": false
        },
        {
         "t": "Abrir a solicitação de registro",
         "dec": false
        },
        {
         "t": "Enviar à ANVISA",
         "dec": false
        }
       ]
      },
      {
       "nome": "Decisão e manutenção",
       "etapas": [
        {
         "t": "Registrar a decisão no Controle de Produtos",
         "dec": false
        },
        {
         "t": "Fechar a solicitação",
         "dec": false
        }
       ]
      }
     ]
    }
   ]
  },
  {
   "id": "documentos",
   "num": "06",
   "nome": "Documentos",
   "modulos": [
    "Controle de Documentos"
   ],
   "pergunta": "Como os documentos são controlados?",
   "titulo": "Cada procedimento no lugar certo, na versão certa.",
   "texto": "O Controle de Documentos conduz o documento da elaboração à vigência e à obsolescência, e controla as cópias impressas.",
   "faz": [
    "Ciclo do documento: elaboração, revisão, aprovação e vigência",
    "Nova revisão, substituição e obsolescência",
    "Identificação única de cada documento",
    "Controle de cópias impressas, com destinatário",
    "Documentos externos (normas, clientes e fornecedores) e documentos anteriores ao sistema",
    "Cadastro de tipos de documento, arquivos e modelos"
   ],
   "resultado": "Documentos aprovados e identificados, com histórico do ciclo.",
   "conecta": [
    "Garantia da Qualidade (treinamento ligado ao POP)"
   ],
   "fluxos": [
    {
     "nome": "Ciclo do documento",
     "linha": "Da inclusão à vigência, com revisão, substituição e obsolescência.",
     "fases": [
      {
       "nome": "Elaboração",
       "etapas": [
        {
         "t": "Incluir o documento",
         "dec": false
        },
        {
         "t": "Enviar para revisão",
         "dec": false
        }
       ]
      },
      {
       "nome": "Revisão",
       "etapas": [
        {
         "t": "Revisar por setor",
         "dec": false
        },
        {
         "t": "Confirmar a revisão",
         "dec": false
        }
       ]
      },
      {
       "nome": "Aprovação",
       "etapas": [
        {
         "t": "Pré-aprovar",
         "dec": false
        },
        {
         "t": "Aprovar",
         "dec": false
        }
       ]
      },
      {
       "nome": "Vigência",
       "etapas": [
        {
         "t": "Tornar vigente",
         "dec": false
        },
        {
         "t": "A revisão anterior sai",
         "dec": false
        }
       ]
      },
      {
       "nome": "Depois",
       "etapas": [
        {
         "t": "Nova revisão",
         "dec": false
        },
        {
         "t": "Obsoletar",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Controle de cópias",
     "linha": "Distribuição de cópias impressas de documentos aprovados.",
     "fases": [
      {
       "nome": "Escolha",
       "etapas": [
        {
         "t": "Pesquisar o documento",
         "dec": false
        }
       ]
      },
      {
       "nome": "Cópia",
       "etapas": [
        {
         "t": "Incluir a cópia",
         "dec": false
        },
        {
         "t": "Salvar a cópia",
         "dec": false
        }
       ]
      },
      {
       "nome": "Impressão",
       "etapas": [
        {
         "t": "Imprimir",
         "dec": false
        }
       ]
      },
      {
       "nome": "Depois",
       "etapas": [
        {
         "t": "Remover a cópia",
         "dec": false
        },
        {
         "t": "Documento substituído ou obsoleto?",
         "dec": true
        }
       ]
      }
     ]
    },
    {
     "nome": "Documento externo e legado",
     "linha": "Normas, documentos de clientes e fornecedores e documentos anteriores ao sistema.",
     "fases": [
      {
       "nome": "Externo",
       "etapas": [
        {
         "t": "Cadastrar o documento externo",
         "dec": false
        },
        {
         "t": "Validade",
         "dec": false
        },
        {
         "t": "Excluir",
         "dec": false
        }
       ]
      },
      {
       "nome": "Legado",
       "etapas": [
        {
         "t": "Incluir documento legado",
         "dec": false
        },
        {
         "t": "Tornar vigente",
         "dec": false
        }
       ]
      },
      {
       "nome": "Consulta",
       "etapas": [
        {
         "t": "Visualizar documento",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Tipo de documento, arquivos e modelos",
     "linha": "O cadastro que define o caminho de cada tipo de documento.",
     "fases": [
      {
       "nome": "Tipo",
       "etapas": [
        {
         "t": "Cadastrar o tipo de documento",
         "dec": false
        },
        {
         "t": "Definir o caminho do tipo",
         "dec": false
        },
        {
         "t": "Excluir o tipo",
         "dec": false
        }
       ]
      },
      {
       "nome": "Ciclo básico",
       "etapas": [
        {
         "t": "Incluir arquivo ou modelo",
         "dec": false
        },
        {
         "t": "Salvar",
         "dec": false
        },
        {
         "t": "Nova revisão",
         "dec": true
        }
       ]
      }
     ]
    }
   ]
  },
  {
   "id": "distribuicao",
   "num": "07",
   "nome": "Produto acabado até o cliente",
   "modulos": [
    "Comercial",
    "Rastreabilidade"
   ],
   "pergunta": "Como o medicamento chega ao cliente e pode ser acompanhado?",
   "titulo": "Depois da fabricação, o lote segue com a sua história.",
   "texto": "O Comercial conduz a venda do lote disponível até a fatura e a remessa. A Rastreabilidade dá a cada embalagem o seu identificador único (IUM) e registra os eventos declarados ao SNCM.",
   "faz": [
    "Cadastro de clientes, contratos e tabelas de venda",
    "Cotação, requisição de produto acabado e reserva do lote no Estoque",
    "Fatura, remessa e cancelamento",
    "IUM gerado para cada embalagem, com etiqueta e agregação em caixas",
    "Linha do tempo de eventos de cada embalagem",
    "Declaração dos eventos ao SNCM"
   ],
   "resultado": "O medicamento entregue e a história de cada embalagem registrada.",
   "conecta": [
    "Estoque (reserva e remessa)",
    "Produção (lote liberado vira IUM)"
   ],
   "fluxos": [
    {
     "nome": "Cliente e cadastros de venda",
     "linha": "A quem a empresa vende e para onde o lote vai.",
     "fases": [
      {
       "nome": "Cliente",
       "etapas": [
        {
         "t": "Tipo de cliente",
         "dec": false
        },
        {
         "t": "Endereços e contatos",
         "dec": false
        }
       ]
      },
      {
       "nome": "Contratos",
       "etapas": [
        {
         "t": "Convênio",
         "dec": false
        },
        {
         "t": "Relacionamento e pregão",
         "dec": false
        }
       ]
      },
      {
       "nome": "Tabelas de apoio",
       "etapas": [
        {
         "t": "Tipo de fornecimento",
         "dec": false
        },
        {
         "t": "Preço, tipos e assinaturas",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Cotação, requisição e reserva",
     "linha": "O lote vendido é escolhido entre os lotes com saldo no Estoque.",
     "fases": [
      {
       "nome": "Cotação",
       "etapas": [
        {
         "t": "Cotar para o cliente",
         "dec": false
        }
       ]
      },
      {
       "nome": "Requisição de PA",
       "etapas": [
        {
         "t": "Abrir a requisição",
         "dec": false
        },
        {
         "t": "Escolher o lote",
         "dec": false
        },
        {
         "t": "Salvar",
         "dec": false
        }
       ]
      },
      {
       "nome": "Reserva no Estoque",
       "etapas": [
        {
         "t": "Cancelar e criar a reserva",
         "dec": false
        },
        {
         "t": "Cancelar a requisição",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Fatura, remessa e cancelamento",
     "linha": "Da requisição separada à saída do material.",
     "fases": [
      {
       "nome": "Fatura",
       "etapas": [
        {
         "t": "Escolher a requisição",
         "dec": false
        },
        {
         "t": "Gerar a fatura",
         "dec": false
        }
       ]
      },
      {
       "nome": "Remessa",
       "etapas": [
        {
         "t": "Remessa GMM",
         "dec": false
        }
       ]
      },
      {
       "nome": "Depois da fatura",
       "etapas": [
        {
         "t": "Finalizar",
         "dec": false
        },
        {
         "t": "Cancelar",
         "dec": false
        },
        {
         "t": "Para quem foi o lote (RV07)",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Geração de IUM e agregação",
     "linha": "Do lote liberado ao IUM de cada embalagem e às caixas.",
     "fases": [
      {
       "nome": "Gerar o IUM",
       "etapas": [
        {
         "t": "Buscar a produção liberada",
         "dec": false
        },
        {
         "t": "Gerar",
         "dec": false
        }
       ]
      },
      {
       "nome": "Etiqueta",
       "etapas": [
        {
         "t": "Imprimir",
         "dec": false
        }
       ]
      },
      {
       "nome": "Agregação",
       "etapas": [
        {
         "t": "Montar e concluir",
         "dec": false
        },
        {
         "t": "Desfazer",
         "dec": false
        }
       ]
      }
     ]
    },
    {
     "nome": "Eventos e declaração à ANVISA",
     "linha": "Eventos de cada embalagem e declaração ao SNCM.",
     "fases": [
      {
       "nome": "Registrar",
       "etapas": [
        {
         "t": "Escolher os IUM ou agregações",
         "dec": false
        },
        {
         "t": "Dados do evento",
         "dec": false
        }
       ]
      },
      {
       "nome": "Enviar",
       "etapas": [
        {
         "t": "Marcar e chamar o microsserviço",
         "dec": false
        },
        {
         "t": "Envio ao SNCM",
         "dec": false
        }
       ]
      },
      {
       "nome": "Depois",
       "etapas": [
        {
         "t": "Retificar",
         "dec": false
        },
        {
         "t": "Linha do tempo e Estoque",
         "dec": false
        }
       ]
      }
     ]
    }
   ]
  }
 ],
 "grupos": [
  "Sistema computadorizado",
  "Materiais e lotes",
  "Sistema da qualidade",
  "Laboratório",
  "Fabricação",
  "Documentação",
  "Distribuição e rastreabilidade"
 ],
 "normas": [
  {
   "id": 3,
   "g": 0,
   "tema": "Trilha de auditoria",
   "norma": "RDC 658/2022, art. 125",
   "nivel": "base",
   "ja": [
    "Histórico campo a campo na maior parte dos cadastros: quem alterou, quando e o valor anterior"
   ],
   "entrega": [
    "Histórico obrigatório em toda inclusão, alteração e exclusão, com motivo e data e hora do servidor, num formato único em todos os módulos"
   ]
  },
  {
   "id": 4,
   "g": 0,
   "tema": "Registro no momento da ação",
   "norma": "RDC 658/2022, art. 124; Guia 33, 9.3.2.3",
   "nivel": "entrega",
   "ja": [
    "Registro de quem cadastrou e de quem autorizou nas principais operações"
   ],
   "entrega": [
    "Registro e confirmação no momento da ação",
    "Envio à ANVISA registrado somente com o protocolo recebido"
   ]
  },
  {
   "id": 5,
   "g": 0,
   "tema": "Assinatura eletrônica nas aprovações",
   "norma": "Guia 33, 9.3.2.3; IN 134/2022",
   "nivel": "entrega",
   "ja": [
    "Separação de funções: quem cadastra não autoriza o mesmo recebimento",
    "Aprovação por etapas nos documentos"
   ],
   "entrega": [
    "Assinatura eletrônica em laudos, aprovações de documentos, mudanças e liberação de lote",
    "Aprovação somente pela função designada"
   ]
  },
  {
   "id": 6,
   "g": 0,
   "tema": "Validação do sistema",
   "norma": "Guia 33, item 9 (GAMP 5, categoria 5)",
   "nivel": "base",
   "ja": [
    "Pacote de validação montado módulo a módulo: regras de negócio, requisitos, análise de risco, plano de testes e matriz de rastreabilidade",
    "Testes nas telas já realizados nos módulos Principal e Estoque"
   ],
   "entrega": [
    "Dossiê de validação completo para os nove módulos"
   ]
  },
  {
   "id": 38,
   "g": 0,
   "tema": "Integrações confiáveis entre os módulos",
   "norma": "Guia 33, 9.3.2.3",
   "nivel": "entrega",
   "ja": [
    "Módulos que trocam informação: o laudo do CQ chega ao Estoque, a reserva do Comercial acontece no Estoque, a remessa gera elo com a Rastreabilidade"
   ],
   "entrega": [
    "Integrações com retorno confirmado: se a informação não chegar ao outro módulo, o usuário é avisado e a operação não segue"
   ]
  },
  {
   "id": 8,
   "g": 1,
   "tema": "Recebimento de fornecedor aprovado",
   "norma": "RDC 658/2022, art. 8º, VI",
   "nivel": "entrega",
   "ja": [
    "Avaliação do fornecedor a cada entrega",
    "Pedido de compra com baixa no recebimento"
   ],
   "entrega": [
    "Qualificação de fornecedor ligada ao recebimento: material de fornecedor não aprovado é sinalizado ou bloqueado"
   ]
  },
  {
   "id": 9,
   "g": 1,
   "tema": "Inspeção e conferência de cada entrega",
   "norma": "RDC 658/2022, arts. 156 e 183",
   "nivel": "entrega",
   "ja": [
    "Portaria, inspeção do veículo, conferência de nota, de quantidade e pesagem"
   ],
   "entrega": [
    "Inspeção da entrega obrigatória e documentada",
    "Divergência de quantidade aceita somente com justificativa"
   ]
  },
  {
   "id": 10,
   "g": 1,
   "tema": "Quarentena até a liberação",
   "norma": "RDC 658/2022, art. 157",
   "nivel": "entrega",
   "ja": [
    "Pelas entradas de material, o lote entra em quarentena, abre a análise no CQ e só sai pelo laudo",
    "O lote reprovado fica bloqueado"
   ],
   "entrega": [
    "Situação única do lote, atualizada no instante do laudo e respeitada por todos os módulos"
   ]
  },
  {
   "id": 11,
   "g": 1,
   "tema": "Uso só de material dentro da validade e do reteste",
   "norma": "RDC 658/2022, art. 189",
   "nivel": "entrega",
   "ja": [
    "Validade obrigatória para item com controle de validade",
    "Agenda de reanálise e revalidação periódica do lote"
   ],
   "entrega": [
    "Trava para lote vencido ou com reanálise vencida",
    "Separação pela validade mais próxima"
   ]
  },
  {
   "id": 12,
   "g": 1,
   "tema": "Identificação do lote como o fabricante o emitiu",
   "norma": "RDC 658/2022, art. 141, V",
   "nivel": "base",
   "ja": [
    "Número de lote único na Produção: lote repetido é recusado"
   ],
   "entrega": [
    "Número do lote preservado exatamente como o fabricante o emitiu"
   ]
  },
  {
   "id": 13,
   "g": 1,
   "tema": "Amostras de retenção guardadas pelo prazo",
   "norma": "RDC 658/2022, art. 14, VIII",
   "nivel": "entrega",
   "ja": [
    "Amostras de referência, retenção e estabilidade registradas e guardadas em almoxarifado especial do CQ"
   ],
   "entrega": [
    "Prazo mínimo de guarda e bloqueio da saída antes do prazo"
   ]
  },
  {
   "id": 14,
   "g": 1,
   "tema": "Liberação do lote pela pessoa designada",
   "norma": "RDC 658/2022, art. 8º, XV",
   "nivel": "entrega",
   "ja": [
    "Laudo final do CQ e liberação da produção, cada um com sua etapa"
   ],
   "entrega": [
    "Certificação do lote pela Pessoa Delegada, com função conferida e assinatura eletrônica",
    "Venda, IUM e expedição somente de lote certificado"
   ]
  },
  {
   "id": 15,
   "g": 2,
   "tema": "Desvios: registro, investigação, causa e CAPA",
   "norma": "RDC 658/2022, art. 8º, XIV; arts. 339 a 342",
   "nivel": "base",
   "ja": [
    "Fluxo completo: registro, ação imediata, pré-avaliação, avaliação pelas áreas, CAPA corretiva e preventiva, monitoramento e encerramento",
    "Número sequencial e justificativa no cancelamento"
   ],
   "entrega": [
    "O desvio retém o lote até a decisão",
    "CAPA obrigatória para desvio crítico e verificação de eficácia"
   ]
  },
  {
   "id": 16,
   "g": 2,
   "tema": "Controle de mudanças",
   "norma": "RDC 658/2022, art. 8º, XII e XIII; arts. 176 e 177",
   "nivel": "entrega",
   "ja": [
    "Fluxo da solicitação à aprovação do produto, com avaliação pelas áreas, plano de ação e histórico"
   ],
   "entrega": [
    "Parecer das áreas obrigatório antes da liberação",
    "Mudança aprovada chega à Produção e aos documentos",
    "Verificação de eficácia"
   ]
  },
  {
   "id": 17,
   "g": 2,
   "tema": "Autoinspeção",
   "norma": "RDC 658/2022, arts. 361 a 366",
   "nivel": "base",
   "ja": [
    "Cadastros, roteiros, programação, execução por departamento, avaliação e relatório final"
   ],
   "entrega": [
    "Independência do inspetor em relação à área auditada",
    "Desvio aberto para cada não conformidade encontrada"
   ]
  },
  {
   "id": 18,
   "g": 2,
   "tema": "Treinamento",
   "norma": "RDC 658/2022, arts. 39 a 46",
   "nivel": "base",
   "ja": [
    "Matriz de treinamento, programação de turmas, avaliação dos treinandos e acompanhamento de vigentes, pendentes e vencidos"
   ],
   "entrega": [
    "Aviso de vencimento",
    "Consulta ao treinamento antes de a pessoa executar a tarefa e de o documento valer",
    "Programa de treinamento aprovado"
   ]
  },
  {
   "id": 19,
   "g": 2,
   "tema": "Registro do produto na ANVISA e prazos",
   "norma": "RDC 658/2022, art. 8º, XII",
   "nivel": "base",
   "ja": [
    "Controle da situação do registro, check-list, solicitação de registro e envio à ANVISA"
   ],
   "entrega": [
    "Avisos de prazo",
    "Produção somente de produto com registro válido"
   ]
  },
  {
   "id": 20,
   "g": 2,
   "tema": "Reclamações e recolhimento",
   "norma": "RDC 658/2022, arts. 319 a 360",
   "nivel": "entrega",
   "ja": [
    "Reclamação já registrável como origem de desvio",
    "Eventos de cada embalagem (IUM) para localizar o lote"
   ],
   "entrega": [
    "Fluxo completo de reclamação e recolhimento, com a lista de clientes por lote"
   ]
  },
  {
   "id": 21,
   "g": 2,
   "tema": "Revisão periódica da qualidade do produto",
   "norma": "RDC 658/2022, arts. 15 a 19",
   "nivel": "entrega",
   "ja": [],
   "entrega": [
    "Revisão periódica da qualidade do produto no módulo de Garantia da Qualidade"
   ]
  },
  {
   "id": 22,
   "g": 2,
   "tema": "Validação de processos, qualificação e calibração",
   "norma": "RDC 658/2022, art. 148, I e II",
   "nivel": "base",
   "ja": [
    "Programação, registro, revisão e liberação de limpeza, calibração, qualificação e manutenção de salas, equipamentos e instrumentos"
   ],
   "entrega": [
    "Resultado com limites numéricos",
    "Aviso de atraso",
    "Validação de processos na Garantia da Qualidade"
   ]
  },
  {
   "id": 23,
   "g": 3,
   "tema": "Amostragem e registro de cada teste",
   "norma": "RDC 658/2022, arts. 247 e 258",
   "nivel": "base",
   "ja": [
    "Amostragem por regra cadastrada",
    "Amostrador e verificador diferentes",
    "Quantidades para análise, retenção, referência e estabilidade, com checklist"
   ],
   "entrega": [
    "Registro do teste com todos os dados que a norma pede"
   ]
  },
  {
   "id": 24,
   "g": 3,
   "tema": "Verificação por outra pessoa e resultado fora de especificação",
   "norma": "RDC 658/2022, arts. 257 e 287",
   "nivel": "entrega",
   "ja": [
    "Resultados conferidos contra os limites cadastrados"
   ],
   "entrega": [
    "Conferência dos cálculos por outra pessoa",
    "Investigação de resultado fora de especificação"
   ]
  },
  {
   "id": 25,
   "g": 3,
   "tema": "Métodos validados, reagentes e padrões",
   "norma": "RDC 658/2022, arts. 253, 255 e 260 a 264",
   "nivel": "entrega",
   "ja": [
    "Regras de análise cadastradas por item"
   ],
   "entrega": [
    "Controle de métodos validados, reagentes, padrões e meios de cultura"
   ]
  },
  {
   "id": 26,
   "g": 3,
   "tema": "Programa de estabilidade",
   "norma": "RDC 658/2022, arts. 271 a 290",
   "nivel": "base",
   "ja": [
    "Regra com os tempos do estudo, abertura automática pelo Estoque, solicitação de cada tempo, interrupção ou final com relatório"
   ],
   "entrega": [
    "Avaliação do estudo e avisos de prazo"
   ]
  },
  {
   "id": 27,
   "g": 4,
   "tema": "Fórmula e instruções de fabricação aprovadas, com versão",
   "norma": "RDC 658/2022, arts. 133 a 135",
   "nivel": "entrega",
   "ja": [
    "Fórmula padrão e ordem de produção por produto",
    "Aprovação com permissão própria: quem elaborou não aprova",
    "Produto com lote padrão travado"
   ],
   "entrega": [
    "Versão e aprovação formal da fórmula e do modelo do registro de lote",
    "Somente a versão vigente chega à produção"
   ]
  },
  {
   "id": 28,
   "g": 4,
   "tema": "Registro de processamento do lote",
   "norma": "RDC 658/2022, art. 137",
   "nivel": "base",
   "ja": [
    "Registro eletrônico com etapas, subetapas e campos obrigatórios por produto",
    "Modelo montado no OPE"
   ],
   "entrega": [
    "Cobertura completa do que o artigo 137 pede"
   ]
  },
  {
   "id": 29,
   "g": 4,
   "tema": "Pesagem e controles em processo e ambientais",
   "norma": "RDC 658/2022, arts. 192 a 194 e 198",
   "nivel": "base",
   "ja": [
    "Pesagem com conferência",
    "Controles em processo e resultados ambientais registrados"
   ],
   "entrega": [
    "Limites obrigatórios nos controles em processo e ambientais"
   ]
  },
  {
   "id": 30,
   "g": 4,
   "tema": "Rendimento, reconciliação e desvio das instruções",
   "norma": "RDC 658/2022, arts. 160, 167 e 199",
   "nivel": "entrega",
   "ja": [
    "Reconciliação ao final da produção, com liberação"
   ],
   "entrega": [
    "Faixa esperada de rendimento e investigação obrigatória",
    "Aprovação formal de desvio das instruções"
   ]
  },
  {
   "id": 31,
   "g": 4,
   "tema": "Terceirização com contrato e registros",
   "norma": "RDC 658/2022, arts. 299 e 316",
   "nivel": "base",
   "ja": [
    "Indicação da etapa terceirizada, fornecedor, anexos e confirmação ou cancelamento"
   ],
   "entrega": [
    "Contrato e qualificação do terceiro vinculados à etapa"
   ]
  },
  {
   "id": 32,
   "g": 5,
   "tema": "Documentos aprovados, com identificação e data de efetividade",
   "norma": "RDC 658/2022, arts. 117 e 119",
   "nivel": "base",
   "ja": [
    "Ciclo completo: elaboração, revisão, aprovação, vigência, nova revisão e obsolescência",
    "Identificação única"
   ],
   "entrega": [
    "Assinatura eletrônica nas aprovações",
    "Vigência calculada em um só lugar"
   ]
  },
  {
   "id": 33,
   "g": 5,
   "tema": "Revisão periódica, documento obsoleto e cópias controladas",
   "norma": "RDC 658/2022, arts. 118 e 121",
   "nivel": "entrega",
   "ja": [
    "Controle de cópias impressas, com destinatário"
   ],
   "entrega": [
    "Revisão periódica obrigatória",
    "Cópia somente de documento vigente"
   ]
  },
  {
   "id": 34,
   "g": 5,
   "tema": "Retenção de documentos e registros de lote",
   "norma": "RDC 658/2022, arts. 127 e 128",
   "nivel": "entrega",
   "ja": [],
   "entrega": [
    "Prazo de retenção de documentos e de registros de lote"
   ]
  },
  {
   "id": 35,
   "g": 6,
   "tema": "Registros de distribuição prontos para o recolhimento",
   "norma": "RDC 658/2022, arts. 345 a 347",
   "nivel": "entrega",
   "ja": [
    "O lote é escolhido na venda e a remessa guarda o endereço",
    "Os eventos de cada embalagem guardam o destinatário"
   ],
   "entrega": [
    "Por lote, os clientes e as embalagens, prontos para um recolhimento"
   ]
  },
  {
   "id": 36,
   "g": 6,
   "tema": "Identificador único por embalagem e declaração ao SNCM",
   "norma": "Lei 11.903/2009 e regulamentação do SNCM",
   "nivel": "entrega",
   "ja": [
    "IUM para cada embalagem, com linha do tempo de eventos",
    "Agregação em caixas e etiqueta"
   ],
   "entrega": [
    "Declaração ao SNCM com protocolo",
    "Número de série único"
   ]
  },
  {
   "id": 37,
   "g": 6,
   "tema": "Etiqueta com os dados da empresa titular",
   "norma": "Normas de rotulagem",
   "nivel": "entrega",
   "ja": [
    "Etiqueta do IUM"
   ],
   "entrega": [
    "Dados da empresa titular configuráveis na etiqueta"
   ]
  }
 ],
 "frentes": [
  {
   "n": 1,
   "titulo": "Aprovações com assinatura eletrônica",
   "texto": "Laudo, documento, mudança e liberação do lote aprovados somente pela função designada, com assinatura eletrônica.",
   "temas": [
    5,
    14
   ]
  },
  {
   "n": 2,
   "titulo": "Histórico completo e confiável",
   "texto": "Toda inclusão, alteração e exclusão com motivo, data e hora do servidor, num formato único em todos os módulos.",
   "temas": [
    3,
    4
   ]
  },
  {
   "n": 3,
   "titulo": "Registro no momento da ação",
   "texto": "Cada ação confirmada somente depois de concluída; o envio à ANVISA registrado com o protocolo recebido.",
   "temas": [
    4,
    36,
    38
   ]
  },
  {
   "n": 4,
   "titulo": "Situação única do lote",
   "texto": "A certificação pela Pessoa Delegada e uma situação do lote respeitada por todos: o laudo muda a situação na hora; venda, IUM e expedição só de lote certificado.",
   "temas": [
    10,
    11,
    14
   ]
  },
  {
   "n": 5,
   "titulo": "Qualidade ligada à operação",
   "texto": "Fornecedor aprovado no recebimento; desvio que retém o lote; registro do produto e treinamento conferidos antes de produzir.",
   "temas": [
    8,
    15,
    18,
    19
   ]
  },
  {
   "n": 6,
   "titulo": "Mudança controlada, com versão",
   "texto": "Fórmula, modelo do registro de lote e documentos só mudam com mudança aprovada, e só a versão vigente chega à operação.",
   "temas": [
    16,
    27,
    32,
    33
   ]
  },
  {
   "n": 7,
   "titulo": "Distribuição e recolhimento",
   "texto": "Por lote, os clientes e as embalagens entregues à Garantia da Qualidade; reclamações e recolhimento.",
   "temas": [
    20,
    35
   ]
  },
  {
   "n": 8,
   "titulo": "Laboratório reforçado",
   "texto": "Conferência por outra pessoa, investigação de resultado fora de especificação, métodos e padrões controlados.",
   "temas": [
    24,
    25
   ]
  },
  {
   "n": 9,
   "titulo": "Etapas da norma obrigatórias",
   "texto": "Inspeção da entrega, CAPA para desvio crítico, parecer das áreas na mudança, verificação de eficácia e revisão periódica dos documentos.",
   "temas": [
    9,
    15,
    16,
    33
   ]
  }
 ],
 "totais": {
  "modulos": 9,
  "fluxos": 35,
  "temas": 35,
  "base": 14,
  "entrega": 21
 }
};
