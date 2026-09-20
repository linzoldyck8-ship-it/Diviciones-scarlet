import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, inspect

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Scarlet Multi-Divisiones", page_icon="⛩️", layout="wide")

# URL OFICIAL DEL LOGO GENERAL DEL EQUIPO
URL_LOGO_EQUIPO = "https://media.discordapp.net/attachments/1272709315039592469/1275623434063314984/SCARLET.png?ex=6aafdba6&is=6aae8a26&hm=4f9d5c1c4d428f813f5a276e19bfae92a3e31a38fdf7bdb6869f7da6338ae00a&=&format=webp&quality=lossless&width=768&height=673"

# URLS DE LOS LOGOS DE CADA JUEGO 
LOGOS_DIVISIONES = {
    "Valorant A": "https://images.seeklogo.com/logo-png/37/1/valorant-logo-png_seeklogo-379976.png",
    "Valorant B": "https://images.seeklogo.com/logo-png/37/1/valorant-logo-png_seeklogo-379976.png",
    "Valorant C": "https://images.seeklogo.com/logo-png/37/1/valorant-logo-png_seeklogo-379976.png",
    "Valorant Femenino": "https://images.seeklogo.com/logo-png/37/1/valorant-logo-png_seeklogo-379976.png",
    "Overwatch A": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/55/Overwatch_circle_logo.svg/1280px-Overwatch_circle_logo.svg.png?utm_source=es.wikipedia.org&utm_campaign=index&utm_content=thumbnail",
    "Overwatch B": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/55/Overwatch_circle_logo.svg/1280px-Overwatch_circle_logo.svg.png?utm_source=es.wikipedia.org&utm_campaign=index&utm_content=thumbnail",
    "CS": "https://images.seeklogo.com/logo-png/62/1/counter-strike-logo-png_seeklogo-622731.png"
}

