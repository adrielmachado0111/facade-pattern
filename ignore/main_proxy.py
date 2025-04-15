from abc import ABC, abstractmethod
import time
import json
import hashlib
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import random

# Simulación de una respuesta HTTP
@dataclass
class Response:
    status_code: int
    content: bytes
    headers: Dict[str, str]
    url: str
    elapsed: float  # tiempo de respuesta en segundos

# Simulación de un cliente HTTP
class ClienteHTTP:
    def realizar_solicitud_get(self, url: str) -> Response:
        """Simula una solicitud HTTP GET."""
        print(f"Realizando solicitud HTTP a: {url}")
        
        # Simulamos latencia de red (entre 0.1 y 1 segundo)
        tiempo_respuesta = random.uniform(0.1, 1.0)
        time.sleep(tiempo_respuesta)
        
        # Simular diferentes tipos de contenido según la URL
        if url.endswith(('.jpg', '.png', '.gif')):
            tipo_contenido = f"image/{url.split('.')[-1]}"
            # Simular datos de imagen
            contenido = b"SIMULATED_IMAGE_DATA" * 1000
        elif url.endswith('.json'):
            tipo_contenido = "application/json"
            # Simular respuesta JSON
            datos_json = {
                "id": hash(url) % 10000,
                "name": f"Resource at {url}",
                "timestamp": datetime.now().isoformat(),
                "data": [random.randint(1, 100) for _ in range(10)]
            }
            contenido = json.dumps(datos_json).encode('utf-8')
        elif url.endswith(('.html', '.htm')):
            tipo_contenido = "text/html"
            # Simular HTML
            contenido = f"<html><body><h1>Page at {url}</h1><p>This is a simulated HTML page.</p></body></html>".encode('utf-8')
        elif url.endswith('.xml'):
            tipo_contenido = "application/xml"
            # Simular XML
            contenido = f"<root><item>Simulated XML for {url}</item></root>".encode('utf-8')
        else:
            tipo_contenido = "application/octet-stream"
            contenido = b"SIMULATED_BINARY_DATA" * 100
        
        # Crear encabezados simulados
        headers = {
            "Content-Type": tipo_contenido,
            "Content-Length": str(len(contenido)),
            "Server": "SimulatedServer/1.0",
            "Date": datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
        }
        
        # Devolver respuesta simulada
        return Response(
            status_code=200,
            content=contenido,
            headers=headers,
            url=url,
            elapsed=tiempo_respuesta
        )
    
    def descargar_archivo(self, url: str, destino: str) -> str:
        """Simula la descarga de un archivo a disco."""
        print(f"Descargando archivo desde {url} a {destino}")
        
        # Simular tiempo de descarga
        tiempo_descarga = random.uniform(0.5, 3.0)
        time.sleep(tiempo_descarga)
        
        # En un sistema real, aquí escribiríamos el archivo
        print(f"Archivo descargado en {tiempo_descarga:.2f} segundos")
        
        return destino

# Clase para representar el contenido web descargado
class ContenidoWeb:
    def __init__(self, datos: bytes, tipo_contenido: str, codigo_respuesta: int, 
                 tamano: int, tiempo_carga: float):
        self.datos = datos
        self.tipo_contenido = tipo_contenido
        self.codigo_respuesta = codigo_respuesta
        self.tamano = tamano
        self.tiempo_carga = tiempo_carga
        self.fecha_creacion = datetime.now()
    
    def obtener_como_texto(self) -> str:
        """Devuelve el contenido como texto UTF-8."""
        try:
            return self.datos.decode('utf-8')
        except UnicodeDecodeError:
            return "[Contenido no es texto válido UTF-8]"
    
    def obtener_como_json(self) -> Dict:
        """Intenta parsear el contenido como JSON."""
        try:
            return json.loads(self.obtener_como_texto())
        except json.JSONDecodeError:
            raise ValueError("El contenido no es un JSON válido")
    
    def obtener_como_bytes(self) -> bytes:
        """Devuelve los datos como bytes crudos."""
        return self.datos
    
    def __str__(self) -> str:
        kb_size = self.tamano / 1024
        return f"ContenidoWeb({kb_size:.1f}KB, {self.tipo_contenido}, cargado en {self.tiempo_carga:.2f}s)"

