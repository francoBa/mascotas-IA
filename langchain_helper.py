import os
import sys
import re
import random
<<<<<<< HEAD
from datetime import datetime
import tempfile
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
# Prompts y Documentos
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.documents import Document
=======
import tempfile
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound

# Prompts y Documentos
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.documents import Document

>>>>>>> fix-youtube-processing
# Componentes de Cadenas y Agentes
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain, LLMMathChain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.agents import create_react_agent, AgentExecutor, Tool
from langchain.retrievers.multi_query import MultiQueryRetriever
<<<<<<< HEAD
=======

>>>>>>> fix-youtube-processing
# Integraciones (Google, Community)
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
<<<<<<< HEAD
# Componentes de LCEL Core
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
=======

# Componentes de LCEL Core
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
>>>>>>> fix-youtube-processing


# --- Clase para los Colores ANSI ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


<<<<<<< HEAD
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
=======
# --- Clase para el Generador de Nombres y Agente ---
class PetNameGenerator:
    def __init__(self, temperature=0.8, top_p=0.9, top_k=40):
        load_dotenv()
        random_temperature = random.uniform(0.7, 1.0)
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
>>>>>>> fix-youtube-processing
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
        2.  **Estilo "Cool":** Los nombres deben sonar interesantes, modernos y tener carácter.
        3.  **Breve Justificación:** Al lado de cada nombre, entre paréntesis, añade una brevísima explicación.
        4.  **Formato Estricto:** La salida debe ser una lista numerada del 1 al 5. Solo la lista.
        5.  **Idioma:** Utiliza un español universalmente entendible pero con un toque moderno.
        # Contexto
        La mascota a nombrar es la siguiente: {animal_description}
        """
        prompt_template = PromptTemplate(template=template_string, input_variables=["animal_description"])
        output_parser = StrOutputParser()
        self._chain = prompt_template | llm | output_parser

    def _parse_response(self, text_response: str) -> list[dict]:
        parsed_names = []
        lines = text_response.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and line[0].isdigit() and '.' in line:
                try:
                    parts = line.split('(', 1)
                    name_part = parts[0]
                    justification_part = parts[1]
                    name = name_part.split('.', 1)[1].strip().replace('*', '')
                    justification = justification_part.rstrip(')').strip()
                    parsed_names.append({"name": name, "justification": justification})
                except IndexError:
                    continue
        if not parsed_names:
             return [{"error": "No se pudo extraer ningún nombre del formato esperado.", "raw": text_response}]
        return parsed_names
    
    def generate(self, animal_description: str) -> list[dict]:
        response_content = self._chain.invoke({"animal_description": animal_description})
        return self._parse_response(response_content)
    
    def create_agent_executor(self, temperature=0.5):
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=temperature)
        api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=2000)
        wikipedia_tool = WikipediaQueryRun(name="wikipedia", description="Una herramienta para buscar información en Wikipedia.", api_wrapper=api_wrapper)
        math_chain = LLMMathChain.from_llm(llm)
        math_tool = Tool(name="Calculator", description="Una calculadora útil para problemas matemáticos.", func=math_chain.run)
        tools = [wikipedia_tool, math_tool]
        template_en_espanol = """
        Responde a la siguiente pregunta de la mejor manera posible. Tienes acceso a las siguientes herramientas:
        {tools}
        **Información Adicional Importante:** La fecha y hora actual es: {current_time}
        Utiliza el siguiente formato:
        Pregunta: la pregunta original que debes responder
        Pensamiento: siempre debes pensar qué hacer a continuación
        Acción: la acción a tomar, debe ser una de [{tool_names}]
        Entrada de la Acción: la entrada para la acción
        Observación: el resultado de la acción
        ... (este patrón de Pensamiento/Acción/Entrada de la Acción/Observación puede repetirse N veces)
        Pensamiento: Ahora sé la respuesta final.
        Final Answer: la respuesta final y definitiva a la pregunta original en español.
        Comienza el proceso.
        Pregunta: {input}
        Pensamiento:{agent_scratchpad}
        """
        prompt = PromptTemplate.from_template(template_en_espanol)
        agent = create_react_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
        return agent_executor


# --- Clase para el Asistente de Documentos (RAG) ---
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
        chunks = []

        if source_type == 'youtube':
            video_id = self._get_youtube_id_robust(source)
            if not video_id:
                raise ValueError("La URL de YouTube no es válida o no tiene un formato reconocido.")
            
            try:
                # --- LÓGICA CORREGIDA Y SIMPLIFICADA ---
                # Intentamos obtener la transcripción directamente en los idiomas preferidos.
                # get_transcript ya devuelve la lista de diccionarios que necesitamos.
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['es', 'en'])
                
                transcript_text = " ".join([d['text'] for d in transcript_data])
                docs = [Document(page_content=transcript_text, metadata={"source": video_id})]
                
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
                chunks = text_splitter.split_documents(docs)

            except NoTranscriptFound:
                # Si no encuentra en es/en, buscamos CUALQUIER transcripción disponible.
                try:
                    print("No se encontró transcripción en es/en. Buscando cualquier idioma disponible...")
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    if not transcript_list:
                        raise ValueError("Este video no tiene ninguna transcripción disponible.")
                    
                    # Tomamos la primera que encontremos y la procesamos
                    transcript = next(iter(transcript_list))
                    transcript_data = transcript.fetch()
                    transcript_text = " ".join([d['text'] for d in transcript_data])
                    docs = [Document(page_content=transcript_text, metadata={"source": video_id})]
                    
                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
                    chunks = text_splitter.split_documents(docs)
                except Exception as e:
                    raise ValueError(f"No se pudo procesar ninguna transcripción del video. Error: {e}")
            except Exception as e:
                raise ValueError(f"Ocurrió un error inesperado al obtener la transcripción. Error: {e}")

        elif source_type == 'pdf':
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(source.getvalue())
                tmp_file_path = tmp_file.name
            try:
                loader = PyPDFLoader(tmp_file_path)
                chunks = loader.load_and_split()
            finally:
                os.remove(tmp_file_path)
        
        if not chunks:
            raise ValueError("El documento no pudo ser dividido en fragmentos de texto procesables.")

        num_chunks = len(chunks)
        print(f"Creando embeddings para {num_chunks} chunks...")
        batch_size = 100
        db = None
        
        try:
            for i in range(0, num_chunks, batch_size):
                batch = chunks[i:i + batch_size]
                if not batch: continue
                if db is None:
                    db = FAISS.from_documents(batch, self.embeddings)
                else:
                    db.add_documents(batch)
                if streamlit_progress_bar:
                    progress = min(float((i + len(batch)) / num_chunks), 1.0)
                    streamlit_progress_bar.progress(progress, text=f"Procesando fragmento {i + len(batch)}/{num_chunks}...")
            if db is None:
                 raise ValueError("No se pudieron crear los embeddings para ningún fragmento.")
            return db
        except Exception as e:
            raise Exception(f"Error durante la creación de embeddings: {e}")

    def create_rag_chain(self, vector_store, use_advanced_retriever: bool, chain_type: str):
        k_value = 7 if chain_type == 'stuff' else 4
        base_retriever = vector_store.as_retriever(search_kwargs={"k": k_value})
        
        if use_advanced_retriever:
            query_prompt = PromptTemplate.from_template("Genera 3 versiones diferentes de la pregunta del usuario para recuperar documentos relevantes.\nPregunta Original: {question}")
            retriever = MultiQueryRetriever.from_llm(retriever=base_retriever, llm=self.llm, prompt=query_prompt)
        else:
            retriever = base_retriever

        if chain_type == 'stuff':
            prompt = ChatPromptTemplate.from_messages([
                ("system", "Eres un asistente servicial. Responde la pregunta del usuario basándote en el contexto proporcionado. Responde siempre en español."),
                ("human", "Contexto:\n{context}\n\nPregunta: {input}")
            ])
            document_chain = create_stuff_documents_chain(self.llm, prompt)
            return create_retrieval_chain(retriever, document_chain)
        
        map_prompt = ChatPromptTemplate.from_template("Resume el siguiente fragmento en español en relación a esta pregunta:\nPregunta: {question}\nFragmento: {context}")
        map_chain = map_prompt | self.llm | StrOutputParser()

        if chain_type == 'map_reduce':
            reduce_prompt = ChatPromptTemplate.from_template("Sintetiza los siguientes resúmenes en una respuesta final y coherente a la pregunta del usuario. Responde siempre en español.\nPregunta Original: {question}\nResúmenes:\n{summaries}\n\nRespuesta final:")
            reduce_chain = reduce_prompt | self.llm | StrOutputParser()
            def combine_summaries(summaries: list) -> str:
                return "\n\n".join(summary for summary in summaries if summary)
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
            def refine_flow(input_dict: dict):
                query = input_dict["input"]
                docs = retriever.invoke(query)
                if not docs:
                    return {"answer": "No se encontró información relevante para responder."}
                initial_response = map_chain.invoke({"context": docs[0].page_content, "question": query})
                for doc in docs[1:]:
                    refine_prompt = ChatPromptTemplate.from_template("Tienes una respuesta existente. Mejórala con el nuevo contexto. Responde siempre en español.\nPregunta: {question}\nRespuesta Existente: {existing_answer}\nNuevo Contexto: {context}\nRespuesta Refinada:")
                    refine_chain = refine_prompt | self.llm | StrOutputParser()
                    initial_response = refine_chain.invoke({"question": query, "existing_answer": initial_response, "context": doc.page_content})
                return {"answer": initial_response}
            return RunnableLambda(refine_flow)
