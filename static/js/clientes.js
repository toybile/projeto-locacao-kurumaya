document.addEventListener("DOMContentLoaded", carregarClientes);

async function carregarClientes() {
    const container = document.getElementById("clientes-container");
    container.innerHTML = "<p>Carregando clientes...</p>";

    try {
        const res = await fetch("/api/clients");

        if (!res.ok) {
            container.innerHTML = "<p>Erro ao carregar clientes.</p>";
            return;
        }

        const data = await res.json();

        if (!Array.isArray(data) || !data.length) {
            container.innerHTML = "<p>Nenhum cliente cadastrado.</p>";
            return;
        }

        container.innerHTML = "";

        data.forEach(c => {
            const item = document.createElement("div");
            item.classList.add("client-item");
            item.style.cssText = "border: 1px solid #ccc; padding: 15px; margin-bottom: 15px; border-radius: 8px;";

            item.innerHTML = `
                <h3>${c.name}</h3>
                <p><strong>E-mail:</strong> ${c.email}</p>
                <p><strong>Telefone:</strong> ${c.phone}</p>
            `;

            container.appendChild(item);
        });
    } catch (err) {
        console.error(err);
        container.innerHTML = "<p>Erro inesperado ao carregar clientes.</p>";
    }
}
