from abc import ABC, abstractmethod
from typing import Dict
from dataclasses import dataclass
import copy
import time

# Clase para representar un fotograma de video
@dataclass
class VideoFrame:
    id: int
    datos: bytes
    timestamp: float
    ancho: int
    alto: int
    
    def __repr__(self):
        return f"VideoFrame(id={self.id}, timestamp={self.timestamp}, ancho={self.ancho}, alto={self.alto})"

# Componente
class FlujoVideo(ABC):
    @abstractmethod
    def procesar_fotograma(self, fotograma: VideoFrame) -> VideoFrame:
        pass
    
    @abstractmethod
    def obtener_metadatos(self) -> Dict:
        pass

# Componente concreto
class FlujoVideoBase(FlujoVideo):
    def __init__(self, ruta_archivo: str, formato: str = "mp4"):
        self.ruta_archivo = ruta_archivo
        self.formato = formato
        self.fecha_creacion = time.time()
    
    def procesar_fotograma(self, fotograma: VideoFrame) -> VideoFrame:
        # Simplemente devuelve el fotograma sin procesar
        return fotograma
    
    def obtener_metadatos(self) -> Dict:
        return {
            "ruta": self.ruta_archivo,
            "formato": self.formato,
            "fecha_creacion": self.fecha_creacion,
            "transformaciones": []
        }

# Decorador base
class DecoradorFlujoVideo(FlujoVideo, ABC):
    def __init__(self, flujo_envuelto: FlujoVideo):
        self.flujo_envuelto = flujo_envuelto
    
    def procesar_fotograma(self, fotograma: VideoFrame) -> VideoFrame:
        return self.flujo_envuelto.procesar_fotograma(fotograma)
    
    def obtener_metadatos(self) -> Dict:
        return self.flujo_envuelto.obtener_metadatos()

