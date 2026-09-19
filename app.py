import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Scarlet Roster", page_icon="🔥", layout="wide")

# --- ESTILOS CORPORATIVOS Y MINIMALISTAS ---
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
    
    .stSelectbox label, .stTextInput label, .stDateInput label, .stFileUploader label, .stMultiSelect label { 
        color: #ece8e1; font-weight: 600; font-size: 0.9rem; 
    }
    div[data-testid="stMetricValue"] { color: #ff4655; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

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

# --- BASE DE DATOS MAESTRA EN SESIÓN ---
if 'df_roster' not in st.session_state:
    st.session_state.df_roster = pd.DataFrame({
        "Riot ID (Nick#TAG)": ["Mazinhooo#lovsf", "Lionora#ZERO", "BestiaDelTrap#ARK", "leO#deus", "ELNIÑOMARAVILLA#14y", "Lotenesquepedir#boka", "Shuten#2006"],
        "Nombre Real": ["Maximiliano", "Lientur", "Facundo", "Leonardo", "Felipe", "Ian", "Leonel"],
        "Rol Principal": ["Iniciador", "Controlador", "Duelista", "Centinela", "Controlador", "Centinela", "Duelista"],
        "Rol Secundario": ["Centinela", "Iniciador", "", "Duelista", "Centinela", "Iniciador", "Centinela"],
        "Agentes Principales": ["Sova, Fade", "Omen, Fade", "Jett, Neon, Raze", "Cypher, Vyse, Chamber", "Chamber, Cypher, Vyse", "Breach, Sova, Fade", "Neon, Phoenix, Iso"],
        "Rango / Cima": ["Ascendente 3", "Plata", "Ascendente 2", "Inmortal 1", "Inmortal 1", "Ascendente 3", "Ascendente 3"],
        "Cargo": ["Capitan", "Sub capitan", "Player", "Player", "Player", "Player", "Player"],
        "Estado": ["Titular", "Banca", "Titular", "Titular", "Titular", "Sexto player", "Titular"],
        "Actividad": ["Alta", "Alta", "Alta", "Media", "Alta", "Media", "Media"],
        "Contacto": ["Mazzito", "LINO", "facuu", "Leo", "felipoomo", "Iansuki", "Shuten"],
        "Strikes": [0, 0, 0, 0, 0, 0, 0]
    })

jugadores_activos = [j for j in st.session_state.df_roster["Nombre Real"].tolist() if str(j).strip() != "" and str(j).lower() != "nan"]

# --- PESTAÑAS PRINCIPALES ---
tab_roster, tab_asistencia, tab_historial, tab_stats = st.tabs([
    "📝 Roster", "📅 Asistencia", "🛡️ Disciplina", "📈 Tracker"
])

# ==========================================
# PESTAÑA 1: ROSTER (Gestión Central)
# ==========================================
with tab_roster:
    st.title("🔥 Gestión de Roster - Valorant")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("TOTAL JUGADORES", len(jugadores_activos))
    col2.metric("TITULARES", len(st.session_state.df_roster[st.session_state.df_roster['Estado'] == 'Titular']))
    col3.metric("SEXTO PLAYER", len(st.session_state.df_roster[st.session_state.df_roster['Estado'] == 'Sexto player']))
    col4.metric("BANCA", len(st.session_state.df_roster[st.session_state.df_roster['Estado'] == 'Banca']))
    
    st.markdown("---")
    
    # --- GRÁFICOS EXPLICATIVOS SENCILLOS ---
    c_g1, c_g2 = st.columns(2)
    with c_g1:
        if not st.session_state.df_roster.empty:
            rol_counts = st.session_state.df_roster['Rol Principal'].value_counts().reset_index()
            rol_counts.columns = ['Rol', 'Cantidad']
            fig_roles = px.bar(rol_counts, x='Rol', y='Cantidad', title="Distribución por Rol Principal", color_discrete_sequence=['#ff4655'])
            fig_roles.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ffffff', height=240, margin=dict(t=30, b=10, l=10, r=10))
            st.plotly_chart(fig_roles, use_container_width=True)
            
    with c_g2:
        if not st.session_state.df_roster.empty:
            estado_counts = st.session_state.df_roster['Estado'].value_counts().reset_index()
            estado_counts.columns = ['Estado', 'Cantidad']
            fig_estado = px.pie(estado_counts, names='Estado', values='Cantidad', title="Estado Actual del Roster", color_discrete_sequence=['#ff4655', '#ece8e1', '#283442', '#52606d'])
            fig_estado.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ffffff', height=240, margin=dict(t=30, b=10, l=10, r=10))
            st.plotly_chart(fig_estado, use_container_width=True)

    st.markdown("---")
    
    # Diccionario de Agentes 
    with st.expander("📚 Diccionario de Agentes por Rol (Referencia)"):
        ca, cb, cc, cd = st.columns(4)
        ca.info(f"**Duelistas:**\n{', '.join(AGENTES_POR_ROL['Duelista'])}")
        cb.info(f"**Iniciadores:**\n{', '.join(AGENTES_POR_ROL['Iniciador'])}")
        cc.info(f"**Controladores:**\n{', '.join(AGENTES_POR_ROL['Controlador'])}")
        cd.info(f"**Centinelas:**\n{', '.join(AGENTES_POR_ROL['Centinela'])}")

    # Tabla Principal (Con agentes bloqueados para edición directa)
    st.markdown("**Planilla de Control General**")
    configuracion_columnas = {
        "Rol Principal": st.column_config.SelectboxColumn("Rol Principal", options=OPCIONES_ROLES),
        "Rol Secundario": st.column_config.SelectboxColumn("Rol Secundario", options=OPCIONES_ROLES),
        "Rango / Cima": st.column_config.SelectboxColumn("Rango / Cima", options=OPCIONES_RANGOS),
        "Cargo": st.column_config.SelectboxColumn("Cargo en Equipo", options=OPCIONES_CARGOS),
        "Estado": st.column_config.SelectboxColumn("Estado", options=OPCIONES_ESTADO),
        "Actividad": st.column_config.SelectboxColumn("Actividad", options=OPCIONES_ACTIVIDAD),
        "Agentes Principales": st.column_config.TextColumn("Agentes Principales (Solo editable abajo ⬇️)", disabled=True),
    }
    
    df_roster_editado = st.data_editor(
        st.session_state.df_roster,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_order=["Riot ID (Nick#TAG)", "Nombre Real", "Rol Principal", "Rol Secundario", "Agentes Principales", "Rango / Cima", "Cargo", "Estado", "Actividad", "Contacto"],
        column_config=configuracion_columnas,
        height=350
    )
    
    if "Strikes" not in df_roster_editado.columns:
        df_roster_editado["Strikes"] = st.session_state.df_roster["Strikes"]
    df_roster_editado["Strikes"] = df_roster_editado["Strikes"].fillna(0).astype(int)
    st.session_state.df_roster = df_roster_editado

    # --- GESTOR INTELIGENTE DE AGENTES ---
    st.markdown("---")
    st.markdown("### 🎭 Gestor Dinámico de Agentes")
    st.caption("Selecciona un jugador. El sistema detectará sus roles y te mostrará solo los agentes correspondientes.")
    
    if len(jugadores_activos) > 0:
        c_sel, c_form = st.columns([1, 2])
        with c_sel:
            jugador_agentes = st.selectbox("1. Selecciona al Jugador:", [""] + jugadores_activos)
        
        if jugador_agentes != "":
            with c_form:
                idx = st.session_state.df_roster[st.session_state.df_roster["Nombre Real"] == jugador_agentes].index[0]
                rol_1 = str(st.session_state.df_roster.at[idx, "Rol Principal"])
                rol_2 = str(st.session_state.df_roster.at[idx, "Rol Secundario"])
                
                opciones_validas = []
                if rol_1 in AGENTES_POR_ROL: opciones_validas.extend(AGENTES_POR_ROL[rol_1])
                if rol_2 in AGENTES_POR_ROL: opciones_validas.extend(AGENTES_POR_ROL[rol_2])
                opciones_validas = list(set(opciones_validas))
                
                if not opciones_validas:
                    st.warning("⚠️ Asigna al menos un Rol (Principal o Secundario) válido en la tabla de arriba para cargar sus agentes.")
                else:
                    agentes_str = st.session_state.df_roster.at[idx, "Agentes Principales"]
                    agentes_actuales = [a.strip() for a in str(agentes_str).split(",")] if pd.notna(agentes_str) and str(agentes_str).strip() != "" else []
                    agentes_actuales = [a for a in agentes_actuales if a in opciones_validas]
                    
                    nuevos_agentes = st.multiselect(
                        f"2. Agentes disponibles para los roles de {jugador_agentes} ({rol_1} / {rol_2}):",
                        options=opciones_validas,
                        default=agentes_actuales
                    )
                    
                    if st.button("💾 Guardar Pool de Agentes"):
                        st.session_state.df_roster.at[idx, "Agentes Principales"] = ", ".join(nuevos_agentes)
                        st.rerun()

# ==========================================
# PESTAÑA 2: ASISTENCIA 
# ==========================================
with tab_asistencia:
    st.title("📅 Asistencia")
    st.caption("P - Presente | A - Ausencia | J - Justificado | T - Tardanza (80%)")
    
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

        df_editado = st.data_editor(df_mes, use_container_width=True)
        df_editado["% Asistencia"] = df_editado.apply(calcular_porcentaje, axis=1)
        
        st.markdown("**Resumen Mensual**")
        st.dataframe(df_editado[["Días Hábiles", "% Asistencia"]], use_container_width=True)

# ==========================================
# PESTAÑA 3: DISCIPLINA
# ==========================================
with tab_historial:
    st.title("🛡️ Panel de Disciplina")
    st.info("💡 Este panel refleja exclusivamente los jugadores registrados en la pestaña Roster. Solo la columna 'Strikes' es editable aquí.")
    
    if len(jugadores_activos) > 0:
        df_disc_view = st.session_state.df_roster[["Nombre Real", "Estado", "Rol Principal", "Strikes"]].copy()
        df_disc_view = df_disc_view[df_disc_view["Nombre Real"].astype(str).str.strip() != ""]
        
        edited_disc = st.data_editor(
            df_disc_view,
            use_container_width=True,
            hide_index=True,
            disabled=["Nombre Real", "Estado", "Rol Principal"]
        )
        
        for index, row in edited_disc.iterrows():
            idx_roster = st.session_state.df_roster.index[st.session_state.df_roster['Nombre Real'] == row['Nombre Real']].tolist()
            if idx_roster:
                st.session_state.df_roster.at[idx_roster[0], 'Strikes'] = row['Strikes']

        st.markdown("---")
        st.markdown("**Registro de Incidencias**")
        with st.form("form_anotacion"):
            c1, c2 = st.columns(2)
            with c1:
                fecha = st.date_input("Fecha")
                tipo = st.selectbox("Tipo", ["Positiva", "Negativa"])
                sancion = st.selectbox("Sanción", ["Ninguna", "Strike 1", "Expulsión"])
            with c2:
                jugador_sel = st.selectbox("Jugador Implicado", jugadores_activos)
                detalles = st.text_area("Detalles")
            if st.form_submit_button("Guardar Registro"):
                st.success(f"Incidencia registrada para {jugador_sel}.")
    else:
        st.warning("Agrega jugadores en la pestaña 'Roster' para iniciar el control de disciplina.")

# ==========================================
# PESTAÑA 4: TRACKER Y STATS
# ==========================================
with tab_stats:
    st.title("📈 Tracker y Estadísticas")
    
    if len(jugadores_activos) > 0:
        c_sel, c_btn = st.columns([2, 1])
        with c_sel: 
            nombres_roster = st.session_state.df_roster[st.session_state.df_roster["Nombre Real"].astype(str).str.strip() != ""]
            dic_nombres_riot = dict(zip(nombres_roster["Nombre Real"], nombres_roster["Riot ID (Nick#TAG)"]))
            jugador_stat = st.selectbox("Seleccionar Jugador", list(dic_nombres_riot.keys()))
            
        with c_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            riot_id_seleccionado = dic_nombres_riot[jugador_stat]
            if pd.notna(riot_id_seleccionado) and "#" in str(riot_id_seleccionado):
                url = f"https://tracker.gg/valorant/profile/riot/{str(riot_id_seleccionado).replace('#', '%23')}/overview"
                st.link_button(f"🔴 Perfil en Tracker.gg", url, use_container_width=True)
            else:
                st.error("Riot ID no válido. Asegúrate de incluir el '#' en la pestaña Roster.")

        st.markdown("---")
        st.markdown(f"**Captura de Rendimiento - {jugador_stat}**")
        img_upload = st.file_uploader("Sube una captura de pantalla del Tracker (Opcional)", type=["png", "jpg", "jpeg"])
        
        if img_upload:
            st.image(img_upload, use_column_width=True, caption=f"Última actualización de stats para {jugador_stat}")
    else:
        st.warning("Agrega jugadores en la pestaña 'Roster'.")
