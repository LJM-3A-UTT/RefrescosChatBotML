"""
Script de Inicialización del Sistema RefrescoBot ML
Configura el entorno completo para el backend

Funciones:
- Inicialización de base de datos con datos JSON
- Creación de directorios necesarios
- Verificación de configuración
- Setup completo del entorno ML
"""

import asyncio
import os
import sys
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importar módulos locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data_manager import DataManager
from ml_engine import ml_engine


async def create_directories():
    """Crea directorios necesarios para el sistema"""
    logger.info("Creando estructura de directorios...")
    
    directories = [
        'data',
        'models', 
        'static',
        'static/images',
        'static/images/bebidas'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Directorio creado/verificado: {directory}")




async def verify_environment():
    """Verifica que el entorno esté configurado correctamente"""
    logger.info("Verificando configuración del entorno...")
    
    # Verificar variables de entorno
    load_dotenv()
    
    required_env_vars = ['MONGO_URL', 'DB_NAME']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Variables de entorno faltantes: {missing_vars}")
        logger.error("Por favor configura las variables de entorno en el archivo .env")
        return False
    
    # Verificar archivos de datos
    required_files = ['data/preguntas.json', 'data/bebidas.json']
    missing_files = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"Archivos de datos faltantes: {missing_files}")
        return False
    
    logger.info("Configuración del entorno verificada correctamente")
    return True


async def test_database_connection():
    """Prueba la conexión a la base de datos"""
    logger.info("Probando conexión a base de datos...")
    
    try:
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ['DB_NAME']
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Probar la conexión
        await client.admin.command('ping')
        logger.info("Conexión a MongoDB exitosa")
        
        return client, db
        
    except Exception as e:
        logger.error(f"Error conectando a MongoDB: {e}")
        return None, None


async def initialize_ml_system():
    """Inicializa el sistema de Machine Learning"""
    logger.info("Inicializando sistema ML...")
    
    try:
        # Verificar que el engine ML esté disponible
        stats = ml_engine.get_model_stats()
        logger.info(f"Estado del ML Engine: {stats}")
        
        # Si hay modelos guardados, cargarlos
        if stats['training_samples'] > 0:
            logger.info(f"Modelos ML cargados con {stats['training_samples']} muestras de entrenamiento")
        else:
            logger.info("Sistema ML iniciado sin datos de entrenamiento previos")
        
        return True
        
    except Exception as e:
        logger.error(f"Error inicializando sistema ML: {e}")
        return False


async def main():
    """Función principal de inicialización"""
    logger.info("=== INICIANDO CONFIGURACIÓN DEL SISTEMA REFRESCOBOT ML ===")
    
    try:
        # 1. Verificar entorno
        if not await verify_environment():
            logger.error("Configuración del entorno inválida. Abortando.")
            return False
        
        # 2. Crear directorios
        await create_directories()
        
        # 3. Probar conexión a base de datos
        client, db = await test_database_connection()
        if not client:
            logger.error("No se pudo conectar a la base de datos. Abortando.")
            return False
        
        # 4. Inicializar base de datos con datos JSON
        logger.info("Inicializando base de datos...")
        data_manager = DataManager(db)
        await data_manager.initialize_database(clean_first=True)
        
        # 5. Verificar integridad de datos
        integrity_stats = await data_manager.verify_data_integrity()
        if not integrity_stats['integridad']['valida']:
            logger.error(f"Problemas de integridad de datos: {integrity_stats['integridad']['errores']}")
            logger.warning("Continuando con inicialización a pesar de los errores...")
        
        # 7. Obtener resumen de datos
        data_summary = await data_manager.get_data_summary()
        logger.info(f"Resumen de datos cargados: {data_summary}")
        
        # 8. Inicializar sistema ML
        if not await initialize_ml_system():
            logger.warning("Sistema ML no se pudo inicializar completamente")
        
        # 9. Cerrar conexión
        client.close()
        
        logger.info("=== SISTEMA REFRESCOBOT ML INICIALIZADO EXITOSAMENTE ===")
        logger.info("El sistema está listo para recibir peticiones.")
        
        return True
        
    except Exception as e:
        logger.error(f"Error durante la inicialización: {e}")
        return False


if __name__ == "__main__":
    # Ejecutar inicialización
    success = asyncio.run(main())
    
    if success:
        print("\n✅ INICIALIZACIÓN COMPLETADA EXITOSAMENTE")
        print("El servidor RefrescoBot ML está listo para ejecutarse.")
        print("\nPara iniciar el servidor, ejecuta:")
        print("uvicorn server:app --host 0.0.0.0 --port 8001 --reload")
    else:
        print("\n❌ INICIALIZACIÓN FALLÓ")
        print("Revisa los logs para más detalles.")
        sys.exit(1)