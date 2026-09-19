import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Scarlet Multi-Divisiones", page_icon="🔥", layout="wide")

# URL OFICIAL DEL LOGO GENERAL DEL EQUIPO
URL_LOGO_EQUIPO = "https://cdn.discordapp.com/attachments/1272709315039592469/1275623434063314984/SCARLET.png?ex=6aaf32e6&is=6aade166&hm=4889e788d8f71a5e470db02c4c8f42b95fb19fcdce9be96f7fabab8b6fec25e4&"

# CONTRASEÑA GLOBAL DE SUPER ADMINISTRADOR
CLAVE_SUPER_ADMIN = "super_secret_2026"

# URLs DE LOS LOGOS DE CADA JUEGO (Puedes modificarlas aquí libremente)
LOGOS_DIVISIONES = {
    "Valorant A": "https://images.seeklogo.com/logo-png/37/1/valorant-logo-png_seeklogo-379976.png",
    "Valorant B": "https://images.seeklogo.com/logo-png/37/1/valorant-logo-png_seeklogo-379976.png",
    "Valorant C": "https://images.seeklogo.com/logo-png/37/1/valorant-logo-png_seeklogo-379976.png",
    "Valorant Femenino": "https://images.seeklogo.com/logo-png/37/1/valorant-logo-png_seeklogo-379976.png",
    "Overwatch A": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/55/Overwatch_circle_logo.svg/1280px-Overwatch_circle_logo.svg.png?utm_source=es.wikipedia.org&utm_campaign=index&utm_content=thumbnail",
    "Overwatch B": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/55/Overwatch_circle_logo.svg/1280px-Overwatch_circle_logo.svg.png?utm_source=es.wikipedia.org&utm_campaign=index&utm_content=thumbnail",
    "CS": "https://images.seeklogo.com/logo-png/62/1/counter-strike-logo-png_seeklogo-622731.png"
}

# --- ESTILOS EMPRESARIALES MINIMALISTAS & SCARLET THEME ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp { 
        background: linear-gradient(135deg, #0b1017 0%, #111a24 100%); 
        color: #e2e8f0; 
        font-family: 'Inter', sans-serif; 
    }
    
    /* Estilo de la portada de bienvenida principal */
    .hero-container {
        position: relative;
        width: 100%;
        min-height: 50vh;
        background: linear-gradient(rgba(11, 16, 23, 0.85), rgba(17, 26, 36, 0.90));
        background-size: cover;
        background-position: center;
        border-radius: 12px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 30px;
        border: 1px solid rgba(255, 70, 85, 0.3);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
        margin-bottom: 25px;
    }
    
    h1, h2, h3 { 
        color: #ffffff !important; 
        font-weight: 700; 
        letter-spacing: -0.5px; 
    }
    
    h1 {
        background: linear-gradient(90deg, #ffffff 0%, #ff4655 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.3rem;
        border-bottom: 2px solid rgba(255, 70, 85, 0.3);
        padding-bottom: 10px;
        margin-bottom: 20px;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #16222d 0%, #0f1923 100%);
        border: 1px solid rgba(255, 70, 85, 0.3);
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #ff4655;
        box-shadow: 0 6px 25px rgba(255, 70, 85, 0.3);
    }
    div[data-testid="stMetricValue"] { 
        color: #ff4655 !important; 
        font-weight: 700; 
    }

    /* Botones corporativos generales */
    .stButton>button { 
        width: 100%;
        background: transparent !important;
        color: #cbd5e1 !important; 
        border: none !important; 
        font-weight: 600; 
        font-size: 0.95rem;
        padding: 8px 12px;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        transition: all 0.2s ease; 
    }
    
    .stButton>button:hover { 
        color: #ff4655 !important;
        background: rgba(255, 70, 85, 0.1) !important;
        border-radius: 4px;
    }

    /* Tarjetas estilizadas de divisiones en la portada con logo ajustado */
    .division-card {
        background-size: 50% !important;
        background-repeat: no-repeat !important;
        background-position: center 25px !important;
        background-color: #111a24;
        border-radius: 12px;
        border: 1px solid rgba(255, 70, 85, 0.4);
        padding: 25px 10px 15px 10px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0,0,0,0.5);
        transition: all 0.3s ease;
        margin-bottom: 15px;
        min-height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
    }
    .division-card:hover {
        transform: translateY(-5px);
        border-color: #ff4655;
        box-shadow: 0 10px 30px rgba(255, 70, 85, 0.4);
    }

    .stTextInput input, .stSelectbox select, .stDateInput input {
        background-color: #111a24 !important;
        color: #ffffff !important;
        border: 1px solid #233242 !important;
        border-radius: 6px !important;
        padding: 10px !important;
    }
    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: #ff4655 !important;
        box-shadow: 0 0 0 2px rgba(255, 70, 85, 0.2) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATOS INICIALES PREDETERMINADOS ---
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
    "Usuario": ["admin"],
    "Contraseña": ["admin123"],
    "Rol": ["admin"],
    "Nombre Real Vinculado": [""]
})

