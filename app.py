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

# URLs DE LOS LOGOS DE CADA JUEGO
LOGOS_DIVISIONES = {
    "Valorant A": "https://images.seeklogo.com/logo-png/37/1/valorant-logo-png_seeklogo-379976.png",
    "Valorant B": "https://images.seeklogo.com/logo-png/37/1/valorant-logo-png_seeklogo-379976.png",
    "Valorant C": "https://images.seeklogo.com/logo-png/37/1/valorant-logo-png_seeklogo-379976.png",
    "Valorant Femenino": "https://images.seeklogo.com/logo-png/37/1/valorant-logo-png_seeklogo-379976.png",
    "Overwatch A": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/55/Overwatch_circle_logo.svg/1280px-Overwatch_circle_logo.svg.png?utm_source=es.wikipedia.org&utm_campaign=index&utm_content=thumbnail",
    "Overwatch B": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/55/Overwatch_circle_logo.svg/1280px-Overwatch_circle_logo.svg.png?utm_source=es.wikipedia.org&utm_campaign=index&utm_content=thumbnail",
    "CS": "https://images.seeklogo.com/logo-png/62/1/counter-strike-logo-png_seeklogo-622731.png"
}

# --- LISTAS DINÁMICAS DE AGENTES / ROLES POR JUEGO ---
AGENTES_VALORANT = [
    "Jett", "Reyna", "Raze", "Neon", "Iso", "Yoru",
    "Sova", "Fade", "Breach", "Skye", "Gekko", "KAY/O",
    "Omen", "Viper", "Astra", "Harbor", "Clove",
    "Cypher", "Killjoy", "Deadlock", "Chamber", "Vyse"
]

HEROES_OVERWATCH = [
    "Reinhardt", "Winston", "D.Va", "Sigma", "Orisa", "Roadhog", "Zarya", "Junker Queen", "Mauga", "Ramattra", "Wrecking Ball",
    "Tracer", "Genji", "Reaper", "Mei", "Pharah", "Echo", "Sombra", "Soldier: 76", "Cassidy", "Ashe", "Hanzo", "Torbjörn", "Bastion", "Symmetra", "Junkrat", "Widowmaker",
    "Mercy", "Ana", "Kiriko", "Juno", "Lucio", "Zenyatta", "Baptiste", "Illari", "Lifeweaver", "Moira", "Brigitte"
]

ROLES_CS = [
    "IGL (In-Game Leader)", "AWPer", "Entry Fragger", "Support", "Lurker", "Fragger", "Rifler", "Capitán de Mapa"
]

# --- ESTILOS EMPRESARIALES MINIMALISTAS & SCARLET THEME ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp { background: linear-gradient(135deg, #0b1017 0%, #111a24 100%); color: #e2e8f0; font-family: 'Inter', sans-serif; }
    .hero-container {
        position: relative; width: 100%; min-height: 50vh;
        background: linear-gradient(rgba(11, 16, 23, 0.85), rgba(17, 26, 36, 0.90));
        border-radius: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center;
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
    "Valorant A", "Valorant B", "Valorant C", "Valorant Femenino", 
    "Overwatch A", "Overwatch B", "CS"
]

# --- CONEXIÓN GOOGLE SHEETS ---
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
# PORTADA DE BIENVENIDA
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
# CARGAR HOJAS DE LA DIVISIÓN ACTIVA
# ==========================================
sheet_roster, sheet_asistencia, sheet_disciplina, sheet_config = obtener_hojas_division(st.session_state.division_activa)
df_config_live = cargar_configuracion_fresco(sheet_config)


