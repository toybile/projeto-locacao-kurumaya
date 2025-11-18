from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
from functools import wraps
from utils.security import (
    hash_password, check_password, validate_email_address,
    validate_phone, validate_password_strength, sanitize_input,
    validate_text_input, validate_number, validate_cnh
)

# =====================================
#   CONFIGURAÇÃO DO FLASK
# =====================================

app = Flask(__name__)
app.secret_key = "TROQUE_PARA_UMA_CHAVE_SECRETA_FORTE_E_ALEATÓRIA_AQUI"

# Configuração de Sessions
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False  # Mudar para True em produção (HTTPS)
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = 86400  # 24 horas

# Rate limiting (proteção contra brute force)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# =====================================
#   BANCO DE DADOS EM MEMÓRIA
# =====================================

CLIENTS = []

USERS = {
    # Funcionários (senhas hasheadas com werkzeug)
    "guilherme.bilibio@gmail.com": {
        "password": hash_password("toybife"),
        "name": "Guilherme",
        "type": "staff"
    },
    "henrique.daisuke@gmail.com": {
        "password": hash_password("AkiyamaDAI@0201"),
        "name": "Henrique",
        "type": "staff"
    },
}

VEHICLES = []
RENTALS = []
CONTACT_MESSAGES = []

next_client_id = 1
next_vehicle_id = 1
next_rental_id = 1
next_message_id = 1
seeded = False

# =====================================
#   DECORATORS (AUTENTICAÇÃO)
# =====================================

def client_required(f):
    """Garante que apenas clientes logados podem acessar"""
    @wraps(f)
    def w(*a, **kw):
        user = session.get("user")
        if not user or user["type"] != "client":
            return redirect(url_for("login"))
        return f(*a, **kw)
    return w


def staff_required(f):
    """Garante que apenas funcionários logados podem acessar"""
    @wraps(f)
    def w(*a, **kw):
        user = session.get("user")
        if not user or user["type"] != "staff":
            return redirect(url_for("login_funcionario"))
        return f(*a, **kw)
    return w

# =====================================
#   PÁGINAS PÚBLICAS
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

@app.route("/signin")
def signin():
    return render_template("signin.html")

@app.route("/frota")
def frota():
    return render_template("frota.html")

@app.route("/contato")
def contato():
    return render_template("contact.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")

@app.route("/solucoes")
def solucoes():
    return render_template("solucoes.html")

# =====================================
#   PÁGINAS PROTEGIDAS (CLIENTES)
# =====================================

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

@app.route("/devolucao")
@client_required
def devolucao_cliente_page():
    return render_template("devolucao_cliente.html")

# =====================================
#   PÁGINAS PROTEGIDAS (FUNCIONÁRIOS)
# =====================================

@app.route("/funcionario")
@staff_required
def funcionario_index():
    return render_template("funcionario/menufuncionario.html")

@app.route("/veiculos")
@staff_required
def veiculos_admin():
    return render_template("funcionario/veiculos.html")

@app.route("/clientes")
@staff_required
def clientes_admin():
    return render_template("funcionario/clientes.html")

@app.route("/mensagens")
@staff_required
def mensagens():
    return render_template("funcionario/mensagens.html")

# =====================================
#   AUTENTICAÇÃO (COM SEGURANÇA)
# =====================================

