import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from supabase import create_client, Client

app = Flask(__name__)
# Clave secreta para manejo de sesiones en Flask
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "esports_secret_key_2026_render")

# Variables de Supabase (Configúralas en las Variables de Entorno de Render)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://tu-proyecto.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "tu-anon-key-de-supabase")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

DIVISIONS = [
    "Valorant A",
    "Valorant B",
    "Valorant C",
    "Valorant Femenino",
    "Overwatch A",
    "Overwatch B",
    "Counter Strike"
]

def build_tracker_url(division, ign):
    if not ign:
        return "#"
    ign_clean = ign.replace("#", "%23")
    
    if "Valorant" in division:
        parts = ign.split("#")
        if len(parts) == 2:
            return f"https://tracker.gg/valorant/profile/riot/{parts[0]}%23{parts[1]}/overview"
        return f"https://tracker.gg/valorant/profile/riot/{ign_clean}/overview"
    elif "Overwatch" in division:
        parts = ign.split("#")
        if len(parts) == 2:
            return f"https://overwatch.tracker.gg/overwatch/profile/battlenet/{parts[0]}-{parts[1]}/overview"
        return f"https://overwatch.tracker.gg/overwatch/profile/battlenet/{ign_clean}/overview"
    elif "Counter" in division:
        return f"https://csstats.gg/player/{ign}"
    return "#"

@app.route("/")
def index():
    selected_division = request.args.get("division", "Valorant A")
    
    # Obtener los jugadores registrados en la división seleccionada
    try:
        response = supabase.table("profiles").select("*").eq("division", selected_division).execute()
        players = response.data if response.data else []
    except Exception as e:
        players = []
        flash(f"Error al conectar con la base de datos: {str(e)}", "danger")

    return render_template(
        "index.html", 
        players=players, 
        selected_division=selected_division, 
        divisions=DIVISIONS
    )

@app.route("/register", methods=["POST"])
def register():
    email = request.form.get("email")
    password = request.form.get("password")
    full_name = request.form.get("full_name")
    discord_tag = request.form.get("discord_tag")
    division = request.form.get("division")
    game_ign = request.form.get("game_ign")
    main_role = request.form.get("main_role")
    favorite_agent = request.form.get("favorite_agent")
    is_admin = request.form.get("is_admin") == "on"
    admin_division = request.form.get("admin_division", division)

    tracker_url = build_tracker_url(division, game_ign)

    data = {
        "email": email,
        "password_hash": password,
        "full_name": full_name,
        "discord_tag": discord_tag,
        "division": division,
        "game_ign": game_ign,
        "main_role": main_role,
        "favorite_agent": favorite_agent,
        "roster_status": "Pendiente",
        "attendance": 100,
        "notes": "Nuevo registro.",
        "tracker_url": tracker_url,
        "is_admin": is_admin,
        "admin_division": admin_division if is_admin else None
    }

    try:
        supabase.table("profiles").insert(data).execute()
        flash("¡Registro completado exitosamente! Ahora puedes iniciar sesión.", "success")
    except Exception as e:
        flash(f"Error al registrar usuario: {str(e)}", "danger")

    return redirect(url_for("index", division=division))

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    try:
        response = supabase.table("profiles").select("*").eq("email", email).eq("password_hash", password).execute()
        users = response.data

        if users and len(users) > 0:
            user = users[0]
            session["user_id"] = user["id"]
            session["user_name"] = user["full_name"]
            session["is_admin"] = user.get("is_admin", False)
            session["admin_division"] = user.get("admin_division")
            session["division"] = user.get("division")
            flash(f"Bienvenido de nuevo, {user['full_name']}", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Correo electrónico o contraseña incorrectos.", "danger")
    except Exception as e:
        flash(f"Error en inicio de sesión: {str(e)}", "danger")

    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión.", "info")
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Por favor inicia sesión para acceder al panel.", "warning")
        return redirect(url_for("index"))

    user_id = session["user_id"]
    is_admin = session.get("is_admin", False)
    admin_division = session.get("admin_division")

    # Obtener información del usuario logueado
    res_user = supabase.table("profiles").select("*").eq("id", user_id).execute()
    current_user = res_user.data[0] if res_user.data else None

    # Obtener lista de jugadores que puede gestionar el Admin
    players_to_manage = []
    if is_admin:
        if admin_division == "TODAS":
            res_players = supabase.table("profiles").select("*").execute()
        else:
            res_players = supabase.table("profiles").select("*").eq("division", admin_division).execute()
        players_to_manage = res_players.data if res_players.data else []

    return render_template(
        "dashboard.html",
        current_user=current_user,
        players_to_manage=players_to_manage,
        admin_division=admin_division,
        divisions=DIVISIONS
    )

@app.route("/admin/update-player", methods=["POST"])
def update_player():
    if not session.get("is_admin"):
        flash("No tienes permisos de administrador.", "danger")
        return redirect(url_for("index"))

    player_id = request.form.get("player_id")
    roster_status = request.form.get("roster_status")
    attendance = float(request.form.get("attendance", 100))
    notes = request.form.get("notes")

    update_data = {
        "roster_status": roster_status,
        "attendance": attendance,
        "notes": notes
    }

    try:
        supabase.table("profiles").update(update_data).eq("id", player_id).execute()
        flash("Datos del jugador actualizados correctamente.", "success")
    except Exception as e:
        flash(f"Error al actualizar jugador: {str(e)}", "danger")

    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
