import json
import time
import requests
from datetime import datetime
from pydantic import ValidationError
from .models import IncidenteLLM

OLLAMA_API = "http://172.21.240.1:11434/api/generate"
MODEL = "llama3.2" 

def clasificar_incidente_llm(correo_texto: str):
    prompt = f"""
    Eres un asistente de clasificación. Lee el siguiente correo y extrae la información en formato JSON estricto.
    No incluyas texto adicional fuera del JSON.
    El JSON debe tener exactamente las siguientes llaves:
    - "categoria": (Accidente, Infracción, Retraso, Otro)
    - "prioridad": (Alta, Media, Baja)
    - "entidades": (Lista de strings con placas, nombres o lugares)
    - "resumen": (Breve resumen de 1-2 oraciones)
    
    Correo:
    "{correo_texto}"
    """
    
    start_time = time.time()
    try:
        response = requests.post(OLLAMA_API, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        respuesta_texto = data.get("response", "{}")
        
        json_obj = json.loads(respuesta_texto)
        incidente_validado = IncidenteLLM(**json_obj)
        latencia = time.time() - start_time
        
        return incidente_validado, latencia, respuesta_texto, None
        
    except ValidationError as ve:
        latencia = time.time() - start_time
        return None, latencia, respuesta_texto, f"Error de validación Pydantic: {ve}"
    except Exception as e:
        latencia = time.time() - start_time
        return None, latencia, str(e), f"Error de conexión con Ollama: {e}"

def consultar_rag(pregunta: str, contexto: str):
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
    Eres un asistente analista experto en logística. 
    Tu única tarea es leer la siguiente información sobre incidentes y responder a la pregunta del operador.
    Actúa como si TÚ ya tuvieras toda la información. NUNCA digas "no tengo acceso a la base de datos". NUNCA digas "te ofrezco una forma de estructurarlo".
    
    INFORMACIÓN DISPONIBLE (Estos son los incidentes reales que debes usar):
    {contexto}
    
    INSTRUCCIONES:
    1. Responde directamente a la pregunta usando SOLO la INFORMACIÓN DISPONIBLE.
    2. Si el operador pide un "reporte" o "resumen", NO le enseñes cómo hacer un reporte. HAZ EL REPORTE TÚ MISMO utilizando los datos de arriba. (Ejemplo: "Hoy se reportaron X incidentes: El camión MMM tuvo un asalto...").
    3. No agregues saludos largos ni disculpas. Ve directo al grano.
    4. La fecha actual es {fecha_actual}.
    
    Pregunta del operador: {pregunta}
    Respuesta:
    """
    try:
        response = requests.post(OLLAMA_API, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }, timeout=30)
        response.raise_for_status()
        return response.json().get("response", "Error leyendo respuesta.")
    except Exception as e:
        return f"Error consultando al LLM: {e}"