@app.route("/auth/login", methods=["POST"])
@limiter.limit("5 per minute")  # Proteção contra brute force
def auth_login():
    """Login seguro com validação e rate limiting"""
    data = request.form or request.json
    
    email = sanitize_input(data.get("email", "")).strip()
    password = data.get("password", "")
    
    if not email or not password:
        return jsonify({"ok": False, "error": "Email e senha são obrigatórios", "message": "Email e senha são obrigatórios"}), 400
    
    if not validate_email_address(email):
        return jsonify({"ok": False, "error": "Email inválido", "message": "Email inválido"}), 400
    
    if len(email) > 255:
        return jsonify({"ok": False, "error": "Email muito longo", "message": "Email muito longo"}), 400
    
    if len(password) > 500:
        return jsonify({"ok": False, "error": "Senha muito longa", "message": "Senha muito longa"}), 400
    
    user = USERS.get(email)
    
    if not user or not check_password(password, user["password"]):
        print(f"[SECURITY] Tentativa de login falha: {email}")
        return jsonify({"ok": False, "error": "Email ou senha incorretos", "message": "Email ou senha incorretos"}), 401
    
    session["user"] = {
        "email": email,
        "name": user["name"],
        "type": user["type"]
    }
    session.permanent = False
    
    print(f"[SECURITY] Login bem-sucedido: {email} ({user['type']})")
    
    if user["type"] == "staff":
        return jsonify({
            "ok": True,
            "message": "✓ Login bem-sucedido!",
            "redirect": "/funcionario"
        })
    else:
        return jsonify({
            "ok": True,
            "message": "✓ Login bem-sucedido!",
            "redirect": "/frota"
        })

@app.route("/auth/cadastro", methods=["POST"])
@limiter.limit("10 per minute")
def auth_cadastro():
    """Registro de novo cliente com validações robustas"""
    global USERS
    
    data = request.form or request.json
    
    # Validação de nome
    valid, name = validate_text_input(
        data.get("name", ""), "Nome",
        min_length=3, max_length=100
    )
    if not valid:
        return jsonify({"ok": False, "error": name, "message": name}), 400
    
    # Validação de email
    email = sanitize_input(data.get("email", "")).strip()
    if not validate_email_address(email):
        return jsonify({"ok": False, "error": "Email inválido", "message": "Email inválido"}), 400
    
    if email in USERS:
        return jsonify({"ok": False, "error": "Email já cadastrado", "message": "Email já cadastrado"}), 400
    
    # Validação de senha
    password = data.get("password", "")
    valid_pw, msg = validate_password_strength(password)
    if not valid_pw:
        return jsonify({"ok": False, "error": msg, "message": msg}), 400
    
    # Validação de telefone (opcional)
    phone = sanitize_input(data.get("phone", "")).strip() if data.get("phone") else None
    if phone and not validate_phone(phone):
        return jsonify({"ok": False, "error": "Telefone inválido", "message": "Telefone inválido"}), 400
    
    # Validação de CNH (opcional)
    cnh = data.get("cnh", "").strip() if data.get("cnh") else None
    if cnh:
        valid_cnh, msg_cnh = validate_cnh(cnh)
        if not valid_cnh:
            return jsonify({"ok": False, "error": msg_cnh, "message": msg_cnh}), 400
    
    USERS[email] = {
        "name": name,
        "password": hash_password(password),
        "type": "client",
        "phone": phone,
        "cnh": cnh
    }
    
    session["user"] = {"email": email, "name": name, "type": "client"}
    session.permanent = False
    
    print(f"[SECURITY] Novo cliente registrado: {email}")
    
    return jsonify({
        "ok": True,
        "message": "✓ Conta criada com sucesso!",
        "redirect": "/frota"
    })

@app.route("/logout")
def logout():
    """Logout seguro"""
    user = session.get("user")
    if user:
        print(f"[SECURITY] Logout: {user['email']}")
    session.clear()
    return redirect("/")

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

# =====================================
#   API — VEÍCULOS
# =====================================

