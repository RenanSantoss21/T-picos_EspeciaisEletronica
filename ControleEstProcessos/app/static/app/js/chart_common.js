/**
 * chart_common.js — Módulo compartilhado para renderização de gráficos CEP
 * Usado por dashboard.js e json_input.js
 */

// ═══════════════════════════════════════════════════════════════
// Constantes CEP (espelhadas do backend const.py)
// ═══════════════════════════════════════════════════════════════
const CONSTANTES_CEP = {
    2: { A2: 1.880, D3: 0, D4: 3.267, d2: 1.128 },
    3: { A2: 1.023, D3: 0, D4: 2.574, d2: 1.693 },
    4: { A2: 0.729, D3: 0, D4: 2.282, d2: 2.059 },
    5: { A2: 0.577, D3: 0, D4: 2.114, d2: 2.326 },
    6: { A2: 0.483, D3: 0, D4: 2.004, d2: 2.534 },
    7: { A2: 0.419, D3: 0, D4: 1.924, d2: 2.704 },
    8: { A2: 0.373, D3: 0, D4: 1.864, d2: 2.847 },
    9: { A2: 0.337, D3: 0, D4: 1.816, d2: 2.970 },
    10: { A2: 0.308, D3: 0, D4: 1.777, d2: 3.078 },
};

// ═══════════════════════════════════════════════════════════════
// Canvas helper
// ═══════════════════════════════════════════════════════════════
function criarCanvas(container, id) {
    const wrapper = document.createElement('div');
    wrapper.className = 'chart-wrapper';
    wrapper.innerHTML = `<canvas id="${id}"></canvas>`;
    container.appendChild(wrapper);
}

// ═══════════════════════════════════════════════════════════════
// Renderização genérica de gráfico Chart.js
// ═══════════════════════════════════════════════════════════════
function renderizarGrafico(canvasId, titulo, labelsX, dadosY, lsc, lic, lc, corLinha, zonas = null, alertasAvancados = null) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const n = labelsX.length;

    // Detectar pontos fora dos limites ou regras
    const pontoCores = dadosY.map((v, index) => {
        if (alertasAvancados) {
            const alerta = alertasAvancados.find(a => a.amostra_index === index + 1);
            if (alerta) {
                return alerta.regra === 1 ? '#ef4444' : '#f97316'; // Vermelho p/ Regra 1, Laranja p/ outras
            }
        }
        if (v > lsc || v < lic) return '#ef4444'; // vermelho para fora do controle
        return corLinha;
    });

    const pontoRaios = dadosY.map((v, index) => {
        if (alertasAvancados) {
            if (alertasAvancados.some(a => a.amostra_index === index + 1)) return 6;
        }
        if (v > lsc || v < lic) return 6;
        return 3;
    });

    const datasets = [
        {
            label: 'Medição Real',
            data: dadosY,
            borderColor: corLinha,
            backgroundColor: corLinha + '33',
            borderWidth: 2,
            tension: 0.2,
            pointBackgroundColor: pontoCores,
            pointBorderColor: pontoCores,
            pointRadius: pontoRaios,
            fill: false,
        },
        {
            label: 'LSC',
            data: Array(n).fill(lsc),
            borderColor: '#ef4444',
            borderDash: [6, 4],
            borderWidth: 1.5,
            pointRadius: 0,
            fill: false,
        },
        {
            label: 'LC',
            data: Array(n).fill(lc),
            borderColor: '#22c55e',
            borderWidth: 2,
            pointRadius: 0,
            fill: false,
        },
        {
            label: 'LIC',
            data: Array(n).fill(lic),
            borderColor: '#ef4444',
            borderDash: [6, 4],
            borderWidth: 1.5,
            pointRadius: 0,
            fill: false,
        }
    ];

    if (zonas) {
        const styleZona = { borderColor: '#94a3b8', borderDash: [2, 2], borderWidth: 1, pointRadius: 0, fill: false };
        datasets.push({ label: '+2σ', data: Array(n).fill(zonas.lsc_2s), ...styleZona });
        datasets.push({ label: '+1σ', data: Array(n).fill(zonas.lsc_1s), ...styleZona });
        datasets.push({ label: '-1σ', data: Array(n).fill(zonas.lic_1s), ...styleZona });
        datasets.push({ label: '-2σ', data: Array(n).fill(zonas.lic_2s), ...styleZona });
    }

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labelsX,
            datasets: datasets
        },
        options: {
            responsive: true,
            interaction: { intersect: false, mode: 'index' },
            plugins: {
                title: {
                    display: true,
                    text: titulo,
                    font: { size: 16, weight: 'bold' },
                    color: '#e2e8f0',
                    padding: { bottom: 16 }
                },
                legend: {
                    labels: { color: '#94a3b8', usePointStyle: true, padding: 16 }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#f1f5f9',
                    bodyColor: '#cbd5e1',
                    borderColor: '#334155',
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8,
                }
            },
            scales: {
                x: {
                    ticks: { color: '#64748b', maxRotation: 45 },
                    grid: { color: 'rgba(51, 65, 85, 0.3)' }
                },
                y: {
                    ticks: { color: '#64748b' },
                    grid: { color: 'rgba(51, 65, 85, 0.3)' }
                }
            }
        }
    });
}

