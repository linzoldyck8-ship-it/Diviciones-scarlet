import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA Y ESTILOS (SCARLET VALORANT) ---
st.set_page_config(page_title="Scarlet Roster", page_icon="🔥", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0f1923; color: #ece8e1; }
    h1, h2, h3 { color: #ff4655; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    .stButton>button { background-color: #ff4655; color: white; border: none; font-weight: bold; }
    .stButton>button:hover { background-color: #0f1923; color: #ff4655; border: 1px solid #ff4655; }
    .stSelectbox label, .stTextInput label, .stDateInput label { color: #ece8e1; font-weight: bold; }
    div[data-testid="stMetricValue"] { color: #ff4655; }
    </style>
""", unsafe_allow_html=True)

# --- PESTAÑAS PRINCIPALES ---
tab_roster, tab_asistencia, tab_historial, tab_stats = st.tabs([
    "📝 Roster & Dashboard", "📅 Asistencia", "🛡️ Control y Disciplina", "📈 Análisis Stats"
])

# ==========================================
# PESTAÑA 1: ROSTER & DASHBOARD
# ==========================================
with tab_roster:
    sub_dash, sub_form = st.tabs(["📊 Panel de Control", "➕ Registrar Jugador"])
    
    with sub_dash:
        st.title("🔥 PANEL DE CONTROL - ROSTER VALORANT")
        
        # Simulación de carga de BD Roster
        df_roster = pd.DataFrame({
            "Estado": ["Titular", "Titular", "Titular", "Titular", "Titular", "Sexto player", "Banca"],
            "Rol Principal": ["Duelista", "Iniciador", "Controlador", "Centinela", "Centinela", "Iniciador", "Controlador"]
        })
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("TOTAL JUGADORES", len(df_roster))
        col2.metric("TITULARES (MAIN)", len(df_roster[df_roster['Estado'] == 'Titular']))
        col3.metric("SEXTO PLAYER", len(df_roster[df_roster['Estado'] == 'Sexto player']))
        col4.metric("EN RESERVA / PRUEBA", len(df_roster[df_roster['Estado'].isin(['Banca', 'En Prueba'])]))
        
        st.markdown("---")
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.subheader("Desglose por Rol Táctico")
            rol_counts = df_roster['Rol Principal'].value_counts().reset_index()
            rol_counts.columns = ['Rol Valorant', 'Cantidad']
            fig_roles = px.bar(rol_counts, x='Rol Valorant', y='Cantidad', color_discrete_sequence=['#0000FF'])
            fig_roles.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ffffff')
            st.plotly_chart(fig_roles, use_container_width=True)

        with col_g2:
            st.subheader("Estado de los Jugadores")
            estado_counts = df_roster['Estado'].value_counts().reset_index()
            estado_counts.columns = ['Estado', 'Cantidad']
            fig_estado = px.pie(estado_counts, names='Estado', values='Cantidad', color_discrete_sequence=px.colors.qualitative.Set1)
            fig_estado.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ffffff')
            st.plotly_chart(fig_estado, use_container_width=True)

    with sub_form:
        st.subheader("Registro / Actualización de Roster")
        with st.form("form_roster"):
            c1, c2 = st.columns(2)
            with c1:
                riot_id = st.text_input("Riot ID (Nick#TAG)")
                nombre_real = st.text_input("Nombre Real")
                rol_principal = st.selectbox("Rol Principal", ["Duelista", "Iniciador", "Controlador", "Centinela", "Flex"])
                rol_secundario = st.selectbox("Rol Secundario", ["Duelista", "Iniciador", "Controlador", "Centinela", "Flex"])
                agentes = st.text_input("Agentes Principales")
                rango = st.selectbox("Rango / Cima", ["Plata", "Oro", "Platino", "Diamante", "Ascendente 1", "Ascendente 2", "Ascendente 3", "Inmortal 1", "Inmortal 2", "Inmortal 3", "Radiante"])
            with c2:
                cargo = st.selectbox("Cargo en Equipo", ["Player", "Capitan", "Sub capitan"])
                estado = st.selectbox("Estado", ["Titular", "Banca", "En Prueba", "Sexto player", "Suspendido", "Expulsado"])
                actividad = st.selectbox("Actividad", ["Alta", "Media", "Baja"])
                contacto = st.text_input("Contacto / Discord")
                notas = st.text_area("Notas / Observaciones")
            if st.form_submit_button("🚀 Registrar Jugador"):
                st.success(f"Jugador {riot_id} registrado (Conectar con gspread aquí).")

# ==========================================
# PESTAÑA 2: ASISTENCIA
# ==========================================
with tab_asistencia:
    st.title("📅 Control Anual de Asistencia")
    sub_mes, sub_anual = st.tabs(["🗓️ Registro Mensual", "📊 Resumen Anual"])

    jugadores_demo = ["Mazzito", "Lino", "Leo", "Soy leo", "Iansuki", "Facu", "Felipo", "Benja"]

    with sub_mes:
        mes_seleccionado = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
        st.caption("P - Presente | A - Ausencia | J - Justificado | T - Tardanza (80%)")
        
        dias_mes = [str(i) for i in range(1, 32)]
        df_mes = pd.DataFrame(index=jugadores_demo, columns=dias_mes).fillna("-")
        df_mes["Días Hábiles"] = 22
        
        def calcular_porcentaje(row):
            dias = int(row["Días Hábiles"])
            if dias == 0: return "0%"
            asistencia = sum(row[dias_mes] == "P") + sum(row[dias_mes] == "J") + (sum(row[dias_mes] == "T") * 0.8)
            return f"{min((asistencia / dias) * 100, 100):.0f}%"

        df_editado = st.data_editor(df_mes, use_container_width=True, height=350)
        df_editado["% Asistencia"] = df_editado.apply(calcular_porcentaje, axis=1)
        
        st.dataframe(df_editado[["Días Hábiles", "% Asistencia"]], use_container_width=True)

    with sub_anual:
        df_anual = pd.DataFrame(index=jugadores_demo, columns=["Enero", "Febrero", "Promedio Anual"]).fillna("00%")
        st.dataframe(df_anual, use_container_width=True)

# ==========================================
# PESTAÑA 3: CONTROL Y DISCIPLINA
# ==========================================
with tab_historial:
    st.title("🛡️ Control de Jugadores e Historial")
    sub_panel, sub_historial = st.tabs(["📋 Panel General", "👤 Historial Personal"])

    with sub_panel:
        df_panel = pd.DataFrame({
            "Jugador": ["Lino", "Facu", "Felipo"],
            "Estado Actual": ["Banca", "Titular", "Titular"],
            "Rol Principal": ["Controlador", "Duelista", "Controlador"],
            "Strikes": [0, 0, 0]
        })
        st.data_editor(df_panel, use_container_width=True, hide_index=True)

    with sub_historial:
        jugador_sel = st.selectbox("Seleccionar Jugador", df_panel["Jugador"].tolist())
        with st.expander("➕ Nueva anotación"):
            with st.form("form_anotacion"):
                c1, c2 = st.columns(2)
                with c1:
                    fecha = st.date_input("Fecha")
                    tipo = st.selectbox("Tipo", ["Positiva", "Negativa"])
                    sancion = st.selectbox("Sanción", ["Ninguna", "Strike 1", "Expulsión"])
                with c2:
                    autor = st.selectbox("Registrado Por", ["Capitán", "Manager", "Coach"])
                    detalles = st.text_area("Detalles")
                if st.form_submit_button("Guardar"):
                    st.success("Guardado en GSheets.")

# ==========================================
# PESTAÑA 4: STATS PREMIER
# ==========================================
with tab_stats:
    st.title("📈 Análisis Stats Premier")
    roster_dic = {"Shuten": "Shuten#2006", "Leo": "leO#deus", "Felipo": "ELNIÑOMARAVILLA#14y"}
    
    c_sel, c_btn = st.columns([2, 1])
    with c_sel: jugador_stat = st.selectbox("Jugador", list(roster_dic.keys()))
    with c_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        url = f"https://tracker.gg/valorant/profile/riot/{roster_dic[jugador_stat].replace('#', '%23')}/overview"
        st.link_button(f"🔴 Ver perfil en Tracker.gg", url, use_container_width=True)

    st.markdown("---")
    
    # Simulación de datos extraídos de Google Sheets
    df_stats = pd.DataFrame({
        "Fecha": ["25 Jul", "18 Jul"], "Mapa": ["Sunset", "Ascent"], 
        "Resultado": ["Victoria", "Derrota"], "K/D": [2.60, 0.60], "DDA": [76, -65]
    })

    c_resumen, c_tabla = st.columns([1, 2])
    with c_resumen:
        st.markdown("**KDA Promedio**")
        st.info(f"**{df_stats['K/D'].mean():.2f}**")
        st.error(f"Negativo (< 0.9): {len(df_stats[df_stats['K/D'] < 0.9])}")
        st.success(f"Positivo (> 1.1): {len(df_stats[df_stats['K/D'] > 1.1])}")

    with c_tabla:
        def colorear_stats(val):
            if isinstance(val, (int, float)):
                if val >= 1.2 or (isinstance(val, int) and val > 10): return 'background-color: rgba(144,238,144,0.2); color: #90EE90;'
                if val <= 0.8 or (isinstance(val, int) and val < -10): return 'background-color: rgba(255,99,71,0.2); color: #FF6347;'
                return 'background-color: rgba(255,215,0,0.2); color: #FFD700;'
            return ''
            
        st.dataframe(df_stats.style.map(colorear_stats, subset=['K/D', 'DDA']), use_container_width=True, hide_index=True)