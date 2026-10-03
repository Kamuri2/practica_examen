import pymongo
from datetime import datetime, timedelta

# Connect to local MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client.logismart_db

# Clear existing data
db.accesos.delete_many({})
db.camiones.delete_many({})
db.evaluaciones_llm.delete_many({})
db.incidentes.delete_many({})
db.riesgos_eticos.delete_many({})

print("Colecciones limpias. Insertando datos de prueba...")

# 1. Camiones
camiones = [
    {"placa": "ABC-123", "camion_id": "CAM-001", "empresa": "Logistica Sur", "autorizacion": True, "certificacion_conductor": True},
    {"placa": "XYZ-987", "camion_id": "CAM-002", "empresa": "TransNorte", "autorizacion": False, "certificacion_conductor": True},
    {"placa": "LMN-456", "camion_id": "CAM-003", "empresa": "Quimicos Express", "autorizacion": True, "certificacion_conductor": False},
]
db.camiones.insert_many(camiones)

# 2. Accesos
accesos = [
    {
        "P": True, "Q": False, "R": False, "S": True, "V": True, "H": True,
        "resultado_A": True, "resultado_E": False,
        "explicacion": "Se concedió acceso (A) porque: tiene permiso (P), inspección aprobada (S), no hay reporte de robo (!Q), tiene certificación vigente (V) y cumple condición de horario/material (!R o H).",
        "marca_tiempo": datetime.now() - timedelta(days=2),
        "operador": "juan.perez"
    },
    {
        "P": True, "Q": False, "R": True, "S": True, "V": True, "H": False,
        "resultado_A": False, "resultado_E": True,
        "explicacion": "Se denegó acceso (A) porque: trae material peligroso fuera de horario permitido (R y !H). Se envió a inspección especial (E) porque: tiene permiso y trae material peligroso (P y R).",
        "marca_tiempo": datetime.now() - timedelta(hours=5),
        "operador": "ana.gomez"
    },
    {
        "P": False, "Q": True, "R": False, "S": False, "V": False, "H": True,
        "resultado_A": False, "resultado_E": False,
        "explicacion": "Se denegó acceso (A) porque: no tiene permiso (P), falló inspección (S), tiene reporte de robo (Q), no tiene certificación vigente (V).",
        "marca_tiempo": datetime.now() - timedelta(minutes=30),
        "operador": "carlos.ruiz"
    }
]
db.accesos.insert_many(accesos)

# 3. Incidentes
incidentes = [
    {
        "correo_original": "URGENTE: El camión ABC-123 acaba de chocar en la entrada principal, hay humo.",
        "estado": "nuevo",
        "clasificacion": {
            "categoria": "Accidente",
            "prioridad": "Alta",
            "entidades": ["ABC-123", "entrada principal"],
            "resumen": "Choque con humo en la entrada principal."
        },
        "metodo": "llm",
        "marca_tiempo": datetime.now() - timedelta(days=1)
    },
    {
        "correo_original": "Notificación: El conductor de XYZ-987 llegó 3 horas tarde a la revisión.",
        "estado": "en_atencion",
        "clasificacion": {
            "categoria": "Retraso",
            "prioridad": "Baja",
            "entidades": ["XYZ-987"],
            "resumen": "Llegada con 3 horas de retraso."
        },
        "metodo": "llm",
        "marca_tiempo": datetime.now() - timedelta(hours=2)
    }
]
db.incidentes.insert_many(incidentes)

# 4. Riesgos Eticos
riesgos = [
    {
        "modulo": "Clasificador LLM",
        "descripcion": "El LLM puede clasificar incorrectamente un correo por sesgo en la forma de escritura del operador (ej. faltas de ortografía).",
        "categoria": "Sesgo",
        "probabilidad": 4,
        "impacto": 3,
        "mitigacion": "Implementar pre-procesamiento de texto y fallback a reglas manuales."
    },
    {
        "modulo": "Asistente RAG",
        "descripcion": "El LLM podría alucinar y dar explicaciones falsas sobre el acceso denegado si el RAG falla en recuperar el contexto correcto.",
        "categoria": "Alucinación",
        "probabilidad": 2,
        "impacto": 5,
        "mitigacion": "Prompt estricto que obligue a responder 'No tengo información' si no hay contexto."
    },
    {
        "modulo": "Base de Datos",
        "descripcion": "Exposición de datos personales del conductor al registrar accesos e incidentes.",
        "categoria": "Privacidad",
        "probabilidad": 3,
        "impacto": 4,
        "mitigacion": "Anonimizar nombres en logs y aplicar controles de acceso basados en roles."
    }
]
db.riesgos_eticos.insert_many(riesgos)

# 5. Evaluaciones LLM
evaluaciones = [
    {
        "prompt": "URGENTE: El camión ABC-123 acaba de chocar en la entrada principal, hay humo.",
        "respuesta": "{\"categoria\": \"Accidente\", \"prioridad\": \"Alta\", \"entidades\": [\"ABC-123\", \"entrada principal\"], \"resumen\": \"Choque con humo en la entrada principal.\"}",
        "modelo": "llama3.2",
        "latencia": 1.45,
        "coincidio_reglas": True,
        "marca_tiempo": datetime.now() - timedelta(days=1)
    }
]
db.evaluaciones_llm.insert_many(evaluaciones)

print("¡Datos de prueba insertados exitosamente en localhost:27017/logismart_db!")
