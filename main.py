import langchain_helper as lch
import streamlit as st

# --- Configuración de la página ---
st.set_page_config(
    page_title="Generador de Nombres para Mascotas",
    page_icon="🐾",
    layout="centered"
)

# --- Título y Descripción ---
st.title("🐾 Generador de Nombres para Mascotas")
st.markdown("""
¡Dale a tu nuevo amigo el nombre genial que se merece! 
Describe a tu mascota y nuestra IA te sugerirá nombres originales con un toque de personalidad.
""")

# --- Formulario de entrada ---
with st.form("name_generator_form"):
    descripcion = st.text_area(
        label="Describe a tu mascota aquí:",
        placeholder="Ej: Gatita negra, muy sigilosa y le gusta esconderse en la sombra.",
        max_chars=120,
        height=100
    )
    submitted = st.form_submit_button("✨ Generar Nombres")

# --- Lógica de Generación y Visualización ---
if submitted and descripcion:
    # Usamos un 'spinner' para mostrar que está trabajando
    with st.spinner("Buscando el nombre perfecto... 🧠"):
        try:
            # Creamos la instancia una sola vez
            # @st.cache_resource se asegura de que esto no se recree en cada recarga
            @st.cache_resource
            def get_generator():
                return lch.PetNameGenerator()

            name_generator = get_generator()
            
            # Llamamos al nuevo método 'generate' que devuelve datos
            generated_names = name_generator.generate(descripcion)

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

elif submitted:
    st.warning("Por favor, escribe una descripción de tu mascota.")

# descripcion = st.text_area(
#     label="Escribe una frase descriptiva de tu mascota y observa los posibles nombres",
#     max_chars=200
# )

# if descripcion:
#     mascota = lch.PetNameGenerator()
#     st.text(mascota.generate_and_show(descripcion))