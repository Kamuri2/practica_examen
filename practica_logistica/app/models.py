from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class Camion(BaseModel):
    placa: str
    camion_id: str
    empresa: str
    autorizacion: bool
    certificacion_conductor: bool

class Acceso(BaseModel):
    P: bool
    Q: bool
    R: bool
    S: bool
    V: bool # Vigencia certificacion
    H: bool # Horario permitido
    resultado_A: bool
    resultado_E: bool
    marca_tiempo: datetime = Field(default_factory=datetime.now)
    operador: str
    explicacion: str

class IncidenteLLM(BaseModel):
    categoria: str = Field(description="Categoría del incidente: Accidente, Infracción, Retraso, Otro")
    prioridad: str = Field(description="Prioridad: Alta, Media, Baja")
    entidades: List[str] = Field(description="Entidades mencionadas: placas, nombres, lugares")
    resumen: str = Field(description="Breve resumen del incidente")

class Incidente(BaseModel):
    correo_original: str
    clasificacion: Optional[IncidenteLLM] = None
    datos_extraidos: Dict = Field(default_factory=dict)
    estado: str = "nuevo" # nuevo, en_atencion, cerrado
    marca_tiempo: datetime = Field(default_factory=datetime.now)

class RiesgoEtico(BaseModel):
    modulo: str
    descripcion: str
    categoria: str
    probabilidad: int = Field(ge=1, le=5)
    impacto: int = Field(ge=1, le=5)
    mitigacion: str
    historico: List[str] = Field(default_factory=list)

class EvaluacionLLM(BaseModel):
    prompt: str
    respuesta: str
    modelo: str
    latencia: float
    coincidio_reglas: bool
    marca_tiempo: datetime = Field(default_factory=datetime.now)
