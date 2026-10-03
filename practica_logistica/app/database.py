import os
from pymongo import MongoClient

# Conexión a base de datos local
MONGO_URI = "mongodb://localhost:27017/"

class Database:
    def __init__(self):
        try:
            self.client = MongoClient(MONGO_URI)
            self.db = self.client.logismart_db
            # Collections
            self.camiones = self.db.camiones
            self.accesos = self.db.accesos
            self.incidentes = self.db.incidentes
            self.riesgos_eticos = self.db.riesgos_eticos
            self.evaluaciones_llm = self.db.evaluaciones_llm
            print("Connected to MongoDB Local (logismart_db)!")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")

db = Database()
