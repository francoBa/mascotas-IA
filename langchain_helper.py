# forma antigua - deprecated
#from langchain.llms import OpenAI

# BUENA PRÁCTICA
# import os
# import sys # <-- Importamos el módulo del sistema
# from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI
# import re # Importamos el módulo de expresiones regulares para parsear la respuesta

# 1. Carga las variables desde el archivo .env
# Esto lee el archivo .env y pone GOOGLE_API_KEY a disposición del programa.
# load_dotenv()

# 2. (Opcional pero recomendado) Verifica que la clave existe
# if not os.getenv("GOOGLE_API_KEY"):
#     raise ValueError("No se encontró la GOOGLE_API_KEY. Revisa tu archivo .env.")

# 3. Instancia el modelo de forma limpia
# No es necesario pasar la clave aquí. LangChain la encontrará por sí solo.
# print("Credenciales encontradas. Cargando el modelo gemini-2.5-flash...")
# try:
#     llm = ChatGoogleGenerativeAI(
#         model="gemini-2.5-flash",
#         temperature=0.8,  # Un valor entre 0.7 y 0.9 es ideal para creatividad
#         top_p=0.9,
#         top_k=40 # A menudo se usa junto a top_p
#     )
# except Exception as e:
#     print(f"Error al cargar el modelo: {e}")
#     print("El programa no puede continuar. Revisa tu API Key y el nombre del modelo.")
    # Al usar exit(), nos aseguramos de que si ocurre un error crítico al inicio, el programa se detiene de inmediato con un mensaje claro, evitando errores en cadena más adelante
    # sys.exit(1) # <-- Usamos sys.exit(). El '1' indica que hubo un error.

# 4. ¡A usarlo!
# print("¡Modelo listo! Ahora puedes interactuar con Gemini.")
# prompt = "Escribe un poema corto sobre la velocidad de la luz y la información."

# def generate_pet_name():
#     name = "Tengo una gatita y quiero un nombre copado para llamarla. Sugiereme 5 nombres muy buenos para mi mascota"
#     return name

# función mejorada con tipos fijos
# def generate_pet_name(animal_type: str, gender: str, style: str) -> str:
#     """
#     Genera una lista de nombres de mascotas usando Gemini.

#     Args:
#         animal_type (str): El tipo de animal (e.g., "gato", "perro", "hurón").
#         gender (str): El género del animal (e.g., "hembra", "macho").
#         style (str): El estilo de nombres deseado (e.g., "copados y modernos", "mitológicos", "de personajes de ciencia ficción").
    
#     Returns:
#         str: La respuesta del modelo con la lista de nombres.
#     """
#     print(f"\nBuscando 5 nombres de estilo '{style}' para un(a) {animal_type} {gender}...")

#     # Creamos un prompt dinámico usando f-strings. ¡Mucho más flexible!
#     prompt = f"""
#     Eres un experto en encontrar los nombres más originales y geniales para mascotas.
#     Quiero que me sugieras 5 nombres para mi {animal_type} {gender}.
#     El estilo de los nombres que busco es: {style}.
    
#     Por favor, presenta los nombres en una lista numerada y no añadas ninguna explicación adicional, solo la lista.
#     """
    
#     # Invocamos el modelo con nuestro prompt dinámico
#     response = llm.invoke(prompt)
    
#     return response.content

# función mejorada con prompt engineering avanzado
# def generate_pet_name_pro(animal_description: str) -> str:
#     """
#     Genera nombres de mascotas usando un prompt estructurado y avanzado.
#     """
    
#     # Este es el prompt "maestro", adaptado de tu ejemplo.
#     prompt_template = f"""
#     # Rol
#     Eres un 'Bautizador de Mascotas' legendario, un poeta de los nombres con un don único para capturar la esencia de un animal en una sola palabra. Tu estilo es moderno, cool, y evita los clichés a toda costa.

#     # Tarea
#     A partir de la descripción de la mascota que te proporciono en el #Contexto, tu misión es generar una lista de 5 nombres que cumplan con todos los requerimientos.