DIVISIONES_DISPONIBLES = [
    "Valorant A", 
    "Valorant B", 
    "Valorant C", 
    "Valorant Femenino", 
    "Overwatch A", 
    "Overwatch B", 
    "CS"
]

# --- CONEXIÓN Y CREACIÓN AUTOMÁTICA DE MULTI-HOJAS POR DIVISIÓN ---
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
            if not data: return DATOS_INICIALES_CONFIG.copy()
            df = pd.DataFrame(data)
            return DATOS_INICIALES_CONFIG.copy() if df.empty else df
        except:
            return DATOS_INICIALES_CONFIG.copy()
    return DATOS_INICIALES_CONFIG.copy()

# --- ESTADOS DE LA SESIÓN ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'rol_usuario' not in st.session_state: st.session_state.rol_usuario = None
if 'nombre_usuario' not in st.session_state: st.session_state.nombre_usuario = None
if 'menu_activo' not in st.session_state: st.session_state.menu_activo = "Roster"
if 'division_activa' not in st.session_state: st.session_state.division_activa = None
if 'division_autenticada' not in st.session_state: st.session_state.division_autenticada = None


# ==========================================
# PORTADA DE BIENVENIDA CON TARJETAS ESTILIZADAS Y LOGOS DE FONDO AJUSTADOS
# ==========================================
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


# ==========================================
# CARGAR HOJAS DE LA DIVISIÓN ACTIVA SELECCIONADA
# ==========================================
sheet_roster, sheet_asistencia, sheet_disciplina, sheet_config = obtener_hojas_division(st.session_state.division_activa)
df_config_live = cargar_configuracion_fresco(sheet_config)


# ==========================================
# BARRA SUPERIOR CON CAMBIO DE DIVISIÓN Y LOGO
# ==========================================
st.markdown("""
    <div style="background-color: #0b1017; border-bottom: 2px solid #ff4655; padding: 12px 0px 8px 0px; margin-bottom: 15px;">
    </div>
""", unsafe_allow_html=True)

c_div_1, c_div_2, c_div_3 = st.columns([0.8, 2, 1])
with c_div_1:
    st.image(URL_LOGO_EQUIPO, width=45)
with c_div_2:
    nueva_div = st.selectbox("Cambiar División Activa", DIVISIONES_DISPONIBLES, index=DIVISIONES_DISPONIBLES.index(st.session_state.division_activa))
    if nueva_div != st.session_state.division_activa:
        st.session_state.division_activa = nueva_div
        st.session_state.autenticado = False
        st.session_state.rol_usuario = None
        st.session_state.nombre_usuario = None
        st.rerun()
with c_div_3:
    if st.button("🏠 Volver al Inicio"):
        st.session_state.division_activa = None
        st.session_state.autenticado = False
        st.session_state.rol_usuario = None
        st.session_state.nombre_usuario = None
        st.rerun()


