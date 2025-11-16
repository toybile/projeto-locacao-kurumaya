document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("formReturn");
    const summaryDiv = document.getElementById("returnSummary");
    const damageGroup = document.getElementById("damageValueGroup");

    let lastPreview = null; // guarda os dados da última simulação

    if (!form) return;

    // Mostrar / esconder campo de valor de danos
    form.has_damage.forEach(radio => {
        radio.addEventListener("change", () => {
            if (radio.value === "yes" && radio.checked) {
                damageGroup.style.display = "block";
            } else if (radio.value === "no" && radio.checked) {
                damageGroup.style.display = "none";
            }
        });
    });

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const rental_id = Number(document.getElementById("rental_id").value);
        const end_km = Number(document.getElementById("end_km").value);

        const hasDamage = [...form.has_damage].find(r => r.checked)?.value === "yes";
        const damage_value = hasDamage ? Number(document.getElementById("damage_value").value) || 0 : 0;

        if (!rental_id || end_km < 0) {
            alert("Preencha os campos corretamente.");
            return;
        }

        try {
    const res = await fetch("/api/rent/return/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rental_id, end_km, damage_value })
    });

    const data = await res.json().catch(() => null);

    if (!res.ok || !data || !data.ok) {
        console.error("Erro na API de preview:", res.status, data);
        alert((data && data.error) || `Erro ao simular devolução (status ${res.status}).`);
        return;
    }
            const s = data.summary;
            lastPreview = { rental_id, end_km, damage_value, summary: s };

            summaryDiv.innerHTML = `
                <h3>Resumo da devolução (simulação)</h3>
                <p><strong>Dias contratados:</strong> ${s.days_contracted}</p>
                <p><strong>Dias usados:</strong> ${s.days_used}</p>
                <p><strong>Diárias extras:</strong> ${s.extra_days} (R$ ${s.extra_days_fee.toFixed(2)})</p>
                <p><strong>Quilometragem total:</strong> ${s.total_km} km</p>
                <p><strong>Km extras:</strong> ${s.extra_km} (R$ ${s.extra_km_fee.toFixed(2)})</p>
                <p><strong>Taxa de danos:</strong> R$ ${s.damage_fee.toFixed(2)}</p>
                <p><strong>Valor base do aluguel:</strong> R$ ${s.base_total.toFixed(2)}</p>
                <p><strong>Valor final:</strong> R$ ${s.final_total.toFixed(2)}</p>
                <p><strong>Caução:</strong> R$ ${s.deposit.toFixed(2)}</p>
                <p><strong>Valor a devolver:</strong> R$ ${s.refund.toFixed(2)}</p>
                <button id="btnConfirmReturn" class="btn-primary" style="margin-top:12px;">
                    Confirmar devolução
                </button>
            `;

            const btnConfirm = document.getElementById("btnConfirmReturn");
            btnConfirm.addEventListener("click", async () => {
                if (!lastPreview) return;

                const confirmRes = await fetch("/api/rent/return/confirm", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        rental_id: lastPreview.rental_id,
                        end_km: lastPreview.end_km,
                        damage_value: lastPreview.damage_value
                    })
                });

                const confirmData = await confirmRes.json();

                if (!confirmData.ok) {
                    alert(confirmData.error || "Erro ao confirmar devolução.");
                    return;
                }

                alert("Aluguel finalizado com sucesso! Você será redirecionado para a frota.");
                window.location.href = "/frota";
            });

        } catch (err) {
        console.error("Erro inesperado no JS:", err);
        alert("Erro inesperado ao simular devolução.");
    }
    });
});
