from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = "troque_essa_chave_para_algo_secreto"

# =====================================
#   BANCO DE DADOS EM MEMÓRIA
# =====================================

CLIENTS = []
USERS = {
    # Funcionários
    "admin@example.com": {"password": "123456", "name": "Admin", "type": "staff"},
    "guilherme.bilibio@gmail.com": {"password": "toybife", "name": "Guilherme", "type": "staff"},
    "henrique.daisuke@gmail.com": {"password": "123456", "name": "Henrique", "type": "staff"},
}

VEHICLES = []
RENTALS = []  # histórico de aluguéis

next_client_id = 1
next_vehicle_id = 1
next_rental_id = 1

seeded = False

# =====================================
#   HELPERS
# =====================================

def client_required(f):
    @wraps(f)
    def w(*a, **kw):
        user = session.get("user")
        if not user or user["type"] != "client":
            return redirect(url_for("login"))
        return f(*a, **kw)
    return w

def staff_required(f):
    @wraps(f)
    def w(*a, **kw):
        user = session.get("user")
        if not user or user["type"] != "staff":
            return redirect(url_for("login_funcionario"))
        return f(*a, **kw)
    return w

# =====================================
#   PÁGINAS
# =====================================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/funcionario/login")
def login_funcionario():
    return render_template("funcionario/login.html")

@app.route("/cadastro")
def cadastro():
    return render_template("signin.html")

@app.route("/frota")
@client_required
def frota():
    return render_template("frota.html")

@app.route("/funcionario")
@staff_required
def funcionario_index():
    return render_template("funcionario/menufuncionario.html")

@app.route("/veiculos")
@staff_required
def veiculos_admin():
    return render_template("funcionario/veiculos.html")

@app.route("/veiculo/<int:vid>")
@client_required
def veiculo_detalhes(vid):
    vehicle = next((v for v in VEHICLES if v["id"] == vid), None)

    if not vehicle:
        return "Veículo não encontrado", 404

    return render_template("veiculo.html", vehicle=vehicle)

@app.route("/pagamento/<int:vid>")
@client_required
def pagamento(vid):
    vehicle = next((v for v in VEHICLES if v["id"] == vid), None)
    if not vehicle:
        return "Veículo não encontrado", 404

    if vehicle["status"] not in ["available", "reserved"]:
        return "Este veículo não pode ser alugado agora.", 400

    return render_template("pagamento.html", vehicle=vehicle)

@app.route("/historico")
@client_required
def historico():
    return render_template("historico.html")
    



# =====================================
#   AUTENTICAÇÃO
# =====================================

@app.route("/auth/login", methods=["POST"])
def auth_login():
    data = request.form or request.json
    email = data.get("email")
    password = data.get("password")

    user = USERS.get(email)
    if not user or user["password"] != password:
        return jsonify({"ok": False, "error": "Credenciais inválidas"})

    session["user"] = {"email": email, "name": user["name"], "type": user["type"]}

    if user["type"] == "staff":
        return jsonify({"ok": True, "redirect": "/funcionario"})
    return jsonify({"ok": True, "redirect": "/frota"})


@app.route("/auth/cadastro", methods=["POST"])
def auth_cadastro():
    global USERS

    data = request.form or request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"ok": False, "error": "Todos os campos são obrigatórios"})

    if email in USERS:
        return jsonify({"ok": False, "error": "Email já cadastrado"})

    USERS[email] = {"name": name, "password": password, "type": "client"}

    session["user"] = {"email": email, "name": name, "type": "client"}

    return jsonify({"ok": True, "redirect": "/frota"})


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# =====================================
#   API — VEÍCULOS
# =====================================

