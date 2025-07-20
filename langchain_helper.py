import os
import sys
import re
import random
from datetime import datetime
import tempfile
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
# Prompts y Documentos
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.documents import Document
# Componentes de Cadenas y Agentes
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain, LLMMathChain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.agents import create_react_agent, AgentExecutor, Tool
from langchain.retrievers.multi_query import MultiQueryRetriever
# Integraciones (Google, Community)
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
# Componentes de LCEL Core
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda


# --- Clase para los Colores ANSI ---
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
        # Usamos una temperatura aleatoria en un rango creativo
        random_temperature = random.uniform(0.7, 1.0)
        # algunas variables que sólo las usamos de manera temporal las delcaramos como locales (sin self.)
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=random_temperature,
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
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=temperature)

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

        # 4. Lista de herramientas
        tools = [wikipedia_tool, math_tool]
        
        # --- AQUÍ VIENE LA MAGIA: NUESTRO PROMPT EN ESPAÑOL ---
        # 5. Definimos la plantilla del prompt en un string.
        #    Hemos traducido y adaptado el prompt ReAct original.
        template_en_espanol = """
Responde a la siguiente pregunta de la mejor manera posible. Tienes acceso a las siguientes herramientas:

{tools}

**Información Adicional Importante:**
*   **La fecha y hora actual es: {current_time}**

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
        # 5.2. Creamos el objeto PromptTemplate a partir de nuestro string.
        prompt = PromptTemplate.from_template(template_en_espanol)

        # 6. Crear el Agente.
        # Se unen el LLM, las herramientas y el prompt. El agente decide QUÉ hacer.
        agent = create_react_agent(llm, tools, prompt)

        # 7. Crear el Ejecutor del Agente.
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
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
        
    def _get_youtube_id_robust(self, url: str) -> str | None:
        patterns = [
            r"watch\?v=([a-zA-Z0-9_-]{11})",
            r"live/([a-zA-Z0-9_-]{11})",
            r"youtu\.be/([a-zA-Z0-9_-]{11})",
            r"embed/([a-zA-Z0-9_-]{11})"
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def create_vector_db(self, source, source_type: str, streamlit_progress_bar=None):
        # --- PASO 1: Cargar los documentos en una lista 'docs' ---
        docs = []
        if source_type == 'youtube':
            video_id = self._get_youtube_id_robust(source)
            if not video_id:
                raise ValueError("La URL de YouTube no es válida o no tiene el formato esperado.")
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['es', 'en', 'en-US'])
                transcript_text = " ".join([d['text'] for d in transcript_list])
                docs = [Document(page_content=transcript_text, metadata={"source": video_id})]
            except Exception as e:
                raise ValueError(f"No se pudo obtener la transcripción del video '{video_id}'. Causa: {e}")

        elif source_type == 'pdf':
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(source.getvalue())
                tmp_file_path = tmp_file.name
            
            loader = PyPDFLoader(tmp_file_path)
            docs = loader.load_and_split()
            os.remove(tmp_file_path)
        
        if not docs:
            raise ValueError("No se pudo cargar ningún contenido del documento o video.")

        # --- PASO 2: Dividir los documentos en chunks ---
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        chunks = text_splitter.split_documents(docs)
        
        if not chunks:
            raise ValueError("El documento no pudo ser dividido en fragmentos de texto procesables.")

        num_chunks = len(chunks)
        print(f"Creando embeddings para {num_chunks} chunks...")

        # --- PASO 3: Crear el índice FAISS de forma incremental (funciona para ambos) ---
        batch_size = 100
        db = None
        
        try:
            for i in range(0, num_chunks, batch_size):
                batch = chunks[i:i + batch_size]
                
                if not batch:
                    continue

                if db is None:
                    # Si es el primer lote, creamos la base de datos
                    db = FAISS.from_documents(batch, self.embeddings)
                else:
                    # Para los lotes siguientes, los añadimos al índice existente
                    db.add_documents(batch)

                # Actualizamos la barra de progreso de Streamlit
                if streamlit_progress_bar:
                    progress = min(float((i + len(batch)) / num_chunks), 1.0)
                    streamlit_progress_bar.progress(progress, text=f"Procesando fragmento {i + len(batch)}/{num_chunks}...")

            if db is None:
                 raise ValueError("No se pudieron crear los embeddings para ningún fragmento.")

            return db
        
        except Exception as e:
            # Capturamos cualquier error durante el embedding y lo reenviamos
            raise Exception(f"Error durante la creación de embeddings: {e}")
        # 1. Cargar Documentos
        # if source_type == 'youtube':
        #     video_id = self._get_youtube_id_robust(source)
        #     if not video_id:
        #         raise ValueError("La URL de YouTube no es válida.")
        #     try:
        #         transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['es', 'en', 'en-US'])
        #         transcript_text = " ".join([d['text'] for d in transcript_list])
        #         docs = [Document(page_content=transcript_text, metadata={"source": video_id})]
        #     except Exception as e:
        #         raise ValueError(f"No se pudo obtener la transcripción del video '{video_id}'. Causa: {e}")
        # elif source_type == 'pdf':
        #     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        #         tmp_file.write(source.getvalue())
        #         tmp_file_path = tmp_file.name
        #     loader = PyPDFLoader(tmp_file_path)
        #     docs = loader.load_and_split()
        #     os.remove(tmp_file_path)
        # else:
        #     raise ValueError("Tipo de fuente no soportado.")
        
        # if not docs:
        #     raise ValueError("No se pudo cargar contenido del documento.")

        # # 2. Dividir en Chunks
        # text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        # chunks = text_splitter.split_documents(docs)
        
        # if not chunks:
        #     raise ValueError("El documento no pudo ser dividido en fragmentos de texto procesables.")

        # num_chunks = len(chunks)
        # print(f"Creando embeddings para {num_chunks} chunks...")

        # # 3. Crear el índice FAISS de forma incremental y robusta
        # batch_size = 100
        
        # try:
        #     # Creamos el índice con el PRIMER lote de chunks
        #     first_batch = chunks[:batch_size]
        #     db = FAISS.from_documents(first_batch, self.embeddings)
            
        #     # Actualizamos la UI
        #     if streamlit_progress_bar:
        #         progress = min(float(len(first_batch) / num_chunks), 1.0)
        #         streamlit_progress_bar.progress(progress, text=f"Procesando fragmento {len(first_batch)}/{num_chunks}...")

        #     # 4. Iteramos sobre los LOTES RESTANTES y los añadimos al índice
        #     for i in range(batch_size, num_chunks, batch_size):
        #         next_batch = chunks[i:i + batch_size]
        #         if next_batch: # Nos aseguramos de que el lote no esté vacío
        #             db.add_documents(next_batch)

        #             # Actualizamos la UI
        #             if streamlit_progress_bar:
        #                 progress = min(float((i + len(next_batch)) / num_chunks), 1.0)
        #                 streamlit_progress_bar.progress(progress, text=f"Procesando fragmento {i + len(next_batch)}/{num_chunks}...")
            
        #     return db
        
        # except Exception as e:
        #     # Capturamos cualquier error durante el embedding y lo reenviamos
        #     # Esto permitirá que el manejo de errores de la UI lo muestre correctamente
        #     raise Exception(f"Error durante la creación de embeddings: {e}")

    def create_rag_chain(self, vector_store, use_advanced_retriever: bool, chain_type: str):
        # 1. SELECCIÓN DEL RETRIEVER
        k_value = 7
        if chain_type in ['map_reduce', 'refine']:
            k_value = 4 if use_advanced_retriever else 5
        
        base_retriever = vector_store.as_retriever(search_kwargs={"k": k_value})
        
        if use_advanced_retriever:
            query_prompt = PromptTemplate.from_template(
                "Eres un asistente de IA. Genera 3 versiones diferentes de la pregunta del usuario para recuperar documentos relevantes.\nPregunta Original: {question}"
            )
            retriever = MultiQueryRetriever.from_llm(
                retriever=base_retriever, llm=self.llm, prompt=query_prompt
            )
        else:
            retriever = base_retriever

        # 2. SELECCIÓN DE LA ESTRATEGIA DE CADENA
        if chain_type == 'stuff':
            # --- ESTRATEGIA "STUFF" (Correcta y sin cambios) ---
            prompt = ChatPromptTemplate.from_messages([
                ("system", "Eres un asistente servicial. Responde la pregunta del usuario basándote en el contexto proporcionado. Responde siempre en español."),
                ("human", "Contexto:\n{context}\n\nPregunta: {input}")
            ])
            document_chain = create_stuff_documents_chain(self.llm, prompt)
            return create_retrieval_chain(retriever, document_chain)
        
        # 3. --- ESTRATEGIAS AVANZADAS CON LCEL PURO ---
        # MAP CHAIN: Esta cadena se aplicará a cada documento recuperado.
        map_prompt = ChatPromptTemplate.from_template(
            "A continuación se muestra un fragmento de texto. Resume su contenido principal en español en relación a esta pregunta:\n"
            "Pregunta: {question}\n"
            "Fragmento: {context}"
        )
        map_chain = map_prompt | self.llm | StrOutputParser()

        if chain_type == 'map_reduce':
            # REDUCE CHAIN: Toma todos los resúmenes y crea la respuesta final.
            reduce_prompt = ChatPromptTemplate.from_template(
                "A continuación se muestran varios resúmenes de un documento. Sintetízalos en una respuesta final y coherente a la pregunta del usuario. Responde siempre en español.\n"
                "Pregunta Original: {question}\n"
                "Resúmenes:\n{summaries}\n\nRespuesta final y completa:"
            )
            reduce_chain = reduce_prompt | self.llm | StrOutputParser()
            
            def combine_summaries(summaries: list) -> str:
                return "\n\n".join(summary for summary in summaries if summary)
            
            # Flujo completo de Map-Reduce
            def map_reduce_flow(input_dict: dict):
                query = input_dict["input"]
                docs = retriever.invoke(query)
                map_inputs = [{"context": doc.page_content, "question": query} for doc in docs]
                summaries = map_chain.batch(map_inputs)
                combined_summaries = combine_summaries(summaries)
                final_answer = reduce_chain.invoke({"summaries": combined_summaries, "question": query})
                return {"answer": final_answer}
            
            return RunnableLambda(map_reduce_flow)
        
        elif chain_type == 'refine':
            # REFINE CHAIN: Es una cadena secuencial.
            def refine_flow(input_dict: dict):
                query = input_dict["input"]
                docs = retriever.invoke(query)
                if not docs:
                    return {"answer": "No se encontró información relevante en el documento para responder a esa pregunta."}

                # Primera respuesta con el primer documento
                initial_response = map_chain.invoke({"context": docs[0].page_content, "question": query})
                
                # Itera sobre el resto de los documentos para refinar
                for doc in docs[1:]:
                    refine_prompt = ChatPromptTemplate.from_template(
                        "Eres un asistente de IA. Tienes una respuesta existente y un nuevo contexto. "
                        "Mejora la respuesta existente con el nuevo contexto. Responde siempre en español.\n"
                        "Pregunta: {question}\n"
                        "Respuesta Existente: {existing_answer}\n"
                        "Nuevo Contexto: {context}\n"
                        "Respuesta Refinada:"
                    )
                    refine_chain = refine_prompt | self.llm | StrOutputParser()
                    initial_response = refine_chain.invoke({
                        "question": query,
                        "existing_answer": initial_response,
                        "context": doc.page_content
                    })
                return {"answer": initial_response}
            
            return RunnableLambda(refine_flow)


# --- Punto de Entrada del Script ---
# if __name__ == "__main__":
    # Creamos la instancia de nuestra clase
    # name_generator = PetNameGenerator()
    # La usamos
    # descripcion_gata = "Gatita hembra, de color blanco y negro, muy juguetona y un poco cariñosa."
    # name_generator.generate_and_show(descripcion_gata)
    # descripcion_perro = "Cachorro de Golden Retriever, muy leal y parece que siempre está sonriendo."
    # name_generator.generate_and_show(descripcion_perro)