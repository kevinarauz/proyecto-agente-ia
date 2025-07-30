#!/usr/bin/env python3
"""Script de prueba para verificar la configuración de modelos"""

import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI

# Cargar variables de entorno
load_dotenv()

def test_models():
    """Probar la configuración de ambos modelos"""
    models = {}
    
    print("🤖 Probando configuración de modelos...")
    
    # Probar Llama3
    try:
        models['llama3'] = ChatOllama(model="llama3", temperature=0.7)
        # Hacer una prueba simple
        response = models['llama3'].invoke("Hola, ¿cómo estás?")
        print("✅ Llama3 funcionando correctamente")
        print(f"   Respuesta: {response.content[:50]}...")
    except Exception as e:
        print(f"⚠️ Llama3 no disponible: {e}")
        models['llama3'] = None
    
    # Probar Gemini
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
            models['gemini-1.5-flash'] = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash", 
                temperature=0.7
            )
            # Hacer una prueba simple
            response = models['gemini-1.5-flash'].invoke("Hola, ¿cómo estás?")
            print("✅ Gemini 1.5 Flash funcionando correctamente")
            print(f"   Respuesta: {response.content[:50]}...")
        else:
            print("⚠️ Gemini no disponible: No se encontró GOOGLE_API_KEY")
            models['gemini-1.5-flash'] = None
    except Exception as e:
        print(f"⚠️ Gemini no disponible: {e}")
        models['gemini-1.5-flash'] = None
    
    # Mostrar resumen
    available = [k for k, v in models.items() if v is not None]
    print(f"\n🎯 Modelos disponibles: {', '.join(available) if available else 'Ninguno'}")
    
    return models

if __name__ == "__main__":
    test_models()
