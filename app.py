import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "scarlet_secret_key_2026")

# CONEXIÓN SEGURA A SUPABASE (DIFERIDA)
engine = None

def get_db():
    global engine
    if engine is None:
        raw_url = os.environ.get("SUPABASE_DB_URL", "")
        if not raw_url:
            raw_url = "postgresql://postgres:password@localhost:5432/postgres"
            
        if raw_url.startswith("postgresql://"):
            raw_url = raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        if ".supabase.co" in raw_url and "pooler.supabase.com" not in raw_url:
            raw_url = raw_url.replace("db.", "").replace(".supabase.co", ".pooler.supabase.com:6543")
        if "?sslmode=" not in raw_url and "sslmode" not in raw_url:
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
    return div_name.replace(" ", "_").lower()

def get_game_data(div_name):
    if "Overwatch" in div_name: return GAME_DATA["Overwatch"]
    if "CS" in div_name: return GAME_DATA["CS"]
    return GAME_DATA["Valorant"]

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
    return render_template('dashboard.html', division=division, user=session.get('user'), role=session.get('role', 'invitado'), game_info=get_game_data(division))

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    division = session.get('division')
    prefix = get_prefix(division)
    
    usuario = data.get('usuario', '').strip().lower()
    password = data.get('password', '').strip()

    df_cfg = pd.read_sql_table(f"{prefix}_config", get_db())
    df_bl = pd.read_sql_table(f"{prefix}_blacklist", get_db())

    match = df_cfg[(df_cfg['usuario'].astype(str).str.lower() == usuario) & (df_cfg['password'].astype(str) == password)]
    if match.empty:
        return jsonify({'error': 'Credenciales incorrectas'}), 401

    nombre_real = match.iloc[0]['nombre_real']
    rol = match.iloc[0]['rol']

    if rol != 'admin' and not df_bl[df_bl['nombre_real'].str.lower() == nombre_real.lower()].empty:
        return jsonify({'error': 'ACCESO DENEGADO: Te encuentras en la Lista Negra.'}), 403

    session['user'] = nombre_real
    session['role'] = rol
    return jsonify({'message': 'Ok', 'role': rol, 'user': nombre_real})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json or {}
    division = session.get('division')
    prefix = get_prefix(division)
    
    nombre_real = data.get('nombre_real', '').strip()
    usuario = data.get('usuario', '').strip().lower()
    
    df_bl = pd.read_sql_table(f"{prefix}_blacklist", get_db())
    df_cfg = pd.read_sql_table(f"{prefix}_config", get_db())
    df_roster = pd.read_sql_table(f"{prefix}_roster", get_db())

    if not df_bl[df_bl['nombre_real'].str.lower() == nombre_real.lower()].empty:
        return jsonify({'error': 'REGISTRO DENEGADO: El jugador está en Lista Negra.'}), 403
    if not df_cfg[df_cfg['usuario'].str.lower() == usuario].empty:
        return jsonify({'error': 'El usuario ya existe.'}), 400

    new_p = pd.DataFrame([{
        "nick": data.get("nick"), "nombre_real": nombre_real,
        "rol_principal": data.get("rol_principal"), "rol_secundario": data.get("rol_secundario", ""),
        "personaje": data.get("personaje"), "rango": data.get("rango"), "cargo": "Player",
        "estado": data.get("estado", "En Prueba"), "actividad": "Alta",
        "contacto": data.get("contacto", ""), "notas": ""
    }])
    pd.concat([df_roster, new_p], ignore_index=True).to_sql(f"{prefix}_roster", get_db(), if_exists='replace', index=False)

    new_u = pd.DataFrame([{"usuario": usuario, "password": data.get("password"), "rol": "jugador", "nombre_real": nombre_real}])
    pd.concat([df_cfg, new_u], ignore_index=True).to_sql(f"{prefix}_config", get_db(), if_exists='replace', index=False)

    return jsonify({'message': 'Registrado con éxito.'})

@app.route('/api/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/roster', methods=['GET', 'POST'])
def api_roster():
    prefix = get_prefix(session.get('division'))
    if request.method == 'GET':
        df = pd.read_sql_table(f"{prefix}_roster", get_db())
        return jsonify(df.to_dict(orient='records'))
    if request.method == 'POST' and session.get('role') == 'admin':
        pd.DataFrame(request.json).to_sql(f"{prefix}_roster", get_db(), if_exists='replace', index=False)
        return jsonify({'message': 'Roster actualizado'})

@app.route('/api/disciplina', methods=['GET', 'POST', 'DELETE'])
def api_disciplina():
    prefix = get_prefix(session.get('division'))
    if request.method == 'GET':
        df = pd.read_sql_table(f"{prefix}_disciplina", get_db())
        return jsonify(df.to_dict(orient='records'))
    if request.method == 'POST' and session.get('role') == 'admin':
        df_curr = pd.read_sql_table(f"{prefix}_disciplina", get_db())
        df_up = pd.concat([df_curr, pd.DataFrame([request.json])], ignore_index=True)
        df_up.to_sql(f"{prefix}_disciplina", get_db(), if_exists='replace', index=False)
        return jsonify({'message': 'Sanción registrada'})

@app.route('/api/capturas', methods=['GET', 'POST'])
def api_capturas():
    prefix = get_prefix(session.get('division'))
    if request.method == 'GET':
        df = pd.read_sql_table(f"{prefix}_capturas", get_db())
        return jsonify(df.to_dict(orient='records'))
    if request.method == 'POST':
        df_curr = pd.read_sql_table(f"{prefix}_capturas", get_db())
        nick = request.json.get('nick')
        df_filtered = df_curr[df_curr['nick'] != nick]
        df_up = pd.concat([df_filtered, pd.DataFrame([request.json])], ignore_index=True)
        df_up.to_sql(f"{prefix}_capturas", get_db(), if_exists='replace', index=False)
        return jsonify({'message': 'Captura guardada'})

@app.route('/api/reset_division', methods=['POST'])
def reset_division():
    password = request.json.get('password')
    prefix = get_prefix(session.get('division'))
    df_cfg = pd.read_sql_table(f"{prefix}_config", get_db())
    
    if df_cfg[(df_cfg['password'].astype(str) == password) & (df_cfg['rol'] == 'admin')].empty:
        return jsonify({'error': 'Contraseña incorrecta'}), 401

    pd.DataFrame(columns=["nick", "nombre_real", "rol_principal", "rol_secundario", "personaje", "rango", "cargo", "estado", "actividad", "contacto", "notas"]).to_sql(f"{prefix}_roster", get_db(), if_exists='replace', index=False)
    pd.DataFrame(columns=["fecha", "jugador", "tipo", "sancion", "detalles"]).to_sql(f"{prefix}_disciplina", get_db(), if_exists='replace', index=False)
    pd.DataFrame(columns=["nick", "imagen_b64"]).to_sql(f"{prefix}_capturas", get_db(), if_exists='replace', index=False)
    return jsonify({'message': 'División reseteada.'})

if __name__ == '__main__':
    app.run(debug=True)
