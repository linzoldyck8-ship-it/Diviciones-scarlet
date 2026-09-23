import os
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine, text
from supabase import create_client

app = Flask(__name__)
app.secret_key = "scarlet_super_secret_key"  # Requerido para usar flash()

# ---------------------------------------------------------
# VARIABLES DE ENTORNO (Render / Supabase)
# ---------------------------------------------------------
DB_URL = os.getenv("DATABASE_URL", "")
if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# ---------------------------------------------------------
# CONEXIONES
# ---------------------------------------------------------
# SQLAlchemy Engine
engine = create_engine(DB_URL, pool_pre_ping=True) if DB_URL else None

# Supabase Storage Client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def init_db_schema(table_name: str):
    """Crea la tabla de la división si no existe."""
    if not engine: return
    schema_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id SERIAL PRIMARY KEY,
        nickname VARCHAR(100) NOT NULL,
        rol VARCHAR(50),
        rango VARCHAR(50),
        estado VARCHAR(50) DEFAULT 'Titular'
    );
    """
    with engine.begin() as conn:
        conn.execute(text(schema_sql))

# ---------------------------------------------------------
# RUTAS DE NAVEGACIÓN
# ---------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    division_slug = request.args.get('division', 'valorant_a')
    table_name = f"roster_{division_slug}"
    
    init_db_schema(table_name)
    
    # Obtener el roster actual
    roster_data = []
    if engine:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {table_name} ORDER BY id ASC"))
            roster_data = [row._asdict() for row in result]
            
    division_name = division_slug.replace('_', ' ').title()
    return render_template('dashboard.html', 
                           division_name=division_name, 
                           division_slug=division_slug, 
                           roster=roster_data)

# ---------------------------------------------------------
# RUTAS DE ACCIÓN (POST)
# ---------------------------------------------------------
@app.route('/add_player', methods=['POST'])
def add_player():
    division_slug = request.form.get('division')
    nickname = request.form.get('nickname')
    rol = request.form.get('rol')
    rango = request.form.get('rango')
    table_name = f"roster_{division_slug}"
    
    if engine and nickname:
        with engine.begin() as conn:
            query = text(f"""
                INSERT INTO {table_name} (nickname, rol, rango, estado) 
                VALUES (:nick, :rol, :rango, 'Titular')
            """)
            conn.execute(query, {"nick": nickname, "rol": rol, "rango": rango})
        flash(f"Jugador {nickname} agregado exitosamente.", "success")
        
    return redirect(url_for('dashboard', division=division_slug))

@app.route('/upload_evidence', methods=['POST'])
def upload_evidence():
    division_slug = request.form.get('division')
    file = request.files.get('file')
    
    if file and file.filename != '' and supabase:
        try:
            bucket_name = "capturas"
            file_path = f"evidencias/{division_slug}/{file.filename}"
            file_bytes = file.read()
            
            # Subir a Supabase Storage
            supabase.storage.from_(bucket_name).upload(
                path=file_path,
                file=file_bytes,
                file_options={"content-type": file.content_type, "upsert": "true"}
            )
            flash("Captura subida exitosamente a Supabase Storage.", "success")
        except Exception as e:
            flash(f"Error al subir: {str(e)}", "danger")
    else:
        flash("No se seleccionó archivo o faltan credenciales de Supabase.", "warning")
        
    return redirect(url_for('dashboard', division=division_slug))

if __name__ == '__main__':
    # Ejecución local en desarrollo
    app.run(debug=True, port=5000)
