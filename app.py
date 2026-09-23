import os
import calendar
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "executive_esports_key_2026_secret")

# --- CONFIGURACIÓN DE SUPABASE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://vlwsrjptvhbthcbqzmws.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZsd3NyanB0dmhidGhjYnF6bXdzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk4Mzc4MzgsImV4cCI6MjEwNTQxMzgzOH0.9l369_HN_QsKgaOSKFDnRqrD6xtnsjccQvB-Tl8WqUU")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Error al conectar con Supabase: {e}")
    supabase = None

DIVISIONS = [
    "Valorant A",
    "Valorant B",
    "Valorant C",
    "Valorant Femenino",
    "Overwatch A",
    "Overwatch B",
    "Counter Strike"
]

MONTH_NAMES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

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

# RUTA PRINCIPAL: Muestra la nueva pantalla de bienvenida
@app.route("/")
def index():
    if "user_id" in session:
        if session.get("role") == "admin":
            target_div = session.get("admin_division", DIVISIONS[0])
            if target_div == "TODAS" or not target_div:
                target_div = DIVISIONS[0]
            return redirect(url_for("division_dashboard", division_name=target_div))
        else:
            return redirect(url_for("division_dashboard", division_name=session.get("division", DIVISIONS[0])))

    return render_template("welcome.html")

# RUTA DEL PORTAL: Muestra el Login y Registro (la pantalla anterior)
@app.route("/portal")
def portal():
    if "user_id" in session:
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
    if not supabase:
        flash("Error: No hay conexión con Supabase.", "danger")
        return redirect(url_for("portal"))

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password")
    full_name = request.form.get("full_name", "").strip()
    discord_tag = request.form.get("discord_tag", "").strip()
    division = request.form.get("division")
    game_ign = request.form.get("game_ign", "").strip()
    main_role = request.form.get("main_role", "").strip()
    favorite_agent = request.form.get("favorite_agent", "").strip()

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
        "notes": "Registro completado.",
        "tracker_url": tracker_url,
        "role": "player",
        "admin_division": None
    }

    try:
        supabase.table("profiles").insert(data).execute()
        flash("Registro de jugador exitoso. Procede a iniciar sesión.", "success")
    except Exception as e:
        flash(f"Error al registrar cuenta: {str(e)}", "danger")

    return redirect(url_for("portal"))

@app.route("/login", methods=["POST"])
def login():
    if not supabase:
        flash("Error: No hay conexión con Supabase.", "danger")
        return redirect(url_for("portal"))

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
                
                flash(f"Sesión iniciada correctamente. Bienvenido {user['full_name']}.", "success")
                
                if session["role"] == "admin":
                    target_div = session.get("admin_division", DIVISIONS[0])
                    if target_div == "TODAS" or not target_div:
                        target_div = DIVISIONS[0]
                    return redirect(url_for("division_dashboard", division_name=target_div))
                else:
                    return redirect(url_for("division_dashboard", division_name=session["division"]))
            else:
                flash("Contraseña incorrecta.", "danger")
        else:
            flash("El correo no se encuentra registrado.", "danger")
    except Exception as e:
        flash(f"Error al autenticar: {str(e)}", "danger")

    return redirect(url_for("portal"))

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("index"))

