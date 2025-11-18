const VEHICLE_API = "/api/vehicles";
const DEFAULT_IMG = "/static/img/default-car.jpg";

document.addEventListener("DOMContentLoaded", () => {
    loadVehicles();
    const form = document.getElementById("formAddVehicle");
    if (form) form.addEventListener("submit", handleFormSubmit);
});

async function handleFormSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const data = {
        plate: form.plate.value.trim(),
        brand: form.brand.value.trim(),
        model: form.model.value.trim(),
        year: +form.year.value,
        category: form.category.value,
        price: +form.price.value,
        image: form.image.value.trim() || null
    };

    if (!Object.values(data).slice(0, -1).every(v => v)) {
        alert("Preencha todos os campos obrigatórios.");
        return;
    }

    try {
        const res = await fetch(VEHICLE_API, {
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
}

async function loadVehicles() {
    const container = document.getElementById("vehiclesList");
    container.innerHTML = "<p>Carregando veículos...</p>";

    try {
        const res = await fetch(VEHICLE_API);
        if (!res.ok) throw new Error("Erro ao carregar");
        
        const data = await res.json();
        
        if (!Array.isArray(data) || !data.length) {
            container.innerHTML = "<p>Nenhum veículo cadastrado.</p>";
            return;
        }

        container.innerHTML = data.map(v => `
            <div class="vehicle-card">
                <div class="vehicle-image">
                    <img src="${v.image || DEFAULT_IMG}" alt="${v.model}" onerror="this.src='${DEFAULT_IMG}'">
                </div>
                <div class="vehicle-info">
                    <h3>${v.brand} ${v.model} (${v.year})</h3>
                    <div class="vehicle-details">
                        <div class="vehicle-detail"><strong>Placa:</strong><span>${v.plate}</span></div>
                        <div class="vehicle-detail"><strong>Categoria:</strong><span>${v.category}</span></div>
                        <div class="vehicle-detail"><strong>Preço/dia:</strong><span>R$ ${(+v.price).toFixed(2)}</span></div>
                        <div class="vehicle-detail"><strong>Status:</strong><span>${v.status}</span></div>
                    </div>
                    <div class="vehicle-actions">
                        <button class="btn-edit" data-id="${v.id}">Editar</button>
                        <button class="btn-delete" data-id="${v.id}">Remover</button>
                    </div>
                </div>
            </div>
        `).join("");

        document.querySelectorAll(".btn-delete").forEach(btn => {
            btn.addEventListener("click", () => deletarVeiculo(+btn.dataset.id));
        });
    } catch (err) {
        console.error(err);
        container.innerHTML = "<p>Erro inesperado ao carregar veículos.</p>";
    }
}

async function deletarVeiculo(id) {
    if (!confirm("Remover este veículo?")) return;

    try {
        const req = await fetch(`${VEHICLE_API}/${id}`, { method: "DELETE" });
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
