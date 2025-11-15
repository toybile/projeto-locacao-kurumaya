document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const form = e.target;
    const data = new FormData(form);

    const response = await fetch("/auth/login", {
        method: "POST",
        body: data
    });

    const result = await response.json();

    const msg = document.getElementById("loginMsg");

    if (!result.ok) {
        msg.innerText = result.error;
        msg.style.color = "red";
        return;
    }

    msg.innerText = "Login realizado!";
    msg.style.color = "green";

    // Redireciona
    window.location.href = result.redirect;
});