@app.route("/division/<path:division_name>")
def division_dashboard(division_name):
    if "user_id" not in session:
        flash("Debe iniciar sesión para ver los registros.", "danger")
        return redirect(url_for("portal"))

    if not supabase:
        flash("Error de conexión con Supabase.", "danger")
        return redirect(url_for("portal"))

    user_role = session.get("role", "player")
    user_division = session.get("division")
    admin_division = session.get("admin_division")

    if user_role == "admin":
        if admin_division != "TODAS" and admin_division != division_name:
            flash(f"RESTRICCIÓN DE ADMIN: Tu cuenta está asignada a la división '{admin_division}'.", "warning")
            return redirect(url_for("division_dashboard", division_name=admin_division))
    else:
        if user_division != division_name:
            flash(f"ACCESO RESTRINGIDO: Perteneces a la división '{user_division}'.", "warning")
            return redirect(url_for("division_dashboard", division_name=user_division))

    # Obtener imagen de la división actual
    division_image = ""
    try:
        div_res = supabase.table("division_config").select("image_url").eq("division_name", division_name).execute()
        if div_res.data and len(div_res.data) > 0:
            division_image = div_res.data[0].get("image_url", "")
    except Exception as e:
        print("Aviso: No se pudo cargar la imagen de la división", e)

    # Configuración del mes y año seleccionados
    now = datetime.now()
    selected_year = request.args.get("year", now.year, type=int)
    selected_month = request.args.get("month", now.month, type=int)

    _, num_days = calendar.monthrange(selected_year, selected_month)
    days_list = list(range(1, num_days + 1))

    try:
        res = supabase.table("profiles").select("*").eq("division", division_name).execute()
        members = res.data if res.data else []
    except Exception as e:
        members = []
        flash(f"Error al cargar datos: {str(e)}", "danger")

    # Cargar matriz de asistencia para el mes seleccionado
    start_date = f"{selected_year:04d}-{selected_month:02d}-01"
    end_date = f"{selected_year:04d}-{selected_month:02d}-{num_days:02d}"

    attendance_data = {}
    try:
        att_res = supabase.table("attendance_logs")\
            .select("*")\
            .gte("date", start_date)\
            .lte("date", end_date)\
            .execute()

        for log in (att_res.data or []):
            p_id = str(log["profile_id"])
            log_day = int(log["date"].split("-")[2])
            if p_id not in attendance_data:
                attendance_data[p_id] = {}
            attendance_data[p_id][log_day] = log["status"]
    except Exception as e:
        print("Aviso: No se pudieron obtener los registros de asistencia:", e)

    # Procesar métricas por jugador
    for m in members:
        p_id = str(m["id"])
        m_logs = attendance_data.get(p_id, {})
        m["daily_status"] = m_logs

        p_cnt = sum(1 for s in m_logs.values() if s == "P")
        a_cnt = sum(1 for s in m_logs.values() if s == "A")
        j_cnt = sum(1 for s in m_logs.values() if s == "J")
        t_cnt = sum(1 for s in m_logs.values() if s == "T")

        total_eval = p_cnt + a_cnt + j_cnt + t_cnt
        m["total_eval_days"] = total_eval

        if total_eval > 0:
            score = (p_cnt * 100.0) + (j_cnt * 100.0) + (t_cnt * 80.0)
            m["monthly_attendance_pct"] = round(score / total_eval, 1)
        else:
            m["monthly_attendance_pct"] = 100.0

    total_members = len(members)
    active_titulares = sum(1 for m in members if m.get("roster_status") == "Titular")
    avg_attendance = round(sum(m["monthly_attendance_pct"] for m in members) / total_members, 1) if total_members > 0 else 100.0

    is_super_admin = (user_role == "admin" and admin_division == "TODAS")
    is_current_admin = (user_role == "admin" and (admin_division == division_name or admin_division == "TODAS"))

    return render_template(
        "dashboard.html",
        division_name=division_name,
        members=members,
        divisions=DIVISIONS,
        total_members=total_members,
        active_titulares=active_titulares,
        avg_attendance=avg_attendance,
        is_current_admin=is_current_admin,
        is_super_admin=is_super_admin,
        selected_year=selected_year,
        selected_month=selected_month,
        selected_month_name=MONTH_NAMES.get(selected_month, ""),
        month_names=MONTH_NAMES,
        days_list=days_list,
        division_image=division_image
    )

# NUEVA RUTA PARA GUARDAR LA IMAGEN DE LA DIVISIÓN
@app.route("/admin/update-division-image", methods=["POST"])
def update_division_image():
    if "user_id" not in session or session.get("role") != "admin":
        flash("Acción denegada.", "danger")
        return redirect(url_for("portal"))

    target_division = request.form.get("target_division")
    image_url = request.form.get("image_url", "").strip()

    try:
        supabase.table("division_config").upsert({
            "division_name": target_division,
            "image_url": image_url
        }, on_conflict="division_name").execute()
        flash("Imagen de la división actualizada correctamente.", "success")
    except Exception as e:
        flash(f"Error al actualizar la imagen: {str(e)}", "danger")

    return redirect(url_for("division_dashboard", division_name=target_division))

