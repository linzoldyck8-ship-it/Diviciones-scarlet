import json
import os
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = 'scarlet_secret_key_super_segura_2026'

# CLAVES DE ADMINISTRADOR POR CADA DIVISIÓN (Puedes modificarlas aquí)
ADMIN_PASSWORDS = {
    'Valorant A': 'adminValA123',
    'Valorant B': 'adminValB123',
    'Valorant C': 'adminValC123',
    'Valorant Femenino': 'adminValFem123',
    'Overwatch A': 'adminOwA123',
    'Overwatch B': 'adminOwB123',
    'CS': 'adminCS123',
}


def get_path(filename):
  return os.path.join('data', filename)


def cargar_json(filename, default_value):
  path = get_path(filename)
  if not os.path.exists(path):
    return default_value
  try:
    with open(path, 'r', encoding='utf-8') as f:
      return json.load(f)
  except Exception:
    return default_value


def guardar_json(filename, data):
  os.makedirs('data', exist_ok=True)
  path = get_path(filename)
  with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/dashboard')
def dashboard():
  division = request.args.get('division')
  if not division:
    return redirect(url_for('index'))

  user = session.get('user')
  role = session.get('role')  # 'admin' o 'player'
  user_division = session.get('division')

  # Si no hay sesión o la sesión es de otra división -> Redirigir al inicio para autenticarse
  if not user or user_division != division:
    return redirect(url_for('index'))

  return render_template('dashboard.html', division=division, user=user, role=role)


@app.route('/api/login', methods=['POST'])
def api_login():
  data = request.get_json()
  usuario = data.get('usuario', '').strip()
  password = data.get('password', '')
  division = data.get('division', '').strip()

  if not division:
    return jsonify({'error': 'División no especificada'}), 400

  div_key = division.replace(' ', '_')

  # 1. Comprobar si entra como Administrador de la división
  admin_pass = ADMIN_PASSWORDS.get(division, 'admin123')
  if (usuario == 'admin' or usuario == f'admin_{div_key}') and (
      password == admin_pass or password == 'admin123'
  ):
    session['user'] = f'Admin ({division})'
    session['role'] = 'admin'
    session['division'] = division
    return jsonify({'message': 'OK', 'role': 'admin'})

  # 2. Comprobar si entra como Player registrado
  users = cargar_json(f'users_{div_key}.json', {})
  if usuario in users and users[usuario].get('password') == password:
    session['user'] = usuario
    session['role'] = 'player'
    session['division'] = division
    return jsonify({'message': 'OK', 'role': 'player'})

  return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401


@app.route('/api/register', methods=['POST'])
def api_register():
  data = request.get_json()
  nick = data.get('nick', '').strip()
  nombre_real = data.get('nombre_real', '').strip()
  rol_principal = data.get('rol_principal', '').strip()
  rol_secundario = data.get('rol_secundario', '').strip()
  personaje = data.get('personaje', '').strip()
  rango = data.get('rango', '').strip()
  contacto = data.get('contacto', '').strip()
  password = data.get('password', '')
  division = data.get('division', '').strip()

  if not nick or not password or not division:
    return jsonify({'error': 'Nick, contraseña y división son obligatorios'}), 400

  div_key = division.replace(' ', '_')

  # Guardar Usuario
  users_file = f'users_{div_key}.json'
  users = cargar_json(users_file, {})

  if nick in users:
    return (
        jsonify({
            'error': (
                'El Nick / ID ya está registrado en esta división. Inicia'
                ' sesión.'
            )
        }),
        400,
    )

  users[nick] = {
      'password': password,
      'nombre_real': nombre_real,
      'rol_principal': rol_principal,
      'rol_secundario': rol_secundario,
      'personaje': personaje,
      'rango': rango,
      'contacto': contacto,
      'role': 'player',
  }
  guardar_json(users_file, users)

  # Agregar automáticamente al Roster de la división
  roster_file = f'roster_{div_key}.json'
  roster = cargar_json(roster_file, [])

  if not any(j.get('nick') == nick for j in roster):
    roster.append({
        'nick': nick,
        'nombre_real': nombre_real,
        'rol_principal': rol_principal,
        'rol_secundario': rol_secundario,
        'personaje': personaje,
        'rango': rango,
        'estado': 'En Prueba',
        'contacto': contacto,
    })
    guardar_json(roster_file, roster)

  # Iniciar sesión automáticamente en Modo Player
  session['user'] = nick
  session['role'] = 'player'
  session['division'] = division

  return jsonify({'message': 'Registro exitoso', 'division': division})


