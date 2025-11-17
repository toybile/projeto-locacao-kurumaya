async function carregarVeiculo() {
    const vid = document.body.dataset.id;

    const res = await fetch(`/api/vehicles`);
    const vehicles = await res.json();

    const v = vehicles.find(x => x.id == vid);

    if (!v) {
        document.getElementById("info").innerHTML = "<p>Veículo não encontrado.</p>";
        return;
    }

    document.getElementById("car-model").innerText = `${v.model} (${v.year})`;
    document.getElementById("car-plate").innerText = v.plate;
    document.getElementById("car-price").innerText = v.price;

    atualizarTotal();
}

function atualizarTotal() {
    const price = Number(document.getElementById("car-price").innerText);
    const days = Number(document.getElementById("dias").value || 1);

    document.getElementById("total").innerText = (price * days).toFixed(2);
}

document.getElementById("dias").addEventListener("input", atualizarTotal);

document.getElementById("pagarBtn").addEventListener("click", async () => {
    const vid = Number(document.body.dataset.id);
    const days = Number(document.getElementById("dias").value);

    const res = await fetch("/api/rent/pay", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ id: vid, days })
    });

    const result = await res.json();

    if (!result.ok) {
        alert(result.error || "Erro no pagamento");
        return;
    }

    alert(`Aluguel concluído! Valor total: R$ ${result.total}`);
    window.location.href = "/frota";
});

carregarVeiculo();
