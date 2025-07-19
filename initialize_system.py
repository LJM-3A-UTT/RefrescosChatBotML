#!/usr/bin/env python3
"""
SISTEMA DE INICIALIZACIÓN COMPLETO - RefrescoBot ML
Este es el script ÚNICO para inicializar todo el sistema automáticamente

FUNCIONALIDADES:
1. Corrige estructura de bebidas (IDs, sabores, etc.)
2. Inicializa base de datos con limpieza selectiva (mantiene sesiones)
3. Procesa bebidas con ML avanzado
4. Genera modelos ML iniciales
5. Inicia servicios backend y frontend
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path
import logging
import numpy as np

def convert_numpy_types(obj):
    """Convierte tipos numpy a tipos Python nativos para serialización MongoDB"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Añadir el directorio backend al path
sys.path.append(str(Path(__file__).parent / "backend"))

async def main():
    """Función principal de inicialización"""
    
    print("🚀 INICIALIZANDO REFRESCOBOT ML - SISTEMA COMPLETO")
    print("=" * 70)
    
    try:
        # 1. Corregir estructura de bebidas
        print("\n📋 PASO 1: Corrigiendo estructura de bebidas...")
        result = subprocess.run([sys.executable, "fix_bebidas_structure.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Estructura de bebidas corregida")
            print(result.stdout)
        else:
            print("❌ Error corrigiendo estructura:", result.stderr)
            return False
        
        # 2. Inicializar base de datos con limpieza selectiva
        print("\n📋 PASO 2: Inicializando base de datos...")
        
        # Importar después de agregar al path
        from motor.motor_asyncio import AsyncIOMotorClient
        from data_manager import initialize_system_data
        from dotenv import load_dotenv
        
        # Cargar variables de entorno
        load_dotenv(Path(__file__).parent / "backend" / ".env")
        
        # Conectar a MongoDB
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ['DB_NAME']
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Inicializar con limpieza selectiva (mantiene sesiones)
        await initialize_system_data(db, clean_first=True)
        print("✅ Base de datos inicializada (sesiones preservadas)")
        
        # 3. Procesar bebidas con ML
        print("\n📋 PASO 3: Procesando bebidas con ML avanzado...")
        
        from beverage_categorizer import beverage_categorizer
        from image_analyzer import image_analyzer
        from presentation_rating_system import presentation_rating_system
        
        # Obtener bebidas de la BD
        bebidas = await db.bebidas.find({}).to_list(None)
        print(f"Procesando {len(bebidas)} bebidas con ML...")
        
        # Procesar con categorización ML
        processed_beverages = beverage_categorizer.process_all_beverages(bebidas)
        
        # Procesar imágenes
        for bebida in processed_beverages:
            try:
                image_analysis = image_analyzer.analyze_beverage_images(bebida)
                bebida['features_imagen'] = image_analysis
                
                # Categorizar presentaciones
                for i, presentacion in enumerate(bebida.get('presentaciones', [])):
                    if 'presentation_id' not in presentacion:
                        presentacion['presentation_id'] = f"{bebida['id']}_{presentacion.get('ml', i)}_{i+1}"
                    
                    ml_size = beverage_categorizer.categorize_presentation_size(presentacion.get('ml', 0))
                    presentacion['categoria_ml'] = ml_size
                    
            except Exception as e:
                logger.warning(f"Error procesando {bebida['nombre']}: {e}")
        
        # Actualizar bebidas en BD con conversión de tipos numpy
        for bebida in processed_beverages:
            # Convertir numpy types a tipos Python nativos
            bebida_serializable = convert_numpy_types(bebida)
            await db.bebidas.update_one(
                {"id": bebida["id"]},
                {"$set": bebida_serializable}
            )
        
        print("✅ Procesamiento ML completado")
        
        # 4. Generar datos ML iniciales para entrenamiento
        print("\n📋 PASO 4: Generando datos ML iniciales...")
        
        from ml_engine import ml_engine
        
        # Generar algunos datos sintéticos para entrenamiento inicial
        await generate_initial_training_data(db)
        print("✅ Datos ML iniciales generados")
        
        # 5. Verificar estado de modelos
        print("\n📋 PASO 5: Verificando modelos ML...")
        
        # Verificar estadísticas de componentes ML
        ml_stats = ml_engine.get_model_stats()
        categorizer_stats = beverage_categorizer.get_category_stats()
        image_stats = image_analyzer.get_analysis_stats()
        presentation_stats = presentation_rating_system.get_system_stats()
        
        print(f"✅ ML Engine: {ml_stats}")
        print(f"✅ Beverage Categorizer: {categorizer_stats}")
        print(f"✅ Image Analyzer: {image_stats}")
        print(f"✅ Presentation Rating: {presentation_stats}")
        
        # 6. Mostrar estadísticas finales
        print("\n📊 ESTADÍSTICAS FINALES:")
        
        # Contar bebidas por tipo
        refrescos_count = await db.bebidas.count_documents({"es_refresco_real": True})
        alternativas_count = await db.bebidas.count_documents({"es_refresco_real": False})
        sesiones_count = await db.sesiones_chat.count_documents({})
        preguntas_count = await db.preguntas.count_documents({})
        
        print(f"🥤 Refrescos reales: {refrescos_count}")
        print(f"🌿 Alternativas saludables: {alternativas_count}")
        print(f"❓ Preguntas disponibles: {preguntas_count}")
        print(f"💾 Sesiones preservadas: {sesiones_count}")
        
        # Cerrar conexión
        client.close()
        
        print("\n🎉 SISTEMA INICIALIZADO EXITOSAMENTE")
        print("=" * 70)
        print("✅ Base de datos lista")
        print("✅ ML engines configurados")
        print("✅ Estructura de bebidas corregida")
        print("✅ Sesiones de aprendizaje preservadas")
        print("\n🚀 Para iniciar los servicios, ejecuta:")
        print("   Backend: cd backend && uvicorn server:app --host 0.0.0.0 --port 8001 --reload")
        print("   Frontend: cd frontend && yarn start")
        
        return True
        
    except Exception as e:
        logger.error(f"Error en inicialización: {e}")
        print(f"\n❌ ERROR CRÍTICO: {e}")
        return False

async def generate_initial_training_data(db):
    """Genera datos iniciales para entrenamiento ML"""
    
    try:
        # Obtener bebidas
        bebidas = await db.bebidas.find({}).to_list(None)
        
        # Generar respuestas sintéticas diversas para entrenamiento inicial
        synthetic_responses = [
            {
                "rutina": "muy_activo",
                "estado_animo": "energico", 
                "preferencias": "natural",
                "fisico": "deportista",
                "temporal": "manana"
            },
            {
                "rutina": "sedentario",
                "estado_animo": "tranquilo",
                "preferencias": "muy_dulce", 
                "fisico": "oficina",
                "temporal": "tarde"
            },
            {
                "rutina": "moderado",
                "estado_animo": "ocupado",
                "preferencias": "equilibrado",
                "fisico": "mixto", 
                "temporal": "noche"
            }
        ]
        
        from ml_engine import ml_engine
        
        # Agregar datos sintéticos de entrenamiento
        for i, responses in enumerate(synthetic_responses):
            for bebida in bebidas:
                # Generar rating sintético basado en características
                rating = generate_synthetic_rating(responses, bebida)
                ml_engine.add_training_data(responses, bebida, rating)
        
        # Intentar entrenar con datos sintéticos
        if len(ml_engine.training_data) >= 10:
            ml_engine.train_models()
            logger.info("Modelos ML entrenados con datos sintéticos")
        
    except Exception as e:
        logger.warning(f"Error generando datos sintéticos: {e}")

def generate_synthetic_rating(responses, bebida):
    """Genera rating sintético realista"""
    
    base_rating = 3.0
    
    # Lógica sintética simplificada
    if responses["preferencias"] == "natural" and not bebida.get("es_refresco_real", True):
        base_rating += 1.5
    elif responses["preferencias"] == "muy_dulce" and bebida.get("nivel_dulzura", 5) >= 7:
        base_rating += 1.0
    
    if responses["rutina"] == "muy_activo" and bebida.get("es_energizante", False):
        base_rating += 0.8
    
    # Agregar variabilidad realista
    import random
    noise = random.uniform(-0.5, 0.5)
    
    return max(1.0, min(5.0, base_rating + noise))

if __name__ == "__main__":
    # Cambiar al directorio del script
    os.chdir(Path(__file__).parent)
    
    # Ejecutar inicialización
    success = asyncio.run(main())
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)