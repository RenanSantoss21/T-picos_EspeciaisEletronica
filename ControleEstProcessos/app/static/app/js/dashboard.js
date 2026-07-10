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

        window.charts = {}; // Para salvar as instâncias

        // ── Renderizar gráficos por tipo ──
        if (data.tipo_carta === 'XR') {
            criarCanvas(container, 'canvasX');
            window.charts['canvasX'] = renderizarGrafico('canvasX', 'Gráfico de Médias (X̄)', labels, amostras.map(a => a.ponto_x), limites.LSC_X, limites.LIC_X, limites.LC_X, '#3b82f6');
            
            criarCanvas(container, 'canvasR');
            window.charts['canvasR'] = renderizarGrafico('canvasR', 'Gráfico de Amplitudes (R)', labels, amostras.map(a => a.ponto_r), limites.LSC_R, limites.LIC_R, limites.LC_R, '#f97316');

        } else if (data.tipo_carta === 'IMR') {
            criarCanvas(container, 'canvasI');
            window.charts['canvasI'] = renderizarGrafico('canvasI', 'Gráfico Individual (I)', labels, amostras.map(a => a.ponto_x), limites.LSC_I, limites.LIC_I, limites.LC_I, '#a855f7');
            
            criarCanvas(container, 'canvasMR');
            window.charts['canvasMR'] = renderizarGrafico('canvasMR', 'Gráfico de Amplitude Móvel (MR)', labels, amostras.map(a => a.ponto_mr), limites.LSC_MR, limites.LIC_MR, limites.LC_MR, '#14b8a6');

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

        // INICIA O WEBSOCKET DEPOIS DE CARREGAR A TELA INICIAL
        iniciarWebSocket(data.tipo_carta);

    } catch (err) {
        console.error(err);
        const titulo = document.getElementById('tituloProcesso');
        titulo.classList.remove('loading');
        titulo.innerText = 'Erro ao carregar';
        document.getElementById('chartContainer').innerHTML = '<p style="color: var(--accent-red); text-align: center; padding: 40px;">Falha ao carregar o gráfico do processo.</p>';
    }
}

