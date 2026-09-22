import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "scarlet_secret_key_2026")

engine = None

def get_db():
    global engine
    if engine is None:
        raw_url = os.environ.get("SUPABASE_DB_URL", "").strip()
        if raw_url.startswith("https://"):
            raw_url = raw_url.replace("https://", "postgresql://", 1)
        elif raw_url.startswith("http://"):
            raw_url = raw_url.replace("http://", "postgresql://", 1)

        if not raw_url:
            raw_url = "postgresql://postgres:password@localhost:5432/postgres"

        raw_url = raw_url.replace("?pgbouncer=true", "").replace("&pgbouncer=true", "")
        raw_url = raw_url.replace("?pgbouncer=false", "").replace("&pgbouncer=false", "")
            
        if raw_url.startswith("postgresql://"):
            raw_url = raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
            
        if "sslmode" not in raw_url:
            separator = "&" if "?" in raw_url else "?"
            raw_url = f"{raw_url}{separator}sslmode=require"
            
        engine = create_engine(raw_url, pool_pre_ping=True)
    return engine

DIVISIONES_DISPONIBLES = [
    "Valorant A", "Valorant B", "Valorant C", "Valorant Femenino",
    "Overwatch A", "Overwatch B", "CS"
]

GAME_DATA = {
    "Valorant": {
        "Roles": ["Duelista", "Iniciador", "Controlador", "Centinela", "Flex"],
        "Rangos": ["Hierro", "Bronce", "Plata", "Oro", "Platino", "Diamante", "Ascendente", "Inmortal", "Radiante"],
        "Personajes": ["Jett", "Reyna", "Phoenix", "Raze", "Neon", "Iso", "Sova", "Fade", "Skye", "Breach", "KAY/O", "Gekko", "Omen", "Brimstone", "Viper", "Astra", "Harbor", "Clove", "Cypher", "Killjoy", "Sage", "Chamber", "Deadlock"]
    },
    "Overwatch": {
        "Roles": ["Tanque", "Daño (DPS)", "Apoyo (Support)", "Flex"],
        "Rangos": ["Bronce", "Plata", "Oro", "Platino", "Esmeralda", "Diamante", "Maestro", "Gran Maestro", "Campeón", "Top 500"],
        "Personajes": ["Reinhardt", "Winston", "D.Va", "Sigma", "Zarya", "Ramattra", "Tracer", "Genji", "Widowmaker", "Cassidy", "Pharah", "Sombra", "Sojourn", "Mercy", "Ana", "Lúcio", "Kiriko", "Zenyatta", "Baptiste", "Illari"]
    },
    "CS": {
        "Roles": ["Entry Fragger", "AWPer", "Support", "IGL", "Lurker", "Flex"],
        "Rangos": ["FACEIT Nivel 1-5", "FACEIT Nivel 6-10", "GC Nivel 1-10", "GC Nivel 11-20"],
        "Personajes": ["Fuerzas Antiterroristas (CT)", "Fuerzas Terroristas (T)"]
    }
}

def get_prefix(div_name):
    if not div_name:
        return "valorant_a"
    return div_name.replace(" ", "_").lower()

def get_game_data(div_name):
    if not div_name: return GAME_DATA["Valorant"]
    if "Overwatch" in div_name: return GAME_DATA["Overwatch"]
    if "CS" in div_name: return GAME_DATA["CS"]
    return GAME_DATA["Valorant"]

def is_admin():
    return session.get('role') == 'admin'

@app.route('/')
def index():
    return render_template('index.html', divisiones=DIVISIONES_DISPONIBLES)

@app.route('/division/<nombre>')
def seleccionar_division(nombre):
    if nombre in DIVISIONES_DISPONIBLES:
        session['division'] = nombre
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    division = session.get('division')
    if not division:
        return redirect(url_for('index'))
    return render_template('dashboard.html', 
                           division=division, 
                           user=session.get('user'), 
                           role=session.get('role', 'invitado'), 
                           game_info=get_game_data(division))

# --- API LOGIN & REGISTRO ---
@app.route('/api/login', methods=['POST'])
def login():
    division = session.get('division')
    if not division:
        return jsonify({'error': 'No has seleccionado división'}), 400
    
    data = request.json or {}
    prefix = get_prefix(division)
    usuario = data.get('usuario', '').strip().lower()
    password = data.get('password', '').strip()

    try:
        df_cfg = pd.read_sql_query(f'SELECT * FROM "{prefix}_config"', get_db())
        df_bl = pd.read_sql_query(f'SELECT * FROM "{prefix}_blacklist"', get_db())

        match = df_cfg[(df_cfg['usuario'].astype(str).str.lower() == usuario) & (df_cfg['password'].astype(str) == password)]
        if match.empty:
            return jsonify({'error': 'Usuario o contraseña incorrectos.'}), 401

        nombre_real = match.iloc[0]['nombre_real']
        rol = match.iloc[0]['rol']

        if rol != 'admin' and not df_bl.empty and not df_bl[df_bl['nombre_real'].astype(str).str.lower() == nombre_real.lower()].empty:
            return jsonify({'error': 'ACCESO DENEGADO: Te encuentras en la Lista Negra.'}), 403

        session['user'] = nombre_real
        session['role'] = rol
        return jsonify({'message': 'Login exitoso', 'role': rol, 'user': nombre_real})
    except Exception as e:
        return jsonify({'error': f'Error en base de datos: {str(e)}'}), 500

