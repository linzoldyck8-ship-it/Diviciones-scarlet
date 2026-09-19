import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Scarlet Roster - Sistema Seguro", page_icon="🔥", layout="wide")

# --- ESTILOS CORPORATIVOS ---
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
    </style>
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
    "Usuario": ["admin", "maximiliano", "lientur", "facundo", "leonardo", "felipe", "ian", "leonel"],
    "Contraseña": ["admin123", "1234", "1234", "1234", "1234", "1234", "1234", "1234"],
    "Rol": ["admin", "jugador", "jugador", "jugador", "jugador", "jugador", "jugador", "jugador"],
    "Nombre Real Vinculado": ["", "Maximiliano", "Lientur", "Facundo", "Leonardo", "Felipe", "Ian", "Leonel"]
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
        
        # 1. Roster
        try:
            sheet_roster = spreadsheet.worksheet("Control General")
        except gspread.exceptions.WorksheetNotFound:
            sheet_roster = spreadsheet.add_worksheet(title="Control General", rows="100", cols="15")
            sheet_roster.update([DATOS_INICIALES_ROSTER.columns.values.tolist()] + DATOS_INICIALES_ROSTER.values.tolist())

        # 2. Asistencia
        try:
            sheet_asistencia = spreadsheet.worksheet("Asistencia")
        except gspread.exceptions.WorksheetNotFound:
            sheet_asistencia = spreadsheet.add_worksheet(title="Asistencia", rows="100", cols="35")
            df_asistencia_init = pd.DataFrame(columns=["Nombre Real", "Mes", "Días Hábiles"] + [str(i) for i in range(1, 32)])
            sheet_asistencia.update([df_asistencia_init.columns.values.tolist()])

        # 3. Disciplina
        try:
            sheet_disciplina = spreadsheet.worksheet("Disciplina")
        except gspread.exceptions.WorksheetNotFound:
            sheet_disciplina = spreadsheet.add_worksheet(title="Disciplina", rows="100", cols="10")
            df_disc_init = pd.DataFrame(columns=["Fecha", "Jugador", "Tipo", "Sanción", "Detalles"])
            sheet_disciplina.update([df_disc_init.columns.values.tolist()])

        # 4. Configuración (Usuarios y Claves)
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

def cargar_roster():
    if sheet_roster is not None:
        try:
            data = sheet_roster.get_all_records()
            if not data:
                guardar_en_sheet(sheet_roster, DATOS_INICIALES_ROSTER)
                return DATOS_INICIALES_ROSTER.copy()
            df = pd.DataFrame(data)
            return DATOS_INICIALES_ROSTER.copy() if df.empty else df
        except:
            return DATOS_INICIALES_ROSTER.copy()
    return DATOS_INICIALES_ROSTER.copy()

def cargar_incidencias():
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

def cargar_configuracion():
    if sheet_config is not None:
        try:
            data = sheet_config.get_all_records()
            if not data:
                guardar_en_sheet(sheet_config, DATOS_INICIALES_CONFIG)
                return DATOS_INICIALES_CONFIG.copy()
            df = pd.DataFrame(data)
            return DATOS_INICIALES_CONFIG.copy() if df.empty else df
        except:
            return DATOS_INICIALES_CONFIG.copy()
    return DATOS_INICIALES_CONFIG.copy()

# --- ESTADOS DE LA SESIÓN ---
if 'df_roster' not in st.session_state:
    st.session_state.df_roster = cargar_roster()

if 'df_incidencias' not in st.session_state:
    st.session_state.df_incidencias = cargar_incidencias()

if 'df_config' not in st.session_state:
    st.session_state.df_config = cargar_configuracion()

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if 'rol_usuario' not in st.session_state:
    st.session_state.rol_usuario = None

if 'nombre_usuario' not in st.session_state:
    st.session_state.nombre_usuario = None


