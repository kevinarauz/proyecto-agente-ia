# Configuración adicional para la aplicación
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración de la aplicación"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu-clave-secreta-super-segura'
    DEBUG = True
    
    # Ollama/Llama3 settings (no requiere API key)
    OLLAMA_MODEL = "llama3"
    OLLAMA_BASE_URL = "http://localhost:11434"
    
    # LangChain settings
    LANGCHAIN_VERBOSE = True
    LANGCHAIN_MAX_ITERATIONS = 3
    
    # Chat settings
    DEFAULT_TEMPERATURE = 0.7
    MAX_TOKENS = 1000
    
    @staticmethod
    def validate_config():
        """Validar que Ollama esté disponible"""
        import requests
        try:
            response = requests.get(f"{Config.OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                llama_available = any('llama3' in model.get('name', '') for model in models)
                if llama_available:
                    print("✅ Configuración validada correctamente")
                    print(f"🦙 Llama3 disponible en Ollama")
                    return True
                else:
                    raise ValueError("Modelo llama3 no encontrado en Ollama")
            else:
                raise ValueError("Ollama no responde correctamente")
        except Exception as e:
            print(f"❌ Error verificando Ollama: {e}")
            print("� Asegúrate de que Ollama esté ejecutándose y tengas llama3 instalado")
            print("🔧 Ejecuta: ollama pull llama3")
            return False
