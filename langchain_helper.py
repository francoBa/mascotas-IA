# --- Módulos estándar de Python ---
import os
import sys
import re
import tempfile
from dotenv import load_dotenv

# --- Librerías de Terceros (opcional, podrías tenerlas en la UI) ---
from youtube_transcript_api import YouTubeTranscriptApi

# --- Componentes Principales de LangChain ---
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.agents import create_react_agent, AgentExecutor, Tool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import LLMMathChain
from langchain import hub

# --- Componentes del Ecosistema de LangChain (Integraciones) ---
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import YoutubeLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# --- Componentes del "Core" de LangChain (Abstracciones Fundamentales) ---
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

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

    # ¡ESTE MÉTODO ES NUEVO! Devuelve una lista de diccionarios.
    def _parse_response(self, text_response: str) -> list[dict]:
        """
        Parsea la respuesta del LLM y la devuelve como una estructura de datos.
        Este método es más robusto y no depende de una regex compleja.
        """
        parsed_names = []
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
    
    def generate(self, animal_description: str) -> list[dict]:
        """
        Método público principal. Invoca la cadena y devuelve los nombres parseados.
        """
        # .invoke() es mejor para una única respuesta que no necesitamos mostrar en tiempo real.
        response_content = self._chain.invoke({"animal_description": animal_description})
        # Llama al nuevo método de parseo y devuelve el resultado
        return self._parse_response(response_content)
    
    # --- NUEVO MÉTODO PARA EL AGENTE ---
    def create_agent_executor(self, temperature=0.5):
        """
        Crea y devuelve un AgentExecutor listo para ser usado.
        Esta es la nueva forma de construir agentes en LangChain.
        """
        # 1. Definir el LLM para el agente (podemos usar una temperatura diferente)
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=temperature)

        # --- CONSTRUCCIÓN MANUAL DE HERRAMIENTAS (LA MEJOR PRÁCTICA) ---
        # 1. Herramienta de Wikipedia
        # Se necesita un "wrapper" de la API y luego se pasa a la herramienta.
        api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=2000)
        wikipedia_tool = WikipediaQueryRun(
            name="wikipedia",
            description="Una herramienta para buscar información en Wikipedia sobre personas, lugares, eventos, etc.",
            api_wrapper=api_wrapper
        )
        
        # 2. Herramienta de Matemáticas
        # Se crea la cadena de matemáticas y se envuelve en un "Tool".
        math_chain = LLMMathChain.from_llm(llm)
        math_tool = Tool(
            name="Calculator",
            description="Una calculadora útil para problemas matemáticos y de aritmética.",
            func=math_chain.run
        )

        # 3. Lista de herramientas
        tools = [wikipedia_tool, math_tool]
        
        # 2. Cargar las herramientas. Esto sigue siendo igual.
        # Wikipedia para buscar información y llm-math para cálculos.
        # tools = load_tools(["wikipedia", "llm-math"], llm=llm)

        # 3. Obtener el prompt del Hub de LangChain.
        # Este prompt está específicamente diseñado para enseñar a los modelos a usar la lógica ReAct.
        # Es el reemplazo moderno de "AgentType.ZERO_SHOT_REACT_DESCRIPTION".
        # prompt = hub.pull("hwchase17/react")
        
        # --- AQUÍ VIENE LA MAGIA: NUESTRO PROMPT EN ESPAÑOL ---
        # 3.1. Definimos la plantilla del prompt en un string.
        #    Hemos traducido y adaptado el prompt ReAct original.
        template_en_espanol = """
Responde a la siguiente pregunta de la mejor manera posible. Tienes acceso a las siguientes herramientas:

{tools}

Utiliza el siguiente formato:

Pregunta: la pregunta original que debes responder
Pensamiento: siempre debes pensar qué hacer a continuación
Acción: la acción a tomar, debe ser una de [{tool_names}]
Entrada de la Acción: la entrada para la acción
Observación: el resultado de la acción
... (este patrón de Pensamiento/Acción/Entrada de la Acción/Observación puede repetirse N veces)
Pensamiento: Ahora sé la respuesta final.
Final Answer: la respuesta final y definitiva a la pregunta original en español  <-- ¡SOLUCIÓN!

Comienza el proceso.

Pregunta: {input}
Pensamiento:{agent_scratchpad}
"""
        # 3.2. Creamos el objeto PromptTemplate a partir de nuestro string.
        prompt = PromptTemplate.from_template(template_en_espanol)

        # 4. Crear el Agente.
        # Se unen el LLM, las herramientas y el prompt. El agente decide QUÉ hacer.
        agent = create_react_agent(llm, tools, prompt)

        # 5. Crear el Ejecutor del Agente.
        # Este es el motor que realmente ejecuta los pasos del agente en un bucle.
        # handle_parsing_errors=True lo hace más robusto.
        agent_executor = AgentExecutor(
            agent=agent, 
            tools=tools, 
            verbose=True, 
            handle_parsing_errors=True
        )
        
        return agent_executor


