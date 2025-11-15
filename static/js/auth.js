// =============== LOGIN ===============

const loginForm = document.getElementById("form-login");
if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const data = new FormData(loginForm);

        const res = await fetch("/auth/login", {
            method: "POST",
            body: data,
        });

        const result = await res.json();

        const msg = document.getElementById("loginMsg");
        if (msg) {
            msg.innerText = result.ok ? "Login realizado!" : result.error;
            msg.style.color = result.ok ? "green" : "red";
        }

        if (result.ok) {
            window.location.href = result.redirect;
        }
    });
}



// =============== SIGN-IN (CADASTRO) ===============

const signinForm = document.getElementById("form-signin");
if (signinForm) {
    signinForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const data = new FormData(signinForm);

        const res = await fetch("/auth/cadastro", {
            method: "POST",
            body: data,
        });

        const result = await res.json();

        const msg = document.getElementById("signupMsg");
        if (msg) {
            msg.innerText = result.ok ? "Conta criada com sucesso!" : result.error;
            msg.style.color = result.ok ? "green" : "red";
        }

        if (result.ok) {
            window.location.href = result.redirect;
        }
    });
}
