import langchain_helper as lch
import streamlit as st

# --- Configuración de la página ---
st.set_page_config(
    page_title="Generador de Nombres para Mascotas",
    page_icon="🐾",
    layout="centered"
)

# --- Título y Descripción ---
# st.title("🐾 Generador de Nombres para Mascotas")
st.title("🐾 Asistente de IA para Mascotas y más")

# --- Usamos pestañas para separar la funcionalidad ---
tab1, tab2 = st.tabs(["Generador de Nombres", "Agente de Investigación"])

# --- Pestaña 1: Generador de Nombres (código existente) ---
with tab1:
    st.header("Generador de Nombres para Mascotas")
    st.markdown("Describe a tu mascota y te daremos nombres geniales.")
    
    with st.form("name_generator_form"):
        descripcion_mascota = st.text_area(
            label="Describe a tu mascota aquí:",
            placeholder="Ej: Gatita negra, muy sigilosa y le gusta esconderse en la sombra.",
            max_chars=120,
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



# st.markdown("""
# ¡Dale a tu nuevo amigo el nombre genial que se merece! 
# Describe a tu mascota y nuestra IA te sugerirá nombres originales con un toque de personalidad.
# """)

# # --- Formulario de entrada ---
# with st.form("name_generator_form"):
#     descripcion = st.text_area(
#         label="Describe a tu mascota aquí:",
#         placeholder="Ej: Gatita negra, muy sigilosa y le gusta esconderse en la sombra.",
#         max_chars=120,
#         height=100
#     )
#     submitted = st.form_submit_button("✨ Generar Nombres")

# --- Lógica de Generación y Visualización ---
# if submitted and descripcion:
#     # Usamos un 'spinner' para mostrar que está trabajando
#     with st.spinner("Buscando el nombre perfecto... 🧠"):
#         try:
#             # Creamos la instancia una sola vez
#             # @st.cache_resource se asegura de que esto no se recree en cada recarga
#             @st.cache_resource
#             def get_generator():
#                 return lch.PetNameGenerator()

#             name_generator = get_generator()
            
#             # Llamamos al nuevo método 'generate' que devuelve datos
#             generated_names = name_generator.generate(descripcion)

#             # --- Mostramos los resultados ---
#             st.subheader("¡Aquí tienes algunas ideas!", divider="rainbow")

#             if "error" in generated_names[0]:
#                 st.error(f"**Error:** {generated_names[0]['error']}")
#                 st.code(generated_names[0]['raw'])
#             else:
#                 for item in generated_names:
#                     st.markdown(f"### • **{item['name']}**")
#                     st.markdown(f"> _{item['justification']}_")
#                     st.write("---") # Separador
        
#         except Exception as e:
#             st.error(f"Ha ocurrido un error inesperado: {e}")

# elif submitted:
#     st.warning("Por favor, escribe una descripción de tu mascota.")

# descripcion = st.text_area(
#     label="Escribe una frase descriptiva de tu mascota y observa los posibles nombres",
#     max_chars=200
# )

# if descripcion:
#     mascota = lch.PetNameGenerator()
#     st.text(mascota.generate_and_show(descripcion))