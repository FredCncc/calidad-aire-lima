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
st.set_page_config(page_title="Business Intelligence - Contaminación del Aire Lima", page_icon="🌎", layout="wide")

# --- FUNCIÓN DE VALIDACIÓN DE CORREO ---
def es_correo_valido(correo):
    # Verifica si el texto tiene estructura de correo real (ejemplo@dominio.com)
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, correo) is not None

# --- CONEXIÓN A BASE DE DATOS ---
# ==============================================================================
# ==============================================================================
# # --- CONEXIÓN CONFIGURADA PARA LA NUBE (SUPABASE) ---
# ==============================================================================
DB_HOST = "aws-1-us-east-2.pooler.supabase.com"
DB_PORT = "6543"
DB_NAME = "postgres"
DB_USER = "postgres.mstdoqrqeuhghzohqdgy"
DB_PASSWORD = "2004Coldplaydeco004"

def ejecutar_consulta(query, datos=None, registrar=False):
    try:
        # AQUÍ ESTÁ EL ARREGLO: Pasamos las variables explícitas que definiste arriba
        conexion = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            sslmode="require"
        )
        cursor = conexion.cursor()
        
        # Crear tabla si no existe
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            correo TEXT UNIQUE NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            clave TEXT NOT NULL
        );
        """)
        conexion.commit()

        # Insertar administrador por defecto de respaldo
        clave_admin_encriptada = encriptar_clave("admin1234")
        cursor.execute("""
            INSERT INTO usuarios (correo, usuario, clave) 
            VALUES (%s, %s, %s) 
            ON CONFLICT (usuario) DO NOTHING;
        """, ("admin@sistema.com", "admin", clave_admin_encriptada))
        conexion.commit()
        
        # Ejecutar la consulta recibida
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



# --- FUNCIÓN PARA EL VIDEO EN BASE64 ---
@st.cache_resource
def obtener_video_base64(ruta_video):
    with open(ruta_video, "rb") as video_file:
        datos = video_file.read()
    return base64.b64encode(datos).decode()
def obtener_imagen_base64(ruta_imagen):
    with open(ruta_imagen, "rb") as image_file:
        datos = image_file.read()
        return base64.b64encode(datos).decode()

# --- MANEJO DE SESIÓN ---
if "logueado" not in st.session_state:
    st.session_state.logueado = False
if "nombre_usuario" not in st.session_state:
    st.session_state.nombre_usuario = ""

# --- INTERFAZ 1: CAJA FLOTANTE DE LOGIN / REGISTRO ---
if not st.session_state.logueado:
    
    # 🌟 EL VIDEO SE MUEVE AQUÍ: Solo se procesará si no está logueado
    ruta_del_video = "assets/video_contaminacion.mp4"
    try:
        video_codificado = obtener_video_base64(ruta_del_video)
        estilos_video = f"""
        <style>
        #video-fondo {{
            position: fixed; right: 0; bottom: 0;
            min-width: 100%; min-height: 100%;
            width: auto; height: auto; z-index: -100;
            background-size: cover; opacity: 0.25;
        }}
        .stApp {{ background: transparent; }}
        </style>
        <video autoplay loop muted playsinline id="video-fondo">
            <source src="data:video/mp4;base64,{video_codificado}" type="video/mp4">
        </video>
        """
        st.markdown(estilos_video, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ No se encontró el video en assets/video_contaminacion.mp4.")
    
    # Encabezado superior con proporciones fijas [1, 3, 1] para evitar errores de Streamlit
    col_logo1, col_titulo, col_logo2 = st.columns([1, 3, 1])
    
    with col_logo1:
        st.image("assets/logo_ucv.png", width=140)
        
    with col_titulo:
        st.markdown("""
        <h1 style='text-align:center; color:#111111; font-size: 26px; margin-bottom:0; font-weight: bold;'>
        Big Data Analitycs para el comportamiento de contaminantes del aire en Lima Metropolitana
        </h1>
        <h4 style='text-align:center; color:#0284c7; font-size: 16px; margin-top:5px; font-weight: 500;'>
        Universidad César Vallejo - SENAMHI
        </h4>
        <br>
        <h3 style='text-align: center; color: #111111; font-size: 20px; margin-bottom: 5px;'>🔐 Inicio de Sesión</h3>
        """, unsafe_allow_html=True)
        
    with col_logo2:
        st.image("assets/logo_senamhi.png", width=140)
   
    st.markdown("<hr style='border: 1px solid #0284c7; margin-top: 0px; margin-bottom: 25px;'>", unsafe_allow_html=True)
    
    # Estilo de la caja flotante exclusiva para el formulario
    st.markdown("""
    <style>
    [data-testid="stTabs"] {
        background-color: rgba(255, 255, 255, 0.96);
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0px 10px 35px rgba(0, 0, 0, 0.35);
        max-width: 480px;
        margin: auto;
    }
    </style>
    """, unsafe_allow_html=True)

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

# --- INTERFAZ 2: ENTORNO INTERNO DEL SOFTWARE (PANEL PRINCIPAL) ---
else:
    import pandas as pd  # Para estructurar las tablas del diccionario de datos
    import sqlite3
    import base64

    # --- FORZAR REGISTRO DEL ADMIN (CORREGIDO Y ENCRIPTADO) ---
    try:
        # Encriptamos la clave primero para que coincida con el sistema de login
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

   # BLOQUE DEL COLOR DE FONDO DE PERU.SVG
    else:
        import pandas as pd
        import sqlite3
        import base64

        # 🎨 CONFIGURACIÓN DE INTERFAZ PREMIUM (ESTILO AQI.IN)
        ruta_del_svg = "assets/peru.svg"
        
        try:
            svg_codificado = obtener_imagen_base64(ruta_del_svg)
            estilos_fondo_sistema = f"""
            <style>
            /* 1. Fondo base con degradado suave crema/arena idéntico al de AQI.in */
            .stApp {{ 
                background: linear-gradient(180deg, #fdfbf7 0%, #f7f3eb 100%) !important;
            }}
            
            /* 2. Silueta de Perú fijada perfectamente en la parte inferior del fondo */
            .stApp::before {{
                content: ""; 
                position: fixed; 
                bottom: 0; 
                left: 0; 
                width: 100%; 
                height: 300px; /* Controla la altura de la silueta en la pantalla */
                background-image: url("data:image/svg+xml;base64,{svg_codificado}");
                background-repeat: no-repeat; 
                background-position: center bottom; 
                background-size: contain; /* Ajusta la silueta horizontalmente de forma limpia */
                opacity: 0.15; /* Opacidad sutil estilo marca de agua para que no sature tus reportes */
                pointer-events: none; 
                z-index: 0;
            }}
            
            /* 3. Estilos de texto oscuros para máxima lectura sobre el fondo claro */
            [data-testid="stMainBlockContainer"] h1,
            [data-testid="stMainBlockContainer"] h2,
            [data-testid="stMainBlockContainer"] h3,
            [data-testid="stMainBlockContainer"] h4,
            [data-testid="stMainBlockContainer"] h5,
            [data-testid="stMainBlockContainer"] p,
            [data-testid="stMainBlockContainer"] span,
            [data-testid="stMainBlockContainer"] label {{
                color: #1e293b !important; /* Gris azulado oscuro muy legible */
                position: relative; 
                z-index: 1;
            }}
            </style>
            """
            st.markdown(estilos_fondo_sistema, unsafe_allow_html=True)
        except FileNotFoundError:
            st.warning("⚠️ No se encontró la silueta en assets/peru.svg.")

    # =========================================================================

    # 🌟 DEFINICIÓN DE LAS FUNCIONES MÓDULO (Tu código continúa exactamente igual desde aquí...)
    def mostrar_open_data():
        st.title("📂 Descarga de Datos Abiertos (Open Data)")
    # 🌟 DEFINICIÓN DE LAS FUNCIONES MÓDULO (Colocadas arriba para evitar el error de Pylance)
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
        # 🔗 NUEVO BOTÓN: Enlace externo oficial para el diccionario de datos
        st.subheader("🔗 Enlaces Externos Oficiales")
        st.info("Puedes consultar o descargar la documentación completa del diccionario de datos técnico usando el siguiente botón:")
        st.link_button(
            "Ir al Diccionario de Datos (Oficial)",
            "https://www.datosabiertos.gob.pe/dataset/monitoreo-de-los-contaminantes-del-aire-en-lima-metropolitana-servicio-nacional-de-1"
        )
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 🖼️ NUEVA SECCIÓN: Mostrar imagen oficial en vez de las tablas de código
        st.subheader("📊 Estructura y Metadatos Oficiales del Dataset")
        try:
            # Asegúrate de colocar tu imagen 'diccionario_datos.png' dentro de la carpeta 'assets'
            st.image("assets/diccionario_datos.png", caption="Diccionario de Datos Oficial - SENAMHI", use_container_width=True)
        except FileNotFoundError:
            st.error("⚠️ No se pudo cargar la imagen. Verifica que el archivo 'diccionario_datos.png' esté guardado dentro de la carpeta 'assets/'.")

    # Asegurar que el entorno principal anule cualquier residuo de capas anteriores
    st.markdown("<style>[data-testid='stVerticalBlock'] > div { max-width: 100% !important; background: transparent !important; box-shadow: none !important; padding: 0px !important; }</style>", unsafe_allow_html=True)

    # 1. BARRA LATERAL (SIDEBAR)
    with st.sidebar:
        st.markdown(f"### 👤 Usuario: **{st.session_state.nombre_usuario}**")
        st.divider()
        st.title("Módulos de Software")
        
        opcion_modulo = option_menu(
            menu_title="Menú General",
            options=[
                "Panel General",
                # --- FASE 1: DATA CORE ORIGINAL ---
                "1. Dashboard Espacial",
                "2. Dashboard Temporal",
                "3. Dashboard Horario",
                "4. Auditoria DataMart",
                 # --- UTILITARIOS DE LA PRIMERA OPEN DATA---
                "5. Descargar Open Data",
                "6. Diccionario de datos",
                # --- FASE 2: BIG DATA & MACHINE LEARNING (OPENMETEO) ---
                "1. Monitoreo Geográfico (OpenMeteo)",
                "2. Análisis Estacional y Flujos",
                "3. Análisis Horario y Tráfico",
                "4. Nivel Relacional (Spearman)",
                "5. Nivel Explicativo",
                "6. Nivel Predictivo (BigQuery ML)",

            ],
            icons=["house", "geo-alt", "graph-up", "clock", "shield-check", "download", "book"],
            menu_icon="cast",
            default_index=0,
            # 🎨 ESTILOS PREMIUM CON CONTRASTE Y TARJETAS BLANCAS REALES
            styles={
                "container": {
                    "padding": "5px 0px", 
                    "background-color": "transparent" # Deja que actúe el fondo base
                },
                "nav-link": {
                    "font-size": "13px", 
                    "text-align": "left", 
                    "margin": "6px 0px",              # <-- Separación física real entre botones
                    "border-radius": "8px",            # <-- Bordes redondeados más visibles
                    "background-color": "#ffffff",     # <-- FONDO BLANCO FIJO para que resalte sobre el fondo gris de la barra lateral
                    "color": "#1e293b",                # <-- Texto oscuro legible
                    "border": "1px solid #e2e8f0",     # <-- BORDE GRIS CLARO para darle volumen al botón
                    "box-shadow": "0px 2px 4px rgba(0,0,0,0.05)", # <-- SOMBRA REAL sutil para que parezcan tarjetas flotantes
                    "transition": "all 0.2s ease"      # <-- Animación fluida para el mouse
                },
                "nav-link-hover": {
                    "background-color": "#cbd5e1",     # <-- PLOMO MÁS OSCURO al pasar el mouse para que se note el cambio de estado
                    "color": "#0f172a",
                    "border": "1px solid #94a3b8"      # <-- El borde también se oscurece al pasar el puntero
                },
                "nav-link-selected": {
                    "background-color": "#66d935",     # <-- Tu color verde cuando está activo
                    "color": "#ffffff", 
                    "font-weight": "bold",
                    "border": "1px solid #4ed01b",
                    "box-shadow": "0px 4px 10px rgba(102, 217, 53, 0.3)" # <-- Sombra verde al estar seleccionado
                }
            }

        )
        
        st.divider()
        if st.button("🚪 Cerrar Sesión", key="btn_logout_sistema_principal", use_container_width=True):
            st.session_state.logueado = False
            st.session_state.nombre_usuario = ""
            st.rerun()

    # 2. ENCABEZADO SUPERIOR DEL PANEL PRINCIPAL (Proporciones fijas [1, 3, 1] asignadas)
    col_main_logo1, col_main_titulo, col_main_logo2 = st.columns([1, 3, 1])
    with col_main_logo1:
        st.image("assets/logo_ucv.png", width=130)
    with col_main_titulo:
        st.markdown("""
        <h2 style='text-align:center; color:#111111; margin-bottom:0; font-weight: bold;'>
        Big Data Analitycs para el comportamiento de contaminantes del aire en Lima Metropolitana
        </h2>
        <h5 style='text-align:center; color:#0284c7; margin-top:5px; font-weight: 500;'>
        Universidad César Vallejo - SENAMHI
        </h5>
        """, unsafe_allow_html=True)
    with col_main_logo2:
        st.image("assets/logo_senamhi.png", width=110)
        
    st.markdown("<hr style='border: 1px solid #0284c7; margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)

    # 3. CONTROL DE VISTAS SEGÚN EL BOTÓN SELECCIONADO (Corregidos para coincidir con tus Options exactamente)
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
        # =====================================================================
        # 🔬 CONTROL DE VISTAS PARA LA FASE 2 (OPENMETEO & DATA SCIENCE)
        # =====================================================================
    elif opcion_modulo == "1. Monitoreo Geográfico (OpenMeteo)":
        st.markdown("### 📍 FASE 2: MONITOREO GEOGRÁFICO Y ESTADO ACTUAL")
        # Pon aquí tu enlace de Looker de la Página 1 de tu nueva tarea:
        st.iframe(src="https://datastudio.google.com/embed/reporting/d9610564-7237-48f7-96f1-792655de36c9/page/wej2F", height=720)

    elif opcion_modulo == "2. Análisis Estacional y Flujos":
        st.markdown("### 📈 FASE 2: ANÁLISIS ESTACIONAL Y FLUJOS (SANKEY)")
        # Pon aquí tu enlace de Looker de la Página 2 de tu nueva tarea:
        st.iframe(src="https://datastudio.google.com/embed/reporting/d9610564-7237-48f7-96f1-792655de36c9/page/p_n470liy44d", height=720)

    elif opcion_modulo == "3. Análisis Horario y Tráfico":
        st.markdown("### ⏰ FASE 2: ANÁLISIS HORARIO Y PATRONES DE TRÁFICO")
        # Pon aquí tu enlace de Looker de la Página 3 de tu nueva tarea:
        st.iframe(src="https://datastudio.google.com/embed/reporting/d9610564-7237-48f7-96f1-792655de36c9/page/p_02gfqv444d", height=720)

    elif opcion_modulo == "4. Nivel Relacional (Spearman)":
        st.markdown("### 🔗 FASE 2: NIVEL RELACIONAL - IMPACTO GEOGRÁFICO")
        # Pon aquí tu enlace de Looker del Gráfico de Dispersión de Spearman:
        st.iframe(src="https://datastudio.google.com/embed/reporting/f787c40c-c07b-45e5-b4d8-3878e37643d7/page/tEnnC", height=720)

    elif opcion_modulo == "5. Nivel Explicativo":
        st.markdown("### 🔍 FASE 2: Nivel Explicativo: Modelo de Regresión Lineal")
        # Pon aquí tu enlace de Looker de la Regresión Logística (Barras Azules/Naranjas):
        st.iframe(src="https://datastudio.google.com/embed/reporting/55c3799a-1d32-4445-b49f-7b2d035de0b1/page/tEnnC", height=720)

    elif opcion_modulo == "6. Nivel Predictivo (BigQuery ML)":
        st.markdown("### 🔮 FASE 2: NIVEL PREDICTIVO - MACHINE LEARNING ARIMA_PLUS")
        # Pon aquí tu enlace de Looker del Pronóstico con Bandas de Error:
        st.iframe(src="https://datastudio.google.com/embed/reporting/5eb59328-b988-4560-8a7f-c8a943f78cba/page/tEnnC", height=720)

    
    


    

   


    

            
    



    