@app.route('/api/vehicles', methods=['GET', 'POST', 'PUT'])
def api_vehicles():
    global VEHICLES, next_vehicle_id

    if request.method == 'GET':
        return jsonify(VEHICLES)

    if request.method == 'POST':
        data = request.json
        plate = data.get('plate')
        model = data.get('model')
        year = data.get('year')

        if not plate or not model or not year:
            return jsonify({'ok': False, 'error': 'Campos obrigatórios faltando'}), 400

        obj = {
            'id': next_vehicle_id,
            'plate': plate,
            'model': model,
            'year': year,
            'status': 'available'
        }
        next_vehicle_id += 1
        VEHICLES.append(obj)

        return jsonify({'ok': True, 'vehicle': obj})

    if request.method == 'PUT':
        data = request.json
        vid = data.get('id')
        status = data.get('status')

        if vid is None or status is None:
            return jsonify({'ok': False, 'error': 'Dados incompletos'}), 400

        for v in VEHICLES:
            if v['id'] == vid:
                v['status'] = status
                return jsonify({'ok': True, 'vehicle': v})

        return jsonify({'ok': False, 'error': 'Veículo não encontrado'}), 404



@app.route("/api/vehicles/<int:vid>", methods=["DELETE"])
@staff_required
def delete_vehicle(vid):
    global VEHICLES
    exists = any(v["id"] == vid for v in VEHICLES)

    if not exists:
        return jsonify({"error": "Veículo não encontrado"}), 404

    VEHICLES = [v for v in VEHICLES if v["id"] != vid]
    return jsonify({"message": "Veículo removido"})

@app.route("/api/rentals/history", methods=["GET"])
@client_required
def rentals_history():
    user = session.get("user")
    email = user["email"]

    user_rentals = [r for r in RENTALS if r["client_email"] == email]

    result = []
    for r in user_rentals:
        vehicle = next((v for v in VEHICLES if v["id"] == r["vehicle_id"]), None)
        if vehicle:
            result.append({
                "rental_id": r["rental_id"],
                "vehicle_id": r["vehicle_id"],
                "model": vehicle["model"],
                "plate": vehicle["plate"],
                "year": vehicle["year"],
                "price_per_day": vehicle["price"],
                "days": r["days"],
                "total": r["total"]
            })

    return jsonify(result)


# =====================================
#   🟢 API — INICIAR ALUGUEL (RESERVA)
# =====================================

@app.route("/api/rent/reserve", methods=["POST"])
@client_required
def reserve_vehicle():
    data = request.json
    vid = data.get("id")

    vehicle = next((v for v in VEHICLES if v["id"] == vid), None)
    if not vehicle:
        return jsonify({"error": "Veículo não existe"}), 404
    
    if vehicle["status"] != "available":
        return jsonify({"error": "Veículo não está disponível"}), 400

    vehicle["status"] = "reserved"
    return jsonify({"ok": True, "redirect": f"/pagamento/{vid}"})


# =====================================
#   🟢 API — PAGAMENTO FICTÍCIO
# =====================================

@app.route("/api/rent/pay", methods=["POST"])
@client_required
def pay_vehicle():
    global nextrentalid
    data = request.json
    vid = data.get("id")
    days = int(data.get("days"))

    vehicle = next((v for v in VEHICLES if v["id"] == vid), None)
    if not vehicle:
        return jsonify(ok=False, error="Veículo não encontrado")

    if vehicle["status"] not in ["available", "reserved"]:
        return jsonify(ok=False, error="Veículo não está disponível")

    total = vehicle["price"] * days
    vehicle["status"] = "rented"

    RENTALS.append({
        "rentalid": nextrentalid,
        "vehicleid": vid,
        "clientemail": session["user"]["email"],
        "days": days,
        "total": total,
        "date": datetime.now().isoformat()
    })
    nextrentalid += 1

    return jsonify(ok=True, total=total)




# =====================================
#   SEED
# =====================================

@app.before_request
def seed_data():
    global seeded, VEHICLES, next_vehicle_id

    if seeded:
        return
    seeded = True

    VEHICLES = [
        {"id": 1, "plate": "ABC-1234", "model": "Corolla", "year": 2018, "price": 150, "status": "available"},
        {"id": 2, "plate": "XYZ-5678", "model": "Civic",   "year": 2020, "price": 180, "status": "available"}
    ]
    next_vehicle_id = 3


if __name__ == "__main__":
    app.run(debug=True)
