import os
import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import Config

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# Validar configuración antes de continuar
try:
    Config.validate_config()
except ValueError as e:
    print(f"❌ Error de configuración: {e}")
    print("💡 Asegúrate de que el archivo .env contenga GOOGLE_API_KEY")
    exit(1)

# Configurar el modelo de IA
if Config.GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = Config.GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-pro", 
    temperature=Config.DEFAULT_TEMPERATURE
)

# Configurar herramientas para el agente
tools = [DuckDuckGoSearchRun()]

# Prompt personalizado para el agente
agent_prompt = PromptTemplate.from_template("""
Eres un asistente inteligente que puede ayudar con información actual y realizar búsquedas web cuando sea necesario.

Tienes acceso a las siguientes herramientas:
{tools}

Usa el siguiente formato:

Pregunta: la pregunta de entrada que debes responder
Pensamiento: siempre debes pensar sobre qué hacer
Acción: la acción a tomar, debe ser una de [{tool_names}]
Entrada de Acción: la entrada a la acción
Observación: el resultado de la acción
... (este Pensamiento/Acción/Entrada de Acción/Observación puede repetirse N veces)
Pensamiento: ahora sé la respuesta final
Respuesta Final: la respuesta final a la pregunta de entrada original

Comienza!

Pregunta: {input}
Pensamiento: {agent_scratchpad}
""")

# Crear el agente
agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True,
    max_iterations=3,
    handle_parsing_errors=True
)

# También configurar un chat simple sin agente para preguntas básicas
simple_chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente útil y amigable. Responde de manera clara y concisa."),
    ("user", "{pregunta}")
])

simple_chain = simple_chat_prompt | llm | StrOutputParser()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        pregunta = data.get('pregunta', '')
        modo = data.get('modo', 'simple')  # 'simple' o 'agente'
        
        if not pregunta:
            return jsonify({'error': 'No se proporcionó ninguna pregunta'}), 400
        
        if modo == 'agente':
            # Usar el agente para preguntas que puedan requerir búsqueda web
            respuesta = agent_executor.invoke({"input": pregunta})
            return jsonify({
                'respuesta': respuesta['output'],
                'modo': 'agente'
            })
        else:
            # Usar chat simple para preguntas básicas
            respuesta = simple_chain.invoke({"pregunta": pregunta})
            return jsonify({
                'respuesta': respuesta,
                'modo': 'simple'
            })
            
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
        
        respuesta = agent_executor.invoke({"input": pregunta_ejemplo})
        
        return jsonify({
            'pregunta': pregunta_ejemplo,
            'respuesta': respuesta['output'],
            'modo': 'agente'
        })
        
    except Exception as e:
        return jsonify({'error': f'Error en ejemplo de agente: {str(e)}'}), 500

if __name__ == '__main__':
    print("🤖 Iniciando aplicación de IA con Agentes...")
    print("📊 Modelo: Google Gemini Pro")
    print("🔍 Herramientas: Búsqueda web con DuckDuckGo")
    print("🌐 Servidor: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
