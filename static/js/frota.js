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
        const buttonText = v.status === "available" ? "Alugar" : "Devolver";

        card.innerHTML = `
        <div>
            <h3>${v.model} (${v.year})</h3>
            <p>Placa: <strong>${v.plate}</strong></p>
            <p>Preço: <strong>R$ ${v.price},00 / dia</strong></p>
            <p>Status: <span class="status ${statusClass}">${statusText}</span></p>
        </div>

        <a href="/veiculo/${v.id}" class="btnDetails">Ver detalhes</a>
    `;



        container.appendChild(card);
    });

    attachRentButtons();
}

function attachRentButtons() {
    document.querySelectorAll(".rentBtn").forEach(btn => {
        btn.addEventListener("click", async () => {
            const id = Number(btn.dataset.id);
            const action = btn.innerText === "Alugar" ? "rented" : "available";

            const response = await fetch("/api/vehicles", {
                method: "PUT",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ id, status: action })
            });

            const result = await response.json();

            if (!result.ok) {
                alert("Erro ao alterar status do veículo.");
                return;
            }

            loadVehicles(); // atualiza a tela
        });
    });
}

// carregar automaticamente
loadVehicles();
