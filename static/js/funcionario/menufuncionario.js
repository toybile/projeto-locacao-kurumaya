document.addEventListener("DOMContentLoaded", () => {
    loadVehicles();

    const form = document.getElementById("formAddVehicle");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const data = {
            plate: document.getElementById("plate").value,
            model: document.getElementById("model").value,
            year: document.getElementById("year").value
        };

        const res = await fetch("/api/vehicles", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const json = await res.json();

        if (!json.ok) {
            alert(json.error);
            return;
        }

        form.reset();
        loadVehicles();
    });
});


async function loadVehicles() {
    const container = document.getElementById("vehiclesList");
    container.innerHTML = "<p>Carregando...</p>";

    const res = await fetch("/api/vehicles");
    const data = await res.json();

    if (!data.length) {
        container.innerHTML = "<p>Nenhum veículo cadastrado.</p>";
        return;
    }

    container.innerHTML = "";

    data.forEach(v => {
        const item = document.createElement("div");
        item.classList.add("vehicle_item");

        item.innerHTML = `
            <strong>${v.model}</strong> (${v.year}) — <b>${v.plate}</b>
            <p>Status: ${v.status}</p>

            <button onclick="deletarVeiculo(${v.id})">Remover</button>

        `;

        container.appendChild(item);
    });

    document.querySelectorAll(".remove_btn").forEach(btn => {
        btn.addEventListener("click", async () => {
            const id = parseInt(btn.dataset.id);

            await fetch("/api/vehicles", {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ id: id, status: "deleted" })
            });

            loadVehicles();
        });
    });
}

async function deletarVeiculo(id) {
    if (!confirm("Tem certeza que quer remover?")) return;

    const req = await fetch(`/api/veiculos/${id}`, {
        method: "DELETE"
    });

    const res = await req.json();

    if (req.ok) {
        alert("Veículo removido com sucesso!");
        loadVehicles();
    } else {
        alert(res.error);
    }
}

