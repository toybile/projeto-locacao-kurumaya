// Arrays em memória para simular armazenamento (Parte 1)
const clientes = [];
const veiculos = [];

// Referências de elementos
const formCliente = document.getElementById("formCliente");
const tabelaClientes = document.querySelector("#tabelaClientes tbody");

const formVeiculo = document.getElementById("formVeiculo");
const tabelaVeiculos = document.querySelector("#tabelaVeiculos tbody");

const selectClienteLocacao = document.getElementById("clienteLocacao");
const selectVeiculoLocacao = document.getElementById("veiculoLocacao");
const btnCalcular = document.getElementById("btnCalcular");
const resultadoLocacao = document.getElementById("resultadoLocacao");

// --- CLIENTES ---

formCliente.addEventListener("submit", function (event) {
    event.preventDefault();

    const cliente = {
        nome: document.getElementById("nomeCliente").value.trim(),
        cnh: document.getElementById("cnhCliente").value.trim(),
        telefone: document.getElementById("telefoneCliente").value.trim(),
        email: document.getElementById("emailCliente").value.trim()
    };

    if (!cliente.nome || !cliente.cnh || !cliente.telefone) {
        alert("Preencha os campos obrigatórios de cliente.");
        return;
    }

    clientes.push(cliente);
    atualizarTabelaClientes();
    atualizarSelectClientes();

    formCliente.reset();
});

function atualizarTabelaClientes() {
    tabelaClientes.innerHTML = "";

    clientes.forEach((cli) => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${cli.nome}</td>
            <td>${cli.cnh}</td>
            <td>${cli.telefone}</td>
            <td>${cli.email || "-"}</td>
        `;

        tabelaClientes.appendChild(tr);
    });
}

function atualizarSelectClientes() {
    selectClienteLocacao.innerHTML = '<option value="">Selecione</option>';

    clientes.forEach((cli) => {
        const option = document.createElement("option");
        option.value = cli.cnh;
        option.textContent = `${cli.nome} - CNH: ${cli.cnh}`;
        selectClienteLocacao.appendChild(option);
    });
}

// --- VEÍCULOS ---

formVeiculo.addEventListener("submit", function (event) {
    event.preventDefault();

    const veiculo = {
        marca: document.getElementById("marcaVeiculo").value.trim(),
        modelo: document.getElementById("modeloVeiculo").value.trim(),
        ano: document.getElementById("anoVeiculo").value,
        placa: document.getElementById("placaVeiculo").value.trim().toUpperCase(),
        cor: document.getElementById("corVeiculo").value.trim(),
        km: document.getElementById("kmVeiculo").value,
        diaria: parseFloat(document.getElementById("valorDiaria").value),
        status: "disponível" // ou "alugado"
    };

    if (!veiculo.marca || !veiculo.modelo || !veiculo.ano || !veiculo.placa || !veiculo.diaria) {
        alert("Preencha todos os campos obrigatórios do veículo.");
        return;
    }

    // Validação simples de placa (pode ser melhorada na Parte 2)
    if (veiculo.placa.length < 6) {
        alert("Placa inválida (muito curta).");
        return;
    }

    veiculos.push(veiculo);
    atualizarTabelaVeiculos();
    atualizarSelectVeiculos();

    formVeiculo.reset();
});

function atualizarTabelaVeiculos() {
    tabelaVeiculos.innerHTML = "";

    veiculos.forEach((v) => {
        const tr = document.createElement("tr");

        const classeStatus = v.status === "disponível" ? "status-disponivel" : "status-alugado";

        tr.innerHTML = `
            <td>${v.marca}</td>
            <td>${v.modelo}</td>
            <td>${v.ano}</td>
            <td>${v.placa}</td>
            <td>${v.cor || "-"}</td>
            <td>${v.km || "0"}</td>
            <td>${v.diaria.toFixed(2)}</td>
            <td class="${classeStatus}">${v.status}</td>
        `;

        tabelaVeiculos.appendChild(tr);
    });
}

function atualizarSelectVeiculos() {
    selectVeiculoLocacao.innerHTML = '<option value="">Selecione</option>';

    veiculos.forEach((v) => {
        if (v.status === "disponível") {
            const option = document.createElement("option");
            option.value = v.placa;
            option.textContent = `${v.marca} ${v.modelo} - ${v.placa}`;
            selectVeiculoLocacao.appendChild(option);
        }
    });
}

// --- SIMULAÇÃO DE LOCAÇÃO (Parte 1) ---

btnCalcular.addEventListener("click", function () {
    const cnhSelecionada = selectClienteLocacao.value;
    const placaSelecionada = selectVeiculoLocacao.value;
    const diasPrevistos = parseInt(document.getElementById("diasPrevistos").value, 10);
    const valorCaucao = parseFloat(document.getElementById("valorCaucao").value);

    if (!cnhSelecionada || !placaSelecionada || !diasPrevistos || !valorCaucao) {
        alert("Preencha todos os campos da simulação.");
        return;
    }

    const veiculoEscolhido = veiculos.find(v => v.placa === placaSelecionada);

    if (!veiculoEscolhido) {
        alert("Veículo não encontrado.");
        return;
    }

    const valorEstimado = diasPrevistos * veiculoEscolhido.diaria;
    let mensagem = `
        <p><strong>Veículo:</strong> ${veiculoEscolhido.marca} ${veiculoEscolhido.modelo} (${veiculoEscolhido.placa})</p>
        <p><strong>Dias previstos:</strong> ${diasPrevistos}</p>
        <p><strong>Valor da diária:</strong> R$ ${veiculoEscolhido.diaria.toFixed(2)}</p>
        <p><strong>Valor estimado da locação:</strong> R$ ${valorEstimado.toFixed(2)}</p>
        <p><strong>Caução informada:</strong> R$ ${valorCaucao.toFixed(2)}</p>
    `;

    if (valorCaucao < valorEstimado * 0.5) {
        mensagem += `<p style="color:#f97373;">Atenção: caução abaixo de 50% do valor estimado.</p>`;
    } else {
        mensagem += `<p style="color:#6ee7b7;">Caução adequada para a locação.</p>`;
    }

    resultadoLocacao.innerHTML = mensagem;
});
