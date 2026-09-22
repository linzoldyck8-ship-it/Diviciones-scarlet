import os
import base64
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import pandas as pd
from sqlalchemy import create_engine, inspect

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "scarlet_secret_key_2026")

# --- CONEXIÓN A SUPABASE ---
SUPABASE_DB_URL = os.environ.get("SUPABASE_DB_URL", "postgresql://postgres:password@db.xxx.supabase.co:5432/postgres")

def get_engine():
    raw_url = SUPABASE_DB_URL
    if raw_url.startswith("postgresql://"):
        raw_url = raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    if ".supabase.co" in raw_url and "pooler.supabase.com" not in raw_url:
        raw_url = raw_url.replace("db.", "").replace(".supabase.co", ".pooler.supabase.com:6543")
    if "?sslmode=" not in raw_url:
        separator = "&" if "?" in raw_url else "?"
        raw_url = f"{raw_url}{separator}sslmode=require"
    return create_engine(raw_url)

engine = get_engine()

# --- DATOS DE JUEGOS Y DIVISIONES ---
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

def get_game_data(div_name):
    if "Overwatch" in div_name: return GAME_DATA["Overwatch"]
    if "CS" in div_name: return GAME_DATA["CS"]
    return GAME_DATA["Valorant"]

def get_table_prefix(div_name):
    return div_name.replace(" ", "_").lower()

def init_tables(prefix):
    inspector = inspect(engine)
    
    tb_roster = f"{prefix}_roster"
    if not inspector.has_table(tb_roster):
        df_init = pd.DataFrame(columns=[
            "id", "nick", "nombre_real", "rol_principal", "rol_secundario",
            "personaje", "rango", "cargo", "estado", "actividad", "contacto", "notas"
        ])
        df_init.to_sql(tb_roster, engine, if_exists='replace', index=False)

    tb_asis = f"{prefix}_asistencia"
    if not inspector.has_table(tb_asis):
        cols = ["nombre_real", "mes", "dias_habiles"] + [str(i) for i in range(1, 32)]
        pd.DataFrame(columns=cols).to_sql(tb_asis, engine, if_exists='replace', index=False)

    tb_disc = f"{prefix}_disciplina"
    if not inspector.has_table(tb_disc):
        pd.DataFrame(columns=["id", "fecha", "jugador", "tipo", "sancion", "detalles"]).to_sql(tb_disc, engine, if_exists='replace', index=False)

    tb_cfg = f"{prefix}_config"
    if not inspector.has_table(tb_cfg):
        df_cfg = pd.DataFrame([{"usuario": "admin", "password": "admin123", "rol": "admin", "nombre_real": "Administrador"}])
        df_cfg.to_sql(tb_cfg, engine, if_exists='replace', index=False)

    tb_bl = f"{prefix}_blacklist"
    if not inspector.has_table(tb_bl):
        pd.DataFrame(columns=["nombre_real", "motivo"]).to_sql(tb_bl, engine, if_exists='replace', index=False)

    tb_cap = f"{prefix}_capturas"
    if not inspector.has_table(tb_cap):
        pd.DataFrame(columns=["nick", "imagen_b64"]).to_sql(tb_cap, engine, if_exists='replace', index=False)

@app.route('/')
def index():
    return render_template('index.html', divisiones=DIVISIONES_DISPONIBLES)

