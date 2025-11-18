document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("#form-signin");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const errorElements = document.querySelectorAll(".error-message");
        errorElements.forEach(el => el.remove());

        const name = document.querySelector("input[name='name']")?.value.trim() || document.querySelector("#fullname")?.value.trim() || "";
        const email = document.querySelector("input[name='email']")?.value.trim() || document.querySelector("#emailsignup")?.value.trim() || "";
        const password = document.querySelector("input[name='password']")?.value || document.querySelector("#passwordsignup")?.value || "";
        const phone = document.querySelector("input[name='phone']")?.value.trim() || document.querySelector("#phonesignup")?.value.trim() || "";
        const cnh = document.querySelector("input[name='cnh']")?.value.trim() || document.querySelector("#cnh")?.value.trim() || "";

        // Array para armazenar erros
        const errors = [];

        // Validação de nome
        if (!name) {
            errors.push("Nome é obrigatório");
        } else if (name.length < 3) {
            errors.push("Nome deve ter no mínimo 3 caracteres");
        }

        // Validação de email
        if (!email) {
            errors.push("Email é obrigatório");
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            errors.push("Email inválido (exemplo: seu@email.com)");
        }

        // Validação de senha
        if (!password) {
            errors.push("Senha é obrigatória");
        } else if (password.length < 6) {
            errors.push("Senha deve ter no mínimo 6 caracteres");
        } else if (!/[a-zA-Z]/.test(password)) {
            errors.push("Senha deve conter pelo menos uma letra");
        } else if (!/\d/.test(password)) {
            errors.push("Senha deve conter pelo menos um número");
        }

        // Validação de telefone
        if (phone && !/^\(\d{2}\)\s?\d{4,5}-?\d{4}$/.test(phone)) {
            errors.push("Telefone inválido. Use o formato: (XX) XXXXX-XXXX ou (XX) XXXX-XXXX");
        }

        // Validação de CNH
        if (cnh) {
            const cnh_only_digits = cnh.replace(/\D/g, "");
            if (cnh_only_digits.length !== 11) {
                errors.push("CNH deve conter exatamente 11 dígitos (somente números)");
            } else if (/^(\d)\1{10}$/.test(cnh_only_digits)) {
                errors.push("CNH inválida (não pode ser uma sequência repetida, ex: 11111111111)");
            }
        }

        if (errors.length > 0) {
            const errorDiv = document.createElement("div");
            errorDiv.className = "error-message";
            errorDiv.style.cssText = `
                background-color: #f8d7da;
                border: 2px solid #f5c6cb;
                color: #721c24;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 20px;
                font-weight: 500;
            `;
            
            const errorList = errors.map(err => `<li style="margin: 5px 0;">• ${err}</li>`).join("");
            errorDiv.innerHTML = `
                <strong style="display: block; margin-bottom: 10px;">⚠️ Erros encontrados:</strong>
                <ul style="margin: 0; padding-left: 0; list-style: none;">
                    ${errorList}
                </ul>
            `;
            
            form.insertBefore(errorDiv, form.firstChild);
            window.scrollTo(0, 0);
            return;
        }

        try {
            const response = await fetch("/auth/cadastro", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, email, password, phone, cnh })
            });

            const data = await response.json();

            if (data.ok) {
                window.location.href = data.redirect;
            } else {
                const errorDiv = document.createElement("div");
                errorDiv.className = "error-message";
                errorDiv.style.cssText = `
                    background-color: #f8d7da;
                    border: 2px solid #f5c6cb;
                    color: #721c24;
                    padding: 15px;
                    border-radius: 6px;
                    margin-bottom: 20px;
                    font-weight: 500;
                `;
                errorDiv.innerHTML = `<strong>❌ Erro:</strong> ${data.error}`;
                form.insertBefore(errorDiv, form.firstChild);
                window.scrollTo(0, 0);
            }
        } catch (err) {
            console.error("Erro ao cadastrar:", err);
            const errorDiv = document.createElement("div");
            errorDiv.className = "error-message";
            errorDiv.style.cssText = `
                background-color: #f8d7da;
                border: 2px solid #f5c6cb;
                color: #721c24;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 20px;
                font-weight: 500;
            `;
            errorDiv.innerHTML = `<strong>❌ Erro:</strong> Erro ao conectar com o servidor`;
            form.insertBefore(errorDiv, form.firstChild);
            window.scrollTo(0, 0);
        }
    });

    // Validação em tempo real
    const phoneInput = document.querySelector("input[name='phone']") || document.querySelector("#phonesignup");
    if (phoneInput) {
        phoneInput.addEventListener("blur", () => {
            const phone = phoneInput.value.trim();
            if (phone && !/^\(\d{2}\)\s?\d{4,5}-?\d{4}$/.test(phone)) {
                phoneInput.style.borderColor = "#dc3545";
                phoneInput.style.backgroundColor = "#fff5f5";
                phoneInput.title = "Formato correto: (XX) XXXXX-XXXX";
            } else if (phone) {
                phoneInput.style.borderColor = "#28a745";
                phoneInput.style.backgroundColor = "#f0fff4";
            } else {
                phoneInput.style.borderColor = "";
                phoneInput.style.backgroundColor = "";
            }
        });
    }

    const cnhInput = document.querySelector("input[name='cnh']") || document.querySelector("#cnh");
    if (cnhInput) {
        cnhInput.addEventListener("blur", () => {
            const cnh = cnhInput.value.trim();
            if (cnh) {
                const cnh_only_digits = cnh.replace(/\D/g, "");
                if (cnh_only_digits.length !== 11) {
                    cnhInput.style.borderColor = "#dc3545";
                    cnhInput.style.backgroundColor = "#fff5f5";
                    cnhInput.title = "CNH deve ter exatamente 11 dígitos";
                } else if (/^(\d)\1{10}$/.test(cnh_only_digits)) {
                    cnhInput.style.borderColor = "#dc3545";
                    cnhInput.style.backgroundColor = "#fff5f5";
                    cnhInput.title = "CNH inválida (sequência repetida)";
                } else {
                    cnhInput.style.borderColor = "#28a745";
                    cnhInput.style.backgroundColor = "#f0fff4";
                }
            } else {
                cnhInput.style.borderColor = "";
                cnhInput.style.backgroundColor = "";
            }
        });

        cnhInput.addEventListener("input", () => {
            const cnh = cnhInput.value.replace(/\D/g, "");
            if (cnh.length > 0) {
                cnhInput.title = `${cnh.length}/11 dígitos`;
            }
        });
    }

    const emailInput = document.querySelector("input[name='email']") || document.querySelector("#emailsignup");
    if (emailInput) {
        emailInput.addEventListener("blur", () => {
            const email = emailInput.value.trim();
            if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                emailInput.style.borderColor = "#dc3545";
                emailInput.style.backgroundColor = "#fff5f5";
            } else if (email) {
                emailInput.style.borderColor = "#28a745";
                emailInput.style.backgroundColor = "#f0fff4";
            } else {
                emailInput.style.borderColor = "";
                emailInput.style.backgroundColor = "";
            }
        });
    }
});