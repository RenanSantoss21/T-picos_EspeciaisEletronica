// index.js — Carrega processos da API e popula o grid
async function carregarProcessos() {
    try {
        const response = await fetch('/api/processos/');
        const processos = await response.json();
        const grid = document.getElementById('processosGrid');

        processos.forEach(proc => {
            const card = document.createElement('a');
            card.href = `/dashboard/${proc.id}/`;
            card.className = 'card';

            // Badge com cor por tipo de carta
            const badgeClass = `badge badge-${proc.tipo_carta.toLowerCase()}`;

            card.innerHTML = `
                <h3>${proc.nome}</h3>
                <p><span class="${badgeClass}">Carta ${proc.tipo_carta}</span></p>
            `;
            grid.appendChild(card);
        });
    } catch (error) {
        console.error("Erro ao carregar os processos:", error);
        const grid = document.getElementById('processosGrid');
        // Manter o card de JSON input, apenas adicionar mensagem de erro
        const errDiv = document.createElement('div');
        errDiv.className = 'card';
        errDiv.innerHTML = '<p style="color: var(--accent-red);">Erro ao conectar com a API. Verifique se você está logado.</p>';
        grid.appendChild(errDiv);
    }
}

// Inicializa
carregarProcessos();