@app.route('/division/<nombre>')
def seleccionar_division(nombre):
    if nombre not in DIVISIONES_DISPONIBLES:
        return redirect(url_for('index'))
    session['division'] = nombre
    init_tables(get_table_prefix(nombre))
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    division = session.get('division')
    if not division:
        return redirect(url_for('index'))
    
    user = session.get('user')
    role = session.get('role', 'invitado')
    game_info = get_game_data(division)
    
    return render_template('dashboard.html', division=division, user=user, role=role, game_info=game_info)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    division = session.get('division')
    prefix = get_table_prefix(division)
    tb_cfg = f"{prefix}_config"
    tb_bl = f"{prefix}_blacklist"

    usuario = data.get('usuario', '').strip().lower()
    password = data.get('password', '').strip()

    df_cfg = pd.read_sql_table(tb_cfg, engine)
    df_bl = pd.read_sql_table(tb_bl, engine)

    match = df_cfg[(df_cfg['usuario'].str.lower() == usuario) & (df_cfg['password'].astype(str) == password)]
    if match.empty:
        return jsonify({'error': 'Credenciales inválidas.'}), 401

    nombre_real = match.iloc[0]['nombre_real']
    rol = match.iloc[0]['rol']

    if rol != 'admin' and not df_bl[df_bl['nombre_real'].str.lower() == nombre_real.lower()].empty:
        return jsonify({'error': 'ACCESO DENEGADO: Te encuentras en la Lista Negra.'}), 403

    session['user'] = nombre_real
    session['role'] = rol
    return jsonify({'message': 'Login exitoso', 'role': rol, 'user': nombre_real})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json or {}
    division = session.get('division')
    prefix = get_table_prefix(division)
    
    nombre_real = data.get('nombre_real', '').strip()
    nick = data.get('nick', '').strip()
    usuario = data.get('usuario', '').strip().lower()
    password = data.get('password', '').strip()
    
    tb_roster = f"{prefix}_roster"
    tb_cfg = f"{prefix}_config"
    tb_bl = f"{prefix}_blacklist"

    df_bl = pd.read_sql_table(tb_bl, engine)
    df_cfg = pd.read_sql_table(tb_cfg, engine)
    df_roster = pd.read_sql_table(tb_roster, engine)

    if not df_bl[df_bl['nombre_real'].str.lower() == nombre_real.lower()].empty:
        return jsonify({'error': 'REGISTRO DENEGADO: El jugador está en la Lista Negra.'}), 403

    if not df_cfg[df_cfg['usuario'].str.lower() == usuario].empty:
        return jsonify({'error': 'El nombre de usuario ya está registrado.'}), 400

    nuevo_id = len(df_roster) + 1
    nueva_fila_roster = pd.DataFrame([{
        "id": nuevo_id, "nick": nick, "nombre_real": nombre_real,
        "rol_principal": data.get("rol_principal"), "rol_secundario": data.get("rol_secundario", ""),
        "personaje": data.get("personaje"), "rango": data.get("rango"), "cargo": "Player",
        "estado": data.get("estado", "En Prueba"), "actividad": "Alta",
        "contacto": data.get("contacto", ""), "notas": ""
    }])
    pd.concat([df_roster, nueva_fila_roster], ignore_index=True).to_sql(tb_roster, engine, if_exists='replace', index=False)

    nueva_fila_cfg = pd.DataFrame([{"usuario": usuario, "password": password, "rol": "jugador", "nombre_real": nombre_real}])
    pd.concat([df_cfg, nueva_fila_cfg], ignore_index=True).to_sql(tb_cfg, engine, if_exists='replace', index=False)

    return jsonify({'message': 'Registro completado exitosamente.'})

@app.route('/api/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/roster', methods=['GET', 'POST'])
def api_roster():
    division = session.get('division')
    prefix = get_table_prefix(division)
    tb_roster = f"{prefix}_roster"

    if request.method == 'GET':
        df = pd.read_sql_table(tb_roster, engine)
        return jsonify(df.to_dict(orient='records'))

    if request.method == 'POST':
        if session.get('role') != 'admin':
            return jsonify({'error': 'Acceso no autorizado'}), 403
        data = request.json
        df_new = pd.DataFrame(data)
        df_new.to_sql(tb_roster, engine, if_exists='replace', index=False)
        return jsonify({'message': 'Roster actualizado en Supabase.'})

@app.route('/api/reset_division', methods=['POST'])
def reset_division():
    data = request.json or {}
    password = data.get('password')
    division = session.get('division')
    prefix = get_table_prefix(division)
    tb_cfg = f"{prefix}_config"

    df_cfg = pd.read_sql_table(tb_cfg, engine)
    match = df_cfg[(df_cfg['password'].astype(str) == password) & (df_cfg['rol'] == 'admin')]

    if match.empty:
        return jsonify({'error': 'Contraseña de administrador incorrecta'}), 401

    pd.DataFrame(columns=["id", "nick", "nombre_real", "rol_principal", "rol_secundario", "personaje", "rango", "cargo", "estado", "actividad", "contacto", "notas"]).to_sql(f"{prefix}_roster", engine, if_exists='replace', index=False)
    pd.DataFrame(columns=["nombre_real", "mes", "dias_habiles"] + [str(i) for i in range(1, 32)]).to_sql(f"{prefix}_asistencia", engine, if_exists='replace', index=False)
    pd.DataFrame(columns=["id", "fecha", "jugador", "tipo", "sancion", "detalles"]).to_sql(f"{prefix}_disciplina", engine, if_exists='replace', index=False)
    
    return jsonify({'message': f'División {division} reseteada exitosamente.'})

if __name__ == '__main__':
    app.run(debug=True)
    
