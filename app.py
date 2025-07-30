import os
import json
from typing import Optional
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from config import Config

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

print("🤖 Configurando modelo Llama3 con Ollama...")

# Validar que Ollama esté disponible
if not Config.validate_config():
    print("❌ Error: Ollama no está disponible")
    exit(1)

# Configurar el modelo de IA local con Ollama
try:
    llm = ChatOllama(
        model="llama3",
        temperature=Config.DEFAULT_TEMPERATURE
    )
    print("✅ Modelo Llama3 configurado correctamente")
except Exception as e:
    print(f"❌ Error configurando Llama3: {e}")
    print("💡 Asegúrate de que Ollama esté ejecutándose y que tengas el modelo llama3")
    exit(1)

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
agent_executor: Optional[AgentExecutor] = None
try:
    agent = create_react_agent(llm, tools, agent_prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        max_iterations=3,
        handle_parsing_errors=True
    )
    print("✅ Agente creado correctamente con Llama3")
except Exception as e:
    print(f"❌ Error creando agente: {e}")
    # Fallback: usar solo chat simple si el agente falla
    agent_executor = None

# También configurar un chat simple sin agente para preguntas básicas
simple_chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente útil y amigable. Responde de manera clara y concisa en español. Siempre mantén un tono profesional pero cercano."),
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
        
        if modo == 'agente' and agent_executor is not None:
            # Usar el agente para preguntas que puedan requerir búsqueda web
            try:
                respuesta = agent_executor.invoke({"input": pregunta})
                return jsonify({
                    'respuesta': respuesta['output'],
                    'modo': 'agente'
                })
            except Exception as e:
                print(f"Error en agente: {e}")
                # Fallback a chat simple si el agente falla
                respuesta = simple_chain.invoke({"pregunta": pregunta})
                return jsonify({
                    'respuesta': f"[Modo Simple] {respuesta}",
                    'modo': 'simple'
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
        
        # Verificar que el agente esté disponible
        if agent_executor is None:
            # Fallback: usar chat simple si el agente no está disponible
            respuesta_simple = simple_chain.invoke({"pregunta": pregunta_ejemplo})
            return jsonify({
                'pregunta': pregunta_ejemplo,
                'respuesta': f"[Modo Simple - Agente no disponible] {respuesta_simple}",
                'modo': 'simple'
            })
        
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
    print("📊 Modelo: Llama3 (Ollama)")
    print("🔍 Herramientas: Búsqueda web con DuckDuckGo")
    print("🌐 Servidor: http://127.0.0.1:5000")
    print("🦙 Usando modelo local - sin dependencia de APIs externas")
    app.run(debug=True, host='127.0.0.1', port=5000)
