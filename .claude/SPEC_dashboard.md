# ESPECIFICAÇÃO TÉCNICA (SPEC) - DASHBOARD CEP v2.0

1. Visão Geral da Atualização (v2.0 - Dashboard CEP)O objetivo desta atualização é criar uma interface de visualização e exportação (Dashboard) para as cartas de controle (X-R, P, I-MR, U). O sistema permitirá que engenheiros ou sistemas externos alimentem a plataforma colando um payload JSON cru. O dashboard processará esses dados, renderizará os gráficos e exibirá a "memória de cálculo" (médias, amplitudes, desvios e limites) de forma clara para auditorias e exportação.
2. Arquitetura de Tipagem (Inspirado nas SKILLS de Matt Pocock)Para lidar com diferentes tipos de cartas de controle vindas de um JSON não confiável (colado pelo usuário), aplicaremos Discriminated Unions e validação em tempo de execução com Zod. Isso garante que o TypeScript saiba exatamente quais campos existem dependendo do tipo_carta.Validação de Entrada (Zod Schema)O JSON colado no front-end deve ser validado imediatamente antes de qualquer cálculo de estado do React.

```TypeScript
import { z } from "zod";

// 1. Schema Base comum a todas as cartas
const BaseProcessoSchema = z.object({
  id: z.number(),
  nome: z.string(),
  criado_em: z.string().datetime(),
});

// 2. Schemas Específicos com "Discriminators" literais
const XRSchema = BaseProcessoSchema.extend({
  tipo_carta: z.literal("XR"),
  limites_controle: z.object({ LC_X: z.number(), LSC_X: z.number(), LIC_X: z.number() }),
  amostras: z.array(z.object({ ponto_x: z.number(), ponto_r: z.number(), data_coleta: z.string() }))
});

const PSchema = BaseProcessoSchema.extend({
  tipo_carta: z.literal("P"),
  limites_controle: z.object({ LC_P: z.number(), LSC_P: z.number(), LIC_P: z.number() }),
  amostras: z.array(z.object({ ponto_grafico: z.number(), data_coleta: z.string() }))
});

// 3. A União Discriminada
const ProcessoPayloadSchema = z.discriminatedUnion("tipo_carta", [
  XRSchema,
  PSchema,
  // Adicionar IMRSchema e USchema seguindo a mesma lógica
]);

// Inferência de Tipo do TypeScript (Skill: Extracting Types from Zod)
export type ProcessoPayload = z.infer<typeof ProcessoPayloadSchema>;
```

