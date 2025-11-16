document.addEventListener("DOMContentLoaded", carregarHistorico);

async function carregarHistorico() {
    const container = document.getElementById("history-container");
    container.innerHTML = "<p>Carregando histórico...</p>";

    console.log("Iniciando carregarHistorico...");

    try {
        const res = await fetch("/api/rentals/history");
        console.log("Resposta /api/rentals/history:", res.status);

        if (!res.ok) {
            container.innerHTML = "<p>Erro ao carregar histórico (status " + res.status + ").</p>";
            return;
        }

        const data = await res.json();
        console.log("Dados recebidos:", data);

        if (!Array.isArray(data) || !data.length) {
            container.innerHTML = "<p>Você ainda não possui aluguéis.</p>";
            return;
        }

        container.innerHTML = "";

        data.forEach(r => {
            const item = document.createElement("div");
            item.classList.add("rental-item");
            item.style.cssText = "border: 1px solid #ccc; padding: 15px; margin-bottom: 15px; border-radius: 8px;";

            const pricePerDay = Number(r.price_per_day);
            const total = Number(r.total);

            item.innerHTML = `
                <h3>${r.model} (${r.year}) - ${r.plate}</h3>
                <p><strong>Dias alugados:</strong> ${r.days}</p>
                <p><strong>Preço por dia:</strong> R$ ${pricePerDay.toFixed(2)}</p>
                <p><strong>Total pago:</strong> R$ ${total.toFixed(2)}</p>
                <p><strong>Código do aluguel:</strong> #${r.rental_id}</p>
            `;

            container.appendChild(item);
        });
    } catch (err) {
        console.error("Erro no carregarHistorico:", err);
        container.innerHTML = "<p>Erro inesperado ao carregar histórico.</p>";
    }
}
