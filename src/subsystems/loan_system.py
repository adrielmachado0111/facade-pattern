from datetime import datetime
from typing import List, Dict, Optional
from src.models.models import Prestamo
from src.subsystems.book_catalog import CatalogoLibros

class SistemaPrestamos:
    def __init__(self, catalogo_libros: CatalogoLibros):
        self.prestamos = {}
        self.contador_id = 1
        self.catalogo = catalogo_libros
    
    def crear_prestamo(self, id_usuario: int, id_libro: int) -> Optional[Prestamo]:
        """Crea un nuevo préstamo si el libro está disponible."""
        libro = self.catalogo.obtener_libro(id_libro)
        if not libro or not libro.disponible:
            print(f"El libro {id_libro} no está disponible para préstamo")
            return None
        
        # Marcar libro como no disponible
        self.catalogo.actualizar_disponibilidad(id_libro, False)
        
        # Crear préstamo
        id_prestamo = self.contador_id
        self.contador_id += 1
        prestamo = Prestamo(id=id_prestamo, id_usuario=id_usuario, id_libro=id_libro)
        self.prestamos[id_prestamo] = prestamo
        
        print(f"Préstamo creado: {prestamo}")
        return prestamo
    
    def finalizar_prestamo(self, id_prestamo: int) -> bool:
        """Finaliza un préstamo y marca el libro como disponible."""
        if id_prestamo not in self.prestamos:
            return False
        
        prestamo = self.prestamos[id_prestamo]
        if prestamo.fecha_devolucion:
            return False  # Ya fue devuelto
        
        # Marcar libro como disponible
        self.catalogo.actualizar_disponibilidad(prestamo.id_libro, True)
        
        # Actualizar fecha de devolución
        prestamo.fecha_devolucion = datetime.now()
        print(f"Préstamo finalizado: {prestamo}")
        
        return True
    
    def calcular_multa(self, id_prestamo: int) -> float:
        """Calcula la multa por devolución tardía."""
        if id_prestamo not in self.prestamos:
            return 0.0
        
        prestamo = self.prestamos[id_prestamo]
        
        # Si ya fue devuelto a tiempo, no hay multa
        if prestamo.fecha_devolucion and prestamo.fecha_devolucion <= prestamo.fecha_vencimiento:
            return 0.0
        
        # Calcular días de retraso
        fecha_limite = prestamo.fecha_vencimiento
        fecha_actual = prestamo.fecha_devolucion or datetime.now()
        
        if fecha_actual <= fecha_limite:
            return 0.0
        
        dias_retraso = (fecha_actual - fecha_limite).days
        tarifa_diaria = 1.5  # Tarifa diaria de multa
        
        return dias_retraso * tarifa_diaria
    
    def extender_plazo(self, id_prestamo: int, dias_adicionales: int) -> bool:
        """Extiende el plazo de devolución de un préstamo."""
        if id_prestamo not in self.prestamos:
            return False
        
        prestamo = self.prestamos[id_prestamo]
        if prestamo.fecha_devolucion or prestamo.esta_vencido:
            return False
        
        prestamo.dias_plazo += dias_adicionales
        print(f"Plazo extendido para préstamo {id_prestamo}. Nueva fecha: {prestamo.fecha_vencimiento}")
        
        return True
    
    def verificar_elegibilidad(self, id_usuario: int) -> bool:
        """Verifica si un usuario es elegible para nuevos préstamos."""
        # Verifica si tiene préstamos vencidos
        prestamos_activos = [p for p in self.prestamos.values() 
                             if p.id_usuario == id_usuario and not p.fecha_devolucion]
        
        return not any(p.esta_vencido for p in prestamos_activos)
    
    def obtener_prestamos_usuario(self, id_usuario: int) -> List[Prestamo]:
        """Obtiene todos los préstamos de un usuario."""
        return [p for p in self.prestamos.values() if p.id_usuario == id_usuario]