# GUARDAR MATRIZ COMPLETA DE ASISTENCIA (SOLO ADMINS)
@app.route("/admin/save-attendance-matrix", methods=["POST"])
def save_attendance_matrix():
    if "user_id" not in session or session.get("role") != "admin":
        flash("Acción denegada: Solo los administradores pueden modificar la asistencia.", "danger")
        return redirect(url_for("portal"))

    target_division = request.form.get("target_division")
    year = int(request.form.get("year"))
    month = int(request.form.get("month"))

    _, num_days = calendar.monthrange(year, month)

    res = supabase.table("profiles").select("id").eq("division", target_division).execute()
    members = res.data or []

    upsert_records = []
    for m in members:
        p_id = str(m["id"])
        for day in range(1, num_days + 1):
            field_name = f"att_{p_id}_{day}"
            status = request.form.get(field_name, "").strip()
            if status in ["P", "A", "J", "T"]:
                date_str = f"{year:04d}-{month:02d}-{day:02d}"
                upsert_records.append({
                    "profile_id": p_id,
                    "date": date_str,
                    "status": status
                })

    try:
        if upsert_records:
            supabase.table("attendance_logs").upsert(upsert_records, on_conflict="profile_id,date").execute()
        flash("Registro de asistencia guardado correctamente.", "success")
    except Exception as e:
        flash(f"Error al guardar la asistencia: {str(e)}", "danger")

    return redirect(url_for("division_dashboard", division_name=target_division, year=year, month=month))

@app.route("/admin/update-member", methods=["POST"])
def update_member():
    if "user_id" not in session or session.get("role") != "admin":
        flash("Acción denegada: Solo los administradores pueden modificar información.", "danger")
        return redirect(url_for("portal"))

    member_id = request.form.get("member_id")
    target_division = request.form.get("target_division")
    game_ign = request.form.get("game_ign", "").strip()
    roster_status = request.form.get("roster_status")
    notes = request.form.get("notes", "").strip()

    new_tracker_url = build_tracker_url(target_division, game_ign)

    update_payload = {
        "game_ign": game_ign,
        "roster_status": roster_status,
        "notes": notes,
        "tracker_url": new_tracker_url
    }

    try:
        supabase.table("profiles").update(update_payload).eq("id", member_id).execute()
        flash("Ficha del jugador actualizada correctamente.", "success")
    except Exception as e:
        flash(f"Error al actualizar la ficha: {str(e)}", "danger")

    return redirect(url_for("division_dashboard", division_name=target_division))

@app.route("/admin/update-role", methods=["POST"])
def update_role():
    if "user_id" not in session or session.get("role") != "admin" or session.get("admin_division") != "TODAS":
        flash("Acción denegada: Solo el Super Administrador puede gestionar permisos.", "danger")
        return redirect(url_for("portal"))

    member_id = request.form.get("member_id")
    target_division = request.form.get("target_division")
    new_role_type = request.form.get("role_type")

    if new_role_type == "player":
        role_val = "player"
        admin_div_val = None
    elif new_role_type == "admin":
        role_val = "admin"
        admin_div_val = request.form.get("assigned_admin_division")
    elif new_role_type == "superadmin":
        role_val = "admin"
        admin_div_val = "TODAS"
    else:
        role_val = "player"
        admin_div_val = None

    update_payload = {
        "role": role_val,
        "admin_division": admin_div_val
    }

    try:
        supabase.table("profiles").update(update_payload).eq("id", member_id).execute()
        flash("Permisos actualizados correctamente.", "success")
    except Exception as e:
        flash(f"Error al actualizar permisos: {str(e)}", "danger")

    return redirect(url_for("division_dashboard", division_name=target_division))

@app.route("/admin/delete-member", methods=["POST"])
def delete_member():
    if "user_id" not in session or session.get("role") != "admin":
        flash("Acción denegada.", "danger")
        return redirect(url_for("portal"))

    member_id = request.form.get("member_id")
    target_division = request.form.get("target_division")

    try:
        supabase.table("profiles").delete().eq("id", member_id).execute()
        flash("Integrante eliminado de la división.", "info")
    except Exception as e:
        flash(f"Error al eliminar: {str(e)}", "danger")

    return redirect(url_for("division_dashboard", division_name=target_division))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