# Decoradores concretos
class DecoradorCompresion(DecoradorFlujoVideo):
    def __init__(self, flujo_envuelto: FlujoVideo, nivel_compresion: int = 80):
        super().__init__(flujo_envuelto)
        self.nivel_compresion = nivel_compresion
    
    def procesar_fotograma(self, fotograma: VideoFrame) -> VideoFrame:
        # Primero procesa con el decorador envuelto
        fotograma_procesado = self.flujo_envuelto.procesar_fotograma(fotograma)
        
        # Luego aplica la compresión
        fotograma_resultado = copy.deepcopy(fotograma_procesado)
        
        # Simulamos la compresión reduciendo el tamaño de los datos
        datos_comprimidos = fotograma_resultado.datos[:len(fotograma_resultado.datos) * (100 - self.nivel_compresion) // 100]
        fotograma_resultado.datos = datos_comprimidos
        
        return fotograma_resultado
    
    def obtener_metadatos(self) -> Dict:
        metadatos = self.flujo_envuelto.obtener_metadatos()
        metadatos["transformaciones"].append(f"compresion-{self.nivel_compresion}%")
        return metadatos

class DecoradorEncriptacion(DecoradorFlujoVideo):
    def __init__(self, flujo_envuelto: FlujoVideo, clave_encriptacion: str, algoritmo: str = "AES"):
        super().__init__(flujo_envuelto)
        self.clave_encriptacion = clave_encriptacion
        self.algoritmo = algoritmo
    
    def procesar_fotograma(self, fotograma: VideoFrame) -> VideoFrame:
        # Primero procesa con el decorador envuelto
        fotograma_procesado = self.flujo_envuelto.procesar_fotograma(fotograma)
        
        # Luego aplica la encriptación
        fotograma_resultado = copy.deepcopy(fotograma_procesado)
        
        # Simulamos la encriptación (XOR con el primer byte de la clave)
        clave_byte = ord(self.clave_encriptacion[0]) if self.clave_encriptacion else 0
        datos_encriptados = bytes(b ^ clave_byte for b in fotograma_resultado.datos)
        fotograma_resultado.datos = datos_encriptados
        
        return fotograma_resultado
    
    def obtener_metadatos(self) -> Dict:
        metadatos = self.flujo_envuelto.obtener_metadatos()
        metadatos["transformaciones"].append(f"encriptacion-{self.algoritmo}")
        return metadatos

class DecoradorMarcaAgua(DecoradorFlujoVideo):
    def __init__(self, flujo_envuelto: FlujoVideo, texto_marca: str, posicion: str = "esquina-inferior-derecha"):
        super().__init__(flujo_envuelto)
        self.texto_marca = texto_marca
        self.posicion = posicion
    
    def procesar_fotograma(self, fotograma: VideoFrame) -> VideoFrame:
        # Primero procesa con el decorador envuelto
        fotograma_procesado = self.flujo_envuelto.procesar_fotograma(fotograma)
        
        # Luego aplica la marca de agua
        fotograma_resultado = copy.deepcopy(fotograma_procesado)
        
        # En un sistema real, aquí se añadiría la marca de agua al fotograma
        # Para esta simulación, simplemente modificamos los metadatos
        
        return fotograma_resultado
    
    def obtener_metadatos(self) -> Dict:
        metadatos = self.flujo_envuelto.obtener_metadatos()
        metadatos["transformaciones"].append(f"marca-agua-{self.posicion}")
        metadatos["marca_agua"] = self.texto_marca
        return metadatos

class DecoradorFiltroColor(DecoradorFlujoVideo):
    def __init__(self, flujo_envuelto: FlujoVideo, tipo_filtro: str, intensidad: float = 1.0):
        super().__init__(flujo_envuelto)
        self.tipo_filtro = tipo_filtro
        self.intensidad = intensidad
    
    def procesar_fotograma(self, fotograma: VideoFrame) -> VideoFrame:
        # Primero procesa con el decorador envuelto
        fotograma_procesado = self.flujo_envuelto.procesar_fotograma(fotograma)
        
        # Luego aplica el filtro de color
        fotograma_resultado = copy.deepcopy(fotograma_procesado)
        
        # En un sistema real, aquí se aplicaría el filtro de color
        # Para esta simulación, simplemente registramos la operación
        
        return fotograma_resultado
    
    def obtener_metadatos(self) -> Dict:
        metadatos = self.flujo_envuelto.obtener_metadatos()
        metadatos["transformaciones"].append(f"filtro-{self.tipo_filtro}-{self.intensidad}")
        return metadatos

# Ejemplo de uso
if __name__ == "__main__":
    # Crear un fotograma de prueba
    fotograma_prueba = VideoFrame(
        id=1,
        datos=bytes([255] * 1024),  # 1KB de datos
        timestamp=1234.56,
        ancho=1920,
        alto=1080
    )
    
    # Crear un flujo de video base
    flujo_base = FlujoVideoBase("video_original.mp4", "mp4")
    
    # Aplicar diferentes decoradores
    flujo_comprimido = DecoradorCompresion(flujo_base, 75)
    flujo_comprimido_encriptado = DecoradorEncriptacion(flujo_comprimido, "clave-secreta", "AES")
    flujo_completo = DecoradorMarcaAgua(
        DecoradorFiltroColor(flujo_comprimido_encriptado, "sepia", 0.8),
        "© Plataforma Streaming 2023",
        "centro"
    )
    
    # Procesar un fotograma a través de toda la cadena de decoradores
    fotograma_resultado = flujo_completo.procesar_fotograma(fotograma_prueba)
    
    # Obtener metadatos
    metadatos = flujo_completo.obtener_metadatos()
    
    print(f"Fotograma original: {fotograma_prueba}")
    print(f"Fotograma procesado: {fotograma_resultado}")
    print(f"Tamaño original: {len(fotograma_prueba.datos)} bytes")
    print(f"Tamaño después del procesamiento: {len(fotograma_resultado.datos)} bytes")
    print(f"Metadatos: {metadatos}")