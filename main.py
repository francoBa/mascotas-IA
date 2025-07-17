import langchain_helper as lch
import streamlit as st
import pytz
from datetime import datetime
import asyncio

# --- PARCHE PARA EL EVENT LOOP EN STREAMLIT ---
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

st.set_page_config(page_title="Asistente de IA Multifunción", page_icon="🤖", layout="centered")
st.title("🤖 Asistente de IA Multifunción")

# --- Inicialización de Clases en Session State (Más eficiente) ---
@st.cache_resource
def get_pet_name_generator():
    return lch.PetNameGenerator()

@st.cache_resource
def get_agent_executor():
    # Creamos una instancia temporal solo para llamar al método.
    return lch.PetNameGenerator().create_agent_executor()

@st.cache_resource
def get_doc_assistant():
    return lch.DocumentAssistant()

st.session_state.pet_name_generator = get_pet_name_generator()
st.session_state.agent_executor = get_agent_executor()
st.session_state.doc_assistant = get_doc_assistant()

# --- Usamos pestañas para separar la funcionalidad ---
tab1, tab2, tab3 = st.tabs(["Generador de Nombres", "Agente de Investigación", "Asistente de Documentos (RAG)"])

# --- Pestaña 1: Generador de Nombres (código existente) ---
with tab1:
    st.header("Generador de Nombres para Mascotas")
    st.markdown("Describe a tu mascota y te daremos nombres geniales.")
    
    with st.form("name_generator_form"):
        descripcion_mascota = st.text_area(
            label="Describe a tu mascota aquí:",
            placeholder="Ej: Gatita negra, muy sigilosa y le gusta esconderse en la sombra.",
            max_chars=150,
            height=100
        )
        submitted_name = st.form_submit_button("✨ Generar Nombres")

    if submitted_name and descripcion_mascota:
        with st.spinner("Buscando el nombre perfecto... 🧠"):
            try:
                # Creamos la instancia una sola vez
                # @st.cache_resource se asegura de que esto no se recree en cada recarga
                @st.cache_resource
                def get_generator():
                    return lch.PetNameGenerator()

                name_generator = get_generator()
                
                # Llamamos al nuevo método 'generate' que devuelve datos
                generated_names = name_generator.generate(descripcion_mascota)

                # --- Mostramos los resultados ---
                st.subheader("¡Aquí tienes algunas ideas!", divider="rainbow")

                if "error" in generated_names[0]:
                    st.error(f"**Error:** {generated_names[0]['error']}")
                    st.code(generated_names[0]['raw'])
                else:
                    for item in generated_names:
                        st.markdown(f"### • **{item['name']}**")
                        st.markdown(f"> _{item['justification']}_")
                        st.write("---") # Separador
            
            except Exception as e:
                st.error(f"Ha ocurrido un error inesperado: {e}")

    elif submitted_name:
        st.warning("Por favor, escribe una descripción de tu mascota.")


