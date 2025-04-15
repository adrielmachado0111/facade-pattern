from typing import List, Dict, Optional
from src.models.models import Libro

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
