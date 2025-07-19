"""
Data Manager para RefrescoBot ML
Maneja la inicialización, limpieza y recarga de datos desde archivos JSON

Funcionalidades:
- Limpieza automática de base de datos en startup
- Carga de datos desde archivos JSON
- Prevención de duplicación de datos
- Inicialización de colecciones
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataManager:
    """
    Manejador de datos para RefrescoBot ML
    
    Responsabilidades:
    - Cargar datos desde archivos JSON
    - Inicializar base de datos
    - Limpiar datos existentes
    - Mantener consistencia de datos
    """
    
    def __init__(self, db: AsyncIOMotorDatabase, data_dir: str = None):
        self.db = db
        
        # Determinar directorio de datos
        if data_dir is None:
            # Buscar el directorio data relativo al archivo actual
            current_dir = Path(__file__).parent
            data_dir = current_dir / "data"
        
        self.data_dir = Path(data_dir)
        
        # Archivos de datos
        self.preguntas_file = self.data_dir / "preguntas.json"
        self.bebidas_file = self.data_dir / "bebidas.json"
        
        # Validar que existen los archivos
        if not self.preguntas_file.exists():
            raise FileNotFoundError(f"Archivo de preguntas no encontrado: {self.preguntas_file}")
        if not self.bebidas_file.exists():
            raise FileNotFoundError(f"Archivo de bebidas no encontrado: {self.bebidas_file}")
    
    async def initialize_database(self, clean_first: bool = True):
        """
        Inicializa la base de datos completa
        
        Args:
            clean_first: Si limpiar la base de datos antes de cargar datos
        """
        logger.info("Iniciando inicialización de base de datos...")
        
        try:
            if clean_first:
                await self.clean_database()
            
            # Cargar datos desde archivos JSON
            await self.load_preguntas()
            await self.load_bebidas()
            
            # Crear índices necesarios
            await self.create_indexes()
            
            logger.info("Base de datos inicializada exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
            raise
    
    async def clean_database(self):
        """
        Limpia SOLO las colecciones de preguntas y bebidas
        MANTIENE las sesiones para conservar el aprendizaje del sistema
        """
        logger.info("Limpiando base de datos (solo preguntas y bebidas)...")
        
        try:
            # Solo limpiar preguntas y bebidas, MANTENER sesiones y puntuaciones
            collections_to_clean = ['preguntas', 'bebidas']
            
            for collection_name in collections_to_clean:
                collection = self.db[collection_name]
                result = await collection.delete_many({})
                logger.info(f"Colección '{collection_name}': {result.deleted_count} documentos eliminados")
            
            # Mostrar estadísticas de sesiones conservadas
            sesiones_collection = self.db['sesiones_chat']
            sesiones_count = await sesiones_collection.count_documents({})
            
            puntuaciones_collection = self.db['puntuaciones']
            puntuaciones_count = await puntuaciones_collection.count_documents({})
            
            logger.info(f"✅ Sesiones conservadas: {sesiones_count}")
            logger.info(f"✅ Puntuaciones conservadas: {puntuaciones_count}")
            logger.info("Base de datos limpiada exitosamente (manteniendo aprendizaje)")
            
        except Exception as e:
            logger.error(f"Error limpiando base de datos: {e}")
            raise
    
    async def clean_sessions_only(self):
        """
        Limpia SOLO las sesiones (para casos especiales)
        """
        logger.info("Limpiando SOLO sesiones de chat...")
        
        try:
            # Solo limpiar sesiones y puntuaciones
            collections_to_clean = ['sesiones_chat', 'puntuaciones', 'puntuaciones_presentacion']
            
            for collection_name in collections_to_clean:
                collection = self.db[collection_name]
                result = await collection.delete_many({})
                logger.info(f"Colección '{collection_name}': {result.deleted_count} documentos eliminados")
            
            logger.info("Sesiones limpiadas exitosamente")
            
        except Exception as e:
            logger.error(f"Error limpiando sesiones: {e}")
            raise
    
    async def load_preguntas(self):
        """
        Carga preguntas desde archivo JSON
        """
        logger.info("Cargando preguntas...")
        
        try:
            # Leer archivo JSON
            with open(self.preguntas_file, 'r', encoding='utf-8') as f:
                preguntas_data = json.load(f)
            
            # Validar estructura de datos
            for pregunta in preguntas_data:
                if not all(key in pregunta for key in ['id', 'pregunta', 'opciones', 'categoria']):
                    raise ValueError(f"Pregunta con ID {pregunta.get('id', 'unknown')} tiene estructura inválida")
            
            # Insertar en base de datos
            collection = self.db['preguntas']
            
            if preguntas_data:
                result = await collection.insert_many(preguntas_data)
                logger.info(f"Insertadas {len(result.inserted_ids)} preguntas")
            
            # Verificar datos
            count = await collection.count_documents({})
            preguntas_fijas = await collection.count_documents({"es_fija": True})
            
            logger.info(f"Total preguntas en DB: {count} (Fijas: {preguntas_fijas})")
            
        except Exception as e:
            logger.error(f"Error cargando preguntas: {e}")
            raise
    
    async def load_bebidas(self):
        """
        Carga bebidas desde archivo JSON
        """
        logger.info("Cargando bebidas...")
        
        try:
            # Leer archivo JSON
            with open(self.bebidas_file, 'r', encoding='utf-8') as f:
                bebidas_data = json.load(f)
            
            # Validar estructura de datos
            for bebida in bebidas_data:
                required_fields = ['id', 'nombre', 'descripcion', 'categoria', 'es_refresco_real', 'presentaciones']
                if not all(key in bebida for key in required_fields):
                    raise ValueError(f"Bebida con ID {bebida.get('id', 'unknown')} tiene estructura inválida")
                
                # Validar presentaciones
                if not bebida['presentaciones'] or not isinstance(bebida['presentaciones'], list):
                    raise ValueError(f"Bebida {bebida['nombre']} no tiene presentaciones válidas")
                
                for presentacion in bebida['presentaciones']:
                    if not all(key in presentacion for key in ['ml', 'precio', 'imagen_local']):
                        raise ValueError(f"Presentación inválida en bebida {bebida['nombre']}")
            
            # Añadir campos por defecto si no existen
            for bebida in bebidas_data:
                # Asegurar campos ML
                bebida.setdefault('nivel_dulzura', 5)
                bebida.setdefault('es_energizante', False)
                bebida.setdefault('perfil_sabor', 'equilibrado')
                bebida.setdefault('contenido_calorias', 'medio')
                bebida.setdefault('tipo_consumidor', 'general')
                
                # Inicializar puntuación promedio
                bebida.setdefault('puntuacion_promedio', 3.0)
                bebida.setdefault('total_puntuaciones', 0)
            
            # Insertar en base de datos
            collection = self.db['bebidas']
            
            if bebidas_data:
                result = await collection.insert_many(bebidas_data)
                logger.info(f"Insertadas {len(result.inserted_ids)} bebidas")
            
            # Verificar datos
            count = await collection.count_documents({})
            refrescos_reales = await collection.count_documents({"es_refresco_real": True})
            alternativas = await collection.count_documents({"es_refresco_real": False})
            
            logger.info(f"Total bebidas en DB: {count} (Refrescos: {refrescos_reales}, Alternativas: {alternativas})")
            
        except Exception as e:
            logger.error(f"Error cargando bebidas: {e}")
            raise
    
    async def create_indexes(self):
        """
        Crea índices necesarios para optimizar consultas
        """
        logger.info("Creando índices...")
        
        try:
            # Índices para preguntas
            preguntas_collection = self.db['preguntas']
            await preguntas_collection.create_index("id", unique=True)
            await preguntas_collection.create_index("es_fija")
            await preguntas_collection.create_index("categoria")
            
            # Índices para bebidas
            bebidas_collection = self.db['bebidas']
            await bebidas_collection.create_index("id", unique=True)
            await bebidas_collection.create_index("es_refresco_real")
            await bebidas_collection.create_index("categoria")
            await bebidas_collection.create_index("puntuacion_promedio")
            
            # Índices para sesiones
            sesiones_collection = self.db['sesiones_chat']
            await sesiones_collection.create_index("session_id", unique=True)
            await sesiones_collection.create_index("fecha_creacion")
            
            logger.info("Índices creados exitosamente")
            
        except Exception as e:
            logger.error(f"Error creando índices: {e}")
            # No lanzar excepción, los índices no son críticos
    
    async def update_from_files(self):
        """
        Actualiza la base de datos desde los archivos JSON
        (útil para actualizaciones sin reiniciar el servidor)
        """
        logger.info("Actualizando datos desde archivos...")
        
        try:
            await self.initialize_database(clean_first=True)
            logger.info("Datos actualizados exitosamente desde archivos")
            
        except Exception as e:
            logger.error(f"Error actualizando datos: {e}")
            raise
    
    async def verify_data_integrity(self) -> Dict[str, Any]:
        """
        Verifica la integridad de los datos en la base de datos
        
        Returns:
            Diccionario con estadísticas de integridad
        """
        logger.info("Verificando integridad de datos...")
        
        try:
            stats = {}
            
            # Verificar preguntas
            preguntas_collection = self.db['preguntas']
            stats['preguntas'] = {
                'total': await preguntas_collection.count_documents({}),
                'fijas': await preguntas_collection.count_documents({"es_fija": True}),
                'aleatorias': await preguntas_collection.count_documents({"es_fija": False})
            }
            
            # Verificar bebidas
            bebidas_collection = self.db['bebidas']
            stats['bebidas'] = {
                'total': await bebidas_collection.count_documents({}),
                'refrescos_reales': await bebidas_collection.count_documents({"es_refresco_real": True}),
                'alternativas': await bebidas_collection.count_documents({"es_refresco_real": False})
            }
            
            # Verificar que cada bebida tenga presentaciones
            bebidas_sin_presentaciones = await bebidas_collection.count_documents({
                "$or": [
                    {"presentaciones": {"$exists": False}},
                    {"presentaciones": {"$size": 0}}
                ]
            })
            stats['bebidas']['sin_presentaciones'] = bebidas_sin_presentaciones
            
            # Verificar sesiones activas
            sesiones_collection = self.db['sesiones_chat']
            stats['sesiones'] = {
                'total': await sesiones_collection.count_documents({}),
                'activas': await sesiones_collection.count_documents({"completada": False})
            }
            
            # Estado general
            stats['integridad'] = {
                'valida': (
                    stats['preguntas']['total'] > 0 and
                    stats['preguntas']['fijas'] >= 1 and
                    stats['bebidas']['total'] > 0 and
                    stats['bebidas']['sin_presentaciones'] == 0
                ),
                'errores': []
            }
            
            # Identificar errores
            if stats['preguntas']['total'] == 0:
                stats['integridad']['errores'].append("No hay preguntas en la base de datos")
            if stats['preguntas']['fijas'] == 0:
                stats['integridad']['errores'].append("No hay preguntas fijas")
            if stats['bebidas']['total'] == 0:
                stats['integridad']['errores'].append("No hay bebidas en la base de datos")
            if stats['bebidas']['sin_presentaciones'] > 0:
                stats['integridad']['errores'].append(f"{stats['bebidas']['sin_presentaciones']} bebidas sin presentaciones")
            
            logger.info(f"Verificación completada. Integridad: {stats['integridad']['valida']}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error verificando integridad: {e}")
            return {
                'integridad': {
                    'valida': False,
                    'errores': [f"Error en verificación: {str(e)}"]
                }
            }
    
    async def get_data_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen de los datos en la base de datos
        
        Returns:
            Diccionario con resumen de datos
        """
        try:
            preguntas_collection = self.db['preguntas']
            bebidas_collection = self.db['bebidas']
            sesiones_collection = self.db['sesiones_chat']
            
            # Estadísticas de preguntas
            preguntas_por_categoria = {}
            async for pregunta in preguntas_collection.find({}):
                categoria = pregunta.get('categoria', 'sin_categoria')
                preguntas_por_categoria[categoria] = preguntas_por_categoria.get(categoria, 0) + 1
            
            # Estadísticas de bebidas
            bebidas_por_categoria = {}
            async for bebida in bebidas_collection.find({}):
                categoria = bebida.get('categoria', 'sin_categoria')
                bebidas_por_categoria[categoria] = bebidas_por_categoria.get(categoria, 0) + 1
            
            # Resumen de sesiones
            total_sesiones = await sesiones_collection.count_documents({})
            
            return {
                'preguntas': {
                    'total': await preguntas_collection.count_documents({}),
                    'por_categoria': preguntas_por_categoria
                },
                'bebidas': {
                    'total': await bebidas_collection.count_documents({}),
                    'por_categoria': bebidas_por_categoria
                },
                'sesiones': {
                    'total': total_sesiones
                },
                'timestamp': asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen: {e}")
            return {'error': str(e)}


# Función de conveniencia para inicializar datos
async def initialize_system_data(db: AsyncIOMotorDatabase, clean_first: bool = True):
    """
    Función de conveniencia para inicializar el sistema de datos
    
    Args:
        db: Base de datos MongoDB
        clean_first: Si limpiar antes de cargar datos
    """
    data_manager = DataManager(db)
    await data_manager.initialize_database(clean_first=clean_first)
    return data_manager