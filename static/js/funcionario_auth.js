document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form-login-funcionario");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const data = {
      email: document.getElementById("email_func").value,
      password: document.getElementById("password_func").value,
    };

    const res = await fetch("/api/funcionarios/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const json = await res.json();

    alert(json.message);

    if (res.ok) {
      window.location.href = "/frota";
    }
  });
});
