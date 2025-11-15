async function loadVehicles() {
    const container = document.getElementById("vehiclesList");
    container.innerHTML = "<p>Carregando...</p>";

    const res = await fetch("/api/vehicles");
    const vehicles = await res.json();

    if (!vehicles.length) {
        container.innerHTML = "<p>Nenhum veículo cadastrado.</p>";
        return;
    }

    container.innerHTML = "";

    vehicles.forEach(v => {
        const card = document.createElement("div");
        card.className = "vehicle_card";

        const statusClass = v.status === "available" ? "available" : "rented";
        const statusText = v.status === "available" ? "Disponível" : "Alugado";

        card.innerHTML = `
            <div>
                <h3>${v.model} (${v.year})</h3>
                <p>Placa: <strong>${v.plate}</strong></p>
                <p>Status: <span class="status ${statusClass}">${statusText}</span></p>
            </div>

            <button data-id="${v.id}">
                ${v.status === "available" ? "Alugar" : "Devolver"}
            </button>
        `;

        container.appendChild(card);
    });

    addButtonEvents();
}

function addButtonEvents() {
    const buttons = document.querySelectorAll(".vehicle_card button");

    buttons.forEach(btn => {
        btn.addEventListener("click", async () => {
            const id = btn.getAttribute("data-id");

            const newStatus = btn.innerText === "Alugar" ? "rented" : "available";

            await fetch("/api/vehicles", {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    id: Number(id),
                    status: newStatus
                })
            });

            loadVehicles();
        });
    });
}

// Carrega tudo ao entrar na página
loadVehicles();
