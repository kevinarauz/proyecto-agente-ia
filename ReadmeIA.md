# 🤖 Agente de IA - Aplicación Web Inteligente

¡Aplicación web completa con agentes de IA que pueden realizar búsquedas web y responder preguntas! Esta aplicación utiliza Python, Flask, LangChain y Google Gemini para crear un asistente inteligente con capacidades avanzadas.

## ✨ Características Principales

- **Chat Simple**: Respuestas directas usando Google Gemini
- **Agente con Búsqueda Web**: Puede buscar información actual en internet
- **Interfaz Moderna**: Diseño responsive con Bootstrap y animaciones
- **Dos Modos de Operación**: Simple y Agente con herramientas
- **Demo Interactivo**: Ejemplos predefinidos para probar las capacidades

## 🚀 Ejecución Rápida

La aplicación ya está configurada y lista para usar. Simplemente ejecuta:

```bash
python app.py
```

Luego abre tu navegador en: `http://127.0.0.1:5000`

> **⚠️ Nota:** Si experimentas errores, consulta la sección de **Troubleshooting** al final de este documento o el archivo `SOLUCION_ERRORES.md`.

## 🎯 Concepto del Proyecto

Esta aplicación demuestra el poder de los **Agentes de IA**: sistemas que no solo responden preguntas, sino que pueden usar herramientas para realizar acciones y obtener información actualizada.

**Flujo de trabajo principal:**

1.  **Frontend (UI/UX):** El usuario introduce datos (texto, preguntas, etc.) en una interfaz web construida con HTML, CSS y JavaScript.
2.  **Backend (Flask):** Un servidor Flask recibe la solicitud del usuario.
3.  **Orquestador (LangChain):** Flask pasa la solicitud a LangChain, que la formatea y la envía al modelo de IA apropiado (Google Gemini).
4.  **Motor de IA (Google Gemini):** El modelo procesa la solicitud y genera una respuesta.
5.  **Respuesta al Usuario:** LangChain devuelve la respuesta a Flask, que la renderiza en la plantilla HTML y la envía de vuelta al navegador del usuario.

---

## 2. Pila Tecnológica (Tech Stack)