#     # Requerimientos
#     1.  **Originalidad Máxima:** Evita a toda costa nombres comunes como "Luna", "Max", "Bella", "Simba", "Lola".
#     2.  **Estilo "Cool":** Los nombres deben sonar interesantes, modernos y tener carácter. Pueden ser de mitología, ciencia ficción, literatura, o simplemente palabras que suenen bien.
#     3.  **Breve Justificación:** Al lado de cada nombre, entre paréntesis, añade una brevísima explicación de una línea sobre por qué ese nombre es genial para esa mascota.
#     4.  **Formato Estricto:** La salida debe ser una lista numerada del 1 al 5. No incluyas introducciones, saludos ni despedidas. Solo la lista.
#     5.  **Idioma:** Utiliza un español universalmente entendible pero con un toque moderno, similar al que se usaría en Argentina para algo "con onda".

#     # Contexto
#     La mascota a nombrar es la siguiente:
#     {animal_description}

#     # Ejemplo de Salida Perfecta
#     (Si el contexto fuera "gatita negra, muy sigilosa y elegante")

#     1.  Umbra (Significa "sombra" en latín, perfecto para su color y sigilo).
#     2.  Nyx (La diosa griega de la noche, poderoso y místico).
#     3.  Vesper (Relacionado con el atardecer, suena sofisticado y misterioso).
#     4.  Morwen (Un nombre de la literatura de Tolkien, suena fuerte y elegante).
#     5.  Pixel (Un toque geek y moderno para una gata pequeña y precisa).
#     """
    
#     print(f"\nGenerando nombres PRO para: {animal_description}")
#     response = llm.invoke(prompt_template)
#     return response.content


# --- MÉTODO ANTIGUO (INVOKE) ---
# print("--- Usando .invoke() (espera completa) ---")
# response = llm.invoke(prompt)
# print(response.content)
# print("\n" + "="*40 + "\n")


# --- MÉTODO NUEVO Y RÁPIDO (STREAM) ---
# print("--- Usando .stream() (respuesta inmediata palabra por palabra) ---")
# .stream() devuelve un generador que podemos recorrer con un bucle for
# full_response = ""
# for chunk in llm.stream(prompt):
#     # chunk.content contiene el nuevo trozo de texto
#     print(chunk.content, end="", flush=True) # flush=True fuerza la impresión inmediata
#     full_response += chunk.content

# if __name__ == "__main__":
    # --- ¡Ahora usemos nuestra función! ---
    # 1. Tu petición original
    # nombres_gata_cool = generate_pet_name(animal_type="gatita", gender="hembra", style="copados y modernos")
    # print("--- Nombres para Gatita Cool ---")
    # print(nombres_gata_cool)

    # # 2. Probemos con otra mascota para ver la flexibilidad
    # nombres_perro_heroe = generate_pet_name(animal_type="perro", gender="macho", style="de héroes de videojuegos")
    # print("--- Nombres para Perro Héroe ---")
    # print(nombres_perro_heroe)

    # # 3. Y otra más
    # nombres_hamster_comida = generate_pet_name(animal_type="hámster", gender="hembra", style="inspirados en comida deliciosa")
    # print("--- Nombres para Hámster Comida ---")
    # print(nombres_hamster_comida)
    
    # --- Usemos la nueva función PRO ---
    # descripcion = "Gatita hembra, de color blanco y negro, muy juguetona y un poco cariñosa."
    # nombres_pro = generate_pet_name_pro(descripcion)
    # print(nombres_pro)
    
    

# usando clases y SOLID
# class PetNameGenerator:
#     def __init__(self, provider="google", temperature=0.8, top_p=0.9):
#         # El constructor se encarga de la configuración inicial.
#         self.temperature = temperature
#         self.top_p = top_p
#         if provider == "google":
#             self.llm = ChatGoogleGenerativeAI(
#                 model="gemini-1.5-flash",
#                 temperature=self.temperature,
#                 top_p=self.top_p
#             )
#         # Aquí podrías añadir un elif para 'openai', etc.
        
#         self.prompt_template = """
# # Rol
# ... (el prompt avanzado que definimos antes) ...
# """

#     def generate(self, animal_description: str) -> str:
#         # El método se centra solo en su tarea: generar.
#         final_prompt = self.prompt_template.format(animal_description=animal_description)
#         response = self.llm.invoke(final_prompt)
#         return response.content

# # --- Uso de la clase ---
# # Creas la instancia una vez
# name_generator = PetNameGenerator() 

# # Y la usas las veces que quieras
# descripcion_perro = "Cachorro de Corgi, muy enérgico y siempre parece estar sonriendo."
# nombres_perro = name_generator.generate(descripcion_perro)
# print(nombres_perro)



# usando clases y SOLID
import os
import sys
import re # Importamos el módulo de expresiones regulares para parsear la respuesta
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser # Un parser simple