# ==========================================
# PANTALLA DE LOGIN / REGISTRO / SUPER ADMIN POR DIVISIÓN
# ==========================================
if not st.session_state.autenticado:
    st.title(f"SCARLET ROSTER — {st.session_state.division_activa.upper()}")
    st.markdown(f"Base de datos y credenciales exclusivas para **{st.session_state.division_activa}**. Inicie sesión o regístrese.")
    
    tab_login_admin, tab_login_super, tab_login_player, tab_reg_player = st.tabs(["Administrador", "Super Admin", "Inicio de Sesión (Jugador)", "Nuevo Registro"])
    
    with tab_login_admin:
        st.markdown(f"### Credenciales de Administrador ({st.session_state.division_activa})")
        with st.form("form_login_admin"):
            user_admin = st.text_input("Usuario Administrador", key="input_admin_user")
            pass_admin = st.text_input("Contraseña de Acceso", type="password", key="input_admin_pass")
            submit_admin = st.form_submit_button("AUTORIZAR ACCESO ADMIN")
            
            if submit_admin:
                match = df_config_live[(df_config_live["Usuario"].astype(str).str.lower() == user_admin.strip().lower()) & 
                                       (df_config_live["Contraseña"].astype(str) == pass_admin.strip()) & 
                                       (df_config_live["Rol"].astype(str).str.lower() == "admin")]
                if not match.empty:
                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = "admin"
                    st.session_state.nombre_usuario = "Administrador"
                    st.session_state.division_autenticada = st.session_state.division_activa
                    st.success(f"Acceso autorizado para {st.session_state.division_activa}. Redirigiendo...")
                    st.rerun()
                else:
                    st.error(f"Credenciales inválidas para la división {st.session_state.division_activa}.")

    with tab_login_super:
        st.markdown(f"### Acceso Global de Super Administrador")
        st.markdown("Ingrese la contraseña maestra para acceder a esta división con privilegios completos de administrador.")
        with st.form("form_login_super_admin"):
            pass_super = st.text_input("Contraseña Maestra de Super Admin", type="password", key="input_super_pass")
            submit_super = st.form_submit_button("ACCEDER COMO SUPER ADMIN")
            
            if submit_super:
                if pass_super.strip() == CLAVE_SUPER_ADMIN:
                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = "admin"
                    st.session_state.nombre_usuario = "Super Administrador"
                    st.session_state.division_autenticada = st.session_state.division_activa
                    st.success(f"Acceso de Super Administrador concedido en {st.session_state.division_activa}. Redirigiendo...")
                    st.rerun()
                else:
                    st.error("Contraseña de Super Administrador incorrecta.")

    with tab_login_player:
        st.markdown(f"### Credenciales de Jugador ({st.session_state.division_activa})")
        with st.form("form_login_jugador"):
            user_player = st.text_input("Usuario", key="input_player_user")
            pass_player = st.text_input("Contraseña", type="password", key="input_player_pass")
            submit_player = st.form_submit_button("INICIAR SESIÓN")
            
            if submit_player:
                match = df_config_live[(df_config_live["Usuario"].astype(str).str.lower() == user_player.strip().lower()) & 
                                       (df_config_live["Contraseña"].astype(str) == pass_player.strip())]
                if not match.empty:
                    row_match = match.iloc[0]
                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = "jugador"
                    st.session_state.nombre_usuario = row_match["Nombre Real Vinculado"]
                    st.session_state.division_autenticada = st.session_state.division_activa
                    st.success(f"Bienvenido, {st.session_state.nombre_usuario}.")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos en esta división.")

    with tab_reg_player:
        st.markdown(f"### Formulario de Alta para Nuevo Integrante ({st.session_state.division_activa})")
        
        OPCIONES_ROLES = ["Duelista", "Iniciador", "Controlador", "Centinela", "Flex"]
        OPCIONES_RANGOS = ["Hierro", "Bronce", "Plata", "Oro", "Platino", "Diamante", "Ascendente 1", "Ascendente 2", "Ascendente 3", "Inmortal 1", "Inmortal 2", "Inmortal 3", "Radiante", "Maestro", "Gran Maestro", "Top 500"]
        OPCIONES_ESTADO = ["Titular", "Banca", "Sexto player", "En Prueba"]
        
        with st.form("form_registro_nuevo_jugador"):
            c_reg1, c_reg2 = st.columns(2)
            with c_reg1:
                reg_nombre_real = st.text_input("Nombre Real")
                reg_nick = st.text_input("Nick / ID (Ej: Player#TAG)")
                reg_rol_princ = st.selectbox("Rol Principal", OPCIONES_ROLES)
                reg_rol_sec = st.selectbox("Rol Secundario", [""] + OPCIONES_ROLES)
                reg_rango = st.selectbox("Rango / Cima Actual", OPCIONES_RANGOS)
            with c_reg2:
                reg_estado = st.selectbox("Estado Asignado", OPCIONES_ESTADO)
                reg_discord = st.text_input("Contacto / Discord")
                reg_usuario = st.text_input("Nuevo Nombre de Usuario")
                reg_pass = st.text_input("Contraseña de Acceso", type="password", key="input_reg_pass")
                reg_pass_conf = st.text_input("Confirmar Contraseña", type="password", key="input_reg_pass_conf")
            
            submit_nuevo_jugador = st.form_submit_button("REGISTRAR INTEGRANTE")
            
            if submit_nuevo_jugador:
                if not reg_nombre_real.strip() or not reg_nick.strip() or not reg_usuario.strip() or not reg_pass.strip():
                    st.error("Todos los campos principales son obligatorios.")
                elif reg_pass != reg_pass_conf:
                    st.error("Las contraseñas no coinciden.")
                else:
                    df_c_check = cargar_configuracion_fresco(sheet_config)
                    df_r_check = cargar_roster_fresco(sheet_roster)
                    
                    if not df_c_check[df_c_check["Usuario"].astype(str).str.lower() == reg_usuario.strip().lower()].empty:
                        st.error("El nombre de usuario ya está registrado en esta división.")
                    elif not df_r_check[df_r_check["Nombre Real"].astype(str).str.lower() == reg_nombre_real.strip().lower()].empty:
                        st.error("Ya existe un registro con este nombre real en esta división.")
                    else:
                        try:
                            max_id = int(df_r_check["ID"].max()) if not df_r_check.empty and "ID" in df_r_check.columns else 0
                        except:
                            max_id = len(df_r_check)
                        nuevo_id = max_id + 1

                        nueva_fila_roster = pd.DataFrame([{
                            "ID": nuevo_id,
                            "Nick / ID": reg_nick.strip(),
                            "Nombre Real": reg_nombre_real.strip(),
                            "Rol Principal": reg_rol_princ,
                            "Rol Secundario": reg_rol_sec if reg_rol_sec != "" else "",
                            "Personajes / Agentes": "",
                            "Rango / Cima": reg_rango,
                            "Cargo en Equipo": "Player",
                            "Estado": reg_estado,
                            "Actividad": "Alta",
                            "Contacto / Discord": reg_discord.strip(),
                            "Notas / Observaciones": ""
                        }])
                        df_roster_updated = pd.concat([df_r_check, nueva_fila_roster], ignore_index=True)
                        guardar_en_sheet(sheet_roster, df_roster_updated)

                        nueva_fila_config = pd.DataFrame([{
                            "Usuario": reg_usuario.strip(),
                            "Contraseña": reg_pass.strip(),
                            "Rol": "jugador",
                            "Nombre Real Vinculado": reg_nombre_real.strip()
                        }])
                        df_config_updated = pd.concat([df_c_check, nueva_fila_config], ignore_index=True)
                        guardar_en_sheet(sheet_config, df_config_updated)

                        st.success(f"Registro completado en {st.session_state.division_activa}. Ya puede iniciar sesión.")
    
    st.stop()