@app.route('/api/vehicles', methods=['GET', 'POST', 'PUT'])
def api_vehicles():
    """GET: lista todos | POST: cria novo | PUT: atualiza"""
    global VEHICLES, next_vehicle_id
    
    if request.method == 'GET':
        return jsonify(VEHICLES)
    
    if request.method == 'POST':
        data = request.json
        
        plate = sanitize_input(data.get('plate', '')).upper()
        model = sanitize_input(data.get('model', ''))
        brand = sanitize_input(data.get('brand', ''))
        year = data.get('year')
        category = sanitize_input(data.get('category', ''))
        price = data.get('price')
        image = data.get('image')
        
        if not all([plate, model, brand, year, category, price]):
            return jsonify({'ok': False, 'error': 'Campos obrigatórios faltando'}), 400
        
        try:
            year = int(year)
            price = float(price)
        except (ValueError, TypeError):
            return jsonify({'ok': False, 'error': 'Ano e preço devem ser números'}), 400
        
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
        
        return jsonify({'ok': True, 'vehicle': obj}), 201
    
    if request.method == 'PUT':
        data = request.json
        vid = data.get('id')
        
        if vid is None:
            return jsonify({'ok': False, 'error': 'ID obrigatório'}), 400
        
        for v in VEHICLES:
            if v['id'] == vid:
                if 'status' in data:
                    v['status'] = sanitize_input(data['status'])
                if 'price' in data:
                    try:
                        v['price'] = float(data['price'])
                    except ValueError:
                        return jsonify({'ok': False, 'error': 'Preço inválido'}), 400
                if 'image' in data:
                    v['image'] = sanitize_input(data['image'])
                
                return jsonify({'ok': True, 'vehicle': v})
        
        return jsonify({'ok': False, 'error': 'Veículo não encontrado'}), 404

@app.route("/api/vehicles/<int:vid>", methods=["DELETE"])
@staff_required
def delete_vehicle(vid):
    """Deleta um veículo (apenas para funcionários)"""
    global VEHICLES
    
    vehicle = next((v for v in VEHICLES if v["id"] == vid), None)
    if not vehicle:
        return jsonify({"ok": False, "error": "Veículo não encontrado"}), 404
    
    VEHICLES = [v for v in VEHICLES if v["id"] != vid]
    
    print(f"[ADMIN] Veículo deletado: {vid}")
    return jsonify({"ok": True, "message": "Veículo removido com sucesso"})

# =====================================
#   API — ALUGUÉIS
# =====================================

@app.route("/api/rentals/history", methods=["GET"])
@client_required
def rentals_history():
    """Histórico de aluguéis do cliente"""
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
                "total": r["total"],
                "status": r["status"]
            })
    
    return jsonify(result)

@app.route("/api/rent/reserve", methods=["POST"])
@client_required
def reserve_vehicle():
    """Reserva um veículo"""
    data = request.json
    vid = data.get("id")
    
    vehicle = next((v for v in VEHICLES if v["id"] == vid), None)
    if not vehicle:
        return jsonify({"error": "Veículo não existe"}), 404
    
    if vehicle["status"] != "available":
        return jsonify({"error": "Veículo não está disponível"}), 400
    
    vehicle["status"] = "reserved"
    
    return jsonify({"ok": True, "redirect": f"/pagamento/{vid}"})

@app.route("/api/rent/pay", methods=["POST"])
@client_required
def pay_vehicle():
    """Pagamento e confirmação de aluguel"""
    global next_rental_id
    
    data = request.json
    vid = data.get("id")
    
    try:
        days = int(data.get("days", 1))
    except (ValueError, TypeError):
        return jsonify({"ok": False, "error": "Dias deve ser um número"}), 400
    
    vehicle = next((v for v in VEHICLES if v["id"] == vid), None)
    if not vehicle:
        return jsonify({"ok": False, "error": "Veículo não encontrado"}), 404
    
    if vehicle["status"] not in ["available", "reserved"]:
        return jsonify({"ok": False, "error": "Veículo não está disponível"}), 400
    
    daily_price = vehicle["price"]
    total = daily_price * days
    vehicle["status"] = "rented"
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
        "end_datetime": None,
        "end_km": None,
        "final_total": total,
        "refund": 0
    })
    
    next_rental_id += 1
    
    return jsonify({"ok": True, "total": total, "deposit": deposit})

