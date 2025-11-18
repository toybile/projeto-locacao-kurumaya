// =====================================
//   LOGIN DE FUNCIONÁRIO (STAFF) — SEGURO
// =====================================

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form-login-funcionario");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // ✅ Limpa mensagens anteriores
    const oldMessage = document.querySelector(".login-message");
    if (oldMessage) oldMessage.remove();

    // ✅ Pega valores com validação
    const emailInput = document.getElementById("email_func");
    const passwordInput = document.getElementById("password_func");

    if (!emailInput || !passwordInput) {
      showMessage("❌ Erro: Campos de login não encontrados", "error");
      return;
    }

    const email = emailInput.value.trim();
    const password = passwordInput.value;

    // ✅ Validações no CLIENTE
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

    // ✅ Desabilita botão durante requisição
    const submitBtn = form.querySelector("button[type='submit']");
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = "Entrando...";
    }

    try {
      // ✅ Envio seguro para o servidor
      const response = await fetch("/auth/login", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          // CSRF token se tiver implementado (opcional)
          // "X-CSRF-Token": getCsrfToken()
        },
        body: JSON.stringify({ email, password }),
        credentials: "same-origin" // Envia cookies se existirem
      });

      // ✅ Verifica se a resposta é JSON válida
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

      // ✅ Valida se json.message existe
      if (json.message) {
        showMessage(json.message, response.ok ? "success" : "error");
      }

      // ✅ Se login bem-sucedido, redireciona
      if (response.ok && json.ok) {
        console.log("✓ Login bem-sucedido");
        // Redireciona sem delay para não roubar credenciais
        window.location.href = "/funcionario";
      } else {
        // ✅ Mostra mensagem de erro
        console.warn("Login falhou:", json.error || json.message);
        
        // Re-habilita botão para tentar novamente
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = "Entrar";
        }
      }
    } catch (error) {
      console.error("Erro na requisição:", error);
      
      // ✅ Não expõe detalhes do erro para o usuário
      if (error.name === "TypeError") {
        showMessage("❌ Erro de conexão. Verifique sua internet.", "error");
      } else {
        showMessage("❌ Erro ao fazer login. Tente novamente.", "error");
      }

      // Re-habilita botão
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = "Entrar";
      }
    }
  });

  /**
   * Mostra mensagem de forma segura
   */
  function showMessage(message, type = "info") {
    // ✅ Sanitiza o texto para evitar XSS
    const messageDiv = document.createElement("div");
    messageDiv.className = `login-message login-${type}`;
    
    // ✅ Usa textContent em vez de innerHTML para segurança
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

    // Remove mensagem anterior se existir
    const oldMessage = document.querySelector(".login-message");
    if (oldMessage) oldMessage.remove();

    // Insere nova mensagem no formulário
    form.parentNode.insertBefore(messageDiv, form);

    // ✅ Remove automaticamente após 5 segundos
    setTimeout(() => {
      if (messageDiv.parentNode) {
        messageDiv.remove();
      }
    }, 5000);
  }
});