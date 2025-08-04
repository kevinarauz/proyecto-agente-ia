import os
import json
import requests
import time
import io
import logging
import re
import traceback
from typing import Optional, Union, Tuple
from flask import Flask, render_template, request, jsonify, Response
from dotenv import load_dotenv

# Importar ChatOllama de la nueva ubicación (si está disponible), sino usar la anterior
try:
    from langchain_ollama import ChatOllama
    print("✅ Usando langchain_ollama (versión actualizada)")
except ImportError:
    from langchain_community.chat_models import ChatOllama
    print("⚠️ Usando langchain_community.chat_models (versión deprecada)")

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from langchain.tools import BaseTool
from langchain_core.tools import Tool
from config import Config

# Definir ChatLMStudio directamente aquí para evitar problemas de importación
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.callbacks import CallbackManagerForLLMRun
from typing import Any, List, Optional
from pydantic import Field
import requests

class ChatLMStudio(BaseChatModel):
    """Chat model wrapper for LM Studio API."""
    
    # Declarar explícitamente los campos que necesitamos
    model: str = Field(description="Nombre del modelo a usar")
    base_url: str = Field(default="http://localhost:1234", description="URL base del servidor LM Studio")
    temperature: float = Field(default=0.7, description="Temperatura para generación")
    max_tokens: int = Field(default=1000, description="Máximo número de tokens")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._last_response = None  # Para almacenar la última respuesta con reasoning_content
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate chat completion."""
        # Convert messages to API format
        api_messages = []
        
        # Combinar mensajes del sistema con el primer mensaje del usuario
        system_content = ""
        user_messages = []
        
        for msg in messages:
            if isinstance(msg, SystemMessage):
                # Acumular contenido del sistema, asegurándonos de que sea string
                content = msg.content if isinstance(msg.content, str) else str(msg.content)
                system_content += content + "\n\n"
            elif isinstance(msg, HumanMessage):
                user_messages.append(msg)
            elif isinstance(msg, AIMessage):
                content = msg.content if isinstance(msg.content, str) else str(msg.content)
                api_messages.append({"role": "assistant", "content": content})
        
        # Si hay contenido del sistema, combinarlo con el primer mensaje del usuario
        if system_content and user_messages:
            first_user_msg = user_messages[0]
            first_content = first_user_msg.content if isinstance(first_user_msg.content, str) else str(first_user_msg.content)
            combined_content = f"{system_content.strip()}\n\nUsuario: {first_content}"
            api_messages.insert(0, {"role": "user", "content": combined_content})
            
            # Agregar los mensajes restantes del usuario
            for msg in user_messages[1:]:
                user_content = msg.content if isinstance(msg.content, str) else str(msg.content)
                api_messages.append({"role": "user", "content": user_content})
        else:
            # Si no hay sistema, agregar mensajes del usuario normalmente
            for msg in user_messages:
                user_content = msg.content if isinstance(msg.content, str) else str(msg.content)
                api_messages.append({"role": "user", "content": user_content})
        
        # Asegurar que no hay mensajes vacíos
        if not api_messages:
            api_messages = [{"role": "user", "content": "Hola"}]
        
        # Make API request
        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json={
                "model": self.model,
                "messages": api_messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": False
            },
            headers={"Content-Type": "application/json"},
            timeout=300  # Aumentar timeout a 5 minutos para modelos lentos
        )
        
        if response.status_code != 200:
            raise ValueError(f"LM Studio API error: {response.status_code} {response.text}")
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Almacenar la respuesta completa para acceso posterior (reasoning_content, etc.)
        self._last_response = result
        
        # Capturar reasoning_content si está disponible (para modelos de razonamiento como DeepSeek R1)
        reasoning_content = None
        if "choices" in result and len(result["choices"]) > 0:
            choice = result["choices"][0]
            if "message" in choice and "reasoning_content" in choice["message"]:
                reasoning_content = choice["message"]["reasoning_content"]
        
        # Return result
        message = AIMessage(content=content)
        
        # Añadir reasoning_content como metadata si está disponible
        if reasoning_content:
            message.additional_kwargs = {"reasoning_content": reasoning_content}
            
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])
    
    @property
    def _llm_type(self) -> str:
        return "lm-studio-api"

def generar_respuesta_fallback(pregunta: str) -> str:
    """Genera una respuesta de fallback simple para casos de timeout"""
    pregunta_lower = pregunta.lower()
    
    if 'java' in pregunta_lower:
        return """Java es un lenguaje de programación orientado a objetos desarrollado por Oracle. 
Sus características principales son: multiplataforma (JVM), orientado a objetos, robusto y seguro. 
Se usa principalmente en aplicaciones empresariales, Android y desarrollo web."""
    elif 'python' in pregunta_lower:
        return """Python es un lenguaje de programación interpretado y de alto nivel. 
Es conocido por su sintaxis simple, versatilidad y amplia comunidad. 
Se usa en desarrollo web, ciencia de datos, IA, automatización y más."""
    elif 'javascript' in pregunta_lower:
        return """JavaScript es un lenguaje de programación interpretado usado principalmente para desarrollo web. 
Permite crear interactividad en páginas web y también se usa en el backend con Node.js."""
    else:
        return f"""Disculpa, el modelo tardó demasiado en procesar tu consulta sobre "{pregunta}". 
