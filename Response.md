# Respostas da Prova — Controle Estatístico de Processos (CEP)

---

## Módulo 1 — Carta XR

### Parâmetros base (dashboard_xr.json)

| Parâmetro | Valor |
|---|---|
| LC_X | 50.2114 |
| LSC_X | 50.9253 |
| LIC_X | 49.4975 |
| R̄ | 2.318 |
| LSC_R | 4.1191 |
| LIC_R | 0.0 |
| n | 10 |
| σ_CP = R̄/d₂ | **0.7530** |

---

### 1. O processo XR atende ao critério de curto prazo?

**Pontos fora dos limites de controle (Carta X̄):**

| Ponto | x | Situação |
|---|---|---|
| **12** | **52.840** | ❌ ACIMA do LSC_X = 50.9253 |
| Demais (1–11, 13–20) | — | ✓ dentro |

Carta R: todos os pontos dentro do LSC_R = 4.1191.

**Resposta:** ❌ **NÃO.** O processo XR não está sob controle estatístico no curto prazo. O ponto 12 (x = 52.840) ultrapassa o LSC_X = 50.9253, indicando presença de causa especial de variação.

---

### 2. O processo XR atende ao critério de longo prazo com meta de ppm = 890?

Limites de especificação operacionais:
- **LSE** = 1.10 × LSC_X = 1.10 × 50.9253 = **56.0178**
- **LIE** = 0.98 × LIC_X = 0.98 × 49.4975 = **48.5076**

RCP global (centralizado) = (56.0178 − 48.5076) / (6 × 0.7530) = 7.5102 / 4.518 = **1.662**

A meta de 890 ppm exige RCP ≥ 1.123. Como RCP = 1.662 ≥ 1.123, a capacidade potencial é suficiente.

**Resposta:** ⚠️ **Condicionalmente SIM.** A capacidade calculada (RCP = 1.662) supera o requisito para 890 ppm. Contudo, a causa especial no ponto 12 compromete a confiabilidade desta estimativa enquanto não for investigada e eliminada.

---

### 3. Qual o valor de X necessário para atingir margem de sucesso de 96%?

Margem de 96% → z bilateral = ±2.054 (2% em cada cauda)

- **x superior** = 50.2114 + 2.054 × 0.7530 = **51.758**
- **x inferior** = 50.2114 − 2.054 × 0.7530 = **48.665**

**Resposta:** Para margem de sucesso de 96%, os limites de tolerância são **x ≈ 51.758** (superior) e **x ≈ 48.665** (inferior).

---

### 4. Qual o RCP_k do processo XR assumindo centralização?

- **LSE** = 56.0178, **LIE** = 48.5076, μ = 50.2114, σ = 0.7530

| Lado | Numerador | Denominador | Resultado |
|---|---|---|---|
| Superior (LSE − μ) / 3σ | 5.8064 | 2.259 | 2.570 |
| Inferior (μ − LIE) / 3σ | 1.7038 | 2.259 | 0.754 |

**RCP_k = min(2.570 ; 0.754) = 0.754**

**Resposta:** O RCP_k = **0.754**, limitado pelo lado inferior (LIE). Por ser inferior a 1.0, o processo é **incapaz** nos limites operacionais definidos — a média deslocada para cima prejudica o lado inferior.

---

### 5. Qual a nova margem de sucesso após deslocamento de +1.50 na linha central?

Nova média: μ' = 50.2114 + 1.50 = **51.7114**

| Lado | z-score | Φ(z) | P(fora) |
|---|---|---|---|
| Superior: (56.0178 − 51.7114) / 0.7530 | **5.719** | ≈ 1 | ≈ 0 |
| Inferior: (51.7114 − 48.5076) / 0.7530 | **4.255** | 0.9999895 | **0.0000105** |

Margem de sucesso = 1 − 0.0000105 = **99.9989%** (~10.5 ppm)

**Resposta:** Após deslocamento de +1.50, a nova margem de sucesso é de **≈ 99.9989%**, com a não-conformidade concentrada no lado inferior (~10.5 ppm).

---

### 6. Qual a probabilidade exata P(X = 85, n = 100, p = 0.96)?

Usando p = 0.96 (margem de 96% definida na questão 3) e Distribuição Binomial:

| Termo | Valor |
|---|---|
| C(100, 15) | ≈ 3.268 × 10¹⁷ |
| (0.96)⁸⁵ | 0.03104 |
| (0.04)¹⁵ | 1.032 × 10⁻²¹ |
| **P(X = 85)** | **≈ 1.047%** |

**Resposta:** A probabilidade exata de obter 85 acertos em 100 tentativas com p = 0.96 é de **≈ 1.047%**.

---

## Módulo 1 — Carta I-MR

### Parâmetros base (dashboard_imr.json)