# ==========================================
# BARRA SUPERIOR
# ==========================================
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
# PANTALLA DE LOGIN / REGISTRO
# ==========================================
if not st.session_state.autenticado:
    st.title(f"SCARLET ROSTER — {st.session_state.division_activa.upper()}")
    tab_login_admin, tab_login_super, tab_login_player, tab_reg_player = st.tabs(["Administrador", "Super Admin", "Inicio de Sesión (Jugador)", "Nuevo Registro"])
    
    with tab_login_admin:
        with st.form("form_login_admin"):
            user_admin = st.text_input("Usuario Administrador")
            pass_admin = st.text_input("Contraseña de Acceso", type="password")
            if st.form_submit_button("AUTORIZAR ACCESO ADMIN"):
                match = df_config_live[(df_config_live["Usuario"].astype(str).str.lower() == user_admin.strip().lower()) & 
                                       (df_config_live["Contraseña"].astype(str) == pass_admin.strip()) & 
                                       (df_config_live["Rol"].astype(str).str.lower() == "admin")]
                if not match.empty:
                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = "admin"
                    st.session_state.nombre_usuario = "Administrador"
                    st.session_state.division_autenticada = st.session_state.division_activa
                    st.rerun()
                else:
                    st.error("Credenciales inválidas.")

    with tab_login_super:
        with st.form("form_login_super_admin"):
            pass_super = st.text_input("Contraseña Maestra de Super Admin", type="password")
            if st.form_submit_button("ACCEDER COMO SUPER ADMIN"):
                if pass_super.strip() == CLAVE_SUPER_ADMIN:
                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = "admin"
                    st.session_state.nombre_usuario = "Super Administrador"
                    st.session_state.division_autenticada = st.session_state.division_activa
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta.")

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
                    st.session_state.division_autenticada = st.session_state.division_activa
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")

    with tab_reg_player:
        OPCIONES_ROLES = ["Duelista", "Iniciador", "Controlador", "Centinela", "Flex"]
        OPCIONES_RANGOS = ["Hierro", "Bronce", "Plata", "Oro", "Platino", "Diamante", "Ascendente", "Inmortal", "Radiante"]
        with st.form("form_registro_nuevo_jugador"):
            reg_nombre_real = st.text_input("Nombre Real")
            reg_nick = st.text_input("Nick / ID")
            reg_rol_princ = st.selectbox("Rol Principal", OPCIONES_ROLES)
            reg_usuario = st.text_input("Usuario")
            reg_pass = st.text_input("Contraseña", type="password")
            if st.form_submit_button("REGISTRAR INTEGRANTE"):
                # Registro simplificado
                st.success("Registrado correctamente.")
    st.stop()

# --- BARRA LATERAL ADMIN ---
if st.session_state.rol_usuario == "admin":
    st.sidebar.markdown(f"👤 **Usuario:** `{st.session_state.nombre_usuario}`")
    st.sidebar.markdown(f"🎯 **División:** `{st.session_state.division_activa}`")
    if st.sidebar.button("🔄 Recargar"): st.rerun()
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
else:
    st.markdown("<style>section[data-testid='stSidebar'] { display: none; }</style>", unsafe_allow_html=True)

# --- NAVEGACIÓN ---
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

st.markdown("<hr style='border: 1px solid rgba(255, 70, 85, 0.4); margin: 15px 0;'>", unsafe_allow_html=True)

df_roster_actual = cargar_roster_fresco(sheet_roster)
df_incidencias_actual = cargar_incidencias_fresco(sheet_disciplina)
df_config_actual = cargar_configuracion_fresco(sheet_config)


