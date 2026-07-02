import streamlit as st
import base64
import sqlite3
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
def ejecutar_consulta(query, datos=None, registrar=False):
    # Esto crea automáticamente el archivo de la base de datos si no existe
    conexion = sqlite3.connect("usuarios.db")
    cursor = conexion.cursor()
    
    # Crea la tabla de usuarios automáticamente si es la primera vez que corre
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        correo TEXT UNIQUE,
        usuario TEXT UNIQUE,
        clave TEXT
    )
    """)
    conexion.commit()
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO usuarios (correo, usuario, clave) VALUES (?, ?, ?)",
            ("admin@sistema.com", "admin", "admin1234")
        )
        conexion.commit()
    except Exception as e:
        pass

    
    try:
        if datos:
            cursor.execute(query, datos)
        else:
            cursor.execute(query)
            
        if registrar:
            conexion.commit()
            return True
        else:
            return cursor.fetchall()
            
    except sqlite3.IntegrityError:
        # Esto maneja de forma automática los usuarios o correos duplicados
        return "duplicado"
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
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
            query = "SELECT usuario FROM usuarios WHERE (usuario = ? OR correo = ?) AND clave = ?"
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
                query = "INSERT INTO usuarios (correo, usuario, clave) VALUES (?, ?, ?)"
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

   #------------------------------------------------------------------
    else:
        import pandas as pd
        import sqlite3
        import base64
    
    # --- FORZAR REGISTRO DEL ADMIN (Tu lógica se mantiene igual) ---
    # ... (deja tu bloque try-except del admin como está) ...

    # 🎨 CSS MEJORADO: CONTRASTE CORRECTO Y MARCA DE AGUA AL 8%
        ruta_del_svg = "assets/peru.svg"
        try:
            svg_codificado = obtener_imagen_base64(ruta_del_svg)
            estilos_fondo_sistema = f"""
            <style>
            /* Fondo principal claro y limpio */
            .stApp {{
                background-color: #f8fafc !important;
            }}
            /* Reducimos la opacidad al 8% para que sea una marca de agua real y no sature */
            .stApp::before {{
                content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background-image: url("data:image/svg+xml;base64,{svg_codificado}");
                background-repeat: no-repeat; background-position: center 75%; background-size: 85% auto;
                opacity: 0.08; pointer-events: none; z-index: 0;
            }}
            /* IMPORTANTE: Cambia el color SOLO a los textos del contenedor principal, no al sidebar */
            [data-testid="stMainBlockContainer"] h1, 
            [data-testid="stMainBlockContainer"] h2, 
            [data-testid="stMainBlockContainer"] h3, 
            [data-testid="stMainBlockContainer"] h5, 
            [data-testid="stMainBlockContainer"] p, 
            [data-testid="stMainBlockContainer"] span, 
            [data-testid="stMainBlockContainer"] label {{
                color: #0f172a !important; /* Azul medianoche ultra legible */
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
                "1. Dashboard Espacial",
                "2. Dashboard Temporal",
                "3. Dashboard Horario",
                "4. Auditoria DataMart",
                "5. Descargar Open Data",
                "6. Diccionario de datos"
            ],
            icons=["house", "geo-alt", "graph-up", "clock", "shield-check", "download", "book"],
            menu_icon="cast",
            default_index=0,
            styles={
                "nav-link-selected": {"background-color": "#66d935"},
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

   


    

            
    



    