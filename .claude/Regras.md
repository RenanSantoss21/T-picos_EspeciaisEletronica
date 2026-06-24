## Regras para avaliação do Software CEP

## Disciplina de Controle Estatístico Remoto de Processos

Professor: Henrique Gomes de Moura

Data: 10 de junho de 2026 (1o semestre de 2026)

### ***

1) Limites de controle 3 sigmas:

```
n – tamanho das amostras
σ – desvio padrão do processo
μ – média do processo
```
2) Gráfico XR:

```
̄ ̄ x – média das médias das amostras
̄ r – amplitude média das amostras
A 2 , D 3 e D 4 – coeficientes tabelados
```

3) Gráfico MRI – Média Móvel e Valor individual

_n_ = (^1) – tamanho da amostra
_am_ ̄ – média das amplitudes entre as amostras
_d_ 2 – coeficiente tabelado


4) Capacidade do processo:

```
LSE – limite superior de especificação
LIE – limite inferior de especificação
σ – desvio padrão estimado do processo
```
5) Gráfico P:

```
n – tamanho das amostras
̄ p – fração defeituosa média
```
6) Gráfico U:

```
̄ u – número médio de defeitos por unidade
n – tamanho das amostras
```
7) Cálculo de probabilidades envolvendo a distribuição Normal Padrão:

```
P ( x < x 0 )=Φ(
x − z
σ )
```
```
P ( x > x 0 )= 1 − P ( x < x 0 )
```
```
P ( x 0 < x < x 1 )=Φ(
```
```
x − z 1
σ )−Φ(
```
```
x − z 0
σ )
```

8) Distribuição Binomial:

```
P ( X = k,p,n )=( n
k )
```
```
pk ( 1 − p )( n − k )
```
Na qual:

```
X é o número de acertos em n tentativas
p é a probabilidade de acerto
```
```
( n
k
```
### )=

```
n!
k! ( n − k )!
```
- coeficiente binomial

Exemplo de uso: Qual é a probabilidade do processo produzir 12 saídas válidas em 20 tentativas,
considerando um deslocamento de + 1 σ na linha central?

9) Regras de aceitação do processo:

Curto prazo: 1 ponto fora de ± 3 σ
Longo prazo: ppm obtido < ppm requerido

10) Sinais de alerta:

→ Adote mecanismos aceitáveis para verificar possíveis deslocamentos na linha central.

→ Podem usar as regras da _Western Eletric Handbook_ (1956) ou filtros de Kalman.

11) Dados:

Obter dos arquivos JSON fornecidos pelo professor, através do SIGAA da disciplina.


# Perguntas

1. Obter os gráficos de controle de variáveis para as cartas XR e MRI. Avaliar se os processos
atendem o curto prazo. Avaliar se os processos atendem o longo prazo (ppm = 990). Calcular qual
seria o valor de X para uma margem de sucesso de 95%. Calcular as capacidades de cada processo,
considerando, centralizado, _LIE_ =0.99 _LIC_ e _LSE_ =1.2 _LSC_. Calcular qual seria a margem de
sucesso em caso de deslocamento de +^1 σ na linha central. Calcular qual seria a probabilidade de
sucesso de acertar 45 valores de X em 50 tentativas do processo.

2. Obter os gráficos de controle por atributos, P e U (quantidade de defeituosos e quantidade de
defeitos por unidade) usando o dado fornecido – mesmo JSON para os dois casos. Avaliar se os
processos encontram-se sob controle estatístico, no curto prazo. Avaliar se existe deslocamento.

# Entregas

Os estudantes terão 2h para realizar a tarefa, durante o horário de aula. As respostas deverão ser
confeccionadas a partir de cada software produzido. O código completo deverá ser fornecido em um
arquivo ZIP, dentro do qual deverá conter um PDF com todas as explicações digitadas e comentadas
pelos estudantes, baseadas no comportamento de cada software. No PDF, as respostas deverão
incluir imagens produzidas exclusivamente pelos softwares, além de textos explicativos
devidamente relacionados com cada imagem produzida. Requisito para entrega:

"matricula".zip
```
.
|_____ data/
|______ xr.json
|______ mri.json
|______ atributos.json
|
|_____ code/
|______ _requirements.txt_ ou equivalente
|______ arquivo principal executável
|______ demais arquivos para execução
|
|_____ report/
|______ response_<matricula>.pdf
```
# Comentário final

- Este simulado servirá de base para a avaliação oficial, a ser realizada em data posterior
combinada em sala de aula com o professor. Na avaliação oficial, os dados e enunciados poderão
sofrer pequenas alterações.


