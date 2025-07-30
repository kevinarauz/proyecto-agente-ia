import os
import json
from typing import Optional
from flask import Flask, render_template, request, jsonify
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
def get_model(model_name: str):
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

# Usar prompt optimizado para Llama3
agent_prompt = PromptTemplate.from_template("""
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
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
                max_iterations=3,
                handle_parsing_errors=True
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
def index():
    return render_template('index.html', modelos_disponibles=available_models)

@app.route('/chat', methods=['POST'])
def chat():
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
                print(f"Error en agente {modelo_seleccionado}: {e}")
                # Fallback a chat simple si el agente falla
                if modelo_seleccionado in simple_chains:
                    respuesta = simple_chains[modelo_seleccionado].invoke({"pregunta": pregunta})
                    return jsonify({
                        'respuesta': f"[Modo Simple] {respuesta}",
                        'modo': 'simple',
                        'modelo_usado': modelo_seleccionado
                    })
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
def ejemplo_agente():
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

if __name__ == '__main__':
    print("🤖 Iniciando aplicación de IA con Agentes...")
    print(f"🧠 Modelos disponibles: {', '.join(available_models)}")
    print("🔍 Herramientas: Búsqueda web con DuckDuckGo")
    print("🌐 Servidor: http://127.0.0.1:5000")
    print("🚀 Aplicación multi-modelo lista!")
    app.run(debug=True, host='127.0.0.1', port=5000)
