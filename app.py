import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Scarlet Roster - Google Sheets", page_icon="🔥", layout="wide")

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

# --- CONEXIÓN CON GOOGLE SHEETS ---
@st.cache_resource
def conectar_google_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("crea el proyecto en formato hoja de calculo como...").worksheet("Control General")
        return sheet
    except Exception as e:
        return None

sheet = conectar_google_sheets()

# Datos predeterminados por si la hoja de Google Sheets está vacía
DATOS_INICIALES = pd.DataFrame({
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

def guardar_datos_en_sheets(df):
    if sheet is not None:
        try:
            df_clean = df.fillna("")
            # Asegura que las columnas coincidan con las de tu Sheets
            data_to_upload = [df_clean.columns.values.tolist()] + df_clean.values.tolist()
            sheet.clear()
            sheet.update(data_to_upload)
        except Exception as e:
            st.error(f"Error al guardar en Google Sheets: {e}")

def cargar_datos():
    if sheet is not None:
        try:
            data = sheet.get_all_records()
            if not data:  # Si la hoja está vacía
                guardar_datos_en_sheets(DATOS_INICIALES)
                return DATOS_INICIALES.copy()
            df = pd.DataFrame(data)
            if df.empty:
                return DATOS_INICIALES.copy()
            return df
        except Exception as e:
            st.warning("⚠️ No se pudieron leer los registros de Sheets, cargando base temporal.")
            return DATOS_INICIALES.copy()
    return DATOS_INICIALES.copy()

if 'df_roster' not in st.session_state:
    st.session_state.df_roster = cargar_datos()

if 'df_incidencias' not in st.session_state:
    st.session_state.df_incidencias = pd.DataFrame(columns=["Fecha", "Jugador", "Tipo", "Sanción", "Detalles"])

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

# --- PESTAÑAS PRINCIPALES ---
tab_roster, tab_asistencia, tab_historial, tab_stats = st.tabs([
    "📝 Roster", "📅 Asistencia", "🛡️ Disciplina", "📈 Tracker"
])

# ==========================================
# PESTAÑA 1: ROSTER
# ==========================================
with tab_roster:
    st.title("🔥 Gestión de Roster - Sincronizado con Google Sheets")
    
    if sheet is None:
        st.error("⚠️ No se pudo conectar con Google Sheets. Verifica los secrets.")
    else:
        st.success("🟢 Conectado en tiempo real con Google Sheets.")

    jugadores_activos_temp = [j for j in st.session_state.df_roster["Nombre Real"].tolist() if str(j).strip() != "" and str(j).lower() != "nan"]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("TOTAL JUGADORES", len(jugadores_activos_temp))
    col2.metric("TITULARES", len(st.session_state.df_roster[st.session_state.df_roster['Estado'] == 'Titular']))
    col3.metric("SEXTO PLAYER", len(st.session_state.df_roster[st.session_state.df_roster['Estado'] == 'Sexto player']))
    col4.metric("BANCA", len(st.session_state.df_roster[st.session_state.df_roster['Estado'] == 'Banca']))
    
    st.markdown("---")
    
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
    
    # Guardado automático transparente en Sheets cada vez que modificas la tabla principal
    if not df_roster_editado.equals(st.session_state.df_roster):
        st.session_state.df_roster = df_roster_editado
        guardar_datos_en_sheets(st.session_state.df_roster)
        st.rerun()

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("💾 Sincronizar Manualmente"):
            guardar_datos_en_sheets(st.session_state.df_roster)
            st.success("✅ ¡Datos guardados en Google Sheets!")
    with col_btn2:
        if st.button("🔄 Recargar desde Google Sheets"):
            st.session_state.df_roster = cargar_datos()
            st.success("🔄 ¡Datos actualizados!")
            st.rerun()

    # --- GESTOR DINÁMICO DE AGENTES ---
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
                            guardar_datos_en_sheets(st.session_state.df_roster)
                            st.rerun()

# ==========================================
# PESTAÑA 2: ASISTENCIA 
# ==========================================
with tab_asistencia:
    st.title("📅 Asistencia")
    jugadores_activos = [j for j in st.session_state.df_roster["Nombre Real"].tolist() if str(j).strip() != "" and str(j).lower() != "nan"]
    
    if len(jugadores_activos) == 0:
        st.warning("Agrega jugadores en la pestaña 'Roster' para ver la asistencia.")
    else:
        mes_seleccionado = st.selectbox("Mes", ["Septiembre", "Octubre", "Noviembre", "Diciembre"])
        dias_mes = [str(i) for i in range(1, 32)]
        df_mes = pd.DataFrame(index=jugadores_activos, columns=dias_mes).fillna("-")
        df_mes["Días Hábiles"] = 22
        
        def calcular_porcentaje(row):
            dias = int(row["Días Hábiles"])
            if dias == 0: return "0%"
            asistencia = sum(row[dias_mes] == "P") + sum(row[dias_mes] == "J") + (sum(row[dias_mes] == "T") * 0.8)
            return f"{min((asistencia / dias) * 100, 100):.0f}%"

        df_editado = st.data_editor(df_mes, use_container_width=True, key="editor_asistencia_mes")
        df_editado["% Asistencia"] = df_editado.apply(calcular_porcentaje, axis=1)
        st.dataframe(df_editado[["Días Hábiles", "% Asistencia"]], use_container_width=True)

# ==========================================
# PESTAÑA 3: DISCIPLINA
# ==========================================
with tab_historial:
    st.title("🛡️ Panel de Disciplina y Conducta")
    
    jugadores_activos = [j for j in st.session_state.df_roster["Nombre Real"].tolist() if str(j).strip() != "" and str(j).lower() != "nan"]
    
    if len(jugadores_activos) == 0:
        st.warning("Agrega jugadores en la pestaña 'Roster' para iniciar el control de disciplina.")
    else:
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
                
                if st.form_submit_button("Guardar Registro"):
                    nueva_fila = pd.DataFrame([{
                        "Fecha": str(fecha),
                        "Jugador": jugador_sel,
                        "Tipo": tipo,
                        "Sanción": sancion,
                        "Detalles": detalles
                    }])
                    st.session_state.df_incidencias = pd.concat([st.session_state.df_incidencias, nueva_fila], ignore_index=True)
                    st.success(f"✅ Incidencia registrada correctamente para {jugador_sel}.")
            
            st.markdown("---")
            st.markdown("### Historial Completo de Incidencias")
            if not st.session_state.df_incidencias.empty:
                st.dataframe(st.session_state.df_incidencias, use_container_width=True, hide_index=True)
            else:
                st.info("No hay incidencias registradas todavía.")

        with sub_ind:
            st.markdown("### Expediente Individual por Jugador")
            jugador_individual = st.selectbox("Selecciona un jugador para ver sus notas exclusivas:", jugadores_activos, key="select_jugador_ind")
            
            if not st.session_state.df_incidencias.empty:
                df_filtrado = st.session_state.df_incidencias[st.session_state.df_incidencias["Jugador"] == jugador_individual]
                
                col_i1, col_i2 = st.columns(2)
                col_i1.metric(f"TOTAL ANOTACIONES DE {jugador_individual.upper()}", len(df_filtrado))
                col_i2.metric("SANCIONES ACTIVAS", len(df_filtrado[df_filtrado["Sanción"] != "Ninguna"]))
                
                st.markdown("---")
                if not df_filtrado.empty:
                    st.dataframe(df_filtrado[["Fecha", "Tipo", "Sanción", "Detalles"]], use_container_width=True, hide_index=True)
                else:
                    st.info(f"✨ El jugador {jugador_individual} no tiene ninguna anotación ni incidencia registrada en su historial.")
            else:
                st.info("Aún no se han registrado incidencias en el sistema.")

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
            jugador_stat = st.selectbox("Seleccionar Jugador", list(dic_nombres_riot.keys()), key="select_stats_jugador")
            
        with c_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            riot_id_seleccionado = dic_nombres_riot.get(jugador_stat, "")
            if pd.notna(riot_id_seleccionado) and "#" in str(riot_id_seleccionado):
                url = f"https://tracker.gg/valorant/profile/riot/{str(riot_id_seleccionado).replace('#', '%23')}/overview"
                st.link_button(f"🔴 Perfil en Tracker.gg", url, use_container_width=True)
            else:
                st.error("Riot ID no válido en Sheets. Asegúrate de incluir el '#' en la columna Riot ID.")

        st.markdown("---")
        st.markdown(f"**Captura de Rendimiento - {jugador_stat}**")
        img_upload = st.file_uploader("Sube una captura de pantalla del Tracker (Opcional)", type=["png", "jpg", "jpeg"])
        if img_upload:
            st.image(img_upload, use_column_width=True, caption=f"Última actualización de stats para {jugador_stat}")
    else:
        st.warning("Agrega jugadores en la pestaña 'Roster'.")