# --- Pestaña 2: Nuevo Agente Interactivo ---
with tab2:
    st.header("Agente de Investigación (con Wikipedia y Calculadora)")
    st.markdown("Haz una pregunta que requiera buscar información o hacer cálculos.")
    
        # --- SELECCIÓN DE ZONA HORARIA MANUAL (LA SOLUCIÓN ROBUSTA) ---
    # Intentamos poner la zona horaria de Argentina por defecto, con un fallback a UTC.
    try:
        default_tz_index = pytz.all_timezones.index("America/Argentina/Buenos_Aires")
    except ValueError:
        default_tz_index = pytz.all_timezones.index("UTC")

    selected_timezone = st.selectbox(
        "Elige tu zona horaria para preguntas sobre fechas:",
        options=pytz.all_timezones,
        index=default_tz_index,
        help="La fecha y hora de esta zona horaria se pasará al agente para cálculos precisos."
    )
    
    st.session_state.user_timezone = selected_timezone

    # Formulario para la pregunta del agente
    with st.form("agent_form"):
        pregunta_agente = st.text_area(
            "Tu pregunta:", 
            placeholder="Ej: ¿Cuántos años han pasado desde la invención del teléfono?",
            height=100, # <-- Le damos un poco más de altura
            max_chars=300 # <-- Límite de seguridad
        )
        submitted_agent = st.form_submit_button("🤖 Preguntar al Agente")

    if submitted_agent and pregunta_agente:
        with st.spinner("El agente está pensando y usando sus herramientas... 🔎"):
            # --- CÁLCULO DE LA HORA LOCAL DEL USUARIO ---
            utc_now = datetime.now(pytz.utc)
            try:
                # Usamos la zona horaria que obtuvimos del navegador
                user_tz = pytz.timezone(st.session_state.user_timezone)
                user_now = utc_now.astimezone(user_tz)
                current_time_str = user_now.strftime('%Y-%m-%d %H:%M:%S %Z')
            except pytz.UnknownTimeZoneError:
                # Fallback por si la zona horaria devuelta no es válida
                current_time_str = utc_now.strftime('%Y-%m-%d %H:%M:%S UTC')
                st.warning(f"No se pudo determinar tu zona horaria. Usando UTC como referencia.")
            
            # Mostramos la hora que usará el agente para que el usuario sea consciente
            st.info(f"ℹ️ Usando como fecha y hora actual: **{current_time_str}**")
            
            # .invoke() es la nueva forma de ejecutar el agente.
            # Pasamos la pregunta en un diccionario con la clave 'input'.
            response = st.session_state.agent_executor.invoke({
                "input": pregunta_agente,
                "current_time": current_time_str # <-- Pasamos la fecha al prompt
            })
            
            st.subheader("Respuesta del Agente:")
            # La respuesta final se encuentra en la clave 'output'.
            st.write(response['output'])
            # Podemos mostrar los pasos intermedios si quisiéramos, 
            # pero por ahora, la salida de verbose=True se verá en la consola 
            # donde corre Streamlit. Para mostrarlo en la UI se necesita
            # una configuración más avanzada (callbacks).


