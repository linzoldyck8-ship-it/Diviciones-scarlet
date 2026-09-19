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

# --- ESTILOS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp { background: linear-gradient(135deg, #0b1017 0%, #111a24 100%); color: #e2e8f0; font-family: 'Inter', sans-serif; }
    
    .hero-container {
        position: relative; width: 100%; min-height: 50vh;
        background: linear-gradient(rgba(11, 16, 23, 0.85), rgba(17, 26, 36, 0.90));
        background-size: cover; background-position: center;
        border-radius: 12px; display: flex; flex-direction: column;
        align-items: center; justify-content: center; text-align: center;
        padding: 30px; border: 1px solid rgba(255, 70, 85, 0.3);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6); margin-bottom: 25px;
    }
    
    h1, h2, h3 { color: #ffffff !important; font-weight: 700; letter-spacing: -0.5px; }
    
    h1 {
        background: linear-gradient(90deg, #ffffff 0%, #ff4655 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 2.3rem; border-bottom: 2px solid rgba(255, 70, 85, 0.3);
        padding-bottom: 10px; margin-bottom: 20px;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #16222d 0%, #0f1923 100%);
        border: 1px solid rgba(255, 70, 85, 0.3); padding: 15px;
        border-radius: 8px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    div[data-testid="stMetric"]:hover { border-color: #ff4655; box-shadow: 0 6px 25px rgba(255, 70, 85, 0.3); }
    div[data-testid="stMetricValue"] { color: #ff4655 !important; font-weight: 700; }

    .stButton>button { 
        width: 100%; background: transparent !important; color: #cbd5e1 !important; 
        border: none !important; font-weight: 600; font-size: 0.95rem;
        padding: 8px 12px; letter-spacing: 0.8px; text-transform: uppercase;
        transition: all 0.2s ease; 
    }
    .stButton>button:hover { color: #ff4655 !important; background: rgba(255, 70, 85, 0.1) !important; border-radius: 4px; }

    .division-card {
        background-size: cover; background-position: center; border-radius: 12px;
        border: 1px solid rgba(255, 70, 85, 0.4); padding: 20px 10px;
        text-align: center; box-shadow: 0 6px 20px rgba(0,0,0,0.5);
        transition: all 0.3s ease; margin-bottom: 15px;
    }
    .division-card:hover { transform: translateY(-5px); border-color: #ff4655; box-shadow: 0 10px 30px rgba(255, 70, 85, 0.4); }

    .stTextInput input, .stSelectbox select, .stDateInput input {
        background-color: #111a24 !important; color: #ffffff !important;
        border: 1px solid #233242 !important; border-radius: 6px !important; padding: 10px !important;
    }
    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: #ff4655 !important; box-shadow: 0 0 0 2px rgba(255, 70, 85, 0.2) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATOS INICIALES ---
DATOS_INICIALES_ROSTER = pd.DataFrame(columns=[
    "ID", "Nick / ID", "Nombre Real", "Rol Principal", "Rol Secundario",
    "Personajes / Agentes", "Rango / Cima", "Cargo en Equipo", "Estado",
    "Actividad", "Contacto / Discord", "Notas / Observaciones"
])

DATOS_INICIALES_CONFIG = pd.DataFrame({
    "Usuario": ["admin"], "Contraseña": ["admin123"], "Rol": ["admin"], "Nombre Real Vinculado": [""]
})

DIVISIONES_DISPONIBLES = ["Valorant A", "Valorant B", "Valorant C", "Valorant Femenino", "Overwatch A", "Overwatch B", "CS"]

# --- FUNCIONES DE BASE DE DATOS OPTIMIZADAS ---
@st.cache_resource
def conectar_google_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open("crea el proyecto en formato hoja de calculo como...") # ¡CÁMBIALO AQUÍ!
    except Exception as e:
        st.error(f"Error crítico conectando a Google Sheets: {e}")
        return None

@st.cache_resource
def obtener_hojas_division(division_nombre):
    spreadsheet = conectar_google_sheets()
    if spreadsheet is None: return None, None, None, None
    
    prefix = division_nombre.replace(" ", "_")
    
    def obtener_o_crear(titulo, filas, cols, init_data=None):
        try:
            return spreadsheet.worksheet(titulo)
        except gspread.exceptions.WorksheetNotFound:
            hoja = spreadsheet.add_worksheet(title=titulo, rows=filas, cols=cols)
            if init_data is not None:
                hoja.update([init_data.columns.values.tolist()] + init_data.values.tolist())
            return hoja

    sheet_roster = obtener_o_crear(f"{prefix}_Roster", "100", "15", DATOS_INICIALES_ROSTER)
    
    df_asis_init = pd.DataFrame(columns=["Nombre Real", "Mes", "Días Hábiles"] + [str(i) for i in range(1, 32)])
    sheet_asistencia = obtener_o_crear(f"{prefix}_Asistencia", "100", "35", df_asis_init)
    
    df_disc_init = pd.DataFrame(columns=["Fecha", "Jugador", "Tipo", "Sanción", "Detalles"])
    sheet_disciplina = obtener_o_crear(f"{prefix}_Disciplina", "100", "10", df_disc_init)
    
    sheet_config = obtener_o_crear(f"{prefix}_Config", "50", "5", DATOS_INICIALES_CONFIG)
        
    return sheet_roster, sheet_asistencia, sheet_disciplina, sheet_config

@st.cache_data(ttl=300) # Cachea los datos por 5 minutos
def extraer_datos(_sheet, datos_iniciales):
    if _sheet is None: return datos_iniciales.copy()
    try:
        data = _sheet.get_all_records()
        if not data: return datos_iniciales.copy()
        df = pd.DataFrame(data)
        return datos_iniciales.copy() if df.empty else df
    except:
        return datos_iniciales.copy()

def guardar_en_sheet(sheet_obj, df):
    if sheet_obj is not None:
        try:
            df_clean = df.fillna("")
            data_to_upload = [df_clean.columns.values.tolist()] + df_clean.values.tolist()
            sheet_obj.clear()
            sheet_obj.update(data_to_upload)
            st.cache_data.clear() # Limpia la memoria para mostrar los nuevos datos de inmediato
        except Exception as e:
            st.error(f"Error al sincronizar con Google Sheets: {e}")


# --- INICIALIZACIÓN DE ESTADOS ---
for key, val in {'autenticado': False, 'rol_usuario': None, 'nombre_usuario': None, 'menu_activo': "Roster", 'division_activa': None}.items():
    if key not in st.session_state: st.session_state[key] = val

# ==========================================
# PORTADA DE BIENVENIDA
# ==========================================
if st.session_state.division_activa is None:
    st.markdown(f"""
        <div class="hero-container" style="background: linear-gradient(rgba(11, 16, 23, 0.88), rgba(17, 26, 36, 0.92)), url('{URL_LOGO_EQUIPO}'); background-size: cover; background-position: center;">
            <img src="{URL_LOGO_EQUIPO}" width="120" style="margin-bottom: 20px; border-radius: 50%; box-shadow: 0 0 25px rgba(255, 70, 85, 0.6);">
            <h1 style="border: none; margin-bottom: 10px;">SCARLET ESPORTS ORGANIZATION</h1>
            <p style="font-size: 1.2rem; color: #94a3b8; max-width: 650px; margin-bottom: 20px;">Plataforma institucional de gestión y analítica.</p>
        </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(3)
    for idx, div_nombre in enumerate(DIVISIONES_DISPONIBLES):
        with cols[idx % 3]:
            logo_url = LOGOS_DIVISIONES.get(div_nombre, URL_LOGO_EQUIPO)
            st.markdown(f"""
                <div class="division-card" style="background: linear-gradient(rgba(11, 16, 23, 0.85), rgba(17, 26, 36, 0.90)), url('{logo_url}');">
                    <img src="{logo_url}" width="35" style="border-radius: 50%; margin-bottom: 8px; border: 1px solid #ff4655;">
                    <h4 style="color: #ffffff; margin-bottom: 15px;">{div_nombre}</h4>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Entrar a {div_nombre}", key=f"btn_card_{idx}"):
                st.session_state.division_activa = div_nombre
                st.rerun()
    st.stop()

# ==========================================
# CARGA CENTRAL DE DATOS (CON CACHÉ)
# ==========================================
sheet_roster, sheet_asistencia, sheet_disciplina, sheet_config = obtener_hojas_division(st.session_state.division_activa)

df_roster_actual = extraer_datos(sheet_roster, DATOS_INICIALES_ROSTER)
df_incidencias_actual = extraer_datos(sheet_disciplina, pd.DataFrame(columns=["Fecha", "Jugador", "Tipo", "Sanción", "Detalles"]))
df_config_actual = extraer_datos(sheet_config, DATOS_INICIALES_CONFIG)

# ==========================================
# BARRA SUPERIOR
# ==========================================
st.markdown('<div style="background-color: #0b1017; border-bottom: 2px solid #ff4655; padding: 12px 0px 8px 0px; margin-bottom: 15px;"></div>', unsafe_allow_html=True)
c_div_1, c_div_2, c_div_3 = st.columns([0.8, 2, 1])
with c_div_1: st.image(URL_LOGO_EQUIPO, width=45)
with c_div_3:
    if st.button("🏠 Volver al Inicio"):
        for k in ['division_activa', 'rol_usuario', 'nombre_usuario']: st.session_state[k] = None
        st.session_state.autenticado = False
        st.rerun()

# ==========================================
# SISTEMA DE LOGIN
# ==========================================
if not st.session_state.autenticado:
    st.title(f"SCARLET ROSTER — {st.session_state.division_activa.upper()}")
    tab_login_admin, tab_login_player, tab_reg_player = st.tabs(["Administrador", "Jugador", "Nuevo Registro"])
    
    with tab_login_admin:
        with st.form("form_login_admin"):
            user_admin = st.text_input("Usuario Administrador")
            pass_admin = st.text_input("Contraseña", type="password")
            if st.form_submit_button("ENTRAR COMO ADMIN"):
                match = df_config_actual[(df_config_actual["Usuario"].astype(str).str.lower() == user_admin.strip().lower()) & 
                                         (df_config_actual["Contraseña"].astype(str) == pass_admin.strip()) & 
                                         (df_config_actual["Rol"].astype(str).str.lower() == "admin")]
                if not match.empty:
                    st.session_state.autenticado = True; st.session_state.rol_usuario = "admin"; st.session_state.nombre_usuario = "Administrador"
                    st.rerun()
                else:
                    st.error("Credenciales inválidas.")

    with tab_login_player:
        with st.form("form_login_jugador"):
            user_player = st.text_input("Usuario")
            pass_player = st.text_input("Contraseña", type="password")
            if st.form_submit_button("INICIAR SESIÓN"):
                match = df_config_actual[(df_config_actual["Usuario"].astype(str).str.lower() == user_player.strip().lower()) & 
                                         (df_config_actual["Contraseña"].astype(str) == pass_player.strip())]
                if not match.empty:
                    st.session_state.autenticado = True; st.session_state.rol_usuario = "jugador"; st.session_state.nombre_usuario = match.iloc[0]["Nombre Real Vinculado"]
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")

    with tab_reg_player:
        with st.form("form_registro_nuevo_jugador"):
            c_reg1, c_reg2 = st.columns(2)
            with c_reg1:
                reg_nombre_real = st.text_input("Nombre Real")
                reg_nick = st.text_input("Nick / ID")
                reg_rol_princ = st.selectbox("Rol Principal", ["Duelista", "Iniciador", "Controlador", "Centinela", "Flex"])
                reg_rol_sec = st.selectbox("Rol Secundario", ["", "Duelista", "Iniciador", "Controlador", "Centinela", "Flex"])
                reg_rango = st.selectbox("Rango", ["Hierro", "Bronce", "Plata", "Oro", "Platino", "Diamante", "Ascendente", "Inmortal", "Radiante"])
            with c_reg2:
                reg_estado = st.selectbox("Estado", ["Titular", "Banca", "Sexto player", "En Prueba"])
                reg_discord = st.text_input("Discord")
                reg_usuario = st.text_input("Usuario App")
                reg_pass = st.text_input("Contraseña App", type="password")
            
            if st.form_submit_button("REGISTRAR INTEGRANTE"):
                if reg_nombre_real and reg_usuario and reg_pass:
                    nueva_fila_roster = pd.DataFrame([{"ID": len(df_roster_actual)+1, "Nick / ID": reg_nick, "Nombre Real": reg_nombre_real, "Rol Principal": reg_rol_princ, "Rol Secundario": reg_rol_sec, "Personajes / Agentes": "", "Rango / Cima": reg_rango, "Cargo en Equipo": "Player", "Estado": reg_estado, "Actividad": "Alta", "Contacto / Discord": reg_discord, "Notas / Observaciones": ""}])
                    guardar_en_sheet(sheet_roster, pd.concat([df_roster_actual, nueva_fila_roster], ignore_index=True))
                    
                    nueva_fila_config = pd.DataFrame([{"Usuario": reg_usuario, "Contraseña": reg_pass, "Rol": "jugador", "Nombre Real Vinculado": reg_nombre_real}])
                    guardar_en_sheet(sheet_config, pd.concat([df_config_actual, nueva_fila_config], ignore_index=True))
                    st.success("Registro completado. Ya puedes iniciar sesión.")
                else:
                    st.error("Faltan campos obligatorios.")
    st.stop()


# ==========================================
# APLICACIÓN PRINCIPAL Y MENÚS
# ==========================================
if st.session_state.rol_usuario == "admin":
    st.sidebar.markdown(f"👤 **{st.session_state.nombre_usuario}**\n\n🏷️ `ADMIN`\n\n🎯 `{st.session_state.division_activa}`")
    if st.sidebar.button("🔄 Recargar"): st.cache_data.clear(); st.rerun()
    if st.sidebar.button("🚪 Salir"): st.session_state.autenticado = False; st.rerun()
else:
    st.markdown('<style>section[data-testid="stSidebar"] { display: none; }</style>', unsafe_allow_html=True)

menus = ["Roster", "Asistencia", "Disciplina", "Tracker", "Config"] if st.session_state.rol_usuario == "admin" else ["Roster", "Asistencia", "Mis Sanciones", "Tracker"]
cols_nav = st.columns(len(menus))
for i, menu in enumerate(menus):
    with cols_nav[i]:
        if st.button(menu): st.session_state.menu_activo = menu if menu != "Mis Sanciones" else "Disciplina"

st.markdown("<hr style='border: 1px solid rgba(255, 70, 85, 0.4); margin: 15px 0;'>", unsafe_allow_html=True)

# --- VISTAS POR PESTAÑA ---
if st.session_state.menu_activo == "Roster":
    st.title("Roster")
    if st.session_state.rol_usuario == "admin":
        df_editado = st.data_editor(df_roster_actual, num_rows="dynamic", use_container_width=True, hide_index=True)
        if not df_editado.equals(df_roster_actual):
            guardar_en_sheet(sheet_roster, df_editado)
            st.success("Guardado!"); st.rerun()
    else:
        st.dataframe(df_roster_actual, use_container_width=True, hide_index=True)

elif st.session_state.menu_activo == "Asistencia":
    st.title("Asistencia")
    st.info("Módulo de asistencia optimizado en progreso.") # (Espacio para tu lógica de asistencia previa)

elif st.session_state.menu_activo == "Disciplina":
    st.title("Disciplina" if st.session_state.rol_usuario == "admin" else "Mis Sanciones")
    if st.session_state.rol_usuario == "admin":
        df_editado = st.data_editor(df_incidencias_actual, num_rows="dynamic", use_container_width=True, hide_index=True)
        if not df_editado.equals(df_incidencias_actual):
            guardar_en_sheet(sheet_disciplina, df_editado); st.rerun()
    else:
        mis_sanciones = df_incidencias_actual[df_incidencias_actual["Jugador"] == st.session_state.nombre_usuario]
        st.dataframe(mis_sanciones, use_container_width=True)

elif st.session_state.menu_activo == "Config" and st.session_state.rol_usuario == "admin":
    st.title("Configuración y Permisos")
    df_editado = st.data_editor(df_config_actual, num_rows="dynamic", use_container_width=True, hide_index=True)
    if not df_editado.equals(df_config_actual):
        guardar_en_sheet(sheet_config, df_editado); st.rerun()
