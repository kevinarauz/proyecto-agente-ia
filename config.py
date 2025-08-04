# Configuración adicional para la aplicación
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración de la aplicación"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu-clave-secreta-super-segura'
    DEBUG = True
    
    # Google Gemini API (opcional)
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    
    # Ollama/Llama3 settings
    OLLAMA_MODEL = "llama3"
    OLLAMA_BASE_URL = "http://localhost:11434"
    
    # LM Studio settings
    LMSTUDIO_BASE_URL = "http://localhost:1234"
    LMSTUDIO_MODEL = "mistral-7b-instruct-v0.3"
    
    # LangChain settings
    LANGCHAIN_VERBOSE = True
    LANGCHAIN_MAX_ITERATIONS = 3
    
    # Chat settings
    DEFAULT_TEMPERATURE = 0.7
    MAX_TOKENS = 1000
    
    @staticmethod
    def validate_ollama():
        """Validar que Ollama esté disponible"""
        import requests
        try:
            response = requests.get(f"{Config.OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                llama_available = any('llama3' in model.get('name', '') for model in models)
                return llama_available
            else:
                return False
        except Exception as e:
            return False
    
    @staticmethod
    def validate_gemini():
        """Validar que Google Gemini esté disponible"""
        return Config.GOOGLE_API_KEY is not None and Config.GOOGLE_API_KEY.strip() != ""
    
    @staticmethod
    def validate_lmstudio():
        """Validar que LM Studio esté disponible"""
        import requests
        try:
            # Intentar conectar a la API de LM Studio
            response = requests.get(f"{Config.LMSTUDIO_BASE_URL}/v1/models", timeout=5)
            return response.status_code == 200
        except Exception as e:
            return False
    
    @staticmethod
    def validate_config():
        """Validar que al menos un modelo esté disponible"""
        ollama_ok = Config.validate_ollama()
        gemini_ok = Config.validate_gemini()
        lmstudio_ok = Config.validate_lmstudio()
        
        print("🔍 Verificando modelos disponibles...")
        
        if ollama_ok:
            print("✅ Llama3 (Ollama) disponible")
        else:
            print("⚠️ Llama3 (Ollama) no disponible")
            
        if gemini_ok:
            print("✅ Google Gemini disponible")
        else:
            print("⚠️ Google Gemini no disponible (falta GOOGLE_API_KEY)")
            
        if lmstudio_ok:
            print("✅ LM Studio disponible")
        else:
            print("⚠️ LM Studio no disponible")
        
        if not ollama_ok and not gemini_ok and not lmstudio_ok:
            print("❌ Error: No hay modelos disponibles")
            print("💡 Configura al menos uno:")
            print("   - Para Ollama: ollama pull llama3")
            print("   - Para Gemini: añade GOOGLE_API_KEY al archivo .env")
            print("   - Para LM Studio: inicia LM Studio y asegúrate que esté en ejecución en el puerto 1234")
            return False
        
        return True
