import os
from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "clave-secreta-esports-123")

# Credenciales de Supabase desde las variables de entorno de Render
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# Inicializar cliente de Supabase
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Error al conectar con Supabase: {e}")

@app.route('/')
def dashboard():
    jugadores = []
    if supabase:
        try:
            # Obtener todos los jugadores de Supabase ordenados por fecha
            response = supabase.table('jugadores').select('*').order('created_at', desc=True).execute()
            jugadores = response.data
        except Exception as e:
            print(f"Error al obtener jugadores: {e}")

    return render_template('dashboard.html', jugadores=jugadores)

@app.route('/registro', methods=['POST'])
def registrar_jugador():
    if not supabase:
        return "Error: Supabase no está configurado correctamente en las variables de entorno.", 500

    # Obtener los datos enviados desde el HTML
    nick = request.form.get('nick')
    nombre_real = request.form.get('nombre_real')
    juego = request.form.get('juego')
    rol_principal = request.form.get('rol_principal')
    rol_secundario = request.form.get('rol_secundario')
    personaje = request.form.get('personaje')
    rango = request.form.get('rango')
    
    # Formatear el contacto
    tipo_contacto = request.form.get('tipo_contacto')
    contacto_valor = request.form.get('contacto_valor')
    contacto_completo = f"{tipo_contacto}: {contacto_valor}" if tipo_contacto and contacto_valor else ""

    notas = request.form.get('notas', '')

    datos = {
        "nick": nick,
        "nombre_real": nombre_real,
        "juego": juego,
        "rol_principal": rol_principal,
        "rol_secundario": rol_secundario,
        "personaje": personaje,
        "rango": rango,
        "contacto": contacto_completo,
        "cargo": "Jugador",
        "estado": "Activo",
        "actividad": "Al día",
        "notas": notas
    }

    try:
        supabase.table('jugadores').insert(datos).execute()
    except Exception as e:
        print(f"Error insertando datos: {e}")

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