# Elemento para almacenar en caché
class CacheItem:
    def __init__(self, clave: str, valor: Any, tiempo_vida: int = 3600):
        self.clave = clave
        self.valor = valor
        self.timestamp = datetime.now()
        self.tiempo_vida = tiempo_vida  # en segundos
    
    def ha_expirado(self) -> bool:
        """Determina si el elemento ha expirado."""
        tiempo_actual = datetime.now()
        tiempo_expiracion = self.timestamp + timedelta(seconds=self.tiempo_vida)
        return tiempo_actual > tiempo_expiracion
    
    def obtener_edad(self) -> float:
        """Obtiene la edad del elemento en segundos."""
        return (datetime.now() - self.timestamp).total_seconds()
    
    def __str__(self) -> str:
        return f"CacheItem(clave={self.clave}, edad={self.obtener_edad():.1f}s, expira_en={self.tiempo_vida}s)"

# Caché implementado como diccionario
class DictCache:
    def __init__(self, tamano_maximo: int = 100):
        self.datos: Dict[str, CacheItem] = {}
        self.tamano_maximo = tamano_maximo
        self.hits = 0
        self.misses = 0
    
    def obtener(self, clave: str) -> Optional[Any]:
        """Obtiene un valor de la caché si existe y no ha expirado."""
        item = self.datos.get(clave)
        
        # Si no existe o ha expirado
        if not item or item.ha_expirado():
            self.misses += 1
            if item:
                # Eliminar elemento expirado
                del self.datos[clave]
            return None
        
        self.hits += 1
        return item.valor
    
    def guardar(self, clave: str, valor: Any, tiempo_vida: int = 3600) -> bool:
        """Guarda un valor en la caché."""
        # Si alcanzamos el tamaño máximo, eliminar elementos
        if len(self.datos) >= self.tamano_maximo:
            self._limpiar_antiguos(int(self.tamano_maximo * 0.2))  # Eliminar el 20% más antiguo
        
        # Crear y guardar nuevo item
        self.datos[clave] = CacheItem(clave, valor, tiempo_vida)
        return True
    
    def eliminar(self, clave: str) -> bool:
        """Elimina un valor de la caché si existe."""
        if clave in self.datos:
            del self.datos[clave]
            return True
        return False
    
    def _limpiar_antiguos(self, cantidad: int) -> int:
        """Elimina los elementos más antiguos de la caché."""
        if not self.datos:
            return 0
        
        # Ordenar por antigüedad
        items_ordenados = sorted(
            self.datos.items(), 
            key=lambda x: x[1].timestamp
        )
        
        # Eliminar los más antiguos
        eliminados = 0
        for i in range(min(cantidad, len(items_ordenados))):
            clave, _ = items_ordenados[i]
            del self.datos[clave]
            eliminados += 1
        
        return eliminados
    
    def limpiar_expirados(self) -> int:
        """Elimina todos los elementos expirados de la caché."""
        claves_expiradas = [
            clave for clave, item in self.datos.items() 
            if item.ha_expirado()
        ]
        
        for clave in claves_expiradas:
            del self.datos[clave]
        
        return len(claves_expiradas)
    
    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas del uso de la caché."""
        total_solicitudes = self.hits + self.misses
        tasa_aciertos = (self.hits / total_solicitudes) * 100 if total_solicitudes > 0 else 0
        
        return {
            "elementos": len(self.datos),
            "capacidad": self.tamano_maximo,
            "porcentaje_uso": (len(self.datos) / self.tamano_maximo) * 100,
            "hits": self.hits,
            "misses": self.misses,
            "tasa_aciertos": tasa_aciertos,
            "elementos_expirados": sum(1 for item in self.datos.values() if item.ha_expirado())
        }

# Políticas de caché
class PoliticasCache:
    def __init__(self):
        # Tiempo de expiración por defecto (en segundos)
        self.tiempo_expiracion_default = 3600  # 1 hora
        
        # Tiempos de expiración por tipo de contenido (en segundos)
        self.tipos_contenido = {
            "image/": 86400,  # 24 horas para imágenes
            "application/json": 300,  # 5 minutos para APIs JSON
            "text/html": 1800,  # 30 minutos para HTML
            "text/css": 86400,  # 24 horas para CSS
            "application/javascript": 86400,  # 24 horas para JS
            "application/pdf": 86400 * 7,  # 7 días para PDFs
        }
        
        # Tamaño máximo para cachear (en bytes)
        self.tamano_maximo = 10 * 1024 * 1024  # 10 MB
        
        # URLs que no se deben cachear (patrones)
        self.no_cachear = [
            "/api/auth/",
            "/login", 
            "/logout",
            "/dashboard/realtime"
        ]
    
    def obtener_tiempo_vida(self, url: str, tipo_contenido: str) -> int:
        """Determina el tiempo de vida para un recurso basado en su tipo y URL."""
        # Buscar match por tipo de contenido
        for tipo, tiempo in self.tipos_contenido.items():
            if tipo_contenido.startswith(tipo):
                return tiempo
        
        # Si no hay match, usar tiempo por defecto
        return self.tiempo_expiracion_default
    
    def debe_cachear(self, url: str, tamano: int, tipo_contenido: str) -> bool:
        """Determina si un recurso debe ser cacheado."""
        # Verificar patrones que no se deben cachear
        for patron in self.no_cachear:
            if patron in url:
                return False
        
        # Verificar tamaño máximo
        if tamano > self.tamano_maximo:
            return False
        
        # Por defecto, cachear
        return True

# PATRÓN PROXY

# Sujeto: Interfaz para RecursoWebReal y Proxy
class RecursoWeb(ABC):
    @abstractmethod
    def obtener_contenido(self, url: str) -> ContenidoWeb:
        """Obtiene el contenido de un recurso web."""
        pass
    
    @abstractmethod
    def obtener_metadatos(self, url: str) -> Dict:
        """Obtiene sólo los metadatos de un recurso web."""
        pass

# Sujeto Real: Implementación que realmente accede a los recursos
class RecursoWebReal(RecursoWeb):
    def __init__(self):
        self.cliente_http = ClienteHTTP()
    
    def obtener_contenido(self, url: str) -> ContenidoWeb:
        """Obtiene el contenido completo de un recurso web."""
        tiempo_inicio = time.time()
        respuesta = self.cliente_http.realizar_solicitud_get(url)
        tiempo_total = time.time() - tiempo_inicio
        
        contenido = ContenidoWeb(
            datos=respuesta.content,
            tipo_contenido=respuesta.headers.get("Content-Type", "application/octet-stream"),
            codigo_respuesta=respuesta.status_code,
            tamano=len(respuesta.content),
            tiempo_carga=tiempo_total
        )
        
        return contenido
    
    def obtener_metadatos(self, url: str) -> Dict:
        """Obtiene sólo los metadatos de un recurso web sin descargar todo el contenido."""
        # En un sistema real, haríamos una solicitud HEAD
        tiempo_inicio = time.time()
        respuesta = self.cliente_http.realizar_solicitud_get(url)
        tiempo_total = time.time() - tiempo_inicio
        
        return {
            "url": url,
            "codigo_respuesta": respuesta.status_code,
            "tipo_contenido": respuesta.headers.get("Content-Type", "unknown"),
            "tamano": int(respuesta.headers.get("Content-Length", 0)),
            "servidor": respuesta.headers.get("Server", "unknown"),
            "fecha": respuesta.headers.get("Date", "unknown"),
            "tiempo_respuesta": tiempo_total
        }

# Proxy: Controla acceso al RecursoWebReal, implementando caché
class ProxyCacheRecursos(RecursoWeb):
    def __init__(self, tiempo_limpieza: int = 3600):
        self.recurso_real = RecursoWebReal()
        self.cache = DictCache(tamano_maximo=200)
        self.politicas_cache = PoliticasCache()
        self.ultimo_tiempo_limpieza = time.time()
        self.intervalo_limpieza = tiempo_limpieza  # en segundos
    
    def _generar_clave_cache(self, url: str) -> str:
        """Genera una clave única para la caché basada en la URL."""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _verificar_limpieza(self) -> None:
        """Verifica si es tiempo de limpiar la caché."""
        tiempo_actual = time.time()
        if tiempo_actual - self.ultimo_tiempo_limpieza > self.intervalo_limpieza:
            eliminados = self.cache.limpiar_expirados()
            if eliminados > 0:
                print(f"Limpieza automática: {eliminados} elementos expirados eliminados")
            self.ultimo_tiempo_limpieza = tiempo_actual
    
    def obtener_contenido(self, url: str) -> ContenidoWeb:
        """Obtiene el contenido, usando caché cuando sea posible."""
        self._verificar_limpieza()
        
        clave = self._generar_clave_cache(url)
        contenido_cache = self.cache.obtener(clave)
        
        if contenido_cache:
            print(f"CACHE HIT: {url}")
            return contenido_cache
        
        print(f"CACHE MISS: {url}")
        # Obtener del recurso real
        contenido = self.recurso_real.obtener_contenido(url)
        
        # Verificar si debemos cachear
        if self.politicas_cache.debe_cachear(url, contenido.tamano, contenido.tipo_contenido):
            tiempo_vida = self.politicas_cache.obtener_tiempo_vida(url, contenido.tipo_contenido)
            self.cache.guardar(clave, contenido, tiempo_vida)
            print(f"Cacheado: {url} por {tiempo_vida} segundos")
        
        return contenido
    
    def obtener_metadatos(self, url: str) -> Dict:
        """Obtiene los metadatos de un recurso, usando caché cuando sea posible."""
        # Intentar obtener de la caché primero
        clave = self._generar_clave_cache(url) + "_meta"
        metadatos_cache = self.cache.obtener(clave)
        
        if metadatos_cache:
            print(f"CACHE HIT (metadatos): {url}")
            return metadatos_cache
        
        print(f"CACHE MISS (metadatos): {url}")
        # Obtener del recurso real
        metadatos = self.recurso_real.obtener_metadatos(url)
        
        # Cachear con un tiempo de vida más corto para metadatos
        tiempo_vida = min(300, self.politicas_cache.obtener_tiempo_vida(url, metadatos.get("tipo_contenido", "")))
        self.cache.guardar(clave, metadatos, tiempo_vida)
        
        return metadatos
    
    def invalidar_cache(self, url: str) -> bool:
        """Invalida un elemento de la caché."""
        clave = self._generar_clave_cache(url)
        eliminado1 = self.cache.eliminar(clave)
        eliminado2 = self.cache.eliminar(clave + "_meta")
        return eliminado1 or eliminado2
    
    def limpiar_cache(self) -> int:
        """Limpia toda la caché y devuelve el número de elementos eliminados."""
        elementos = len(self.cache.datos)
        self.cache.datos.clear()
        self.ultimo_tiempo_limpieza = time.time()
        return elementos
    
    def obtener_estadisticas_cache(self) -> Dict:
        """Obtiene estadísticas de uso de la caché."""
        return self.cache.obtener_estadisticas()

# Cliente que utiliza el proxy
class GestorRecursosWeb:
    def __init__(self):
        self.proxy_cache = ProxyCacheRecursos()
    
    def cargar_imagen(self, url: str) -> bytes:
        """Carga una imagen desde una URL."""
        if not url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            raise ValueError("URL no corresponde a una imagen válida")
        
        contenido = self.proxy_cache.obtener_contenido(url)
        
        if not contenido.tipo_contenido.startswith('image/'):
            raise ValueError(f"El recurso no es una imagen: {contenido.tipo_contenido}")
        
        # En un sistema real, aquí convertiríamos los bytes a un objeto de imagen
        print(f"Imagen cargada: {len(contenido.datos)} bytes de tipo {contenido.tipo_contenido}")
        
        return contenido.datos
    
    def obtener_datos_api(self, url: str) -> Dict:
        """Obtiene datos de una API REST."""
        contenido = self.proxy_cache.obtener_contenido(url)
        
        try:
            return contenido.obtener_como_json()
        except ValueError:
            raise ValueError(f"No se pudo parsear la respuesta como JSON válido")
    
    def obtener_documento(self, url: str) -> str:
        """Obtiene un documento textual (HTML, XML, etc.)."""
        contenido = self.proxy_cache.obtener_contenido(url)
        
        if contenido.tipo_contenido.startswith(('text/', 'application/xml', 'application/json')):
            return contenido.obtener_como_texto()
        else:
            raise ValueError(f"El recurso no es un documento textual: {contenido.tipo_contenido}")
    
    def verificar_disponibilidad(self, url: str) -> Dict:
        """Verifica si un recurso está disponible sin descargar todo su contenido."""
        return self.proxy_cache.obtener_metadatos(url)
    
    def refrescar_recurso(self, url: str) -> bool:
        """Fuerza la actualización de un recurso en caché."""
        # Primero invalidar
        self.proxy_cache.invalidar_cache(url)
        
        # Luego recargar
        try:
            self.proxy_cache.obtener_contenido(url)
            return True
        except Exception:
            return False
    
    def mostrar_estadisticas_cache(self) -> None:
        """Muestra estadísticas de uso de la caché."""
        stats = self.proxy_cache.obtener_estadisticas_cache()
        print("\n=== Estadísticas de Caché ===")
        print(f"Elementos en caché: {stats['elementos']}/{stats['capacidad']} ({stats['porcentaje_uso']:.1f}%)")
        print(f"Hits/Misses: {stats['hits']}/{stats['misses']}")
        print(f"Tasa de aciertos: {stats['tasa_aciertos']:.1f}%")
        print(f"Elementos expirados pendientes de limpieza: {stats['elementos_expirados']}")
        print("=============================\n")

# Ejemplo de uso
if __name__ == "__main__":
    # Crear el gestor que usa el proxy
    gestor = GestorRecursosWeb()
    
    # URLs de ejemplo
    url_imagen = "https://example.com/imagen.jpg"
    url_api = "https://api.example.com/data.json"
    url_documento = "https://example.com/page.html"
    
    # Simular cargas y mostrar beneficios del caché
    print("\n=== Primera carga (sin caché) ===")
    
    # Cargar imagen
    t_inicio = time.time()
    gestor.cargar_imagen(url_imagen)
    print(f"Tiempo: {time.time() - t_inicio:.2f} segundos")
    
    # Obtener datos API
    t_inicio = time.time()
    datos_api = gestor.obtener_datos_api(url_api)
    print(f"Datos API: {datos_api}")
    print(f"Tiempo: {time.time() - t_inicio:.2f} segundos")
    
    # Obtener documento
    t_inicio = time.time()
    documento = gestor.obtener_documento(url_documento)
    print(f"Documento (primeros 50 chars): {documento[:50]}...")
    print(f"Tiempo: {time.time() - t_inicio:.2f} segundos")
    
    print("\n=== Segunda carga (con caché) ===")
    
    # Cargar la misma imagen (debería ser más rápido)
    t_inicio = time.time()
    gestor.cargar_imagen(url_imagen)
    print(f"Tiempo: {time.time() - t_inicio:.2f} segundos")
    
    # Obtener los mismos datos de API
    t_inicio = time.time()
    gestor.obtener_datos_api(url_api)
    print(f"Tiempo: {time.time() - t_inicio:.2f} segundos")
    
    # Obtener el mismo documento
    t_inicio = time.time()
    gestor.obtener_documento(url_documento)
    print(f"Tiempo: {time.time() - t_inicio:.2f} segundos")
    
    # Mostrar estadísticas
    gestor.mostrar_estadisticas_cache()
    
    # Simular recarga forzada
    print("\n=== Recarga forzada ===")
    gestor.refrescar_recurso(url_api)
    
    # Verificar disponibilidad sin descargar contenido completo
    print("\n=== Verificar disponibilidad ===")
    info = gestor.verificar_disponibilidad("https://example.com/large_file.zip")
    print(f"Metadatos: {info}")
    
    # Mostrar estadísticas finales
    gestor.mostrar_estadisticas_cache()