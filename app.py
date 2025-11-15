from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from functools import wraps

app = Flask(__name__)
app.secret_key = 'troque_essa_chave_para_algo_secreto'

# Bancos em memória
CLIENTS = []
VEHICLES = []
USERS = {
    # Funcionário padrão
    'admin@example.com': {'password': '123456', 'name': 'Admin', 'type': 'staff'}
}

next_client_id = 1
next_vehicle_id = 1
seeded = False


# ========================
#   Helpers
# ========================

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('user'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper


# ========================
#   Páginas públicas
# ========================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_funcionario')
def login_funcionario():
    return render_template('login_funcionario.html')

@app.route('/cadastro')
def cadastro():
    return render_template('signin.html')


# ========================
#   Autenticação
# ========================

@app.route('/auth/login', methods=['POST'])
def auth_login():
    data = request.form or request.json
    email = data.get('email')
    password = data.get('password')

    user = USERS.get(email)

    if user and user['password'] == password:
        session['user'] = {
            'email': email,
            'name': user['name'],
            'type': user['type']
        }

        # Funcionário -> vai para clientes
        if user['type'] == 'staff':
            return jsonify({'ok': True, 'redirect': url_for('clientes_page')})

        # Cliente -> frota
        return jsonify({'ok': True, 'redirect': url_for('frota')})

    return jsonify({'ok': False, 'error': 'Credenciais inválidas'})


@app.route('/auth/cadastro', methods=['POST'])
def auth_cadastro():
    global USERS

    data = request.form or request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'ok': False, 'error': 'Preencha todos os campos'})

    if email in USERS:
        return jsonify({'ok': False, 'error': 'E-mail já cadastrado'})

    USERS[email] = {
        'name': name,
        'password': password,
        'type': 'client'
    }

    session['user'] = {
        'email': email,
        'name': name,
        'type': 'client'
    }

    return jsonify({'ok': True, 'redirect': url_for('frota')})


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ========================
#   Páginas protegidas
# ========================

@app.route('/frota')
@login_required
def frota():
    return render_template('frota.html')

@app.route('/clientes')
@login_required
def clientes_page():
    return render_template('clientes.html')

@app.route('/veiculos')
@login_required
def veiculos_page():
    return render_template('veiculos.html')


# ========================
#         APIs
# ========================

@app.route('/api/clients', methods=['GET', 'POST', 'DELETE'])
def api_clients():
    global CLIENTS, next_client_id

    if request.method == 'GET':
        return jsonify(CLIENTS)

    if request.method == 'POST':
        data = request.json
        name = data.get('name')
        phone = data.get('phone')

        if not name or not phone:
            return jsonify({'ok': False, 'error': 'Campos obrigatórios faltando'}), 400

        obj = {'id': next_client_id, 'name': name, 'phone': phone}
        next_client_id += 1
        CLIENTS.append(obj)

        return jsonify({'ok': True, 'client': obj})

    if request.method == 'DELETE':
        id_target = request.json.get('id')
        CLIENTS = [c for c in CLIENTS if c['id'] != id_target]
        return jsonify({'ok': True})


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

        for v in VEHICLES:
            if v['id'] == vid:
                if 'status' in data:
                    v['status'] = data['status']
                return jsonify({'ok': True, 'vehicle': v})

        return jsonify({'ok': False, 'error': 'Veículo não encontrado'}), 404


# ========================
#   Seed inicial
# ========================

@app.before_request
def seed_data():
    global seeded, CLIENTS, VEHICLES, next_client_id, next_vehicle_id

    if seeded:
        return

    seeded = True

    if not CLIENTS:
        CLIENTS = [
            {'id': 1, 'name': 'João Silva', 'phone': '(11) 99999-0000'},
            {'id': 2, 'name': 'Maria Oliveira', 'phone': '(21) 98888-1111'}
        ]
        next_client_id = 3

    if not VEHICLES:
        VEHICLES = [
            {'id': 1, 'plate': 'ABC-1234', 'model': 'Toyota Corolla', 'year': 2018, 'status': 'available'},
            {'id': 2, 'plate': 'XYZ-9876', 'model': 'Honda Civic', 'year': 2020, 'status': 'rented'}
        ]
        next_vehicle_id = 3


# ========================
#   Execução
# ========================

if __name__ == '__main__':
    app.run(debug=True)
