#!/usr/bin/env python3
"""
Script para inicializar la base de datos MongoDB Atlas 'refrescos_chat_bot'
Uso: python inicializar_atlas.py
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Añadir el directorio backend al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_manager import initialize_system_data

async def main():
    """Inicializar base de datos en MongoDB Atlas"""
    
    print("🌐 Inicializando base de datos MongoDB Atlas: refrescos_chat_bot")
    print("=" * 65)
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Configuración Atlas
    MONGO_URL = "mongodb+srv://LJM:ljm542136@cluster0.7mlbi.mongodb.net/refrescos_chat_bot"
    DB_NAME = "refrescos_chat_bot"
    
    try:
        # Conectar a MongoDB Atlas
        print(f"🌐 Conectando a MongoDB Atlas...")
        print(f"📍 Cluster: cluster0.7mlbi.mongodb.net")
        print(f"🗄️ Base de datos: {DB_NAME}")
        
        client = AsyncIOMotorClient(MONGO_URL)
        
        # Verificar conexión
        await client.admin.command('ismaster')
        print("✅ Conexión a MongoDB Atlas exitosa")
        
        # Seleccionar base de datos
        db = client[DB_NAME]
        
        # Verificar si ya existen datos
        bebidas_existentes = await db.bebidas.count_documents({})
        preguntas_existentes = await db.preguntas.count_documents({})
        
        if bebidas_existentes > 0 or preguntas_existentes > 0:
            print(f"📊 Datos existentes encontrados:")
            print(f"   - Bebidas: {bebidas_existentes}")
            print(f"   - Preguntas: {preguntas_existentes}")
            
            respuesta = input("\n❓ ¿Limpiar y recargar datos? (s/n): ").lower()
            clean_first = respuesta == 's'
        else:
            print("📝 Base de datos vacía, inicializando...")
            clean_first = True
        
        if clean_first:
            print("🧹 Limpiando base de datos existente...")
            await initialize_system_data(db, clean_first=True)
        
        # Verificar datos cargados
        bebidas_count = await db.bebidas.count_documents({})
        preguntas_count = await db.preguntas.count_documents({})
        
        print("✅ Base de datos Atlas configurada exitosamente!")
        print(f"📊 Bebidas cargadas: {bebidas_count}")
        print(f"❓ Preguntas cargadas: {preguntas_count}")
        
        # Estadísticas de presentaciones
        bebidas = await db.bebidas.find({}, {"_id": 0}).to_list(None)
        total_presentaciones = sum(len(b.get('presentaciones', [])) for b in bebidas)
        print(f"📦 Total presentaciones: {total_presentaciones}")
        
        # Verificar nuevas bebidas incluidas
        nuevas_bebidas = [b for b in bebidas if b['id'] in [16, 17, 18]]
        if nuevas_bebidas:
            print(f"\n🆕 Bebidas nuevas incluidas:")
            for bebida in nuevas_bebidas:
                print(f"   - {bebida['nombre']} ({len(bebida.get('presentaciones', []))} presentaciones)")
        
        # Mostrar estadísticas por tipo
        refrescos = [b for b in bebidas if b.get('es_refresco_real', True)]
        alternativas = [b for b in bebidas if not b.get('es_refresco_real', True)]
        
        print(f"\n📊 Distribución:")
        print(f"   🥤 Refrescos reales: {len(refrescos)}")
        print(f"   🌿 Alternativas saludables: {len(alternativas)}")
        
        print(f"\n🎯 Base de datos 'refrescos_chat_bot' en Atlas lista!")
        print("🌐 Requiere conexión a internet para funcionar")
        print("🚀 Backend y frontend funcionan localmente")
        
        # Cerrar conexión
        client.close()
        
    except Exception as e:
        print(f"❌ Error conectando a Atlas: {e}")
        print("\n💡 Posibles soluciones:")
        print("   1. Verificar conexión a internet")
        print("   2. Confirmar credenciales de MongoDB Atlas")
        print("   3. Verificar que la IP está en whitelist de Atlas")
        print("   4. Comprobar que el cluster está activo")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1)