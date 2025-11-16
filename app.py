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
RENTALS = []

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
        brand = data.get('brand')
        year = data.get('year')
        category = data.get('category')
        price = data.get('price')
        image = data.get('image')

        if not all([plate, model, brand, year, category, price]):
            return jsonify({'ok': False, 'error': 'Campos obrigatórios faltando'}), 400

        obj = {
            'id': next_vehicle_id,
            'plate': plate,
            'model': model,
            'brand': brand,
            'year': year,
            'category': category,
            'price': price,
            'image': image or '/static/img/default-car.jpg',
            'status': 'available'
        }
        next_vehicle_id += 1
        VEHICLES.append(obj)

        return jsonify({'ok': True, 'vehicle': obj})

    if request.method == 'PUT':
        data = request.json
        vid = data.get('id')
        
        if vid is None:
            return jsonify({'ok': False, 'error': 'ID obrigatório'}), 400

        for v in VEHICLES:
            if v['id'] == vid:
                if 'status' in data:
                    v['status'] = data['status']
                if 'price' in data:
                    v['price'] = data['price']
                if 'image' in data:
                    v['image'] = data['image']
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
                "brand": vehicle["brand"],
                "plate": vehicle["plate"],
                "year": vehicle["year"],
                "price_per_day": vehicle["price"],
                "days": r["days"],
                "total": r["total"]
            })

    return jsonify(result)

# =====================================
#   API — INICIAR ALUGUEL (RESERVA)
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
#   API — PAGAMENTO FICTÍCIO
# =====================================