# ==========================================
# APLICACIÓN PRINCIPAL (POST-LOGIN)
# ==========================================

# --- BARRA LATERAL EXCLUSIVA PARA ADMINISTRADORES ---
if st.session_state.rol_usuario == "admin":
    st.sidebar.markdown(f"👤 **Usuario:** `{st.session_state.nombre_usuario}`")
    st.sidebar.markdown(f"🏷️ **Credencial:** `ADMIN`")
    st.sidebar.markdown(f"🎯 **División:** `{st.session_state.division_activa}`")
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Recargar Datos"):
        st.rerun()

    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.rol_usuario = None
        st.session_state.nombre_usuario = None
        st.session_state.division_autenticada = None
        st.rerun()
else:
    st.markdown("""
        <style>
        section[data-testid="stSidebar"] { display: none; }
        </style>
    """, unsafe_allow_html=True)

# --- BOTONES DE NAVEGACIÓN SUPERIORES ---
if st.session_state.rol_usuario == "admin":
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

st.markdown(f"<hr style='border: 1px solid rgba(255, 70, 85, 0.4); margin: 15px 0;'>", unsafe_allow_html=True)

df_roster_actual = cargar_roster_fresco(sheet_roster)
df_incidencias_actual = cargar_incidencias_fresco(sheet_disciplina)
df_config_actual = cargar_configuracion_fresco(sheet_config)

OPCIONES_ROLES = ["Duelista", "Iniciador", "Controlador", "Centinela", "Flex", ""]
OPCIONES_RANGOS = ["Hierro", "Bronce", "Plata", "Oro", "Platino", "Diamante", "Ascendente 1", "Ascendente 2", "Ascendente 3", "Inmortal 1", "Inmortal 2", "Inmortal 3", "Radiante", "Maestro", "Gran Maestro", "Top 500", ""]
OPCIONES_CARGOS = ["Capitan", "Sub capitan", "Player", "Manager", "Coach", ""]
OPCIONES_ESTADO = ["Titular", "Banca", "Sexto player", "En Prueba", "Inactivo", ""]
OPCIONES_ACTIVIDAD = ["Alta", "Media", "Baja", ""]


