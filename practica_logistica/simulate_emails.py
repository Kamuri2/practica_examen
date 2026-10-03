import sys
import os
from datetime import datetime

# Make sure we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import db
from app.llm import clasificar_incidente_llm

correos = [
    "El camión TTT-999 se quedó sin frenos y chocó contra la caseta 2.",
    "Guardia reporta que el conductor de GGG-111 venía con aliento alcohólico a la zona de pesaje.",
    "Retraso de 4 horas del proveedor de materiales en el camión XYZ-333 por llanta ponchada.",
    "Fuga de material químico peligroso en el patio de maniobras del camión HHH-777.",
    "Se detectó documentación falsa al intentar ingresar el camión LLL-000 en la Aduana.",
    "Conductor se bajó del camión AAA-999 sin chaleco reflectante en la zona de montacargas.",
    "Volcadura leve en la rampa de acceso sur, camión BBB-222.",
    "El sistema de refrigeración del camión FFF-444 falló y la carga está en riesgo de podrirse.",
    "Exceso de velocidad detectado por radar interno al camión JJJ-555.",
    "Choque entre montacargas y el camión KKK-666 en el andén 4.",
    "El camión NNN-888 llegó fuera de la ventana de horario permitido por 2 horas.",
    "Chofer del camión MMM-123 reporta intento de asalto durante el trayecto antes de llegar a puerta."
]

print("Iniciando inyección de 12 correos reales a través de Ollama...")

for i, correo in enumerate(correos, 1):
    print(f"\nProcesando {i}/12...")
    resultado, latencia, raw, error = clasificar_incidente_llm(correo)
    
    if error:
        print(f"Error de LLM en correo {i}: {error}")
        cat_manual = "Otro"
        if "choque" in correo.lower() or "accidente" in correo.lower() or "volcadura" in correo.lower():
            cat_manual = "Accidente"
        
        db.incidentes.insert_one({
            "correo_original": correo,
            "estado": "nuevo",
            "clasificacion_manual": cat_manual,
            "metodo": "reglas_fallback",
            "marca_tiempo": datetime.now()
        })
    else:
        print(f"Exito! Categoría: {resultado.categoria} | Latencia: {latencia:.2f}s")
        db.incidentes.insert_one({
            "correo_original": correo,
            "estado": "nuevo",
            "clasificacion": resultado.model_dump(),
            "metodo": "llm",
            "marca_tiempo": datetime.now()
        })
        
        db.evaluaciones_llm.insert_one({
            "prompt": correo,
            "respuesta": raw,
            "modelo": "llama3.2",
            "latencia": latencia,
            "coincidio_reglas": True,
            "marca_tiempo": datetime.now()
        })

print("\n¡Simulación completada! Revisa el Dashboard de Streamlit.")
