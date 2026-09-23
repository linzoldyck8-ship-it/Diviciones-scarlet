import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "executive_esports_key_2026_secret")

# Variables de entorno en Render
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
    if not ign or not ign.strip():
        return "#"
    clean_ign = ign.strip()
    
    if "Valorant" in division:
        parts = clean_ign.split("#")
        if len(parts) == 2:
            return f"https://tracker.gg/valorant/profile/riot/{parts[0]}%23{parts[1]}/overview"
        return f"https://tracker.gg/valorant/profile/riot/{clean_ign}/overview"
    elif "Overwatch" in division:
        parts = clean_ign.split("#")
        if len(parts) == 2:
            return f"https://overwatch.tracker.gg/overwatch/profile/battlenet/{parts[0]}-{parts[1]}/overview"
        return f"https://overwatch.tracker.gg/overwatch/profile/battlenet/{clean_ign}/overview"
    elif "Counter" in division:
        return f"https://csstats.gg/player/{clean_ign}"
    return "#"

@app.route("/")
def index():
    if "user_id" in session:
        # Redireccionar al departamento autorizado según rol
        if session.get("role") == "admin":
            target_div = session.get("admin_division", DIVISIONS[0])
            if target_div == "TODAS" or not target_div:
                target_div = DIVISIONS[0]
            return redirect(url_for("division_dashboard", division_name=target_div))
        else:
            return redirect(url_for("division_dashboard", division_name=session.get("division", DIVISIONS[0])))

    return render_template("index.html", divisions=DIVISIONS)

@app.route("/register", methods=["POST"])
def register():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password")
    full_name = request.form.get("full_name", "").strip()
    discord_tag = request.form.get("discord_tag", "").strip()
    division = request.form.get("division")
    game_ign = request.form.get("game_ign", "").strip()
    main_role = request.form.get("main_role", "").strip()
    favorite_agent = request.form.get("favorite_agent", "").strip()
    
    account_type = request.form.get("account_type", "player")
    admin_division = request.form.get("admin_division") if account_type == "admin" else None

    # Hashing seguro de contraseña
    password_hash = generate_password_hash(password)
    tracker_url = build_tracker_url(division, game_ign)

    data = {
        "email": email,
        "password_hash": password_hash,
        "full_name": full_name,
        "discord_tag": discord_tag,
        "division": division,
        "game_ign": game_ign,
        "main_role": main_role,
        "favorite_agent": favorite_agent,
        "roster_status": "Pendiente",
        "attendance": 100,
        "notes": "Registro corporativo completado.",
        "tracker_url": tracker_url,
        "role": account_type,
        "admin_division": admin_division
    }

    try:
        supabase.table("profiles").insert(data).execute()
        flash("Solicitud de acceso enviada correctamente. Proceda a iniciar sesión.", "success")
    except Exception as e:
        flash(f"Error al registrar cuenta: {str(e)}", "danger")

    return redirect(url_for("index"))

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password")

    try:
        res = supabase.table("profiles").select("*").eq("email", email).execute()
        users = res.data

        if users and len(users) > 0:
            user = users[0]
            if check_password_hash(user["password_hash"], password):
                session["user_id"] = user["id"]
                session["user_name"] = user["full_name"]
                session["role"] = user.get("role", "player")
                session["division"] = user.get("division")
                session["admin_division"] = user.get("admin_division")
                
                flash(f"Bienvenido de nuevo, {user['full_name']}.", "success")
                
                if session["role"] == "admin":
                    target_div = session.get("admin_division", DIVISIONS[0])
                    if target_div == "TODAS":
                        target_div = DIVISIONS[0]
                    return redirect(url_for("division_dashboard", division_name=target_div))
                else:
                    return redirect(url_for("division_dashboard", division_name=session["division"]))
            else:
                flash("Credenciales no válidas. Contraseña incorrecta.", "danger")
        else:
            flash("No existe un perfil registrado con este correo.", "danger")
    except Exception as e:
        flash(f"Error al procesar la autenticación: {str(e)}", "danger")

    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión corporativa cerrada exitosamente.", "info")
    return redirect(url_for("index"))

# DASHBOARD POR DEPARTAMENTO / DIVISIÓN CON CONTROL RIGUROSO
@app.route("/division/<path:division_name>")
def division_dashboard(division_name):
    if "user_id" not in session:
        flash("Acceso restringido. Por favor inicie sesión.", "danger")
        return redirect(url_for("index"))

    user_role = session.get("role", "player")
    user_division = session.get("division")
    admin_division = session.get("admin_division")

    # CONTROL ESTRICTO DE ACCESO POR DIVISIÓN
    if user_role == "admin":
        if admin_division != "TODAS" and admin_division != division_name:
            flash(f"ACCESO RESTRINGIDO: Su cuenta de Administrador está asignada exclusivamente a '{admin_division}'.", "danger")
            return redirect(url_for("division_dashboard", division_name=admin_division))
    else:
        if user_division != division_name:
            flash(f"ACCESO NO AUTORIZADO: Su perfil pertenece al departamento '{user_division}'.", "warning")
            return redirect(url_for("division_dashboard", division_name=user_division))

    # Cargar miembros de la división activa
    try:
        res = supabase.table("profiles").select("*").eq("division", division_name).execute()
        members = res.data if res.data else []
    except Exception as e:
        members = []
        flash(f"Error al cargar registros del departamento: {str(e)}", "danger")

    # Métricas del Departamento
    total_members = len(members)
    active_titulares = sum(1 for m in members if m.get("roster_status") == "Titular")
    avg_attendance = round(sum(float(m.get("attendance", 100)) for m in members) / total_members, 1) if total_members > 0 else 100.0

    return render_template(
        "dashboard.html",
        division_name=division_name,
        members=members,
        divisions=DIVISIONS,
        total_members=total_members,
        active_titulares=active_titulares,
        avg_attendance=avg_attendance,
        is_current_admin=(user_role == "admin" and (admin_division == division_name or admin_division == "TODAS"))
    )

@app.route("/admin/update-member", methods=["POST"])
def update_member():
    if "user_id" not in session or session.get("role") != "admin":
        flash("Acción no autorizada.", "danger")
        return redirect(url_for("index"))

    member_id = request.form.get("member_id")
    target_division = request.form.get("target_division")
    admin_division = session.get("admin_division")

    if admin_division != "TODAS" and admin_division != target_division:
        flash("ACCESO RESTRINGIDO: No tiene permisos de edición sobre esta división.", "danger")
        return redirect(url_for("division_dashboard", division_name=admin_division))

    roster_status = request.form.get("roster_status")
    attendance = float(request.form.get("attendance", 100))
    notes = request.form.get("notes")

    update_payload = {
        "roster_status": roster_status,
        "attendance": attendance,
        "notes": notes
    }

    try:
        supabase.table("profiles").update(update_payload).eq("id", member_id).execute()
        flash("Ficha del integrante actualizada con éxito.", "success")
    except Exception as e:
        flash(f"Error al guardar los cambios: {str(e)}", "danger")

    return redirect(url_for("division_dashboard", division_name=target_division))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