# ==========================================
# SECCIÓN 1: ROSTER
# ==========================================
if st.session_state.menu_activo == "Roster":
    st.title(f"Gestión de Roster — {st.session_state.division_activa}")
    
    jugadores_activos_temp = [j for j in df_roster_actual["Nombre Real"].tolist() if str(j).strip() != "" and str(j).lower() != "nan"]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("TOTAL JUGADORES", len(jugadores_activos_temp))
    col2.metric("TITULARES", len(df_roster_actual[df_roster_actual['Estado'] == 'Titular']))
    col3.metric("SEXTO PLAYER", len(df_roster_actual[df_roster_actual['Estado'] == 'Sexto player']))
    col4.metric("BANCA", len(df_roster_actual[df_roster_actual['Estado'] == 'Banca']))
    
    st.markdown("---")
    
    if st.session_state.rol_usuario == "admin":
        configuracion_columnas = {
            "Rol Principal": st.column_config.SelectboxColumn("Rol Principal", options=OPCIONES_ROLES),
            "Rol Secundario": st.column_config.SelectboxColumn("Rol Secundario", options=OPCIONES_ROLES),
            "Rango / Cima": st.column_config.SelectboxColumn("Rango / Cima", options=OPCIONES_RANGOS),
            "Cargo en Equipo": st.column_config.SelectboxColumn("Cargo en Equipo", options=OPCIONES_CARGOS),
            "Estado": st.column_config.SelectboxColumn("Estado", options=OPCIONES_ESTADO),
            "Actividad": st.column_config.SelectboxColumn("Actividad", options=OPCIONES_ACTIVIDAD),
        }
        
        df_roster_editado = st.data_editor(
            df_roster_actual,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            column_config=configuracion_columnas,
            height=350,
            key="editor_roster_principal"
        )
        
        if not df_roster_editado.equals(df_roster_actual):
            guardar_en_sheet(sheet_roster, df_roster_editado)
            st.success("Roster actualizado y sincronizado.")
            st.rerun()

        # --- GRÁFICOS ANALÍTICOS DE ROSTER ---
        st.markdown("---")
        st.markdown("### Analítica Ejecutiva del Plantel")
        
        df_validos_graf = df_roster_actual[df_roster_actual["Nombre Real"].astype(str).str.strip() != ""].copy()
        
        if not df_validos_graf.empty:
            g_col1, g_col2, g_col3 = st.columns(3)
            
            with g_col1:
                df_roles = df_validos_graf["Rol Principal"].value_counts().reset_index()
                df_roles.columns = ["Rol", "Cantidad"]
                fig_roles = px.pie(df_roles, names="Rol", values="Cantidad", title="Distribución por Rol", hole=0.5, color_discrete_sequence=px.colors.sequential.Reds)
                fig_roles.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
                st.plotly_chart(fig_roles, use_container_width=True)
                
            with g_col2:
                df_estados = df_validos_graf["Estado"].value_counts().reset_index()
                df_estados.columns = ["Estado", "Cantidad"]
                fig_estados = px.bar(df_estados, x="Estado", y="Cantidad", title="Estado Actual", color="Estado", color_discrete_sequence=px.colors.sequential.Burg)
                fig_estados.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
                st.plotly_chart(fig_estados, use_container_width=True)
                
            with g_col3:
                df_rangos = df_validos_graf["Rango / Cima"].value_counts().reset_index()
                df_rangos.columns = ["Rango", "Cantidad"]
                fig_rangos = px.bar(df_rangos, x="Rango", y="Cantidad", title="Desglose por Rango", color="Rango", color_discrete_sequence=px.colors.sequential.Sunsetdark)
                fig_rangos.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
                st.plotly_chart(fig_rangos, use_container_width=True)
    else:
        st.info("Modo Visualización.")
        st.dataframe(df_roster_actual, use_container_width=True, hide_index=True)