function iniciarWebSocket(tipo_carta) {
    const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const ws = new WebSocket(protocol + window.location.host + '/ws/telemetria/');

    ws.onmessage = function(e) {
        const msg = JSON.parse(e.data);

        // Verifica se é uma mensagem de broadcast 'nova_amostra'
        if (msg.type === "nova_amostra") {
            // Verifica se a mensagem pertence ao processo atual
            let amostra = null;
            let limites = null;

            if (processoId == msg.processo_temp_id) {
                amostra = msg.amostra_temp;
                limites = msg.limites_temp;
            } else if (processoId == msg.processo_hum_id) {
                amostra = msg.amostra_hum;
                limites = msg.limites_hum;
            }

            if (amostra && limites) {
                // É o nosso processo! Atualizamos o gráfico!
                const label = new Date(amostra.data_coleta).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
                
                if (tipo_carta === 'IMR') {
                    // Atualiza chart I
                    if (window.charts && window.charts['canvasI']) {
                        const c = window.charts['canvasI'];
                        c.data.labels.push(label);
                        c.data.datasets[0].data.push(amostra.ponto_x);
                        
                        // Atualiza as linhas de limite retroativamente para que fiquem retas com o novo cálculo
                        const len = c.data.labels.length;
                        c.data.datasets[1].data = Array(len).fill(limites.LSC_I);
                        c.data.datasets[2].data = Array(len).fill(limites.LC_I);
                        c.data.datasets[3].data = Array(len).fill(limites.LIC_I);
                        
                        c.update('none'); // update sem animação para ficar suave
                    }
                    
                    // Atualiza chart MR
                    if (window.charts && window.charts['canvasMR']) {
                        const c = window.charts['canvasMR'];
                        c.data.labels.push(label);
                        c.data.datasets[0].data.push(amostra.ponto_mr);
                        
                        const len = c.data.labels.length;
                        c.data.datasets[1].data = Array(len).fill(limites.LSC_MR);
                        c.data.datasets[2].data = Array(len).fill(limites.LC_MR);
                        c.data.datasets[3].data = Array(len).fill(limites.LIC_MR);
                        
                        c.update('none');
                    }

                    // Atualiza o painel lateral de memória de cálculo
                    const nAmostras = window.charts['canvasI'] ? window.charts['canvasI'].data.labels.length : 0;
                    const pseudoData = {
                        tipo_carta: 'IMR',
                        limites_controle: limites,
                        amostras: Array(nAmostras).fill({ valores: [0] })
                    };
                    document.getElementById('memoriaCalculo').innerHTML = gerarMemoriaCalculo(pseudoData);
                } else if (tipo_carta === 'XR') {
                    // Atualiza chart X
                    if (window.charts && window.charts['canvasX']) {
                        const c = window.charts['canvasX'];
                        c.data.labels.push(label);
                        c.data.datasets[0].data.push(amostra.ponto_x);
                        
                        // Atualiza as linhas de limite retroativamente para que fiquem retas
                        const len = c.data.labels.length;
                        c.data.datasets[1].data = Array(len).fill(limites.LSC_X);
                        c.data.datasets[2].data = Array(len).fill(limites.LC_X);
                        c.data.datasets[3].data = Array(len).fill(limites.LIC_X);
                        
                        c.update('none'); // update sem animação para ficar suave
                    }
                    
                    // Atualiza chart R
                    if (window.charts && window.charts['canvasR']) {
                        const c = window.charts['canvasR'];
                        c.data.labels.push(label);
                        c.data.datasets[0].data.push(amostra.ponto_r);
                        
                        const len = c.data.labels.length;
                        c.data.datasets[1].data = Array(len).fill(limites.LSC_R);
                        c.data.datasets[2].data = Array(len).fill(limites.LC_R);
                        c.data.datasets[3].data = Array(len).fill(limites.LIC_R);
                        
                        c.update('none');
                    }

                    // Atualiza o painel lateral de memória de cálculo
                    const nAmostras = window.charts['canvasX'] ? window.charts['canvasX'].data.labels.length : 0;
                    const pseudoData = {
                        tipo_carta: 'XR',
                        limites_controle: limites,
                        amostras: Array(nAmostras).fill({ valores: Array(10).fill(0) }) // mock for n=10
                    };
                    document.getElementById('memoriaCalculo').innerHTML = gerarMemoriaCalculo(pseudoData);
                } else if (tipo_carta === 'P' || tipo_carta === 'U') {
                    // Atualiza chart de Atributos
                    if (window.charts && window.charts['canvasPU']) {
                        const c = window.charts['canvasPU'];
                        
                        let amostraAttr = null;
                        let limitesAttr = null;
                        if (processoId == msg.proc_p_id && tipo_carta === 'P') {
                            amostraAttr = msg.amostra_p;
                            limitesAttr = msg.limites_p;
                        } else if (processoId == msg.proc_u_id && tipo_carta === 'U') {
                            amostraAttr = msg.amostra_u;
                            limitesAttr = msg.limites_u;
                        }

                        if (amostraAttr && limitesAttr) {
                            const dataLabel = new Date(amostraAttr.data_coleta).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'medium' });
                            c.data.labels.push(dataLabel);
                            c.data.datasets[0].data.push(amostraAttr.ponto_grafico);

                            // Atualiza as linhas de limite retroativamente para que fiquem retas
                            const len = c.data.labels.length;
                            const tLsc = tipo_carta === 'P' ? limitesAttr.LSC_P : limitesAttr.LSC_U;
                            const tLc = tipo_carta === 'P' ? limitesAttr.LC_P : limitesAttr.LC_U;
                            const tLic = tipo_carta === 'P' ? limitesAttr.LIC_P : limitesAttr.LIC_U;

                            c.data.datasets[1].data = Array(len).fill(tLsc);
                            c.data.datasets[2].data = Array(len).fill(tLc);
                            c.data.datasets[3].data = Array(len).fill(tLic);

                            c.update('none'); // update sem animação para ficar suave

                            // Atualiza o painel lateral de memória de cálculo
                            const pseudoData = {
                                tipo_carta: tipo_carta,
                                limites_controle: limitesAttr,
                                amostras: Array(len).fill({ tamanho_amostra: 10, quantidade_ocorrencias: 0 }) // mock
                            };
                            document.getElementById('memoriaCalculo').innerHTML = gerarMemoriaCalculo(pseudoData);
                        }
                    }
                }
            }
        }
    };

    ws.onclose = function() {
        console.warn("WebSocket fechado. Os gráficos pararam de atualizar em tempo real.");
    };
}

initDashboard();