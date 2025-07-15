import langchain_helper as lch
import streamlit as st

# --- Configuración de la página (sin cambios) ---
st.set_page_config(
    page_title="Asistente de IA Multifunción",
    page_icon="🤖",
    layout="centered"
)
st.title("🤖 Asistente de IA Multifunción")

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
    
    # Usamos st.session_state para recordar el agente y no recrearlo
    if 'agent_executor' not in st.session_state:
        # Creamos una instancia de nuestra clase helper
        helper = lch.PetNameGenerator()
        st.session_state.agent_executor = helper.create_agent_executor()

    # Formulario para la pregunta del agente
    with st.form("agent_form"):
        pregunta_agente = st.text_area(
            "Tu pregunta:", 
            placeholder="Ej: ¿Quién fue el primer emperador de Roma? ¿En qué año comenzó su mandato?",
            height=100, # <-- Le damos un poco más de altura
            max_chars=300 # <-- Límite de seguridad
        )
        submitted_agent = st.form_submit_button("🤖 Preguntar al Agente")

    if submitted_agent and pregunta_agente:
        with st.spinner("El agente está pensando y usando sus herramientas... 🔎"):
            # .invoke() es la nueva forma de ejecutar el agente.
            # Pasamos la pregunta en un diccionario con la clave 'input'.
            response = st.session_state.agent_executor.invoke({
                "input": pregunta_agente
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

    # Inicializamos el asistente en el session_state
    if 'doc_assistant' not in st.session_state:
        st.session_state.doc_assistant = lch.DocumentAssistant()

    # Selección del tipo de fuente
    source_type = st.radio("Elige el tipo de fuente:", ("PDF", "YouTube"), horizontal=True)

    # Widgets de entrada para la fuente
    if source_type == "PDF":
        uploaded_file = st.file_uploader(
            label=f"**1. Sube tu archivo PDF (Límite: {PDF_MAX_SIZE_MB} MB)**",
            help=f"Arrastra un archivo o haz clic para buscarlo. El tamaño máximo permitido es de {PDF_MAX_SIZE_MB} MB.",
            type="pdf"
        )
        source = uploaded_file
    else:
        youtube_url = st.text_input("Ingresa la URL de YouTube", max_chars=80)
        source = youtube_url

    if st.button("Procesar Documento"):
        if source:
            # --- NUEVO BLOQUE DE VALIDACIÓN ---
            is_valid = True # Empezamos asumiendo que es válido
            if source_type == 'PDF':
                file_size_mb = source.size / (1024 * 1024) # Convertimos bytes a MB
                if file_size_mb > PDF_MAX_SIZE_MB:
                    st.error(f"Error: El archivo es demasiado grande ({file_size_mb:.2f} MB). El límite es de {PDF_MAX_SIZE_MB} MB.")
                    is_valid = False # Marcamos como no válido
            # Solo continuamos si la validación pasó
            if is_valid:
                with st.spinner(f"Procesando {source_type}... Para archivos grandes, esto puede tardar varios minutos."):
                    try:
                        # Creamos la base de datos de vectores y la guardamos en el estado de la sesión
                        vector_db = st.session_state.doc_assistant.create_vector_db(source, source_type.lower())
                        st.session_state.vector_store = vector_db
                        st.success(f"¡{source_type} procesado y listo para tus preguntas!")
                    except Exception as e:
                        st.error(f"Error al procesar: {e}")
                        st.warning("Esto puede ocurrir con PDFs muy grandes debido a los límites de la API o con videos sin transcripción. Intenta con un documento más pequeño o un video diferente.")
        else:
            st.warning("Por favor, sube un archivo o ingresa una URL.")

    # Sección de preguntas, solo aparece si el documento ha sido procesado
    if 'vector_store' in st.session_state:
        st.subheader("Haz tu pregunta sobre el documento:", divider="rainbow")
        
        # ¡NUEVA OPCIÓN PARA EL USUARIO!
        use_advanced_retriever = st.toggle(
            "Activar búsqueda avanzada (Multi-Query)", 
            value=True, # Activado por defecto
            help="Usa un LLM para generar múltiples preguntas y mejorar la calidad de la búsqueda. Puede ser un poco más lento."
        )
        
        query = st.text_area("Pregunta:", height=100, max_chars=150)
        
        if st.button("Obtener Respuesta"):
            if query:
                with st.spinner("Buscando la respuesta..."):
                    # Obtenemos la base de datos de vectores del estado de la sesión
                    vector_store = st.session_state.vector_store
                    
                    if use_advanced_retriever:
                        # Usamos la nueva cadena avanzada
                        rag_chain = st.session_state.doc_assistant.create_advanced_rag_chain(vector_store)
                    else:
                        # Usamos la cadena simple original
                        rag_chain = st.session_state.doc_assistant.create_rag_chain(vector_store)
                    
                    # Invocamos la cadena para obtener la respuesta
                    response = rag_chain.invoke(query)
                    
                    st.success("Respuesta:")
                    st.write(response)
            else:
                st.warning("Por favor, escribe una pregunta.")