# --- Pestaña 3: Nuevo Asistente de Documentos (RAG) ---
with tab3:
    st.header("Chatea con tus Documentos")
    st.markdown("Sube un PDF o proporciona una URL de YouTube para hacerle preguntas sobre su contenido.")

    PDF_MAX_SIZE_MB = 50 # Pongamos un límite más razonable para empezar
    source_type = st.radio("Elige el tipo de fuente:", ("PDF", "YouTube"), horizontal=True, key="source_type_selector")
    
    source = None
    if source_type == "PDF":
        source = st.file_uploader(
            label=f"**Sube tu archivo PDF (Límite: {PDF_MAX_SIZE_MB} MB)**",
            help=f"El tamaño máximo permitido es de {PDF_MAX_SIZE_MB} MB.",
            type="pdf",
            key="pdf_uploader"
        )
    else:
        source = st.text_input("Ingresa la URL de YouTube", max_chars=80, key="youtube_url_input")

    if st.button("Procesar Documento", key="process_button"):
        if source:
            is_valid = True
            if source_type == 'PDF' and source.size / (1024 * 1024) > PDF_MAX_SIZE_MB:
                st.error(f"Error: El archivo es demasiado grande. El límite es de {PDF_MAX_SIZE_MB} MB.")
                is_valid = False
            
            if is_valid:
                st.info(f"Procesando {source_type}... Para archivos grandes, esto puede tardar varios minutos. Por favor, espera.")
                progress_bar = st.progress(0, text="Iniciando procesamiento...")
                
                try:
                    # Pasamos la barra de progreso a nuestro método del helper
                    vector_db = st.session_state.doc_assistant.create_vector_db(
                        source, source_type.lower(), streamlit_progress_bar=progress_bar
                    )
                    st.session_state.vector_store = vector_db
                    progress_bar.progress(1.0, text="¡Documento procesado!")
                    st.success("¡Listo para tus preguntas!")
                    if 'query_input' in st.session_state:
                        st.session_state.query_input = ""
                
                except Exception as e:
                    progress_bar.empty() # Ocultamos la barra de progreso si hay un error
                    # --- LÓGICA DE MENSAJE DE ERROR INTELIGENTE PARA EL USUARIO ---
                    error_message = str(e)
                    # Verificamos si es el error específico de límite de cuota
                    if "Quota exceeded" in error_message or "429" in error_message or "limit" in error_message.lower():
                        st.error("Se ha alcanzado el límite de uso de la API.")
                        st.warning(
                            "Has realizado demasiadas peticiones en un corto período de tiempo. "
                            "Esto suele ocurrir al procesar documentos muy grandes.\n\n"
                            "**Por favor, espera unos minutos e inténtalo de nuevo.**"
                        )
                    else:
                        # Para cualquier otro error, mostramos un mensaje más genérico
                        st.error("Ocurrió un error inesperado al procesar el documento.")
                        st.info(
                            "Esto puede deberse a un formato de archivo incorrecto, un video sin transcripción, "
                            "o un problema temporal de conexión. Por favor, verifica la fuente y vuelve a intentarlo."
                        )
        else:
            st.warning("Por favor, sube un archivo o ingresa una URL.")

    if 'vector_store' in st.session_state:
        st.subheader("Haz tu pregunta sobre el documento:", divider="rainbow")
        
        # --- NUEVO SELECTOR DE ESTRATEGIA ---
        strategy = st.selectbox(
            "Elige una estrategia de consulta:",
            options=["Simple (Rápida)", "Map-Reduce (Para documentos grandes)", "Refine (La más robusta)"],
            index=0,
            help="**Simple:** Rápida, ideal para la mayoría de los casos. **Map-Reduce:** Buena para PDFs grandes, procesa en paralelo. **Refine:** La más lenta pero la que mejor maneja documentos muy densos y evita errores de límite."
        )
        
        use_advanced_retriever = st.toggle(
            "Activar búsqueda avanzada (Multi-Query)", value=False,
            help="Usa IA para generar múltiples preguntas y mejorar la calidad de la búsqueda. Un poco más lento."
        )
            
        chain_type = {"Simple (Rápida)": "stuff", "Map-Reduce (Para documentos grandes)": "map_reduce", "Refine (La más robusta)": "refine"}[strategy]
        
        query = st.text_area("Pregunta:", height=100, max_chars=150, key="query_input")
        
        if st.button("Obtener Respuesta", key="get_answer_button"):
            if query:
                spinner_message = f"Procesando en modo '{strategy}'..." if chain_type != "stuff" else "Buscando la respuesta..."
                
                with st.spinner(spinner_message):
                    try:
                        # --- CÓDIGO DE LLAMADA SIMPLIFICADO ---
                        rag_chain = st.session_state.doc_assistant.create_rag_chain(
                            st.session_state.vector_store, use_advanced_retriever, chain_type
                        )
                        response = rag_chain.invoke({"input": query})
                        st.success("Respuesta:")
                        st.write(response['answer'])

                    except Exception as e:
                        st.error("Ocurrió un error al generar la respuesta.")
                        
                        # --- LÓGICA DE MENSAJE INTELIGENTE ---
                        error_message = str(e)
                        if "ResourceExhausted" in error_message or "limit" in error_message.lower():
                            # El error es de límite de API
                            if chain_type == "stuff":
                                st.warning("El documento parece ser muy grande para el modo simple. Prueba seleccionando la estrategia 'Map-Reduce' o 'Refine'.")
                            elif chain_type == "map_reduce":
                                st.warning("Incluso con el modo Map-Reduce, se alcanzó un límite. El documento puede ser extremadamente denso. Prueba la estrategia 'Refine', que es más lenta pero más segura.")
                            else: # Refine
                                st.warning("Se alcanzó un límite incluso con la estrategia más robusta. El documento es excepcionalmente grande o complejo. Intenta con una pregunta más específica o un documento más pequeño.")
                        else:
                            # Otros errores
                            st.info(f"Detalle técnico: {error_message}")
            else:
                st.warning("Por favor, escribe una pregunta.")