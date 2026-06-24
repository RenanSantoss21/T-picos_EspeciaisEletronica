## O que construir

Implementar a fundação estrutural e visual para as Regras do Western Electric Handbook (Cartas X e I). O sistema deve ser capaz de receber um JSON com a flag `usar_regras_western` verdadeira. Ao receber esta flag, o sistema processará os dados e devolverá, junto aos limites padrão, os limites exatos das zonas de 1 Sigma e 2 Sigmas, além do Sigma calculado. A interface (Dashboard) desenhará essas zonas como linhas guias no gráfico e exibirá os valores exatos na Memória de Cálculo para auditoria. Nenhuma regra de alerta de tendência precisa ser calculada ainda, apenas a fundação matemática e visual das zonas.

## Critérios de Aceite

- [ ] O schema do JSON de entrada (Zod/Django) aceita o booleano opcional `usar_regras_western`.
- [ ] Ao processar Cartas XR ou IMR com a flag verdadeira, o backend calcula o Sigma estatístico e os limites de 1 e 2 Sigmas.
- [ ] O backend retorna esses novos limites acoplados ao objeto `limites_controle`.
- [ ] O frontend/Dashboard renderiza visualmente linhas tracejadas mais opacas para as zonas (1 e 2 Sigmas) no gráfico.
- [ ] A seção "Memória de Cálculo" do Dashboard (e consequentemente no PDF) exibe os valores exatos calculados do Sigma do Processo e os limites dessas zonas intermediárias.

## Bloqueado por

None - can start immediately
