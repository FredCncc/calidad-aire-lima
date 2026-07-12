import streamlit as st
import base64
import psycopg2
import re  # Librería nativa de Python para validar correos
import hashlib
from streamlit_option_menu import option_menu  # Requrequiere: pip install streamlit-option-menu

# --- FUNCIÓN DE ENCRIPTACIÓN ---
def encriptar_clave(clave):
    # Transforma la contraseña en un hash irreversible SHA-256 por seguridad
    return hashlib.sha256(clave.encode()).hexdigest()

# Configurar la página de Streamlit
st.set_page_config(page_title="EcoWayraTec", page_icon="🌎", layout="wide")
# Header transparente sin ocultar ningún contenedor: así el botón para
# colapsar/reabrir el sidebar (que vive dentro del header) nunca se bloquea.
# El botón "Deploy" ya está oculto por 'toolbarMode = "viewer"' en config.toml.
st.markdown(
    """
    <style>
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        box-shadow: none !important;
    }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True
)


def es_correo_valido(correo):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, correo) is not None

DB_HOST = "aws-1-us-east-2.pooler.supabase.com"
DB_PORT = "6543"
DB_NAME = "postgres"
DB_USER = "postgres.mstdoqrqeuhghzohqdgy"
DB_PASSWORD = st.secrets["DB_PASSWORD"]

def ejecutar_consulta(query, datos=None, registrar=False):
    try:
        conexion = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, database=DB_NAME,
            user=DB_USER, password=DB_PASSWORD, sslmode="require"
        )
        cursor = conexion.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            correo TEXT UNIQUE NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            clave TEXT NOT NULL
        );
        """)
        conexion.commit()
        clave_admin_encriptada = encriptar_clave("admin1234")
        cursor.execute("""
            INSERT INTO usuarios (correo, usuario, clave) 
            VALUES (%s, %s, %s) 
            ON CONFLICT (usuario) DO NOTHING;
        """, ("admin@sistema.com", "admin", clave_admin_encriptada))
        conexion.commit()
        if datos:
            query_adaptada = query.replace("?", "%s")
            cursor.execute(query_adaptada, datos)
        else:
            cursor.execute(query)
        if registrar:
            conexion.commit()
            return True
        else:
            return cursor.fetchall()
    except psycopg2.errors.UniqueViolation:
        return "duplicado"
    except Exception as e:
        print(f"Error de conexión en la nube: {e}")
        return False
    finally:
        if 'conexion' in locals():
            cursor.close()
            conexion.close()


@st.cache_resource
def obtener_imagen_base64(ruta_imagen):
    with open(ruta_imagen, "rb") as image_file:
        datos = image_file.read()
        return base64.b64encode(datos).decode()

if "logueado" not in st.session_state:
    st.session_state.logueado = False
if "nombre_usuario" not in st.session_state:
    st.session_state.nombre_usuario = ""