# --- Clase para los Colores ANSI ---
# Definir esto en una clase hace que el código sea más legible
class Colors:
    HEADER = '\033[95m'    # Morado claro
    BLUE = '\033[94m'      # Azul
    CYAN = '\033[96m'      # Cyan
    GREEN = '\033[92m'     # Verde
    WARNING = '\033[93m'   # Amarillo
    FAIL = '\033[91m'      # Rojo
    ENDC = '\033[0m'       # Código para resetear el color
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# --- Nuestra Clase Principal ---
class PetNameGenerator:
    def __init__(self, temperature=0.8, top_p=0.9, top_k=40):
        load_dotenv()
        # algunas variables que sólo las usamos de manera temporal las delcaramos como locales (sin self.)
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=temperature,
                top_p=top_p,
                top_k=top_k
            )
        except Exception as e:
            print(f"{Colors.FAIL}Error crítico al cargar el modelo: {e}{Colors.ENDC}")
            sys.exit(1)

        template_string = """
        # Rol
        Eres un 'Bautizador de Mascotas' legendario, un poeta de los nombres con un don único para capturar la esencia de un animal en una sola palabra. Tu estilo es moderno, cool, y evita los clichés a toda costa.

        # Tarea
        A partir de la descripción de la mascota que te proporciono en el #Contexto, tu misión es generar una lista de 5 nombres que cumplan con todos los requerimientos.

        # Requerimientos
        1.  **Originalidad Máxima:** Evita a toda costa nombres comunes como "Luna", "Max", "Bella", "Simba", "Lola".
        2.  **Estilo "Cool":** Los nombres deben sonar interesantes, modernos y tener carácter. Pueden ser de mitología, ciencia ficción, literatura, o simplemente palabras que suenen bien.
        3.  **Breve Justificación:** Al lado de cada nombre, entre paréntesis, añade una brevísima explicación de una línea sobre por qué ese nombre es genial para esa mascota.
        4.  **Formato Estricto:** La salida debe ser una lista numerada del 1 al 5. No incluyas introducciones, saludos ni despedidas. Solo la lista.
        5.  **Idioma:** Utiliza un español universalmente entendible pero con un toque moderno, similar al que se usaría en Argentina para algo "con onda".

        # Contexto
        La mascota a nombrar es la siguiente:
        {animal_description}

        # Ejemplo de Salida Perfecta
        (Si el contexto fuera "gatita negra, muy sigilosa y elegante")

        1.  Umbra (Significa "sombra" en latín, perfecto para su color y sigilo).
        2.  Nyx (La diosa griega de la noche, poderoso y místico).
        3.  Vesper (Relacionado con el atardecer, suena sofisticado y misterioso).
        4.  Morwen (Un nombre de la literatura de Tolkien, suena fuerte y elegante).
        5.  Pixel (Un toque geek y moderno para una gata pequeña y precisa).
        """
        
        prompt_template = PromptTemplate(
            template=template_string,
            input_variables=["animal_description"]
        )
        
        # 3. Definimos el Parser de Salida
        # En este caso, solo queremos asegurarnos de que la salida sea un string.
        output_parser = StrOutputParser()
        
        # 4. 🔥 CONSTRUIMOS LA CADENA USANDO LCEL 🔥
        # Esta es la "magia". Unimos los componentes con el operador pipe.
        # El flujo de datos es: Diccionario de entrada -> Prompt -> LLM -> Parser de Salida
        self._chain = prompt_template | llm | output_parser

    # def _parse_and_display(self, text_response: str):
    #     """
    #     Método privado para parsear la respuesta del LLM y mostrarla con colores.
    #     Esto separa la presentación de la lógica de generación.
    #     Parsea la respuesta del LLM y la devuelve como una estructura de datos.
    #     """
    # ¡ESTE MÉTODO ES NUEVO! Devuelve una lista de diccionarios.
    def _parse_response(self, text_response: str) -> list[dict]:
        """
        Parsea la respuesta del LLM y la devuelve como una estructura de datos.
        Este método es más robusto y no depende de una regex compleja.
        """
        # Expresión regular para capturar el número, el nombre y la justificación
        # Busca el patrón: "1. Nombre (justificación)"
        parsed_names = []
        # pattern = re.compile(r"^\s*(\d+)\.\s+(.+?)\s+\((.*)\)", re.MULTILINE)
        # matches = pattern.findall(text_response)
        # Dividimos la respuesta completa en líneas individuales
        lines = text_response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # Nos aseguramos de que la línea parezca una línea de nombre (empieza con un número y un punto)
            if line and line[0].isdigit() and '.' in line:
                try:
                    # Dividimos por el primer paréntesis que encontremos
                    parts = line.split('(', 1)
                    name_part = parts[0]
                    justification_part = parts[1]

                    # Limpiamos el nombre (quitamos número, punto, asteriscos y espacios)
                    name = name_part.split('.', 1)[1].strip().replace('*', '')
                    
                    # Limpiamos la justificación (quitamos el paréntesis final)
                    justification = justification_part.rstrip(')').strip()

                    parsed_names.append({
                        "name": name,
                        "justification": justification
                    })
                except IndexError:
                    # Si una línea no tiene el formato esperado, la ignoramos para no romper la app
                    continue
        
        if not parsed_names:
             return [{"error": "No se pudo extraer ningún nombre del formato esperado.", "raw": text_response}]

        return parsed_names

        # if not matches:
             # Si el parseo falla, simplemente imprime la respuesta sin formato
            # print(f"{Colors.WARNING}No se pudo parsear la respuesta, mostrando en bruto:{Colors.ENDC}")
            # print(text_response)
            # return
            # Si falla, devolvemos un diccionario de error para mostrar en la UI
            # return [{"error": "No se pudo parsear la respuesta del modelo.", "raw": text_response}]

        # for match in matches:
            # number, name, justification = match
            # name = name.strip().replace('*', '') # Limpiamos el nombre por si acaso
            # print(
            #     f"{Colors.HEADER}{number}.{Colors.ENDC} "
            #     f"{Colors.BOLD}{Colors.CYAN}{name}{Colors.ENDC} "
            #     f"({Colors.GREEN}{justification}{Colors.ENDC})"
            # )
            # name, justification = match[1], match[2]
            # parsed_names.append({
            #     "name": name.strip().replace('*', ''),
            #     "justification": justification.strip()
            # })
            # return parsed_names

    # def generate_and_show(self, animal_description: str):
    #     """
    #     Método público que orquesta todo el proceso.
    #     Este método ahora es mucho más simple. Solo invoca la cadena.
    #     """
    #     print(
    #         f"\n{Colors.BLUE}Buscando nombres PRO para:{Colors.ENDC} "
    #         f"{Colors.BOLD}{animal_description}{Colors.ENDC}"
    #     )
    #     # Usamos un bucle de stream para dar feedback inmediato de que está funcionando
    #     print(f"{Colors.WARNING}Pensando...{Colors.ENDC}", end="", flush=True)
        
    #     # final_prompt = self.prompt_template.format(animal_description=animal_description)
        
    #     # --- Invocamos la cadena usando .stream() ---
    #     # La cadena se encarga de todo el trabajo pesado por nosotros.
    #     full_response = ""
    #     # .stream() ahora funciona en toda la cadena. La entrada es un diccionario.
    #     for chunk in self._chain.stream({"animal_description": animal_description}):
    #         print(f"{Colors.WARNING}.{Colors.ENDC}", end="", flush=True)
    #         full_response += chunk
        
    #     # response_content = ""
    #     # for chunk in self.llm.stream(final_prompt):
    #     #     print(f"{Colors.WARNING}.{Colors.ENDC}", end="", flush=True)
    #     #     response_content += chunk.content
        
    #     print("\n") # Salto de línea después de los puntos de "Pensando..."
    #     self._parse_and_display(full_response)
    #     # Llamamos a nuestro método de presentación
    #     # self._parse_and_display(response_content)
    
    def generate(self, animal_description: str) -> list[dict]:
        """
        Método público principal. Invoca la cadena y devuelve los nombres parseados.
        """
        # .invoke() es mejor para una única respuesta que no necesitamos mostrar en tiempo real.
        response_content = self._chain.invoke({"animal_description": animal_description})
        # Llama al nuevo método de parseo y devuelve el resultado
        return self._parse_response(response_content)


# --- Punto de Entrada del Script ---
# if __name__ == "__main__":
    # Creamos la instancia de nuestra clase
    # name_generator = PetNameGenerator()

    # La usamos
    # descripcion_gata = "Gatita hembra, de color blanco y negro, muy juguetona y un poco cariñosa."
    # name_generator.generate_and_show(descripcion_gata)

    # descripcion_perro = "Cachorro de Golden Retriever, muy leal y parece que siempre está sonriendo."
    # name_generator.generate_and_show(descripcion_perro)