# ==========================================
# SECCIÓN 1: ROSTER (CON SELECCIÓN DINÁMICA DE AGENTES/ROLES)
# ==========================================
if st.session_state.menu_activo == "Roster":
    st.title(f"Gestión de Roster — {st.session_state.division_activa}")
    
    # Determinar qué opciones de agentes/roles mostrar según el juego seleccionado
    div_actual = st.session_state.division_activa.lower()
    if "valorant" in div_actual:
        opciones_juego = AGENTES_VALORANT
        label_agentes = "Agentes principales (Valorant)"
    elif "overwatch" in div_actual:
        opciones_juego = HEROES_OVERWATCH
        label_agentes = "Héroes principales (Overwatch)"
    else:  # CS
        opciones_juego = ROLES_CS
        label_agentes = "Roles tácticos (CS)"

    if st.session_state.rol_usuario == "admin":
        st.markdown("### Modificación Rápida de Plantel (Tabla)")
        
        OPCIONES_ROLES = ["Duelista", "Iniciador", "Controlador", "Centinela", "Flex", "Tank", "Damage", "Support", ""]
        OPCIONES_RANGOS = ["Hierro", "Bronce", "Plata", "Oro", "Platino", "Diamante", "Ascendente", "Inmortal", "Radiante", "Global Elite", ""]
        OPCIONES_ESTADO = ["Titular", "Banca", "Sexto player", "En Prueba", "Inactivo", ""]

        configuracion_columnas = {
            "Rol Principal": st.column_config.SelectboxColumn("Rol Principal", options=OPCIONES_ROLES),
            "Rol Secundario": st.column_config.SelectboxColumn("Rol Secundario", options=OPCIONES_ROLES),
            "Rango / Cima": st.column_config.SelectboxColumn("Rango / Cima", options=OPCIONES_RANGOS),
            "Estado": st.column_config.SelectboxColumn("Estado", options=OPCIONES_ESTADO),
        }
        
        df_roster_editado = st.data_editor(
            df_roster_actual,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            column_config=configuracion_columnas,
            height=300,
            key="editor_roster_principal"
        )
        
        if not df_roster_editado.equals(df_roster_actual):
            guardar_en_sheet(sheet_roster, df_roster_editado)
            st.success("Roster actualizado y sincronizado.")
            st.rerun()

        # --- SELECTOR DINÁMICO MÁS FÁCIL (SIN ESCRIBIR A MANO) ---
        st.markdown("---")
        st.markdown(f"### Selección Dinámica de {label_agentes} por Jugador")
        
        jugadores_disponibles = df_roster_actual["Nombre Real"].dropna().tolist()
        jugadores_disponibles = [j for j in jugadores_disponibles if str(j).strip() != "" and str(j).lower() != "nan"]
        
        if jugadores_disponibles:
            col_sel_p, col_sel_a = st.columns(2)
            with col_sel_p:
                jugador_elegido = st.selectbox("Seleccionar Jugador", jugadores_disponibles, key="select_jugador_agentes")
            
            # Buscar agentes actuales del jugador seleccionado
            fila_jugador = df_roster_actual[df_roster_actual["Nombre Real"] == jugador_elegido]
            agentes_actuales_str = str(fila_jugador.iloc[0]["Personajes / Agentes"]) if not fila_jugador.empty else ""
            default_selection = [a.strip() for a in agentes_actuales_str.split(",") if a.strip() in opciones_juego]

            with col_sel_a:
                nuevos_agentes = st.multiselect(
                    f"Selecciona los agentes/roles para {jugador_elegido}:",
                    options=opciones_juego,
                    default=default_selection,
                    key=f"multiselect_{jugador_elegido}"
                )
            
            if st.button("Guardar Selección de Agentes"):
                agentes_texto_final = ", ".join(nuevos_agentes)
                df_roster_actual.loc[df_roster_actual["Nombre Real"] == jugador_elegido, "Personajes / Agentes"] = agentes_texto_final
                guardar_en_sheet(sheet_roster, df_roster_actual)
                st.success(f"¡Agentes actualizados para {jugador_elegido} con éxito!")
                st.rerun()
    else:
        st.info("Modo Visualización de Roster.")
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
            except: pass

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
            try: dias = int(row["Días Hábiles"])
            except: dias = 22
            if dias == 0: return "0%"
            asistencia = sum(row[dias_mes] == "P") + sum(row[dias_mes] == "J") + (sum(row[dias_mes] == "T") * 0.8)
            return f"{min((asistencia / dias) * 100, 100):.0f}%"

        if st.session_state.rol_usuario == "admin":
            df_editado = st.data_editor(df_mes, use_container_width=True, key="editor_asistencia_mes")
            df_editado["% Asistencia"] = df_editado.apply(calcular_porcentaje, axis=1)
            if st.button("GUARDAR ASISTENCIA EN SHEETS"):
                df_para_guardar = df_editado.reset_index()
                if not df_asistencia_guardada.empty:
                    otros_meses = df_asistencia_guardada[df_asistencia_guardada["Mes"] != mes_seleccionado]
                    df_final_asis = pd.concat([otros_meses, df_para_guardar], ignore_index=True)
                else: df_final_asis = df_para_guardar
                guardar_en_sheet(sheet_asistencia, df_final_asis)
                st.success("Asistencia sincronizada correctamente.")
        else:
            df_mes["% Asistencia"] = df_mes.apply(calcular_porcentaje, axis=1)
            if st.session_state.nombre_usuario in df_mes.index:
                st.dataframe(df_mes.loc[[st.session_state.nombre_usuario]], use_container_width=True)