| Parâmetro | Valor |
|---|---|
| LC_I | 74.8707 |
| LSC_I | 77.0721 |
| LIC_I | 72.6694 |
| MR̄ | 0.8277 |
| LSC_MR | 2.7041 |
| LIC_MR | 0 |
| σ_CP = MR̄/d₂ | **0.7338** |

---

### 7. O processo I-MR atende ao critério de curto prazo?

**Carta I — Pontos fora dos limites (LSC = 77.0721 | LIC = 72.6694):**

| Ponto | x | Situação |
|---|---|---|
| **14** | **78.21** | ❌ ACIMA do LSC_I |
| **33** | **71.82** | ❌ ABAIXO do LIC_I |

**Carta MR — Pontos fora do limite (LSC_MR = 2.7041):**

| Ponto | MR | Situação |
|---|---|---|
| **14** | **3.26** | ❌ ACIMA do LSC_MR |
| **15** | **3.33** | ❌ ACIMA do LSC_MR |
| **34** | **3.44** | ❌ ACIMA do LSC_MR |

**Resposta:** ❌ **NÃO.** O processo I-MR não está sob controle estatístico no curto prazo. Foram identificados 2 pontos fora na Carta I (pontos 14 e 33) e 3 pontos fora na Carta MR (pontos 14, 15 e 34), indicando causas especiais de variação.

---

### 8. Qual o RCP_k do processo I-MR assumindo centralização?

- **LSE** = 1.10 × 77.0721 = **84.7793**
- **LIE** = 0.98 × 72.6694 = **71.2160**
- μ = 74.8707, σ = 0.7338

| Lado | Resultado |
|---|---|
| (LSE − μ) / 3σ = 9.9086 / 2.2014 | 4.501 |
| (μ − LIE) / 3σ = 3.6547 / 2.2014 | 1.660 |

**RCP_k = min(4.501 ; 1.660) = 1.660**

**Resposta:** O RCP_k = **1.660**, indicando boa capacidade potencial do processo I-MR. O lado crítico é o inferior (LIE).

---

## Módulo 2 — Carta P

### Parâmetros base (dashboard_p.json)

| Parâmetro | Valor |
|---|---|
| LC_P (p̄) | 0.095 |
| LSC_P | 0.3732 |
| LIC_P | 0.000 |
| n | 10 |

---

### 9. O processo P está sob controle estatístico no curto prazo?

Todos os 40 pontos plotados estão dentro dos limites [0.000 ; 0.3732]:
- 38 pontos com valor 0.1
- 2 pontos com valor 0.0 (pontos 22 e 34)
- Nenhum ponto fora dos limites de controle.

**Resposta:** ✅ **SIM.** O processo P está sob controle estatístico no curto prazo. Nenhum ponto viola os limites de controle.

⚠️ **Alerta:** A concentração de 38/40 pontos exatamente em 0.1 configura ausência de variabilidade natural — possível indício de medição discreta ou viés no critério de defeito. Recomenda-se investigação.

---

### 10. Existem deslocamentos detectáveis na linha central — Carta P?

Com p̄ = 0.095 e n = 10, os valores discretos possíveis são 0.0, 0.1, 0.2, … A alta concentração em 0.1 (38/40 pontos) indica:

- **Nenhuma violação de limite** detectada.
- **Falta de variabilidade natural** (Regras de Western Electric): 38 pontos consecutivos num único valor constitui padrão de estratificação.
- Sem tendência crescente ou decrescente identificada.

**Resposta:** O processo está em controle estatístico, mas a **uniformidade excessiva** dos pontos sugere que a proporção real de defeitos está muito próxima de 1/10 = 0.10, levemente acima da LC = 0.095. O subgrupo de tamanho n = 10 pode ser insuficiente para detectar variações reais na proporção de defeituosos.

---

## Resumo Executivo

| Processo | Curto Prazo | RCP_k | Observação |
|---|---|---|---|
| **XR** | ❌ Não controlado | 0.754 | Ponto 12 (x = 52.840) acima do LSC_X |
| **I-MR** | ❌ Não controlado | 1.660 | Pts 14 e 33 fora na Carta I; pts 14, 15 e 34 fora na Carta MR |
| **P** | ✅ Sob controle | — | Uniformidade excessiva — alerta de estratificação |

| Cálculo | Resultado |
|---|---|
| σ_CP (XR) | 0.7530 |
| x para 96% de sucesso (XR) | 51.758 (sup) / 48.665 (inf) |
| RCP global XR (centralizado) | 1.662 |
| RCP_k XR | 0.754 |
| Nova margem após deslocamento +1.50 | ≈ 99.9989% (~10.5 ppm) |
| σ_CP (IMR) | 0.7338 |
| RCP_k IMR | 1.660 |
| P(X = 85, n = 100, p = 0.96) | ≈ 1.047% |
