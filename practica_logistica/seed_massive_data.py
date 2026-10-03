from pymongo import MongoClient
import random
from datetime import datetime, timedelta

# Conectar a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["logismart_db"]

# Limpiar para no duplicar masivamente
db.incidentes.delete_many({"estado": "simulado_masivo"})
db.accesos.delete_many({"operador": "simulado_masivo"})

placas_base = ["ABC-123", "XYZ-987", "DEF-456", "TRK-001", "GHI-789", "SIM-001", "DEC-345"]

# Generar 40 Incidentes variados
incidentes = []
categorias = ["Accidente", "Infracción", "Retraso", "Otro"]
prioridades = ["Alta", "Media", "Baja"]

ejemplos_texto = [
    "Choque en la zona de carga norte, el camión {placa} derribó un poste.",
    "El conductor de {placa} llegó con 2 horas de retraso por tráfico en la carretera.",
    "Se detectó exceso de velocidad en el radar interno por parte de {placa}.",
    "Fuga de aceite del motor en el camión {placa} cerca de la aduana.",
    "El guardia reporta que {placa} intentó ingresar sin los papeles en regla.",
    "Llantas ponchadas en {placa}, bloqueando el carril principal por 40 minutos.",
    "Conductor de {placa} con actitud agresiva hacia el personal de seguridad.",
    "Derrame químico menor en la zona de maniobras causado por {placa}."
]

for i in range(40):
    cat = random.choice(categorias)
    prio = random.choice(prioridades)
    placa = random.choice(placas_base)
    texto = random.choice(ejemplos_texto).format(placa=placa)
    
    # Random date within the last 3 days
    fecha = datetime.now() - timedelta(days=random.randint(0, 3), hours=random.randint(1, 12))
    
    incidentes.append({
        "correo_original": texto,
        "estado": "simulado_masivo", # Para distinguirlos
        "clasificacion": {
            "categoria": cat,
            "prioridad": prio,
            "entidades": [placa, "Guardia", "Zona de Carga"],
            "resumen": texto
        },
        "metodo": "seed",
        "marca_tiempo": fecha
    })

if incidentes:
    db.incidentes.insert_many(incidentes)

# Generar 50 Accesos variados
accesos = []
for i in range(50):
    placa = random.choice(placas_base)
    fecha = datetime.now() - timedelta(days=random.randint(0, 3), hours=random.randint(1, 12))
    
    aprobado = random.choice([True, False])
    motivo = "Todo en regla" if aprobado else random.choice(["Sin permiso", "Licencia vencida", "Fuera de horario"])
    
    accesos.append({
        "placa": placa,
        "P": random.choice([True, False]),
        "Q": random.choice([True, False]),
        "R": random.choice([True, False]),
        "S": random.choice([True, False]),
        "V": random.choice([True, False]),
        "H": random.choice([True, False]),
        "resultado_A": aprobado,
        "resultado_E": random.choice([True, False]),
        "explicacion": motivo,
        "marca_tiempo": fecha,
        "operador": "simulado_masivo"
    })

if accesos:
    db.accesos.insert_many(accesos)

print("¡Se inyectaron 40 incidentes y 50 accesos simulados exitosamente!")
