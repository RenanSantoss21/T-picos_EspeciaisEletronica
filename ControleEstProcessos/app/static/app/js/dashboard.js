// dashboard.js — Busca dados da API e renderiza gráficos + memória de cálculo
// Usa funções do chart_common.js (criarCanvas, renderizarGrafico, gerarMemoriaCalculo)

const metaTag = document.querySelector('meta[name="processo-id"]');
const processoId = metaTag ? metaTag.content : null;
const API_URL = `/api/processos/${processoId}/`;

async function initDashboard() {
    if (!processoId) return;

    try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error("Erro ao buscar dados.");
        const data = await response.json();

        // Atualizar título
        const titulo = document.getElementById('tituloProcesso');
        titulo.innerText = `${data.nome} (Carta ${data.tipo_carta})`;
        titulo.classList.remove('loading');

        // Mostrar botão de exportar
        document.getElementById('btnExport').style.display = '';

        const container = document.getElementById('chartContainer');
        const amostras = data.amostras;
        const labels = amostras.map(a => new Date(a.data_coleta).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' }));
        const limites = data.limites_controle;

        // ── Renderizar gráficos por tipo ──
        if (data.tipo_carta === 'XR') {
            criarCanvas(container, 'canvasX');
            renderizarGrafico('canvasX', 'Gráfico de Médias (X̄)', labels, amostras.map(a => a.ponto_x), limites.LSC_X, limites.LIC_X, limites.LC_X, '#3b82f6');
            
            criarCanvas(container, 'canvasR');
            renderizarGrafico('canvasR', 'Gráfico de Amplitudes (R)', labels, amostras.map(a => a.ponto_r), limites.LSC_R, limites.LIC_R, limites.LC_R, '#f97316');

        } else if (data.tipo_carta === 'IMR') {
            criarCanvas(container, 'canvasI');
            renderizarGrafico('canvasI', 'Gráfico Individual (I)', labels, amostras.map(a => a.ponto_x), limites.LSC_I, limites.LIC_I, limites.LC_I, '#a855f7');
            
            criarCanvas(container, 'canvasMR');
            renderizarGrafico('canvasMR', 'Gráfico de Amplitude Móvel (MR)', labels, amostras.map(a => a.ponto_mr), limites.LSC_MR, limites.LIC_MR, limites.LC_MR, '#14b8a6');

        } else if (data.tipo_carta === 'P' || data.tipo_carta === 'U') {
            const labelNome = data.tipo_carta === 'P' ? 'Proporção de Defeituosos (p)' : 'Taxa de Defeitos (u)';
            const lscKey = `LSC_${data.tipo_carta}`;
            const licKey = `LIC_${data.tipo_carta}`;
            const lcKey = `LC_${data.tipo_carta}`;
            const cor = data.tipo_carta === 'P' ? '#ef4444' : '#f97316';

            criarCanvas(container, 'canvasAtributo');
            renderizarGrafico('canvasAtributo', labelNome, labels, amostras.map(a => a.ponto_grafico), limites[lscKey], limites[licKey], limites[lcKey], cor);
        }

        // ── Memória de Cálculo ──
        document.getElementById('memoriaCalculo').innerHTML = gerarMemoriaCalculo(data);

    } catch (err) {
        console.error(err);
        const titulo = document.getElementById('tituloProcesso');
        titulo.classList.remove('loading');
        titulo.innerText = 'Erro ao carregar';
        document.getElementById('chartContainer').innerHTML = '<p style="color: var(--accent-red); text-align: center; padding: 40px;">Falha ao carregar o gráfico do processo.</p>';
    }
}

initDashboard();