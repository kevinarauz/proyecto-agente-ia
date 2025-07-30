import os
import json
import requests
from typing import Optional, Union, Tuple
from flask import Flask, render_template, request, jsonify, Response
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOllama
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

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

print("🤖 Configurando modelos de IA...")

# Configurar ambos modelos de IA
models = {}

# Configurar Llama3 (local)
try:
    models['llama3'] = ChatOllama(
        model="llama3",
        temperature=Config.DEFAULT_TEMPERATURE
    )
    print("✅ Llama3 configurado correctamente")
except Exception as e:
    print(f"⚠️ Llama3 no disponible: {e}")
    models['llama3'] = None

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
    
    # Método 2: API de búsqueda alternativa (usando scraping básico)
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
                max_iterations=4,  # Reducido porque ahora es más eficiente
                max_execution_time=20,  # Reducido
                handle_parsing_errors=True,
                return_intermediate_steps=True
            )
            print(f"✅ Agente {model_name} creado con herramientas avanzadas")
        except Exception as e:
            print(f"⚠️ Error creando agente {model_name}: {e}")
            agents[model_name] = None

# También configurar un chat simple sin agente para preguntas básicas
simple_chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente útil y amigable. Responde de manera clara y concisa en español. Siempre mantén un tono profesional pero cercano."),
    ("user", "{pregunta}")
])

simple_chains = {}
for model_name, model_instance in models.items():
    if model_instance is not None:
        simple_chains[model_name] = simple_chat_prompt | model_instance | StrOutputParser()
        print(f"✅ Chat simple {model_name} configurado")

@app.route('/')
def index() -> str:
    return render_template('index.html', modelos_disponibles=available_models)

@app.route('/chat', methods=['POST'])
def chat() -> Union[Response, Tuple[Response, int]]:
    try:
        data = request.get_json()
        pregunta = data.get('pregunta', '')
        modo = data.get('modo', 'simple')  # 'simple' o 'agente'
        modelo_seleccionado = data.get('modelo', available_models[0] if available_models else 'llama3')
        
        if not pregunta:
            return jsonify({'error': 'No se proporcionó ninguna pregunta'}), 400
        
        # Obtener el modelo seleccionado
        modelo = get_model(modelo_seleccionado)
        if modelo is None:
            return jsonify({'error': 'No hay modelos disponibles'}), 500
        
        if modo == 'agente' and modelo_seleccionado in agents and agents[modelo_seleccionado] is not None:
            # Usar el agente para preguntas que puedan requerir búsqueda web
            try:
                respuesta_completa = agents[modelo_seleccionado].invoke({"input": pregunta})
                
                # Extraer pasos intermedios si están disponibles
                pasos_intermedios = []
                if 'intermediate_steps' in respuesta_completa:
                    for paso in respuesta_completa['intermediate_steps']:
                        if len(paso) >= 2:
                            accion = paso[0]
                            observacion = paso[1]
                            pasos_intermedios.append({
                                'action': accion.tool,
                                'action_input': accion.tool_input,
                                'observation': observacion[:200] + '...' if len(observacion) > 200 else observacion
                            })
                
                return jsonify({
                    'respuesta': respuesta_completa['output'],
                    'modo': 'agente',
                    'modelo_usado': modelo_seleccionado,
                    'pasos_intermedios': pasos_intermedios
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
                        'modelo_usado': modelo_seleccionado
                    })
                else:
                    return jsonify({'error': f'Modelo {modelo_seleccionado} no disponible para fallback'}), 500
        else:
            # Usar chat simple
            if modelo_seleccionado in simple_chains:
                respuesta = simple_chains[modelo_seleccionado].invoke({"pregunta": pregunta})
                return jsonify({
                    'respuesta': respuesta,
                    'modo': 'simple',
                    'modelo_usado': modelo_seleccionado
                })
            else:
                return jsonify({'error': f'Modelo {modelo_seleccionado} no disponible'}), 400
            
    except Exception as e:
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
                respuesta_completa = agents[modelo_seleccionado].invoke({"input": pregunta})
                
                # Extraer pasos intermedios si están disponibles
                pasos_intermedios = []
                if 'intermediate_steps' in respuesta_completa:
                    for paso in respuesta_completa['intermediate_steps']:
                        if len(paso) >= 2:
                            accion = paso[0]
                            observacion = paso[1]
                            pasos_intermedios.append({
                                'action': accion.tool,
                                'action_input': accion.tool_input,
                                'observation': observacion[:200] + '...' if len(observacion) > 200 else observacion
                            })
                
                return jsonify({
                    'pregunta': pregunta,
                    'respuesta': respuesta_completa['output'],
                    'modo': 'agente_general',
                    'modelo_usado': modelo_seleccionado,
                    'tipo_demo': tipo_demo,
                    'pasos_intermedios': pasos_intermedios
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