@app.route("/api/rent/pay", methods=["POST"])
@client_required
def pay_vehicle():
    global next_rental_id
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
        "rental_id": next_rental_id,
        "vehicle_id": vid,
        "client_email": session["user"]["email"],
        "days": days,
        "total": total,
        "date": datetime.now().isoformat()
    })
    next_rental_id += 1

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
        {
            "id": 1,
            "plate": "ABC-1234",
            "model": "Corolla",
            "brand": "Toyota",
            "year": 2022,
            "category": "Sedan",
            "price": 150,
            "image": "https://www.webmotors.com.br/imagens/prod/348395/VOLKSWAGEN_NIVUS_1.0_200_TSI_TOTAL_FLEX_HIGHLINE_AUTOMATICO_34839515100377384.webp",
            "status": "available"
        },
        {
            "id": 2,
            "plate": "XYZ-5678",
            "model": "Civic",
            "brand": "Honda",
            "year": 2023,
            "category": "Sedan",
            "price": 180,
            "image": "https://www.webmotors.com.br/imagens/prod/348395/VOLKSWAGEN_NIVUS_1.0_200_TSI_TOTAL_FLEX_HIGHLINE_AUTOMATICO_34839515100377384.webp",
            "status": "available"
        },
        {
            "id": 3,
            "plate": "DEF-9012",
            "model": "HR-V",
            "brand": "Honda",
            "year": 2021,
            "category": "SUV",
            "price": 200,
            "image": "https://www.webmotors.com.br/imagens/prod/348395/VOLKSWAGEN_NIVUS_1.0_200_TSI_TOTAL_FLEX_HIGHLINE_AUTOMATICO_34839515100377384.webp",
            "status": "available"
        },
        {
            "id": 4,
            "plate": "GHI-3456",
            "model": "Onix",
            "brand": "Chevrolet",
            "year": 2023,
            "category": "Hatch",
            "price": 120,
            "image": "https://www.webmotors.com.br/imagens/prod/348395/VOLKSWAGEN_NIVUS_1.0_200_TSI_TOTAL_FLEX_HIGHLINE_AUTOMATICO_34839515100377384.webp",
            "status": "rented"
        },
        {
            "id": 5,
            "plate": "JKL-7890",
            "model": "Compass",
            "brand": "Jeep",
            "year": 2022,
            "category": "SUV",
            "price": 250,
            "image": "https://www.webmotors.com.br/imagens/prod/348395/VOLKSWAGEN_NIVUS_1.0_200_TSI_TOTAL_FLEX_HIGHLINE_AUTOMATICO_34839515100377384.webp",
            "status": "available"
        },
        {
            "id": 6,
            "plate": "MNO-1122",
            "model": "Gol",
            "brand": "Volkswagen",
            "year": 2020,
            "category": "Hatch",
            "price": 100,
            "image": "https://www.webmotors.com.br/imagens/prod/348395/VOLKSWAGEN_NIVUS_1.0_200_TSI_TOTAL_FLEX_HIGHLINE_AUTOMATICO_34839515100377384.webp",
            "status": "available"
        },
        {
            "id": 7,
            "plate": "PQR-3344",
            "model": "Nivus",
            "brand": "Volkswagen",
            "year": 2022,
            "category": "SUV",
            "price": 190,
            "image": "https://www.webmotors.com.br/imagens/prod/348395/VOLKSWAGEN_NIVUS_1.0_200_TSI_TOTAL_FLEX_HIGHLINE_AUTOMATICO_34839515100377384.webp",
            "status": "available"
        },
        {
            "id": 8,
            "plate": "STU-5566",
            "model": "Tracker",
            "brand": "Chevrolet",
            "year": 2021,
            "category": "SUV",
            "price": 210,
            "image": "https://www.webmotors.com.br/imagens/prod/348395/VOLKSWAGEN_NIVUS_1.0_200_TSI_TOTAL_FLEX_HIGHLINE_AUTOMATICO_34839515100377384.webp",
            "status": "reserved"
        },
        {
            "id": 9,
            "plate": "VWX-7788",
            "model": "Argo",
            "brand": "Fiat",
            "year": 2022,
            "category": "Hatch",
            "price": 115,
            "image": "https://www.webmotors.com.br/imagens/prod/348395/VOLKSWAGEN_NIVUS_1.0_200_TSI_TOTAL_FLEX_HIGHLINE_AUTOMATICO_34839515100377384.webp",
            "status": "available"
        },
        {
            "id": 10,
            "plate": "YZA-9900",
            "model": "Cronos",
            "brand": "Fiat",
            "year": 2021,
            "category": "Sedan",
            "price": 130,
            "image": "https://www.webmotors.com.br/imagens/prod/348395/VOLKSWAGEN_NIVUS_1.0_200_TSI_TOTAL_FLEX_HIGHLINE_AUTOMATICO_34839515100377384.webp",
            "status": "available"
        },
        {
            "id": 11,
            "plate": "BCA-2233",
            "model": "Kicks",
            "brand": "Nissan",
            "year": 2023,
            "category": "SUV",
            "price": 220,
            "image": "https://www.webmotors.com.br/imagens/prod/348395/VOLKSWAGEN_NIVUS_1.0_200_TSI_TOTAL_FLEX_HIGHLINE_AUTOMATICO_34839515100377384.webp",
            "status": "available"
        },
        {
            "id": 12,
            "plate": "DEF-4455",
            "model": "Corolla Cross",
            "brand": "Toyota",
            "year": 2023,
            "category": "SUV",
            "price": 260,
            "image": "https://www.webmotors.com.br/imagens/prod/348395/VOLKSWAGEN_NIVUS_1.0_200_TSI_TOTAL_FLEX_HIGHLINE_AUTOMATICO_34839515100377384.webp",
            "status": "available"
        },
        {
            "id": 13,
            "plate": "GHI-6677",
            "model": "HB20",
            "brand": "Hyundai",
            "year": 2021,
            "category": "Hatch",
            "price": 110,
            "image": "https://www.webmotors.com.br/imagens/prod/348395/VOLKSWAGEN_NIVUS_1.0_200_TSI_TOTAL_FLEX_HIGHLINE_AUTOMATICO_34839515100377384.webp",
            "status": "available"
        },
        {
            "id": 14,
            "plate": "JKL-8899",
            "model": "Creta",
            "brand": "Hyundai",
            "year": 2022,
            "category": "SUV",
            "price": 230,
            "image": "https://www.webmotors.com.br/imagens/prod/348395/VOLKSWAGEN_NIVUS_1.0_200_TSI_TOTAL_FLEX_HIGHLINE_AUTOMATICO_34839515100377384.webp",
            "status": "rented"
        },
        {
            "id": 15,
            "plate": "MNO-1357",
            "model": "Renegade",
            "brand": "Jeep",
            "year": 2021,
            "category": "SUV",
            "price": 240,
            "image": "https://www.webmotors.com.br/imagens/prod/348395/VOLKSWAGEN_NIVUS_1.0_200_TSI_TOTAL_FLEX_HIGHLINE_AUTOMATICO_34839515100377384.webp",
            "status": "available"
        },
        {
            "id": 16,
            "plate": "PQR-2468",
            "model": "Sandero",
            "brand": "Renault",
            "year": 2020,
            "category": "Hatch",
            "price": 95,
            "image": "https://www.webmotors.com.br/imagens/prod/348395/VOLKSWAGEN_NIVUS_1.0_200_TSI_TOTAL_FLEX_HIGHLINE_AUTOMATICO_34839515100377384.webp",
            "status": "available"
        },
        {
            "id": 17,
            "plate": "STU-3691",
            "model": "Logan",
            "brand": "Renault",
            "year": 2021,
            "category": "Sedan",
            "price": 115,
            "image": "https://www.webmotors.com.br/imagens/prod/348395/VOLKSWAGEN_NIVUS_1.0_200_TSI_TOTAL_FLEX_HIGHLINE_AUTOMATICO_34839515100377384.webp",
            "status": "maintenance"
        },
        {
            "id": 18,
            "plate": "VWX-4826",
            "model": "Yaris",
            "brand": "Toyota",
            "year": 2022,
            "category": "Hatch",
            "price": 140,
            "image": "https://www.webmotors.com.br/imagens/prod/348395/VOLKSWAGEN_NIVUS_1.0_200_TSI_TOTAL_FLEX_HIGHLINE_AUTOMATICO_34839515100377384.webp",
            "status": "available"
        },
        {
            "id": 19,
            "plate": "YZA-5937",
            "model": "City",
            "brand": "Honda",
            "year": 2022,
            "category": "Sedan",
            "price": 170,
            "image": "https://www.webmotors.com.br/imagens/prod/348395/VOLKSWAGEN_NIVUS_1.0_200_TSI_TOTAL_FLEX_HIGHLINE_AUTOMATICO_34839515100377384.webp",
            "status": "available"
        },
        {
            "id": 20,
            "plate": "BCA-6048",
            "model": "T-Cross",
            "brand": "Volkswagen",
            "year": 2023,
            "category": "SUV",
            "price": 245,
            "image": "https://www.webmotors.com.br/imagens/prod/348395/VOLKSWAGEN_NIVUS_1.0_200_TSI_TOTAL_FLEX_HIGHLINE_AUTOMATICO_34839515100377384.webp",
            "status": "available"
        },
        {
            "id": 21,
            "plate": "DEF-7159",
            "model": "Captur",
            "brand": "Renault",
            "year": 2021,
            "category": "SUV",
            "price": 205,
            "image": "https://www.webmotors.com.br/imagens/prod/348395/VOLKSWAGEN_NIVUS_1.0_200_TSI_TOTAL_FLEX_HIGHLINE_AUTOMATICO_34839515100377384.webp",
            "status": "available"
        },
    ]
    next_vehicle_id = 22

if __name__ == "__main__":
    app.run(debug=True)
