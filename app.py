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

@app.route("/clientes")
@staff_required
def clientes_admin():
    return render_template("funcionario/clientes.html")

@app.route("/devolucao")
@client_required
def devolucao_cliente_page():
    return render_template("devolucao_cliente.html")



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
    phone = data.get("phone", "")  # Aceita telefone opcional

    if not name or not email or not password:
        return jsonify({"ok": False, "error": "Todos os campos são obrigatórios"})

    if email in USERS:
        return jsonify({"ok": False, "error": "Email já cadastrado"})

    USERS[email] = {
        "name": name,
        "password": password,
        "type": "client",
        "phone": phone
    }
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
    
    # Filtra aluguéis do cliente logado
    user_rentals = [r for r in RENTALS if r["client_email"] == email]
    
    # Junta informações do veículo
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

    daily_price = vehicle["price"]
    total = daily_price * days
    vehicle["status"] = "rented"

    # caução (ex.: 50% do valor previsto)
    deposit = total * 0.5

    RENTALS.append({
        "rental_id": next_rental_id,
        "vehicle_id": vid,
        "client_email": session["user"]["email"],
        "days": days,
        "daily_price": daily_price,
        "total": total,
        "deposit": deposit,
        "start_datetime": datetime.now().isoformat(),
        "start_km": data.get("start_km", 0),
        "status": "ongoing",
        # campos de devolução, preenchidos depois
        "end_datetime": None,
        "end_km": None,
        "final_total": total,
        "refund": 0
    })

    next_rental_id += 1

    return jsonify(ok=True, total=total, deposit=deposit)


@app.route("/api/clients", methods=["GET"])
@staff_required
def api_clients():
    # Filtra apenas usuários do tipo "client" de USERS
    clients_list = []
    for email, user_data in USERS.items():
        if user_data.get("type") == "client":
            clients_list.append({
                "email": email,
                "name": user_data.get("name"),
                "phone": user_data.get("phone", "Não informado")
            })
    return jsonify(clients_list)

@app.route("/api/rent/return/preview", methods=["POST"])
@client_required
def preview_return():
    from datetime import datetime

    data = request.json
    rental_id = data.get("rental_id")
    end_km = data.get("end_km")
    damage_value = float(data.get("damage_value", 0) or 0)

    if rental_id is None or end_km is None:
        return jsonify(ok=False, error="ID do aluguel e km final são obrigatórios"), 400

    KM_LIMIT_PER_RENTAL = 300
    EXTRA_KM_PRICE = 1.5

    rental = next((r for r in RENTALS if r["rental_id"] == rental_id), None)
    if not rental:
        return jsonify(ok=False, error="Aluguel não encontrado"), 404

    user = session.get("user")
    if not user or user["email"] != rental["client_email"]:
        return jsonify(ok=False, error="Você não tem permissão para este aluguel"), 403

    if rental.get("status") == "finished":
        return jsonify(ok=False, error="Este aluguel já foi finalizado"), 400

    start_datetime = datetime.fromisoformat(rental["start_datetime"])
    end_datetime = datetime.now()
    days_used = (end_datetime - start_datetime).days
    if days_used < 1:
        days_used = 1

    extra_days = max(0, days_used - rental["days"])
    extra_days_fee = extra_days * rental["daily_price"]

    start_km = float(rental.get("start_km", 0))
    end_km = float(end_km)
    total_km = max(0, end_km - start_km)
    extra_km = max(0, total_km - KM_LIMIT_PER_RENTAL)
    extra_km_fee = extra_km * EXTRA_KM_PRICE

    damage_fee = damage_value

    base_total = rental["total"]
    additional_costs = extra_days_fee + extra_km_fee + damage_fee
    final_total = base_total + additional_costs

    deposit = rental.get("deposit", 0)
    refund = max(0, deposit - additional_costs)

    return jsonify({
        "ok": True,
        "summary": {
            "rental_id": rental_id,
            "days_contracted": rental["days"],
            "days_used": days_used,
            "extra_days": extra_days,
            "extra_days_fee": extra_days_fee,
            "total_km": total_km,
            "extra_km": extra_km,
            "extra_km_fee": extra_km_fee,
            "damage_fee": damage_fee,
            "base_total": base_total,
            "final_total": final_total,
            "deposit": deposit,
            "refund": refund,
            "end_km": end_km
        }
    })


