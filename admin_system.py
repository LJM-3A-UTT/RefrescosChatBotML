#!/usr/bin/env python3
"""
SISTEMA DE ADMINISTRACIÓN MANUAL - RefrescoBot ML
Panel de control para administración del sistema

FUNCIONALIDADES:
1. Gestión de base de datos (limpiar sesiones, estadísticas)
2. Gestión de ML (reentrenar, estadísticas de modelos)
3. Gestión de bebidas (agregar, modificar, verificar imágenes)
4. Diagnósticos del sistema
5. Configuración avanzada
"""

import os
import sys
import asyncio
import json
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Añadir el directorio backend al path
sys.path.append(str(Path(__file__).parent / "backend"))

class AdminPanel:
    """Panel de administración para RefrescoBot ML"""
    
    def __init__(self):
        self.db = None
        self.client = None
    
    async def connect_db(self):
        """Conectar a la base de datos"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            from dotenv import load_dotenv
            
            # Cargar variables de entorno
            load_dotenv(Path(__file__).parent / "backend" / ".env")
            
            mongo_url = os.environ['MONGO_URL']
            db_name = os.environ['DB_NAME']
            self.client = AsyncIOMotorClient(mongo_url)
            self.db = self.client[db_name]
            
            print("✅ Conectado a MongoDB Atlas")
            return True
            
        except Exception as e:
            print(f"❌ Error conectando a BD: {e}")
            return False
    
    def show_main_menu(self):
        """Mostrar menú principal"""
        print("\n" + "="*60)
        print("🛠️  PANEL DE ADMINISTRACIÓN - REFRESCOBOT ML")
        print("="*60)
        print("1. 📊 Estadísticas del Sistema")
        print("2. 🗄️  Gestión de Base de Datos")
        print("3. 🤖 Gestión de Machine Learning") 
        print("4. 🥤 Gestión de Bebidas")
        print("5. 🔧 Diagnósticos del Sistema")
        print("6. ⚙️  Configuración Avanzada")
        print("7. 🚪 Salir")
        print("="*60)
    
    async def show_statistics(self):
        """Mostrar estadísticas del sistema"""
        print("\n📊 ESTADÍSTICAS DEL SISTEMA")
        print("-" * 40)
        
        try:
            # Estadísticas de bebidas
            total_bebidas = await self.db.bebidas.count_documents({})
            refrescos = await self.db.bebidas.count_documents({"es_refresco_real": True})
            alternativas = await self.db.bebidas.count_documents({"es_refresco_real": False})
            
            print(f"🥤 Total bebidas: {total_bebidas}")
            print(f"   - Refrescos reales: {refrescos}")
            print(f"   - Alternativas saludables: {alternativas}")
            
            # Estadísticas de sesiones
            total_sesiones = await self.db.sesiones_chat.count_documents({})
            sesiones_completadas = await self.db.sesiones_chat.count_documents({"completada": True})
            
            print(f"\n💬 Sesiones de chat:")
            print(f"   - Total sesiones: {total_sesiones}")
            print(f"   - Completadas: {sesiones_completadas}")
            
            # Estadísticas de puntuaciones
            total_puntuaciones = await self.db.puntuaciones.count_documents({})
            puntuaciones_presentacion = await self.db.puntuaciones_presentacion.count_documents({}) if await self.db.list_collection_names().__contains__("puntuaciones_presentacion") else 0
            
            print(f"\n⭐ Puntuaciones:")
            print(f"   - Puntuaciones generales: {total_puntuaciones}")
            print(f"   - Puntuaciones por presentación: {puntuaciones_presentacion}")
            
            # Estadísticas de preguntas
            total_preguntas = await self.db.preguntas.count_documents({})
            pregunta_fija = await self.db.preguntas.count_documents({"es_fija": True})
            
            print(f"\n❓ Preguntas:")
            print(f"   - Total preguntas: {total_preguntas}")
            print(f"   - Pregunta fija: {pregunta_fija}")
            
            # Estadísticas ML
            try:
                from ml_engine import ml_engine
                ml_stats = ml_engine.get_model_stats()
                print(f"\n🤖 Machine Learning:")
                print(f"   - Modelo entrenado: {'Sí' if ml_stats.get('is_trained', False) else 'No'}")
                print(f"   - Datos de entrenamiento: {ml_stats.get('training_samples', 0)}")
                print(f"   - Clusters activos: {ml_stats.get('n_clusters', 0)}")
            except Exception as e:
                print(f"\n🤖 Machine Learning: Error obteniendo stats - {e}")
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
    
    async def database_management(self):
        """Gestión de base de datos"""
        print("\n🗄️  GESTIÓN DE BASE DE DATOS")
        print("-" * 40)
        print("1. Limpiar SOLO sesiones (mantener bebidas/preguntas)")
        print("2. Limpiar SOLO bebidas y preguntas (mantener sesiones)")
        print("3. Limpiar TODO (PELIGROSO)")
        print("4. Exportar datos a JSON")
        print("5. Volver al menú principal")
        
        choice = input("\nSelecciona una opción: ")
        
        if choice == "1":
            await self.clean_sessions_only()
        elif choice == "2":
            await self.clean_beverages_questions()
        elif choice == "3":
            await self.clean_all_data()
        elif choice == "4":
            await self.export_data()
        
    async def clean_sessions_only(self):
        """Limpiar solo sesiones"""
        confirm = input("⚠️  ¿Confirmas limpiar SOLO las sesiones? (esto eliminará el aprendizaje) [y/N]: ")
        if confirm.lower() == 'y':
            try:
                from data_manager import DataManager
                dm = DataManager(self.db)
                await dm.clean_sessions_only()
                print("✅ Sesiones limpiadas exitosamente")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def clean_beverages_questions(self):
        """Limpiar solo bebidas y preguntas"""
        confirm = input("⚠️  ¿Confirmas limpiar bebidas y preguntas? (mantiene sesiones) [y/N]: ")
        if confirm.lower() == 'y':
            try:
                from data_manager import DataManager
                dm = DataManager(self.db)
                await dm.clean_database()  # La versión nueva que preserva sesiones
                print("✅ Bebidas y preguntas limpiadas (sesiones preservadas)")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def clean_all_data(self):
        """Limpiar todos los datos"""
        confirm = input("⚠️  ¿Confirmas limpiar TODO? Esto es IRREVERSIBLE [y/N]: ")
        if confirm.lower() == 'y':
            confirm2 = input("⚠️  ¿REALMENTE estás seguro? Escribe 'DELETE ALL': ")
            if confirm2 == 'DELETE ALL':
                try:
                    collections = ['preguntas', 'bebidas', 'sesiones_chat', 'puntuaciones', 'puntuaciones_presentacion']
                    for collection_name in collections:
                        collection = self.db[collection_name]
                        result = await collection.delete_many({})
                        print(f"Colección '{collection_name}': {result.deleted_count} documentos eliminados")
                    print("✅ Toda la base de datos limpiada")
                except Exception as e:
                    print(f"❌ Error: {e}")
    
    async def ml_management(self):
        """Gestión de Machine Learning"""
        print("\n🤖 GESTIÓN DE MACHINE LEARNING")
        print("-" * 40)
        print("1. Ver estadísticas de modelos")
        print("2. Reentrenar todos los modelos")
        print("3. Limpiar datos de entrenamiento")
        print("4. Generar datos sintéticos")
        print("5. Volver al menú principal")
        
        choice = input("\nSelecciona una opción: ")
        
        if choice == "1":
            await self.show_ml_stats()
        elif choice == "2":
            await self.retrain_models()
        elif choice == "3":
            await self.clear_training_data()
        elif choice == "4":
            await self.generate_synthetic_data()
    
    async def show_ml_stats(self):
        """Mostrar estadísticas detalladas de ML"""
        try:
            from ml_engine import ml_engine
            from beverage_categorizer import beverage_categorizer
            from image_analyzer import image_analyzer
            from presentation_rating_system import presentation_rating_system
            
            print("\n📊 ESTADÍSTICAS ML DETALLADAS:")
            
            # ML Engine principal
            ml_stats = ml_engine.get_model_stats()
            print(f"\n🧠 ML Engine Principal:")
            for key, value in ml_stats.items():
                print(f"   - {key}: {value}")
            
            # Beverage Categorizer
            cat_stats = beverage_categorizer.get_category_stats()
            print(f"\n🏷️  Beverage Categorizer:")
            for key, value in cat_stats.items():
                print(f"   - {key}: {value}")
            
            # Image Analyzer
            img_stats = image_analyzer.get_analysis_stats()
            print(f"\n🖼️  Image Analyzer:")
            for key, value in img_stats.items():
                print(f"   - {key}: {value}")
            
            # Presentation Rating System
            pres_stats = presentation_rating_system.get_system_stats()
            print(f"\n📦 Presentation Rating System:")
            for key, value in pres_stats.items():
                print(f"   - {key}: {value}")
                
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas ML: {e}")
    
    async def beverage_management(self):
        """Gestión de bebidas"""
        print("\n🥤 GESTIÓN DE BEBIDAS")
        print("-" * 40)
        print("1. Corregir estructura de bebidas")
        print("2. Verificar imágenes faltantes")
        print("3. Reprocesar bebidas con ML")
        print("4. Agregar nueva bebida")
        print("5. Volver al menú principal")
        
        choice = input("\nSelecciona una opción: ")
        
        if choice == "1":
            await self.fix_beverage_structure()
        elif choice == "2":
            await self.check_missing_images()
        elif choice == "3":
            await self.reprocess_beverages()
    
    async def fix_beverage_structure(self):
        """Corregir estructura de bebidas"""
        try:
            # Ejecutar el script de corrección
            import subprocess
            result = subprocess.run([sys.executable, "fix_bebidas_structure.py"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Estructura corregida")
                print(result.stdout)
            else:
                print("❌ Error:", result.stderr)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def check_missing_images(self):
        """Verificar imágenes faltantes"""
        try:
            bebidas = await self.db.bebidas.find({}).to_list(None)
            imagenes_path = Path("backend/static/images/bebidas")
            missing = []
            
            for bebida in bebidas:
                for presentacion in bebida.get('presentaciones', []):
                    imagen_local = presentacion.get('imagen_local', '')
                    imagen_file = imagen_local.replace('/static/images/', '')
                    imagen_full_path = imagenes_path / imagen_file.replace('bebidas/', '')
                    
                    if not imagen_full_path.exists():
                        missing.append(imagen_local)
            
            if missing:
                print(f"⚠️  Imágenes faltantes ({len(missing)}):")
                for img in missing:
                    print(f"   - {img}")
            else:
                print("✅ Todas las imágenes están presentes")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def system_diagnostics(self):
        """Diagnósticos del sistema"""
        print("\n🔧 DIAGNÓSTICOS DEL SISTEMA")
        print("-" * 40)
        print("1. Test conexión MongoDB")
        print("2. Test modelos ML")
        print("3. Test estructura de datos")
        print("4. Test endpoints backend")
        print("5. Volver al menú principal")
        
        choice = input("\nSelecciona una opción: ")
        
        if choice == "1":
            await self.test_mongodb()
        elif choice == "2":
            await self.test_ml_models()
        elif choice == "3":
            await self.test_data_structure()
    
    async def test_mongodb(self):
        """Test conexión MongoDB"""
        try:
            # Test básico de conectividad
            collections = await self.db.list_collection_names()
            print(f"✅ MongoDB conectado. Colecciones: {collections}")
            
            # Test de operaciones básicas
            test_doc = {"test": "conexion", "timestamp": "2025-01-01"}
            await self.db.test_connection.insert_one(test_doc)
            found = await self.db.test_connection.find_one({"test": "conexion"})
            await self.db.test_connection.delete_one({"test": "conexion"})
            
            if found:
                print("✅ Operaciones de lectura/escritura funcionando")
            else:
                print("❌ Error en operaciones de lectura/escritura")
                
        except Exception as e:
            print(f"❌ Error en test MongoDB: {e}")
    
    async def run(self):
        """Ejecutar panel de administración"""
        print("🚀 Iniciando Panel de Administración...")
        
        if not await self.connect_db():
            return
        
        try:
            while True:
                self.show_main_menu()
                choice = input("\nSelecciona una opción: ")
                
                if choice == "1":
                    await self.show_statistics()
                elif choice == "2":
                    await self.database_management()
                elif choice == "3":
                    await self.ml_management()
                elif choice == "4":
                    await self.beverage_management()
                elif choice == "5":
                    await self.system_diagnostics()
                elif choice == "7":
                    print("👋 ¡Hasta luego!")
                    break
                else:
                    print("❌ Opción inválida")
                
                input("\nPresiona Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\n👋 Panel cerrado por el usuario")
        finally:
            if self.client:
                self.client.close()

async def main():
    """Función principal"""
    # Cambiar al directorio del script
    os.chdir(Path(__file__).parent)
    
    admin = AdminPanel()
    await admin.run()

if __name__ == "__main__":
    asyncio.run(main())