// ═══════════════════════════════════════════════════════════════
// Memória de Cálculo — gera HTML de tabela com os parâmetros
// ═══════════════════════════════════════════════════════════════
function gerarMemoriaCalculo(data) {
    const limites = data.limites_controle;
    const amostras = data.amostras;
    const tipo = data.tipo_carta;

    if (!limites || Object.keys(limites).length === 0) {
        return '<p class="calc-empty">Sem dados suficientes para calcular limites.</p>';
    }

    let html = '<div class="calc-memory"><h3>📊 Memória de Cálculo</h3>';

    if (tipo === 'XR') {
        const n = amostras.length > 0 && amostras[0].valores ? amostras[0].valores.length : '—';
        const constantes = CONSTANTES_CEP[n] || {};
        html += `
        <table class="calc-table">
            <thead>
                <tr><th colspan="2">Parâmetros — Carta X̄-R</th></tr>
            </thead>
            <tbody>
                <tr><td>Tamanho do subgrupo (n)</td><td>${n}</td></tr>
                <tr><td>Média Global (X̄̄)</td><td>${fmt(limites.LC_X)}</td></tr>
                <tr><td>Amplitude Média (R̄)</td><td>${fmt(limites.LC_R)}</td></tr>
                ${limites.Sigma !== undefined ? `<tr><td>Sigma do Processo (σ)</td><td>${fmt(limites.Sigma)}</td></tr>` : ''}
                <tr class="sep"><td colspan="2">Constantes Utilizadas</td></tr>
                <tr><td>A₂</td><td>${constantes.A2 ?? '—'}</td></tr>
                <tr><td>D₃</td><td>${constantes.D3 ?? '—'}</td></tr>
                <tr><td>D₄</td><td>${constantes.D4 ?? '—'}</td></tr>
                <tr class="sep"><td colspan="2">Limites de Controle — Gráfico X̄</td></tr>
                <tr><td>LSC_X</td><td>${fmt(limites.LSC_X)}</td></tr>
                ${limites.Sigma !== undefined ? `
                <tr class="western-rule" style="color: #94a3b8; font-size: 0.9em;"><td>LSC_X_2S (+2σ)</td><td>${fmt(limites.LSC_X_2S)}</td></tr>
                <tr class="western-rule" style="color: #94a3b8; font-size: 0.9em;"><td>LSC_X_1S (+1σ)</td><td>${fmt(limites.LSC_X_1S)}</td></tr>
                ` : ''}
                <tr><td>LC_X</td><td>${fmt(limites.LC_X)}</td></tr>
                ${limites.Sigma !== undefined ? `
                <tr class="western-rule" style="color: #94a3b8; font-size: 0.9em;"><td>LIC_X_1S (-1σ)</td><td>${fmt(limites.LIC_X_1S)}</td></tr>
                <tr class="western-rule" style="color: #94a3b8; font-size: 0.9em;"><td>LIC_X_2S (-2σ)</td><td>${fmt(limites.LIC_X_2S)}</td></tr>
                ` : ''}
                <tr><td>LIC_X</td><td>${fmt(limites.LIC_X)}</td></tr>
                <tr class="sep"><td colspan="2">Limites de Controle — Gráfico R</td></tr>
                <tr><td>LSC_R</td><td>${fmt(limites.LSC_R)}</td></tr>
                <tr><td>LC_R</td><td>${fmt(limites.LC_R)}</td></tr>
                <tr><td>LIC_R</td><td>${fmt(limites.LIC_R)}</td></tr>
            </tbody>
        </table>`;

    } else if (tipo === 'IMR') {
        const n = amostras.length > 0 && amostras[0].valores ? amostras[0].valores.length : '—';
        const constantes = CONSTANTES_CEP[n] || CONSTANTES_CEP[2];
        html += `
        <table class="calc-table">
            <thead>
                <tr><th colspan="2">Parâmetros — Carta I-MR</th></tr>
            </thead>
            <tbody>
                <tr><td>Média Individual (X̄)</td><td>${fmt(limites.LC_I)}</td></tr>
                <tr><td>Amplitude Móvel Média (M̄R)</td><td>${fmt(limites.LC_MR)}</td></tr>
                ${limites.Sigma !== undefined ? `<tr><td>Sigma do Processo (σ)</td><td>${fmt(limites.Sigma)}</td></tr>` : ''}
                <tr class="sep"><td colspan="2">Constantes Utilizadas (n=2 para MR)</td></tr>
                <tr><td>A₂</td><td>${constantes.A2 ?? '—'}</td></tr>
                <tr><td>D₃</td><td>${constantes.D3 ?? '—'}</td></tr>
                <tr><td>D₄</td><td>${constantes.D4 ?? '—'}</td></tr>
                <tr class="sep"><td colspan="2">Limites de Controle — Gráfico I</td></tr>
                <tr><td>LSC_I</td><td>${fmt(limites.LSC_I)}</td></tr>
                ${limites.Sigma !== undefined ? `
                <tr class="western-rule" style="color: #94a3b8; font-size: 0.9em;"><td>LSC_I_2S (+2σ)</td><td>${fmt(limites.LSC_I_2S)}</td></tr>
                <tr class="western-rule" style="color: #94a3b8; font-size: 0.9em;"><td>LSC_I_1S (+1σ)</td><td>${fmt(limites.LSC_I_1S)}</td></tr>
                ` : ''}
                <tr><td>LC_I</td><td>${fmt(limites.LC_I)}</td></tr>
                ${limites.Sigma !== undefined ? `
                <tr class="western-rule" style="color: #94a3b8; font-size: 0.9em;"><td>LIC_I_1S (-1σ)</td><td>${fmt(limites.LIC_I_1S)}</td></tr>
                <tr class="western-rule" style="color: #94a3b8; font-size: 0.9em;"><td>LIC_I_2S (-2σ)</td><td>${fmt(limites.LIC_I_2S)}</td></tr>
                ` : ''}
                <tr><td>LIC_I</td><td>${fmt(limites.LIC_I)}</td></tr>
                <tr class="sep"><td colspan="2">Limites de Controle — Gráfico MR</td></tr>
                <tr><td>LSC_MR</td><td>${fmt(limites.LSC_MR)}</td></tr>
                <tr><td>LC_MR</td><td>${fmt(limites.LC_MR)}</td></tr>
                <tr><td>LIC_MR</td><td>${fmt(limites.LIC_MR)}</td></tr>
            </tbody>
        </table>`;

    } else if (tipo === 'P') {
        // Calcular n médio e sigma a partir das amostras
        const totalN = amostras.reduce((s, a) => s + (a.tamanho_amostra || 0), 0);
        const nMedio = amostras.length > 0 ? totalN / amostras.length : 0;
        const pBar = limites.LC_P;
        const sigma = nMedio > 0 ? Math.sqrt((pBar * (1 - pBar)) / nMedio) : 0;

        html += `
        <table class="calc-table">
            <thead>
                <tr><th colspan="2">Parâmetros — Carta P</th></tr>
            </thead>
            <tbody>
                <tr><td>Número de amostras</td><td>${amostras.length}</td></tr>
                <tr><td>Tamanho médio da amostra (n̄)</td><td>${fmt(nMedio)}</td></tr>
                <tr><td>Proporção global (p̄)</td><td>${fmt(pBar)}</td></tr>
                <tr><td>Desvio padrão (σ_p)</td><td>${fmt(sigma)}</td></tr>
                <tr class="sep"><td colspan="2">Limites de Controle</td></tr>
                <tr><td>LSC_P</td><td>${fmt(limites.LSC_P)}</td></tr>
                <tr><td>LC_P</td><td>${fmt(limites.LC_P)}</td></tr>
                <tr><td>LIC_P</td><td>${fmt(limites.LIC_P)}</td></tr>
            </tbody>
        </table>`;

    } else if (tipo === 'U') {
        const totalN = amostras.reduce((s, a) => s + (a.tamanho_amostra || 0), 0);
        const nMedio = amostras.length > 0 ? totalN / amostras.length : 0;
        const uBar = limites.LC_U;
        const sigma = nMedio > 0 ? Math.sqrt(uBar / nMedio) : 0;

        html += `
        <table class="calc-table">
            <thead>
                <tr><th colspan="2">Parâmetros — Carta U</th></tr>
            </thead>
            <tbody>
                <tr><td>Número de amostras</td><td>${amostras.length}</td></tr>
                <tr><td>Tamanho médio da amostra (n̄)</td><td>${fmt(nMedio)}</td></tr>
                <tr><td>Taxa média de defeitos (ū)</td><td>${fmt(uBar)}</td></tr>
                <tr><td>Desvio padrão Poisson (σ_u)</td><td>${fmt(sigma)}</td></tr>
                <tr class="sep"><td colspan="2">Limites de Controle</td></tr>
                <tr><td>LSC_U</td><td>${fmt(limites.LSC_U)}</td></tr>
                <tr><td>LC_U</td><td>${fmt(limites.LC_U)}</td></tr>
                <tr><td>LIC_U</td><td>${fmt(limites.LIC_U)}</td></tr>
            </tbody>
        </table>`;
    }

    if (limites.alertas_avancados && limites.alertas_avancados.length > 0) {
        html += `
        </div>
        <div class="calc-memory" style="margin-top: 20px; border-top: 3px solid #ef4444; padding-top: 15px;">
            <h3 style="color: #ef4444;">🚨 Alertas Preditivos (Western Electric)</h3>
            <table class="calc-table">
                <thead>
                    <tr><th>Amostra</th><th>Regra Violada</th><th>Descrição</th></tr>
                </thead>
                <tbody>`;
        limites.alertas_avancados.forEach(alerta => {
            let dataColeta = `#${alerta.amostra_index}`;
            if (amostras[alerta.amostra_index - 1] && amostras[alerta.amostra_index - 1].data_coleta) {
                dataColeta = amostras[alerta.amostra_index - 1].data_coleta;
                try {
                    dataColeta = new Date(dataColeta).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
                } catch (e) {}
            }
            const cor = alerta.regra === 1 ? '#ef4444' : '#f97316';
            html += `
                    <tr>
                        <td>${dataColeta}</td>
                        <td style="color: ${cor}; font-weight: bold;">Regra ${alerta.regra}</td>
                        <td>${alerta.mensagem}</td>
                    </tr>`;
        });
        html += `
                </tbody>
            </table>`;
    }

    html += '</div>';
    return html;
}