@app.route("/api/rent/return/confirm", methods=["POST"])
@client_required
def confirm_return():
    from datetime import datetime

    data = request.json
    rental_id = data.get("rental_id")
    end_km = data.get("end_km")
    damage_value = float(data.get("damage_value", 0) or 0)

    if rental_id is None or end_km is None:
        return jsonify(ok=False, error="Dados incompletos"), 400

    KM_LIMIT_PER_RENTAL = 300
    EXTRA_KM_PRICE = 1.5

    rental = next((r for r in RENTALS if r["rental_id"] == rental_id), None)
    if not rental:
        return jsonify(ok=False, error="Aluguel não encontrado"), 404

    user = session.get("user")
    if not user or user["email"] != rental["client_email"]:
        return jsonify(ok=False, error="Você não tem permissão para este aluguel"), 403

    if rental.get("status") == "finished":
        return jsonify(ok=False, error="Este aluguel já foi finalizado"), 400

    vehicle = next((v for v in VEHICLES if v["id"] == rental["vehicle_id"]), None)
    if not vehicle:
        return jsonify(ok=False, error="Veículo não encontrado"), 404

    start_datetime = datetime.fromisoformat(rental["start_datetime"])
    end_datetime = datetime.now()
    days_used = (end_datetime - start_datetime).days
    if days_used < 1:
        days_used = 1

    extra_days = max(0, days_used - rental["days"])
    extra_days_fee = extra_days * rental["daily_price"]

    start_km = float(rental.get("start_km", 0))
    end_km = float(end_km)
    total_km = max(0, end_km - start_km)
    extra_km = max(0, total_km - KM_LIMIT_PER_RENTAL)
    extra_km_fee = extra_km * EXTRA_KM_PRICE

    damage_fee = damage_value

    base_total = rental["total"]
    additional_costs = extra_days_fee + extra_km_fee + damage_fee
    final_total = base_total + additional_costs

    deposit = rental.get("deposit", 0)
    refund = max(0, deposit - additional_costs)

    rental.update({
        "end_datetime": end_datetime.isoformat(),
        "end_km": end_km,
        "extra_days": extra_days,
        "extra_km_fee": extra_km_fee,
        "damage_fee": damage_fee,
        "final_total": final_total,
        "refund": refund,
        "status": "finished"
    })

    vehicle["status"] = "available"

    return jsonify({
        "ok": True,
        "message": "Aluguel finalizado com sucesso.",
        "summary": {
            "days_contracted": rental["days"],
            "days_used": days_used,
            "extra_days": extra_days,
            "extra_days_fee": extra_days_fee,
            "total_km": total_km,
            "extra_km": extra_km,
            "extra_km_fee": extra_km_fee,
            "damage_fee": damage_fee,
            "base_total": base_total,
            "final_total": final_total,
            "deposit": deposit,
            "refund": refund
        }
    })



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
            "category": "sedan",
            "price": 150,
            "image": "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=800&q=80",
            "status": "available"
        },
        {
            "id": 2,
            "plate": "XYZ-5678",
            "model": "Civic",
            "brand": "Honda",
            "year": 2023,
            "category": "sedan",
            "price": 180,
            "image": "https://images.unsplash.com/photo-1606611013016-969c19d14311?w=800&q=80",
            "status": "available"
        },
        {
            "id": 3,
            "plate": "DEF-9012",
            "model": "HR-V",
            "brand": "Honda",
            "year": 2021,
            "category": "suv",
            "price": 200,
            "image": "https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=800&q=80",
            "status": "available"
        },
        {
            "id": 4,
            "plate": "GHI-3456",
            "model": "Onix",
            "brand": "Chevrolet",
            "year": 2023,
            "category": "hatch",
            "price": 120,
            "image": "https://images.unsplash.com/photo-1489824904134-891ab64532f1?w=800&q=80",
            "status": "rented"
        },
        {
            "id": 5,
            "plate": "JKL-7890",
            "model": "Compass",
            "brand": "Jeep",
            "year": 2022,
            "category": "suv",
            "price": 250,
            "image": "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=800&q=80",
            "status": "available"
        },
        {
            "id": 6,
            "plate": "MNO-1122",
            "model": "Gol",
            "brand": "Volkswagen",
            "year": 2020,
            "category": "hatch",
            "price": 100,
            "image": "https://images.unsplash.com/photo-1590362891990-f8ddb41d006d?w=800&q=80",
            "status": "available"
        },
        {
            "id": 7,
            "plate": "PQR-3344",
            "model": "Nivus",
            "brand": "Volkswagen",
            "year": 2022,
            "category": "suv",
            "price": 190,
            "image": "https://images.unsplash.com/photo-1581540222194-0def2dda95b8?w=800&q=80",
            "status": "available"
        },
        {
            "id": 8,
            "plate": "STU-5566",
            "model": "Tracker",
            "brand": "Chevrolet",
            "year": 2021,
            "category": "suv",
            "price": 210,
            "image": "https://images.unsplash.com/photo-1606611013016-969c19d14311?w=800&q=80",
            "status": "reserved"
        },
        {
            "id": 9,
            "plate": "VWX-7788",
            "model": "Argo",
            "brand": "Fiat",
            "year": 2022,
            "category": "hatch",
            "price": 115,
            "image": "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=800&q=80",
            "status": "available"
        },
        {
            "id": 10,
            "plate": "YZA-9900",
            "model": "Cronos",
            "brand": "Fiat",
            "year": 2021,
            "category": "sedan",
            "price": 130,
            "image": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800&q=80",
            "status": "available"
        },
        {
            "id": 11,
            "plate": "BCA-2233",
            "model": "Kicks",
            "brand": "Nissan",
            "year": 2023,
            "category": "suv",
            "price": 220,
            "image": "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=800&q=80",
            "status": "available"
        },
        {
            "id": 12,
            "plate": "DEF-4455",
            "model": "Corolla Cross",
            "brand": "Toyota",
            "year": 2023,
            "category": "suv",
            "price": 260,
            "image": "https://images.unsplash.com/photo-1606664515524-2134e2f37a85?w=800&q=80",
            "status": "available"
        },
        {
            "id": 13,
            "plate": "GHI-6677",
            "model": "HB20",
            "brand": "Hyundai",
            "year": 2021,
            "category": "hatch",
            "price": 110,
            "image": "https://images.unsplash.com/photo-1485463611174-f302f6a5c1c9?w=800&q=80",
            "status": "available"
        },
        {
            "id": 14,
            "plate": "JKL-8899",
            "model": "Creta",
            "brand": "Hyundai",
            "year": 2022,
            "category": "suv",
            "price": 230,
            "image": "https://images.unsplash.com/photo-1551830820-330a71b99659?w=800&q=80",
            "status": "rented"
        },
        {
            "id": 15,
            "plate": "MNO-1357",
            "model": "Renegade",
            "brand": "Jeep",
            "year": 2021,
            "category": "suv",
            "price": 240,
            "image": "https://images.unsplash.com/photo-1606611013016-969c19d14311?w=800&q=80",
            "status": "available"
        },
        {
            "id": 16,
            "plate": "PQR-2468",
            "model": "Sandero",
            "brand": "Renault",
            "year": 2020,
            "category": "hatch",
            "price": 95,
            "image": "https://images.unsplash.com/photo-1520031441872-265e4ff70366?w=800&q=80",
            "status": "available"
        },
        {
            "id": 17,
            "plate": "STU-3691",
            "model": "Logan",
            "brand": "Renault",
            "year": 2021,
            "category": "sedan",
            "price": 115,
            "image": "https://images.unsplash.com/photo-1502877338535-766e1452684a?w=800&q=80",
            "status": "maintenance"
        },
        {
            "id": 18,
            "plate": "VWX-4826",
            "model": "Yaris",
            "brand": "Toyota",
            "year": 2022,
            "category": "hatch",
            "price": 140,
            "image": "https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=800&q=80",
            "status": "available"
        },
        {
            "id": 19,
            "plate": "YZA-5937",
            "model": "City",
            "brand": "Honda",
            "year": 2022,
            "category": "sedan",
            "price": 170,
            "image": "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=800&q=80",
            "status": "available"
        },
        {
            "id": 20,
            "plate": "BCA-6048",
            "model": "T-Cross",
            "brand": "Volkswagen",
            "year": 2023,
            "category": "suv",
            "price": 245,
            "image": "https://images.unsplash.com/photo-1506521781263-d8422e82f27a?w=800&q=80",
            "status": "available"
        },
        {
            "id": 21,
            "plate": "DEF-7159",
            "model": "Captur",
            "brand": "Renault",
            "year": 2021,
            "category": "suv",
            "price": 205,
            "image": "https://images.unsplash.com/photo-1514316454349-750a7fd3da3a?w=800&q=80",
            "status": "available"
        }
    ]
    
    next_vehicle_id = 22


@app.route("/api/auth/status", methods=["GET"])
def auth_status():
    """Retorna o status de login do usuário"""
    user = session.get("user")
    if user:
        return jsonify({
            "logged_in": True,
            "name": user["name"],
            "type": user["type"]
        })
    return jsonify({"logged_in": False})




if __name__ == "__main__":
    app.run(debug=True)
