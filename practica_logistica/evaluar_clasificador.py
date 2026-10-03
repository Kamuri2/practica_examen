import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from app.llm import clasificar_incidente_llm

# Conjunto de datos etiquetado a mano (30 correos)
datos_prueba = [
    ("Choque muy fuerte en la puerta principal, necesitamos ayuda", "Accidente"),
    ("El chofer llegó 2 horas después de su turno", "Retraso"),
    ("El guardia reportó que traía licencia vencida", "Infracción"),
    ("Fuga de agua en el patio 3", "Otro"),
    ("Volcadura de un camión en la aduana", "Accidente"),
    ("Retraso por tráfico en la carretera federal", "Retraso"),
    ("Se saltó la pluma de seguridad sin permiso", "Infracción"),
    ("El camión tiene una llanta ponchada", "Otro"),
    ("Colisión múltiple cerca de la báscula", "Accidente"),
    ("Llegada tardía por problemas mecánicos", "Retraso"),
    ("Exceso de velocidad dentro de las instalaciones", "Infracción"),
    ("Derrame de aceite leve", "Otro"),
    ("Atropello en la zona de descarga", "Accidente"),
    ("Demora en el punto de revisión", "Retraso"),
    ("Conductor sin equipo de protección personal", "Infracción"),
    ("Ruido extraño en el motor del camión", "Otro"),
    ("Choque contra la barrera de seguridad", "Accidente"),
    ("Llegó fuera de horario permitido", "Retraso"),
    ("Intento de soborno al guardia", "Infracción"),
    ("Luz trasera fundida", "Otro"),
    ("Incendio menor en el remolque", "Accidente"),
    ("Esperando asignación de andén por más de 1 hora", "Retraso"),
    ("Estacionamiento en zona prohibida", "Infracción"),
    ("Falta de limpieza en el vehículo", "Otro"),
    ("Golpe leve entre dos camiones", "Accidente"),
    ("Retraso en la entrega de documentos", "Retraso"),
    ("Documentación falsa o alterada", "Infracción"),
    ("Falta de rotulación de material peligroso", "Infracción"),
    ("Chofer reporta malestar estomacal", "Otro"),
    ("Accidente grave con heridos", "Accidente")
]

def evaluar():
    print("Iniciando evaluación del clasificador híbrido (LLM + Reglas)...")
    y_true = []
    y_pred = []
    latencias = []

    for idx, (correo, etiqueta_real) in enumerate(datos_prueba, 1):
        y_true.append(etiqueta_real)
        
        # Llamar al LLM
        resultado, latencia, raw, error = clasificar_incidente_llm(correo)
        latencias.append(latencia)
        
        if error:
            # Fallback a reglas
            if "choque" in correo.lower() or "accidente" in correo.lower() or "volcadura" in correo.lower():
                pred = "Accidente"
            elif "retraso" in correo.lower() or "tarde" in correo.lower() or "demora" in correo.lower():
                pred = "Retraso"
            elif "licencia" in correo.lower() or "sin permiso" in correo.lower() or "infracción" in correo.lower():
                pred = "Infracción"
            else:
                pred = "Otro"
            print(f"[{idx}/30] Fallback a reglas -> Pred: {pred} | Real: {etiqueta_real}")
        else:
            pred = resultado.categoria
            print(f"[{idx}/30] LLM -> Pred: {pred} | Real: {etiqueta_real} | Lat: {latencia:.2f}s")
            
        y_pred.append(pred)

    exactitud = accuracy_score(y_true, y_pred)
    latencia_media = sum(latencias) / len(latencias)
    
    print("-" * 50)
    print(f"MÉTRICAS DE RENDIMIENTO:")
    print(f"Exactitud (Accuracy): {exactitud:.2%}")
    print(f"Latencia Promedio: {latencia_media:.2f} segundos por correo")
    
    # Matriz de confusión
    etiquetas = ["Accidente", "Retraso", "Infracción", "Otro"]
    cm = confusion_matrix(y_true, y_pred, labels=etiquetas)
    
    # Graficar
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=etiquetas, yticklabels=etiquetas)
    plt.xlabel('Predicción (LLM/Híbrido)')
    plt.ylabel('Valor Real (Etiquetado a mano)')
    plt.title(f'Matriz de Confusión\nExactitud: {exactitud:.2%}')
    plt.savefig('matriz_confusion.png')
    print("Gráfica guardada como 'matriz_confusion.png'.")

if __name__ == "__main__":
    evaluar()