Por favor, intenta reformular la pregunta de manera más específica o prueba con otro modelo."""

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

def formatear_duracion(segundos):
    """Convierte segundos a formato legible (minutos y segundos)"""
    if segundos < 1:
        return f"{round(segundos * 1000)}ms"
    elif segundos < 60:
        return f"{round(segundos, 1)}s"
    else:
        minutos = int(segundos // 60)
        segundos_restantes = round(segundos % 60, 1)
        if segundos_restantes == 0:
            return f"{minutos}m"
        else:
            return f"{minutos}m {segundos_restantes}s"

print("🤖 Configurando modelos de IA...")

# Configurar modelos de IA
models = {}

# Configurar modelos de Ollama (locales)
ollama_models = [
    ('llama3', 'Llama3 8B'),
    ('deepseek-coder', 'DeepSeek Coder'),
    ('phi3', 'Microsoft Phi-3'),
    ('gemma:2b', 'Google Gemma 2B'),
    ('gemma3:4b', 'Google Gemma3 4B')
]

for model_key, model_name in ollama_models:
    try:
        models[model_key] = ChatOllama(
            model=model_key
        )
        print(f"✅ {model_name} configurado correctamente")
    except Exception as e:
        print(f"⚠️ {model_name} no disponible: {e}")
        models[model_key] = None

# Configurar Google Gemini (API)
try:
    if Config.GOOGLE_API_KEY:
        os.environ["GOOGLE_API_KEY"] = Config.GOOGLE_API_KEY
        models['gemini-1.5-flash'] = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash"
        )
        print("✅ Google Gemini 1.5 Flash configurado correctamente")
    else:
        print("⚠️ Google Gemini no disponible: No se encontró GOOGLE_API_KEY")
        models['gemini-1.5-flash'] = None
except Exception as e:
    print(f"⚠️ Google Gemini no disponible: {e}")
    models['gemini-1.5-flash'] = None

# Configurar LM Studio (API local)
try:
    if Config.validate_lmstudio():
        # Configurar Google Gemma 3-12B
        models['lmstudio-gemma'] = ChatLMStudio(
            model=Config.LMSTUDIO_MODEL,
            base_url=Config.LMSTUDIO_BASE_URL,
            temperature=Config.DEFAULT_TEMPERATURE,
            max_tokens=Config.MAX_TOKENS
        )
        print("✅ LM Studio (Gemma 3-12B) configurado correctamente")
        
        # Configurar Mistral 7B
        models['lmstudio-mistral'] = ChatLMStudio(
            model=Config.LMSTUDIO_MODEL_MISTRAL,
            base_url=Config.LMSTUDIO_BASE_URL,
            temperature=Config.DEFAULT_TEMPERATURE,
            max_tokens=Config.MAX_TOKENS
        )
        print("✅ LM Studio (Mistral 7B) configurado correctamente")
        
        # Configurar DeepSeek Coder
        models['lmstudio-deepseek'] = ChatLMStudio(
            model=Config.LMSTUDIO_MODEL_DEEPSEEK,
            base_url=Config.LMSTUDIO_BASE_URL,
            temperature=0.3,  # Temperatura más baja para respuestas más rápidas y directas
            max_tokens=800    # Reducir tokens para respuestas más concisas
        )
        print("✅ LM Studio (DeepSeek Coder) configurado correctamente")
    else:
        print("⚠️ LM Studio no disponible")
        models['lmstudio-gemma'] = None
        models['lmstudio-mistral'] = None
        models['lmstudio-deepseek'] = None
except Exception as e:
    print(f"⚠️ LM Studio no disponible: {e}")
    models['lmstudio-gemma'] = None
    models['lmstudio-mistral'] = None
    models['lmstudio-deepseek'] = None

# Verificar que al menos un modelo esté disponible
available_models = [k for k, v in models.items() if v is not None]
if not available_models:
    print("❌ Error: No hay modelos disponibles")
    print("💡 Asegúrate de que:")
    print("   - Ollama esté ejecutándose con llama3 instalado, O")
    print("   - Tengas GOOGLE_API_KEY configurada en .env, O")
    print("   - LM Studio esté ejecutándose con un modelo cargado")
    exit(1)

print(f"🎯 Modelos disponibles: {', '.join(available_models)}")

# Función para obtener el modelo según la selección
def get_model(model_name: str) -> Optional[Union[ChatOllama, ChatGoogleGenerativeAI, ChatLMStudio]]:
    """Obtiene el modelo solicitado o el primero disponible como fallback"""
    if model_name in models and models[model_name] is not None:
        return models[model_name]
    
    # Fallback al primer modelo disponible
    for model_key, model_instance in models.items():
        if model_instance is not None:
            print(f"⚠️ Usando {model_key} como fallback")
            return model_instance
    
    return None

# Función para obtener clima usando API gratuita
def obtener_clima_api(ciudad: str = "Quito") -> dict:
    """Obtiene información del clima usando API gratuita de wttr.in"""
    try:
        # API gratuita que no requiere clave
        url = f"https://wttr.in/{ciudad}?format=j1"
        
        print(f"🌐 Consultando API de clima para {ciudad}...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extraer información relevante
            current = data.get('current_condition', [{}])[0]
            weather_info = {
                'temperatura': current.get('temp_C', 'N/A'),
                'descripcion': current.get('weatherDesc', [{}])[0].get('value', 'N/A'),
                'humedad': current.get('humidity', 'N/A'),
                'sensacion_termica': current.get('FeelsLikeC', 'N/A'),
                'velocidad_viento': current.get('windspeedKmph', 'N/A'),
                'direccion_viento': current.get('winddir16Point', 'N/A'),
                'hora_consulta': current.get('observation_time', 'N/A'),
                'ciudad': ciudad
            }
            
            print(f"✅ Clima obtenido: {weather_info['temperatura']}°C en {ciudad}")
            return {'success': True, 'data': weather_info}
            
        else:
            print(f"⚠️ Error API clima: {response.status_code}")
            return {'success': False, 'error': f'Error de API: {response.status_code}'}
            
    except requests.exceptions.Timeout:
        print("⚠️ Timeout al consultar API de clima")
        return {'success': False, 'error': 'Timeout en consulta'}
    except Exception as e:
        print(f"⚠️ Error consultando API de clima: {e}")
        return {'success': False, 'error': str(e)}

# Función para búsqueda web avanzada usando múltiples APIs
def busqueda_web_avanzada(query: str) -> str:
    """Búsqueda web usando múltiples métodos para mayor confiabilidad"""
    print(f"🔍 Búsqueda web avanzada: {query}")
    
    resultados = []
    
    # Método 1: DuckDuckGo (original)
    try:
        ddg_search = DuckDuckGoSearchRun()
        resultado_ddg = ddg_search.invoke(query)
        if resultado_ddg and len(resultado_ddg.strip()) > 30:
            resultados.append(f"[DuckDuckGo] {resultado_ddg}")
            print("✅ DuckDuckGo: Resultados obtenidos")
        else:
            print("⚠️ DuckDuckGo: Sin resultados útiles")
    except Exception as e:
        print(f"⚠️ DuckDuckGo falló: {e}")
    
    # Método 2: Para noticias específicas, usar términos más específicos
    if any(palabra in query.lower() for palabra in ['noticias', 'news', 'hoy', 'today', 'actualidad']):
        try:
            # Buscar noticias más específicas
            queries_noticias = [
                "noticias tecnología inteligencia artificial hoy",
                "noticias Ecuador últimas",
                "breaking news today",
                "noticias mundo actualidad"
            ]
            
            for query_especifica in queries_noticias:
                try:
                    ddg_search = DuckDuckGoSearchRun()
                    resultado = ddg_search.invoke(query_especifica)
                    if resultado and len(resultado.strip()) > 30:
                        resultados.append(f"[Noticias {query_especifica}] {resultado[:500]}...")
                        print(f"✅ Noticias encontradas para: {query_especifica}")
                        break  # Si encontramos algo, salir del loop
                except:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Búsqueda de noticias específicas falló: {e}")
    
    # Método 3: API de búsqueda alternativa (usando scraping básico)
    try:
        # Usar una API pública de búsqueda o scraping básico
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extraer resultados de la API
            abstract = data.get('Abstract', '')
            answer = data.get('Answer', '')
            
            if abstract:
                resultados.append(f"[API Abstract] {abstract}")
                print("✅ API DuckDuckGo: Abstract obtenido")
            
            if answer:
                resultados.append(f"[API Answer] {answer}")
                print("✅ API DuckDuckGo: Answer obtenido")
                
    except Exception as e:
        print(f"⚠️ API DuckDuckGo falló: {e}")
    
    # Método 3: Para clima específico, usar nuestra API
    if any(palabra in query.lower() for palabra in ['clima', 'weather', 'temperatura', 'temperature', 'tiempo']):
        try:
            # Extraer ciudad de la consulta
            ciudad = 'Quito'  # Default
            if 'quito' in query.lower():
                ciudad = 'Quito'
            elif 'guayaquil' in query.lower():
                ciudad = 'Guayaquil'
            elif 'cuenca' in query.lower():
                ciudad = 'Cuenca'
            elif 'new york' in query.lower() or 'nueva york' in query.lower():
                ciudad = 'New York'
            elif 'london' in query.lower() or 'londres' in query.lower():
                ciudad = 'London'
            elif 'madrid' in query.lower():
                ciudad = 'Madrid'
            
            clima_data = obtener_clima_api(ciudad)
            if clima_data['success']:
                data = clima_data['data']
                clima_info = f"Clima actual en {ciudad}: {data['temperatura']}°C, {data['descripcion']}, Humedad: {data['humedad']}%, Viento: {data['velocidad_viento']} km/h"
                resultados.append(f"[Clima API] {clima_info}")
                print(f"✅ Clima API: Datos obtenidos para {ciudad}")
                
        except Exception as e:
            print(f"⚠️ API Clima falló: {e}")
    
    # Compilar resultados
    if resultados:
        resultado_final = "\n\n".join(resultados)
        print(f"✅ Búsqueda completada con {len(resultados)} fuentes")
        return resultado_final
    else:
        print("❌ No se obtuvieron resultados de ninguna fuente")
        return f"No se pudo obtener información actualizada sobre '{query}'. Se recomienda consultar fuentes directas como Google, sitios web oficiales o aplicaciones especializadas."

# Crear herramienta personalizada para búsqueda web
def crear_herramienta_busqueda():
    """Crea una herramienta de búsqueda web personalizada"""
    return Tool(
        name="web_search",
        description="Busca información actual en internet sobre cualquier tema. Útil para noticias, precios, eventos actuales, etc. Input debe ser una consulta de búsqueda específica.",
        func=busqueda_web_avanzada
    )

def ejecutar_comando_ollama(command: str) -> str:
    """Ejecuta comandos de Ollama y retorna el resultado"""
    try:
        import subprocess
        import json
        
        command = command.strip()
        if not command:
            return "❌ Error: Comando vacío"
        
        # Lista de comandos permitidos por seguridad
        allowed_commands = ['ps', 'list', 'serve', 'run', 'stop', 'show', 'create', 'rm', 'cp', 'push', 'pull']
        
        # Parsear el comando
        cmd_parts = command.split()
        if not cmd_parts or cmd_parts[0] not in allowed_commands:
            return f"❌ Error: Comando no permitido. Comandos disponibles: {', '.join(allowed_commands)}"
        
        # Construir comando completo
        full_command = ['ollama'] + cmd_parts
        
        try:
            # Ejecutar comando con timeout
            if cmd_parts[0] == 'serve':
                # Para serve, iniciar en background
                process = subprocess.Popen(
                    full_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
                return "✅ Ollama serve iniciado en background. Verifica el estado con 'ollama ps'."
            else:
                # Para otros comandos, ejecutar y obtener output
                result = subprocess.run(
                    full_command,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False
                )
                
                # Combinar stdout y stderr
                output = ''
                if result.stdout:
                    output += result.stdout
                if result.stderr:
                    output += result.stderr
                
                if not output:
                    output = f"✅ Comando '{command}' ejecutado exitosamente (sin output)"
                
                return f"📋 Resultado de 'ollama {command}':\n{output}"
                
        except subprocess.TimeoutExpired:
            return f"⏰ Error: Timeout al ejecutar comando 'ollama {command}' (>30s)"
        except subprocess.CalledProcessError as e:
            return f"❌ Error al ejecutar comando 'ollama {command}': {e}"
        except Exception as e:
            return f"❌ Error inesperado: {str(e)}"
            
    except Exception as e:
        return f"❌ Error al ejecutar comando Ollama: {str(e)}"

def crear_herramienta_ollama():
    """Crea una herramienta para ejecutar comandos Ollama"""
    return Tool(
        name="ollama_command",
        description="Ejecuta comandos de Ollama para gestionar modelos de IA. Comandos disponibles: ps (ver modelos en ejecución), list (listar modelos), serve (iniciar servicio), run <modelo> (ejecutar modelo), stop <modelo> (detener modelo), show <modelo> (info del modelo), pull <modelo> (descargar modelo). Input debe ser el comando sin 'ollama' (ej: 'ps', 'list', 'run llama3')",
        func=ejecutar_comando_ollama
    )

def formatear_respuesta_clima(clima_data: dict, modelo_seleccionado: str) -> str:
    """Formatea la respuesta del clima de manera atractiva"""
    if clima_data['success']:
        data = clima_data['data']
        return f"""🌤️ **Clima actual en {data['ciudad']}**

📊 **Condiciones actuales:**
• **Temperatura:** {data['temperatura']}°C
• **Sensación térmica:** {data['sensacion_termica']}°C
• **Condiciones:** {data['descripcion']}
• **Humedad:** {data['humedad']}%
• **Viento:** {data['velocidad_viento']} km/h ({data['direccion_viento']})
• **Última actualización:** {data['hora_consulta']}

🏔️ **Información contextual:**
Quito se encuentra a 2,850 metros sobre el nivel del mar, lo que influye en su clima templado durante todo el año. Las temperaturas suelen oscilar entre 10°C y 25°C.

