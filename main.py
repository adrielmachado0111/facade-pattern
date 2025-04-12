from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid

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

# SUBSISTEMAS

# Subsistema 1: Gestión de Usuarios
class SistemaUsuarios:
    def __init__(self):
        self.usuarios = {}
        self.contador_id = 1
    
    def crear_usuario(self, nombre: str, email: str) -> Usuario:
        """Crea un nuevo usuario en el sistema."""
        id_usuario = self.contador_id
        self.contador_id += 1
        usuario = Usuario(id=id_usuario, nombre=nombre, email=email)
        self.usuarios[id_usuario] = usuario
        print(f"Usuario creado: {usuario}")
        return usuario
    
    def buscar_usuario(self, id_usuario: int) -> Optional[Usuario]:
        """Busca un usuario por su ID."""
        return self.usuarios.get(id_usuario)
    
    def actualizar_usuario(self, usuario: Usuario) -> bool:
        """Actualiza la información de un usuario existente."""
        if usuario.id in self.usuarios:
            self.usuarios[usuario.id] = usuario
            return True
        return False
    
    def validar_credenciales(self, email: str, clave: str) -> bool:
        """Valida las credenciales de un usuario para iniciar sesión."""
        # En un sistema real, aquí se verificaría la contraseña hasheada
        return any(u.email == email and u.activo for u in self.usuarios.values())

# Subsistema 2: Catálogo de Libros
class CatalogoLibros:
    def __init__(self):
        self.libros = {}
        self.contador_id = 1
    
    def agregar_libro(self, titulo: str, autor: str, isbn: str) -> Libro:
        """Agrega un nuevo libro al catálogo."""
        id_libro = self.contador_id
        self.contador_id += 1
        libro = Libro(id=id_libro, titulo=titulo, autor=autor, isbn=isbn)
        self.libros[id_libro] = libro
        print(f"Libro agregado: {libro}")
        return libro
    
    def buscar_por_titulo(self, titulo: str) -> List[Libro]:
        """Busca libros por título."""
        return [libro for libro in self.libros.values() 
                if titulo.lower() in libro.titulo.lower()]
    
    def buscar_por_autor(self, autor: str) -> List[Libro]:
        """Busca libros por autor."""
        return [libro for libro in self.libros.values() 
                if autor.lower() in libro.autor.lower()]
    
    def obtener_libro(self, id_libro: int) -> Optional[Libro]:
        """Obtiene un libro por su ID."""
        return self.libros.get(id_libro)
    
    def actualizar_disponibilidad(self, id_libro: int, disponible: bool) -> bool:
        """Actualiza la disponibilidad de un libro."""
        if id_libro in self.libros:
            self.libros[id_libro].disponible = disponible
            return True
        return False
    
    def obtener_informacion_detallada(self, id_libro: int) -> Dict:
        """Obtiene información detallada de un libro."""
        libro = self.obtener_libro(id_libro)
        if not libro:
            return {}
        
        return {
            "id": libro.id,
            "titulo": libro.titulo,
            "autor": libro.autor,
            "isbn": libro.isbn,
            "disponible": libro.disponible
        }

# Subsistema 3: Sistema de Préstamos
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

# Subsistema 4: Servicio de Notificaciones
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

# PATRÓN FACADE
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
        asunto = "Bienvenido a la Biblioteca Digital"
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

# Ejemplo de uso
if __name__ == "__main__":
    # Crear fachada
    biblioteca = FachadaBiblioteca()
    
    # Registrar usuarios
    usuario1 = biblioteca.registrar_usuario("Ana García", "ana@example.com")
    usuario2 = biblioteca.registrar_usuario("Carlos López", "carlos@example.com")
    
    # Agregar libros
    libro1 = biblioteca.agregar_libro("Cien años de soledad", "Gabriel García Márquez", "9780307474728")
    libro2 = biblioteca.agregar_libro("El código Da Vinci", "Dan Brown", "9780307474536")
    libro3 = biblioteca.agregar_libro("Harry Potter y la piedra filosofal", "J.K. Rowling", "9788478884957")
    
    # Buscar libros
    print("\nBúsqueda de libros:")
    resultados = biblioteca.buscar_libro("código")
    for libro in resultados:
        print(f"Encontrado: {libro}")
    
    # Realizar préstamos
    print("\nRealizando préstamos:")
    prestamo1 = biblioteca.realizar_prestamo(usuario1.id, libro1.id)
    prestamo2 = biblioteca.realizar_prestamo(usuario2.id, libro3.id)
    
    # Intentar prestar un libro ya prestado
    print("\nIntentando prestar un libro no disponible:")
    prestamo_fallido = biblioteca.realizar_prestamo(usuario2.id, libro1.id)
    
    # Devolver un libro
    print("\nDevolviendo libro:")
    biblioteca.devolver_libro(prestamo1.id)
    
    # Enviar recordatorios de vencimiento
    print("\nEnviando recordatorios de vencimiento:")
    notificaciones_enviadas = biblioteca.enviar_recordatorios_vencimiento()
    print(f"Se enviaron {notificaciones_enviadas} recordatorios de vencimiento")