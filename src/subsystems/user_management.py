from typing import Optional
from src.models.models import Usuario


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