📱 **Para más detalles:**
• Pronóstico extendido: [wttr.in/Quito](https://wttr.in/Quito)
• Apps recomendadas: AccuWeather, Weather Underground
• Sitios web: weather.com, tiempo.com

*Datos obtenidos de API meteorológica en tiempo real*"""
    else:
        return f"""❌ **No se pudo obtener el clima actual**

Error: {clima_data['error']}

🌤️ **Información general sobre Quito:**
Quito tiene un clima subtropical de montaña con temperaturas relativamente estables durante todo el año:
• **Día:** 18-24°C
• **Noche:** 8-15°C
• **Julio:** Estación seca, días soleados y noches frescas

📱 **Consulta información actualizada en:**
• Google: "clima Quito Ecuador"
• AccuWeather.com
• Weather.com
• Apps móviles de clima"""

# Configurar herramientas para el agente
herramienta_busqueda = crear_herramienta_busqueda()
herramienta_ollama = crear_herramienta_ollama()
tools = [herramienta_busqueda, herramienta_ollama, DuckDuckGoSearchRun()]

# Prompt optimizado para búsquedas generales
agent_prompt = PromptTemplate.from_template("""
Eres un asistente de IA especializado en proporcionar respuestas precisas y actuales. Tienes acceso a herramientas de búsqueda web y gestión de modelos Ollama.

Herramientas disponibles:
{tools}

REGLAS IMPORTANTES: 
1. SIEMPRE usa búsqueda web para: noticias recientes, precios actuales, eventos deportivos, información actualizada
2. USA ollama_command para: gestionar modelos Ollama, ver modelos disponibles, ejecutar/detener modelos, obtener información de modelos
3. NUNCA digas que no tienes acceso a información en tiempo real - ¡SÍ LO TIENES!
4. Si una búsqueda falla, intenta con términos diferentes
5. Proporciona respuestas útiles basadas en los resultados obtenidos
6. Para comandos Ollama, usa solo el comando sin 'ollama' (ej: 'ps', 'list', 'run llama3')

COMANDOS OLLAMA DISPONIBLES:
• ps - Ver modelos en ejecución
• list - Listar todos los modelos instalados
• serve - Iniciar el servicio Ollama
• run <modelo> - Ejecutar un modelo específico
• stop <modelo> - Detener un modelo específico
• show <modelo> - Mostrar información detallada de un modelo
• pull <modelo> - Descargar un nuevo modelo

Formato OBLIGATORIO:
Question: la pregunta que debes responder
Thought: necesito buscar información actual sobre [tema específico] O necesito ejecutar comando Ollama [comando]
Action: duckduckgo_search O web_search O ollama_command
Action Input: [términos de búsqueda específicos] O [comando ollama sin 'ollama']
Observation: [resultados de la búsqueda o comando]
Thought: ahora tengo información actual y puedo responder
Final Answer: [respuesta completa en español basada en los resultados]

Pregunta: {input}
Thought:{agent_scratchpad}
""")

# Crear el agente con manejo de errores y herramientas mejoradas
agents = {}
for model_name, model_instance in models.items():
    if model_instance is not None:
        try:
            # Usar el prompt estándar de React que funciona
            react_prompt = hub.pull("hwchase17/react")
            
            agent = create_react_agent(model_instance, tools, react_prompt)
            agents[model_name] = AgentExecutor(
                agent=agent, 
                tools=tools, 
                verbose=True,
                max_iterations=20,  # Aumentado significativamente para búsquedas extensas
                max_execution_time=1800,  # 30 minutos para búsquedas completas
                handle_parsing_errors=True,
                return_intermediate_steps=True
            )
            print(f"✅ Agente {model_name} creado con herramientas avanzadas")
        except Exception as e:
            print(f"⚠️ Error creando agente {model_name}: {e}")
            agents[model_name] = None

# También configurar un chat simple sin agente para preguntas básicas
simple_chat_prompt = ChatPromptTemplate.from_messages([
    ("system", """Eres un asistente de IA especializado y conocedor. Tu trabajo es proporcionar respuestas directas, precisas y útiles en español.

REGLAS IMPORTANTES:
1. Responde DIRECTAMENTE a la pregunta formulada
2. Proporciona información específica y detallada
3. Si te preguntan "¿qué es X?", explica qué es X de manera clara y completa
4. Si te preguntan sobre conceptos técnicos, da definiciones precisas
5. Mantén un tono profesional pero accesible
6. No digas solo "estoy aquí para ayudar" - da la respuesta específica

EJEMPLOS:
- Si preguntan "¿qué es Java?" → Explica que Java es un lenguaje de programación
- Si preguntan "¿qué es Python?" → Explica que Python es un lenguaje de programación
- Si preguntan "¿qué es HTML?" → Explica que HTML es un lenguaje de marcado

Siempre proporciona información útil y específica."""),
    ("user", "{pregunta}")
])

# Crear prompts específicos para diferentes modelos
def crear_prompt_para_modelo(model_name: str) -> ChatPromptTemplate:
    """Crea un prompt optimizado según el modelo específico"""
    
    if model_name == 'deepseek-coder':
        return ChatPromptTemplate.from_messages([
            ("system", """Eres DeepSeek Coder, un asistente especializado en programación y desarrollo. Proporciona respuestas técnicas precisas y código cuando sea necesario.

ESPECIALIDADES:
- Explicar conceptos de programación
- Proporcionar ejemplos de código
- Debugging y resolución de problemas
- Mejores prácticas de desarrollo

FORMATO DE RESPUESTA:
- Respuestas directas y técnicas
- Incluye ejemplos de código cuando sea relevante
- Explica conceptos paso a paso
- Menciona ventajas y desventajas cuando sea apropiado"""),
            ("user", "{pregunta}")
        ])
    
    elif model_name == 'deepseek-r1:8b':
        return ChatPromptTemplate.from_messages([
            ("system", """Eres DeepSeek R1, un modelo de razonamiento avanzado diseñado para análisis profundo y respuestas reflexivas.

CARACTERÍSTICAS ESPECIALES:
- Razonamiento paso a paso antes de responder
- Análisis crítico y evaluación de múltiples perspectivas
- Explicaciones detalladas y fundamentadas
- Capacidad de autorreflexión y corrección

FORMATO DE RESPUESTA OBLIGATORIO:
🔍 **ANÁLISIS INICIAL:** [Comprensión del problema/pregunta]

🧠 **RAZONAMIENTO:**
• **Paso 1:** [Primera consideración o enfoque]
• **Paso 2:** [Segunda consideración o análisis]
• **Paso 3:** [Tercera consideración o síntesis]

📋 **RESPUESTA:** [Conclusión fundamentada y detallada]

🔄 **REFLEXIÓN:** [Validación de la respuesta y posibles alternativas]

IMPORTANTE: Siempre usa este formato estructurado para mostrar tu proceso de pensamiento completo."""),
            ("user", "{pregunta}")
        ])
    
    elif model_name == 'lmstudio-deepseek':
        return ChatPromptTemplate.from_messages([
            ("system", """Eres DeepSeek Coder ejecutándose en LM Studio. Proporciona respuestas técnicas claras y directas.

INSTRUCCIONES:
- Respuestas concisas pero completas
- Enfócate en aspectos técnicos cuando sea relevante
- Usa formato claro con viñetas o numeración
- Evita explicaciones excesivamente largas
- Proporciona ejemplos de código solo cuando sea necesario

FORMATO DE RESPUESTA:
🔧 **EXPLICACIÓN TÉCNICA:** [Definición clara y directa]

💻 **CARACTERÍSTICAS PRINCIPALES:**
• [Característica 1]
• [Característica 2] 
• [Característica 3]

📝 **EJEMPLO PRÁCTICO:** [Solo si es relevante y breve]

Mantén las respuestas enfocadas y útiles."""),
            ("user", "{pregunta}")
        ])
    
    elif model_name == 'gemma:2b':
        return ChatPromptTemplate.from_messages([
            ("system", """Eres un asistente útil. Responde de forma clara y completa.

Si preguntan "¿qué es X?", explica qué es X con:
1. Definición principal
2. Características importantes
3. Usos principales

EJEMPLO para "¿qué es Java?":
Java es un lenguaje de programación orientado a objetos desarrollado por Sun Microsystems (ahora Oracle). Sus características principales son:

• **Multiplataforma**: "Write once, run anywhere" - el código Java se ejecuta en cualquier sistema con JVM
• **Orientado a objetos**: Organiza el código en clases y objetos
• **Robusto y seguro**: Manejo automático de memoria y verificación de código
• **Usos principales**: Aplicaciones empresariales, aplicaciones móviles (Android), desarrollo web

Es uno de los lenguajes más populares para desarrollo de software empresarial y aplicaciones Android.

Responde siempre de manera útil y completa."""),
            ("user", "{pregunta}")
        ])
    
    elif model_name == 'phi3':
        return ChatPromptTemplate.from_messages([
            ("system", f"""Eres Microsoft Phi-3, un modelo compacto pero potente diseñado para respuestas rápidas y precisas.

FECHA ACTUAL: {time.strftime('%d de %B de %Y')} 

IMPORTANTE: Para preguntas sobre noticias, eventos actuales, precios, clima o información reciente, debes indicar claramente que necesitas búsqueda web en tiempo real, ya que tu conocimiento tiene una fecha de corte y puede estar desactualizado.

CARACTERÍSTICAS:
- Respuestas concisas pero completas
- Enfoque en eficiencia y claridad
- Proporciona información práctica y útil
- Evita redundancias y texto innecesario
- SIEMPRE reconoce limitaciones temporales para información actual

FORMATO:
1. Respuesta directa a la pregunta
2. Información clave en 2-3 puntos
3. Ejemplo o aplicación práctica si es relevante
4. Para noticias/eventos actuales: Recomendar búsqueda web"""),
            ("user", "{pregunta}")
        ])
    
    else:
        # Prompt por defecto para Llama3 y Gemini
        return ChatPromptTemplate.from_messages([
            ("system", """Eres un asistente de IA especializado y conocedor. Tu trabajo es proporcionar respuestas directas, precisas y útiles en español.

REGLAS IMPORTANTES:
1. Responde DIRECTAMENTE a la pregunta formulada
2. Proporciona información específica y detallada
3. Si te preguntan "¿qué es X?", explica qué es X de manera clara y completa
4. Si te preguntan sobre conceptos técnicos, da definiciones precisas
5. Mantén un tono profesional pero accesible
6. No digas solo "estoy aquí para ayudar" - da la respuesta específica

EJEMPLOS:
- Si preguntan "¿qué es Java?" → Explica que Java es un lenguaje de programación
- Si preguntan "¿qué es Python?" → Explica que Python es un lenguaje de programación
- Si preguntan "¿qué es HTML?" → Explica que HTML es un lenguaje de marcado

Siempre proporciona información útil y específica."""),
            ("user", "{pregunta}")
        ])

simple_chains = {}
for model_name, model_instance in models.items():
    if model_instance is not None:
        # Obtener prompt personalizado para cada modelo
        model_prompt = crear_prompt_para_modelo(model_name)
        
        # Configurar chain con temperatura si es posible
        ollama_models_list = ['llama3', 'deepseek-coder', 'deepseek-r1:8b', 'phi3', 'gemma:2b']
        lmstudio_models_list = ['lmstudio-gemma', 'lmstudio-mistral', 'lmstudio-deepseek']
        
        if model_name in ollama_models_list:
            # Para modelos de Ollama, configurar directamente sin bind (temperatura no es compatible)
            simple_chains[model_name] = model_prompt | model_instance | StrOutputParser()
        elif model_name in lmstudio_models_list:
            # Para modelos de LM Studio, configurar con temperatura
            configured_model = model_instance
            simple_chains[model_name] = model_prompt | configured_model | StrOutputParser()
        elif model_name == 'gemini-1.5-flash':
            # Para Gemini, configurar temperatura usando bind
            configured_model = model_instance.bind(temperature=Config.DEFAULT_TEMPERATURE)
            simple_chains[model_name] = model_prompt | configured_model | StrOutputParser()
        else:
            # Fallback sin temperatura específica
            simple_chains[model_name] = model_prompt | model_instance | StrOutputParser()
        
        print(f"✅ Chat simple {model_name} configurado con prompt personalizado")

@app.route('/')
def index() -> str:
    return render_template('index.html', modelos_disponibles=available_models)

@app.route('/chat', methods=['POST'])
def chat() -> Union[Response, Tuple[Response, int]]:
    try:
        print("🔍 DEBUG: Iniciando función chat()")
        data = request.get_json()
        print(f"🔍 DEBUG: Datos recibidos: {data}")
        
        pregunta = data.get('pregunta', '')
        modo = data.get('modo', 'simple')  # 'simple' o 'agente'
        modelo_seleccionado = data.get('modelo', available_models[0] if available_models else 'llama3')
        permitir_internet = data.get('permitir_internet', True)  # Por defecto permitir internet
        
        print(f"🔍 DEBUG: pregunta='{pregunta}', modo='{modo}', modelo='{modelo_seleccionado}', internet={permitir_internet}")
        
        if not pregunta:
            return jsonify({'error': 'No se proporcionó ninguna pregunta'}), 400
        
        # Obtener el modelo seleccionado
        modelo = get_model(modelo_seleccionado)
        print(f"🔍 DEBUG: Modelo obtenido: {modelo}")
        
        if modelo is None:
            return jsonify({'error': 'No hay modelos disponibles'}), 500

        # Detección inteligente para forzar modo agente cuando se necesite información actual
        palabras_actualidad = [
            'noticias', 'news', 'actualidad', 'hoy', 'today', 'actual', 'reciente', 
            'precio', 'price', 'cotización', 'último', 'latest', 'breaking',
            'eventos', 'acontecimiento', 'qué pasó', 'qué está pasando'
        ]
        
        # Detección de comandos Ollama para activar modo agente
        palabras_ollama = [
            'ollama ps', 'ollama list', 'ollama serve', 'ollama run', 'ollama stop', 
            'ollama show', 'ollama pull', 'modelos ollama', 'ver modelos', 
            'ejecutar modelo', 'detener modelo', 'instalar modelo', 'descargar modelo',
            'estado ollama', 'servicio ollama', 'gestionar ollama', 'comandos ollama'
        ]
        
        necesita_busqueda_web = any(palabra in pregunta.lower() for palabra in palabras_actualidad)
        necesita_comando_ollama = any(palabra in pregunta.lower() for palabra in palabras_ollama)
        
        if (necesita_busqueda_web or necesita_comando_ollama) and permitir_internet and modo == 'simple':
            if necesita_comando_ollama:
                print(f"🤖 Detectada consulta de comandos Ollama, cambiando a modo agente")
            else:
                print(f"🔄 Detectada consulta que requiere información actual, cambiando a modo agente")
            modo = 'agente'

        # Forzar modo simple si internet está deshabilitado y se intenta usar modos que requieren web
        if not permitir_internet and modo in ['agente', 'busqueda_rapida']:
            print(f"🔍 DEBUG: Forzando modo simple porque internet está deshabilitado")
            modo = 'simple'

        if modo == 'agente' and permitir_internet and modelo_seleccionado in agents and agents[modelo_seleccionado] is not None:
            # Verificar si es una consulta de clima para usar endpoint especializado
            if any(palabra in pregunta.lower() for palabra in ['clima', 'weather', 'temperatura', 'temp', 'tiempo']):
                print(f"🌤️ Detectada consulta de clima, usando endpoint especializado")
                try:
                    tiempo_inicio = time.time()
                    
                    # Extraer ciudad de la pregunta
                    ciudad = 'Quito'  # Default
                    if 'quito' in pregunta.lower():
                        ciudad = 'Quito'
                    elif 'guayaquil' in pregunta.lower():
                        ciudad = 'Guayaquil'
                    elif 'cuenca' in pregunta.lower():
                        ciudad = 'Cuenca'
                    
                    # Obtener datos del clima directamente
                    clima_data = obtener_clima_api(ciudad)
                    tiempo_fin = time.time()
                    duracion = round(tiempo_fin - tiempo_inicio, 2)
                    duracion_formateada = formatear_duracion(duracion)
                    
                    if clima_data['success']:
                        # Usar el modelo para generar una respuesta formateada
                        if modelo_seleccionado in simple_chains:
                            prompt_clima = f"""La consulta del usuario es: "{pregunta}"

Los datos actuales del clima en {ciudad} son:
- Temperatura: {clima_data['data']['temperatura']}°C
- Condiciones: {clima_data['data']['descripcion']}
- Humedad: {clima_data['data']['humedad']}%
- Sensación térmica: {clima_data['data']['sensacion_termica']}°C
- Viento: {clima_data['data']['velocidad_viento']} km/h ({clima_data['data']['direccion_viento']})
- Hora de consulta: {clima_data['data']['hora_consulta']}

Responde de manera clara y útil con estos datos actuales."""
                            
                            respuesta_formateada = simple_chains[modelo_seleccionado].invoke({"pregunta": prompt_clima})
                            
                            return jsonify({
                                'respuesta': respuesta_formateada,
                                'modo': 'clima_directo_agente',
                                'modelo_usado': modelo_seleccionado,
                                'pensamientos': [
                                    f"🌤️ Detectada consulta sobre clima en {ciudad}",
                                    "🔍 Consultando API meteorológica en tiempo real",
                                    f"📊 Datos obtenidos: {clima_data['data']['temperatura']}°C, {clima_data['data']['descripcion']}",
                                    "🧠 Procesando respuesta personalizada"
                                ],
                                'metadata': {
                                    'duracion': duracion,
                                    'duracion_formateada': duracion_formateada,
                                    'iteraciones': 1,
                                    'busquedas': 1,
                                    'timestamp': time.time(),
                                    'timestamp_inicio': tiempo_inicio,
                                    'timestamp_fin': tiempo_fin,
                                    'internetHabilitado': permitir_internet,
                                    'tipo_consulta': 'clima_optimizada'
                                }
                            })
                    
                except Exception as e:
                    print(f"⚠️ Error en consulta de clima optimizada: {e}")
                    # Fallback al agente normal
                    pass
            
            # Usar el agente para preguntas que puedan requerir búsqueda web
            tiempo_inicio = time.time()  # Mover antes del try para tenerlo disponible en except
            logs_agente = []  # Para capturar logs detallados del agente
            
            try:
                print(f"🤖 Iniciando agente {modelo_seleccionado} para: {pregunta[:50]}...")
                logs_agente.append("🚀 Iniciando sistema AgentExecutor")
                logs_agente.append("⚡ > Entering new AgentExecutor chain...")
                
                # Configurar captura de logs más detallada para obtener <think> y otros elementos
                import io
                import sys
                import logging
                from contextlib import redirect_stdout, redirect_stderr
                
                # Crear capturadores de salida
                captured_output = io.StringIO()
                captured_logs = []
                
                # Handler personalizado para capturar logs
                class LogCapture(logging.Handler):
                    def emit(self, record):
                        captured_logs.append(self.format(record))
                
                log_capture = LogCapture()
                logging.getLogger().addHandler(log_capture)
                
                try:
                    # Ejecutar el agente con captura
                    with redirect_stdout(captured_output):
                        respuesta_completa = agents[modelo_seleccionado].invoke({"input": pregunta})
                finally:
                    # Remover el handler
                    logging.getLogger().removeHandler(log_capture)
                
                # Obtener toda la salida capturada
                agent_full_output = captured_output.getvalue()
                
                tiempo_fin = time.time()
                duracion = round(tiempo_fin - tiempo_inicio, 2)
                duracion_formateada = formatear_duracion(duracion)
                
                logs_agente.append("🏁 > Finished chain.")
                logs_agente.append(f"✅ Agente completado en {duracion_formateada}")
                
                print(f"✅ Agente completado en {duracion_formateada}")
                
                # Procesar la salida capturada para extraer <think> y otros elementos
                think_content = []
                if agent_full_output:
                    # Buscar contenido <think> usando regex
                    import re
                    think_matches = re.findall(r'<think>(.*?)</think>', agent_full_output, re.DOTALL | re.IGNORECASE)
                    for i, think in enumerate(think_matches):
                        think_content.append(f"💭 <think> {i+1}: {think.strip()}")
                    
                    # Buscar otros patrones útiles
                    thought_matches = re.findall(r'Thought: (.*?)(?=\n(?:Action:|Observation:|Final Answer:)|$)', agent_full_output, re.DOTALL)
                    for i, thought in enumerate(thought_matches):
                        if thought.strip():
                            logs_agente.append(f"🧠 Thought {i+1}: {thought.strip()}")
                    
                    # Buscar acciones específicas
                    action_input_matches = re.findall(r'Action Input: (.*?)(?=\n|$)', agent_full_output)
                    for i, action_input in enumerate(action_input_matches):
                        if action_input.strip():
                            logs_agente.append(f"📝 Action Input {i+1}: {action_input.strip()}")
                
                # Agregar logs capturados
                for log_msg in captured_logs:
                    if any(keyword in log_msg.lower() for keyword in ['think', 'thought', 'action', 'observation']):
                        logs_agente.append(f"📋 Log: {log_msg}")
                
                # Extraer pasos intermedios si están disponibles
                pasos_intermedios = []
                busquedas_count = 0
                pensamientos = logs_agente.copy()  # Empezar con los logs del agente
                
                # Agregar contenido <think> a los pensamientos
                if think_content:
                    pensamientos.extend(think_content)
                    print(f"📝 Capturado {len(think_content)} bloques <think>")
                
                if 'intermediate_steps' in respuesta_completa:
                    print(f"📊 Procesando {len(respuesta_completa['intermediate_steps'])} pasos intermedios...")
                    
                    for i, paso in enumerate(respuesta_completa['intermediate_steps']):
                        if len(paso) >= 2:
                            accion = paso[0]
                            observacion = paso[1]
                            
                            # Contar búsquedas
                            if hasattr(accion, 'tool') and accion.tool in ['web_search', 'duckduckgo_search']:
                                busquedas_count += 1
                                pensamientos.append(f"🔍 Realizando búsqueda: '{accion.tool_input}'")
                            
                            # Agregar información del paso
                            paso_info = {
                                'step': i + 1,
                                'action': accion.tool if hasattr(accion, 'tool') else str(accion),
                                'action_input': accion.tool_input if hasattr(accion, 'tool_input') else str(accion),
                                'observation': observacion[:500] + '...' if len(str(observacion)) > 500 else str(observacion),
                                'thought': f"Ejecutando {accion.tool}" if hasattr(accion, 'tool') else "Procesando información"
                            }
                            pasos_intermedios.append(paso_info)
                            
                            # Agregar pensamiento formateado más detallado
                            if hasattr(accion, 'tool'):
                                pensamientos.append(f"💭 Paso {i+1}: Usando herramienta '{accion.tool}' con entrada: '{accion.tool_input}'")
                                # Mostrar resultado truncado pero más informativo
                                resultado_truncado = str(observacion)[:300]
                                if len(str(observacion)) > 300:
                                    resultado_truncado += "..."
                                pensamientos.append(f"📋 Resultado: {resultado_truncado}")
                            
                            # Agregar análisis del resultado
                            if "No good" in str(observacion):
                                pensamientos.append("⚠️ Búsqueda sin resultados útiles, intentando método alternativo")
                            elif len(str(observacion)) > 50:
                                pensamientos.append("✅ Información obtenida, procesando para generar respuesta")
                
                # Si hay pasos pero sin pensamientos detallados, agregar contexto
                if len(pasos_intermedios) > 0 and len(pensamientos) == 0:
                    pensamientos.append("🔄 Ejecutando proceso de búsqueda y análisis")
                    pensamientos.append(f"📊 Completados {len(pasos_intermedios)} pasos de investigación")
                
                # Si no hay pasos intermedios, crear pensamientos básicos
                if len(pasos_intermedios) == 0:
                    pensamientos.append("💭 Analizando consulta con conocimiento base")
                    pensamientos.append("🧠 Generando respuesta usando modelo de IA")
                    if "noticias" in pregunta.lower() or "hoy" in pregunta.lower():
                        pensamientos.append("📰 Nota: Para noticias actuales se recomienda activar búsqueda web")
                else:
                    # Agregar pensamiento final
                    pensamientos.append("🎯 Sintetizando información recopilada")
                    pensamientos.append("📝 Formateando respuesta final")
                
                # Verificar si las búsquedas fallaron y generar respuesta de fallback inteligente
                respuesta_output = respuesta_completa.get('output', '')
                if busquedas_count > 0 and respuesta_output and "No good DuckDuckGo Search Result was found" in respuesta_output:
                    print("⚠️ Búsquedas web fallaron, generando respuesta de fallback inteligente...")
                    
                    # Generar respuesta de fallback específica para noticias
                    if any(palabra in pregunta.lower() for palabra in ['noticias', 'news', 'hoy', 'actualidad']):
                        respuesta_completa['output'] = f"""📰 **Información sobre noticias del día**

Lo siento, actualmente estoy experimentando dificultades para acceder a fuentes de noticias en tiempo real. Sin embargo, te puedo sugerir las mejores fuentes para mantenerte informado sobre las noticias de hoy:

🌐 **Fuentes recomendadas de noticias:**
• **Internacionales:** BBC News, CNN, Reuters, Associated Press
• **Ecuador:** El Universo, El Comercio, Primicias, GK
• **Tecnología:** TechCrunch, Wired, The Verge
• **Deportes:** ESPN, Marca, Fox Sports

🔍 **Para noticias específicas, te recomiendo:**
1. Visitar directamente Google News
2. Usar aplicaciones de noticias como Apple News o Google News
3. Seguir cuentas verificadas en redes sociales
4. Consultar sitios web oficiales de medios

📱 **Tip:** Configura alertas de Google para temas específicos que te interesen.

¿Hay algún tema específico de noticias sobre el que te gustaría que te ayude a encontrar información?"""

                        pensamientos.append("🔄 Búsqueda web no disponible, proporcionando fuentes alternativas para noticias")
                        pensamientos.append("💡 Sugiriendo medios confiables y métodos alternativos de búsqueda")
                    else:
                        # Para otras consultas que requieren información actualizada
                        respuesta_completa['output'] = f"""🔍 **Dificultades para acceder a información en tiempo real**

Actualmente no puedo acceder a información actualizada sobre "{pregunta}" debido a limitaciones en las herramientas de búsqueda web.

💡 **Te sugiero:**
1. Consultar directamente Google o Bing
2. Visitar sitios web oficiales relacionados con tu consulta
3. Usar aplicaciones especializadas
4. Verificar redes sociales oficiales

❓ **¿Puedo ayudarte con algo más específico?**
Mientras tanto, puedo responder preguntas sobre temas generales, explicaciones conceptuales, o ayudarte de otras maneras."""
                        
                        pensamientos.append("⚠️ Información en tiempo real no disponible")
                        pensamientos.append("🛠️ Proporcionando alternativas para obtener información actualizada")
                
                return jsonify({
                    'respuesta': respuesta_completa['output'],
                    'modo': 'agente',
                    'modelo_usado': modelo_seleccionado,
                    'pasos_intermedios': pasos_intermedios,
                    'pensamientos': pensamientos,
                    'metadata': {
                        'duracion': duracion,
                        'duracion_formateada': duracion_formateada,
                        'iteraciones': len(pasos_intermedios),
                        'busquedas': busquedas_count,
                        'timestamp': time.time(),
                        'timestamp_inicio': tiempo_inicio,
                        'timestamp_fin': tiempo_fin,
                        'internetHabilitado': permitir_internet
                    }
                })
            except Exception as e:
                error_msg = str(e)
                print(f"Error en agente {modelo_seleccionado}: {error_msg}")
                
                # Manejo específico para diferentes tipos de errores
                if "iteration limit" in error_msg.lower() or "time limit" in error_msg.lower():
                    print("⚠️ Agente detenido por límite de tiempo/iteraciones, intentando extraer información parcial...")
                    
                    # Intentar extraer información del error si está disponible
                    try:
                        # Si hay pasos intermedios en el error, intentar usarlos
                        tiempo_fin = time.time()
                        duracion = round(tiempo_fin - tiempo_inicio, 2)
                        duracion_formateada = formatear_duracion(duracion)
                        
                        # Crear respuesta usando la información disponible de la búsqueda
                        if modelo_seleccionado in simple_chains:
                            prompt_con_contexto = f"""
                            El usuario preguntó: "{pregunta}"
                            
                            Se realizó una búsqueda web que encontró información parcial. Aunque el proceso se detuvo por límite de tiempo, puedo proporcionar una respuesta útil basada en:
                            
                            INFORMACIÓN DE BÚSQUEDA ENCONTRADA:
                            - Se encontraron fuentes sobre Google Noticias y cómo buscar noticias
                            - Información sobre configuración de búsquedas de noticias por ubicación
                            - Referencias a herramientas para organizar y encontrar noticias
                            
                            Por favor, proporciona una respuesta útil sobre las noticias de hoy, incluyendo:
                            1. Reconocimiento de que la búsqueda encontró información parcial
                            2. Recomendaciones específicas para obtener noticias actuales
                            3. Mencionar Google News como herramienta principal encontrada
                            4. Sugerir otros sitios de noticias confiables
                            5. Tips para configurar búsquedas de noticias
                            
                            Responde de manera útil y proactiva.
                            """
                            
                            respuesta_con_contexto = simple_chains[modelo_seleccionado].invoke({"pregunta": prompt_con_contexto})
                            
                            return jsonify({
                                'respuesta': respuesta_con_contexto,
                                'modo': 'agente_parcial',
                                'modelo_usado': modelo_seleccionado,
                                'pensamientos': [
                                    "🔍 Búsqueda web iniciada exitosamente",
                                    "📊 Información parcial obtenida de fuentes web",
                                    "⏰ Proceso detenido por límite de tiempo",
                                    "🧠 Generando respuesta con información disponible",
                                    "💡 Proporcionando recomendaciones adicionales"
                                ],
                                'metadata': {
                                    'duracion': duracion,
                                    'duracion_formateada': duracion_formateada,
                                    'iteraciones': 1,
                                    'busquedas': 1,
                                    'timestamp': time.time(),
                                    'timestamp_inicio': tiempo_inicio,
                                    'timestamp_fin': tiempo_fin,
                                    'internetHabilitado': permitir_internet,
                                    'nota': 'Respuesta generada con información parcial'
                                }
                            })
                    except:
                        pass
                    
                    fallback_msg = f"⚠️ La búsqueda tomó más tiempo del esperado. Intentando respuesta rápida...\n\n"
                elif "parsing" in error_msg.lower():
                    fallback_msg = f"⚠️ Hubo un problema procesando la búsqueda. Usando respuesta directa...\n\n"
                else:
                    fallback_msg = f"⚠️ Error en búsqueda web. Usando modo simple...\n\n"
                
                # Fallback a chat simple si el agente falla
                if modelo_seleccionado in simple_chains:
                    respuesta = simple_chains[modelo_seleccionado].invoke({"pregunta": pregunta})
                    return jsonify({
                        'respuesta': f"{fallback_msg}{respuesta}",
                        'modo': 'simple_fallback',
                        'modelo_usado': modelo_seleccionado,
                        'metadata': {
                            'internetHabilitado': permitir_internet,
                            'iteraciones': 0,
                            'busquedas': 0
                        }
                    })
                else:
                    return jsonify({'error': f'Modelo {modelo_seleccionado} no disponible para fallback'}), 500
        else:
            # Usar chat simple
            print(f"🔍 DEBUG: Usando modo simple con modelo {modelo_seleccionado}")
            if modelo_seleccionado in simple_chains:
                print(f"🔍 DEBUG: Chain encontrada para {modelo_seleccionado}")
                tiempo_inicio = time.time()
                
                # Manejo especial para DeepSeek R1 - Generar pensamientos simulados
                pensamientos_proceso = []
                if modelo_seleccionado == 'deepseek-r1:8b':
                    # Simular proceso de razonamiento paso a paso
                    pensamientos_proceso = [
                        f"🔍 Analizando pregunta: '{pregunta}'",
                        "🧠 Identificando conceptos clave y contexto",
                        "📚 Accediendo a conocimiento base sobre el tema",
                        "🔗 Conectando información relevante",
                        "📝 Estructurando respuesta paso a paso",
                        "🔄 Validando coherencia y completitud"
                    ]
                elif modelo_seleccionado.startswith('lmstudio-'):
                    # Para modelos LM Studio, mostrar proceso de conexión
                    pensamientos_proceso = [
                        f"🔧 Conectando con LM Studio ({modelo_seleccionado})",
                        f"📝 Procesando consulta: '{pregunta}'",
                        "⚡ Generando respuesta técnica especializada"
                    ]
                
                try:
                    resultado_chain = simple_chains[modelo_seleccionado].invoke({"pregunta": pregunta})
                    tiempo_fin = time.time()
                    duracion = round(tiempo_fin - tiempo_inicio, 2)
                    duracion_formateada = formatear_duracion(duracion)
                    
                    print(f"✅ Chat simple completado en {duracion_formateada}")
                    
                    # Extraer reasoning_content si está disponible (para modelos de razonamiento)
                    reasoning_content = None
                    respuesta_final = resultado_chain
                    
                    # Si el modelo es DeepSeek con LM Studio, intentar extraer reasoning de la respuesta
                    if modelo_seleccionado == 'lmstudio-deepseek':
                        # Acceder al modelo directamente para obtener la última respuesta
                        modelo_instance = models[modelo_seleccionado]
                        if hasattr(modelo_instance, '_last_response') and modelo_instance._last_response:
                            last_response = modelo_instance._last_response
                            if isinstance(last_response, dict) and "choices" in last_response:
                                choice = last_response["choices"][0]
                                if "message" in choice and "reasoning_content" in choice["message"]:
                                    reasoning_content = choice["message"]["reasoning_content"]
                                    pensamientos_proceso.append("🧠 Proceso de razonamiento capturado del modelo")
                                    print(f"📝 Reasoning content encontrado: {len(reasoning_content)} caracteres")
                    
                    # Si no se encontró reasoning en _last_response, intentar extraerlo del resultado del chain
                    if not reasoning_content and hasattr(resultado_chain, '__dict__'):
                        # Buscar en los metadatos adicionales del mensaje
                        try:
                            # El resultado del chain puede contener información adicional
                            if hasattr(resultado_chain, 'additional_kwargs'):
                                reasoning_content = resultado_chain.additional_kwargs.get('reasoning_content')
                        except:
                            pass
                    
                    # Preparar respuesta con reasoning si está disponible
                    respuesta_data = {
                        'respuesta': respuesta_final,
                        'modo': 'simple',
                        'modelo_usado': modelo_seleccionado,
                        'pensamientos': pensamientos_proceso,
                        'metadata': {
                            'duracion': duracion,
                            'duracion_formateada': duracion_formateada,
                            'timestamp': time.time(),
                            'internetHabilitado': permitir_internet,
                            'iteraciones': 0,
                            'busquedas': 0,
                            'razonamiento_visible': modelo_seleccionado == 'deepseek-r1:8b' or reasoning_content is not None
                        }
                    }
                    
                    # Añadir reasoning_content si está disponible
                    if reasoning_content:
                        respuesta_data['reasoning_content'] = reasoning_content
                        respuesta_data['metadata']['tiene_razonamiento'] = True
                        print(f"📝 Reasoning content capturado ({len(reasoning_content)} caracteres)")
                    
                    return jsonify(respuesta_data)
                
                except Exception as model_error:
                    tiempo_fin = time.time()
                    duracion = round(tiempo_fin - tiempo_inicio, 2)
                    duracion_formateada = formatear_duracion(duracion)
                    
                    error_msg = str(model_error)
                    
                    # Manejo específico para timeout de LM Studio
                    if "ReadTimeout" in error_msg or "timed out" in error_msg:
                        if modelo_seleccionado.startswith('lmstudio-'):
                            return jsonify({
                                'respuesta': f"""⏰ **Timeout del modelo LM Studio**

El modelo {modelo_seleccionado} está tardando más de lo esperado en responder. Esto puede deberse a:

🔧 **Posibles causas:**
• El modelo está procesando una respuesta compleja
• LM Studio está sobrecargado o funcionando lento
• La consulta requiere mucho tiempo de procesamiento

💡 **Sugerencias:**
• Intenta con una pregunta más específica
• Prueba otro modelo disponible
• Verifica que LM Studio esté funcionando correctamente

⚡ **Respuesta rápida para tu pregunta "{pregunta}":**
{generar_respuesta_fallback(pregunta)}

*Tiempo transcurrido: {duracion_formateada}*""",
                                'modo': 'timeout_fallback',
                                'modelo_usado': modelo_seleccionado,
                                'pensamientos': pensamientos_proceso + [
                                    f"⏰ Timeout después de {duracion_formateada}",
                                    "🔄 Generando respuesta de fallback"
                                ],
                                'metadata': {
                                    'duracion': duracion,
                                    'duracion_formateada': duracion_formateada,
                                    'timestamp': time.time(),
                                    'internetHabilitado': permitir_internet,
                                    'error': 'timeout',
                                    'iteraciones': 0,
                                    'busquedas': 0
                                }
                            })
                    
                    # Para otros errores, propagar el error
                    raise model_error
            else:
                print(f"❌ DEBUG: Chain no encontrada para {modelo_seleccionado}")
                return jsonify({'error': f'Modelo {modelo_seleccionado} no disponible'}), 400
            
    except Exception as e:
        print(f"❌ DEBUG: Error en función chat: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al procesar la pregunta: {str(e)}'}), 500

@app.route('/ejemplo-agente', methods=['POST'])
def ejemplo_agente() -> Union[Response, Tuple[Response, int]]:
    """Endpoint específico para demostrar capacidades del agente"""
    try:
        ejemplos = [
            "¿Cuáles son las últimas noticias sobre inteligencia artificial?",
            "¿Cuál es el precio actual del Bitcoin?",
            "¿Quién ganó la final de la Champions League más reciente?",
            "¿Cuáles son las últimas noticias tecnológicas?"
        ]
        
        pregunta_ejemplo = ejemplos[0]  # Tomar el primer ejemplo
        
        # Usar el primer modelo y agente disponible
        modelo_disponible = available_models[0] if available_models else None
        
        if modelo_disponible and modelo_disponible in agents and agents[modelo_disponible] is not None:
            # Usar el agente para la demo
            respuesta = agents[modelo_disponible].invoke({"input": pregunta_ejemplo})
            return jsonify({
                'pregunta': pregunta_ejemplo,
                'respuesta': respuesta['output'],
                'modo': 'agente',
                'modelo_usado': modelo_disponible
            })
        elif modelo_disponible and modelo_disponible in simple_chains:
            # Fallback: usar chat simple si el agente no está disponible
            respuesta_simple = simple_chains[modelo_disponible].invoke({"pregunta": pregunta_ejemplo})
            return jsonify({
                'pregunta': pregunta_ejemplo,
                'respuesta': f"[Modo Simple - Agente no disponible] {respuesta_simple}",
                'modo': 'simple',
                'modelo_usado': modelo_disponible
            })
        else:
            return jsonify({'error': 'No hay modelos disponibles para la demo'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Error en ejemplo de agente: {str(e)}'}), 500

@app.route('/busqueda-rapida', methods=['POST'])
def busqueda_rapida() -> Union[Response, Tuple[Response, int]]:
    """Endpoint optimizado para búsquedas web rápidas"""
    try:
        data = request.get_json()
        pregunta = data.get('pregunta', '')
        modelo_seleccionado = data.get('modelo', available_models[0] if available_models else 'gemini-1.5-flash')
        
        if not pregunta:
            return jsonify({'error': 'No se proporcionó ninguna pregunta'}), 400
        
        # Búsqueda directa con DuckDuckGo sin agente complejo
        search_tool = DuckDuckGoSearchRun()
        
        # Mejorar términos de búsqueda según el tipo de pregunta
        def mejorar_consulta_busqueda(pregunta_original):
            pregunta_lower = pregunta_original.lower()
            if 'precio' in pregunta_lower and 'bitcoin' in pregunta_lower:
                return [
                    "Bitcoin price USD current today",
                    "precio Bitcoin actual dólares",
                    "BTC price now current value"
                ]
            elif 'noticias' in pregunta_lower:
                return [
                    f"noticias {pregunta_original} hoy",
                    f"latest news {pregunta_original} today",
                    f"breaking news {pregunta_original} 2025"
                ]
            elif 'openai' in pregunta_lower:
                return [
                    "OpenAI news latest updates",
                    "noticias OpenAI ChatGPT",
                    "OpenAI developments 2025"
                ]
            elif 'champions' in pregunta_lower or 'deportes' in pregunta_lower:
                return [
                    "Champions League final winner",
                    "latest sports news football",
                    "resultados deportivos recientes"
                ]
            elif 'petróleo' in pregunta_lower or 'oil' in pregunta_lower:
                return [
                    "oil price current USD barrel",
                    "precio petróleo actual",
                    "crude oil price today"
                ]
            
            # Búsqueda genérica mejorada
            return [pregunta_original, f"{pregunta_original} today", f"{pregunta_original} 2025"]
        
        try:
            consultas = mejorar_consulta_busqueda(pregunta)
            search_results = None
            consulta_exitosa = None
            
            # Intentar múltiples consultas hasta obtener resultados útiles
            for consulta in consultas:
                try:
                    print(f"🔍 Buscando: {consulta}")
                    resultado = search_tool.invoke(consulta)
                    
                    # Verificar si el resultado tiene contenido útil
                    if resultado and len(resultado.strip()) > 50:
                        # Verificaciones adicionales para detectar resultados irrelevantes
                        resultado_lower = resultado.lower()
                        palabras_irrelevantes = [
                            "no se encontraron resultados",
                            "página no encontrada", 
                            "error 404",
                            "no hay resultados",
                            "try again later"
                        ]
                        
                        # Verificar que no tenga palabras irrelevantes
                        es_irrelevante = any(palabra in resultado_lower for palabra in palabras_irrelevantes)
                        
                        if not es_irrelevante:
                            search_results = resultado
                            consulta_exitosa = consulta
                            print(f"✅ Búsqueda exitosa con: {consulta}")
                            break
                        else:
                            print(f"⚠️ Resultado irrelevante con: {consulta}")
                
                except Exception as e:
                    print(f"⚠️ Error en búsqueda '{consulta}': {e}")
                    continue
            
            if not search_results:
                # Fallback inteligente para cualquier consulta
                modelo = get_model(modelo_seleccionado)
                if modelo and modelo_seleccionado in simple_chains:
                    prompt_fallback = f"""
                    No pude obtener información actualizada de internet sobre "{pregunta}". 
                    
                    Como experto asistente, proporciona una respuesta útil que incluya:
                    
                    1. Información general relevante sobre el tema consultado
                    2. Recomendaciones específicas para obtener información actual:
                       - Sitios web especializados
                       - Aplicaciones móviles relevantes
                       - Búsquedas específicas en Google
                    3. Contexto útil sobre el tema
                    4. Consejos prácticos para encontrar la información
                    
                    Sé específico y útil, adaptándote al tipo de consulta realizada.
                    """
                    
                    respuesta_fallback = simple_chains[modelo_seleccionado].invoke({"pregunta": prompt_fallback})
                    
                    return jsonify({
                        'respuesta': f"🌐 **Búsqueda web limitada - Respuesta inteligente:**\n\n{respuesta_fallback}",
                        'modo': 'busqueda_inteligente_fallback',
                        'modelo_usado': modelo_seleccionado,
                        'fuente': 'Asistente inteligente'
                    })
                else:
                    return jsonify({
                        'respuesta': "❌ No pude obtener información actualizada desde internet en este momento. Te recomiendo:\n\n1. Consultar sitios web especializados\n2. Usar aplicaciones móviles relevantes\n3. Buscar en Google con términos específicos\n4. Intentar la búsqueda más tarde",
                        'modo': 'busqueda_fallback',
                        'modelo_usado': modelo_seleccionado,
                        'fuente': 'Error en búsqueda'
                    })
            
            # Usar el modelo para resumir y formatear los resultados
            modelo = get_model(modelo_seleccionado)
            if modelo and modelo_seleccionado in simple_chains:
                prompt_busqueda = f"""
                INSTRUCCIONES ESPECÍFICAS: Eres un experto asistente que debe extraer y presentar información útil de resultados de búsqueda web.

                PREGUNTA DEL USUARIO: "{pregunta}"
                
                RESULTADOS DE BÚSQUEDA OBTENIDOS:
                {search_results}

                TAREAS OBLIGATORIAS:
                1. ANALIZA cuidadosamente los resultados de búsqueda
                2. EXTRAE cualquier información relevante disponible (precios, noticias, datos específicos)
                3. Si encuentras datos parciales o relacionados, ÚSALOS y sé transparente sobre las limitaciones
                4. COMPLEMENTA con información contextual útil y recomendaciones
                5. NUNCA digas simplemente "no hay información" - siempre proporciona valor

                ESTRUCTURA DE RESPUESTA:
                - Información encontrada (aunque sea limitada)
                - Contexto adicional útil
                - Recomendaciones para información más completa
                - Consejos prácticos

                IMPORTANTE: Sé proactivo y útil. Si los resultados mencionan sitios web o aplicaciones, incorpóralos como recomendaciones adicionales.
                
                RESPUESTA EN ESPAÑOL:
                """
                
                respuesta = simple_chains[modelo_seleccionado].invoke({"pregunta": prompt_busqueda})
                
                return jsonify({
                    'respuesta': f"🔍 **Búsqueda realizada con:** {consulta_exitosa}\n\n{respuesta}",
                    'modo': 'busqueda_rapida',
                    'modelo_usado': modelo_seleccionado,
                    'fuente': 'DuckDuckGo'
                })
            else:
                return jsonify({
                    'respuesta': f"**Resultados de búsqueda directa:**\n\n{search_results}",
                    'modo': 'busqueda_directa',
                    'modelo_usado': 'ninguno',
                    'fuente': 'DuckDuckGo'
                })
                
        except Exception as search_error:
            return jsonify({'error': f'Error en búsqueda: {str(search_error)}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Error en búsqueda rápida: {str(e)}'}), 500

@app.route('/clima-directo', methods=['POST'])
def clima_directo() -> Union[Response, Tuple[Response, int]]:
    """Endpoint específico para consultas de clima con respuesta directa inteligente"""
    try:
        data = request.get_json()
        pregunta = data.get('pregunta', '')
        modelo_seleccionado = data.get('modelo', available_models[0] if available_models else 'gemini-1.5-flash')
        ciudad = data.get('ciudad', 'Quito')
        
        if not pregunta:
            return jsonify({'error': 'No se proporcionó ninguna pregunta'}), 400
        
        # Usar el modelo para generar una respuesta útil sobre clima
        modelo = get_model(modelo_seleccionado)
        if modelo and modelo_seleccionado in simple_chains:
            prompt_clima = f"""
            El usuario pregunta sobre el clima en {ciudad}. Aunque no puedo acceder a datos meteorológicos en tiempo real desde mi entrenamiento, puedo proporcionar información útil y recomendaciones prácticas.

            Pregunta del usuario: "{pregunta}"

            Proporciona una respuesta útil que incluya:
            1. Reconocimiento de la limitación para datos en tiempo real
            2. Información general sobre el clima típico de {ciudad} según la época del año (es julio 2025)
            3. Recomendaciones específicas para obtener información actual:
               - Sitios web específicos (weather.com, accuweather.com, clima.com)
               - Aplicaciones móviles recomendadas
               - Búsquedas específicas en Google
            4. Consejos prácticos para el clima típico de la región en esta época

            Sé útil, específico y práctico en tu respuesta.
            """
            
            respuesta = simple_chains[modelo_seleccionado].invoke({"pregunta": prompt_clima})
            
            return jsonify({
                'respuesta': f"🌤️ **Información sobre clima en {ciudad}**\n\n{respuesta}",
                'modo': 'clima_directo',
                'modelo_usado': modelo_seleccionado,
                'fuente': 'Respuesta inteligente'
            })
        else:
            return jsonify({
                'respuesta': f"Para obtener el clima actual en {ciudad}, te recomiendo consultar:\n• weather.com\n• accuweather.com\n• Google Weather\n• Apps móviles de clima",
                'modo': 'clima_basico',
                'modelo_usado': 'ninguno',
                'fuente': 'Recomendaciones estáticas'
            })
            
    except Exception as e:
        return jsonify({'error': f'Error en consulta de clima: {str(e)}'}), 500

@app.route('/clima-actual', methods=['POST'])
def clima_actual() -> Union[Response, Tuple[Response, int]]:
    """Endpoint rápido y optimizado para consultas de clima actual"""
    try:
        data = request.get_json()
        pregunta = data.get('pregunta', '')
        modelo_seleccionado = data.get('modelo', available_models[0] if available_models else 'llama3')
        
        if not pregunta:
            return jsonify({'error': 'No se proporcionó ninguna pregunta'}), 400
        
        # Extraer ciudad de la pregunta
        ciudad = 'Quito'  # Default
        pregunta_lower = pregunta.lower()
        
        if 'quito' in pregunta_lower:
            ciudad = 'Quito'
        elif 'guayaquil' in pregunta_lower:
            ciudad = 'Guayaquil'
        elif 'cuenca' in pregunta_lower:
            ciudad = 'Cuenca'
        elif 'new york' in pregunta_lower or 'nueva york' in pregunta_lower:
            ciudad = 'New York'
        elif 'madrid' in pregunta_lower:
            ciudad = 'Madrid'
        elif 'london' in pregunta_lower or 'londres' in pregunta_lower:
            ciudad = 'London'
        
        print(f"🌤️ Consulta rápida de clima para {ciudad}")
        tiempo_inicio = time.time()
        
        # Obtener datos del clima
        clima_data = obtener_clima_api(ciudad)
        
        if clima_data['success']:
            data_clima = clima_data['data']
            
            # Si tenemos un modelo disponible, usarlo para formatear la respuesta
            if modelo_seleccionado in simple_chains:
                prompt_clima = f"""El usuario pregunta: "{pregunta}"

Datos meteorológicos ACTUALES para {ciudad}:
🌡️ Temperatura: {data_clima['temperatura']}°C
🌡️ Sensación térmica: {data_clima['sensacion_termica']}°C
☁️ Condiciones: {data_clima['descripcion']}
💧 Humedad: {data_clima['humedad']}%
💨 Viento: {data_clima['velocidad_viento']} km/h hacia {data_clima['direccion_viento']}
🕐 Última actualización: {data_clima['hora_consulta']}

Responde de manera natural y útil con esta información actualizada."""
                
                respuesta_formateada = simple_chains[modelo_seleccionado].invoke({"pregunta": prompt_clima})
            else:
                # Respuesta básica sin modelo
                respuesta_formateada = f"""🌤️ **Clima actual en {ciudad}**

📊 **Condiciones actuales:**
• **Temperatura:** {data_clima['temperatura']}°C
• **Sensación térmica:** {data_clima['sensacion_termica']}°C
• **Condiciones:** {data_clima['descripcion']}
• **Humedad:** {data_clima['humedad']}%
• **Viento:** {data_clima['velocidad_viento']} km/h ({data_clima['direccion_viento']})
• **Última actualización:** {data_clima['hora_consulta']}

*Datos obtenidos de API meteorológica en tiempo real*"""
            
            tiempo_fin = time.time()
            duracion = round(tiempo_fin - tiempo_inicio, 2)
            duracion_formateada = formatear_duracion(duracion)
            
            return jsonify({
                'respuesta': respuesta_formateada,
                'modo': 'clima_actual',
                'modelo_usado': modelo_seleccionado,
                'pensamientos': [
                    f"🌤️ Consultando clima actual en {ciudad}",
                    "🔍 Conectando con API meteorológica wttr.in",
                    f"📊 Datos obtenidos: {data_clima['temperatura']}°C, {data_clima['descripcion']}",
                    "✅ Respuesta generada con datos en tiempo real"
                ],
                'metadata': {
                    'duracion': duracion,
                    'duracion_formateada': duracion_formateada,
                    'timestamp': time.time(),
                    'internetHabilitado': True,
                    'iteraciones': 1,
                    'busquedas': 1,
                    'ciudad': ciudad,
                    'fuente_datos': 'wttr.in',
                    'tipo_consulta': 'clima_rapido'
                }
            })
        else:
            return jsonify({
                'respuesta': f"❌ No pude obtener el clima actual de {ciudad}.\n\nError: {clima_data['error']}\n\n🌤️ **Recomendaciones:**\n• Consulta weather.com\n• Usa Google Weather\n• Apps: AccuWeather, Weather Underground",
                'modo': 'clima_error',
                'modelo_usado': modelo_seleccionado,
                'metadata': {
                    'internetHabilitado': True,
                    'error': clima_data['error'],
                    'ciudad': ciudad
                }
            })
            
    except Exception as e:
        return jsonify({'error': f'Error en consulta de clima: {str(e)}'}), 500

@app.route('/clima-api', methods=['POST'])
def clima_api() -> Union[Response, Tuple[Response, int]]:
    """Endpoint para obtener clima usando API externa gratuita"""
    try:
        data = request.get_json()
        pregunta = data.get('pregunta', '')
        modelo_seleccionado = data.get('modelo', available_models[0] if available_models else 'gemini-1.5-flash')
        ciudad = data.get('ciudad', 'Quito')
        
        # Extraer ciudad de la pregunta si está presente
        if 'quito' in pregunta.lower():
            ciudad = 'Quito'
        elif 'guayaquil' in pregunta.lower():
            ciudad = 'Guayaquil'
        elif 'cuenca' in pregunta.lower():
            ciudad = 'Cuenca'
        
        print(f"🌤️ Solicitando clima para {ciudad}...")
        
        # Obtener clima usando API
        clima_data = obtener_clima_api(ciudad)
        
        # Formatear respuesta
        respuesta_formateada = formatear_respuesta_clima(clima_data, modelo_seleccionado)
        
        return jsonify({
            'respuesta': respuesta_formateada,
            'modo': 'clima_api',
            'modelo_usado': modelo_seleccionado,
            'fuente': 'wttr.in API',
            'ciudad': ciudad,
            'success': clima_data['success']
        })
        
    except Exception as e:
        return jsonify({'error': f'Error en consulta de clima API: {str(e)}'}), 500

@app.route('/agente-general', methods=['POST'])
def agente_general() -> Union[Response, Tuple[Response, int]]:
    """Endpoint para demostraciones del agente con búsquedas generales"""
    try:
        data = request.get_json()
        tipo_demo = data.get('tipo', 'clima')  # clima, noticias, bitcoin, deportes
        modelo_seleccionado = data.get('modelo', available_models[0] if available_models else 'gemini-1.5-flash')
        
        # Preguntas predefinidas para diferentes tipos de demos
        demos = {
            'noticias': "¿Cuáles son las últimas noticias sobre inteligencia artificial?",
            'bitcoin': "¿Cuál es el precio actual del Bitcoin en USD?",
            'deportes': "¿Quién ganó la final de la Champions League más reciente?",
            'tech': "¿Cuáles son las últimas noticias sobre OpenAI?",
            'economia': "¿Cuál es el precio actual del petróleo?",
            'general': "¿Cuáles son las noticias más importantes de hoy?"
        }
        
        pregunta = demos.get(tipo_demo, demos['noticias'])
        
        # Usar el agente mejorado
        if modelo_seleccionado in agents and agents[modelo_seleccionado] is not None:
            try:
                print(f"🤖 Ejecutando demo '{tipo_demo}' con {modelo_seleccionado}")
                tiempo_inicio = time.time()
                respuesta_completa = agents[modelo_seleccionado].invoke({"input": pregunta})
                tiempo_fin = time.time()
                duracion = round(tiempo_fin - tiempo_inicio, 2)
                
                # Extraer pasos intermedios si están disponibles
                pasos_intermedios = []
                busquedas_count = 0
                if 'intermediate_steps' in respuesta_completa:
                    for paso in respuesta_completa['intermediate_steps']:
                        if len(paso) >= 2:
                            accion = paso[0]
                            observacion = paso[1]
                            
                            # Contar búsquedas
                            if accion.tool in ['web_search', 'duckduckgo_search']:
                                busquedas_count += 1
                            
                            pasos_intermedios.append({
                                'action': accion.tool,
                                'action_input': accion.tool_input,
                                'observation': observacion[:300] + '...' if len(observacion) > 300 else observacion
                            })
                
                return jsonify({
                    'pregunta': pregunta,
                    'respuesta': respuesta_completa['output'],
                    'modo': 'agente_general',
                    'modelo_usado': modelo_seleccionado,
                    'tipo_demo': tipo_demo,
                    'pasos_intermedios': pasos_intermedios,
                    'metadata': {
                        'duracion': duracion,
                        'iteraciones': len(pasos_intermedios),
                        'busquedas': busquedas_count,
                        'timestamp': time.time()
                    }
                })
                
            except Exception as e:
                error_msg = str(e)
                print(f"Error en agente general {modelo_seleccionado}: {error_msg}")
                
                # Fallback inteligente
                if modelo_seleccionado in simple_chains:
                    respuesta_fallback = simple_chains[modelo_seleccionado].invoke({
                        "pregunta": f"Aunque no puedo buscar en internet en este momento, responde de la mejor manera posible: {pregunta}"
                    })
                    
                    return jsonify({
                        'pregunta': pregunta,
                        'respuesta': f"⚠️ Agente no disponible. Respuesta básica:\n\n{respuesta_fallback}",
                        'modo': 'fallback_general',
                        'modelo_usado': modelo_seleccionado,
                        'tipo_demo': tipo_demo
                    })
        
        return jsonify({'error': 'Agente no disponible'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Error en agente general: {str(e)}'}), 500

@app.route('/api/models/status', methods=['GET'])
def get_models_status():
    """Obtener el estado actual de todos los modelos"""
    try:
        import requests
        
        model_status = {
            'ollama': {
                'available': False,
                'models': []
            },
            'lmstudio': {
                'available': False,
                'models': []
            },
            'gemini': {
                'available': bool(Config.GOOGLE_API_KEY)
            }
        }
        
        # Verificar Ollama
        try:
            response = requests.get(f"{Config.OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                model_status['ollama']['available'] = True
                ollama_models_data = response.json().get('models', [])
                model_status['ollama']['models'] = [
                    {
                        'name': model['name'],
                        'size': model.get('size', 'Unknown'),
                        'modified': model.get('modified_at', 'Unknown')
                    }
                    for model in ollama_models_data
                ]
        except:
            pass
            
        # Verificar LM Studio
        try:
            response = requests.get(f"{Config.LMSTUDIO_BASE_URL}/v1/models", timeout=5)
            if response.status_code == 200:
                model_status['lmstudio']['available'] = True
                lm_models_data = response.json().get('data', [])
                model_status['lmstudio']['models'] = [
                    {
                        'id': model['id'],
                        'object': model.get('object', 'model')
                    }
                    for model in lm_models_data
                ]
        except:
            pass
            
        return jsonify(model_status)
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener estado de modelos: {str(e)}'}), 500

@app.route('/api/models/ollama/<action>', methods=['POST'])
def control_ollama(action):
    """Controlar modelos de Ollama"""
    try:
        import subprocess
        
        if action == 'start':
            # Intentar iniciar Ollama serve en background
            try:
                subprocess.Popen(
                    ['ollama', 'serve'],
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
                return jsonify({'message': 'Ollama iniciado en background', 'status': 'started'})
            except Exception as e:
                return jsonify({'error': f'Error al iniciar Ollama: {str(e)}'}), 500
                
        elif action == 'stop':
            # En Windows, intentar terminar el proceso ollama
            try:
                if os.name == 'nt':
                    subprocess.run(['taskkill', '/F', '/IM', 'ollama.exe'], check=False)
                else:
                    subprocess.run(['pkill', 'ollama'], check=False)
                return jsonify({'message': 'Ollama detenido', 'status': 'stopped'})
            except Exception as e:
                return jsonify({'error': f'Error al detener Ollama: {str(e)}'}), 500
                
        else:
            return jsonify({'error': 'Acción no válida. Use start o stop'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Error en control de Ollama: {str(e)}'}), 500

@app.route('/api/models/lmstudio/<action>', methods=['POST'])
def control_lmstudio(action):
    """Controlar LM Studio"""
    try:
        if action == 'start':
            # Mostrar mensaje de instrucciones para LM Studio
            return jsonify({
                'message': 'Para iniciar LM Studio, abra la aplicación manualmente desde el escritorio o menú inicio.',
                'instructions': [
                    '1. Abrir LM Studio desde el escritorio',
                    '2. Cargar un modelo desde la pestaña "My Models"',
                    '3. Asegurarse de que el servidor local esté en puerto 1234'
                ],
                'status': 'manual_start_required'
            })
            
        elif action == 'stop':
            return jsonify({
                'message': 'Para detener LM Studio, cierre la aplicación manualmente.',
                'instructions': [
                    '1. Hacer clic en el botón "Stop" en LM Studio',
                    '2. Cerrar la aplicación LM Studio'
                ],
                'status': 'manual_stop_required'
            })
            
        else:
            return jsonify({'error': 'Acción no válida. Use start o stop'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Error en control de LM Studio: {str(e)}'}), 500

@app.route('/api/models/ollama/individual/<model_name>/<action>', methods=['POST'])
def control_ollama_individual(model_name, action):
    """Controlar modelos individuales de Ollama"""
    try:
        import subprocess
        import requests
        
        if action == 'run':
            # Ejecutar modelo específico
            try:
                # Primero verificar si Ollama está ejecutándose
                try:
                    requests.get(f"{Config.OLLAMA_BASE_URL}/api/tags", timeout=3)
                except:
                    # Si Ollama no está ejecutándose, iniciarlo primero
                    subprocess.Popen(
                        ['ollama', 'serve'],
                        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                    )
                    # Esperar un momento para que se inicie
                    import time
                    time.sleep(3)
                
                # Ejecutar el modelo en background
                subprocess.Popen(
                    ['ollama', 'run', model_name],
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
                
                return jsonify({
                    'message': f'Modelo {model_name} cargado exitosamente',
                    'model': model_name,
                    'status': 'running'
                })
            except Exception as e:
                return jsonify({'error': f'Error al ejecutar modelo {model_name}: {str(e)}'}), 500
                
        elif action == 'stop':
            # Detener modelo específico
            try:
                subprocess.run(['ollama', 'stop', model_name], check=True, timeout=10)
                return jsonify({
                    'message': f'Modelo {model_name} detenido exitosamente',
                    'model': model_name,
                    'status': 'stopped'
                })
            except subprocess.CalledProcessError as e:
                return jsonify({'error': f'Error al detener modelo {model_name}: {str(e)}'}), 500
            except subprocess.TimeoutExpired:
                return jsonify({'error': f'Timeout al detener modelo {model_name}'}), 500
                
        else:
            return jsonify({'error': 'Acción no válida. Use run o stop'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Error en control individual de Ollama: {str(e)}'}), 500

@app.route('/api/models/ollama/running', methods=['GET'])
def get_running_ollama_models():
    """Obtener modelos de Ollama que están ejecutándose actualmente"""
    try:
        import requests
        
        # Verificar si Ollama está ejecutándose
        try:
            # Intentar obtener información de modelos en ejecución
            response = requests.get(f"{Config.OLLAMA_BASE_URL}/api/ps", timeout=5)
            if response.status_code == 200:
                running_models = response.json().get('models', [])
                
                # También obtener todos los modelos disponibles
                tags_response = requests.get(f"{Config.OLLAMA_BASE_URL}/api/tags", timeout=5)
                all_models = []
                if tags_response.status_code == 200:
                    all_models = tags_response.json().get('models', [])
                
                # Crear estructura de respuesta con estado de cada modelo
                models_status = []
                for model in all_models:
                    model_name = model['name']
                    is_running = any(rm['name'] == model_name for rm in running_models)
                    
                    model_info = {
                        'name': model_name,
                        'is_running': is_running,
                        'size': model.get('size', 'Unknown'),
                        'modified': model.get('modified_at', 'Unknown'),
                        'digest': model.get('digest', '')[:12] if model.get('digest') else ''
                    }
                    
                    # Si está ejecutándose, añadir información adicional
                    if is_running:
                        running_info = next((rm for rm in running_models if rm['name'] == model_name), None)
                        if running_info:
                            model_info.update({
                                'vram_usage': running_info.get('size_vram', 0),
                                'expires_at': running_info.get('expires_at', ''),
                            })
                    
                    models_status.append(model_info)
                
                return jsonify({
                    'ollama_available': True,
                    'models': models_status,
                    'running_count': len(running_models)
                })
            else:
                return jsonify({
                    'ollama_available': False,
                    'models': [],
                    'running_count': 0
                })
        except:
            return jsonify({
                'ollama_available': False,
                'models': [],
                'running_count': 0
            })
            
    except Exception as e:
        return jsonify({'error': f'Error al obtener modelos en ejecución: {str(e)}'}), 500

@app.route('/api/ollama/console', methods=['POST'])
def ollama_console_command():
    """Ejecutar comandos de consola Ollama"""
    try:
        import subprocess
        import json
        
        data = request.get_json()
        command = data.get('command', '').strip()
        
        if not command:
            return jsonify({'error': 'Comando vacío'}), 400
        
        # Lista de comandos permitidos por seguridad
        allowed_commands = ['ps', 'list', 'serve', 'run', 'stop', 'show', 'create', 'rm', 'cp', 'push', 'pull']
        
        # Parsear el comando
        cmd_parts = command.split()
        if not cmd_parts or cmd_parts[0] not in allowed_commands:
            return jsonify({
                'error': f'Comando no permitido. Comandos disponibles: {", ".join(allowed_commands)}',
                'output': '',
                'success': False
            }), 400
        
        # Construir comando completo
        full_command = ['ollama'] + cmd_parts
        
        try:
            # Ejecutar comando con timeout
            if cmd_parts[0] == 'serve':
                # Para serve, iniciar en background
                process = subprocess.Popen(
                    full_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
                return jsonify({
                    'command': command,
                    'output': 'Ollama serve iniciado en background. Verifica el estado con "ollama ps".',
                    'success': True,
                    'background': True
                })
            else:
                # Para otros comandos, ejecutar y obtener output
                result = subprocess.run(
                    full_command,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False
                )
                
                # Combinar stdout y stderr
                output = ''
                if result.stdout:
                    output += result.stdout
                if result.stderr:
                    output += '\n' + result.stderr if output else result.stderr
                
                if not output:
                    output = f'Comando "{command}" ejecutado exitosamente (sin output)'
                
                return jsonify({
                    'command': command,
                    'output': output.strip(),
                    'success': result.returncode == 0,
                    'return_code': result.returncode
                })
                
        except subprocess.TimeoutExpired:
            return jsonify({
                'command': command,
                'output': 'Error: Comando excedió el tiempo límite (30s)',
                'success': False,
                'timeout': True
            }), 408
            
        except subprocess.CalledProcessError as e:
            return jsonify({
                'command': command,
                'output': f'Error ejecutando comando: {e.stderr if e.stderr else str(e)}',
                'success': False,
                'error': str(e)
            }), 500
            
    except Exception as e:
        return jsonify({
            'error': f'Error interno del servidor: {str(e)}',
            'output': '',
            'success': False
        }), 500

@app.route('/api/ollama/models-for-actions', methods=['GET'])
def get_ollama_models_for_actions():
    """Obtener lista de modelos para acciones (run/stop)"""
    try:
        import requests
        import subprocess
        
        # Intentar obtener modelos via API REST
        try:
            response = requests.get(f"{Config.OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                return jsonify({
                    'models': models,
                    'source': 'api',
                    'available': True
                })
        except:
            pass
        
        # Si falla la API, intentar con comando
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                models = []
                for line in lines:
                    if line.strip():
                        # Extraer nombre del modelo (primera columna)
                        parts = line.split()
                        if parts:
                            models.append(parts[0])
                
                return jsonify({
                    'models': models,
                    'source': 'command',
                    'available': True
                })
        except:
            pass
        
        return jsonify({
            'models': [],
            'source': 'none',
            'available': False,
            'error': 'No se pudo obtener lista de modelos'
        })
        
    except Exception as e:
        return jsonify({
            'models': [],
            'available': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🤖 Iniciando aplicación de IA con Agentes...")
    print(f"🧠 Modelos disponibles: {', '.join(available_models)}")
    print("🔍 Herramientas: Búsqueda web avanzada")
    print("🌐 Servidor: http://127.0.0.1:5000")
    print("🚀 Aplicación de consultas generales lista!")
    app.run(debug=True, host='127.0.0.1', port=5000)