# --- FONDOS POR URL PARA CADA DIVISIÓN (MODIFICA AQUÍ TUS URLS) ---
FONDOS_DIVISIONES = {
    "Valorant A": "https://www.chromethemer.com/wallpapers/images/960/valorant-wallpaper-4k.jpg",
    "Valorant B": "https://www.chromethemer.com/wallpapers/images/960/valorant-wallpaper-4k.jpg",
    "Valorant C": "https://www.chromethemer.com/wallpapers/images/960/valorant-wallpaper-4k.jpg",
    "Valorant Femenino": "https://www.chromethemer.com/wallpapers/images/960/valorant-wallpaper-4k.jpg",
    "Overwatch A": "https://c4.wallpaperflare.com/wallpaper/111/24/27/blizzard-entertainment-overwatch-video-games-reaper-overwatch-wallpaper-preview.jpg",
    "Overwatch B": "https://c4.wallpaperflare.com/wallpaper/111/24/27/blizzard-entertainment-overwatch-video-games-reaper-overwatch-wallpaper-preview.jpg",
    "CS": "https://wallpapers.com/images/featured/counter-strike-global-offensive-b5gx1yg1eegl77ew.jpg"
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
    
    h1, h2, h3 { color: #ffffff !important; font-weight: 700; letter-spacing: -0.5px; }
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
    div[data-testid="stMetric"]:hover { border-color: #ff4655; box-shadow: 0 6px 25px rgba(255, 70, 85, 0.3); }
    div[data-testid="stMetricValue"] { color: #ff4655 !important; font-weight: 700; }

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

    .division-card {
        background-size: cover;
        background-position: center;
        border-radius: 12px;
        border: 1px solid rgba(255, 70, 85, 0.4);
        padding: 20px 10px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0,0,0,0.5);
        transition: all 0.3s ease;
        margin-bottom: 15px;
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

# --- DICCIONARIOS ESPECÍFICOS POR JUEGO ---
GAME_DATA = {
    "Valorant": {
        "Roles": ["Duelista", "Iniciador", "Controlador", "Centinela", "Flex", ""],
        "Rangos": ["Hierro", "Bronce", "Plata", "Oro", "Platino", "Diamante", "Ascendente", "Inmortal", "Radiante", ""],
        "Personajes": ["Jett", "Reyna", "Phoenix", "Raze", "Neon", "Iso", "Sova", "Fade", "Skye", "Breach", "KAY/O", "Gekko", "Omen", "Brimstone", "Viper", "Astra", "Harbor", "Clove", "Cypher", "Killjoy", "Sage", "Chamber", "Deadlock", "Ninguno"]
    },
    "Overwatch": {
        "Roles": ["Tanque", "Daño (DPS)", "Apoyo (Support)", "Flex", ""],
        "Rangos": ["Bronce", "Plata", "Oro", "Platino", "Esmeralda", "Diamante", "Maestro", "Gran Maestro", "Campeón", "Top 500", ""],
        "Personajes": ["Reinhardt", "Winston", "D.Va", "Sigma", "Zarya", "Ramattra", "Tracer", "Genji", "Widowmaker", "Cassidy", "Pharah", "Sombra", "Sojourn", "Mercy", "Ana", "Lúcio", "Kiriko", "Zenyatta", "Baptiste", "Illari", "Ninguno"]
    },
    "CS": {
        "Roles": ["Entry Fragger", "AWPer", "Support", "IGL", "Lurker", "Flex", ""],
        "Rangos": [
            "FACEIT Nivel 1", "FACEIT Nivel 2", "FACEIT Nivel 3", "FACEIT Nivel 4", "FACEIT Nivel 5",
            "FACEIT Nivel 6", "FACEIT Nivel 7", "FACEIT Nivel 8", "FACEIT Nivel 9", "FACEIT Nivel 10",
            "GC Nivel 1-5", "GC Nivel 6-10", "GC Nivel 11-15", "GC Nivel 16-20", "GC Level S", ""
        ],
        "Personajes": ["Fuerzas Antiterroristas (CT)", "Fuerzas Terroristas (T)", "Ninguno"]
    }
}

def obtener_datos_juego(division_nombre):
    if not division_nombre: return GAME_DATA["Valorant"]
    if "Valorant" in division_nombre: return GAME_DATA["Valorant"]
    if "Overwatch" in division_nombre: return GAME_DATA["Overwatch"]
    if "CS" in division_nombre: return GAME_DATA["CS"]
    return GAME_DATA["Valorant"]

# --- DATOS INICIALES PREDETERMINADOS ---
DATOS_INICIALES_ROSTER = pd.DataFrame(columns=[
    "ID", "Nick / ID", "Nombre Real", "Rol Principal", "Rol Secundario",
    "Personajes / Agentes", "Rango / Cima", "Cargo en Equipo", "Estado",
    "Actividad", "Contacto / Discord", "Notas / Observaciones"
])

DATOS_INICIALES_CONFIG = pd.DataFrame({
    "Usuario": ["admin"],
    "Contraseña": ["admin123"],
    "Rol": ["admin"],
    "Nombre Real Vinculado": [""]
})

DATOS_INICIALES_BLACKLIST = pd.DataFrame(columns=["Nombre Real", "Motivo"])

DIVISIONES_DISPONIBLES = [
    "Valorant A", 
    "Valorant B", 
    "Valorant C", 
    "Valorant Femenino", 
    "Overwatch A", 
    "Overwatch B", 
    "CS"
]

# --- CONEXIÓN Y CREACIÓN AUTOMÁTICA EN SUPABASE ---
@st.cache_resource
def conectar_supabase():
    try:
        raw_url = st.secrets["SUPABASE_DB_URL"]
        
        if raw_url.startswith("postgresql://"):
            raw_url = raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        elif not raw_url.startswith("postgresql+psycopg2://"):
            raw_url = f"postgresql+psycopg2://{raw_url}"
            
        if ".supabase.co" in raw_url and "pooler.supabase.com" not in raw_url:
            raw_url = raw_url.replace("db.", "").replace(".supabase.co", ".pooler.supabase.com:6543")
            
        if "?sslmode=" not in raw_url:
            separator = "&" if "?" in raw_url else "?"
            raw_url = f"{raw_url}{separator}sslmode=require"

        engine = create_engine(raw_url)
        return engine
    except Exception as e:
        st.error(f"Error crítico conectando a Supabase: {e}")
        return None

engine = conectar_supabase()

def cargar_o_crear_tabla(table_name, df_inicial):
    if engine is None: return df_inicial.copy()
    inspector = inspect(engine)
    if not inspector.has_table(table_name):
        df_inicial.to_sql(table_name, engine, if_exists='replace', index=False)
        return df_inicial.copy()
    else:
        return pd.read_sql_table(table_name, engine)

def obtener_tablas_division(division_nombre):
    if engine is None: return None, None, None, None, None
    prefix = division_nombre.replace(" ", "_").lower()
    return f"{prefix}_roster", f"{prefix}_asistencia", f"{prefix}_disciplina", f"{prefix}_config", f"{prefix}_admin_config"

def obtener_tabla_blacklist(division_nombre):
    if engine is None: return None
    prefix = division_nombre.replace(" ", "_").lower()
    return f"{prefix}_blacklist"

def guardar_en_bd(table_name, df):
    if engine is not None and table_name is not None:
        try:
            df_clean = df.fillna("")
            df_clean.to_sql(table_name, engine, if_exists='replace', index=False)
        except Exception as e:
            st.error(f"Error al sincronizar con Supabase: {e}")

def cargar_roster_fresco(tb_roster):
    if tb_roster: return cargar_o_crear_tabla(tb_roster, DATOS_INICIALES_ROSTER)
    return DATOS_INICIALES_ROSTER.copy()

def cargar_incidencias_fresco(tb_disciplina):
    if tb_disciplina: 
        df_init = pd.DataFrame(columns=["Fecha", "Jugador", "Tipo", "Sanción", "Detalles"])
        return cargar_o_crear_tabla(tb_disciplina, df_init)
    return pd.DataFrame(columns=["Fecha", "Jugador", "Tipo", "Sanción", "Detalles"])

def cargar_configuracion_fresco(tb_config):
    if tb_config: return cargar_o_crear_tabla(tb_config, DATOS_INICIALES_CONFIG)
    return DATOS_INICIALES_CONFIG.copy()

def cargar_blacklist_fresco(tb_blacklist):
    if tb_blacklist: return cargar_o_crear_tabla(tb_blacklist, DATOS_INICIALES_BLACKLIST)
    return DATOS_INICIALES_BLACKLIST.copy()

# --- ESTADOS DE LA SESIÓN ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'rol_usuario' not in st.session_state: st.session_state.rol_usuario = None
if 'nombre_usuario' not in st.session_state: st.session_state.nombre_usuario = None
if 'menu_activo' not in st.session_state: st.session_state.menu_activo = "Roster"
if 'division_activa' not in st.session_state: st.session_state.division_activa = None
if 'division_autenticada' not in st.session_state: st.session_state.division_autenticada = None


# ==========================================
# PORTADA DE BIENVENIDA CON TARJETAS ESTILIZADAS Y LOGOS DE FONDO
# ==========================================
if st.session_state.division_activa is None:
    st.markdown(f"""
        <div class="hero-container" style="
            background-image: linear-gradient(rgba(11, 16, 23, 0.88), rgba(17, 26, 36, 0.92)), url('{URL_LOGO_EQUIPO}'), url('{URL_LOGO_EQUIPO}');
            background-position: center, left 5% center, right 5% center;
            background-size: cover, 25%, 25%;
            background-repeat: no-repeat, no-repeat, no-repeat;
        ">
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
                <div class="division-card" style="background: linear-gradient(rgba(11, 16, 23, 0.85), rgba(17, 26, 36, 0.90)), url('{logo_url}'); background-size: cover; background-position: center;">
                    <img src="{logo_url}" width="35" style="border-radius: 50%; margin-bottom: 8px; border: 1px solid #ff4655;">
                    <h4 style="color: #ffffff; margin-bottom: 15px; font-weight: 600; letter-spacing: 0.5px;">{div_nombre}</h4>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Entrar a {div_nombre}", key=f"btn_card_{idx}"):
                st.session_state.division_activa = div_nombre
                st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
            
    st.stop()


# ==========================================
# APLICAR FONDO POR URL AL ENTRAR A CADA DIVISIÓN (ADMIN O JUGADOR)
# ==========================================
fondo_actual_url = FONDOS_DIVISIONES.get(st.session_state.division_activa, "")
if fondo_actual_url:
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(11, 16, 23, 0.90), rgba(17, 26, 36, 0.95)), url('{fondo_actual_url}') !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }}
        </style>
    """, unsafe_allow_html=True)


# ==========================================
# CARGAR TABLAS Y DATOS DE LA DIVISIÓN ACTIVA SELECCIONADA
# ==========================================
tb_roster, tb_asistencia, tb_disciplina, tb_config, tb_admin_config = obtener_tablas_division(st.session_state.division_activa)
tb_blacklist = obtener_tabla_blacklist(st.session_state.division_activa) 

# ASEGURAR CLAVES PRIMARIAS (PRIMARY KEYS) EN SUPABASE PARA EVITAR EL ERROR DE EDICIÓN EN LA WEB
if engine is not None:
    try:
        with engine.begin() as conn:
            # Asegurar PK en tabla de configuración general
            conn.execute(f"CREATE TABLE IF NOT EXISTS {tb_config} (id SERIAL PRIMARY KEY, \"Usuario\" TEXT, \"Contraseña\" TEXT, \"Rol\" TEXT, \"Nombre Real Vinculado\" TEXT);")
            conn.execute(f"ALTER TABLE {tb_config} ADD COLUMN IF NOT EXISTS id SERIAL;")
            try:
                conn.execute(f"ALTER TABLE {tb_config} ADD PRIMARY KEY (id);")
            except Exception:
                pass

            # Asegurar PK en tabla admin_config
            conn.execute(f"CREATE TABLE IF NOT EXISTS {tb_admin_config} (id SERIAL PRIMARY KEY, clave TEXT, valor TEXT);")
            conn.execute(f"ALTER TABLE {tb_admin_config} ADD COLUMN IF NOT EXISTS id SERIAL;")
            try:
                conn.execute(f"ALTER TABLE {tb_admin_config} ADD PRIMARY KEY (id);")
            except Exception:
                pass
    except Exception as e:
        print(f"Nota de esquema: {e}")

df_config_live = cargar_configuracion_fresco(tb_config)

# Extraer roles y rangos específicos del juego activo
datos_juego_actual = obtener_datos_juego(st.session_state.division_activa)
ROLES_JUEGO = [r for r in datos_juego_actual["Roles"] if r != ""]
RANGOS_JUEGO = [r for r in datos_juego_actual["Rangos"] if r != ""]
PERSONAJES_JUEGO = [r for r in datos_juego_actual["Personajes"] if r != ""]

# ==========================================
# BARRA SUPERIOR
# ==========================================
st.markdown("""
    <div style="background-color: #0b1017; border-bottom: 2px solid #ff4655; padding: 12px 0px 8px 0px; margin-bottom: 15px;"></div>
""", unsafe_allow_html=True)

c_div_1, c_div_2, c_div_3 = st.columns([0.8, 2, 1])
with c_div_1: st.image(URL_LOGO_EQUIPO, width=120)
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
    st.markdown(f"Base de datos y credenciales exclusivas para **{st.session_state.division_activa}**.")
    
    tab_login_admin, tab_login_player, tab_reg_player = st.tabs(["Administrador", "Inicio de Sesión (Jugador)", "Nuevo Registro"])
    
    with tab_login_admin:
        with st.form("form_login_admin"):
            user_admin = st.text_input("Usuario Administrador")
            pass_admin = st.text_input("Contraseña de Acceso", type="password")
            if st.form_submit_button("AUTORIZAR ACCESO ADMIN"):
                match = df_config_live[(df_config_live["Usuario"].astype(str).str.lower() == user_admin.strip().lower()) & 
                                       (df_config_live["Contraseña"].astype(str) == pass_admin.strip()) & 
                                       (df_config_live["Rol"].astype(str).str.lower() == "admin")]
                
                # Respaldo de validación por admin_config seguro
                pass_admin_valido = False
                if not match.empty:
                    pass_admin_valido = True
                else:
                    try:
                        df_adm_cfg = pd.read_sql_table(tb_admin_config, engine)
                        val_pass = df_adm_cfg[df_adm_cfg["clave"] == "password_admin"]["valor"].values
                        if len(val_pass) > 0 and pass_admin.strip() == str(val_pass[0]) and user_admin.strip().lower() == "admin":
                            pass_admin_valido = True
                    except Exception:
                        pass

                if pass_admin_valido:
                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = "admin"
                    st.session_state.nombre_usuario = "Administrador"
                    st.session_state.division_autenticada = st.session_state.division_activa
                    st.rerun()
                else:
                    st.error(f"Credenciales inválidas para la división {st.session_state.division_activa}.")

    with tab_login_player:
        with st.form("form_login_jugador"):
            user_player = st.text_input("Usuario")
            pass_player = st.text_input("Contraseña", type="password")
            if st.form_submit_button("INICIAR SESIÓN"):
                match = df_config_live[(df_config_live["Usuario"].astype(str).str.lower() == user_player.strip().lower()) & 
                                       (df_config_live["Contraseña"].astype(str) == pass_player.strip())]
                if not match.empty:
                    nombre_real_vinculado = str(match.iloc[0]["Nombre Real Vinculado"]).strip()
                    df_blacklist_check = cargar_blacklist_fresco(tb_blacklist)
                    if not df_blacklist_check[df_blacklist_check["Nombre Real"].astype(str).str.lower() == nombre_real_vinculado.lower()].empty:
                        st.error("ACCESO DENEGADO: Este jugador se encuentra en la Lista Negra.")
                    else:
                        st.session_state.autenticado = True
                        st.session_state.rol_usuario = "jugador"
                        st.session_state.nombre_usuario = match.iloc[0]["Nombre Real Vinculado"]
                        st.session_state.division_autenticada = st.session_state.division_activa
                        st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")

    with tab_reg_player:
        OPCIONES_ESTADO = ["Titular", "Banca", "Sexto player", "En Prueba"]
        
        with st.form("form_registro_nuevo_jugador"):
            c_reg1, c_reg2 = st.columns(2)
            with c_reg1:
                reg_nombre_real = st.text_input("Nombre Real")
                reg_nick = st.text_input("Nick / ID (Ej: Player#TAG)")
                reg_rol_princ = st.selectbox("Rol Principal", ROLES_JUEGO)
                reg_rol_sec = st.selectbox("Rol Secundario", [""] + ROLES_JUEGO)
                reg_personaje = st.selectbox("Faccion/Personaje Principal", PERSONAJES_JUEGO)
                reg_rango = st.selectbox("Rango / Cima Actual", RANGOS_JUEGO)
            with c_reg2:
                reg_estado = st.selectbox("Estado Asignado", OPCIONES_ESTADO)
                reg_discord = st.text_input("Contacto / Discord")
                reg_usuario = st.text_input("Nuevo Nombre de Usuario")
                reg_pass = st.text_input("Contraseña de Acceso", type="password")
                reg_pass_conf = st.text_input("Confirmar Contraseña", type="password")
            
            if st.form_submit_button("REGISTRAR INTEGRANTE"):
                if not reg_nombre_real.strip() or not reg_nick.strip() or not reg_usuario.strip() or not reg_pass.strip():
                    st.error("Todos los campos principales son obligatorios.")
                elif reg_pass != reg_pass_conf:
                    st.error("Las contraseñas no coinciden.")
                else:
                    df_c_check = cargar_configuracion_fresco(tb_config)
                    df_r_check = cargar_roster_fresco(tb_roster)
                    df_bl_check = cargar_blacklist_fresco(tb_blacklist)
                    
                    if not df_bl_check[df_bl_check["Nombre Real"].astype(str).str.lower() == reg_nombre_real.strip().lower()].empty:
                        st.error("REGISTRO DENEGADO: Este jugador se encuentra en la Lista Negra.")
                    elif not df_c_check[df_c_check["Usuario"].astype(str).str.lower() == reg_usuario.strip().lower()].empty:
                        st.error("El nombre de usuario ya está registrado.")
                    elif not df_r_check[df_r_check["Nombre Real"].astype(str).str.lower() == reg_nombre_real.strip().lower()].empty:
                        st.error("Ya existe un registro con este nombre real.")
                    else:
                        nuevo_id = (int(df_r_check["ID"].max()) if not df_r_check.empty and "ID" in df_r_check.columns else len(df_r_check)) + 1
                        nueva_fila_roster = pd.DataFrame([{
                            "ID": nuevo_id, "Nick / ID": reg_nick.strip(), "Nombre Real": reg_nombre_real.strip(),
                            "Rol Principal": reg_rol_princ, "Rol Secundario": reg_rol_sec, "Personajes / Agentes": reg_personaje,
                            "Rango / Cima": reg_rango, "Cargo en Equipo": "Player", "Estado": reg_estado,
                            "Actividad": "Alta", "Contacto / Discord": reg_discord.strip(), "Notas / Observaciones": ""
                        }])
                        df_roster_updated = pd.concat([df_r_check, nueva_fila_roster], ignore_index=True)
                        guardar_en_bd(tb_roster, df_roster_updated)

                        nueva_fila_config = pd.DataFrame([{
                            "Usuario": reg_usuario.strip(), "Contraseña": reg_pass.strip(), "Rol": "jugador", "Nombre Real Vinculado": reg_nombre_real.strip()
                        }])
                        df_config_updated = pd.concat([df_c_check, nueva_fila_config], ignore_index=True)
                        guardar_en_bd(tb_config, df_config_updated)
                        st.success("Registro completado. Ya puede iniciar sesión.")
    st.stop()


# ==========================================
# APLICACIÓN PRINCIPAL (POST-LOGIN)
# ==========================================
if st.session_state.rol_usuario == "admin":
    st.sidebar.markdown(f"👤 **Usuario:** `{st.session_state.nombre_usuario}`\n🏷️ **Credencial:** `ADMIN`\n🎯 **División:** `{st.session_state.division_activa}`")
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Limpiar Caché / Recargar"):
        st.cache_data.clear()
        st.rerun()
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.rol_usuario = None
        st.rerun()
else:
    st.markdown("""<style>section[data-testid="stSidebar"] { display: none; }</style>""", unsafe_allow_html=True)

# --- NAVEGACIÓN ---
cols_nav = st.columns(5) if st.session_state.rol_usuario == "admin" else st.columns(4)
if cols_nav[0].button("Roster"): st.session_state.menu_activo = "Roster"
if cols_nav[1].button("Asistencia"): st.session_state.menu_activo = "Asistencia"
if cols_nav[2].button("Disciplina" if st.session_state.rol_usuario == "admin" else "Mis Sanciones"): st.session_state.menu_activo = "Disciplina"
if cols_nav[3].button("Tracker"): st.session_state.menu_activo = "Tracker"
if st.session_state.rol_usuario == "admin" and cols_nav[4].button("Config"): st.session_state.menu_activo = "Config"
st.markdown("<hr style='border: 1px solid rgba(255, 70, 85, 0.4); margin: 15px 0;'>", unsafe_allow_html=True)

key_roster_state = f"roster_{st.session_state.division_activa}"
key_disciplina_state = f"disciplina_{st.session_state.division_activa}"

st.session_state[key_roster_state] = cargar_roster_fresco(tb_roster)
st.session_state[key_disciplina_state] = cargar_incidencias_fresco(tb_disciplina)
df_config_actual = cargar_configuracion_fresco(tb_config)


# ==========================================
# SECCIÓN 1: ROSTER
# ==========================================
if st.session_state.menu_activo == "Roster":
    st.title(f"Gestión de Roster — {st.session_state.division_activa}")
    df_roster_actual = st.session_state[key_roster_state]
    
    jugadores_activos_temp = [j for j in df_roster_actual["Nombre Real"].tolist() if str(j).strip() != "" and str(j).lower() != "nan"]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("TOTAL JUGADORES", len(jugadores_activos_temp))
    col2.metric("TITULARES", len(df_roster_actual[df_roster_actual['Estado'] == 'Titular']) if not df_roster_actual.empty else 0)
    col3.metric("SEXTO PLAYER", len(df_roster_actual[df_roster_actual['Estado'] == 'Sexto player']) if not df_roster_actual.empty else 0)
    col4.metric("BANCA", len(df_roster_actual[df_roster_actual['Estado'] == 'Banca']) if not df_roster_actual.empty else 0)
    st.markdown("---")
    
    if st.session_state.rol_usuario == "admin":
        configuracion_columnas = {
            "Rol Principal": st.column_config.SelectboxColumn("Rol Principal", options=datos_juego_actual["Roles"]),
            "Rol Secundario": st.column_config.SelectboxColumn("Rol Secundario", options=datos_juego_actual["Roles"]),
            "Personajes / Agentes": st.column_config.SelectboxColumn("Personajes / Agentes", options=datos_juego_actual["Personajes"]),
            "Rango / Cima": st.column_config.SelectboxColumn("Rango / Cima", options=datos_juego_actual["Rangos"]),
            "Cargo en Equipo": st.column_config.SelectboxColumn("Cargo en Equipo", options=["Capitan", "Sub capitan", "Player", "Manager", "Coach", ""]),
            "Estado": st.column_config.SelectboxColumn("Estado", options=["Titular", "Banca", "Sexto player", "En Prueba", "Inactivo", ""]),
            "Actividad": st.column_config.SelectboxColumn("Actividad", options=["Alta", "Media", "Baja", ""]),
        }
        
        df_roster_editado = st.data_editor(
            df_roster_actual, num_rows="dynamic", use_container_width=True, hide_index=True,
            column_config=configuracion_columnas, height=350, key="editor_roster_principal"
        )
        
        if st.button("💾 GUARDAR CAMBIOS DE ROSTER EN SUPABASE"):
            guardar_en_bd(tb_roster, df_roster_editado)
            st.success("Roster sincronizado con la Base de Datos correctamente.")
            st.rerun()

        st.markdown("### Analítica Ejecutiva del Plantel")
        if not df_roster_editado.empty:
            df_validos_graf = df_roster_editado[df_roster_editado["Nombre Real"].astype(str).str.strip() != ""].copy()
            if not df_validos_graf.empty:
                g_col1, g_col2, g_col3 = st.columns(3)
                with g_col1:
                    df_roles = df_validos_graf["Rol Principal"].value_counts().reset_index()
                    df_roles.columns = ["Rol", "Cantidad"]
                    st.plotly_chart(px.pie(df_roles, names="Rol", values="Cantidad", title="Distribución por Rol", hole=0.5, color_discrete_sequence=px.colors.sequential.Reds).update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0"), use_container_width=True)
                with g_col2:
                    df_estados = df_validos_graf["Estado"].value_counts().reset_index()
                    df_estados.columns = ["Estado", "Cantidad"]
                    st.plotly_chart(px.bar(df_estados, x="Estado", y="Cantidad", title="Estado Actual", color="Estado", color_discrete_sequence=px.colors.sequential.Burg).update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0"), use_container_width=True)
                with g_col3:
                    df_rangos = df_validos_graf["Rango / Cima"].value_counts().reset_index()
                    df_rangos.columns = ["Rango", "Cantidad"]
                    st.plotly_chart(px.bar(df_rangos, x="Rango", y="Cantidad", title="Desglose por Rango", color="Rango", color_discrete_sequence=px.colors.sequential.Sunsetdark).update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0"), use_container_width=True)
            else: st.info("Faltan datos para graficar.")
    else:
        st.info("Modo Visualización.")
        st.dataframe(df_roster_actual, use_container_width=True, hide_index=True)


# ==========================================
# SECCIÓN 2: ASISTENCIA 
# ==========================================
elif st.session_state.menu_activo == "Asistencia":
    st.title(f"Control de Asistencia — {st.session_state.division_activa}")
    df_roster_actual = st.session_state[key_roster_state]
    jugadores_activos = [j for j in df_roster_actual["Nombre Real"].tolist() if str(j).strip() != "" and str(j).lower() != "nan"] if not df_roster_actual.empty else []
    
    if not jugadores_activos:
        st.warning("No hay jugadores registrados.")
    else:
        mes_seleccionado = st.selectbox("Seleccionar Mes Operativo", ["Septiembre", "Octubre", "Noviembre", "Diciembre"])
        df_asis_init = pd.DataFrame(columns=["Nombre Real", "Mes", "Días Hábiles"] + [str(i) for i in range(1, 32)])
        df_asistencia_guardada = cargar_o_crear_tabla(tb_asistencia, df_asis_init)
        
        dias_mes = [str(i) for i in range(1, 32)]
        df_mes = pd.DataFrame(index=jugadores_activos, columns=dias_mes).fillna("-")
        df_mes["Días Hábiles"] = 22
        df_mes["Mes"] = mes_seleccionado
        df_mes = df_mes.reset_index().rename(columns={"index": "Nombre Real"})

        if not df_asistencia_guardada.empty and "Mes" in df_asistencia_guardada.columns:
            df_mes_filtrado = df_asistencia_guardada[df_asistencia_guardada["Mes"] == mes_seleccionado]
            for idx, row in df_mes_filtrado.iterrows():
                if row["Nombre Real"] in df_mes["Nombre Real"].values:
                    for col in dias_mes + ["Días Hábiles"]:
                        if col in row and row[col] != "": df_mes.loc[df_mes["Nombre Real"] == row["Nombre Real"], col] = row[col]

        df_mes = df_mes.set_index("Nombre Real")
        def calcular_porcentaje(row):
            dias = int(row.get("Días Hábiles", 22))
            return "0%" if dias == 0 else f"{min(((sum(row[dias_mes] == 'P') + sum(row[dias_mes] == 'J') + (sum(row[dias_mes] == 'T') * 0.8)) / dias) * 100, 100):.0f}%"

        if st.session_state.rol_usuario == "admin":
            df_editado = st.data_editor(df_mes, use_container_width=True, key="editor_asistencia_mes")
            df_editado["% Asistencia"] = df_editado.apply(calcular_porcentaje, axis=1)
            st.dataframe(df_editado[["Mes", "Días Hábiles", "% Asistencia"]], use_container_width=True)
            if st.button("💾 GUARDAR ASISTENCIA EN SUPABASE"):
                df_para_guardar = df_editado.reset_index()
                df_final_asis = pd.concat([df_asistencia_guardada[df_asistencia_guardada["Mes"] != mes_seleccionado], df_para_guardar], ignore_index=True) if not df_asistencia_guardada.empty else df_para_guardar
                guardar_en_bd(tb_asistencia, df_final_asis)
                st.success("Asistencia sincronizada correctamente.")
        else:
            df_mes["% Asistencia"] = df_mes.apply(calcular_porcentaje, axis=1)
            if st.session_state.nombre_usuario in df_mes.index:
                st.markdown(f"### Tu Asistencia: {st.session_state.nombre_usuario}")
                st.dataframe(df_mes.loc[[st.session_state.nombre_usuario]], use_container_width=True)


# ==========================================
# SECCIÓN 3: DISCIPLINA / MIS SANCIONES
# ==========================================
elif st.session_state.menu_activo == "Disciplina":
    df_roster_actual = st.session_state[key_roster_state]
    df_incidencias_actual = st.session_state[key_disciplina_state]
    
    if st.session_state.rol_usuario == "admin":
        st.title(f"Panel Disciplinario — {st.session_state.division_activa}")
        jugadores_activos = [j for j in df_roster_actual["Nombre Real"].tolist() if str(j).strip() != "" and str(j).lower() != "nan"] if not df_roster_actual.empty else []
        sub_gen, sub_ind = st.tabs(["Registro General", "Expediente por Jugador"])
        
        with sub_gen:
            with st.form("form_anotacion", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    fecha = st.date_input("Fecha")
                    tipo = st.selectbox("Tipo de Incidencia", ["Positiva", "Negativa", "Advertencia"])
                    sancion = st.selectbox("Sanción", ["Ninguna", "Strike 1", "Strike 2", "Expulsión"])
                with c2:
                    jugador_sel = st.selectbox("Jugador Implicado", jugadores_activos if jugadores_activos else ["Sin jugadores"])
                    detalles = st.text_area("Notas / Observaciones detalladas")
                
                if st.form_submit_button("REGISTRAR INCIDENCIA"):
                    if jugador_sel != "Sin jugadores":
                        nueva_fila = pd.DataFrame([{"Fecha": str(fecha), "Jugador": jugador_sel, "Tipo": tipo, "Sanción": sancion, "Detalles": detalles}])
                        df_updated_disc = pd.concat([df_incidencias_actual, nueva_fila], ignore_index=True)
                        guardar_en_bd(tb_disciplina, df_updated_disc)
                        st.success("Incidencia registrada y sincronizada.")
                        st.rerun()
            st.dataframe(df_incidencias_actual, use_container_width=True, hide_index=True)

        with sub_ind:
            if jugadores_activos:
                jugador_individual = st.selectbox("Seleccionar Jugador:", jugadores_activos)
                df_filtrado = df_incidencias_actual[df_incidencias_actual["Jugador"] == jugador_individual]
                col_i1, col_i2 = st.columns(2)
                col_i1.metric("TOTAL ANOTACIONES", len(df_filtrado))
                col_i2.metric("SANCIONES ACTIVAS", len(df_filtrado[df_filtrado["Sanción"] != "Ninguna"]))
                st.dataframe(df_filtrado[["Fecha", "Tipo", "Sanción", "Detalles"]], use_container_width=True, hide_index=True) if not df_filtrado.empty else st.info("El jugador no registra incidencias.")
    else:
        st.title("Expediente Personal y Sanciones")
        df_mis_inc = df_incidencias_actual[df_incidencias_actual["Jugador"].str.lower() == st.session_state.nombre_usuario.lower()] if not df_incidencias_actual.empty else pd.DataFrame()
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("TOTAL ANOTACIONES", len(df_mis_inc))
        col_m2.metric("SANCIONES ACTIVAS", len(df_mis_inc[df_mis_inc["Sanción"] != "Ninguna"]))
        st.dataframe(df_mis_inc[["Fecha", "Tipo", "Sanción", "Detalles"]], use_container_width=True, hide_index=True) if not df_mis_inc.empty else st.success("Expediente impecable.")


# ==========================================
# SECCIÓN 4: TRACKER Y STATS
# ==========================================
elif st.session_state.menu_activo == "Tracker":
    st.title(f"Tracker y Estadísticas — {st.session_state.division_activa}")
    df_roster_actual = st.session_state[key_roster_state]
    df_validos_tracker = df_roster_actual[(df_roster_actual["Nick / ID"].astype(str).str.strip() != "") & (df_roster_actual["Nick / ID"].astype(str).str.lower() != "nan")] if not df_roster_actual.empty else pd.DataFrame()
    nicks_lista = df_validos_tracker["Nick / ID"].tolist()
    
    if nicks_lista:
        c_sel, c_btn = st.columns([2, 1])
        with c_sel:
            default_idx = nicks_lista.index(df_validos_tracker[df_validos_tracker["Nombre Real"].astype(str).str.lower() == st.session_state.nombre_usuario.lower()].iloc[0]["Nick / ID"]) if st.session_state.rol_usuario == "jugador" and not df_validos_tracker[df_validos_tracker["Nombre Real"].astype(str).str.lower() == st.session_state.nombre_usuario.lower()].empty else 0
            nick_seleccionado = st.selectbox("Seleccionar Integrante", nicks_lista, index=default_idx)
        
        with c_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if pd.notna(nick_seleccionado) and str(nick_seleccionado).strip() != "":
                nick_str = str(nick_seleccionado).strip()
                division_actual = st.session_state.division_activa
                
                # Enlace para Valorant (Requiere # en el ID)
                if "Valorant" in division_actual:
                    if "#" in nick_str:
                        url_tracker = f"https://tracker.gg/valorant/profile/riot/{nick_str.replace('#', '%23')}/overview"
                        st.link_button("VER PERFIL EXTERNO", url_tracker, use_container_width=True)
                    else:
                        st.info("Falta '#' en el ID (Ej: Jugador#TAG)")
                
                # Enlace para Overwatch (Battle.net cambia # por - en la URL)
                elif "Overwatch" in division_actual:
                    if "#" in nick_str or "-" in nick_str:
                        url_tracker = f"https://tracker.gg/overwatch/profile/battlenet/{nick_str.replace('#', '-')}/overview"
                        st.link_button("VER PERFIL EXTERNO", url_tracker, use_container_width=True)
                    else:
                        st.info("Falta '#' en el BattleTag (Ej: Jugador#1234)")
                
                # Enlace para Counter-Strike (FACEIT)
                elif "CS" in division_actual:
                    url_tracker = f"https://www.faceit.com/es/players/{nick_str}"
                    st.link_button("VER PERFIL EN FACEIT", url_tracker, use_container_width=True)
                    
            else:
                st.info("ID no configurado correctamente.")
                
        st.markdown(f"**Captura de Rendimiento — {nick_seleccionado}**")
        img_upload = st.file_uploader("Cargar captura", type=["png", "jpg", "jpeg"])
     if img_upload: 
        st.image(img_upload, use_container_width=True, caption=f"Registro analítico para {nick_seleccionado}")


# ==========================================
# SECCIÓN 5: CONFIGURACIÓN Y BORRADOS (SOLO ADMIN)
# ==========================================
elif st.session_state.menu_activo == "Config" and st.session_state.rol_usuario == "admin":
    st.title(f"Configuración de División — {st.session_state.division_activa}")
    
    # Sección especial para respaldo seguro de contraseña vía admin_config con llave primaria
    st.markdown("### Credenciales de Respaldo de Administrador")
    try:
        df_admin_sec = pd.read_sql_table(tb_admin_config, engine)
        admin_sec_editado = st.data_editor(df_admin_sec, num_rows="dynamic", use_container_width=True, hide_index=True, key="editor_admin_sec")
        if not admin_sec_editado.equals(df_admin_sec):
            guardar_en_bd(tb_admin_config, admin_sec_editado)
            st.success("Contraseña de respaldo actualizada en Supabase y app con éxito.")
            st.rerun()
    except Exception:
        pass

    st.markdown("### Usuarios y Credenciales Generales")
    config_editado = st.data_editor(df_config_actual, num_rows="dynamic", use_container_width=True, hide_index=True)
    if not config_editado.equals(df_config_actual):
        guardar_en_bd(tb_config, config_editado)
        st.success("Credenciales actualizadas.")
        st.rerun()

    st.markdown("### ⛔ Lista Negra (Blacklist)")
    st.info("Escribe el 'Nombre Real' del jugador que deseas bloquear. No podrá registrarse de nuevo ni iniciar sesión en su cuenta.")
    df_blacklist_actual = cargar_blacklist_fresco(tb_blacklist)
    blacklist_editado = st.data_editor(df_blacklist_actual, num_rows="dynamic", use_container_width=True, hide_index=True, key="editor_bl")
    if not blacklist_editado.equals(df_blacklist_actual):
        guardar_en_bd(tb_blacklist, blacklist_editado)
        st.success("Lista Negra actualizada correctamente.")
        st.rerun()

    df_roster_actual = st.session_state[key_roster_state]
    df_incidencias_actual = st.session_state[key_disciplina_state]

    st.markdown("### Panel de Eliminación Específica")
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        st.markdown("#### Eliminar Sanción")
        if not df_incidencias_actual.empty:
            opciones_sanciones = [f"[{row['Fecha']}] {row['Jugador']} - {row['Sanción']}" for idx, row in df_incidencias_actual.iterrows()]
            sancion_a_borrar = st.selectbox("Seleccionar sanción", [""] + opciones_sanciones)
            if st.button("ELIMINAR SANCIÓN") and sancion_a_borrar:
                nuevo_df_disc = df_incidencias_actual.drop(df_incidencias_actual.index[opciones_sanciones.index(sancion_a_borrar) - 1]).reset_index(drop=True)
                guardar_en_bd(tb_disciplina, nuevo_df_disc)
                st.success("Sanción eliminada.")
                st.rerun()
    with col_b2:
        st.markdown("#### Eliminar Jugador")
        jugadores_para_borrar = [j for j in df_roster_actual["Nombre Real"].tolist() if str(j).strip() != "" and str(j).lower() != "nan"] if not df_roster_actual.empty else []
        if jugadores_para_borrar:
            jugador_a_eliminar = st.selectbox("Seleccionar jugador", [""] + jugadores_para_borrar)
            if st.button("ELIMINAR INTEGRANTE") and jugador_a_eliminar:
                nuevo_df_roster = df_roster_actual[df_roster_actual["Nombre Real"] != jugador_a_eliminar].reset_index(drop=True)
                guardar_en_bd(tb_roster, nuevo_df_roster)
                guardar_en_bd(tb_config, df_config_actual[df_config_actual["Nombre Real Vinculado"].str.lower() != jugador_a_eliminar.lower()].reset_index(drop=True))
                st.success(f"{jugador_a_eliminar} dado de baja.")
                st.rerun()
    with col_b3:
        st.markdown("#### Limpiar Asistencia")
        mes_a_limpiar = st.selectbox("Mes a limpiar", ["Septiembre", "Octubre", "Noviembre", "Diciembre"])
        if st.button("RESETEAR MES"):
            df_asis_init = pd.DataFrame(columns=["Nombre Real", "Mes", "Días Hábiles"] + [str(i) for i in range(1, 32)])
            data_asis = cargar_o_crear_tabla(tb_asistencia, df_asis_init)
            if not data_asis.empty:
                guardar_en_bd(tb_asistencia, data_asis[data_asis["Mes"] != mes_a_limpiar])
                st.success(f"Registros de {mes_a_limpiar} limpiados.")
                st.rerun()

    st.markdown("### ZONA DE EMERGENCIA — RESET DIVISIÓN")
    with st.form("form_emergencia_reset", clear_on_submit=True):
        pass_confirmacion = st.text_input("Contraseña de Admin", type="password")
        if st.form_submit_button("VACIAR Y REINICIAR DIVISIÓN"):
            if not df_config_actual[(df_config_actual["Contraseña"].astype(str) == pass_confirmacion.strip()) & (df_config_actual["Rol"].astype(str).str.lower() == "admin")].empty:
                guardar_en_bd(tb_roster, DATOS_INICIALES_ROSTER)
                guardar_en_bd(tb_asistencia, pd.DataFrame(columns=["Nombre Real", "Mes", "Días Hábiles"] + [str(i) for i in range(1, 32)]))
                guardar_en_bd(tb_disciplina, pd.DataFrame(columns=["Fecha", "Jugador", "Tipo", "Sanción", "Detalles"]))
                guardar_en_bd(tb_config, DATOS_INICIALES_CONFIG)
                guardar_en_bd(tb_blacklist, DATOS_INICIALES_BLACKLIST)
                st.success(f"¡División {st.session_state.division_activa} reiniciada a valores de fábrica!")
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
