//   LOGIN DE FUNCIONÁRIO (STAFF)

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form-login-funcionario");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const oldMessage = document.querySelector(".login-message");
    if (oldMessage) oldMessage.remove();

    const emailInput = document.getElementById("email_func");
    const passwordInput = document.getElementById("password_func");

    if (!emailInput || !passwordInput) {
      showMessage("❌ Erro: Campos de login não encontrados", "error");
      return;
    }

    const email = emailInput.value.trim();
    const password = passwordInput.value;

    if (!email || !password) {
      showMessage("❌ Email e senha são obrigatórios!", "error");
      return;
    }

    if (email.length > 255) {
      showMessage("❌ Email muito longo!", "error");
      return;
    }

    if (password.length > 500) {
      showMessage("❌ Senha muito longa!", "error");
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      showMessage("❌ Email inválido (exemplo: seu@email.com)", "error");
      return;
    }

    const submitBtn = form.querySelector("button[type='submit']");
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = "Entrando...";
    }

    try {
      const response = await fetch("/auth/login", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
        credentials: "same-origin" // Envia cookies se existirem
      });

      let json;
      try {
        json = await response.json();
      } catch (e) {
        console.error("Erro ao fazer parse do JSON:", e);
        showMessage("❌ Erro de servidor. Tente novamente.", "error");
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = "Entrar";
        }
        return;
      }

      if (json.message) {
        showMessage(json.message, response.ok ? "success" : "error");
      }

      if (response.ok && json.ok) {
        console.log("✓ Login bem-sucedido");
        window.location.href = "/funcionario";
      } else {
        console.warn("Login falhou:", json.error || json.message);
        
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = "Entrar";
        }
      }
    } catch (error) {
      console.error("Erro na requisição:", error);
      
      // Não expõe detalhes do erro para o usuário
      if (error.name === "TypeError") {
        showMessage("❌ Erro de conexão. Verifique sua internet.", "error");
      } else {
        showMessage("❌ Erro ao fazer login. Tente novamente.", "error");
      }

      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = "Entrar";
      }
    }
  });

  function showMessage(message, type = "info") {
    //  Sanitiza o texto para evitar XSS
    const messageDiv = document.createElement("div");
    messageDiv.className = `login-message login-${type}`;
    
    // Usa textContent em vez de innerHTML para segurança
    messageDiv.textContent = message;
    
    messageDiv.style.cssText = `
      padding: 12px 15px;
      margin-bottom: 15px;
      border-radius: 6px;
      font-weight: bold;
      animation: slideIn 0.3s ease;
      ${type === "success" 
        ? "background: #d4edda; color: #155724; border: 1px solid #c3e6cb;" 
        : type === "error"
        ? "background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb;"
        : "background: #e7f3ff; color: #004085; border: 1px solid #b8daff;"
      }
    `;

    const oldMessage = document.querySelector(".login-message");
    if (oldMessage) oldMessage.remove();

    form.parentNode.insertBefore(messageDiv, form);

    setTimeout(() => {
      if (messageDiv.parentNode) {
        messageDiv.remove();
      }
    }, 5000);
  }
});