Vantagem: Se o TypeScript identificar que payload.tipo_carta === "XR", ele habilitará automaticamente o autocompletar para payload.limites_controle.LSC_X, e bloqueará tentativas de acessar LSC_P.
3. Especificação da Interface e Fluxo (UI/UX)
3.1. Módulo de Entrada (Input)Componente: Um <textarea> amplo com suporte a formatação de código.Comportamento: Ao colar o JSON e clicar em "Gerar Dashboard", o payload passa pelo ProcessoPayloadSchema.parse().Tratamento de Erros: Se o JSON for inválido (ex: faltar uma vírgula ou faltar o campo LSC), a interface renderiza as mensagens de erro exatas retornadas pelo Zod, sem quebrar a tela.
3.2. Módulo de Renderização do GráficoEixo X: Extraído das datas de coleta.Eixo Y (Série Principal): Os dados reais do processo ($\bar{X}$, $R$, $p$, $u$, etc.).Eixo Y (Limites de Controle): Linhas horizontais tracejadas representando $LSC$, $LIC$ e uma linha sólida para a Linha Central ($LC$).
3.3. Memória de Cálculo (Obrigatório para Auditoria)Abaixo do gráfico, uma tabela ou painel exibirá os cálculos utilizados para chegar aos limites, garantindo transparência:Para XR: Exibição da Média Global ($\bar{\bar{X}}$), Amplitude Média ($\bar{R}$) e as constantes utilizadas (ex: $A_2$, $D_3$, $D_4$).Para P/U: Exibição do tamanho médio da amostra ($n$), probabilidade global ($p$ ou $u$) e o desvio padrão calculado ($\sigma$).
3.4. ExportaçãoBotão "Exportar Relatório": Utilizará bibliotecas como html2pdf.js ou a função nativa de impressão do navegador (window.print()) formatada via CSS (@media print) para gerar um PDF em formato A4 contendo o gráfico e a memória de cálculo, omitindo a caixa de entrada do JSON.
4. Infraestrutura: Preparação para Tunelamento (Ngrok)Quando o Ngrok for ativado, ele criará um túnel seguro mapeando um endereço público (ex: https://1a2b3c.ngrok-free.app) para o seu localhost. Para que o sistema aceite essa entrada de dados JSON de fontes externas sem bloquear a conexão, duas configurações são cruciais no backend (Django):Configuração de Hosts PermitidosO Django, por segurança, bloqueia requisições de domínios que ele não conhece. O cabeçalho do Ngrok será rejeitado se não estiver configurado.

```Python
# No arquivo settings.py
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.ngrok-free.app'] 
```
Configuração de CORS (Cross-Origin Resource Sharing)Se o front-end que envia o JSON não estiver rodando exatamente na mesma porta/domínio que a API, o navegador bloqueará a requisição por política de mesma origem.
```Python
# Instalar: pip install django-cors-headers
# No arquivo settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://seu-dominio-ngrok.ngrok-free.app"
]
```

## 5. Análise Avançada: Regras do Western Electric Handbook

Para aprofundar a análise preditiva dos gráficos de variáveis contínuas (Cartas X no X-R e Cartas I no I-MR), o sistema deve suportar as 4 Regras clássicas do Western Electric Handbook. O objetivo é identificar quebras de aleatoriedade antes que o processo saia de controle estatístico, avaliando proximidades com os limites.

### 5.1. Escopo e Ativação
- **Ativação:** O JSON de entrada passará a aceitar uma flag booleana opcional `usar_regras_western: boolean` no schema base (`BaseProcessoSchema`).
- **Escopo Estatístico:** Esta análise será aplicada estritamente nas séries principais que assumem normalidade (Cartas X e I). Gráficos secundários (R e MR) e cartas de atributos (P, U) não rodarão o motor do Western Electric, limitando-se a detectar anomalias através dos limites padrão (Regra 1 / $3\sigma$).

### 5.2. Memória de Cálculo e Zonas (Backend)
Quando o parâmetro for `true`, o Backend precisará:
1. Inferir o desvio padrão da carta: $\sigma = \frac{(LSC - LC)}{3}$.
2. Determinar as divisões de zonas do gráfico:
   - **Limites da Zona C ($1\sigma$)**: $LC \pm 1\sigma$
   - **Limites da Zona B ($2\sigma$)**: $LC \pm 2\sigma$
   - **Limites da Zona A ($3\sigma$)**: $LSC$ e $LIC$ convencionais.
3. Incorporar os valores de $1\sigma$ e $2\sigma$ ao objeto `limites_controle` da resposta.

### 5.3. Motor de Verificação de Regras
O sistema iterará sob a série de amostras, aplicando os seguintes testes:
- **Regra 1:** 1 único ponto além da Zona A (Maior que LSC ou menor que LIC).
- **Regra 2:** 2 de 3 pontos consecutivos na Zona A ou além (do mesmo lado da linha central).
- **Regra 3:** 4 de 5 pontos consecutivos na Zona B ou além (do mesmo lado da linha central).
- **Regra 4:** 8 pontos consecutivos caindo do mesmo lado da linha central.

*Esses alertas devem ser anexados na resposta como uma lista, contendo o ID da amostra e a regra violada.*

### 5.4. Interface Visual e Dashboard
- **Plotagem das Zonas:** O gráfico renderizará linhas guias secundárias, finas e opacas, indicando visualmente as marcações de $1\sigma$ e $2\sigma$, se as regras estiverem ativas.
- **Destaque de Pontos Anômalos:** O "dot" no gráfico correspondente a um ponto violado deve alterar de cor, diferenciando infrações de tendência (Regras 2, 3 e 4 em laranja) de instabilidades críticas (Regra 1 em vermelho).

### 5.5. Exportação e Relatório Final
Na Memória de Cálculo renderizada abaixo do gráfico e no PDF gerado para auditoria:
- Uma nova coluna ou card com o valor do **$\sigma$ do Processo** calculado.
- Os valores exatos das faixas das zonas.
- Uma **Tabela de Alertas Preditivos** enumerando os pontos violados e a descrição descritiva da regra do Western Handbook que falhou.

### 5.6. Diretrizes de Implementação e Arquitetura (Backend)
Para garantir a estabilidade do sistema e evitar regressões nas funcionalidades atuais, o desenvolvimento do motor de regras deve seguir restrições estritas:
- **Restrição 1 (Isolamento Lógico):** O método base `gerar_alertas()` da classe `EstrategiaCarta` (que processa as quebras convencionais de limite) **NÃO** deve ser alterado. A análise antiga deve continuar rodando intacta.
- **Restrição 2 (Zero Novas Dependências):** Toda a lógica de análise de padrões (janelas deslizantes de amostras) deve ser construída utilizando **Python Puro** (iteração em listas, *slices*, contadores de estado). A introdução de bibliotecas matemáticas/estatísticas externas (como `numpy` ou `pandas`) é proibida para não inchar o projeto.
- **Acoplamento Seguro:**
  - A lógica das 4 regras será encapsulada em um novo método utilitário independente (ex: `_avaliar_regras_western(amostras, lc, sigma)`).
  - Este método será invocado exclusivamente no cálculo de limites das classes `CartaXR` e `CartaIMR`, ignorando as demais estratégias.
  - **Saída Segregada:** O JSON final incluirá uma nova chave `alertas_avancados` separada da chave `Alertas` tradicional, retornada apenas quando o parâmetro de configuração for acionado. Isso garante total compatibilidade com clientes legados (Backward Compatibility).