# --- NUEVA CLASE PARA ASISTENTE DE DOCUMENTOS (RAG) ---
class DocumentAssistant:
    def __init__(self):
        """
        Inicializa el asistente con el modelo de embeddings de Google.
        """
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
        
    # --- NUEVA FUNCIÓN DE AYUDA DENTRO DE LA CLASE ---
    def _get_video_id_from_url(self, url: str) -> str | None:
        """Extrae el ID del video de una URL de YouTube."""
        # Patrón para URLs de youtube.com/watch?v=...
        match = re.search(r"v=([a-zA-Z0-9_-]{11})", url)
        if match:
            return match.group(1)
        # Patrón para URLs cortas de youtu.be/...
        match = re.search(r"youtu\.be/([a-zA-Z0-9_-]{11})", url)
        if match:
            return match.group(1)
        return None

    def create_vector_db(self, source, source_type: str):
        """
        Crea una base de datos de vectores a partir de una fuente (URL de YouTube o archivo PDF).
        
        Args:
            source: La URL del video o el objeto de archivo subido desde Streamlit.
            source_type: 'youtube' o 'pdf'.
        
        Returns:
            El objeto de base de datos de vectores FAISS.
        """
        docs = [] # Inicializamos una lista vacía para los documentos

        if source_type == 'youtube':
            video_id = self._get_video_id_from_url(source)
            if not video_id:
                raise ValueError("La URL de YouTube no es válida o no tiene el formato esperado.")
            
            try:
                # Usamos la librería directamente, que es más fiable
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['es', 'en'])
                
                # Unimos todos los trozos de texto en un solo string
                transcript_text = " ".join([d['text'] for d in transcript_list])
                
                # Creamos un único objeto Document de LangChain con la transcripción
                docs = [Document(page_content=transcript_text, metadata={"source": video_id})]

            except Exception as e:
                # Si falla (ej. no hay transcripción), lanzamos un error claro
                raise Exception(f"No se pudo obtener la transcripción del video. Causa: {e}")

        elif source_type == 'pdf':
            # El código para PDF no cambia
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(source.getvalue())
                tmp_file_path = tmp_file.name
            
            loader = PyPDFLoader(tmp_file_path)
            docs = loader.load_and_split()
            os.remove(tmp_file_path)
        
        else:
            raise ValueError("Tipo de fuente no soportado.")
        
        if not docs:
            raise ValueError("No se pudo cargar ningún contenido del documento o video.")

        # El resto del proceso (splitter, FAISS) es idéntico y funcionará con la lista 'docs'
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(docs)
        
        db = FAISS.from_documents(chunks, self.embeddings)
        return db

    def create_rag_chain(self, vector_store):
        """
        Crea y devuelve una cadena RAG usando LCEL.
        """
        # El retriever busca documentos similares en la base de datos de vectores
        retriever = vector_store.as_retriever()

        # Plantilla del prompt para guiar al LLM
        template = """
        Eres un asistente experto en responder preguntas.
        Utiliza únicamente el siguiente contexto para responder la pregunta del usuario.
        Si la respuesta no se encuentra en el contexto, di amablemente que no tienes esa información.
        
        Contexto:
        {context}
        
        Pregunta:
        {question}
        
        Respuesta:
        """
        prompt = ChatPromptTemplate.from_template(template)

        # Construcción de la cadena LCEL
        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return rag_chain



# --- Punto de Entrada del Script ---
# if __name__ == "__main__":
    # Creamos la instancia de nuestra clase
    # name_generator = PetNameGenerator()

    # La usamos
    # descripcion_gata = "Gatita hembra, de color blanco y negro, muy juguetona y un poco cariñosa."
    # name_generator.generate_and_show(descripcion_gata)

    # descripcion_perro = "Cachorro de Golden Retriever, muy leal y parece que siempre está sonriendo."
    # name_generator.generate_and_show(descripcion_perro)