# ==========================================
# PANTALLA DE LOGIN / SELECCIÓN DE MODO
# ==========================================
if not st.session_state.autenticado:
    st.title("🔥 Scarlet Roster - Control de Acceso")
    st.markdown("Selecciona tu modo de acceso o inicia sesión con tus credenciales guardadas en Google Sheets.")
    
    col_l1, col_l2 = st.columns(2)
    
    with col_l1:
        st.markdown("### 🛡️ Acceso Administrador")
        with st.form("form_login_admin"):
            user_admin = st.text_input("Usuario Administrador", key="input_admin_user")
            pass_admin = st.text_input("Contraseña", type="password", key="input_admin_pass")
            submit_admin = st.form_submit_button("Entrar como Admin")
            
            if submit_admin:
                df_c = st.session_state.df_config
                match = df_c[(df_c["Usuario"].astype(str).str.lower() == user_admin.strip().lower()) & 
                             (df_c["Contraseña"].astype(str) == pass_admin.strip()) & 
                             (df_c["Rol"].astype(str).str.lower() == "admin")]
                if not match.empty:
                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = "admin"
                    st.session_state.nombre_usuario = "Administrador"
                    st.success("✅ ¡Acceso concedido como Administrador!")
                    st.rerun()
                else:
                    st.error("❌ Credenciales o permisos de administrador incorrectos.")

    with col_l2:
        st.markdown("### 🎮 Acceso Jugador (Modo Normal)")
        with st.form("form_login_jugador"):
            user_player = st.text_input("Tu Usuario / Nick en el sistema", key="input_player_user")
            pass_player = st.text_input("Tu Contraseña", type="password", key="input_player_pass")
            submit_player = st.form_submit_button("Entrar como Jugador")
            
            if submit_player:
                df_c = st.session_state.df_config
                match = df_c[(df_c["Usuario"].astype(str).str.lower() == user_player.strip().lower()) & 
                             (df_c["Contraseña"].astype(str) == pass_player.strip())]
                if not match.empty:
                    row_match = match.iloc[0]
                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = "jugador"
                    st.session_state.nombre_usuario = row_match["Nombre Real Vinculado"]
                    st.success(f"✅ ¡Bienvenido, {st.session_state.nombre_usuario}!")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")
    
    st.stop() # Detiene la ejecución aquí hasta que el usuario inicie sesión


# ==========================================
# APLICACIÓN PRINCIPAL (POST-LOGIN)
# ==========================================
st.sidebar.markdown(f"👤 **Conectado como:** `{st.session_state.nombre_usuario}`")
st.sidebar.markdown(f"🏷️ **Rol:** `{st.session_state.rol_usuario.upper()}`")
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.autenticado = False
    st.session_state.rol_usuario = None
    st.session_state.nombre_usuario = None
    st.rerun()

st.sidebar.markdown("---")

# --- DICCIONARIOS Y LISTAS DESPLEGABLES ---
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

