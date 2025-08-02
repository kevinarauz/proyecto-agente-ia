import os
import json
import requests
import time
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
    ('deepseek-r1:8b', 'DeepSeek R1 8B'),
    ('phi3', 'Microsoft Phi-3'),
    ('gemma:2b', 'Google Gemma 2B')
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

# Verificar que al menos un modelo esté disponible
available_models = [k for k, v in models.items() if v is not None]
if not available_models:
    print("❌ Error: No hay modelos disponibles")
    print("💡 Asegúrate de que:")
    print("   - Ollama esté ejecutándose con llama3 instalado, O")
    print("   - Tengas GOOGLE_API_KEY configurada en .env")
    exit(1)

print(f"🎯 Modelos disponibles: {', '.join(available_models)}")

# Función para obtener el modelo según la selección
def get_model(model_name: str) -> Optional[Union[ChatOllama, ChatGoogleGenerativeAI]]:
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
    if any(palabra in query.lower() for palabra in ['clima', 'weather', 'temperatura', 'temperature']):
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
tools = [herramienta_busqueda, DuckDuckGoSearchRun()]

# Prompt optimizado para búsquedas generales
agent_prompt = PromptTemplate.from_template("""
Eres un asistente de IA especializado en proporcionar respuestas precisas y actuales. Tienes acceso a herramientas de búsqueda web.

Herramientas disponibles:
{tools}

REGLAS IMPORTANTES: 
1. SIEMPRE usa búsqueda web para: noticias recientes, precios actuales, eventos deportivos, información actualizada
2. NUNCA digas que no tienes acceso a información en tiempo real - ¡SÍ LO TIENES!
3. Si una búsqueda falla, intenta con términos diferentes
4. Proporciona respuestas útiles basadas en los resultados obtenidos
5. Adapta tu búsqueda según el tipo de información solicitada

Formato OBLIGATORIO:
Question: la pregunta que debes responder
Thought: necesito buscar información actual sobre [tema específico]
Action: duckduckgo_search
Action Input: [términos de búsqueda específicos y efectivos]
Observation: [resultados de la búsqueda]
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
                max_iterations=6,  # Incrementado para más análisis
                max_execution_time=30,  # Incrementado para análisis detallado
                handle_parsing_errors=True,
                return_intermediate_steps=True,
                early_stopping_method="generate"  # Permite generar respuesta parcial si llega al límite
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
        
        if model_name in ollama_models_list:
            # Para modelos de Ollama, configurar directamente sin bind (temperatura no es compatible)
            simple_chains[model_name] = model_prompt | model_instance | StrOutputParser()
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
        
        necesita_busqueda_web = any(palabra in pregunta.lower() for palabra in palabras_actualidad)
        
        if necesita_busqueda_web and permitir_internet and modo == 'simple':
            print(f"🔄 Detectada consulta que requiere información actual, cambiando a modo agente")
            modo = 'agente'

        # Forzar modo simple si internet está deshabilitado y se intenta usar modos que requieren web
        if not permitir_internet and modo in ['agente', 'busqueda_rapida']:
            print(f"🔍 DEBUG: Forzando modo simple porque internet está deshabilitado")
            modo = 'simple'

        if modo == 'agente' and permitir_internet and modelo_seleccionado in agents and agents[modelo_seleccionado] is not None:
            # Verificar si es una consulta de clima para usar endpoint especializado
            if any(palabra in pregunta.lower() for palabra in ['clima', 'weather', 'temperatura', 'temp']):
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
            try:
                tiempo_inicio = time.time()
                print(f"🤖 Iniciando agente {modelo_seleccionado} para: {pregunta[:50]}...")
                
                # Ejecutar el agente
                respuesta_completa = agents[modelo_seleccionado].invoke({"input": pregunta})
                tiempo_fin = time.time()
                duracion = round(tiempo_fin - tiempo_inicio, 2)
                duracion_formateada = formatear_duracion(duracion)
                
                print(f"✅ Agente completado en {duracion_formateada}")
                
                # Extraer pasos intermedios si están disponibles
                pasos_intermedios = []
                busquedas_count = 0
                pensamientos = []
                
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
                            
                            # Agregar pensamiento formateado
                            if hasattr(accion, 'tool'):
                                pensamientos.append(f"💭 Paso {i+1}: Usando herramienta '{accion.tool}' con entrada: '{accion.tool_input}'")
                                pensamientos.append(f"📋 Resultado: {observacion[:200]}..." if len(str(observacion)) > 200 else f"📋 Resultado: {observacion}")
                else:
                    print("ℹ️ No se encontraron pasos intermedios")
                    # Para consultas simples, agregar un pensamiento básico
                    pensamientos.append("💭 Procesando consulta directamente sin necesidad de búsquedas web")
                
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
                
                respuesta = simple_chains[modelo_seleccionado].invoke({"pregunta": pregunta})
                tiempo_fin = time.time()
                duracion = round(tiempo_fin - tiempo_inicio, 2)
                duracion_formateada = formatear_duracion(duracion)
                
                print(f"✅ Chat simple completado en {duracion_formateada}")
                
                return jsonify({
                    'respuesta': respuesta,
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
                        'razonamiento_visible': modelo_seleccionado == 'deepseek-r1:8b'
                    }
                })
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

if __name__ == '__main__':
    print("🤖 Iniciando aplicación de IA con Agentes...")
    print(f"🧠 Modelos disponibles: {', '.join(available_models)}")
    print("🔍 Herramientas: Búsqueda web avanzada")
    print("🌐 Servidor: http://127.0.0.1:5000")
    print("🚀 Aplicación de consultas generales lista!")
    app.run(debug=True, host='127.0.0.1', port=5000)
