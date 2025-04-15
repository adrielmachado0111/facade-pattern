from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Clases de datos para entidades
@dataclass
class Usuario:
    id: int
    nombre: str
    email: str
    fecha_registro: datetime = field(default_factory=datetime.now)
    activo: bool = True
    
    def __str__(self):
        return f"Usuario(id={self.id}, nombre='{self.nombre}', email='{self.email}')"

@dataclass
class Libro:
    id: int
    titulo: str
    autor: str
    isbn: str
    disponible: bool = True
    
    def __str__(self):
        estado = "disponible" if self.disponible else "no disponible"
        return f"Libro(id={self.id}, '{self.titulo}' por {self.autor}, {estado})"

@dataclass
class Prestamo:
    id: int
    id_usuario: int
    id_libro: int
    fecha_prestamo: datetime = field(default_factory=datetime.now)
    fecha_devolucion: Optional[datetime] = None
    dias_plazo: int = 14
    
    @property
    def fecha_vencimiento(self) -> datetime:
        return self.fecha_prestamo + timedelta(days=self.dias_plazo)
    
    @property
    def esta_vencido(self) -> bool:
        return not self.fecha_devolucion and datetime.now() > self.fecha_vencimiento
    
    def __str__(self):
        estado = "activo" if not self.fecha_devolucion else "devuelto"
        return f"Prestamo(id={self.id}, libro={self.id_libro}, usuario={self.id_usuario}, {estado})"