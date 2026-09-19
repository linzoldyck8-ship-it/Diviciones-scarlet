import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Scarlet Roster", page_icon="🔥", layout="wide")

# --- ESTILOS CORPORATIVOS Y MINIMALISTAS (SCARLET) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    .stApp { background-color: #0f1923; color: #ece8e1; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #ff4655; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; }
    
    /* Estilo de Botones Minimalista */
    .stButton>button { 
        background-color: transparent; 
        color: #ff4655; 
        border: 1px solid #ff4655; 
        border-radius: 4px; 
        font-weight: 600; 
        transition: all 0.3s ease; 
    }
    .stButton>button:hover { background-color: #ff4655; color: #0f1923; }
    
    /* Inputs y Selectores */
    .stSelectbox label, .stTextInput label, .stDateInput label, .stFileUploader label { 
        color: #ece8e1; font-weight: 600; font-size: 0.9rem; 
    }
    div[data-testid="stMetricValue"] { color: #ff4655; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

# --- VARIABLES DE SESIÓN (Para agregar/quitar jugadores dinámicamente) ---
if 'jugadores_asistencia' not in st.session_state:
    st.session_state.jugadores_asistencia = ["Mazzito", "Lino", "Leo", "Soy leo", "Iansuki", "Facu", "Felipo", "Benja"]

if 'df_disciplina' not in st.session_state:
    st.session_state.df_disciplina = pd.DataFrame({
        "Jugador": ["Lino", "Facu", "Felipo"],
        "Estado Actual": ["Banca", "Titular", "Titular"],
        "Rol Principal": ["Controlador", "Duelista", "Controlador"],
        "Strikes": [0, 0, 0]
    })

# --- PESTAÑAS PRINCIPALES ---
tab_roster, tab_asistencia, tab_historial, tab_stats = st.tabs([
    "📝 Roster", "📅 Asistencia", "🛡️ Disciplina", "📈 Tracker"
])

# ==========================================
# PESTAÑA 1: ROSTER & DASHBOARD
# ==========================================
with tab_roster:
    st.title("🔥 Panel Corporativo - Roster")
    
    df_roster = pd.DataFrame({
        "Estado": ["Titular", "Titular", "Titular", "Titular", "Titular", "Sexto player", "Banca"],
        "Rol Principal": ["Duelista", "Iniciador", "Controlador", "Centinela", "Centinela", "Iniciador", "Controlador"]
    })
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("TOTAL JUGADORES", len(df_roster))
    col2.metric("TITULARES", len(df_roster[df_roster['Estado'] == 'Titular']))
    col3.metric("SEXTO PLAYER", len(df_roster[df_roster['Estado'] == 'Sexto player']))
    col4.metric("RESERVA", len(df_roster[df_roster['Estado'].isin(['Banca', 'En Prueba'])]))
    
    st.markdown("---")
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown("**Desglose por Rol Táctico**")
        rol_counts = df_roster['Rol Principal'].value_counts().reset_index()
        rol_counts.columns = ['Rol Valorant', 'Cantidad']
        fig_roles = px.bar(rol_counts, x='Rol Valorant', y='Cantidad', color_discrete_sequence=['#ff4655'])
        fig_roles.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ffffff', margin=dict(t=10, b=10))
        st.plotly_chart(fig_roles, use_container_width=True)

    with col_g2:
        st.markdown("**Estado de los Jugadores**")
        estado_counts = df_roster['Estado'].value_counts().reset_index()
        estado_counts.columns = ['Estado', 'Cantidad']
        fig_estado = px.pie(estado_counts, names='Estado', values='Cantidad', color_discrete_sequence=['#ff4655', '#ece8e1', '#0f1923'])
        fig_estado.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ffffff', margin=dict(t=10, b=10))
        st.plotly_chart(fig_estado, use_container_width=True)

# ==========================================
# PESTAÑA 2: ASISTENCIA (Con Agregar/Quitar)
# ==========================================
with tab_asistencia:
    st.title("📅 Asistencia")
    
    with st.expander("⚙️ Administrar Lista de Asistencia"):
        c_add, c_rem = st.columns(2)
        with c_add:
            nuevo_j = st.text_input("Nuevo Jugador:")
            if st.button("➕ Añadir a Lista") and nuevo_j:
                if nuevo_j not in st.session_state.jugadores_asistencia:
                    st.session_state.jugadores_asistencia.append(nuevo_j)
                    st.rerun()
        with c_rem:
            quitar_j = st.selectbox("Eliminar Jugador:", [""] + st.session_state.jugadores_asistencia)
            if st.button("❌ Eliminar de Lista") and quitar_j:
                st.session_state.jugadores_asistencia.remove(quitar_j)
                st.rerun()

    mes_seleccionado = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
    st.caption("P - Presente | A - Ausencia | J - Justificado | T - Tardanza (80%)")
    
    dias_mes = [str(i) for i in range(1, 32)]
    df_mes = pd.DataFrame(index=st.session_state.jugadores_asistencia, columns=dias_mes).fillna("-")
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
# PESTAÑA 3: DISCIPLINA (Con Agregar/Quitar)
# ==========================================
with tab_historial:
    st.title("🛡️ Panel de Disciplina")
    
    with st.expander("⚙️ Administrar Jugadores en Disciplina"):
        c1, c2 = st.columns(2)
        with c1:
            nuevo_disc = st.text_input("Añadir Jugador al Panel:")
            if st.button("➕ Añadir a Disciplina") and nuevo_disc:
                nueva_fila = {"Jugador": nuevo_disc, "Estado Actual": "Titular", "Rol Principal": "Pendiente", "Strikes": 0}
                st.session_state.df_disciplina = pd.concat([st.session_state.df_disciplina, pd.DataFrame([nueva_fila])], ignore_index=True)
                st.rerun()
        with c2:
            quitar_disc = st.selectbox("Eliminar Jugador del Panel:", [""] + st.session_state.df_disciplina["Jugador"].tolist())
            if st.button("❌ Eliminar de Disciplina") and quitar_disc:
                st.session_state.df_disciplina = st.session_state.df_disciplina[st.session_state.df_disciplina["Jugador"] != quitar_disc]
                st.rerun()

    st.markdown("**Estado General**")
    st.data_editor(st.session_state.df_disciplina, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("**Registro de Incidencias**")
    with st.form("form_anotacion"):
        c1, c2 = st.columns(2)
        with c1:
            fecha = st.date_input("Fecha")
            tipo = st.selectbox("Tipo", ["Positiva", "Negativa"])
            sancion = st.selectbox("Sanción", ["Ninguna", "Strike 1", "Expulsión"])
        with c2:
            jugador_sel = st.selectbox("Jugador Implicado", st.session_state.df_disciplina["Jugador"].tolist())
            detalles = st.text_area("Detalles")
        if st.form_submit_button("Guardar Registro"):
            st.success("Incidencia registrada.")

# ==========================================
# PESTAÑA 4: TRACKER Y STATS (Minimalista)
# ==========================================
with tab_stats:
    st.title("📈 Tracker y Estadísticas")
    roster_dic = {"Shuten": "Shuten#2006", "Leo": "leO#deus", "Felipo": "ELNIÑOMARAVILLA#14y"}
    
    c_sel, c_btn = st.columns([2, 1])
    with c_sel: 
        jugador_stat = st.selectbox("Seleccionar Jugador", list(roster_dic.keys()))
    with c_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        url = f"https://tracker.gg/valorant/profile/riot/{roster_dic[jugador_stat].replace('#', '%23')}/overview"
        st.link_button(f"🔴 Perfil en Tracker.gg", url, use_container_width=True)

    st.markdown("---")
    
    st.markdown(f"**Captura de Rendimiento - {jugador_stat}**")
    img_upload = st.file_uploader("Sube una captura de pantalla del Tracker (Opcional)", type=["png", "jpg", "jpeg"])
    
    if img_upload:
        st.image(img_upload, use_column_width=True, caption=f"Última actualización de stats para {jugador_stat}")
    else:
        st.info("💡 Haz clic en el botón superior para ver las estadísticas en vivo. Aquí puedes subir una captura fija si deseas almacenarla en la interfaz.")