@app.route("/api/rent/return/preview", methods=["POST"])
@client_required
def preview_return():
    """Preview de devolução com cálculos"""
    data = request.json
    rental_id = data.get("rental_id")
    end_km = data.get("end_km")
    damage_value = float(data.get("damage_value", 0) or 0)
    
    if rental_id is None or end_km is None:
        return jsonify({"ok": False, "error": "ID do aluguel e km final são obrigatórios"}), 400
    
    KM_LIMIT_PER_RENTAL = 300
    EXTRA_KM_PRICE = 1.5
    
    rental = next((r for r in RENTALS if r["rental_id"] == rental_id), None)
    if not rental:
        return jsonify({"ok": False, "error": "Aluguel não encontrado"}), 404
    
    user = session.get("user")
    if not user or user["email"] != rental["client_email"]:
        return jsonify({"ok": False, "error": "Você não tem permissão para este aluguel"}), 403
    
    if rental.get("status") == "finished":
        return jsonify({"ok": False, "error": "Este aluguel já foi finalizado"}), 400
    
    start_datetime = datetime.fromisoformat(rental["start_datetime"])
    end_datetime = datetime.now()
    days_used = max(1, (end_datetime - start_datetime).days)
    
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
    refund = final_total - deposit
    
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
    """Confirma devolução do veículo"""
    data = request.json
    rental_id = data.get("rental_id")
    end_km = data.get("end_km")
    damage_value = float(data.get("damage_value", 0) or 0)
    
    if rental_id is None or end_km is None:
        return jsonify({"ok": False, "error": "Dados incompletos"}), 400
    
    KM_LIMIT_PER_RENTAL = 300
    EXTRA_KM_PRICE = 1.5
    
    rental = next((r for r in RENTALS if r["rental_id"] == rental_id), None)
    if not rental:
        return jsonify({"ok": False, "error": "Aluguel não encontrado"}), 404
    
    user = session.get("user")
    if not user or user["email"] != rental["client_email"]:
        return jsonify({"ok": False, "error": "Você não tem permissão para este aluguel"}), 403
    
    if rental.get("status") == "finished":
        return jsonify({"ok": False, "error": "Este aluguel já foi finalizado"}), 400
    
    vehicle = next((v for v in VEHICLES if v["id"] == rental["vehicle_id"]), None)
    if not vehicle:
        return jsonify({"ok": False, "error": "Veículo não encontrado"}), 404
    
    start_datetime = datetime.fromisoformat(rental["start_datetime"])
    end_datetime = datetime.now()
    days_used = max(1, (end_datetime - start_datetime).days)
    
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
    
    print(f"[RENTAL] Devolução confirmada: rental_id={rental_id}, cliente={user['email']}")
    
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
#   API — CLIENTES
# =====================================

@app.route("/api/clients", methods=["GET"])
@staff_required
def api_clients():
    """Lista todos os clientes (apenas funcionários)"""
    clients_list = []
    for email, user_data in USERS.items():
        if user_data.get("type") == "client":
            clients_list.append({
                "email": email,
                "name": user_data.get("name"),
                "phone": user_data.get("phone", "Não informado"),
                "cnh": user_data.get("cnh", "Não informada")
            })
    return jsonify(clients_list)

# =====================================
#   API — MENSAGENS DE CONTATO
# =====================================

@app.route("/api/contact/send", methods=["POST"])
def send_contact_message():
    """Envia uma mensagem de contato"""
    global next_message_id
    
    data = request.json
    
    name = sanitize_input(data.get("name", "")).strip()
    email = sanitize_input(data.get("email", "")).strip()
    phone = sanitize_input(data.get("phone", "")).strip()
    message = sanitize_input(data.get("message", "")).strip()
    
    if not name or not email or not message:
        return jsonify({"ok": False, "error": "Nome, email e mensagem são obrigatórios"}), 400
    
    if not validate_email_address(email):
        return jsonify({"ok": False, "error": "Email inválido"}), 400
    
    if len(message) < 10:
        return jsonify({"ok": False, "error": "A mensagem deve ter no mínimo 10 caracteres"}), 400
    
    CONTACT_MESSAGES.append({
        "id": next_message_id,
        "name": name,
        "email": email,
        "phone": phone,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "read": False
    })
    
    next_message_id += 1
    
    print(f"[CONTACT] Nova mensagem: {email}")
    
    return jsonify({"ok": True, "message": "Mensagem enviada com sucesso!"})

