// json_input.js — Processa JSON colado manualmente e renderiza dashboard
// Usa funções do chart_common.js

function processarJSON() {
    const textarea = document.getElementById('jsonInput');
    const errorsDiv = document.getElementById('validationErrors');
    const resultDiv = document.getElementById('renderResult');

    // Limpar estados anteriores
    errorsDiv.innerHTML = '';
    resultDiv.innerHTML = '';
    document.getElementById('btnExport').style.display = 'none';

    // 1. Tentar parsear o JSON
    let payload;
    try {
        payload = JSON.parse(textarea.value);
    } catch (e) {
        errorsDiv.innerHTML = `
            <div class="validation-errors">
                <h4>⚠️ JSON Inválido</h4>
                <ul><li>${e.message}</li></ul>
            </div>`;
        return;
    }

    // 2. Validar o payload
    const erros = validarPayload(payload);
    if (erros.length > 0) {
        errorsDiv.innerHTML = `
            <div class="validation-errors">
                <h4>⚠️ Erros de Validação (${erros.length})</h4>
                <ul>${erros.map(e => `<li>${e}</li>`).join('')}</ul>
            </div>`;
        return;
    }

    // 3. Renderizar dashboard
    renderizarDashboard(payload, resultDiv);
}

function renderizarDashboard(data, container) {
    const tipo = data.tipo_carta;
    const amostras = data.amostras;
    const limites = data.limites_controle;
    const labels = amostras.map(a => {
        try {
            return new Date(a.data_coleta).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
        } catch {
            return a.data_coleta;
        }
    });

    // Header do resultado
    container.innerHTML = `
        <div class="render-result">
            <div class="header">
                <h2>${data.nome} (Carta ${tipo})</h2>
            </div>
            <div id="chartContainerJson"></div>
            <div id="memoriaCalculoJson"></div>
        </div>`;

    const chartContainer = document.getElementById('chartContainerJson');

    // Renderizar gráficos por tipo
    if (tipo === 'XR') {
        const zonasX = limites.Sigma !== undefined ? { lsc_1s: limites.LSC_X_1S, lsc_2s: limites.LSC_X_2S, lic_1s: limites.LIC_X_1S, lic_2s: limites.LIC_X_2S } : null;
        const alertas = limites.alertas_avancados || null;

        criarCanvas(chartContainer, 'canvasXJson');
        renderizarGrafico('canvasXJson', 'Gráfico de Médias (X̄)', labels,
            amostras.map(a => a.ponto_x), limites.LSC_X, limites.LIC_X, limites.LC_X, '#3b82f6', zonasX, alertas);

        criarCanvas(chartContainer, 'canvasRJson');
        renderizarGrafico('canvasRJson', 'Gráfico de Amplitudes (R)', labels,
            amostras.map(a => a.ponto_r), limites.LSC_R, limites.LIC_R, limites.LC_R, '#f97316');

    } else if (tipo === 'IMR') {
        const zonasI = limites.Sigma !== undefined ? { lsc_1s: limites.LSC_I_1S, lsc_2s: limites.LSC_I_2S, lic_1s: limites.LIC_I_1S, lic_2s: limites.LIC_I_2S } : null;
        const alertas = limites.alertas_avancados || null;

        criarCanvas(chartContainer, 'canvasIJson');
        renderizarGrafico('canvasIJson', 'Gráfico Individual (I)', labels,
            amostras.map(a => a.ponto_x), limites.LSC_I, limites.LIC_I, limites.LC_I, '#a855f7', zonasI, alertas);

        criarCanvas(chartContainer, 'canvasMRJson');
        renderizarGrafico('canvasMRJson', 'Gráfico de Amplitude Móvel (MR)', labels,
            amostras.map(a => a.ponto_mr), limites.LSC_MR, limites.LIC_MR, limites.LC_MR, '#14b8a6');

    } else if (tipo === 'P' || tipo === 'U') {
        const labelNome = tipo === 'P' ? 'Proporção de Defeituosos (p)' : 'Taxa de Defeitos (u)';
        const cor = tipo === 'P' ? '#ef4444' : '#f97316';

        criarCanvas(chartContainer, 'canvasAtributoJson');
        renderizarGrafico('canvasAtributoJson', labelNome, labels,
            amostras.map(a => a.ponto_grafico),
            limites[`LSC_${tipo}`], limites[`LIC_${tipo}`], limites[`LC_${tipo}`], cor);
    }

    // Memória de cálculo
    document.getElementById('memoriaCalculoJson').innerHTML = gerarMemoriaCalculo(data);

    // Mostrar botão exportar
    document.getElementById('btnExport').style.display = '';

    // Scroll suave para o resultado
    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function limparTudo() {
    document.getElementById('jsonInput').value = '';
    document.getElementById('validationErrors').innerHTML = '';
    document.getElementById('renderResult').innerHTML = '';
    document.getElementById('btnExport').style.display = 'none';
}
