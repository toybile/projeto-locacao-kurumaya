// static/js/auth_ui.js
document.addEventListener("DOMContentLoaded", async () => {
    try {
        const res = await fetch("/api/auth/status");
        const data = await res.json();

        // Seleciona os botões (ajusta os seletores pros seus botões reais)
        const loginBtn = document.querySelector('a[href="/login"]');
        const cadastroBtn = document.querySelector('a[href="/signin"]');
        const logoutBtn = document.querySelector('a[href="/logout"]');
        const loginFuncBtn = document.querySelector('a[href="/funcionario/login"]');

        if (data.logged_in) {
            // Usuário LOGADO: esconde login/cadastro, mostra logout
            if (loginBtn) loginBtn.style.display = "none";
            if (cadastroBtn) cadastroBtn.style.display = "none";
            if (loginFuncBtn) loginFuncBtn.style.display = "none";
            if (logoutBtn) logoutBtn.style.display = "inline-block";
        } else {
            // Usuário NÃO LOGADO: mostra login/cadastro, esconde logout
            if (loginBtn) loginBtn.style.display = "inline-block";
            if (cadastroBtn) cadastroBtn.style.display = "inline-block";
            if (loginFuncBtn) loginFuncBtn.style.display = "inline-block";
            if (logoutBtn) logoutBtn.style.display = "none";
        }
    } catch (err) {
        console.error("Erro ao verificar status de login:", err);
    }
});