# ==========================================
# SECCIÓN 2: ASISTENCIA 
# ==========================================
elif st.session_state.menu_activo == "Asistencia":
    st.title(f"Control de Asistencia — {st.session_state.division_activa}")
    jugadores_activos = [j for j in df_roster_actual["Nombre Real"].tolist() if str(j).strip() != "" and str(j).lower() != "nan"]
    
    if len(jugadores_activos) == 0:
        st.warning("No hay jugadores registrados en esta división.")
    else:
        mes_seleccionado = st.selectbox("Seleccionar Mes Operativo", ["Septiembre", "Octubre", "Noviembre", "Diciembre"])
        
        df_asistencia_guardada = pd.DataFrame()
        if sheet_asistencia is not None:
            try:
                data_asis = sheet_asistencia.get_all_records()
                if data_asis: df_asistencia_guardada = pd.DataFrame(data_asis)
            except:
                pass

        dias_mes = [str(i) for i in range(1, 32)]
        df_mes = pd.DataFrame(index=jugadores_activos, columns=dias_mes).fillna("-")
        df_mes["Días Hábiles"] = 22
        df_mes["Mes"] = mes_seleccionado
        df_mes = df_mes.reset_index().rename(columns={"index": "Nombre Real"})

        if not df_asistencia_guardada.empty and "Mes" in df_asistencia_guardada.columns and "Nombre Real" in df_asistencia_guardada.columns:
            df_mes_filtrado = df_asistencia_guardada[df_asistencia_guardada["Mes"] == mes_seleccionado]
            for idx, row in df_mes_filtrado.iterrows():
                nombre = row["Nombre Real"]
                if nombre in df_mes["Nombre Real"].values:
                    for col in dias_mes + ["Días Hábiles"]:
                        if col in row and row[col] != "":
                            df_mes.loc[df_mes["Nombre Real"] == nombre, col] = row[col]

        df_mes = df_mes.set_index("Nombre Real")

        def calcular_porcentaje(row):
            try:
                dias = int(row["Días Hábiles"])
            except:
                dias = 22
            if dias == 0: return "0%"
            asistencia = sum(row[dias_mes] == "P") + sum(row[dias_mes] == "J") + (sum(row[dias_mes] == "T") * 0.8)
            return f"{min((asistencia / dias) * 100, 100):.0f}%"

        if st.session_state.rol_usuario == "admin":
            df_editado = st.data_editor(df_mes, use_container_width=True, key="editor_asistencia_mes")
            df_editado["% Asistencia"] = df_editado.apply(calcular_porcentaje, axis=1)
            st.dataframe(df_editado[["Mes", "Días Hábiles", "% Asistencia"]], use_container_width=True)

            if st.button("GUARDAR ASISTENCIA EN SHEETS"):
                df_para_guardar = df_editado.reset_index()
                if not df_asistencia_guardada.empty:
                    otros_meses = df_asistencia_guardada[df_asistencia_guardada["Mes"] != mes_seleccionado]
                    df_final_asis = pd.concat([otros_meses, df_para_guardar], ignore_index=True)
                else:
                    df_final_asis = df_para_guardar
                guardar_en_sheet(sheet_asistencia, df_final_asis)
                st.success("Asistencia sincronizada correctamente.")
        else:
            df_mes["% Asistencia"] = df_mes.apply(calcular_porcentaje, axis=1)
            if st.session_state.nombre_usuario in df_mes.index:
                df_personal = df_mes.loc[[st.session_state.nombre_usuario]]
                st.markdown(f"### Tu Asistencia: {st.session_state.nombre_usuario}")
                st.dataframe(df_personal, use_container_width=True)
            else:
                st.info("Sin registros de asistencia asociados.")


