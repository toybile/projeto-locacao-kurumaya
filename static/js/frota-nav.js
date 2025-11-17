document.addEventListener("DOMContentLoaded", async () => {
    try {
        const res = await fetch("/api/auth/status");
        const data = await res.json();

        const devolucaoLink = document.querySelector('a[href="/devolucao"]');
        const historicoLink = document.querySelector('a[href="/historico"]');

        if (data.logged_in) {
            if (devolucaoLink) devolucaoLink.style.display = "inline-block";
            if (historicoLink) historicoLink.style.display = "inline-block";
        } else {
            if (devolucaoLink) devolucaoLink.style.display = "none";
            if (historicoLink) historicoLink.style.display = "none";
        }
    } catch (err) {
        console.error("Erro ao verificar status de login:", err);
    }
});