@app.route("/api/contact/messages", methods=["GET"])
@staff_required
def get_contact_messages():
    """Retorna todas as mensagens de contato (apenas funcionários)"""
    return jsonify(CONTACT_MESSAGES)

@app.route("/api/contact/messages/<int:msg_id>/read", methods=["PUT"])
@staff_required
def mark_message_read(msg_id):
    """Marca uma mensagem como lida"""
    try:
        for msg in CONTACT_MESSAGES:
            if msg["id"] == msg_id:
                msg["read"] = True
                return jsonify({"ok": True, "message": "Marcado como lida"})
        
        return jsonify({"ok": False, "error": "Mensagem não encontrada"}), 404
    except Exception as e:
        print(f"[ERROR] Erro ao marcar mensagem como lida: {str(e)}")
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/contact/messages/<int:msg_id>", methods=["DELETE"])
@staff_required
def delete_contact_message(msg_id):
    """Deleta uma mensagem de contato"""
    try:
        global CONTACT_MESSAGES
        
        original_len = len(CONTACT_MESSAGES)
        CONTACT_MESSAGES = [msg for msg in CONTACT_MESSAGES if msg["id"] != msg_id]
        
        if len(CONTACT_MESSAGES) < original_len:
            print(f"[ADMIN] Mensagem deletada: {msg_id}")
            return jsonify({"ok": True, "message": "Deletado com sucesso"})
        else:
            return jsonify({"ok": False, "error": "Mensagem não encontrada"}), 404
    except Exception as e:
        print(f"[ERROR] Erro ao deletar mensagem: {str(e)}")
        return jsonify({"ok": False, "error": str(e)}), 500

# =====================================
#   SEED DE DADOS
# =====================================