function fmt(val) {
    if (val === null || val === undefined) return '—';
    return typeof val === 'number' ? val.toFixed(4) : val;
}

// ═══════════════════════════════════════════════════════════════
// Validação de payload JSON (equivalente Zod simplificado)
// ═══════════════════════════════════════════════════════════════
function validarPayload(payload) {
    const erros = [];

    if (!payload || typeof payload !== 'object') {
        return ['O payload deve ser um objeto JSON válido.'];
    }

    // Campos base obrigatórios
    if (typeof payload.nome !== 'string' || !payload.nome.trim()) {
        erros.push('Campo "nome" (string) é obrigatório.');
    }
    if (!['XR', 'IMR', 'P', 'U'].includes(payload.tipo_carta)) {
        erros.push('Campo "tipo_carta" deve ser "XR", "IMR", "P" ou "U".');
    }
    
    if (payload.usar_regras_western !== undefined && typeof payload.usar_regras_western !== 'boolean') {
        erros.push('Campo "usar_regras_western" deve ser booleano se fornecido.');
    }

    // Limites de controle
    if (!payload.limites_controle || typeof payload.limites_controle !== 'object') {
        erros.push('Campo "limites_controle" (objeto) é obrigatório.');
    } else {
        const lim = payload.limites_controle;
        const tipo = payload.tipo_carta;

        const camposEsperados = {
            'XR': ['LC_X', 'LSC_X', 'LIC_X', 'LC_R', 'LSC_R', 'LIC_R'],
            'IMR': ['LC_I', 'LSC_I', 'LIC_I', 'LC_MR', 'LSC_MR', 'LIC_MR'],
            'P': ['LC_P', 'LSC_P', 'LIC_P'],
            'U': ['LC_U', 'LSC_U', 'LIC_U'],
        };

        const esperados = camposEsperados[tipo] || [];
        for (const campo of esperados) {
            if (typeof lim[campo] !== 'number') {
                erros.push(`limites_controle.${campo} (number) é obrigatório para carta ${tipo}.`);
            }
        }
    }

    // Amostras
    if (!Array.isArray(payload.amostras) || payload.amostras.length === 0) {
        erros.push('Campo "amostras" (array não vazio) é obrigatório.');
    } else {
        const tipo = payload.tipo_carta;
        payload.amostras.forEach((a, i) => {
            if (tipo === 'XR' || tipo === 'IMR') {
                if (typeof a.ponto_x !== 'number') erros.push(`amostras[${i}].ponto_x (number) é obrigatório.`);
                if (tipo === 'XR' && typeof a.ponto_r !== 'number') erros.push(`amostras[${i}].ponto_r (number) é obrigatório.`);
                if (tipo === 'IMR' && a.ponto_mr === undefined) erros.push(`amostras[${i}].ponto_mr (number|null) é obrigatório.`);
            } else {
                if (typeof a.ponto_grafico !== 'number') erros.push(`amostras[${i}].ponto_grafico (number) é obrigatório.`);
            }
            if (!a.data_coleta) erros.push(`amostras[${i}].data_coleta (string) é obrigatório.`);
        });
    }

    return erros;
}

// ═══════════════════════════════════════════════════════════════
// Exportar Relatório (window.print com formatação CSS)
// ═══════════════════════════════════════════════════════════════
function exportarRelatorio() {
    window.print();
}
