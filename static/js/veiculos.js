document.addEventListener("DOMContentLoaded", () => {
    loadVehicles();

    const form = document.getElementById("formAddVehicle");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const data = {
            plate: document.getElementById("plate").value.trim(),
            brand: document.getElementById("brand").value.trim(),
            model: document.getElementById("model").value.trim(),
            year: Number(document.getElementById("year").value),
            category: document.getElementById("category").value,
            price: Number(document.getElementById("price").value),
            image: document.getElementById("image").value.trim() || null
        };

        if (!data.plate || !data.brand || !data.model || !data.year || !data.category || !data.price) {
            alert("Preencha todos os campos obrigatórios.");
            return;
        }

        try {
            const res = await fetch("/api/vehicles", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });

            const json = await res.json();

            if (!json.ok) {
                alert(json.error || "Erro ao cadastrar veículo.");
                return;
            }

            alert("Veículo cadastrado com sucesso!");
            form.reset();
            loadVehicles();
        } catch (err) {
            console.error(err);
            alert("Erro inesperado ao cadastrar veículo.");
        }
    });
});

async function loadVehicles() {
    const container = document.getElementById("vehiclesList");
    container.innerHTML = "<p>Carregando veículos...</p>";

    try {
        const res = await fetch("/api/vehicles");
        if (!res.ok) {
            container.innerHTML = "<p>Erro ao carregar veículos.</p>";
            return;
        }

        const data = await res.json();

        if (!Array.isArray(data) || !data.length) {
            container.innerHTML = "<p>Nenhum veículo cadastrado.</p>";
            return;
        }

        container.innerHTML = "";

        data.forEach(v => {
            const item = document.createElement("div");
            item.classList.add("vehicle_item");

            const imgSrc = v.image || "/static/img/default-car.jpg";

            item.innerHTML = `
                <img src="${imgSrc}" alt="${v.model}" class="vehicle_image"
                    onerror="this.onerror=null; this.src='/static/img/default-car.jpg';">
                <div class="vehicle_info">
                    <h3>${v.brand} ${v.model} (${v.year})</h3>
                    <p><strong>Placa:</strong> ${v.plate}</p>
                    <p><strong>Categoria:</strong> ${v.category}</p>
                    <p><strong>Preço por dia:</strong> R$ ${Number(v.price).toFixed(2)}</p>
                    <p><strong>Status:</strong> ${v.status}</p>
                    <button class="remove_btn" data-id="${v.id}">Remover</button>
                </div>
            `;


            container.appendChild(item);
        });

        document.querySelectorAll(".remove_btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                const id = Number(btn.dataset.id);
                await deletarVeiculo(id);
            });
        });
    } catch (err) {
        console.error(err);
        container.innerHTML = "<p>Erro inesperado ao carregar veículos.</p>";
    }
}

async function deletarVeiculo(id) {
    if (!confirm("Tem certeza que deseja remover este veículo?")) return;

    try {
        const req = await fetch(`/api/vehicles/${id}`, { method: "DELETE" });
        const res = await req.json();

        if (req.ok && res.ok) {
            alert("Veículo removido com sucesso!");
            loadVehicles();
        } else {
            alert(res.error || "Erro ao remover veículo.");
        }
    } catch (err) {
        console.error(err);
        alert("Erro inesperado ao remover veículo.");
    }
}
