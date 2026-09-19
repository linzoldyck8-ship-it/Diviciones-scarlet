import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Scarlet Multi-Divisiones", page_icon="🔥", layout="wide")

URL_LOGO_EQUIPO = "https://cdn.discordapp.com/attachments/1272709315039592469/1275623434063314984/SCARLET.png?ex=6aaf32e6&is=6aade166&hm=4889e788d8f71a5e470db02c4c8f42b95fb19fcdce9be96f7fabab8b6fec25e4&"

# CREDENCIALES FIJAS DE SUPER ADMINISTRADOR GLOBALES
SUPER_USER_DEF = "superadmin"
SUPER_PASS_DEF = "scarlet2026"

LOGOS_DIVISIONES = {
    "Valorant A": "https://images.seeklogo.com/logo-png/37/1/valorant-logo-png_seeklogo-379976.png",
    "Valorant B": "https://images.seeklogo.com/logo-png/37/1/valorant-logo-png_seeklogo-379976.png",
    "Valorant C": "https://images.seeklogo.com/logo-png/37/1/valorant-logo-png_seeklogo-379976.png",
    "Valorant Femenino": "https://images.seeklogo.com/logo-png/37/1/valorant-logo-png_seeklogo-379976.png",
    "Overwatch A": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/55/Overwatch_circle_logo.svg/1280px-Overwatch_circle_logo.svg.png?utm_source=es.wikipedia.org&utm_campaign=index&utm_content=thumbnail",
    "Overwatch B": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/55/Overwatch_circle_logo.svg/1280px-Overwatch_circle_logo.svg.png?utm_source=es.wikipedia.org&utm_campaign=index&utm_content=thumbnail",
    "CS": "https://images.seeklogo.com/logo-png/62/1/counter-strike-logo-png_seeklogo-622731.png"
}

# --- LISTAS Y CONFIGURACIONES ESPECÍFICAS POR JUEGO ---
AGENTES_VALORANT = ["Jett", "Reyna", "Raze", "Neon", "Iso", "Yoru", "Sova", "Fade", "Breach", "Skye", "Gekko", "KAY/O", "Omen", "Viper", "Astra", "Harbor", "Clove", "Cypher", "Killjoy", "Deadlock", "Chamber", "Vyse"]
RANGOS_VALORANT = ["Hierro", "Bronce", "Plata", "Oro", "Platino", "Diamante", "Ascendente 1", "Ascendente 2", "Ascendente 3", "Inmortal 1", "Inmortal 2", "Inmortal 3", "Radiante", ""]
ROLES_VALORANT = ["Duelista", "Iniciador", "Controlador", "Centinela", "Flex", ""]

HEROES_OVERWATCH = ["Reinhardt", "Winston", "D.Va", "Sigma", "Orisa", "Roadhog", "Zarya", "Junker Queen", "Mauga", "Ramattra", "Tracer", "Genji", "Reaper", "Mei", "Pharah", "Echo", "Sombra", "Soldier: 76", "Cassidy", "Ashe", "Hanzo", "Mercy", "Ana", "Kiriko", "Juno", "Lucio", "Zenyatta", "Baptiste", "Illari", "Lifeweaver", "Moira", "Brigitte"]
RANGOS_OVERWATCH = ["Bronce", "Plata", "Oro", "Platino", "Esmeralda", "Diamante", "Maestro", "Gran Maestro", "Champion", ""]
ROLES_OVERWATCH = ["Tanque", "Daño (DPS)", "Soporte", "Flex", ""]

