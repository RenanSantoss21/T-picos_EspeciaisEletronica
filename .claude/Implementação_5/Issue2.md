## O que construir

Implementar o motor de verificação preditiva do Western Electric e seu reflexo visual no Dashboard e relatório final. Com as zonas matemáticas ativadas, o sistema varrerá o histórico de amostras das Cartas X e I buscando por quebras de aleatoriedade (pontos muito próximos aos limites ou sequências atípicas). Os pontos afetados devem ser destacados no gráfico para visualização instantânea da anomalia, e detalhados em uma tabela de auditoria preditiva no relatório gerado. 

## Critérios de Aceite

- [ ] Criar o método estrito em Python puro `_avaliar_regras_western(amostras, lc, sigma)` sem alterar a lógica legada.
- [ ] O método implementa corretamente a avaliação das 4 regras clássicas usando janelas deslizantes (ex: 4 de 5 pontos, 8 seguidos).
- [ ] O backend devolve a lista segregada `alertas_avancados` no JSON final informando o ID da amostra e a regra violada.
- [ ] O gráfico recolore dinamicamente o ponto que violou uma regra (ex: vermelho para fora de controle agudo, laranja para regras de tendência).
- [ ] O Dashboard exibe a "Tabela de Alertas Preditivos" e a mesma é refletida adequadamente na visualização de impressão/PDF.

## Bloqueado por

- [Issue1.md](Issue1.md)