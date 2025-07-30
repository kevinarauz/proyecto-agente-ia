import os
import json
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
            model="gemini-1.5-flash",
            temperature=Config.DEFAULT_TEMPERATURE
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

# Configurar herramientas para el agente
tools = [DuckDuckGoSearchRun()]

# Prompt optimizado para búsquedas eficientes
agent_prompt = PromptTemplate.from_template("""
Eres un asistente de IA especializado en proporcionar respuestas precisas y actuales. Tienes acceso a herramientas de búsqueda web.

Herramientas disponibles:
{tools}

REGLAS IMPORTANTES: 
1. SIEMPRE usa búsqueda web para: clima actual, noticias recientes, precios actuales, eventos deportivos
2. Para clima, busca términos específicos como: "weather [ciudad] today current" o "clima actual [ciudad]"
3. NUNCA digas que no tienes acceso a información en tiempo real - ¡SÍ LO TIENES!
4. Si una búsqueda falla, intenta con términos diferentes
5. Proporciona respuestas útiles basadas en los resultados obtenidos

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

# Crear el agente con manejo de errores
agents = {}
for model_name, model_instance in models.items():
    if model_instance is not None:
        try:
            agent = create_react_agent(model_instance, tools, agent_prompt)
            agents[model_name] = AgentExecutor(
                agent=agent, 
                tools=tools, 
                verbose=True,
                max_iterations=6,  # Aumentado para permitir más búsquedas
                max_execution_time=30,  # Límite de tiempo de 30 segundos
                handle_parsing_errors=True,
                return_intermediate_steps=True
            )
            print(f"✅ Agente {model_name} creado correctamente")
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
                respuesta = agents[modelo_seleccionado].invoke({"input": pregunta})
                return jsonify({
                    'respuesta': respuesta['output'],
                    'modo': 'agente',
                    'modelo_usado': modelo_seleccionado
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
            "¿Cuál es el clima actual en Quito, Ecuador?",
            "¿Quién ganó la final de la Champions League más reciente?",
            "¿Cuáles son las últimas noticias sobre inteligencia artificial?",
            "¿Cuál es el precio actual del Bitcoin?"
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
            if 'clima' in pregunta_lower or 'weather' in pregunta_lower:
                if 'quito' in pregunta_lower:
                    return [
                        "weather Quito Ecuador today current",
                        "clima actual Quito Ecuador hoy",
                        "Quito weather forecast today"
                    ]
            elif 'precio' in pregunta_lower and 'bitcoin' in pregunta_lower:
                return [
                    "Bitcoin price today USD current",
                    "precio Bitcoin actual USD"
                ]
            elif 'noticias' in pregunta_lower:
                return [
                    f"{pregunta_original} últimas 24 horas",
                    f"latest news {pregunta_original}"
                ]
            
            # Búsqueda genérica mejorada
            return [pregunta_original, f"{pregunta_original} 2025"]
        
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
                    if resultado and len(resultado.strip()) > 50 and not "No se encontraron resultados" in resultado:
                        search_results = resultado
                        consulta_exitosa = consulta
                        print(f"✅ Búsqueda exitosa con: {consulta}")
                        break
                except Exception as e:
                    print(f"⚠️ Error en búsqueda '{consulta}': {e}")
                    continue
            
            if not search_results:
                return jsonify({
                    'respuesta': "❌ No pude obtener información actualizada desde internet en este momento. Esto puede deberse a limitaciones temporales del servicio de búsqueda. Te recomiendo:\n\n1. Consultar directamente sitios como Google Weather, AccuWeather o Weather.com\n2. Usar aplicaciones móviles de clima\n3. Intentar la búsqueda más tarde",
                    'modo': 'busqueda_fallback',
                    'modelo_usado': modelo_seleccionado,
                    'fuente': 'Error DuckDuckGo'
                })
            
            # Usar el modelo para resumir y formatear los resultados
            modelo = get_model(modelo_seleccionado)
            if modelo and modelo_seleccionado in simple_chains:
                prompt_busqueda = f"""
                INSTRUCCIONES: Eres un asistente experto que SIEMPRE debe proporcionar información útil basada en los resultados de búsqueda.

                PREGUNTA DEL USUARIO: "{pregunta}"
                
                RESULTADOS DE BÚSQUEDA OBTENIDOS:
                {search_results}

                IMPORTANTE:
                1. NUNCA digas que no tienes acceso a información en tiempo real
                2. SIEMPRE analiza y extrae información útil de los resultados
                3. Si hay datos específicos (temperatura, precios, fechas), inclúyelos
                4. Estructura la respuesta de forma clara y útil
                5. Si los resultados no son perfectos, extrae lo que sea útil y admítelo
                
                RESPUESTA REQUERIDA (en español):
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

if __name__ == '__main__':
    print("🤖 Iniciando aplicación de IA con Agentes...")
    print(f"🧠 Modelos disponibles: {', '.join(available_models)}")
    print("🔍 Herramientas: Búsqueda web con DuckDuckGo")
    print("🌐 Servidor: http://127.0.0.1:5000")
    print("🚀 Aplicación multi-modelo lista!")
    app.run(debug=True, host='127.0.0.1', port=5000)
