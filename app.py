import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Scarlet Multi-Divisiones", page_icon="🔥", layout="wide")

URL_LOGO_EQUIPO = "https://cdn.discordapp.com/attachments/1272709315039592469/1275623434063314984/SCARLET.png?ex=6aaf32e6&is=6aade166&hm=4889e788d8f71a5e470db02c4c8f42b95fb19fcdce9be96f7fabab8b6fec25e4&"

LOGOS_DIVISIONES = {
    "Valorant A": "https://images.seeklogo.com/logo-png/37/1/valorant-logo-png_seeklogo-379976.png",
    "Valorant B": "https://images.seeklogo.com/logo-png/37/1/valorant-logo-png_seeklogo-379976.png",
    "Valorant C": "https://images.seeklogo.com/logo-png/37/1/valorant-logo-png_seeklogo-379976.png",
    "Valorant Femenino": "https://images.seeklogo.com/logo-png/37/1/valorant-logo-png_seeklogo-379976.png",
    "Overwatch A": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/55/Overwatch_circle_logo.svg/1280px-Overwatch_circle_logo.svg.png",
    "Overwatch B": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/55/Overwatch_circle_logo.svg/1280px-Overwatch_circle_logo.svg.png",
    "CS": "https://images.seeklogo.com/logo-png/62/1/counter-strike-logo-png_seeklogo-622731.png"
}

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp { background: linear-gradient(135deg, #0b1017 0%, #111a24 100%); color: #e2e8f0; font-family: 'Inter', sans-serif; }
    .hero-container {
        border-radius: 12px; display: flex; flex-direction: column; align-items: center;
        justify-content: center; text-align: center; padding: 30px;
        border: 1px solid rgba(255, 70, 85, 0.3); box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6); margin-bottom: 25px;
    }
    h1, h2, h3 { color: #ffffff !important; font-weight: 700; }
    h1 {
        background: linear-gradient(90deg, #ffffff 0%, #ff4655 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.3rem;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #16222d 0%, #0f1923 100%);
        border: 1px solid rgba(255, 70, 85, 0.3); padding: 15px; border-radius: 8px;
    }
    div[data-testid="stMetricValue"] { color: #ff4655 !important; font-weight: 700; }
    .division-card {
        width: 100%; border-radius: 10px; border: 1px solid rgba(255, 70, 85, 0.4);
        padding: 20px 10px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 110px;
    }
    </style>
""", unsafe_allow_html=True)

DATOS_INICIALES_ROSTER = pd.DataFrame({
    "ID": [1, 2, 3, 4, 5],
    "Nick / ID": ["Player1#TAG", "Player2#TAG", "Player3#TAG", "Player4#TAG", "Player5#TAG"],
    "Nombre Real": ["Juan", "Carlos", "Mateo", "Lucas", "Gabriel"],
    "Rol Principal": ["Duelista", "Iniciador", "Controlador", "Centinela", "Flex"],
    "Rol Secundario": ["Flex", "Duelista", "Iniciador", "Controlador", "Centinela"],
    "Personajes / Agentes": ["Jett", "Sova", "Omen", "Cypher", "Breach"],
    "Rango / Cima": ["Inmortal 1", "Ascendente 3", "Diamante 2", "Inmortal 2", "Radiante"],
    "Cargo en Equipo": ["Capitan", "Player", "Player", "Player", "Sub capitan"],
    "Estado": ["Titular", "Titular", "Titular", "Titular", "Banca"],
    "Actividad": ["Alta", "Alta", "Media", "Alta", "Alta"],
    "Contacto / Discord": ["discord1", "discord2", "discord3", "discord4", "discord5"],
    "Notas / Observaciones": ["", "", "", "", ""]
})

DATOS_INICIALES_CONFIG = pd.DataFrame({
    "Usuario": ["admin"],
    "Contraseña": ["admin123"],
    "Rol": ["admin"],
    "Nombre Real Vinculado": [""]
})

DATOS_SUPER_ADMIN_INIT = pd.DataFrame({
    "Usuario": ["superadmin"],
    "Contraseña": ["admin123"],
    "Rol": ["superadmin"]
})

DIVISIONES_DISPONIBLES = [
    "Valorant A", "Valorant B", "Valorant C", 
    "Valorant Femenino", "Overwatch A", "Overwatch B", "CS"
]

# --- CONEXIÓN A GOOGLE SHEETS ---
@st.cache_resource
def conectar_google_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open("crea el proyecto en formato hoja de calculo como...")
        return spreadsheet
    except Exception as e:
        st.error(f"Error conectando a Google Sheets: {e}")
        return None

spreadsheet = conectar_google_sheets()

# Función auxiliar robusta para obtener o crear hojas al vuelo sin errores de API
def obtener_o_crear_hoja(nombre_hoja, df_init):
    if spreadsheet is None: return None
    try:
        return spreadsheet.worksheet(nombre_hoja)
    except:
        ws = spreadsheet.add_worksheet(title=nombre_hoja, rows="100", cols="20")
        if not df_init.empty:
            ws.update([df_init.columns.values.tolist()] + df_init.values.tolist())
        else:
            ws.update([df_init.columns.values.tolist()])
        return ws

def obtener_hojas_division(division_nombre):
    prefix = division_nombre.replace(" ", "_")
    return (
        obtener_o_crear_hoja(f"{prefix}_Roster", DATOS_INICIALES_ROSTER),
        obtener_o_crear_hoja(f"{prefix}_Asistencia", pd.DataFrame(columns=["Nombre Real", "Mes", "Días Hábiles"] + [str(i) for i in range(1, 32)])),
        obtener_o_crear_hoja(f"{prefix}_Disciplina", pd.DataFrame(columns=["Fecha", "Jugador", "Tipo", "Sanción", "Detalles"])),
        obtener_o_crear_hoja(f"{prefix}_Config", DATOS_INICIALES_CONFIG)
    )

def guardar_en_sheet(sheet_obj, df):
    if sheet_obj is not None:
        try:
            df_clean = df.fillna("")
            sheet_obj.clear()
            sheet_obj.update([df_clean.columns.values.tolist()] + df_clean.values.tolist())
        except Exception as e:
            st.error(f"Error al sincronizar: {e}")

def cargar_roster_fresco(sheet_roster):
    try:
        data = sheet_roster.get_all_records()
        return pd.DataFrame(data) if data else DATOS_INICIALES_ROSTER.copy()
    except:
        return DATOS_INICIALES_ROSTER.copy()

def cargar_incidencias_fresco(sheet_disciplina):
    try:
        data = sheet_disciplina.get_all_records()
        df = pd.DataFrame(data)
        if df.empty or "Fecha" not in df.columns:
            return pd.DataFrame(columns=["Fecha", "Jugador", "Tipo", "Sanción", "Detalles"])
        return df
    except:
        return pd.DataFrame(columns=["Fecha", "Jugador", "Tipo", "Sanción", "Detalles"])

def cargar_configuracion_fresco(sheet_config):
    try:
        data = sheet_config.get_all_records()
        return pd.DataFrame(data) if data else DATOS_INICIALES_CONFIG.copy()
    except:
        return DATOS_INICIALES_CONFIG.copy()

# --- ESTADOS DE LA SESIÓN ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'rol_usuario' not in st.session_state: st.session_state.rol_usuario = None
if 'nombre_usuario' not in st.session_state: st.session_state.nombre_usuario = None
if 'menu_activo' not in st.session_state: st.session_state.menu_activo = "Roster"
if 'division_activa' not in st.session_state: st.session_state.division_activa = None
if 'es_super_admin' not in st.session_state: st.session_state.es_super_admin = False


# ==========================================
# PORTADA DE BIENVENIDA / LOBBY
# ==========================================
if st.session_state.division_activa is None:
    # Menú Super Admin oculto y pequeño en la esquina superior derecha
    col_top_l, col_top_r = st.columns([6, 1])
    with col_top_r:
        with st.expander("🔑 Admin"):
            with st.form("form_login_super_admin"):
                sa_user = st.text_input("Usuario SA", value="superadmin")
                sa_pass = st.text_input("Contraseña SA", type="password")
                if st.form_submit_button("Entrar"):
                    ws_sa = obtener_o_crear_hoja("SuperAdmin_Config", DATOS_SUPER_ADMIN_INIT)
                    try:
                        df_sa_live = pd.DataFrame(ws_sa.get_all_records())
                    except:
                        df_sa_live = DATOS_SUPER_ADMIN_INIT

                    match_sa = df_sa_live[(df_sa_live["Usuario"].astype(str).str.lower() == sa_user.strip().lower()) & 
                                          (df_sa_live["Contraseña"].astype(str) == sa_pass.strip())]
                    if not match_sa.empty:
                        st.session_state.es_super_admin = True
                        st.session_state.autenticado = True
                        st.session_state.rol_usuario = "admin"
                        st.session_state.nombre_usuario = "Super Administrador"
                        st.session_state.division_activa = DIVISIONES_DISPONIBLES[0]
                        st.success("¡Acceso de Super Admin concedido!")
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas en la hoja SuperAdmin_Config.")

    st.markdown(f"""
        <div class="hero-container" style="background: linear-gradient(rgba(11, 16, 23, 0.88), rgba(17, 26, 36, 0.92)), url('{URL_LOGO_EQUIPO}'); background-size: cover; background-position: center;">
            <img src="{URL_LOGO_EQUIPO}" width="100" style="margin-bottom: 15px; border-radius: 50%; box-shadow: 0 0 20px rgba(255, 70, 85, 0.6);">
            <h1 style="border: none; margin-bottom: 5px;">SCARLET ESPORTS ORGANIZATION</h1>
            <p style="font-size: 1.1rem; color: #94a3b8; max-width: 600px;">
                Plataforma institucional de gestión de planteles y control analítico.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center; margin: 20px 0;'>Selecciona una División:</h3>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    for idx, div_nombre in enumerate(DIVISIONES_DISPONIBLES):
        col_target = cols[idx % 3]
        logo_url = LOGOS_DIVISIONES.get(div_nombre, URL_LOGO_EQUIPO)
        
        with col_target:
            st.markdown(f"""
                <div class="division-card" style="background: linear-gradient(rgba(11, 16, 23, 0.85), rgba(17, 26, 36, 0.90)), url('{logo_url}'); background-size: cover; background-position: center;">
                    <img src="{logo_url}" width="35" style="border-radius: 50%; margin-bottom: 8px; border: 1px solid #ff4655;">
                    <h4 style="color: #ffffff; margin: 0; font-weight: 600;">{div_nombre}</h4>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Ingresar a {div_nombre}", key=f"btn_card_{idx}", use_container_width=True):
                st.session_state.division_activa = div_nombre
                st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
            
    st.stop()


# ==========================================
# CARGAR HOJAS DE LA DIVISIÓN ACTIVA
# ==========================================
sheet_roster, sheet_asistencia, sheet_disciplina, sheet_config = obtener_hojas_division(st.session_state.division_activa)
df_config_live = cargar_configuracion_fresco(sheet_config)


# ==========================================
# BARRA SUPERIOR DE NAVEGACIÓN
# ==========================================
c_div_1, c_div_2, c_div_3 = st.columns([0.8, 2, 1])
with c_div_1:
    st.image(URL_LOGO_EQUIPO, width=40)

with c_div_2:
    if st.session_state.es_super_admin:
        nueva_div = st.selectbox("Cambiar División (Super Admin)", DIVISIONES_DISPONIBLES, index=DIVISIONES_DISPONIBLES.index(st.session_state.division_activa))
        if nueva_div != st.session_state.division_activa:
            st.session_state.division_activa = nueva_div
            st.rerun()
    else:
        st.markdown(f"<h4 style='color: #ff4655; margin-top: 5px;'>División: {st.session_state.division_activa}</h4>", unsafe_allow_html=True)

with c_div_3:
    if st.button("🏠 Volver al Lobby", use_container_width=True):
        st.session_state.division_activa = None
        st.session_state.autenticado = False
        st.session_state.rol_usuario = None
        st.session_state.nombre_usuario = None
        st.session_state.es_super_admin = False
        st.rerun()


# ==========================================
# PANTALLA DE LOGIN / REGISTRO POR DIVISIÓN
# ==========================================
if not st.session_state.autenticado:
    st.title(f"SCARLET ROSTER — {st.session_state.division_activa.upper()}")
    
    tab_login_admin, tab_login_player, tab_reg_player = st.tabs(["Administrador", "Jugador", "Nuevo Registro"])
    
    with tab_login_admin:
        with st.form("form_login_admin"):
            user_admin = st.text_input("Usuario Administrador")
            pass_admin = st.text_input("Contraseña", type="password")
            if st.form_submit_button("ACCEDER"):
                match = df_config_live[(df_config_live["Usuario"].astype(str).str.lower() == user_admin.strip().lower()) & 
                                       (df_config_live["Contraseña"].astype(str) == pass_admin.strip()) & 
                                       (df_config_live["Rol"].astype(str).str.lower() == "admin")]
                if not match.empty:
                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = "admin"
                    st.session_state.nombre_usuario = "Administrador"
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas.")

    with tab_login_player:
        with st.form("form_login_jugador"):
            user_player = st.text_input("Usuario")
            pass_player = st.text_input("Contraseña", type="password")
            if st.form_submit_button("INICIAR SESIÓN"):
                match = df_config_live[(df_config_live["Usuario"].astype(str).str.lower() == user_player.strip().lower()) & 
                                       (df_config_live["Contraseña"].astype(str) == pass_player.strip())]
                if not match.empty:
                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = "jugador"
                    st.session_state.nombre_usuario = match.iloc[0]["Nombre Real Vinculado"]
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")

    with tab_reg_player:
        with st.form("form_registro_nuevo_jugador"):
            reg_nombre_real = st.text_input("Nombre Real")
            reg_nick = st.text_input("Nick / ID (Ej: Player#TAG)")
            reg_rol_princ = st.selectbox("Rol Principal", ["Duelista", "Iniciador", "Controlador", "Centinela", "Flex"])
            reg_rango = st.selectbox("Rango", ["Hierro", "Bronce", "Plata", "Oro", "Platino", "Diamante", "Ascendente", "Inmortal", "Radiante"])
            reg_usuario = st.text_input("Usuario para la App")
            reg_pass = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("REGISTRARSE"):
                df_r_check = cargar_roster_fresco(sheet_roster)
                nuevo_id = int(df_r_check["ID"].max()) + 1 if not df_r_check.empty and "ID" in df_r_check.columns else 1
                
                nueva_fila = pd.DataFrame([{
                    "ID": nuevo_id, "Nick / ID": reg_nick, "Nombre Real": reg_nombre_real,
                    "Rol Principal": reg_rol_princ, "Rol Secundario": "", "Personajes / Agentes": "",
                    "Rango / Cima": reg_rango, "Cargo en Equipo": "Player", "Estado": "Titular",
                    "Actividad": "Alta", "Contacto / Discord": "", "Notas / Observaciones": ""
                }])
                guardar_en_sheet(sheet_roster, pd.concat([df_r_check, nueva_fila], ignore_index=True))
                
                nueva_config = pd.DataFrame([{"Usuario": reg_usuario, "Contraseña": reg_pass, "Rol": "jugador", "Nombre Real Vinculado": reg_nombre_real}])
                guardar_en_sheet(sheet_config, pd.concat([df_config_live, nueva_config], ignore_index=True))
                st.success("¡Registro exitoso! Ya puedes iniciar sesión.")
    st.stop()


# ==========================================
# APLICACIÓN PRINCIPAL (POST-LOGIN)
# ==========================================
if st.session_state.rol_usuario == "admin":
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.rol_usuario = None
        st.session_state.es_super_admin = False
        st.rerun()

# Menú de navegación interno
menu_opciones = ["Roster", "Asistencia", "Disciplina", "Tracker", "Config"] if st.session_state.rol_usuario == "admin" else ["Roster", "Asistencia", "Disciplina", "Tracker"]
cols_nav = st.columns(len(menu_opciones))
for i, opcion in enumerate(menu_opciones):
    with cols_nav[i]:
        if st.button(opcion, use_container_width=True):
            st.session_state.menu_activo = opcion

st.markdown("---")

df_roster_actual = cargar_roster_fresco(sheet_roster)
df_incidencias_actual = cargar_incidencias_fresco(sheet_disciplina)

# --- VISTA ROSTER ---
if st.session_state.menu_activo == "Roster":
    st.title(f"Roster — {st.session_state.division_activa}")
    if st.session_state.rol_usuario == "admin":
        df_editado = st.data_editor(df_roster_actual, num_rows="dynamic", use_container_width=True, hide_index=True, key="edit_rost")
        if not df_editado.equals(df_roster_actual):
            guardar_en_sheet(sheet_roster, df_editado)
            st.success("Actualizado.")
            st.rerun()
    else:
        st.dataframe(df_roster_actual, use_container_width=True, hide_index=True)

# --- VISTA ASISTENCIA ---
elif st.session_state.menu_activo == "Asistencia":
    st.title(f"Asistencia — {st.session_state.division_activa}")
    st.info("Módulo de asistencia activo para esta división.")

# --- VISTA DISCIPLINA ---
elif st.session_state.menu_activo == "Disciplina":
    st.title(f"Disciplina — {st.session_state.division_activa}")
    if not df_incidencias_actual.empty:
        st.dataframe(df_incidencias_actual, use_container_width=True, hide_index=True)
    else:
        st.info("No hay incidencias registradas.")

# --- VISTA TRACKER ---
elif st.session_state.menu_activo == "Tracker":
    st.title(f"Tracker — {st.session_state.division_activa}")
    nicks = df_roster_actual["Nick / ID"].tolist()
    if nicks:
        sel_nick = st.selectbox("Seleccionar Jugador", nicks)
        if "#" in str(sel_nick):
            st.link_button("Ver Perfil en Tracker.gg", f"https://tracker.gg/valorant/profile/riot/{str(sel_nick).replace('#', '%23')}/overview")

# --- VISTA CONFIG ---
elif st.session_state.menu_activo == "Config" and st.session_state.rol_usuario == "admin":
    st.title(f"Configuración — {st.session_state.division_activa}")
    cfg_edit = st.data_editor(df_config_live, num_rows="dynamic", use_container_width=True, key="edit_cfg")
    if not cfg_edit.equals(df_config_live):
        guardar_en_sheet(sheet_config, cfg_edit)
        st.success("Configuración actualizada.")
        st.rerun()