| Categoría | Tecnología | Propósito |
| :--- | :--- | :--- |
| **Backend** | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) | Lenguaje de programación principal para la lógica del servidor. |
| | ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white) | Micro-framework web para crear las rutas y manejar las solicitudes HTTP. |
| **Inteligencia Artificial**| ![LangChain](https://img.shields.io/badge/LangChain-000000?style=for-the-badge) | Framework para simplificar la interacción con los modelos de lenguaje. |
| | ![Google Gemini](https://img.shields.io/badge/Google_Gemini-8E75B7?style=for-the-badge&logo=google-gemini&logoColor=white) | El modelo de lenguaje grande (LLM) que proporciona la "inteligencia". |
| **Frontend** | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white) | Estructura de la página web. |
| | ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white) | Estilos y diseño visual. |
| | ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black) | Interactividad en el lado del cliente. |
| **UI/UX Frameworks** | ![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white) | Framework CSS para un diseño responsive y componentes pre-diseñados. |
| | ![SweetAlert2](https://img.shields.io/badge/SweetAlert2-850000?style=for-the-badge) | Librería para crear alertas y modales atractivos y personalizables. |
| | ![AOS](https://img.shields.io/badge/AOS-000000?style=for-the-badge) | Librería para animaciones al hacer scroll (Animate On Scroll). |

---

## 3. Guía de Estilo y Diseño Frontend (UI/UX)

Para mantener una consistencia visual y una experiencia de usuario de alta calidad, este proyecto sigue una serie de directrices de diseño.

### a) Filosofía de Diseño
- **Simplicidad y Claridad:** La interfaz debe ser intuitiva y fácil de navegar.
- **Consistencia:** Los elementos recurrentes (botones, tarjetas, menús) deben lucir y comportarse de la misma manera en toda la aplicación.
- **Mobile-First:** El diseño se piensa primero para dispositivos móviles y luego se adapta a pantallas más grandes, garantizando una experiencia óptima en cualquier dispositivo.

### b) Framework Principal: Bootstrap 5
La base de todo el layout y los componentes es **Bootstrap 5**. Se debe priorizar el uso de sus clases y componentes nativos (`container`, `row`, `col-`, `btn`, `card`, `navbar`, etc.) para agilizar el desarrollo y asegurar la responsividad.

### c) Tipografía
- **Fuente Principal:** Se recomienda usar una fuente sans-serif moderna y legible como **'Inter'** o **'Poppins'**, importada desde Google Fonts.
- **Jerarquía de Títulos:**
    - `<h1>`: Título principal de la página (ej. 48px).
    - `<h2>`: Títulos de secciones principales (ej. 36px).
    - `<h3>`: Subtítulos o títulos de tarjetas (ej. 24px).
    - `<p>`: Texto de párrafo (ej. 16px o 1rem).

### d) Layout y Estructura
- **Grid System de Bootstrap:** Para la maquetación general de la página (división en columnas), se debe usar el sistema de rejilla de Bootstrap (`<div class="row">` y `<div class="col-md-6">`).
- **Flexbox:** Para alinear elementos dentro de un componente (centrar un ícono y texto en un botón, distribuir elementos en una cabecera), se deben usar las utilidades de Flexbox de Bootstrap (`d-flex`, `justify-content-*`, `align-items-*`).

### e) Componentes Clave
- **Menús de Navegación:** Utilizar el componente `navbar` de Bootstrap, asegurando que sea colapsable en móviles.
- **Botones:** Usar las clases `.btn` de Bootstrap (`.btn-primary`, `.btn-secondary`) para mantener la consistencia en los llamados a la acción.
- **Tarjetas (Cards):** Para mostrar contenido encapsulado (como las respuestas de la IA), usar el componente `.card` de Bootstrap.

### f) Animaciones y Efectos
- **AOS (Animate On Scroll):** Para animaciones sutiles al hacer scroll y revelar contenido.
- **Transiciones CSS:** Para efectos `hover` en botones y enlaces, usar transiciones suaves (`transition: all 0.3s ease;`) en lugar de cambios bruscos.

---

## 4. Estructura del Proyecto

Para mantener el código organizado y escalable, se recomienda la siguiente estructura de carpetas.

```
/mi_proyecto_ia/
|
├── app.py                  # Archivo principal de la aplicación Flask y lógica de LangChain
├── .env                    # Archivo para guardar claves de API (¡NO subir a Git!)
├── requirements.txt        # Lista de dependencias de Python
|
├── /templates/
│   └── index.html          # Plantilla HTML principal para la interfaz de usuario
|
└── /static/
    ├── /css/
    │   └── style.css       # Tus estilos CSS personalizados
    └── /js/
        └── script.js       # Tu código JavaScript personalizado
```

---

## 5. Guía de Instalación y Configuración

Sigue estos pasos para poner en marcha el proyecto en tu máquina local. Los comandos están adaptados para Windows.

1.  **Clonar el Repositorio** (si estuviera en Git)
    ```bash
    git clone <url-del-repositorio>
    cd mi_proyecto_ia
    ```

2.  **Crear y Activar Entorno Virtual**
    ```bash
    # Crear el entorno (funciona en CMD y PowerShell)
    python -m venv venv

    # Activar en Windows (CMD y PowerShell)
    .\venv\Scripts\activate
    ```

3.  **Instalar Dependencias desde `requirements.txt`**

    El archivo `requirements.txt` es una lista de todas las librerías de Python que nuestro proyecto necesita para funcionar. El comando `pip install -r` lee este archivo e instala todo automáticamente.

    **Paso 3.1: Crear el archivo**
    En la carpeta raíz de tu proyecto (`/mi_proyecto_ia/`), crea un archivo de texto llamado `requirements.txt`.

    **Paso 3.2: Añadir el contenido**
    Abre el archivo y pega la siguiente lista de librerías:
    ```txt
    flask
    langchain
    langchain-google-genai
    langchain-community # Necesario para modelos locales con Ollama
    python-dotenv
    duckduckgo-search   # Herramienta para agentes
    ```

    **Paso 3.3: Instalar las librerías**
    Asegúrate de que tu entorno virtual esté activo (deberías ver `(venv)` en tu terminal). Luego, ejecuta el siguiente comando:
    ```bash
    pip install -r requirements.txt
    ```
    Pip leerá el archivo e instalará cada una de las librerías especificadas.

4.  **Configurar Clave de API (Opcional, para Gemini)**
    Crea un archivo `.env` en la raíz del proyecto y añade tu clave de la API de Google Gemini:
    ```
    GOOGLE_API_KEY="AIzaSyCypmLSsEUQ7qoCYZXjy_pbXRKVR1a51D0"
    ```

---

## 6. Interacción con la API de Gemini

Existen dos formas principales de comunicarse con la API:

### a) Directa (con cURL o PowerShell)

Útil para pruebas rápidas desde la terminal. Esto te permite entender la estructura fundamental de una petición a la API.

**Nota sobre el Token de Autenticación:**
Toda petición directa a la API debe incluir tu clave secreta (`API Key`) en los encabezados. Este es tu "token" de autenticación.

#### Request (Opción 1: para Símbolo del sistema - CMD)
```cmd
curl "[https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent](https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent)" -H "Content-Type: application/json" -H "X-goog-api-key: AIzaSyCypmLSsEUQ7qoCYZXjy_pbXRKVR1a51D0" -X POST -d "{\"contents\":[{\"parts\":[{\"text\":\"Explain how AI works in a few words\"}]}]}"
```

#### Request (Opción 2: para PowerShell)
```powershell
Invoke-WebRequest -Uri "[https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent](https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent)" -Method POST -ContentType "application/json" -Headers @{"X-goog-api-key"="AIzaSyCypmLSsEUQ7qoCYZXjy_pbXRKVR1a51D0"} -Body '{"contents":[{"parts":[{"text":"Explain how AI works in a few words"}]}]}'
```

#### Response (Respuesta de la API)
```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "AI learns patterns from data to make predictions or decisions.\n"
          }
        ],
        "role": "model"
      },
      "finishReason": "STOP"
    }
  ],
  "usageMetadata": {
    "promptTokenCount": 8,
    "candidatesTokenCount": 12,
    "totalTokenCount": 20
  }
}
```

### b) A través del SDK de Python (Recomendado para aplicaciones)

Esta es la forma limpia y profesional de integrar Gemini en tu código Python.

```python
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel('gemini-2.0-flash')
response = model.generate_content("Explain how AI works in a few words")
print(response.text)
```

---

## 7. Ejecución de la Aplicación

Una vez que todo está configurado, puedes iniciar el servidor de desarrollo de Flask:

```bash
python app.py
```

Abre tu navegador y visita `http://127.0.0.1:5000` para ver tu aplicación en acción.

---

## 8. Prompting Avanzado: Dando Personalidad y Contexto

### a) Usando un "System Prompt" (Mensaje de Sistema)

Un **System Prompt** es una instrucción base que se envía a la IA en cada solicitud para definir su **rol, tono, o las reglas que debe seguir**.

```python
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=os.getenv("GOOGLE_API_KEY"))

prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente experto en historia del Ecuador. Responde siempre en un tono amigable y educativo."),
    ("user", "{pregunta_del_usuario}")
])

output_parser = StrOutputParser()
chain = prompt | llm | output_parser
respuesta = chain.invoke({"pregunta_del_usuario": "¿Quién fue Eloy Alfaro?"})
print(respuesta)
```

### b) Manteniendo Memoria en la Conversación (Memory Buffer)

Para que un chatbot recuerde interacciones pasadas, necesitas añadir un **buffer de memoria** (ej. `ConversationBufferMemory` en LangChain). Este objeto almacena el historial y lo inyecta automáticamente en el prompt, dando contexto a la IA.

---

## 9. Alternativa Local: Ejecutando un LLM en tu Propia Máquina

Puedes ejecutar modelos de código abierto como **Llama 3** en tu computadora con **Ollama**.

### a) Instalación y Gestión de Modelos
1.  **Instala Ollama:** Descárgalo desde [ollama.com](https://ollama.com/) para Windows.
2.  **Explora Modelos Disponibles:** Para ver la lista completa de modelos que puedes descargar, visita la biblioteca oficial en la web: **[https://ollama.com/library](https://ollama.com/library)**. Ollama no tiene un comando de terminal para buscar modelos remotos.
3.  **Gestiona Modelos Localmente:**
    ```bash
    # Ver modelos que ya tienes instalados
    ollama list

    # Descargar un modelo de la biblioteca
    ollama pull llama3

    # Chatear con un modelo instalado
    ollama run llama3
    ```

### b) Eligiendo un Modelo Local: Comparativa
No todos los modelos son iguales. Aquí tienes una comparación para ayudarte a decidir.

| Modelo | Parámetros | Tamaño (Peso) | Fortalezas Clave | Comando `pull` |
| :--- | :--- | :--- | :--- | :--- |
| **Llama 3** | 8B | ~4.7 GB | **El mejor todoterreno.** Excelente razonamiento general, bueno para seguir instrucciones complejas. La opción más segura y recomendada para empezar. | `ollama pull llama3` |
| **DeepSeek-Coder** | 7B | ~4.1 GB | **Especialista en Código.** Superior en tareas de programación, autocompletado y lógica de código. Muy buen razonador general. | `ollama pull deepseek-coder` |
| **Mistral** | 7B | ~4.1 GB | **El más eficiente.** Rendimiento increíble para su tamaño, a menudo compite con modelos más grandes. Muy rápido y balanceado. | `ollama pull mistral` |
| **Phi-3** | 3.8B | ~2.3 GB | **Potente y pequeño.** Muy bueno en lógica y código para su tamaño. Ideal si Llama 3 es un poco pesado para tu sistema. | `ollama pull phi3` |

**B** = Billones (Miles de millones) de parámetros. Más parámetros generalmente significan mayor capacidad, pero también mayores requisitos de hardware.

### c) Usando Modelos Locales como una API
Ollama expone una API REST en `http://localhost:11434`. Puedes hacerle peticiones directamente.

**Ejemplo de API Request a Llama 3 local (CMD):**
```cmd
curl http://localhost:11434/api/generate -d "{\"model\": \"llama3\", \"prompt\": \"Why is the sky blue?\", \"stream\": false}"
```

### d) Integración con LangChain

```python
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOllama(model="llama3")

prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un pirata. Responde a todas las preguntas con jerga de pirata."),
    ("user", "{pregunta}")
])

output_parser = StrOutputParser()
chain = prompt | llm | output_parser
respuesta = chain.invoke({"pregunta": "¿Cuál es la capital de Japón?"})
print(respuesta)
```

---

## 10. Más Allá de las Preguntas: Automatización de Tareas con Agentes de IA

Un **Agente de IA** usa un LLM como "cerebro" para razonar y utilizar **herramientas** (como una búsqueda web) para realizar acciones.

### a) Ejemplo Práctico: Un Agente de Búsqueda Web

```python
from langchain_community.chat_models import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

# 1. Inicializa el modelo local (el cerebro del agente)
llm = ChatOllama(model="llama3")

# 2. Define las herramientas que el agente puede usar
tools = [DuckDuckGoSearchRun()]

# 3. Carga un prompt pre-diseñado para agentes (ReAct)
prompt = hub.pull("hwchase17/react")

# 4. Crea el agente
agent = create_react_agent(llm, tools, prompt)

# 5. Crea el "ejecutor" del agente
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 6. Invoca al agente
pregunta = "¿Quién ganó la final de la Champions League más reciente?"
respuesta = agent_executor.invoke({"input": pregunta})

print(respuesta)
```
Al ejecutar con `verbose=True`, verás el proceso de "pensamiento" del agente en la terminal.

---

## 11. Troubleshooting y Solución de Problemas

### 🔧 Problemas Comunes y Soluciones

Si encuentras errores al ejecutar la aplicación, aquí tienes las soluciones más comunes:

#### Error 500 (Internal Server Error)
```
❌ Problema: La aplicación devuelve error 500 al hacer peticiones
✅ Solución: Verificar que todas las dependencias estén instaladas correctamente
```bash
# Reinstalar dependencias
pip install -r requirements.txt

# Verificar configuración
python diagnostico.py
```

#### Error de Conexión (ERR_CONNECTION_RESET)
```
❌ Problema: El navegador no puede conectarse al servidor
✅ Solución: Asegurarse de que la aplicación esté ejecutándose
```bash
# Verificar que Python esté ejecutando la aplicación
python app.py

# Si no funciona, intentar:
python run_app.py  # Script con mejor manejo de errores
```

#### Problemas con el Agente
```
❌ Problema: El agente no funciona correctamente
✅ Solución: La aplicación tiene fallback automático a chat simple
```

El código está diseñado para funcionar incluso si el agente falla, usando el chat simple como respaldo.

#### Error de API Key
```
❌ Problema: Error relacionado con GOOGLE_API_KEY
✅ Solución: Verificar archivo .env
```bash
# Verificar que el archivo .env contenga:
GOOGLE_API_KEY="tu_clave_aqui"
```

### 📋 Scripts de Diagnóstico

Para diagnosticar problemas, usa estos scripts incluidos:

```bash
# Verificar todas las dependencias y configuración
python diagnostico.py

# Probar imports específicos
python test_imports.py

# Ejecutar con mejor manejo de errores
python run_app.py
```

### 📝 Archivos de Ayuda

- `SOLUCION_ERRORES.md`: Documentación completa de errores solucionados
- `diagnostico.py`: Script para verificar el estado de la aplicación
- `test_imports.py`: Verificación de dependencias específicas

### 🆘 Si Todo Falla

1. **Verificar versión de Python**: Debe ser 3.8 o superior
2. **Recrear entorno virtual**: 
   ```bash
   python -m venv venv_nuevo
   .\venv_nuevo\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Verificar conexión a internet**: Necesaria para descargar dependencias y usar el agente
4. **Consultar logs**: Revisar mensajes de error en la terminal para más detalles