# --- PESTAÑAS SEGÚN ROL ---
if st.session_state.rol_usuario == "admin":
    tab_roster, tab_asistencia, tab_historial, tab_stats, tab_config = st.tabs([
        "📝 Roster", "📅 Asistencia", "🛡️ Disciplina", "📈 Tracker", "⚙️ Config / Claves"
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
    
    jugadores_activos_temp = [j for j in st.session_state.df_roster["Nombre Real"].tolist() if str(j).strip() != "" and str(j).lower() != "nan"]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("TOTAL JUGADORES", len(jugadores_activos_temp))
    col2.metric("TITULARES", len(st.session_state.df_roster[st.session_state.df_roster['Estado'] == 'Titular']))
    col3.metric("SEXTO PLAYER", len(st.session_state.df_roster[st.session_state.df_roster['Estado'] == 'Sexto player']))
    col4.metric("BANCA", len(st.session_state.df_roster[st.session_state.df_roster['Estado'] == 'Banca']))
    
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
            st.session_state.df_roster,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            column_config=configuracion_columnas,
            height=350,
            key="editor_roster_principal"
        )
        
        if not df_roster_editado.equals(st.session_state.df_roster):
            st.session_state.df_roster = df_roster_editado
            guardar_en_sheet(sheet_roster, st.session_state.df_roster)
            st.rerun()

        if st.button("🔄 Recargar Roster desde Sheets"):
            st.session_state.df_roster = cargar_roster()
            st.success("🔄 ¡Datos actualizados!")
            st.rerun()

        # --- GESTOR DINÁMICO DE AGENTES (SOLO ADMIN) ---
        st.markdown("---")
        st.markdown("### 🎭 Gestor Dinámico de Agentes")
        riot_ids_actuales = [r for r in st.session_state.df_roster["Riot ID (Nick#TAG)"].tolist() if str(r).strip() != "" and str(r).lower() != "nan"]
        
        if len(riot_ids_actuales) > 0:
            c_sel, c_form = st.columns([1, 2])
            with c_sel:
                jugador_agentes = st.selectbox("1. Selecciona al Riot ID:", [""] + riot_ids_actuales, key="select_riot_agente")
            
            if jugador_agentes != "":
                with c_form:
                    filas_coinciondentes = st.session_state.df_roster[st.session_state.df_roster["Riot ID (Nick#TAG)"] == jugador_agentes]
                    if not filas_coinciondentes.empty:
                        idx = filas_coinciondentes.index[0]
                        rol_1 = str(st.session_state.df_roster.at[idx, "Rol Principal"])
                        rol_2 = str(st.session_state.df_roster.at[idx, "Rol Secundario"])
                        
                        opciones_validas = []
                        if rol_1 in AGENTES_POR_ROL: opciones_validas.extend(AGENTES_POR_ROL[rol_1])
                        if rol_2 in AGENTES_POR_ROL: opciones_validas.extend(AGENTES_POR_ROL[rol_2])
                        opciones_validas = list(set(opciones_validas))
                        
                        if not opciones_validas:
                            st.warning("⚠️ Asigna al menos un Rol válido en la tabla superior para este jugador.")
                        else:
                            agentes_str = st.session_state.df_roster.at[idx, "Agentes Principales"]
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
                                st.session_state.df_roster.at[idx, "Agentes Principales"] = nuevos_str
                                guardar_en_sheet(sheet_roster, st.session_state.df_roster)
                                st.rerun()
    else:
        # Modo Normal: Solo visualización del Roster
        st.info("👁️ Modo Visualización: Solo puedes ver el estado del equipo y consultar los agentes.")
        st.dataframe(st.session_state.df_roster, use_container_width=True, hide_index=True)


# ==========================================
# PESTAÑA 2: ASISTENCIA 
# ==========================================
with tab_asistencia:
    st.title("📅 Control de Asistencia")
    jugadores_activos = [j for j in st.session_state.df_roster["Nombre Real"].tolist() if str(j).strip() != "" and str(j).lower() != "nan"]
    
    if len(jugadores_activos) == 0:
        st.warning("No hay jugadores registrados en el Roster.")
    else:
        mes_seleccionado = st.selectbox("Seleccionar Mes", ["Septiembre", "Octubre", "Noviembre", "Diciembre"])
        
        df_asistencia_guardada = pd.DataFrame()
        if sheet_asistencia is not None:
            try:
                data_asis = sheet_asistencia.get_all_records()
                if data_asis:
                    df_asistencia_guardada = pd.DataFrame(data_asis)
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
            # Modo Normal: Solo ve su propia asistencia
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
        jugadores_activos = [j for j in st.session_state.df_roster["Nombre Real"].tolist() if str(j).strip() != "" and str(j).lower() != "nan"]
        
        sub_gen, sub_ind = st.tabs(["📋 Historial General e Ingreso", "👤 Anotaciones por Jugador"])
        
        with sub_gen:
            st.markdown("### Registrar Nueva Incidencia o Anotación")
            with st.form("form_anotacion"):
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
                    st.session_state.df_incidencias = pd.concat([st.session_state.df_incidencias, nueva_fila], ignore_index=True)
                    guardar_en_sheet(sheet_disciplina, st.session_state.df_incidencias)
                    st.success(f"✅ Incidencia registrada para {jugador_sel}.")
                    st.rerun()
            
            st.markdown("---")
            st.markdown("### Historial Completo de Incidencias")
            if not st.session_state.df_incidencias.empty:
                st.dataframe(st.session_state.df_incidencias, use_container_width=True, hide_index=True)
            else:
                st.info("No hay incidencias registradas todavía.")

        with sub_ind:
            st.markdown("### Expediente Individual por Jugador")
            jugador_individual = st.selectbox("Selecciona un jugador:", jugadores_activos, key="select_jugador_ind")
            if not st.session_state.df_incidencias.empty:
                df_filtrado = st.session_state.df_incidencias[st.session_state.df_incidencias["Jugador"] == jugador_individual]
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
        # Modo Normal: Pestaña "Mis Sanciones"
        st.title("🛡️ Mis Sanciones y Anotaciones")
        mi_nombre = st.session_state.nombre_usuario
        
        if not st.session_state.df_incidencias.empty and mi_nombre:
            df_mis_inc = st.session_state.df_incidencias[st.session_state.df_incidencias["Jugador"].str.lower() == mi_nombre.lower()]
            
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
    jugadores_activos = [j for j in st.session_state.df_roster["Nombre Real"].tolist() if str(j).strip() != "" and str(j).lower() != "nan"]
    
    if len(jugadores_activos) > 0:
        c_sel, c_btn = st.columns([2, 1])
        with c_sel: 
            nombres_roster = st.session_state.df_roster[st.session_state.df_roster["Nombre Real"].astype(str).str.strip() != ""]
            dic_nombres_riot = dict(zip(nombres_roster["Nombre Real"], nombres_roster["Riot ID (Nick#TAG)"]))
            
            # Si es jugador normal, preseleccionar su propio nombre si existe en el diccionario
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
# PESTAÑA 5: CONFIGURACIÓN Y CLAVES (SOLO ADMIN)
# ==========================================
if st.session_state.rol_usuario == "admin":
    with tab_config:
        st.title("⚙️ Configuración y Gestión de Credenciales")
        st.markdown("Aquí puedes gestionar los usuarios, contraseñas y roles de acceso que se guardan en la hoja **Configuracion** de tu Google Sheets.")
        
        config_editado = st.data_editor(
            st.session_state.df_config,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="editor_configuracion"
        )
        
        if not config_editado.equals(st.session_state.df_config):
            st.session_state.df_config = config_editado
            guardar_en_sheet(sheet_config, st.session_state.df_config)
            st.success("✅ ¡Credenciales y configuración guardadas en Google Sheets!")

        if st.button("🔄 Recargar Configuración"):
            st.session_state.df_config = cargar_configuracion()
            st.success("🔄 ¡Datos de configuración recargados!")
            st.rerun()
