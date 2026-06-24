# Plano de Implementação TDD (Issue 2) - Motor de Alertas Western

Este plano detalha o fluxo de TDD para criar a lógica de detecção preditiva (Regras 1 a 4) no backend e sua respectiva renderização visual no frontend, sem ferir lógicas existentes.

## Ciclos TDD (Tracer Bullets)

### Ciclo 1: Lógica Preditiva (Backend)
- **Teste (RED):** Adicionar testes em `tests.py` que injetam sequências matemáticas precisas para acionar cada uma das 4 regras isoladamente:
  - Teste Regra 1: Ponto único além de $3\sigma$.
  - Teste Regra 2: 2 de 3 pontos acima de $2\sigma$.
  - Teste Regra 3: 4 de 5 pontos acima de $1\sigma$.
  - Teste Regra 4: 8 pontos consecutivos acima do LC.
- **Código (GREEN):** 
  - Criar o método `_avaliar_regras_western(self, amostras, lc, sigma)` em `EstrategiaCarta` operando em Python puro usando o `amostra.media` ou equivalente.
  - O método iterará pelas amostras usando uma janela deslizante nativa (slices de arrays ou listas).
  - Retornará uma lista de dicionários contendo o índice temporal da amostra (`amostra_index`) e a violação.
- **Integração:** Adicionar a chamada do método nas classes `CartaXR` e `CartaIMR`, gravando o resultado em `limites['alertas_avancados']`.
- **Refatoração:** Limpar complexidade ciclomática da verificação.

### Ciclo 2: Colorização Condicional dos Pontos (Frontend)
- **Modificações (JS):** 
  - Atualizar `renderizarGrafico` (em `chart_common.js`) para aceitar o array `alertas_avancados`.
  - Sobrepor as cores geradas para os pontos: Se houver alerta de Regra 1 $\rightarrow$ vermelho. Se for Regra 2, 3 ou 4 $\rightarrow$ laranja.

### Ciclo 3: Tabela de Alertas Preditivos (Frontend)
- **Modificações (JS):**
  - Construir uma nova função utilitária `gerarTabelaAlertas(alertas_avancados)` ou acoplá-la ao final de `gerarMemoriaCalculo()`.
  - A tabela listará qual amostra violou qual regra, garantindo clareza para auditorias em PDF.

## User Review Required
> [!IMPORTANT]
> - O payload colado manualmente no front pode **não ter um ID de banco de dados (`amostra_id`)**. Posso alterar a SPEC sutilmente para retornar `amostra_index` (A posição cronológica, ex: Amostra #1, Amostra #2) em vez do ID físico do banco para identificar os alertas? Isso torna o código à prova de falhas para inputs em memória.

## Open Questions
- Está de acordo com este plano e a alteração sugerida acima sobre o identificador temporal da amostra?
