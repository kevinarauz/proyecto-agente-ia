# 🎯 Guía de Uso - Agente de IA

## 🚀 Cómo Ejecutar la Aplicación

### Opción 1: Usar el script batch (CMD)
Haz doble clic en `iniciar_app.bat` o ejecuta en CMD:
```cmd
iniciar_app.bat
```

### Opción 2: Usar PowerShell
Ejecuta en PowerShell:
```powershell
.\iniciar_app.ps1
```

### Opción 3: Comando directo
```cmd
python app.py
```

## 🎮 Cómo Usar la Aplicación

1. **Abrir en navegador**: Ve a `http://127.0.0.1:5000`

2. **Seleccionar Modo**:
   - **💬 Chat Simple**: Para preguntas generales
   - **🔍 Agente con Búsqueda Web**: Para información actual

3. **Ejemplos de Preguntas**:

### Chat Simple (Conocimiento general)
- "¿Qué es la inteligencia artificial?"
- "Explícame qué es Python"
- "¿Cómo funciona Flask?"
- "Dame consejos para aprender programación"

### Agente con Búsqueda Web (Información actual)
- "¿Cuál es el clima actual en Quito, Ecuador?"
- "¿Quién ganó la final de la Champions League más reciente?"
- "Últimas noticias sobre inteligencia artificial"
- "¿Cuál es el precio actual del Bitcoin?"
- "Noticias recientes sobre tecnología"

## 🛠️ Características Técnicas

### Tecnologías Usadas:
- **Backend**: Python + Flask
- **IA**: Google Gemini Pro (via LangChain)
- **Agente**: LangChain con herramientas de búsqueda
- **Búsqueda Web**: DuckDuckGo (sin necesidad de API key)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap

### Funcionalidades del Agente:
1. **Razonamiento**: El agente decide cuándo necesita buscar información
2. **Búsqueda Web**: Usa DuckDuckGo para obtener información actualizada
3. **Síntesis**: Combina la información encontrada para dar una respuesta coherente

## 🔧 Configuración

El archivo `.env` contiene:
```
GOOGLE_API_KEY="AIzaSyCypmLSsEUQ7qoCYZXjy_pbXRKVR1a51D0"
```

## 📋 Dependencias Instaladas

Todas las dependencias ya están instaladas:
- flask
- langchain
- langchain-google-genai
- langchain-community
- python-dotenv
- duckduckgo-search
- google-generativeai

## 🎪 Demo Interactivo

En la interfaz web, puedes:
1. **Usar el botón "Demo Agente"** para ver una demostración automática
2. **Hacer clic en preguntas de ejemplo** para probar rápidamente
3. **Cambiar entre modos** para ver la diferencia
4. **Limpiar el chat** cuando necesites empezar de nuevo

## 🚨 Solución de Problemas

Si hay errores:
1. **Verificar conexión a internet** (necesaria para Gemini y búsquedas)
2. **Revisar que la API key esté configurada** en el archivo `.env`
3. **Comprobar que todas las dependencias estén instaladas**

## 🎯 Próximos Pasos

Esta aplicación es una base sólida que puedes extender con:
- Más herramientas para el agente (calculadora, APIs específicas, etc.)
- Memoria de conversación para recordar interacciones pasadas
- Diferentes modelos de IA (local con Ollama, OpenAI, etc.)
- Autenticación de usuarios
- Base de datos para guardar conversaciones
