document.addEventListener("DOMContentLoaded", carregarHistorico);

async function carregarHistorico() {
    const container = document.getElementById("history-container");
    container.innerHTML = "<p>Carregando histórico...</p>";

    try {
        const res = await fetch("/api/rentals/history");
        if (!res.ok) {
            container.innerHTML = "<p>Erro ao carregar histórico.</p>";
            return;
        }

        const data = await res.json();

        if (!data.length) {
            container.innerHTML = "<p>Você ainda não possui aluguéis.</p>";
            return;
        }

        container.innerHTML = "";

        data.forEach(r => {
            const item = document.createElement("div");
            item.classList.add("rental-item");

            item.innerHTML = `
                <h3>${r.model} (${r.year}) - ${r.plate}</h3>
                <p>Dias alugados: <strong>${r.days}</strong></p>
                <p>Preço por dia: <strong>R$ ${r.price_per_day.toFixed(2)}</strong></p>
                <p>Total pago: <strong>R$ ${r.total.toFixed(2)}</strong></p>
                <p>Código do aluguel: #${r.rental_id}</p>
            `;

            container.appendChild(item);
        });
    } catch (err) {
        console.error(err);
        container.innerHTML = "<p>Erro inesperado ao carregar histórico.</p>";
    }
}
