# -*- coding: utf-8 -*
from datetime import datetime
from typing import List, Optional
# Importando las clases de los subsistemas

from src.subsystems.user_management import SistemaUsuarios
from src.subsystems.book_catalog import CatalogoLibros
from src.subsystems.loan_system import SistemaPrestamos
from src.subsystems.notification_service import ServicioNotificaciones
from src.models.models import Usuario, Libro, Prestamo

class FachadaBiblioteca:
    def __init__(self):
        self.sistema_usuarios = SistemaUsuarios()
        self.catalogo_libros = CatalogoLibros()
        self.sistema_prestamos = SistemaPrestamos(self.catalogo_libros)
        self.servicio_notificaciones = ServicioNotificaciones()
    
    def registrar_usuario(self, nombre: str, email: str) -> Usuario:
        """Crea un nuevo usuario en el sistema y envía email de bienvenida."""
        usuario = self.sistema_usuarios.crear_usuario(nombre, email)
        
        # Enviar email de bienvenida
        asunto = "Bienvenido a la Biblioteca Digital ITM"
        contenido = (
            f"Hola {nombre},\n\n"
            f"Te damos la bienvenida a nuestra Biblioteca Digital. "
            f"Ya puedes comenzar a explorar nuestro catálogo y solicitar préstamos.\n\n"
            f"Atentamente,\nEquipo de Biblioteca Digital"
        )
        self.servicio_notificaciones.enviar_email(email, asunto, contenido)
        
        return usuario
    
    def agregar_libro(self, titulo: str, autor: str, isbn: str) -> Libro:
        """Agrega un nuevo libro al catálogo."""
        return self.catalogo_libros.agregar_libro(titulo, autor, isbn)
    
    def buscar_libro(self, titulo: str) -> List[Libro]:
        """Busca libros por título."""
        return self.catalogo_libros.buscar_por_titulo(titulo)
    
    def realizar_prestamo(self, id_usuario: int, id_libro: int) -> Optional[Prestamo]:
        """Realiza un préstamo completo: verifica elegibilidad, crea préstamo y notifica."""
        # Verificar si el usuario existe
        usuario = self.sistema_usuarios.buscar_usuario(id_usuario)
        if not usuario:
            print(f"Usuario {id_usuario} no encontrado")
            return None
        
        # Verificar elegibilidad
        if not self.sistema_prestamos.verificar_elegibilidad(id_usuario):
            print(f"Usuario {id_usuario} no es elegible (tiene préstamos vencidos)")
            return None
        
        # Crear préstamo
        prestamo = self.sistema_prestamos.crear_prestamo(id_usuario, id_libro)
        if not prestamo:
            return None
        
        # Notificar al usuario
        libro_info = self.catalogo_libros.obtener_informacion_detallada(id_libro)
        asunto = f"Confirmación de préstamo: {libro_info.get('titulo', 'Libro')}"
        contenido = (
            f"Estimado/a {usuario.nombre},\n\n"
            f"Confirmamos su préstamo del libro '{libro_info.get('titulo', 'Libro')}'.\n"
            f"Fecha de devolución: {prestamo.fecha_vencimiento.strftime('%d/%m/%Y')}\n\n"
            f"Atentamente,\nSistema de Biblioteca Digital"
        )
        self.servicio_notificaciones.enviar_email(usuario.email, asunto, contenido)
        
        return prestamo
    
    def devolver_libro(self, id_prestamo: int) -> bool:
        """Procesa la devolución de un libro, calcula multas y notifica."""
        # Obtener información del préstamo
        if id_prestamo not in self.sistema_prestamos.prestamos:
            print(f"Préstamo {id_prestamo} no encontrado")
            return False
        
        prestamo = self.sistema_prestamos.prestamos[id_prestamo]
        id_usuario = prestamo.id_usuario
        id_libro = prestamo.id_libro
        
        # Calcular multa antes de finalizar el préstamo
        multa = self.sistema_prestamos.calcular_multa(id_prestamo)
        
        # Finalizar préstamo
        exito = self.sistema_prestamos.finalizar_prestamo(id_prestamo)
        if not exito:
            return False
        
        # Obtener información para la notificación
        usuario = self.sistema_usuarios.buscar_usuario(id_usuario)
        libro_info = self.catalogo_libros.obtener_informacion_detallada(id_libro)
        
        # Notificar al usuario
        asunto = f"Confirmación de devolución: {libro_info.get('titulo', 'Libro')}"
        contenido = (
            f"Estimado/a {usuario.nombre},\n\n"
            f"Confirmamos la devolución del libro '{libro_info.get('titulo', 'Libro')}'.\n"
        )
        
        if multa > 0:
            contenido += f"Se ha generado una multa de ${multa:.2f} por devolución tardía.\n"
        
        contenido += "\nAtentamente,\nSistema de Biblioteca Digital"
        self.servicio_notificaciones.enviar_email(usuario.email, asunto, contenido)
        
        return True
    
    def enviar_recordatorios_vencimiento(self) -> int:
        """Envía recordatorios para préstamos a punto de vencer (3 días o menos)."""
        # Esta función podría ejecutarse diariamente mediante un programador de tareas
        
        contador_notificaciones = 0
        for prestamo in self.sistema_prestamos.prestamos.values():
            # Solo préstamos activos que no han sido devueltos
            if prestamo.fecha_devolucion:
                continue
            
            # Calcular días hasta el vencimiento
            dias_restantes = (prestamo.fecha_vencimiento - datetime.now()).days
            
            # Enviar recordatorio si quedan 3 días o menos
            if 0 <= dias_restantes <= 3:
                usuario = self.sistema_usuarios.buscar_usuario(prestamo.id_usuario)
                if usuario:
                    self.servicio_notificaciones.notificar_vencimiento(prestamo, usuario)
                    contador_notificaciones += 1
        
        return contador_notificaciones