# ==========================================
# SECCIÓN 3: DISCIPLINA
# ==========================================
elif st.session_state.menu_activo == "Disciplina":
    if st.session_state.rol_usuario == "admin":
        st.title(f"Panel Disciplinario — {st.session_state.division_activa}")
        jugadores_activos = [j for j in df_roster_actual["Nombre Real"].tolist() if str(j).strip() != ""]
        with st.form("form_anotacion", clear_on_submit=True):
            fecha = st.date_input("Fecha")
            tipo = st.selectbox("Tipo", ["Positiva", "Negativa", "Advertencia"])
            sancion = st.selectbox("Sanción", ["Ninguna", "Strike 1", "Strike 2", "Expulsión"])
            jugador_sel = st.selectbox("Jugador", jugadores_activos)
            detalles = st.text_area("Detalles")
            if st.form_submit_button("REGISTRAR"):
                nueva_fila = pd.DataFrame([{"Fecha": str(fecha), "Jugador": jugador_sel, "Tipo": tipo, "Sanción": sancion, "Detalles": detalles}])
                df_disc_actualizado = pd.concat([df_incidencias_actual, nueva_fila], ignore_index=True)
                guardar_en_sheet(sheet_disciplina, df_disc_actualizado)
                st.success("Registrado con éxito.")
                st.rerun()
        if not df_incidencias_actual.empty:
            st.dataframe(df_incidencias_actual, use_container_width=True, hide_index=True)
    else:
        st.title("Tus Sanciones")
        mi_nombre = st.session_state.nombre_usuario
        if not df_incidencias_actual.empty and mi_nombre:
            st.dataframe(df_incidencias_actual[df_incidencias_actual["Jugador"].str.lower() == mi_nombre.lower()], use_container_width=True)


# ==========================================
# SECCIÓN 4: TRACKER
# ==========================================
elif st.session_state.menu_activo == "Tracker":
    st.title(f"Tracker — {st.session_state.division_activa}")
    nicks_lista = df_roster_actual["Nick / ID"].dropna().tolist()
    if nicks_lista:
        nick_seleccionado = st.selectbox("Seleccionar Integrante", nicks_lista)
        if "#" in str(nick_seleccionado):
            url = f"https://tracker.gg/valorant/profile/riot/{str(nick_seleccionado).replace('#', '%23')}/overview"
            st.link_button("VER PERFIL EXTERNO", url)


# ==========================================
# SECCIÓN 5: CONFIGURACIÓN
# ==========================================
elif st.session_state.menu_activo == "Config" and st.session_state.rol_usuario == "admin":
    st.title(f"Configuración — {st.session_state.division_activa}")
    config_editado = st.data_editor(df_config_actual, num_rows="dynamic", use_container_width=True, hide_index=True)
    if not config_editado.equals(df_config_actual):
        guardar_en_sheet(sheet_config, config_editado)
        st.success("Configuración actualizada.")
        st.rerun()