# ==========================================
# SECCIÓN 3: DISCIPLINA / MIS SANCIONES
# ==========================================
elif st.session_state.menu_activo == "Disciplina":
    if st.session_state.rol_usuario == "admin":
        st.title(f"Panel Disciplinario — {st.session_state.division_activa}")
        jugadores_activos = [j for j in df_roster_actual["Nombre Real"].tolist() if str(j).strip() != "" and str(j).lower() != "nan"]
        
        sub_gen, sub_ind = st.tabs(["Registro General", "Expediente por Jugador"])
        
        with sub_gen:
            st.markdown("### Registrar Nueva Incidencia")
            with st.form("form_anotacion", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    fecha = st.date_input("Fecha")
                    tipo = st.selectbox("Tipo de Incidencia", ["Positiva", "Negativa", "Advertencia"])
                    sancion = st.selectbox("Sanción", ["Ninguna", "Strike 1", "Strike 2", "Expulsión"])
                with c2:
                    jugador_sel = st.selectbox("Jugador Implicado", jugadores_activos)
                    detalles = st.text_area("Notas / Observaciones detalladas")
                
                if st.form_submit_button("REGISTRAR Y SINCRONIZAR"):
                    nueva_fila = pd.DataFrame([{
                        "Fecha": str(fecha),
                        "Jugador": jugador_sel,
                        "Tipo": tipo,
                        "Sanción": sancion,
                        "Detalles": detalles
                    }])
                    df_disc_actualizado = pd.concat([df_incidencias_actual, nueva_fila], ignore_index=True)
                    guardar_en_sheet(sheet_disciplina, df_disc_actualizado)
                    st.success(f"Incidencia registrada para {jugador_sel}.")
                    st.rerun()
            
            st.markdown("---")
            st.markdown("### Historial General de Incidencias")
            if not df_incidencias_actual.empty:
                st.dataframe(df_incidencias_actual, use_container_width=True, hide_index=True)
            else:
                st.info("Sin incidencias registradas.")

        with sub_ind:
            st.markdown("### Expediente Individual")
            jugador_individual = st.selectbox("Seleccionar Jugador:", jugadores_activos, key="select_jugador_ind")
            if not df_incidencias_actual.empty:
                df_filtrado = df_incidencias_actual[df_incidencias_actual["Jugador"] == jugador_individual]
                col_i1, col_i2 = st.columns(2)
                col_i1.metric("TOTAL ANOTACIONES", len(df_filtrado))
                col_i2.metric("SANCIONES ACTIVAS", len(df_filtrado[df_filtrado["Sanción"] != "Ninguna"]))
                st.markdown("---")
                if not df_filtrado.empty:
                    st.dataframe(df_filtrado[["Fecha", "Tipo", "Sanción", "Detalles"]], use_container_width=True, hide_index=True)
                else:
                    st.info("El jugador no registra incidencias.")
            else:
                st.info("Sin registros.")
    else:
        st.title("Expediente Personal y Sanciones")
        mi_nombre = st.session_state.nombre_usuario
        
        if not df_incidencias_actual.empty and mi_nombre:
            df_mis_inc = df_incidencias_actual[df_incidencias_actual["Jugador"].str.lower() == mi_nombre.lower()]
            
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("TOTAL ANOTACIONES", len(df_mis_inc))
            col_m2.metric("SANCIONES ACTIVAS", len(df_mis_inc[df_mis_inc["Sanción"] != "Ninguna"]))
            
            st.markdown("---")
            if not df_mis_inc.empty:
                st.dataframe(df_mis_inc[["Fecha", "Tipo", "Sanción", "Detalles"]], use_container_width=True, hide_index=True)
            else:
                st.success("Expediente impecable. Sin sanciones ni advertencias registradas.")
        else:
            st.info("Sin registros en el sistema.")


# ==========================================
# SECCIÓN 4: TRACKER Y STATS
# ==========================================
elif st.session_state.menu_activo == "Tracker":
    st.title(f"Tracker y Estadísticas — {st.session_state.division_activa}")
    
    df_validos_tracker = df_roster_actual[
        (df_roster_actual["Nick / ID"].astype(str).str.strip() != "") & 
        (df_roster_actual["Nick / ID"].astype(str).str.lower() != "nan")
    ]
    
    nicks_lista = df_validos_tracker["Nick / ID"].tolist()
    
    if len(nicks_lista) > 0:
        c_sel, c_btn = st.columns([2, 1])
        with c_sel: 
            default_idx = 0
            if st.session_state.rol_usuario == "jugador" and st.session_state.nombre_usuario:
                match_user = df_validos_tracker[df_validos_tracker["Nombre Real"].astype(str).str.lower() == st.session_state.nombre_usuario.lower()]
                if not match_user.empty:
                    target_nick = match_user.iloc[0]["Nick / ID"]
                    if target_nick in nicks_lista:
                        default_idx = nicks_lista.index(target_nick)
                
            nick_seleccionado = st.selectbox("Seleccionar Integrante", nicks_lista, index=default_idx, key="select_stats_nick")
            
        with c_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if pd.notna(nick_seleccionado) and "#" in str(nick_seleccionado):
                url = f"https://tracker.gg/valorant/profile/riot/{str(nick_seleccionado).replace('#', '%23')}/overview"
                st.link_button("VER PERFIL EXTERNO", url, use_container_width=True)
            else:
                st.info("ID configurado.")

        st.markdown("---")
        st.markdown(f"**Captura de Rendimiento — {nick_seleccionado}**")
        img_upload = st.file_uploader("Cargar captura de rendimiento (Opcional)", type=["png", "jpg", "jpeg"])
        if img_upload:
            st.image(img_upload, use_column_width=True, caption=f"Registro analítico para {nick_seleccionado}")
    else:
        st.warning("No hay IDs registrados en esta división.")


# ==========================================
# SECCIÓN 5: CONFIGURACIÓN Y BORRADOS (SOLO ADMIN)
# ==========================================
elif st.session_state.menu_activo == "Config" and st.session_state.rol_usuario == "admin":
    st.title(f"Configuración de División — {st.session_state.division_activa}")
    st.markdown(f"Gestión de credenciales exclusivas de la hoja **{st.session_state.division_activa.replace(' ', '_')}_Config**.")
    
    st.markdown("### Credenciales de Acceso Exclusivas")
    config_editado = st.data_editor(
        df_config_actual,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="editor_configuracion"
    )
    
    if not config_editado.equals(df_config_actual):
        guardar_en_sheet(sheet_config, config_editado)
        st.success("Credenciales actualizadas y sincronizadas para esta división.")
        st.rerun()

    st.markdown("---")
    st.markdown("### Panel de Eliminación Específica")
    st.warning("Las acciones eliminan permanentemente los datos seleccionados de esta división en Google Sheets.")
    
    col_b1, col_b2, col_b3 = st.columns(3)
    
    with col_b1:
        st.markdown("#### Eliminar Sanción")
        if not df_incidencias_actual.empty:
            opciones_sanciones = [f"[{row['Fecha']}] {row['Jugador']} - {row['Sanción']} ({row['Detalles'][:20]}...)" for idx, row in df_incidencias_actual.iterrows()]
            sancion_a_borrar = st.selectbox("Seleccionar sanción", [""] + opciones_sanciones, key="sel_borrar_sancion")
            
            if st.button("ELIMINAR SANCIÓN"):
                if sancion_a_borrar != "":
                    idx_seleccionado = opciones_sanciones.index(sancion_a_borrar)
                    df_disc_nuevo = df_incidencias_actual.drop(df_incidencias_actual.index[idx_seleccionado]).reset_index(drop=True)
                    guardar_en_sheet(sheet_disciplina, df_disc_nuevo)
                    st.success("Sanción eliminada con éxito.")
                    st.rerun()
        else:
            st.info("Sin sanciones para eliminar.")

    with col_b2:
        st.markdown("#### Eliminar Jugador del Roster")
        jugadores_para_borrar = [j for j in df_roster_actual["Nombre Real"].tolist() if str(j).strip() != "" and str(j).lower() != "nan"]
        if len(jugadores_para_borrar) > 0:
            jugador_a_eliminar = st.selectbox("Seleccionar jugador", [""] + jugadores_para_borrar, key="sel_borrar_jugador")
            
            if st.button("ELIMINAR INTEGRANTE"):
                if jugador_a_eliminar != "":
                    df_roster_nuevo = df_roster_actual[df_roster_actual["Nombre Real"] != jugador_a_eliminar].reset_index(drop=True)
                    guardar_en_sheet(sheet_roster, df_roster_nuevo)
                    
                    df_config_live_b = cargar_configuracion_fresco(sheet_config)
                    df_config_nuevo = df_config_live_b[df_config_live_b["Nombre Real Vinculado"].str.lower() != jugador_a_eliminar.lower()].reset_index(drop=True)
                    guardar_en_sheet(sheet_config, df_config_nuevo)
                    
                    st.success(f"Integrante {jugador_a_eliminar} dado de baja.")
                    st.rerun()
        else:
            st.info("Roster vacío.")

    with col_b3:
        st.markdown("#### Limpiar Asistencia")
        if sheet_asistencia is not None:
            mes_a_limpiar = st.selectbox("Mes a limpiar", ["Septiembre", "Octubre", "Noviembre", "Diciembre"], key="sel_limpiar_mes")
            if st.button("RESETEAR MES"):
                try:
                    data_asis_all = sheet_asistencia.get_all_records()
                    if data_asis_all:
                        df_asis_all = pd.DataFrame(data_asis_all)
                        df_asis_filtrado = df_asis_all[df_asis_all["Mes"] != mes_a_limpiar]
                        guardar_en_sheet(sheet_asistencia, df_asis_filtrado)
                        st.success(f"Registros de {mes_a_limpiar} limpiados.")
                        st.rerun()
                    else:
                        st.info("Hoja de asistencia vacía.")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown("### ZONA DE EMERGENCIA — RESET DIVISIÓN")
    st.warning("Restablece toda la base de datos de esta división a valores iniciales de fábrica.")
    
    with st.form("form_emergencia_reset", clear_on_submit=True):
        st.markdown("Ingrese contraseña de administrador o de Super Admin para autorizar:")
        pass_confirmacion_emergencia = st.text_input("Contraseña", type="password", key="input_emergencia_pass")
        btn_ejecutar_emergencia = st.form_submit_button("VACIAR Y REINICIAR DIVISIÓN")
        
        if btn_ejecutar_emergencia:
            if not pass_confirmacion_emergencia.strip():
                st.error("Ingrese la contraseña.")
            else:
                match_admin = df_config_actual[(df_config_actual["Contraseña"].astype(str) == pass_confirmacion_emergencia.strip()) & 
                                               (df_config_actual["Rol"].astype(str).str.lower() == "admin")]
                es_super = (pass_confirmacion_emergencia.strip() == CLAVE_SUPER_ADMIN)
                
                if match_admin.empty and not es_super:
                    st.error("Contraseña incorrecta. Operación cancelada.")
                else:
                    try:
                        guardar_en_sheet(sheet_roster, DATOS_INICIALES_ROSTER)
                        
                        df_asistencia_init = pd.DataFrame(columns=["Nombre Real", "Mes", "Días Hábiles"] + [str(i) for i in range(1, 32)])
                        guardar_en_sheet(sheet_asistencia, df_asistencia_init)
                        
                        df_disc_init = pd.DataFrame(columns=["Fecha", "Jugador", "Tipo", "Sanción", "Detalles"])
                        guardar_en_sheet(sheet_disciplina, df_disc_init)
                        
                        guardar_en_sheet(sheet_config, DATOS_INICIALES_CONFIG)
                        
                        st.success(f"¡División {st.session_state.division_activa} reiniciada a valores de fábrica!")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error crítico: {e}")