if not st.session_state.logueado:
    if "mostrando_formulario" not in st.session_state:
        st.session_state.mostrando_formulario = False

    # Carga segura de tus nuevas imágenes corporativas
    try:
        img_bienvenida = obtener_imagen_base64("assets/fondo.png")
        img_fondo_login = obtener_imagen_base64("assets/limanoche.png")
    except FileNotFoundError:
        st.error("⚠️ Error: Verifica que las imágenes se llamen 'fondo.png' y 'limanoche.png' dentro de la carpeta assets.")
        st.stop()

        # --- SUB-PANTALLA A: PRESENTACIÓN PRINCIPAL DE ECOWAYRATEC (BOTÓN SUPERIOR INDEPENDIENTE) ---
    if not st.session_state.mostrando_formulario:

        # ==================== PRIMERA INTERFAZ ====================

        try:
            fondo = obtener_imagen_base64("assets/fondo_inicio.png")
            logo_ucv = obtener_imagen_base64("assets/logo_ucv.png")
            logo_senamhi = obtener_imagen_base64("assets/logo_senamhi.png")
        except FileNotFoundError:
            st.error("No se encontraron las imágenes en la carpeta assets.")
            st.stop()

        st.markdown(f"""
        <style>

        @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap');

        .stApp {{
            background-image:
                linear-gradient(rgba(255,255,255,0.18),
                rgba(255,255,255,0.18)),
                url("data:image/jpg;base64,{fondo}");

            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        [data-testid="stMainBlockContainer"] {{
            padding-top:20px;
            max-width:900% !important;
            margin:0 auto !important;
        }}

        .presentacion{{
            width:100%;
            text-align:center;
        }}

        .logos{{
            display:flex;
            justify-content:space-between;
            align-items:center;
            padding:20px 60px;
        }}

        .logo-ucv{{
            width:180px;
        }}

        .logo-senamhi{{
            width:180px;
        }}

        .titulo{{
            margin-top:40px;
            font-size:40px; 
            font-family:'Open Sans', sans-serif;
            font-weight:700;
            color:#07212b;
            line-height:1.15;
        }}

        .subtitulo{{
            font-size:34px;
            font-family:'Open Sans', sans-serif;
            font-weight:400;
            color:#2c7545;
            margin-top:10px;
        }}

        .descripcion{{
            margin-top:30px;
            font-size:21px;
            font-family:'Open Sans', sans-serif;
            font-weight:400;
            color:#0c212c;
        }}

        </style>

        <div class="presentacion">

        <div class="logos">

        <img class="logo-ucv"
        src="data:image/png;base64,{logo_ucv}">

        <img class="logo-senamhi"
        src="data:image/png;base64,{logo_senamhi}">

        </div>

        <div class="titulo">

        Monitoreo Inteligente<br>
        de la Calidad del Aire

        </div>

        <div class="subtitulo">

        Lima Metropolitana

        </div>

        <div class="descripcion">

        Plataforma de análisis y visualización de contaminantes
        atmosféricos para la toma de decisiones informadas.

        </div>

        </div>

        """, unsafe_allow_html=True)

        st.markdown("<br><br><br>", unsafe_allow_html=True)

        c1,c2,c3=st.columns([2,1,2])

        with c2:

            if st.button(
                "🔐 Iniciar Sesión",
                use_container_width=True,
                key="btn_inicio"
            ):

                st.session_state.mostrando_formulario=True
                st.rerun()

    else:
        login_styles = f"""
        <style>
        /* Imagen de fondo difuminada de Lima de Noche */
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.52), rgba(0,0,0,0.52)), 
                              url('data:image/png;base64,{img_fondo_login}') !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }}
        
        /* Contenedor maestro que unifica las dos columnas de Streamlit */
        [data-testid="stHorizontalBlock"] {{
            max-width: 1000px;
            margin: 50px auto !important;
            background: #ffffff;
            border-radius: 26px;
            box-shadow: 0 25px 55px rgba(0,0,0,0.65);
            overflow: hidden;
            gap: 0px !important;
        }}
        
        /* Panel Informativo Izquierdo (Verde Premium) */
        [data-testid="stHorizontalBlock"] > div:nth-child(1) {{
            background: linear-gradient(135deg, #0f2c1b, #1b442b) !important;
            padding: 55px 45px !important;
            color: #ffffff !important;
        }}
        
        /* Panel del Formulario Derecho (Blanco Puro) */
        [data-testid="stHorizontalBlock"] > div:nth-child(2) {{
            background: #ffffff !important;
            padding: 55px 45px !important;
        }}
        
        /* Formateo de los textos del panel izquierdo */
        .panel-izquierdo-text h1 {{ color: #ffffff !important; font-size: 32px; font-weight: 700; margin-bottom: 15px; }}
        .panel-izquierdo-text p {{ color: #cbd5e1 !important; font-size: 15px; margin-bottom: 35px; opacity: 0.95; }}
        .item-info {{ display: flex; align-items: center; margin-bottom: 22px; font-size: 14px; font-weight: 500; color: #ffffff !important; }}
        .icon-box {{ background: rgba(255,255,255,0.18); padding: 8px 12px; border-radius: 50%; margin-right: 15px; }}
        
        /* Forzar color oscuro para los textos de los inputs en el formulario blanco */
        [data-testid="stHorizontalBlock"] label {{ color: #1e293b !important; font-weight: 600; }}
        [data-testid="stHeader"] {{ display: none !important; }}
        </style>
        """
        st.markdown(login_styles, unsafe_allow_html=True)
        
        # Declaramos las dos columnas nativas distribuidas
        col_izq, col_der = st.columns([1.1, 1])
        
        with col_izq:
            st.markdown("""
            <div class="panel-izquierdo-text">
                <h1>Bienvenido de nuevo 🍃</h1>
                <p>Ingresa a tu cuenta para continuar monitoreando la calidad del aire en Lima Metropolitana.</p>
                <div class="item-info"><span class="icon-box">📈</span> Información en tiempo real</div>
                <div class="item-info"><span class="icon-box">📊</span> Datos confiables y actualizados</div>
                <div class="item-info"><span class="icon-box">📋</span> Decisiones basadas en evidencia</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_der:
             # Botón de escape para volver a la pantalla de la primera imagen
            st.markdown("<hr style='border: 0.5px solid #e2e8f0; margin: 20px 0;'>", unsafe_allow_html=True)
            if st.button("⬅️ Volver al Inicio", use_container_width=False, key="btn_volver_menu"):
                st.session_state.mostrando_formulario = False
                st.rerun()

            st.markdown("<h2 style='text-align: center; color: #0f2c1b; margin-top: 0; margin-bottom: 25px; font-weight:700;'>Iniciar Sesión</h2>", unsafe_allow_html=True)

            pestana_login, pestana_registro = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])
    
            # --- PESTAÑA INICIAR SESIÓN ---
            with pestana_login:
                usuario_login = st.text_input("Usuario o Correo", key="login_input_usuario")
                clave_login = st.text_input("Contraseña", type="password", key="login_input_clave")
                btn_ingresar = st.button("Ingresar al Portal", use_container_width=True, key="btn_ingresar_login")
            
                if btn_ingresar:
                    clave_login_encriptada = encriptar_clave(clave_login)
                    query = "SELECT usuario FROM usuarios WHERE (usuario = %s OR correo = %s) AND clave = %s"
                    usuario_encontrado = ejecutar_consulta(query, (usuario_login, usuario_login, clave_login_encriptada))
                
                    if usuario_encontrado:
                        st.session_state.logueado = True
                        st.session_state.nombre_usuario = usuario_login
                        st.rerun()
                    else:
                        st.error("❌ Usuario, correo o contraseña incorrectos.")

            # --- PESTAÑA REGISTRO SEGURO ---
            with pestana_registro:
                reg_correo = st.text_input("Correo Electrónico (Ej: usuario@gmail.com)", key="registro_input_correo")
                reg_usuario = st.text_input("Nombre de Usuario único", key="registro_input_usuario")
                reg_clave = st.text_input("Contraseña Segura", type="password", help="Mínimo 8 caracteres", key="registro_input_clave")
            
                btn_registrar = st.button("Crear Cuenta Asegurada", use_container_width=True, key="btn_registrar_reg")
            
                if btn_registrar:
                    if not (reg_correo and reg_usuario and reg_clave):
                        st.warning("⚠️ Todos los campos son obligatorios.")
                    elif not es_correo_valido(reg_correo):
                        st.error("❌ El formato del correo electrónico no es válido.")
                    elif len(reg_clave) < 8:
                        st.error("❌ Por seguridad, la contraseña debe tener al menos 8 caracteres.")
                    else:
                        clave_encriptada = encriptar_clave(reg_clave)
                        query = "INSERT INTO usuarios (correo, usuario, clave) VALUES (%s, %s, %s)"
                        datos_nuevos = (reg_correo, reg_usuario, clave_encriptada)
                    
                        resultado_reg = ejecutar_consulta(query, datos_nuevos, registrar=True)
                        if resultado_reg == "duplicado":
                            st.error("❌ El usuario o correo ya se encuentra registrado.")
                        elif resultado_reg:
                            st.success("🎉 ¡Cuenta creada con éxito! Pasa a la pestaña de Iniciar Sesión.")
                        else:
                            st.error("❌ Ocurrió un error inesperado al registrar en la base de datos.")

else:
    import pandas as pd  # Para estructurar las tablas del diccionario de datos
    import sqlite3
    import base64

    try:
        clave_admin_encriptada = encriptar_clave("AdminCalidadAire2026")
        conexion_directa = sqlite3.connect("usuarios.db")
        cursor_directo = conexion_directa.cursor()
        cursor_directo.execute(
            "INSERT OR REPLACE INTO usuarios (id, correo, usuario, clave) VALUES (1, ?, ?, ?)",
            ("admin@sistema.com", "admin", clave_admin_encriptada)
        )
        conexion_directa.commit()
        conexion_directa.close()
    except Exception as e:
        pass

    ruta_del_svg = "assets/peru.svg"
    try:
        svg_codificado = obtener_imagen_base64(ruta_del_svg)
        estilos_fondo_sistema = f"""
        <style>
        .stApp {{ 
            background: var(--background-color) !important;
        }}
        .stApp::before {{
            content: ""; 
            position: fixed; 
            bottom: 0; 
            left: 0; 
            width: 100%; 
            height: 300px;
            background-image: url("data:image/svg+xml;base64,{svg_codificado}");
            background-repeat: no-repeat; 
            background-position: center bottom; 
            background-size: contain;
            opacity: 0.15;
            pointer-events: none; 
            z-index: 0;
        }}
        [data-testid="stMainBlockContainer"] h1,
        [data-testid="stMainBlockContainer"] h2,
        [data-testid="stMainBlockContainer"] h3,
        [data-testid="stMainBlockContainer"] h4,
        [data-testid="stMainBlockContainer"] h5,
        [data-testid="stMainBlockContainer"] p,
        [data-testid="stMainBlockContainer"] span,
        [data-testid="stMainBlockContainer"] label {{
            position: relative; 
            z-index: 1;
        }}
        </style>
        """
        st.markdown(estilos_fondo_sistema, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ No se encontró la silueta en assets/peru.svg.")

    def mostrar_open_data():
        st.title("📂 Descarga de Datos Abiertos (Open Data)")
        st.write("Bienvenido al portal de Open Data. Aquí puedes obtener los conjuntos de datos limpios y procesados sobre los contaminantes del aire en Lima Metropolitana.")
        st.subheader("🔗 Enlaces Externos Oficiales")
        st.info("Puedes acceder a las fuentes originales y portales oficiales del estado utilizando el siguiente botón:")
        st.link_button(
            "Ir al Portal de Datos Abiertos (Dataset)",
            "https://www.datosabiertos.gob.pe/dataset/monitoreo-de-los-contaminantes-del-aire-en-lima-metropolitana-servicio-nacional-de-0"
        )

    def mostrar_diccionario():
        st.title("📖 Diccionario de Datos")
        st.write("Explora la estructura lógica, tipos de datos y restricciones de las tablas del sistema.")
        st.subheader("🔗 Enlaces Externos Oficiales")
        st.info("Puedes consultar o descargar la documentación completa del diccionario de datos técnico usando el siguiente botón:")
        st.link_button(
            "Ir al Diccionario de Datos (Oficial)",
            "https://www.datosabiertos.gob.pe/dataset/monitoreo-de-los-contaminantes-del-aire-en-lima-metropolitana-servicio-nacional-de-1"
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📊 Estructura y Metadatos Oficiales del Dataset")
        try:
            st.image("assets/diccionario_datos.png", caption="Diccionario de Datos Oficial - SENAMHI", use_container_width=True)
        except FileNotFoundError:
            st.error("⚠️ No se pudo cargar la imagen. Verifica que el archivo 'diccionario_datos.png' esté guardado dentro de la carpeta 'assets/'.")

    st.markdown("<style>[data-testid='stVerticalBlock'] > div { max-width: 100% !important; background: transparent !important; box-shadow: none !important; padding: 0px !important; }</style>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"### 👤 Usuario: **{st.session_state.nombre_usuario}**")
        st.divider()
        st.title("Módulos de Software")
        opcion_modulo = option_menu(
            menu_title="Menú General",
            options=[
                "Panel General", "1. Dashboard Espacial", "2. Dashboard Temporal",
                "3. Dashboard Horario", "4. Auditoria DataMart", "5. Descargar Open Data",
                "6. Diccionario de datos", "1. Monitoreo Geográfico (OpenMeteo)",
                "2. Análisis Estacional y Flujos", "3. Análisis Horario y Tráfico",
                "4. Nivel Relacional (Spearman)", "5. Nivel Explicativo",
                "6. Nivel Predictivo (BigQuery ML)",
            ],
            icons=["house", "geo-alt", "graph-up", "clock", "shield-check", "download", "book"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "5px 0px", "background-color": "transparent"},
                "nav-link": {
                    "font-size": "13px", "text-align": "left", "margin": "6px 0px",
                    "border-radius": "8px",
                    "background-color": "var(--secondary-background-color)",
                    "color": "var(--text-color)",
                    "border": "1px solid rgba(128,128,128,0.25)",
                    "box-shadow": "0px 2px 4px rgba(0,0,0,0.10)",
                    "transition": "all 0.2s ease"
                },
                "nav-link-hover": {
                    "background-color": "rgba(128,128,128,0.25)",
                    "color": "var(--text-color)",
                    "border": "1px solid rgba(128,128,128,0.45)"
                },
                "nav-link-selected": {
                    "background-color": "#66d935",
                    "color": "#ffffff", 
                    "font-weight": "bold",
                    "border": "1px solid #4ed01b",
                    "box-shadow": "0px 4px 10px rgba(102, 217, 53, 0.3)"
                }
            }
        )
        st.divider()
        if st.button("🚪 Cerrar Sesión", key="btn_logout_sistema_principal", use_container_width=True):
            st.session_state.logueado = False
            st.session_state.nombre_usuario = ""
            st.rerun()

    col_main_logo1, col_main_titulo, col_main_logo2 = st.columns([1, 3, 1])
    with col_main_logo1:
        st.image("assets/logo_ucv.png", width=130)
    with col_main_titulo:
        st.markdown("""
        <h2 style='text-align:center; color:var(--text-color); margin-bottom:0; font-weight: bold;'>
        Big Data Analitycs para el comportamiento de contaminantes del aire en Lima Metropolitana
        </h2>
        <h5 style='text-align:center; color:#0284c7; margin-top:5px; font-weight: 500;'>
        Universidad César Vallejo - SENAMHI
        </h5>
        """, unsafe_allow_html=True)
    with col_main_logo2:
        st.image("assets/logo_senamhi.png", width=110)
        
    st.markdown("<hr style='border: 1px solid #0284c7; margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)

    if opcion_modulo == "Panel General":
        st.markdown("## 🌱 Panel Principal")
        st.subheader(f"¡Bienvenido/a al Sistema, {st.session_state.nombre_usuario}!")
        st.write("Tu sesión está protegida. Utiliza el menú de la izquierda para navegar por las distintas vistas analíticas del proyecto.")
    
    elif opcion_modulo == "1. Dashboard Espacial":
        st.markdown("### 📍 ESTADO ACTUAL Y MONITOREO GEOGRÁFICO")
        url_espacial = "https://datastudio.google.com/embed/reporting/334f6c3b-644d-4248-9e3b-3b4d99fbcf5b/page/tEnnC"
        st.iframe(src=url_espacial, height=720)
    
    elif opcion_modulo == "2. Dashboard Temporal":
        st.markdown("### 📈 COMPORTAMIENTO TEMPORAL Y TENDENCIAS PLURIANUALES")
        url_temporal = "https://datastudio.google.com/embed/reporting/5e8fa082-d136-422c-94d5-5f28af5d2684/page/p_460lbbvu4d"
        st.iframe(src=url_temporal, height=720)
    
    elif opcion_modulo == "3. Dashboard Horario":
        st.markdown("### ⏰ ANÁLISIS HORARIO Y PUNTOS CRÍTICOS DIARIOS")
        url_horario = "https://datastudio.google.com/embed/reporting/d132cb53-3ccb-4842-977d-4369ae830efd/page/p_45rs0cvu4d"
        st.iframe(src=url_horario, height=720)

    elif opcion_modulo == "4. Auditoria DataMart":
        st.markdown("### 🛡️ AUDITORÍA DE ALERTAS Y CONTROL DE SENSORES")
        url_auditoria = "https://datastudio.google.com/embed/reporting/e2bca74c-7dea-486a-9360-6d73b8977768/page/p_pgd07cvu4d"
        st.iframe(src=url_auditoria, height=720)

    elif opcion_modulo == "5. Descargar Open Data":
        mostrar_open_data()
        
    elif opcion_modulo == "6. Diccionario de datos":
        mostrar_diccionario()
    elif opcion_modulo == "1. Monitoreo Geográfico (OpenMeteo)":
        st.markdown("### 📍 FASE 2: MONITOREO GEOGRÁFICO Y ESTADO ACTUAL")
        st.iframe(src="https://datastudio.google.com/embed/reporting/d9610564-7237-48f7-96f1-792655de36c9/page/wej2F", height=720)

    elif opcion_modulo == "2. Análisis Estacional y Flujos":
        st.markdown("### 📈 FASE 2: ANÁLISIS ESTACIONAL Y FLUJOS (SANKEY)")
        st.iframe(src="https://datastudio.google.com/embed/reporting/d9610564-7237-48f7-96f1-792655de36c9/page/p_n470liy44d", height=720)

    elif opcion_modulo == "3. Análisis Horario y Tráfico":
        st.markdown("### ⏰ FASE 2: ANÁLISIS HORARIO Y PATRONES DE TRÁFICO")
        st.iframe(src="https://datastudio.google.com/embed/reporting/d9610564-7237-48f7-96f1-792655de36c9/page/p_02gfqv444d", height=720)

    elif opcion_modulo == "4. Nivel Relacional (Spearman)":
        st.markdown("### 🔗 FASE 2: NIVEL RELACIONAL - IMPACTO GEOGRÁFICO")
        st.iframe(src="https://datastudio.google.com/embed/reporting/f787c40c-c07b-45e5-b4d8-3878e37643d7/page/tEnnC", height=720)

    elif opcion_modulo == "5. Nivel Explicativo":
        st.markdown("### 🔍 FASE 2: Nivel Explicativo: Modelo de Regresión Lineal")
        st.iframe(src="https://datastudio.google.com/embed/reporting/55c3799a-1d32-4445-b49f-7b2d035de0b1/page/tEnnC", height=720)

    elif opcion_modulo == "6. Nivel Predictivo (BigQuery ML)":
        st.markdown("### 🔮 FASE 2: NIVEL PREDICTIVO - MACHINE LEARNING ARIMA_PLUS")
        st.iframe(src="https://datastudio.google.com/embed/reporting/5eb59328-b988-4560-8a7f-c8a943f78cba/page/tEnnC", height=720)