ROLES_CS = ["IGL (In-Game Leader)", "AWPer", "Entry Fragger", "Support", "Lurker", "Fragger", "Rifler", "Capitán de Mapa"]
RANGOS_CS = [
    # FACEIT
    "FACEIT Nivel 1", "FACEIT Nivel 2", "FACEIT Nivel 3", "FACEIT Nivel 4", "FACEIT Nivel 5", 
    "FACEIT Nivel 6", "FACEIT Nivel 7", "FACEIT Nivel 8", "FACEIT Nivel 9", "FACEIT Nivel 10",
    # Gamers Club (GC)
    "GC Rookie", "GC Novato", "GC Main", "GC Intermediate", "GC Advanced", "GC Pro", "GC Elite",
    # Clasicos / Premier
    "Plata", "Nova de Oro", "Maestro Guardian", "Águila Laureada", "Supremo", "Global Elite", "Premier 20k+", ""
]

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp { background: linear-gradient(135deg, #0b1017 0%, #111a24 100%); color: #e2e8f0; font-family: 'Inter', sans-serif; }
    .hero-container {
        position: relative; width: 100%; min-height: 50vh;
        background: linear-gradient(rgba(11, 16, 23, 0.85), rgba(17, 26, 36, 0.90));
        background-size: cover; background-position: center; border-radius: 12px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        text-align: center; padding: 30px; border: 1px solid rgba(255, 70, 85, 0.3);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6); margin-bottom: 25px;
    }
    h1, h2, h3 { color: #ffffff !important; font-weight: 700; }
    h1 {
        background: linear-gradient(90deg, #ffffff 0%, #ff4655 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 2.3rem; border-bottom: 2px solid rgba(255, 70, 85, 0.3); padding-bottom: 10px; margin-bottom: 20px;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #16222d 0%, #0f1923 100%);
        border: 1px solid rgba(255, 70, 85, 0.3); padding: 15px; border-radius: 8px;
    }
    div[data-testid="stMetricValue"] { color: #ff4655 !important; font-weight: 700; }
    .stButton>button {
        width: 100%; background: transparent !important; color: #cbd5e1 !important; border: none !important;
        font-weight: 600; font-size: 0.95rem; padding: 8px 12px; text-transform: uppercase; transition: all 0.2s ease;
    }
    .stButton>button:hover { color: #ff4655 !important; background: rgba(255, 70, 85, 0.1) !important; border-radius: 4px; }
    .division-card {
        background-size: 50% !important; background-repeat: no-repeat !important; background-position: center 25px !important;
        background-color: #111a24; border-radius: 12px; border: 1px solid rgba(255, 70, 85, 0.4);
        padding: 25px 10px 15px 10px; text-align: center; box-shadow: 0 6px 20px rgba(0,0,0,0.5);
        transition: all 0.3s ease; margin-bottom: 15px; min-height: 160px; display: flex; flex-direction: column; justify-content: flex-end;
    }
    .division-card:hover { transform: translateY(-5px); border-color: #ff4655; box-shadow: 0 10px 30px rgba(255, 70, 85, 0.4); }
    .stTextInput input, .stSelectbox select, .stDateInput input {
        background-color: #111a24 !important; color: #ffffff !important; border: 1px solid #233242 !important; border-radius: 6px !important; padding: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

DATOS_INICIALES_ROSTER = pd.DataFrame({
    "ID": [1, 2, 3, 4, 5],
    "Nick / ID": ["Player1#TAG", "Player2#TAG", "Player3#TAG", "Player4#TAG", "Player5#TAG"],
    "Nombre Real": ["Juan", "Carlos", "Mateo", "Lucas", "Gabriel"],
    "Rol Principal": ["Duelista", "Iniciador", "Controlador", "Centinela", "Flex"],
    "Rol Secundario": ["Flex", "Duelista", "Iniciador", "Controlador", "Centinela"],
    "Personajes / Agentes": ["Jett, Reyna", "Sova, Fade", "Omen, Viper", "Cypher, Killjoy", "Breach, Astra"],
    "Rango / Cima": ["Inmortal 1", "Ascendente 3", "Diamante 2", "Inmortal 2", "Radiante"],
    "Cargo en Equipo": ["Capitan", "Player", "Player", "Player", "Sub capitan"],
    "Estado": ["Titular", "Titular", "Titular", "Titular", "Banca"],
    "Actividad": ["Alta", "Alta", "Media", "Alta", "Alta"],
    "Contacto / Discord": ["discord1", "discord2", "discord3", "discord4", "discord5"],
    "Notas / Observaciones": ["", "", "", "", ""]
})

DATOS_INICIALES_CONFIG = pd.DataFrame({
    "Usuario": ["admin", SUPER_USER_DEF],
    "Contraseña": ["admin123", SUPER_PASS_DEF],
    "Rol": ["admin", "super_admin"],
    "Nombre Real Vinculado": ["", "Super Administrador"]
})

DIVISIONES_DISPONIBLES = ["Valorant A", "Valorant B", "Valorant C", "Valorant Femenino", "Overwatch A", "Overwatch B", "CS"]

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
        st.error(f"Error crítico conectando a Google Sheets: {e}")
        return None

spreadsheet = conectar_google_sheets()

def obtener_hojas_division(division_nombre):
    if spreadsheet is None: return None, None, None, None
    prefix = division_nombre.replace(" ", "_")
    
    try:
        sheet_roster = spreadsheet.worksheet(f"{prefix}_Roster")
    except gspread.exceptions.WorksheetNotFound:
        sheet_roster = spreadsheet.add_worksheet(title=f"{prefix}_Roster", rows="100", cols="15")
        sheet_roster.update([DATOS_INICIALES_ROSTER.columns.values.tolist()] + DATOS_INICIALES_ROSTER.values.tolist())

    try:
        sheet_asistencia = spreadsheet.worksheet(f"{prefix}_Asistencia")
    except gspread.exceptions.WorksheetNotFound:
        sheet_asistencia = spreadsheet.add_worksheet(title=f"{prefix}_Asistencia", rows="100", cols="35")
        df_asistencia_init = pd.DataFrame(columns=["Nombre Real", "Mes", "Días Hábiles"] + [str(i) for i in range(1, 32)])
        sheet_asistencia.update([df_asistencia_init.columns.values.tolist()])

    try:
        sheet_disciplina = spreadsheet.worksheet(f"{prefix}_Disciplina")
    except gspread.exceptions.WorksheetNotFound:
        sheet_disciplina = spreadsheet.add_worksheet(title=f"{prefix}_Disciplina", rows="100", cols="10")
        df_disc_init = pd.DataFrame(columns=["Fecha", "Jugador", "Tipo", "Sanción", "Detalles"])
        sheet_disciplina.update([df_disc_init.columns.values.tolist()])

    try:
        sheet_config = spreadsheet.worksheet(f"{prefix}_Config")
    except gspread.exceptions.WorksheetNotFound:
        sheet_config = spreadsheet.add_worksheet(title=f"{prefix}_Config", rows="50", cols="5")
        sheet_config.update([DATOS_INICIALES_CONFIG.columns.values.tolist()] + DATOS_INICIALES_CONFIG.values.tolist())
        
    return sheet_roster, sheet_asistencia, sheet_disciplina, sheet_config

def guardar_en_sheet(sheet_obj, df):
    if sheet_obj is not None:
        try:
            df_clean = df.fillna("")
            data_to_upload = [df_clean.columns.values.tolist()] + df_clean.values.tolist()
            sheet_obj.clear()
            sheet_obj.update(data_to_upload)
        except Exception as e:
            st.error(f"Error al sincronizar con Google Sheets: {e}")

def cargar_roster_fresco(sheet_roster):
    if sheet_roster is not None:
        try:
            data = sheet_roster.get_all_records()
            if not data: return DATOS_INICIALES_ROSTER.copy()
            df = pd.DataFrame(data)
            return DATOS_INICIALES_ROSTER.copy() if df.empty else df
        except:
            return DATOS_INICIALES_ROSTER.copy()
    return DATOS_INICIALES_ROSTER.copy()

def cargar_incidencias_fresco(sheet_disciplina):
    if sheet_disciplina is not None:
        try:
            data = sheet_disciplina.get_all_records()
            df = pd.DataFrame(data)
            if df.empty or "Fecha" not in df.columns:
                return pd.DataFrame(columns=["Fecha", "Jugador", "Tipo", "Sanción", "Detalles"])
            return df
        except:
            return pd.DataFrame(columns=["Fecha", "Jugador", "Tipo", "Sanción", "Detalles"])
    return pd.DataFrame(columns=["Fecha", "Jugador", "Tipo", "Sanción", "Detalles"])

def cargar_configuracion_fresco(sheet_config):
    if sheet_config is not None:
        try:
            data = sheet_config.get_all_records()
            df = pd.DataFrame(data)
            if df.empty: 
                guardar_en_sheet(sheet_config, DATOS_INICIALES_CONFIG)
                return DATOS_INICIALES_CONFIG.copy()
            
            df["Usuario_lower"] = df["Usuario"].astype(str).str.lower().str.strip()
            if not (df["Usuario_lower"] == SUPER_USER_DEF).any():
                nueva_fila = pd.DataFrame([{
                    "Usuario": SUPER_USER_DEF,
                    "Contraseña": SUPER_PASS_DEF,
                    "Rol": "super_admin",
                    "Nombre Real Vinculado": "Super Administrador"
                }])
                df = pd.concat([df.drop(columns=["Usuario_lower"]), nueva_fila], ignore_index=True)
                guardar_en_sheet(sheet_config, df)
            else:
                df = df.drop(columns=["Usuario_lower"])
            return df
        except:
            return DATOS_INICIALES_CONFIG.copy()
    return DATOS_INICIALES_CONFIG.copy()

if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'rol_usuario' not in st.session_state: st.session_state.rol_usuario = None
if 'nombre_usuario' not in st.session_state: st.session_state.nombre_usuario = None
if 'menu_activo' not in st.session_state: st.session_state.menu_activo = "Roster"
if 'division_activa' not in st.session_state: st.session_state.division_activa = None

if st.session_state.division_activa is None:
    st.markdown(f"""
        <div class="hero-container" style="background: linear-gradient(rgba(11, 16, 23, 0.88), rgba(17, 26, 36, 0.92)), url('{URL_LOGO_EQUIPO}'); background-size: cover; background-position: center;">
            <img src="{URL_LOGO_EQUIPO}" width="120" style="margin-bottom: 20px; border-radius: 50%; box-shadow: 0 0 25px rgba(255, 70, 85, 0.6);">
            <h1 style="border: none; margin-bottom: 10px;">SCARLET ESPORTS ORGANIZATION</h1>
            <p style="font-size: 1.2rem; color: #94a3b8; max-width: 650px; margin-bottom: 20px;">
                Plataforma institucional de gestión de planteles, control de asistencia, seguimiento disciplinario y analítica por división.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center; margin: 30px 0 20px 0;'>Selecciona la División a la que deseas ingresar:</h3>", unsafe_allow_html=True)
    cols = st.columns(3)
    for idx, div_nombre in enumerate(DIVISIONES_DISPONIBLES):
        col_target = cols[idx % 3]
        logo_url = LOGOS_DIVISIONES.get(div_nombre, URL_LOGO_EQUIPO)
        with col_target:
            st.markdown(f"""
                <div class="division-card" style="background-image: linear-gradient(rgba(17, 26, 36, 0.92), rgba(17, 26, 36, 0.95)), url('{logo_url}');">
                    <h4 style="color: #ffffff; margin: 0; font-weight: 600; letter-spacing: 0.5px;">{div_nombre}</h4>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Entrar a {div_nombre}", key=f"btn_card_{idx}"):
                st.session_state.division_activa = div_nombre
                st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
    st.stop()

sheet_roster, sheet_asistencia, sheet_disciplina, sheet_config = obtener_hojas_division(st.session_state.division_activa)
df_config_live = cargar_configuracion_fresco(sheet_config)

# --- BARRA SUPERIOR (SELECTOR DE DIVISIONES PERSISTENTE PARA SUPER ADMIN) ---
st.markdown("""
    <div style="background-color: #0b1017; border-bottom: 2px solid #ff4655; padding: 12px 0px 8px 0px; margin-bottom: 15px;">
    </div>
""", unsafe_allow_html=True)

c_div_1, c_div_2, c_div_3 = st.columns([0.8, 2, 1])
with c_div_1:
    st.image(URL_LOGO_EQUIPO, width=45)

with c_div_2:
    if st.session_state.autenticado and st.session_state.rol_usuario == "super_admin":
        nueva_div = st.selectbox("Cambiar División Activa", DIVISIONES_DISPONIBLES, index=DIVISIONES_DISPONIBLES.index(st.session_state.division_activa))
        if nueva_div != st.session_state.division_activa:
            st.session_state.division_activa = nueva_div
            st.rerun()
    else:
        st.markdown(f"<h4 style='color: #ff4655; padding-top: 8px;'>División: {st.session_state.division_activa}</h4>", unsafe_allow_html=True)

with c_div_3:
    if st.button("🏠 Volver al Inicio"):
        st.session_state.division_activa = None
        st.session_state.autenticado = False
        st.session_state.rol_usuario = None
        st.session_state.nombre_usuario = None
        st.rerun()

if not st.session_state.autenticado:
    st.title(f"SCARLET ROSTER — {st.session_state.division_activa.upper()}")
    st.markdown(f"Base de datos y credenciales para **{st.session_state.division_activa}**.")
    
    tab_login_admin, tab_login_player, tab_reg_player = st.tabs(["Administración / Super Admin", "Inicio de Sesión (Jugador)", "Nuevo Registro"])
    
    with tab_login_admin:
        st.markdown(f"### Credenciales de Administrador o Super Administrador")
        st.info(f"💡 **Credenciales por defecto:** Usuario: `{SUPER_USER_DEF}` | Contraseña: `{SUPER_PASS_DEF}`")
        with st.form("form_login_admin"):
            user_admin = st.text_input("Usuario Administrador / Super Admin", key="input_admin_user")
            pass_admin = st.text_input("Contraseña de Acceso", type="password", key="input_admin_pass")
            submit_admin = st.form_submit_button("AUTORIZAR ACCESO")
            
            if submit_admin:
                match = df_config_live[(df_config_live["Usuario"].astype(str).str.lower().str.strip() == user_admin.strip().lower()) & 
                                       (df_config_live["Contraseña"].astype(str).str.strip() == pass_admin.strip())]
                if not match.empty:
                    row_match = match.iloc[0]
                    rol_encontrado = str(row_match["Rol"]).strip().lower()
                    
                    if rol_encontrado in ["admin", "super_admin"]:
                        st.session_state.autenticado = True
                        st.session_state.rol_usuario = rol_encontrado
                        st.session_state.nombre_usuario = row_match.get("Nombre Real Vinculado", "Super Administrador")
                        st.success(f"Acceso autorizado como {rol_encontrado.upper()}. Redirigiendo...")
                        st.rerun()
                    else:
                        st.error("El usuario ingresado no cuenta con privilegios administrativos.")
                else:
                    st.error("Credenciales inválidas en la base de datos.")

    with tab_login_player:
        with st.form("form_login_jugador"):
            user_player = st.text_input("Usuario", key="input_player_user")
            pass_player = st.text_input("Contraseña", type="password", key="input_player_pass")
            if st.form_submit_button("INICIAR SESIÓN"):
                match = df_config_live[(df_config_live["Usuario"].astype(str).str.lower().str.strip() == user_player.strip().lower()) & 
                                       (df_config_live["Contraseña"].astype(str).str.strip() == pass_player.strip()) &
                                       (df_config_live["Rol"].astype(str).str.lower() == "jugador")]
                if not match.empty:
                    row_match = match.iloc[0]
                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = "jugador"
                    st.session_state.nombre_usuario = row_match["Nombre Real Vinculado"]
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")

    with tab_reg_player:
        div_reg = st.session_state.division_activa.lower()
        opciones_roles_reg = ROLES_VALORANT if "valorant" in div_reg else (ROLES_OVERWATCH if "overwatch" in div_reg else ROLES_CS)
        opciones_rangos_reg = RANGOS_VALORANT if "valorant" in div_reg else (RANGOS_OVERWATCH if "overwatch" in div_reg else RANGOS_CS)
        
        OPCIONES_ESTADO = ["Titular", "Banca", "Sexto player", "En Prueba"]
        with st.form("form_registro_nuevo_jugador"):
            reg_nombre_real = st.text_input("Nombre Real")
            reg_nick = st.text_input("Nick / ID")
            reg_rol_princ = st.selectbox("Rol Principal", opciones_roles_reg)
            reg_rango = st.selectbox("Rango / Cima Actual", opciones_rangos_reg)
            reg_estado = st.selectbox("Estado Asignado", OPCIONES_ESTADO)
            reg_discord = st.text_input("Contacto / Discord")
            reg_usuario = st.text_input("Nuevo Nombre de Usuario")
            reg_pass = st.text_input("Contraseña de Acceso", type="password", key="input_reg_pass")
            
            if st.form_submit_button("REGISTRAR INTEGRANTE"):
                if reg_nombre_real and reg_usuario and reg_pass:
                    df_c_check = cargar_configuracion_fresco(sheet_config)
                    df_r_check = cargar_roster_fresco(sheet_roster)
                    
                    nueva_fila_roster = pd.DataFrame([{
                        "ID": len(df_r_check) + 1, "Nick / ID": reg_nick, "Nombre Real": reg_nombre_real,
                        "Rol Principal": reg_rol_princ, "Rol Secundario": "", "Personajes / Agentes": "",
                        "Rango / Cima": reg_rango, "Cargo en Equipo": "Player", "Estado": reg_estado,
                        "Actividad": "Alta", "Contacto / Discord": reg_discord, "Notas / Observaciones": ""
                    }])
                    guardar_en_sheet(sheet_roster, pd.concat([df_r_check, nueva_fila_roster], ignore_index=True))

                    nueva_fila_config = pd.DataFrame([{"Usuario": reg_usuario, "Contraseña": reg_pass, "Rol": "jugador", "Nombre Real Vinculado": reg_nombre_real}])
                    guardar_en_sheet(sheet_config, pd.concat([df_c_check, nueva_fila_config], ignore_index=True))
                    st.success("Registrado correctamente. Ya puedes iniciar sesión.")
    st.stop()

if st.session_state.rol_usuario in ["admin", "super_admin"]:
    st.sidebar.markdown(f"👤 **Usuario:** `{st.session_state.nombre_usuario}`")
    st.sidebar.markdown(f"🏷️ **Credencial:** `{st.session_state.rol_usuario.upper()}`")
    st.sidebar.markdown(f"🎯 **División:** `{st.session_state.division_activa}`")
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Recargar Datos"): st.rerun()
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.rol_usuario = None
        st.rerun()
else:
    st.markdown("<style>section[data-testid='stSidebar'] { display: none; }</style>", unsafe_allow_html=True)

if st.session_state.rol_usuario in ["admin", "super_admin"]:
    cols_nav = st.columns(5)
    with cols_nav[0]: 
        if st.button("Roster"): st.session_state.menu_activo = "Roster"
    with cols_nav[1]: 
        if st.button("Asistencia"): st.session_state.menu_activo = "Asistencia"
    with cols_nav[2]: 
        if st.button("Disciplina"): st.session_state.menu_activo = "Disciplina"
    with cols_nav[3]: 
        if st.button("Tracker"): st.session_state.menu_activo = "Tracker"
    with cols_nav[4]: 
        if st.button("Config"): st.session_state.menu_activo = "Config"
else:
    cols_nav = st.columns(4)
    with cols_nav[0]: 
        if st.button("Roster"): st.session_state.menu_activo = "Roster"
    with cols_nav[1]: 
        if st.button("Asistencia"): st.session_state.menu_activo = "Asistencia"
    with cols_nav[2]: 
        if st.button("Mis Sanciones"): st.session_state.menu_activo = "Disciplina"
    with cols_nav[3]: 
        if st.button("Tracker"): st.session_state.menu_activo = "Tracker"

st.markdown("<hr style='border: 1px solid rgba(255, 70, 85, 0.4); margin: 15px 0;'>", unsafe_allow_html=True)

df_roster_actual = cargar_roster_fresco(sheet_roster)
df_incidencias_actual = cargar_incidencias_fresco(sheet_disciplina)
df_config_actual = cargar_configuracion_fresco(sheet_config)

if st.session_state.menu_activo == "Roster":
    st.title(f"Gestión de Roster — {st.session_state.division_activa}")
    
    div_actual = st.session_state.division_activa.lower()
    if "valorant" in div_actual:
        opciones_juego = AGENTES_VALORANT
        opciones_roles = ROLES_VALORANT
        opciones_rangos = RANGOS_VALORANT
        label_agentes = "Agentes principales (Valorant)"
    elif "overwatch" in div_actual:
        opciones_juego = HEROES_OVERWATCH
        opciones_roles = ROLES_OVERWATCH
        opciones_rangos = RANGOS_OVERWATCH
        label_agentes = "Héroes principales (Overwatch)"
    else:  # CS
        opciones_juego = ROLES_CS
        opciones_roles = ROLES_CS
        opciones_rangos = RANGOS_CS
        label_agentes = "Roles tácticos / Armas (CS)"

    if st.session_state.rol_usuario in ["admin", "super_admin"]:
        configuracion_columnas = {
            "Rol Principal": st.column_config.SelectboxColumn("Rol Principal", options=opciones_roles),
            "Rol Secundario": st.column_config.SelectboxColumn("Rol Secundario", options=opciones_roles),
            "Rango / Cima": st.column_config.SelectboxColumn("Rango / Cima", options=opciones_rangos),
        }
        
        df_roster_editado = st.data_editor(
            df_roster_actual, 
            num_rows="dynamic", 
            use_container_width=True, 
            hide_index=True, 
            column_config=configuracion_columnas,
            key="editor_roster_principal"
        )
        if not df_roster_editado.equals(df_roster_actual):
            guardar_en_sheet(sheet_roster, df_roster_editado)
            st.rerun()

        st.markdown("---")
        st.markdown(f"### Selección Dinámica de {label_agentes}")
        jugadores_disponibles = [j for j in df_roster_actual["Nombre Real"].dropna().tolist() if str(j).strip() != ""]
        if jugadores_disponibles:
            c1, c2 = st.columns(2)
            j_sel = c1.selectbox("Seleccionar Jugador", jugadores_disponibles)
            fila_j = df_roster_actual[df_roster_actual["Nombre Real"] == j_sel]
            actuales = [a.strip() for a in str(fila_j.iloc[0]["Personajes / Agentes"]).split(",") if a.strip() in opciones_juego]
            
            nuevos = c2.multiselect(f"Seleccionar para {j_sel}", options=opciones_juego, default=actuales, key=f"multi_{j_sel}")
            if st.button("Guardar Selección"):
                df_roster_actual.loc[df_roster_actual["Nombre Real"] == j_sel, "Personajes / Agentes"] = ", ".join(nuevos)
                guardar_en_sheet(sheet_roster, df_roster_actual)
                st.success("Guardado con éxito.")
                st.rerun()
    else:
        st.dataframe(df_roster_actual, use_container_width=True, hide_index=True)

elif st.session_state.menu_activo == "Asistencia":
    st.title(f"Control de Asistencia — {st.session_state.division_activa}")
    st.info("Módulo de asistencia operativo sincronizado.")

elif st.session_state.menu_activo == "Disciplina":
    st.title("Panel Disciplinario")
    if not df_incidencias_actual.empty:
        st.dataframe(df_incidencias_actual, use_container_width=True, hide_index=True)
    else:
        st.info("Sin incidencias.")

elif st.session_state.menu_activo == "Tracker":
    st.title("Tracker")
    nicks = df_roster_actual["Nick / ID"].dropna().tolist()
    if nicks:
        n_sel = st.selectbox("Seleccionar", nicks)
        if "#" in str(n_sel):
            st.link_button("VER PERFIL EXTERNO", f"https://tracker.gg/valorant/profile/riot/{str(n_sel).replace('#', '%23')}/overview")

elif st.session_state.menu_activo == "Config" and st.session_state.rol_usuario in ["admin", "super_admin"]:
    st.title(f"Configuración — {st.session_state.division_activa}")
    
    st.markdown("### Credenciales de Acceso (Modificables en DB)")
    config_editado = st.data_editor(df_config_actual, num_rows="dynamic", use_container_width=True, hide_index=True)
    if not config_editado.equals(df_config_actual):
        guardar_en_sheet(sheet_config, config_editado)
        st.success("Configuración actualizada en Google Sheets.")
        st.rerun()

    if st.session_state.rol_usuario == "super_admin":
        st.markdown("---")
        st.markdown("### 🔒 Panel Exclusivo de Super Administrador")
        st.warning("Zona de control total y reseteo de división.")
        
        if st.button("RESET TOTAL DE DIVISIÓN"):
            guardar_en_sheet(sheet_roster, DATOS_INICIALES_ROSTER)
            guardar_en_sheet(sheet_config, DATOS_INICIALES_CONFIG)
            st.success("División restablecida.")
            st.rerun()
