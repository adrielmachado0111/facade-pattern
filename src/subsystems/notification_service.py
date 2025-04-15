from datetime import datetime
import uuid
from typing import List
from src.models.models import Usuario, Prestamo
# Servicio de Notificaciones

class ServicioNotificaciones:
    def __init__(self):
        self.notificaciones_enviadas = []
    
    def enviar_email(self, destinatario: str, asunto: str, contenido: str) -> bool:
        """Envía un email a un usuario."""
        # En un sistema real, aquí se conectaría con un servicio de email
        notificacion = {
            "tipo": "email",
            "destinatario": destinatario,
            "asunto": asunto,
            "contenido": contenido,
            "fecha": datetime.now(),
            "id": str(uuid.uuid4())
        }
        self.notificaciones_enviadas.append(notificacion)
        print(f"Email enviado a {destinatario}: {asunto}")
        return True
    
    def enviar_sms(self, numero: str, mensaje: str) -> bool:
        """Envía un SMS a un usuario."""
        # En un sistema real, aquí se conectaría con un servicio de SMS
        notificacion = {
            "tipo": "sms",
            "destinatario": numero,
            "contenido": mensaje,
            "fecha": datetime.now(),
            "id": str(uuid.uuid4())
        }
        self.notificaciones_enviadas.append(notificacion)
        print(f"SMS enviado a {numero}: {mensaje[:20]}...")
        return True
    
    def programar_recordatorio(self, id_usuario: int, fecha: datetime, mensaje: str) -> bool:
        """Programa un recordatorio para un usuario."""
        # En un sistema real, esto se guardaría en una cola de tareas programadas
        notificacion = {
            "tipo": "recordatorio",
            "id_usuario": id_usuario,
            "fecha_programada": fecha,
            "mensaje": mensaje,
            "fecha_creacion": datetime.now(),
            "id": str(uuid.uuid4())
        }
        self.notificaciones_enviadas.append(notificacion)
        print(f"Recordatorio programado para usuario {id_usuario} el {fecha}")
        return True
    
    def notificar_vencimiento(self, prestamo: Prestamo, usuario: Usuario) -> bool:
        """Notifica a un usuario sobre un préstamo a punto de vencer."""
        dias_restantes = (prestamo.fecha_vencimiento - datetime.now()).days
        
        asunto = f"Recordatorio: Devolución de libro '{prestamo.id_libro}'"
        contenido = (
            f"Estimado/a {usuario.nombre},\n\n"
            f"Le recordamos que su préstamo vencerá en {dias_restantes} días.\n"
            f"Por favor, devuelva el libro a tiempo para evitar multas.\n\n"
            f"Atentamente,\nSistema de Biblioteca Digital"
        )
        
        return self.enviar_email(usuario.email, asunto, contenido)