# Configuración adicional para la aplicación
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración de la aplicación"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu-clave-secreta-super-segura'
    DEBUG = True
    
    # Google Gemini API
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    
    # LangChain settings
    LANGCHAIN_VERBOSE = True
    LANGCHAIN_MAX_ITERATIONS = 3
    
    # Chat settings
    DEFAULT_TEMPERATURE = 0.7
    MAX_TOKENS = 1000
    
    @staticmethod
    def validate_config():
        """Validar que todas las configuraciones necesarias estén presentes"""
        if not Config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY no está configurada en el archivo .env")
        
        print("✅ Configuración validada correctamente")
        print(f"🔑 API Key configurada: {Config.GOOGLE_API_KEY[:10]}...")
        
        return True
