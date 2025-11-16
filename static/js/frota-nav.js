document.addEventListener("DOMContentLoaded", async () => {
    try {
        const res = await fetch("/api/auth/status");
        const data = await res.json();

        // Seleciona os links da nav (ajusta os seletores conforme seus links)
        const devolucaoLink = document.querySelector('a[href="/devolucao"]');
        const historicoLink = document.querySelector('a[href="/historico"]');

        if (data.logged_in) {
            // Usuário LOGADO: mostra Devolução e Histórico
            if (devolucaoLink) devolucaoLink.style.display = "inline-block";
            if (historicoLink) historicoLink.style.display = "inline-block";
        } else {
            // Usuário NÃO LOGADO: esconde Devolução e Histórico
            if (devolucaoLink) devolucaoLink.style.display = "none";
            if (historicoLink) historicoLink.style.display = "none";
        }
    } catch (err) {
        console.error("Erro ao verificar status de login:", err);
    }
});