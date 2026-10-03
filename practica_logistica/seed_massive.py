import pymongo
from datetime import datetime, timedelta
import random

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client.logismart_db

# Clear existing
db.accesos.delete_many({})
db.camiones.delete_many({})
db.evaluaciones_llm.delete_many({})
db.incidentes.delete_many({})
db.riesgos_eticos.delete_many({})

print("Colecciones limpias. Insertando datos de prueba masivos...")

empresas = ["Logistica Sur", "TransNorte", "Quimicos Express", "Aceros y Mas", "Carga Pesada S.A.", "Transportes Globales", "Ruta Rapida", "Distribuidora del Centro"]
operadores = ["juan.perez", "ana.gomez", "carlos.ruiz", "luisa.martinez", "roberto.sanchez"]

# 1. Generar 30 Camiones
camiones = []
for i in range(1, 31):
    placa = f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}-{random.randint(100, 999)}"
    camion_id = f"CAM-{i:03d}"
    empresa = random.choice(empresas)
    aut = random.choice([True, True, True, False]) # 75% autorizados
    cert = random.choice([True, True, False]) # 66% certificados
    camiones.append({"placa": placa, "camion_id": camion_id, "empresa": empresa, "autorizacion": aut, "certificacion_conductor": cert})

db.camiones.insert_many(camiones)

# 2. Generar 50 Accesos con diferentes combinaciones
accesos = []
for i in range(50):
    P = random.choice([True, True, True, False])
    S = random.choice([True, True, False])
    V = random.choice([True, True, False])
    Q = random.choice([False, False, False, False, True]) # 20% robos
    R = random.choice([False, False, True]) # 33% material peligroso
    H = random.choice([True, True, False])
    
    A = P and S and (not Q) and V and ((not R) or H)
    E = P and (R or Q) or (P and not V)
    
    explicacion = []
    if A:
        explicacion.append("Se concedió acceso (A) porque: tiene permiso (P), inspección aprobada (S), no hay reporte de robo (!Q), tiene certificación vigente (V) y cumple condición de horario/material (!R o H).")
    else:
        motivos = []
        if not P: motivos.append("no tiene permiso")
        if not S: motivos.append("falló inspección")
        if Q: motivos.append("tiene reporte de robo")
        if not V: motivos.append("no tiene certificación vigente")
        if R and not H: motivos.append("trae material peligroso fuera de horario")
        explicacion.append("Se denegó acceso (A) porque: " + ", ".join(motivos) + ".")

    if E:
        motivos_e = []
        if P and R: motivos_e.append("tiene permiso y trae material peligroso")
        if P and Q: motivos_e.append("tiene reporte de robo")
        if P and not V: motivos_e.append("no tiene certificación vigente")
        explicacion.append("Se envió a inspección especial (E) porque: " + ", ".join(motivos_e) + ".")

    dias_atras = random.randint(0, 15)
    horas_atras = random.randint(0, 23)
    marca = datetime.now() - timedelta(days=dias_atras, hours=horas_atras)
    
    accesos.append({
        "P": P, "Q": Q, "R": R, "S": S, "V": V, "H": H,
        "resultado_A": A, "resultado_E": E,
        "explicacion": " ".join(explicacion),
        "marca_tiempo": marca,
        "operador": random.choice(operadores)
    })

db.accesos.insert_many(accesos)

# 3. Generar 15 Incidentes
plantillas_incidentes = [
    ("URGENTE: El camión {placa} acaba de chocar en la entrada {lugar}, hay humo.", "Accidente", "Alta", "Choque con humo."),
    ("Notificación: El conductor de {placa} llegó tarde a la revisión en {lugar}.", "Retraso", "Baja", "Llegada tarde a revisión."),
    ("Alerta: El guardia detectó que {placa} traía documentación falsa en {lugar}.", "Infracción", "Alta", "Documentación falsa detectada."),
    ("Aviso: Fuga de aceite leve en el camión {placa} estacionado en {lugar}.", "Otro", "Media", "Fuga de aceite detectada."),
    ("Emergencia médica: Conductor de {placa} se desmayó cerca de {lugar}.", "Accidente", "Alta", "Emergencia médica del conductor."),
    ("Problema logístico: {placa} bloqueando la salida de {lugar}.", "Retraso", "Media", "Camión bloqueando salida."),
    ("Incidente de seguridad: Intento de acceso no autorizado por {placa} en {lugar}.", "Infracción", "Alta", "Intento de acceso no autorizado.")
]
lugares = ["Puerta Norte", "Zona de Descarga A", "Báscula 1", "Aduana", "Patio Central", "Salida Sur"]

incidentes = []
for i in range(15):
    cam = random.choice(camiones)['placa']
    lug = random.choice(lugares)
    plantilla, cat, prio, res = random.choice(plantillas_incidentes)
    correo = plantilla.format(placa=cam, lugar=lug)
    
    dias = random.randint(0, 10)
    estado = random.choice(["nuevo", "en_atencion", "cerrado"])
    
    incidentes.append({
        "correo_original": correo,
        "estado": estado,
        "clasificacion": {
            "categoria": cat,
            "prioridad": prio,
            "entidades": [cam, lug],
            "resumen": res
        },
        "metodo": random.choice(["llm", "reglas_fallback"]),
        "marca_tiempo": datetime.now() - timedelta(days=dias)
    })

db.incidentes.insert_many(incidentes)

# 4. Generar Riesgos Eticos (Más variados)
riesgos = [
    {"modulo": "Clasificador LLM", "descripcion": "Sesgo socioeconómico al penalizar correos con mala ortografía o jerga.", "categoria": "Sesgo", "probabilidad": 4, "impacto": 3, "mitigacion": "Normalización de texto antes del LLM."},
    {"modulo": "Asistente RAG", "descripcion": "Alucinación de motivos de rechazo cuando no se encuentra el registro del camión.", "categoria": "Alucinación", "probabilidad": 2, "impacto": 5, "mitigacion": "Instrucción de no inventar si el contexto está vacío."},
    {"modulo": "Módulo de Accesos", "descripcion": "Exposición de datos médicos o personales del conductor en la bitácora de justificaciones.", "categoria": "Privacidad", "probabilidad": 3, "impacto": 4, "mitigacion": "Anonimizar identificadores personales."},
    {"modulo": "Motor de Reglas", "descripcion": "Exclusión sistemática de transportistas pequeños que no pueden costear certificación express.", "categoria": "Sesgo", "probabilidad": 4, "impacto": 2, "mitigacion": "Revisar políticas de certificación con proveedores."},
    {"modulo": "Sistema General", "descripcion": "Exceso de confianza en la automatización; los guardias dejan de revisar físicamente porque 'el sistema dice que A es verde'.", "categoria": "Dependencia", "probabilidad": 5, "impacto": 5, "mitigacion": "Auditorías aleatorias obligatorias ignorando el sistema."}
]
db.riesgos_eticos.insert_many(riesgos)

# 5. Evaluaciones LLM (Histórico)
evaluaciones = []
for i in range(10):
    evaluaciones.append({
        "prompt": "Ejemplo de correo procesado...",
        "respuesta": '{"categoria": "Otro", "prioridad": "Baja", "entidades": [], "resumen": "Ok"}',
        "modelo": "llama3.2",
        "latencia": round(random.uniform(1.2, 4.5), 2),
        "coincidio_reglas": random.choice([True, True, True, False]),
        "marca_tiempo": datetime.now() - timedelta(days=random.randint(1, 5))
    })
db.evaluaciones_llm.insert_many(evaluaciones)

print("¡Semilla masiva completada exitosamente!")
