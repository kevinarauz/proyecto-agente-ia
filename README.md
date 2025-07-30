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

> **⚠️ Nota:** Si experimentas errores, consulta el archivo `SOLUCION_ERRORES.md` que contiene soluciones a problemas comunes como errores 500, problemas de dependencias y configuración del agente.

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

Para mantener el código organizado y escalable, se recomienda la siguiente estructura de carpetas, que separa la lógica (Python), las plantillas (HTML) y los archivos estáticos (CSS, JS).

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
Toda petición directa a la API debe incluir tu clave secreta (`API Key`) en los encabezados. Este es tu "token" de autenticación. En los ejemplos siguientes, se envía en el encabezado `-H "X-goog-api-key: TU_API_KEY"`. Este paso es crucial sin importar el lenguaje o herramienta que uses.

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
      "finishReason": "STOP",
      "avgLogprobs": -0.048756192127863564
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

Esta es la forma limpia y profesional de integrar Gemini en tu código Python. El SDK maneja toda la complejidad de las solicitudes HTTP (encabezados, JSON, etc.) por ti.

```python
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carga la clave desde el archivo .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Elige el modelo
model = genai.GenerativeModel('gemini-2.0-flash')

# Genera el contenido
response = model.generate_content("Explain how AI works in a few words")

# Imprime la respuesta
print(response.text)
```

---

## 7. Ejecución de la Aplicación

Una vez que todo está configurado, puedes iniciar el servidor de desarrollo de Flask con un simple comando:

```bash
python app.py
```

Abre tu navegador y visita `http://127.0.0.1:5000` para ver tu aplicación en acción.

---

## 8. Prompting Avanzado: Dando Personalidad y Contexto

Para crear aplicaciones más sofisticadas, no basta con enviar solo la pregunta del usuario. Necesitas darle un contexto y rol a la IA.

### a) Usando un "System Prompt" (Mensaje de Sistema)

Un **System Prompt** es una instrucción base que se envía a la IA en cada solicitud para definir su **rol, tono, o las reglas que debe seguir**. Es la forma de decirle "Tú eres..." antes de que vea la pregunta del usuario.

LangChain facilita esto con `ChatPromptTemplate`, que distingue entre mensajes del sistema y mensajes del usuario.

**Ejemplo de implementación:**

```python
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# Configura el modelo, asegurándote de pasar la clave de API
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=os.getenv("GOOGLE_API_KEY"))

# Crea la plantilla del prompt con un mensaje de sistema
prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente experto en historia del Ecuador. Responde siempre en un tono amigable y educativo."),
    ("user", "{pregunta_del_usuario}")
])

# Crea el parser de salida
output_parser = StrOutputParser()

# Construye la cadena (chain)
chain = prompt | llm | output_parser

# Invoca la cadena con una pregunta
respuesta = chain.invoke({"pregunta_del_usuario": "¿Quién fue Eloy Alfaro?"})
print(respuesta)
```

### b) Manteniendo Memoria en la Conversación (Memory Buffer)

Para que un chatbot recuerde interacciones pasadas en una misma sesión (por ejemplo, si el usuario dice "explícame más sobre eso"), necesitas añadir un **buffer de memoria**.

En LangChain, esto se logra con objetos de memoria como `ConversationBufferMemory`. Este objeto almacena el historial de la conversación y lo inyecta automáticamente en el prompt en cada nueva interacción, dando a la IA el contexto completo de lo que se ha hablado.

Integrar memoria es un paso más avanzado, pero es esencial para construir verdaderos asistentes conversacionales.

---

## 9. Alternativa Local: Ejecutando un LLM en tu Propia Máquina

No siempre necesitas depender de una API de pago. Puedes ejecutar modelos de lenguaje de código abierto como **Llama 3**, **Gemma** o **Phi-3** directamente en tu computadora. La forma más sencilla de hacerlo es con **Ollama**.

### a) ¿Qué es Ollama?