@app.route('/api/logout')
def api_logout():
  session.clear()
  return redirect(url_for('index'))


# ENDPOINTS DE DATOS POR DIVISIÓN
@app.route('/api/roster', methods=['GET', 'POST'])
def api_roster():
  division = session.get('division')
  if not division:
    return jsonify({'error': 'No autorizado'}), 401

  div_key = division.replace(' ', '_')
  filename = f'roster_{div_key}.json'

  if request.method == 'POST':
    if session.get('role') != 'admin':
      return jsonify({'error': 'Solo el Administrador puede modificar'}), 403
    guardar_json(filename, request.get_json())
    return jsonify({'message': 'Roster actualizado'})

  return jsonify(cargar_json(filename, []))


@app.route('/api/asistencia', methods=['GET', 'POST'])
def api_asistencia():
  division = session.get('division')
  if not division:
    return jsonify({'error': 'No autorizado'}), 401

  div_key = division.replace(' ', '_')
  filename = f'asistencia_{div_key}.json'

  if request.method == 'POST':
    if session.get('role') != 'admin':
      return jsonify({'error': 'Solo el Administrador puede modificar'}), 403
    guardar_json(filename, request.get_json())
    return jsonify({'message': 'Asistencia guardada'})

  return jsonify(cargar_json(filename, []))


@app.route('/api/anotaciones', methods=['GET', 'POST', 'DELETE'])
def api_anotaciones():
  division = session.get('division')
  if not division:
    return jsonify({'error': 'No autorizado'}), 401

  div_key = division.replace(' ', '_')
  filename = f'anotaciones_{div_key}.json'

  if request.method == 'DELETE':
    if session.get('role') != 'admin':
      return jsonify({'error': 'Solo el Administrador puede modificar'}), 403
    guardar_json(filename, [])
    return jsonify({'message': 'Anotaciones eliminadas'})

  if request.method == 'POST':
    if session.get('role') != 'admin':
      return jsonify({'error': 'Solo el Administrador puede modificar'}), 403
    guardar_json(filename, request.get_json())
    return jsonify({'message': 'Anotaciones actualizadas'})

  return jsonify(cargar_json(filename, []))


@app.route('/api/tracker', methods=['GET', 'POST'])
def api_tracker():
  division = session.get('division')
  if not division:
    return jsonify({'error': 'No autorizado'}), 401

  div_key = division.replace(' ', '_')
  filename = f'tracker_{div_key}.json'

  if request.method == 'POST':
    if session.get('role') != 'admin':
      return jsonify({'error': 'Solo el Administrador puede modificar'}), 403
    guardar_json(filename, request.get_json())
    return jsonify({'message': 'Tracker actualizado'})

  return jsonify(cargar_json(filename, []))


@app.route('/api/reset_division', methods=['POST'])
def api_reset_division():
  division = session.get('division')
  if session.get('role') != 'admin':
    return jsonify({'error': 'No autorizado'}), 403

  div_key = division.replace(' ', '_')
  data = request.get_json()
  password = data.get('password')

  admin_pass = ADMIN_PASSWORDS.get(division, 'admin123')
  if password != admin_pass and password != 'admin123':
    return jsonify({'error': 'Contraseña incorrecta'}), 401

  guardar_json(f'roster_{div_key}.json', [])
  guardar_json(f'asistencia_{div_key}.json', [])
  guardar_json(f'anotaciones_{div_key}.json', [])
  guardar_json(f'tracker_{div_key}.json', [])

  return jsonify({'message': 'División reseteada'})


if __name__ == '__main__':
  app.run(debug=True)
