import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Scarlet Roster - Sistema Seguro en Tiempo Real", page_icon="🔥", layout="wide")

# --- ESTILOS CORPORATIVOS Y BLOQUEO RADICAL DE EXTENSIONES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    .stApp { background-color: #0f1923; color: #ece8e1; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #ff4655; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; }
    .stButton>button { 
        background-color: transparent; color: #ff4655; border: 1px solid #ff4655; 
        border-radius: 4px; font-weight: 600; transition: all 0.3s ease; 
    }
    .stButton>button:hover { background-color: #ff4655; color: #0f1923; }
    .stSelectbox label, .stTextInput label, .stMultiSelect label { color: #ece8e1; font-weight: 600; font-size: 0.9rem; }
    div[data-testid="stMetricValue"] { color: #ff4655; font-weight: 700; }

    /* CLASE CSS PARA SIMULAR CONTRASEÑA EVITANDO QUE LAS EXTENSIONES LA DETECTEN COMO INPUT DE LOGIN */
    input.fake-password {
        -webkit-text-security: disc !important;
        text-security: disc !important;
    }
    </style>

    <!-- SCRIPT DE JAVASCRIPT PARA MATAR EL AUTOCOMPLETADO Y RESTRICCIONES DE EXTENSIONES -->
    <script>
    function desactivarAutocompletado() {
        const inputs = document.querySelectorAll('input');
        inputs.forEach(input => {
            input.setAttribute('autocomplete', 'off');
            input.setAttribute('autocorrect', 'off');
            input.setAttribute('autocapitalize', 'off');
            input.setAttribute('spellcheck', 'false');
            input.setAttribute('data-lpignore', 'true'); // Ignorar por LastPass / Dashlane
            input.setAttribute('data-form-type', 'other'); // Despistar extensiones de correo
        });
    }
    window.addEventListener('DOMContentLoaded', desactivarAutocompletado);
    const observer = new MutationObserver(desactivarAutocompletado);
    observer.observe(document.body, { childList: true, subtree: true });
    </script>
""", unsafe_allow_html=True)

# --- DATOS INICIALES PREDETERMINADOS ---
DATOS_INICIALES_ROSTER = pd.DataFrame({
    "ID": [1, 2, 3, 4, 5, 6, 7],
    "Riot ID (Nick#TAG)": ["Mazinhooo#lovsf", "Lionora#ZERO", "BestiaDelTrap#ARK", "leO#deus", "ELNIÑOMARAVILLA#14y", "Lotenesquepedir#boka", "Shuten#2006"],
    "Nombre Real": ["Maximiliano", "Lientur", "Facundo", "Leonardo", "Felipe", "Ian", "Leonel"],
    "Rol Principal": ["Iniciador", "Controlador", "Duelista", "Centinela", "Controlador", "Centinela", "Duelista"],
    "Rol Secundario": ["Centinela", "Iniciador", "", "Duelista", "Centinela", "Iniciador", "Centinela"],
    "Agentes Principales": ["Sova, Fade", "Omen, Fade", "Jett, Neon, Raze", "Cypher, Vyse, Chamber", "Chamber, Cypher, Vyse", "Breach, Sova, Fade", "Neon, Phoenix, Iso"],
    "Rango / Cima": ["Ascendente 3", "Plata", "Ascendente 2", "Inmortal 1", "Inmortal 1", "Ascendente 3", "Ascendente 3"],
    "Cargo en Equipo": ["Capitan", "Sub capitan", "Player", "Player", "Player", "Player", "Player"],
    "Estado": ["Titular", "Banca", "Titular", "Titular", "Titular", "Sexto player", "Titular"],
    "Actividad": ["Alta", "Alta", "Alta", "Media", "Alta", "Media", "Media"],
    "Contacto / Discord": ["Mazzito", "LINO", "facuu", "Leo", "felipoomo", "Iansuki", "Shuten"],
    "Notas / Observaciones": ["", "", "", "", "", "", ""]
})

DATOS_INICIALES_CONFIG = pd.DataFrame({
    "Usuario": ["admin"],
    "Contraseña": ["admin123"],
    "Rol": ["admin"],
    "Nombre Real Vinculado": [""]
})

# --- CONEXIÓN Y CREACIÓN AUTOMÁTICA DE MULTI-HOJAS ---
@st.cache_resource
def conectar_google_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        spreadsheet = client.open("crea el proyecto en formato hoja de calculo como...")
        
        try:
            sheet_roster = spreadsheet.worksheet("Control General")
        except gspread.exceptions.WorksheetNotFound:
            sheet_roster = spreadsheet.add_worksheet(title="Control General", rows="100", cols="15")
            sheet_roster.update([DATOS_INICIALES_ROSTER.columns.values.tolist()] + DATOS_INICIALES_ROSTER.values.tolist())

        try:
            sheet_asistencia = spreadsheet.worksheet("Asistencia")
        except gspread.exceptions.WorksheetNotFound:
            sheet_asistencia = spreadsheet.add_worksheet(title="Asistencia", rows="100", cols="35")
            df_asistencia_init = pd.DataFrame(columns=["Nombre Real", "Mes", "Días Hábiles"] + [str(i) for i in range(1, 32)])
            sheet_asistencia.update([df_asistencia_init.columns.values.tolist()])

        try:
            sheet_disciplina = spreadsheet.worksheet("Disciplina")
        except gspread.exceptions.WorksheetNotFound:
            sheet_disciplina = spreadsheet.add_worksheet(title="Disciplina", rows="100", cols="10")
            df_disc_init = pd.DataFrame(columns=["Fecha", "Jugador", "Tipo", "Sanción", "Detalles"])
            sheet_disciplina.update([df_disc_init.columns.values.tolist()])

        try:
            sheet_config = spreadsheet.worksheet("Configuracion")
        except gspread.exceptions.WorksheetNotFound:
            sheet_config = spreadsheet.add_worksheet(title="Configuracion", rows="50", cols="5")
            sheet_config.update([DATOS_INICIALES_CONFIG.columns.values.tolist()] + DATOS_INICIALES_CONFIG.values.tolist())
            
        return spreadsheet, sheet_roster, sheet_asistencia, sheet_disciplina, sheet_config
    except Exception as e:
        st.error(f"Error crítico conectando a Google Sheets: {e}")
        return None, None, None, None, None

spreadsheet, sheet_roster, sheet_asistencia, sheet_disciplina, sheet_config = conectar_google_sheets()

def guardar_en_sheet(sheet_obj, df):
    if sheet_obj is not None:
        try:
            df_clean = df.fillna("")
            data_to_upload = [df_clean.columns.values.tolist()] + df_clean.values.tolist()
            sheet_obj.clear()
            sheet_obj.update(data_to_upload)
        except Exception as e:
            st.error(f"Error al sincronizar con Google Sheets: {e}")

def cargar_roster_fresco():
    if sheet_roster is not None:
        try:
            data = sheet_roster.get_all_records()
            if not data: return DATOS_INICIALES_ROSTER.copy()
            df = pd.DataFrame(data)
            return DATOS_INICIALES_ROSTER.copy() if df.empty else df
        except:
            return DATOS_INICIALES_ROSTER.copy()
    return DATOS_INICIALES_ROSTER.copy()

def cargar_incidencias_fresco():
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

def cargar_configuracion_fresco():
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


# ==========================================
# PANTALLA DE LOGIN / REGISTRO / SELECCIÓN
# ==========================================
if not st.session_state.autenticado:
    st.title("🔥 Scarlet Roster - Control de Acceso")
    st.markdown("Inicia sesión o regístrate por primera vez si fuiste aceptado en la división.")
    
    df_config_live = cargar_configuracion_fresco()
    
    tab_login_admin, tab_login_player, tab_reg_player = st.tabs(["🛡️ Admin", "🎮 Iniciar Sesión (Jugador)", "✨ Registro de Nuevo Jugador"])
    
    # 1. Pestaña Admin
    with tab_login_admin:
        st.markdown("### Acceso Administrador")
        with st.form("form_login_admin"):
            user_admin = st.text_input("Usuario Administrador", key="input_admin_user")
            
            # Campo de contraseña blindado contra extensiones mediante HTML personalizado
            st.markdown("Contraseña", unsafe_allow_html=True)
            pass_admin = st.text_input("ContraseñaAdminOculta", label_visibility="collapsed", key="input_admin_pass_custom")
            st.markdown('<script>document.querySelector(\'input[aria-label="ContraseñaAdminOculta"]\').type = "text"; document.querySelector(\'input[aria-label="ContraseñaAdminOculta"]\').classList.add("fake-password");</script>', unsafe_allow_html=True)
            
            submit_admin = st.form_submit_button("Entrar como Admin")
            
            if submit_admin:
                match = df_config_live[(df_config_live["Usuario"].astype(str).str.lower() == user_admin.strip().lower()) & 
                                       (df_config_live["Contraseña"].astype(str) == pass_admin.strip()) & 
                                       (df_config_live["Rol"].astype(str).str.lower() == "admin")]
                if not match.empty:
                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = "admin"
                    st.session_state.nombre_usuario = "Administrador"
                    st.success("✅ ¡Acceso concedido como Administrador!")
                    st.rerun()
                else:
                    st.error("❌ Credenciales o permisos de administrador incorrectos.")

    # 2. Pestaña Login Jugador
    with tab_login_player:
        st.markdown("### Iniciar Sesión (Jugadores)")
        with st.form("form_login_jugador"):
            user_player = st.text_input("Tu Usuario", key="input_player_user")
            
            st.markdown("Tu Contraseña", unsafe_allow_html=True)
            pass_player = st.text_input("TuContrasenaPlayerOculta", label_visibility="collapsed", key="input_player_pass_custom")
            st.markdown('<script>document.querySelector(\'input[aria-label="TuContrasenaPlayerOculta"]\').type = "text"; document.querySelector(\'input[aria-label="TuContrasenaPlayerOculta"]\').classList.add("fake-password");</script>', unsafe_allow_html=True)
            
            submit_player = st.form_submit_button("Iniciar Sesión")
            
            if submit_player:
                match = df_config_live[(df_config_live["Usuario"].astype(str).str.lower() == user_player.strip().lower()) & 
                                       (df_config_live["Contraseña"].astype(str) == pass_player.strip())]
                if not match.empty:
                    row_match = match.iloc[0]
                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = "jugador"
                    st.session_state.nombre_usuario = row_match["Nombre Real Vinculado"]
                    st.success(f"✅ ¡Bienvenido, {st.session_state.nombre_usuario}!")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")

    # 3. Pestaña Registro de Nuevo Jugador
    with tab_reg_player:
        st.markdown("### ✨ Registro de Ingreso para Nuevo Jugador")
        
        OPCIONES_ROLES = ["Duelista", "Iniciador", "Controlador", "Centinela", "Flex"]
        OPCIONES_RANGOS = ["Hierro", "Bronce", "Plata", "Oro", "Platino", "Diamante", "Ascendente 1", "Ascendente 2", "Ascendente 3", "Inmortal 1", "Inmortal 2", "Inmortal 3", "Radiante"]
        OPCIONES_ESTADO = ["Titular", "Banca", "Sexto player", "En Prueba"]
        
        with st.form("form_registro_nuevo_jugador"):
            c_reg1, c_reg2 = st.columns(2)
            with c_reg1:
                reg_nombre_real = st.text_input("Tu Nombre Real")
                reg_riot_id = st.text_input("Riot ID (Ej: Nick#TAG)")
                reg_rol_princ = st.selectbox("Rol Principal", OPCIONES_ROLES)
                reg_rol_sec = st.selectbox("Rol Secundario", [""] + OPCIONES_ROLES)
                reg_rango = st.selectbox("Rango / Cima Actual", OPCIONES_RANGOS)
            with c_reg2:
                reg_estado = st.selectbox("Estado Asignado", OPCIONES_ESTADO)
                reg_discord = st.text_input("Usuario de Discord / Contacto")
                reg_usuario = st.text_input("Elige tu Nombre de Usuario nuevo")
                
                st.markdown("Elige tu Contraseña", unsafe_allow_html=True)
                reg_pass = st.text_input("RegPassOculta", label_visibility="collapsed", key="input_reg_pass_custom")
                st.markdown('<script>document.querySelector(\'input[aria-label="RegPassOculta"]\').type = "text"; document.querySelector(\'input[aria-label="RegPassOculta"]\').classList.add("fake-password");</script>', unsafe_allow_html=True)
                
                st.markdown("Confirma tu Contraseña", unsafe_allow_html=True)
                reg_pass_conf = st.text_input("RegPassConfOculta", label_visibility="collapsed", key="input_reg_pass_conf_custom")
                st.markdown('<script>document.querySelector(\'input[aria-label="RegPassConfOculta"]\').type = "text"; document.querySelector(\'input[aria-label="RegPassConfOculta"]\').classList.add("fake-password");</script>', unsafe_allow_html=True)
            
            submit_nuevo_jugador = st.form_submit_button("Completar Registro y Entrar al Roster")
            
            if submit_nuevo_jugador:
                if not reg_nombre_real.strip() or not reg_riot_id.strip() or not reg_usuario.strip() or not reg_pass.strip():
                    st.error("❌ Los campos Nombre Real, Riot ID, Usuario y Contraseña son obligatorios.")
                elif reg_pass != reg_pass_conf:
                    st.error("❌ Las contraseñas no coinciden.")
                else:
                    df_c_check = cargar_configuracion_fresco()
                    df_r_check = cargar_roster_fresco()
                    
                    if not df_c_check[df_c_check["Usuario"].astype(str).str.lower() == reg_usuario.strip().lower()].empty:
                        st.error("❌ Este nombre de usuario ya está en uso. Elige otro.")
                    elif not df_r_check[df_r_check["Nombre Real"].astype(str).str.lower() == reg_nombre_real.strip().lower()].empty:
                        st.error("❌ Ya existe un jugador registrado con este Nombre Real en el Roster.")
                    else:
                        try:
                            max_id = int(df_r_check["ID"].max()) if not df_r_check.empty and "ID" in df_r_check.columns else 0
                        except:
                            max_id = len(df_r_check)
                        nuevo_id = max_id + 1

                        nueva_fila_roster = pd.DataFrame([{
                            "ID": nuevo_id,
                            "Riot ID (Nick#TAG)": reg_riot_id.strip(),
                            "Nombre Real": reg_nombre_real.strip(),
                            "Rol Principal": reg_rol_princ,
                            "Rol Secundario": reg_rol_sec if reg_rol_sec != "" else "",
                            "Agentes Principales": "",
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

                        st.success("✅ ¡Registro completado con éxito! Ya formas parte del Roster y puedes iniciar sesión en la pestaña anterior.")
    
    st.stop()


# ==========================================
# APLICACIÓN PRINCIPAL (POST-LOGIN)
# ==========================================
st.sidebar.markdown(f"👤 **Conectado como:** `{st.session_state.nombre_usuario}`")
st.sidebar.markdown(f"🏷️ **Rol:** `{st.session_state.rol_usuario.upper()}`")

if st.sidebar.button("🔄 Forzar Recarga Total"):
    st.rerun()

if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.autenticado = False
    st.session_state.rol_usuario = None
    st.session_state.nombre_usuario = None
    st.rerun()

st.sidebar.markdown("---")

df_roster_actual = cargar_roster_fresco()
df_incidencias_actual = cargar_incidencias_fresco()
df_config_actual = cargar_configuracion_fresco()

AGENTES_POR_ROL = {
    "Duelista": ["Jett", "Neon", "Raze", "Reyna", "Phoenix", "Yoru", "Iso"],
    "Iniciador": ["Sova", "Fade", "Breach", "KAY/O", "Skye", "Gekko"],
    "Controlador": ["Omen", "Astra", "Viper", "Brimstone", "Harbor", "Clove"],
    "Centinela": ["Killjoy", "Cypher", "Sage", "Chamber", "Deadlock", "Vyse"]
}

OPCIONES_ROLES = ["Duelista", "Iniciador", "Controlador", "Centinela", "Flex", ""]
OPCIONES_RANGOS = ["Hierro", "Bronce", "Plata", "Oro", "Platino", "Diamante", "Ascendente 1", "Ascendente 2", "Ascendente 3", "Inmortal 1", "Inmortal 2", "Inmortal 3", "Radiante", ""]
OPCIONES_CARGOS = ["Capitan", "Sub capitan", "Player", "Manager", "Coach", ""]
OPCIONES_ESTADO = ["Titular", "Banca", "Sexto player", "En Prueba", "Inactivo", ""]
OPCIONES_ACTIVIDAD = ["Alta", "Media", "Baja", ""]

if st.session_state.rol_usuario == "admin":
    tab_roster, tab_asistencia, tab_historial, tab_stats, tab_config = st.tabs([
        "📝 Roster", "📅 Asistencia", "🛡️ Disciplina", "📈 Tracker", "⚙️ Config / Borrados"
    ])
else:
    tab_roster, tab_asistencia, tab_historial, tab_stats = st.tabs([
        "📝 Roster", "📅 Asistencia", "🛡️ Mis Sanciones", "📈 Tracker"
    ])

# ==========================================
# PESTAÑA 1: ROSTER
# ==========================================
with tab_roster:
    st.title("🔥 Gestión de Roster")
    
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
            "Agentes Principales": st.column_config.TextColumn("Agentes Principales (Gestionable abajo ⬇️)", disabled=True),
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
            st.success("✅ Roster actualizado y sincronizado en tiempo real.")
            st.rerun()

        st.markdown("---")
        st.markdown("### 🎭 Gestor Dinámico de Agentes")
        riot_ids_actuales = [r for r in df_roster_actual["Riot ID (Nick#TAG)"].tolist() if str(r).strip() != "" and str(r).lower() != "nan"]
        
        if len(riot_ids_actuales) > 0:
            c_sel, c_form = st.columns([1, 2])
            with c_sel:
                jugador_agentes = st.selectbox("1. Selecciona al Riot ID:", [""] + riot_ids_actuales, key="select_riot_agente")
            
            if jugador_agentes != "":
                with c_form:
                    filas_coinciondentes = df_roster_actual[df_roster_actual["Riot ID (Nick#TAG)"] == jugador_agentes]
                    if not filas_coinciondentes.empty:
                        idx = filas_coinciondentes.index[0]
                        rol_1 = str(df_roster_actual.at[idx, "Rol Principal"])
                        rol_2 = str(df_roster_actual.at[idx, "Rol Secundario"])
                        
                        opciones_validas = []
                        if rol_1 in AGENTES_POR_ROL: opciones_validas.extend(AGENTES_POR_ROL[rol_1])
                        if rol_2 in AGENTES_POR_ROL: opciones_validas.extend(AGENTES_POR_ROL[rol_2])
                        opciones_validas = list(set(opciones_validas))
                        
                        if not opciones_validas:
                            st.warning("⚠️ Asigna al menos un Rol válido en la tabla superior para este jugador.")
                        else:
                            agentes_str = df_roster_actual.at[idx, "Agentes Principales"]
                            agentes_actuales = [a.strip() for a in str(agentes_str).split(",")] if pd.notna(agentes_str) and str(agentes_str).strip() != "" else []
                            agentes_actuales = [a for a in agentes_actuales if a in opciones_validas]
                            
                            nuevos_agentes = st.multiselect(
                                f"2. Agentes disponibles para {jugador_agentes} ({rol_1} / {rol_2}):",
                                options=opciones_validas,
                                default=agentes_actuales,
                                key=f"multi_agentes_{jugador_agentes}"
                            )
                            
                            nuevos_str = ", ".join(nuevos_agentes)
                            if agentes_str != nuevos_str:
                                df_roster_actual.at[idx, "Agentes Principales"] = nuevos_str
                                guardar_en_sheet(sheet_roster, df_roster_actual)
                                st.rerun()
    else:
        st.info("👁️ Modo Visualización: Solo puedes ver el estado del equipo y consultar los agentes.")
        st.dataframe(df_roster_actual, use_container_width=True, hide_index=True)


# ==========================================
# PESTAÑA 2: ASISTENCIA 
# ==========================================
with tab_asistencia:
    st.title("📅 Control de Asistencia")
    jugadores_activos = [j for j in df_roster_actual["Nombre Real"].tolist() if str(j).strip() != "" and str(j).lower() != "nan"]
    
    if len(jugadores_activos) == 0:
        st.warning("No hay jugadores registrados en el Roster.")
    else:
        mes_seleccionado = st.selectbox("Seleccionar Mes", ["Septiembre", "Octubre", "Noviembre", "Diciembre"])
        
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

            if st.button("💾 Guardar Cambios de Asistencia en Sheets"):
                df_para_guardar = df_editado.reset_index()
                if not df_asistencia_guardada.empty:
                    otros_meses = df_asistencia_guardada[df_asistencia_guardada["Mes"] != mes_seleccionado]
                    df_final_asis = pd.concat([otros_meses, df_para_guardar], ignore_index=True)
                else:
                    df_final_asis = df_para_guardar
                guardar_en_sheet(sheet_asistencia, df_final_asis)
                st.success("✅ ¡Asistencia guardada correctamente!")
        else:
            df_mes["% Asistencia"] = df_mes.apply(calcular_porcentaje, axis=1)
            if st.session_state.nombre_usuario in df_mes.index:
                df_personal = df_mes.loc[[st.session_state.nombre_usuario]]
                st.markdown(f"### Tu Asistencia: {st.session_state.nombre_usuario}")
                st.dataframe(df_personal, use_container_width=True)
            else:
                st.info("No se encontró registro de asistencia asociado a tu usuario.")


# ==========================================
# PESTAÑA 3: DISCIPLINA / MIS SANCIONES
# ==========================================
with tab_historial:
    if st.session_state.rol_usuario == "admin":
        st.title("🛡️ Panel de Disciplina y Conducta")
        jugadores_activos = [j for j in df_roster_actual["Nombre Real"].tolist() if str(j).strip() != "" and str(j).lower() != "nan"]
        
        sub_gen, sub_ind = st.tabs(["📋 Historial General e Ingreso", "👤 Anotaciones por Jugador"])
        
        with sub_gen:
            st.markdown("### Registrar Nueva Incidencia o Anotación")
            with st.form("form_anotacion", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    fecha = st.date_input("Fecha")
                    tipo = st.selectbox("Tipo de Incidencia", ["Positiva", "Negativa", "Advertencia"])
                    sancion = st.selectbox("Sanción", ["Ninguna", "Strike 1", "Strike 2", "Expulsión"])
                with c2:
                    jugador_sel = st.selectbox("Jugador Implicado", jugadores_activos)
                    detalles = st.text_area("Notas / Observaciones detalladas")
                
                if st.form_submit_button("Guardar y Sincronizar Registro"):
                    nueva_fila = pd.DataFrame([{
                        "Fecha": str(fecha),
                        "Jugador": jugador_sel,
                        "Tipo": tipo,
                        "Sanción": sancion,
                        "Detalles": detalles
                    }])
                    df_disc_actualizado = pd.concat([df_incidencias_actual, nueva_fila], ignore_index=True)
                    guardar_en_sheet(sheet_disciplina, df_disc_actualizado)
                    st.success(f"✅ Incidencia registrada para {jugador_sel}.")
                    st.rerun()
            
            st.markdown("---")
            st.markdown("### Historial Completo de Incidencias (Tiempo Real)")
            if not df_incidencias_actual.empty:
                st.dataframe(df_incidencias_actual, use_container_width=True, hide_index=True)
            else:
                st.info("No hay incidencias registradas todavía.")

        with sub_ind:
            st.markdown("### Expediente Individual por Jugador")
            jugador_individual = st.selectbox("Selecciona un jugador:", jugadores_activos, key="select_jugador_ind")
            if not df_incidencias_actual.empty:
                df_filtrado = df_incidencias_actual[df_incidencias_actual["Jugador"] == jugador_individual]
                col_i1, col_i2 = st.columns(2)
                col_i1.metric(f"TOTAL ANOTACIONES", len(df_filtrado))
                col_i2.metric("SANCIONES ACTIVAS", len(df_filtrado[df_filtrado["Sanción"] != "Ninguna"]))
                st.markdown("---")
                if not df_filtrado.empty:
                    st.dataframe(df_filtrado[["Fecha", "Tipo", "Sanción", "Detalles"]], use_container_width=True, hide_index=True)
                else:
                    st.info("El jugador no tiene anotaciones.")
            else:
                st.info("Aún no hay incidencias.")
    else:
        st.title("🛡️ Mis Sanciones y Anotaciones")
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
                st.success("✨ ¡Excelente! No tienes ninguna sanción ni advertencia registrada en tu expediente.")
        else:
            st.info("No hay registros en el sistema.")


# ==========================================
# PESTAÑA 4: TRACKER Y STATS
# ==========================================
with tab_stats:
    st.title("📈 Tracker y Estadísticas (Stats Premier)")
    jugadores_activos = [j for j in df_roster_actual["Nombre Real"].tolist() if str(j).strip() != "" and str(j).lower() != "nan"]
    
    if len(jugadores_activos) > 0:
        c_sel, c_btn = st.columns([2, 1])
        with c_sel: 
            nombres_roster = df_roster_actual[df_roster_actual["Nombre Real"].astype(str).str.strip() != ""]
            dic_nombres_riot = dict(zip(nombres_roster["Nombre Real"], nombres_roster["Riot ID (Nick#TAG)"]))
            
            default_idx = 0
            if st.session_state.rol_usuario == "jugador" and st.session_state.nombre_usuario in list(dic_nombres_riot.keys()):
                default_idx = list(dic_nombres_riot.keys()).index(st.session_state.nombre_usuario)
                
            jugador_stat = st.selectbox("Seleccionar Jugador", list(dic_nombres_riot.keys()), index=default_idx, key="select_stats_jugador")
            
        with c_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            riot_id_seleccionado = dic_nombres_riot.get(jugador_stat, "")
            if pd.notna(riot_id_seleccionado) and "#" in str(riot_id_seleccionado):
                url = f"https://tracker.gg/valorant/profile/riot/{str(riot_id_seleccionado).replace('#', '%23')}/overview"
                st.link_button(f"🔴 Perfil en Tracker.gg", url, use_container_width=True)
            else:
                st.error("Riot ID no válido en Sheets.")

        st.markdown("---")
        st.markdown(f"**Captura de Rendimiento - {jugador_stat}**")
        img_upload = st.file_uploader("Sube una captura de pantalla del Tracker (Opcional)", type=["png", "jpg", "jpeg"])
        if img_upload:
            st.image(img_upload, use_column_width=True, caption=f"Última actualización de stats para {jugador_stat}")
    else:
        st.warning("No hay jugadores en el Roster.")


# ==========================================
# PESTAÑA 5: CONFIGURACIÓN Y BORRADOS (SOLO ADMIN)
# ==========================================
if st.session_state.rol_usuario == "admin":
    with tab_config:
        st.title("⚙️ Configuración y Panel de Borrado Avanzado")
        st.markdown("Gestiona las credenciales de la hoja **Configuracion** y utiliza los botones de borrado específico por sección.")
        
        st.markdown("### 🔑 Credenciales de Acceso")
        config_editado = st.data_editor(
            df_config_actual,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="editor_configuracion"
        )
        
        if not config_editado.equals(df_config_actual):
            guardar_en_sheet(sheet_config, config_editado)
            st.success("✅ ¡Credenciales guardadas y sincronizadas!")
            st.rerun()

        st.markdown("---")
        st.markdown("### 🗑️ Panel de Borrado Específico (Administrador)")
        st.warning("⚠️ Las acciones de borrado eliminan permanentemente la información seleccionada de la base de datos de Google Sheets.")
        
        col_b1, col_b2, col_b3 = st.columns(3)
        
        with col_b1:
            st.markdown("#### Borrar Sanción")
            if not df_incidencias_actual.empty:
                opciones_sanciones = [f"[{row['Fecha']}] {row['Jugador']} - {row['Sanción']} ({row['Detalles'][:20]}...)" for idx, row in df_incidencias_actual.iterrows()]
                sancion_a_borrar = st.selectbox("Selecciona sanción a eliminar", [""] + opciones_sanciones, key="sel_borrar_sancion")
                
                if st.button("🗑️ Eliminar Sanción Seleccionada"):
                    if sancion_a_borrar != "":
                        idx_seleccionado = opciones_sanciones.index(sancion_a_borrar)
                        df_disc_nuevo = df_incidencias_actual.drop(df_incidencias_actual.index[idx_seleccionado]).reset_index(drop=True)
                        guardar_en_sheet(sheet_disciplina, df_disc_nuevo)
                        st.success("✅ Sanción eliminada con éxito.")
                        st.rerun()
            else:
                st.info("No hay sanciones para borrar.")

        with col_b2:
            st.markdown("#### Borrar Jugador del Roster")
            jugadores_para_borrar = [j for j in df_roster_actual["Nombre Real"].tolist() if str(j).strip() != "" and str(j).lower() != "nan"]
            if len(jugadores_para_borrar) > 0:
                jugador_a_eliminar = st.selectbox("Selecciona jugador a eliminar", [""] + jugadores_para_borrar, key="sel_borrar_jugador")
                
                if st.button("🗑️ Eliminar Jugador del Roster"):
                    if jugador_a_eliminar != "":
                        df_roster_nuevo = df_roster_actual[df_roster_actual["Nombre Real"] != jugador_a_eliminar].reset_index(drop=True)
                        guardar_en_sheet(sheet_roster, df_roster_nuevo)
                        
                        df_config_live_b = cargar_configuracion_fresco()
                        df_config_nuevo = df_config_live_b[df_config_live_b["Nombre Real Vinculado"].str.lower() != jugador_a_eliminar.lower()].reset_index(drop=True)
                        guardar_en_sheet(sheet_config, df_config_nuevo)
                        
                        st.success(f"✅ Jugador {jugador_a_eliminar} eliminado del Roster y de los accesos.")
                        st.rerun()
            else:
                st.info("No hay jugadores en el Roster.")

        with col_b3:
            st.markdown("#### Limpiar Asistencia")
            if sheet_asistencia is not None:
                mes_a_limpiar = st.selectbox("Mes a limpiar registros", ["Septiembre", "Octubre", "Noviembre", "Diciembre"], key="sel_limpiar_mes")
                if st.button("🗑️ Resetear Asistencia del Mes"):
                    try:
                        data_asis_all = sheet_asistencia.get_all_records()
                        if data_asis_all:
                            df_asis_all = pd.DataFrame(data_asis_all)
                            df_asis_filtrado = df_asis_all[df_asis_all["Mes"] != mes_a_limpiar]
                            guardar_en_sheet(sheet_asistencia, df_asis_filtrado)
                            st.success(f"✅ Registros del mes de {mes_a_limpiar} limpiados correctamente.")
                            st.rerun()
                        else:
                            st.info("La hoja de asistencia está vacía.")
                    except Exception as e:
                        st.error(f"Error al limpiar asistencia: {e}")

        st.markdown("---")
        st.markdown("### 🚨 ZONA DE EMERGENCIA - RESET TOTAL")
        st.error("⚠️ **ADVERTENCIA CRÍTICA:** Esto borrará absolutamente **toda** la información de Google Sheets (Roster, Asistencia, Disciplina y Credenciales) y la restablecerá a los valores iniciales de fábrica.")
        
        with st.form("form_emergencia_reset", clear_on_submit=True):
            st.markdown("Para autorizar este vaciado total, ingresa tu **contraseña de administrador** actual:")
            
            st.markdown("Contraseña de Administrador de Confirmación", unsafe_allow_html=True)
            pass_confirmacion_emergencia = st.text_input("PassEmergenciaOculta", label_visibility="collapsed", key="input_emergencia_pass_custom")
            st.markdown('<script>document.querySelector(\'input[aria-label="PassEmergenciaOculta"]\').type = "text"; document.querySelector(\'input[aria-label="PassEmergenciaOculta"]\'].classList.add("fake-password");</script>', unsafe_allow_html=True)
            
            btn_ejecutar_emergencia = st.form_submit_button("🔥 VACIAR Y REINICIAR TODA LA BASE DE DATOS")
            
            if btn_ejecutar_emergencia:
                if not pass_confirmacion_emergencia.strip():
                    st.error("❌ Debes ingresar la contraseña de administrador.")
                else:
                    match_admin = df_config_actual[(df_config_actual["Contraseña"].astype(str) == pass_confirmacion_emergencia.strip()) & 
                                                   (df_config_actual["Rol"].astype(str).str.lower() == "admin")]
                    if match_admin.empty:
                        st.error("❌ Contraseña incorrecta. Operación cancelada por seguridad.")
                    else:
                        try:
                            guardar_en_sheet(sheet_roster, DATOS_INICIALES_ROSTER)
                            
                            df_asistencia_init = pd.DataFrame(columns=["Nombre Real", "Mes", "Días Hábiles"] + [str(i) for i in range(1, 32)])
                            guardar_en_sheet(sheet_asistencia, df_asistencia_init)
                            
                            df_disc_init = pd.DataFrame(columns=["Fecha", "Jugador", "Tipo", "Sanción", "Detalles"])
                            guardar_en_sheet(sheet_disciplina, df_disc_init)
                            
                            guardar_en_sheet(sheet_config, DATOS_INICIALES_CONFIG)
                            
                            st.success("✅ ¡Base de datos completamente vaciada y reiniciada a fábrica con éxito!")
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error crítico durante el reseteo de emergencia: {e}")