@app.route('/api/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- API ROSTER ---
@app.route('/api/roster', methods=['GET', 'POST'])
def api_roster():
    division = session.get('division')
    if not division: return jsonify([]), 200
    prefix = get_prefix(division)

    if request.method == 'GET':
        try:
            df = pd.read_sql_query(f'SELECT * FROM "{prefix}_roster"', get_db())
            return jsonify(df.to_dict(orient='records'))
        except Exception:
            return jsonify([])

    if request.method == 'POST':
        if not is_admin():
            return jsonify({'error': 'Solo administradores pueden modificar el roster'}), 403
        try:
            pd.DataFrame(request.json).to_sql(f"{prefix}_roster", get_db(), if_exists='replace', index=False)
            return jsonify({'message': 'Roster actualizado correctamente'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# --- API ASISTENCIA ---
@app.route('/api/asistencia', methods=['GET', 'POST'])
def api_asistencia():
    division = session.get('division')
    if not division: return jsonify([]), 200
    prefix = get_prefix(division)

    if request.method == 'GET':
        try:
            df = pd.read_sql_query(f'SELECT * FROM "{prefix}_asistencia"', get_db())
            return jsonify(df.to_dict(orient='records'))
        except Exception:
            return jsonify([])

    if request.method == 'POST':
        if not is_admin():
            return jsonify({'error': 'Acceso denegado. Se requiere rol de administrador.'}), 403
        try:
            pd.DataFrame(request.json).to_sql(f"{prefix}_asistencia", get_db(), if_exists='replace', index=False)
            return jsonify({'message': 'Asistencia guardada correctamente'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# --- API ANOTACIONES Y SANCIONES ---
@app.route('/api/anotaciones', methods=['GET', 'POST'])
def api_anotaciones():
    division = session.get('division')
    if not division: return jsonify([]), 200
    prefix = get_prefix(division)

    if request.method == 'GET':
        try:
            df = pd.read_sql_query(f'SELECT * FROM "{prefix}_anotaciones"', get_db())
            return jsonify(df.to_dict(orient='records'))
        except Exception:
            return jsonify([])

    if request.method == 'POST':
        if not is_admin():
            return jsonify({'error': 'Acceso denegado. Se requiere rol de administrador.'}), 403
        try:
            pd.DataFrame(request.json).to_sql(f"{prefix}_anotaciones", get_db(), if_exists='replace', index=False)
            return jsonify({'message': 'Anotaciones guardadas correctamente'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# --- API TRACKER ---
@app.route('/api/tracker', methods=['GET', 'POST'])
def api_tracker():
    division = session.get('division')
    if not division: return jsonify([]), 200
    prefix = get_prefix(division)

    if request.method == 'GET':
        try:
            df = pd.read_sql_query(f'SELECT * FROM "{prefix}_tracker"', get_db())
            return jsonify(df.to_dict(orient='records'))
        except Exception:
            return jsonify([])

    if request.method == 'POST':
        if not is_admin():
            return jsonify({'error': 'Acceso denegado. Se requiere rol de administrador.'}), 403
        try:
            pd.DataFrame(request.json).to_sql(f"{prefix}_tracker", get_db(), if_exists='replace', index=False)
            return jsonify({'message': 'Tracker actualizado correctamente'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/reset_division', methods=['POST'])
def reset_division():
    if not is_admin():
        return jsonify({'error': 'Solo los administradores pueden resetear la división'}), 403
    password = request.json.get('password')
    division = session.get('division')
    prefix = get_prefix(division)
    
    try:
        df_cfg = pd.read_sql_query(f'SELECT * FROM "{prefix}_config"', get_db())
        if df_cfg[(df_cfg['password'].astype(str) == password) & (df_cfg['rol'] == 'admin')].empty:
            return jsonify({'error': 'Contraseña de administrador incorrecta'}), 401

        pd.DataFrame(columns=["nick", "nombre_real", "rol_principal", "rol_secundario", "personaje", "rango", "cargo", "estado", "actividad", "contacto", "notas"]).to_sql(f"{prefix}_roster", get_db(), if_exists='replace', index=False)
        return jsonify({'message': 'División reseteada exitosamente.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