@app.before_request
def seed_data():
    """Carrega dados iniciais"""
    global seeded, VEHICLES, next_vehicle_id
    
    if seeded:
        return
    
    seeded = True
    
    VEHICLES = [
        {"id": 1, "plate": "ABC-1234", "model": "Corolla", "brand": "Toyota", "year": 2022, "category": "sedan", "price": 150, "image": "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=800&q=80", "status": "available"},
        {"id": 2, "plate": "XYZ-5678", "model": "Civic", "brand": "Honda", "year": 2023, "category": "sedan", "price": 180, "image": "https://images.unsplash.com/photo-1606611013016-969c19d14311?w=800&q=80", "status": "available"},
        {"id": 3, "plate": "DEF-9012", "model": "HR-V", "brand": "Honda", "year": 2021, "category": "suv", "price": 200, "image": "https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=800&q=80", "status": "available"},
        {"id": 4, "plate": "GHI-3456", "model": "Onix", "brand": "Chevrolet", "year": 2023, "category": "hatch", "price": 120, "image": "https://images.unsplash.com/photo-1489824904134-891ab64532f1?w=800&q=80", "status": "rented"},
        {"id": 5, "plate": "JKL-7890", "model": "Compass", "brand": "Jeep", "year": 2022, "category": "suv", "price": 250, "image": "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=800&q=80", "status": "available"},
        {"id": 6, "plate": "MNO-1122", "model": "Gol", "brand": "Volkswagen", "year": 2020, "category": "hatch", "price": 100, "image": "https://images.unsplash.com/photo-1590362891990-f8ddb41d006d?w=800&q=80", "status": "available"},
        {"id": 7, "plate": "PQR-3344", "model": "Nivus", "brand": "Volkswagen", "year": 2022, "category": "suv", "price": 190, "image": "https://images.unsplash.com/photo-1581540222194-0def2dda95b8?w=800&q=80", "status": "available"},
        {"id": 8, "plate": "STU-5566", "model": "Tracker", "brand": "Chevrolet", "year": 2021, "category": "suv", "price": 210, "image": "https://images.unsplash.com/photo-1606611013016-969c19d14311?w=800&q=80", "status": "reserved"},
        {"id": 9, "plate": "VWX-7788", "model": "Argo", "brand": "Fiat", "year": 2022, "category": "hatch", "price": 115, "image": "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=800&q=80", "status": "available"},
        {"id": 10, "plate": "YZA-9900", "model": "Cronos", "brand": "Fiat", "year": 2021, "category": "sedan", "price": 130, "image": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800&q=80", "status": "available"},
        {"id": 11, "plate": "BCA-2233", "model": "Kicks", "brand": "Nissan", "year": 2023, "category": "suv", "price": 220, "image": "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=800&q=80", "status": "available"},
        {"id": 12, "plate": "DEF-4455", "model": "Corolla Cross", "brand": "Toyota", "year": 2023, "category": "suv", "price": 260, "image": "https://images.unsplash.com/photo-1606664515524-2134e2f37a85?w=800&q=80", "status": "available"},
        {"id": 13, "plate": "GHI-6677", "model": "HB20", "brand": "Hyundai", "year": 2021, "category": "hatch", "price": 110, "image": "https://images.unsplash.com/photo-1485463611174-f302f6a5c1c9?w=800&q=80", "status": "available"},
        {"id": 14, "plate": "JKL-8899", "model": "Creta", "brand": "Hyundai", "year": 2022, "category": "suv", "price": 230, "image": "https://images.unsplash.com/photo-1551830820-330a71b99659?w=800&q=80", "status": "rented"},
        {"id": 15, "plate": "MNO-1357", "model": "Renegade", "brand": "Jeep", "year": 2021, "category": "suv", "price": 240, "image": "https://images.unsplash.com/photo-1606611013016-969c19d14311?w=800&q=80", "status": "available"},
        {"id": 16, "plate": "PQR-2468", "model": "Sandero", "brand": "Renault", "year": 2020, "category": "hatch", "price": 95, "image": "https://images.unsplash.com/photo-1520031441872-265e4ff70366?w=800&q=80", "status": "available"},
        {"id": 17, "plate": "STU-3691", "model": "Logan", "brand": "Renault", "year": 2021, "category": "sedan", "price": 115, "image": "https://images.unsplash.com/photo-1502877338535-766e1452684a?w=800&q=80", "status": "maintenance"},
        {"id": 18, "plate": "VWX-4826", "model": "Yaris", "brand": "Toyota", "year": 2022, "category": "hatch", "price": 140, "image": "https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=800&q=80", "status": "available"},
        {"id": 19, "plate": "YZA-5937", "model": "City", "brand": "Honda", "year": 2022, "category": "sedan", "price": 170, "image": "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=800&q=80", "status": "available"},
        {"id": 20, "plate": "BCA-6048", "model": "T-Cross", "brand": "Volkswagen", "year": 2023, "category": "suv", "price": 245, "image": "https://images.unsplash.com/photo-1506521781263-d8422e82f27a?w=800&q=80", "status": "available"},
        {"id": 21, "plate": "DEF-7159", "model": "Captur", "brand": "Renault", "year": 2021, "category": "suv", "price": 205, "image": "https://images.unsplash.com/photo-1514316454349-750a7fd3da3a?w=800&q=80", "status": "available"}
    ]
    
    next_vehicle_id = 22

# =====================================
#   INICIALIZAÇÃO
# =====================================

if __name__ == "__main__":
    app.run(debug=True)