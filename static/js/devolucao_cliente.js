document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("formReturn");
    const summaryDiv = document.getElementById("returnSummary");
    const damageGroup = document.getElementById("damageValueGroup");

    let lastPreview = null;

    if (!form) return;

    form.has_damage.forEach(radio => {
        radio.addEventListener("change", () => {
            if (radio.value === "yes" && radio.checked) {
                damageGroup.style.display = "block";
            } else if (radio.value === "no" && radio.checked) {
                damageGroup.style.display = "none";
                document.getElementById("damage_value").value = "0";
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

            const balanceAfterDeposit = s.final_total - s.deposit;
            const owesAmount = balanceAfterDeposit > 0 ? balanceAfterDeposit : 0;
            const refundAmount = balanceAfterDeposit < 0 ? Math.abs(balanceAfterDeposit) : 0;

            const paymentHTML = balanceAfterDeposit > 0
                ? `<div class="payment-row owes-row">
                    <span class="payment-label">⚠️ Você deve pagar:</span>
                    <span class="payment-value-highlight">R$ ${owesAmount.toFixed(2)}</span>
                  </div>`
                : `<div class="payment-row refund-row">
                    <span class="payment-label">💰 Reembolso:</span>
                    <span class="payment-value-highlight">R$ ${refundAmount.toFixed(2)}</span>
                  </div>`;

            summaryDiv.innerHTML = `
                <h3>📋 Resumo da Devolução</h3>
                <div class="summary-grid">
                    <div class="summary-item">
                        <span class="label">Dias Contratados</span>
                        <span class="value">${s.days_contracted}</span>
                    </div>
                    <div class="summary-item">
                        <span class="label">Dias Utilizados</span>
                        <span class="value">${s.days_used}</span>
                    </div>
                    <div class="summary-item">
                        <span class="label">Diárias Extras</span>
                        <span class="value">${s.extra_days} <span class="fee">(R$ ${s.extra_days_fee.toFixed(2)})</span></span>
                    </div>
                    <div class="summary-item">
                        <span class="label">Quilometragem Total</span>
                        <span class="value">${s.total_km} km</span>
                    </div>
                    <div class="summary-item">
                        <span class="label">Km Extras</span>
                        <span class="value">${s.extra_km} km <span class="fee">(R$ ${s.extra_km_fee.toFixed(2)})</span></span>
                    </div>
                    <div class="summary-item">
                        <span class="label">Taxa de Danos</span>
                        <span class="value">R$ ${s.damage_fee.toFixed(2)}</span>
                    </div>
                </div>

                <div class="summary-divider"></div>

                <div class="summary-calculation">
                    <div class="calc-row">
                        <span class="calc-label">Valor Base do Aluguel:</span>
                        <span class="calc-value">R$ ${s.base_total.toFixed(2)}</span>
                    </div>
                    <div class="calc-row">
                        <span class="calc-label">Custos Adicionais:</span>
                        <span class="calc-value">R$ ${(s.extra_days_fee + s.extra_km_fee + s.damage_fee).toFixed(2)}</span>
                    </div>
                    <div class="calc-row total-final-row">
                        <span class="calc-label">Total a Pagar:</span>
                        <span class="calc-value-final">R$ ${s.final_total.toFixed(2)}</span>
                    </div>
                </div>

                <div class="summary-divider"></div>

                <div class="payment-section">
                    <div class="payment-row">
                        <span class="payment-label">Caução Paga:</span>
                        <span class="payment-value">R$ ${s.deposit.toFixed(2)}</span>
                    </div>
                    ${paymentHTML}
                </div>

                <button id="btnConfirmReturn" class="btn-confirm">
                    ✓ Confirmar Devolução
                </button>
            `;

            summaryDiv.classList.add("show");

            const btnConfirm = document.getElementById("btnConfirmReturn");
            btnConfirm.addEventListener("click", async () => {
                if (!lastPreview) return;

                btnConfirm.disabled = true;
                btnConfirm.textContent = "Processando...";

                try {
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
                        btnConfirm.disabled = false;
                        btnConfirm.textContent = "✓ Confirmar Devolução";
                        return;
                    }

                    const finalSummary = confirmData.summary;
                    const finalBalance = finalSummary.final_total - finalSummary.deposit;

                    const successPaymentHTML = finalBalance > 0
                        ? `<div class="detail-row owes-detail">
                            <span class="detail-label">⚠️ Total a Pagar:</span>
                            <span class="detail-value">R$ ${finalBalance.toFixed(2)}</span>
                          </div>`
                        : `<div class="detail-row refund-detail">
                            <span class="detail-label">💰 Reembolso:</span>
                            <span class="detail-value">R$ ${Math.abs(finalBalance).toFixed(2)}</span>
                          </div>`;

                    summaryDiv.innerHTML = `
                        <h3>✅ Aluguel Finalizado com Sucesso!</h3>
                        <div class="success-message">
                            <p>Obrigado por utilizar os serviços Kurumaya!</p>
                            <div class="success-details">
                                <div class="detail-row">
                                    <span class="detail-label">Total Cobrado:</span>
                                    <span class="detail-value">R$ ${finalSummary.final_total.toFixed(2)}</span>
                                </div>
                                <div class="detail-row">
                                    <span class="detail-label">Caução Paga:</span>
                                    <span class="detail-value">R$ ${finalSummary.deposit.toFixed(2)}</span>
                                </div>
                                ${successPaymentHTML}
                            </div>
                        </div>
                    `;

                    setTimeout(() => {
                        window.location.href = "/frota";
                    }, 3000);
                } catch (err) {
                    console.error("Erro ao confirmar:", err);
                    alert("Erro ao processar a confirmação.");
                    btnConfirm.disabled = false;
                    btnConfirm.textContent = "✓ Confirmar Devolução";
                }
            });

        } catch (err) {
            console.error("Erro inesperado no JS:", err);
            alert("Erro inesperado ao simular devolução.");
        }
    });
});