Ollama es una herramienta que simplifica la descarga, configuración y ejecución de LLMs en tu máquina local. Crea un servidor local al que puedes hacer peticiones, de forma muy similar a como lo harías con una API en la nube.

### b) Instalación de Ollama

1.  **Descarga Ollama:** Ve a [ollama.com](https://ollama.com/) e instala la aplicación para Windows.
2.  **Verifica la Instalación:** Abre una nueva terminal (CMD o PowerShell) y ejecuta `ollama`. Si ves una lista de comandos, la instalación fue exitosa.

### c) Gestionando Modelos con Ollama

Puedes tener múltiples modelos descargados y cambiar entre ellos fácilmente.

#### 1. Listar los Modelos Instalados
Para ver qué modelos ya tienes en tu máquina, usa el comando `list`.

```bash
ollama list
```
Esto te mostrará una tabla con el nombre, ID, tamaño y fecha de modificación de cada modelo.

#### 2. Descargar un Modelo (`pull`)
El comando `pull` solo descarga un modelo de internet a tu disco duro para tenerlo listo.

```bash
# Descargar la versión estándar (8B) de Llama 3
ollama pull llama3

# Descargar la versión más liviana (2B) de Gemma
ollama pull gemma:2b
```

#### 3. Ejecutar un Modelo (`run`)
El comando `run` inicia una sesión de chat interactiva con el modelo que elijas. Si el modelo no está descargado, `run` lo descargará automáticamente primero.

```bash
# Iniciar un chat con Llama 3
ollama run llama3

# Iniciar un chat con la versión 2B de Gemma
ollama run gemma:2b
```
Puedes usar `Ctrl+D` o escribir `/bye` para salir de la sesión de chat.

### d) Eligiendo un Modelo Local
No todos los modelos son iguales. Aquí tienes una comparación rápida de los modelos más populares para ayudarte a decidir cuál usar.

| Modelo | Parámetros | Tamaño (Peso) | Uso Ideal | Comando `pull` |
| :--- | :--- | :--- | :--- | :--- |
| **Llama 3** | 8B | ~4.7 GB | **El mejor todoterreno.** Excelente razonamiento, bueno para código y seguir instrucciones complejas. Ideal para empezar. | `ollama pull llama3` |
| **Gemma** | 2B | ~1.7 GB | **El más liviano.** Perfecto para máquinas con pocos recursos (4-8 GB RAM). Bueno para tareas creativas y chat general. | `ollama pull gemma:2b` |
| **Phi-3** | 3.8B | ~2.3 GB | **Potente y pequeño.** Muy bueno en lógica y código, a menudo supera a modelos más grandes en estas áreas. Gran alternativa a Llama 3. | `ollama pull phi3` |

**B** = Billones (Miles de millones) de parámetros. Más parámetros generalmente significan mayor capacidad, pero también mayores requisitos de hardware.

### e) Usando Modelos Locales como una API
La gran ventaja de Ollama es que, por defecto, **expone cualquier modelo que ejecutes como una API REST en tu `localhost`**. Esto te permite desarrollar tu aplicación consumiendo una API local gratuita, y si en el futuro necesitas más potencia, solo tienes que cambiar la URL a un proveedor de API en la nube.

1.  **Asegúrate de que Ollama esté corriendo:** La aplicación de Ollama debe estar en ejecución en tu bandeja del sistema en Windows.
2.  **Haz una petición a la API local:** Abre una terminal y usa `curl` para enviar una petición al servidor de Ollama, que corre en el puerto `11434`.

**Ejemplo de API Request a Llama 3 local (CMD):**
```cmd
curl http://localhost:11434/api/generate -d "{\"model\": \"llama3\", \"prompt\": \"Why is the sky blue?\", \"stream\": false}"
```
* `"model": "llama3"`: Especifica qué modelo de los que tienes descargados quieres usar.
* `"prompt": "..."`: Tu pregunta.
* `"stream": false`: Para recibir la respuesta completa de una vez.

Esto te devolverá un JSON muy similar al de la API de Gemini, demostrando que puedes desarrollar con la misma lógica de API.

### f) Integración con LangChain

LangChain tiene una integración nativa con Ollama, lo que hace que cambiar de un modelo en la nube a uno local sea trivial.

**Ejemplo de implementación:**

```python
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Inicializa el modelo local a través de Ollama
# Asegúrate de que el nombre del modelo coincida con uno de tu lista de `ollama list`.
llm = ChatOllama(model="llama3")

# 2. Crea el prompt (puedes usar el mismo formato que antes)
prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un pirata. Responde a todas las preguntas con jerga de pirata."),
    ("user", "{pregunta}")
])

# 3. Construye la cadena
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# 4. Invoca la cadena
respuesta = chain.invoke({"pregunta": "¿Cuál es la capital de Japón?"})
print(respuesta)
# Salida esperada: "¡Ahoy, marinero! La capital de esas tierras lejanas es Tokio, ¡arrr!"
```

Usar un modelo local es una excelente opción para desarrollo, prototipado rápido y para aplicaciones donde la privacidad de los datos es una prioridad, ya que ninguna información sale de tu máquina.

---

## 10. Más Allá de las Preguntas: Automatización de Tareas con Agentes de IA

El verdadero poder de los LLMs no es solo responder preguntas, sino **realizar acciones**. Para esto, usamos **Agentes de IA**.

### a) ¿Qué es un Agente de IA?

Un agente es un sistema que utiliza un LLM como su "cerebro" para razonar y decidir qué acciones tomar. En lugar de solo generar texto, un agente puede usar un conjunto de **herramientas** para interactuar con el mundo exterior.

El ciclo de un agente es:
1.  **Observa:** Recibe una solicitud del usuario (ej. "Investiga el clima en Guayaquil y resúmelo").
2.  **Piensa:** El LLM decide qué herramienta necesita para cumplir la solicitud (ej. "Necesito una herramienta de búsqueda web").
3.  **Actúa:** El agente ejecuta la herramienta elegida (ej. busca en internet "clima en Guayaquil").
4.  **Observa de nuevo:** Recibe el resultado de la herramienta (ej. una página con datos del clima).
5.  **Repite:** El LLM procesa el resultado y decide el siguiente paso (ej. "Ahora voy a resumir este texto") hasta que la tarea original esté completa.

### b) Ejemplo Práctico: Un Agente de Búsqueda Web

Vamos a crear un agente simple que puede navegar por internet para responder preguntas sobre eventos actuales. Usaremos la herramienta de búsqueda de DuckDuckGo, que no requiere clave de API.

**1. Actualiza tus dependencias:**
Asegúrate de que tu archivo `requirements.txt` incluya `duckduckgo-search` y vuelve a instalar las dependencias si es necesario.

**2. Código del Agente:**
Este código crea un agente que sabe usar la herramienta de búsqueda.

```python
from langchain_community.chat_models import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain import hub

# 1. Inicializa el modelo local (el cerebro del agente)
llm = ChatOllama(model="llama3")

# 2. Define las herramientas que el agente puede usar
# En este caso, solo una herramienta para buscar en DuckDuckGo
tools = [DuckDuckGoSearchRun()]

# 3. Carga un prompt pre-diseñado para agentes (ReAct)
# Este prompt le enseña al LLM cómo pensar y usar herramientas.
prompt = hub.pull("hwchase17/react")

# 4. Crea el agente
agent = create_react_agent(llm, tools, prompt)

# 5. Crea el "ejecutor" del agente, que es lo que realmente corre el ciclo
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 6. Invoca al agente con una pregunta que requiera información actual
# El agente se dará cuenta de que no sabe la respuesta y usará la herramienta de búsqueda.
pregunta = "¿Quién ganó la final de la Champions League más reciente?"
respuesta = agent_executor.invoke({"input": pregunta})

print(respuesta)
```

Al ejecutar este código con `verbose=True`, verás en la terminal todo el proceso de "pensamiento" del agente: cómo decide usar la herramienta de búsqueda, qué busca, qué encuentra y cómo formula la respuesta final. Esto es la automatización de tareas en acción.

---