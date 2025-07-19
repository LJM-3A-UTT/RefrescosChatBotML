#!/usr/bin/env python3
"""
Panel de Administración para RefrescoBot ML
Ejecutar: python admin_panel.py

Este script te permite:
1. Ver todas las bebidas y preguntas
2. Agregar nuevas bebidas
3. Agregar nuevas preguntas
4. Ver estadísticas del sistema
5. Exportar/Importar datos
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path
import uuid
from datetime import datetime
import json

# Cargar variables de entorno
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

class AdminPanel:
    def __init__(self):
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[db_name]
    
    async def mostrar_menu(self):
        """Muestra el menú principal del panel de administración"""
        print("\n" + "="*60)
        print("🤖 PANEL DE ADMINISTRACIÓN - REFRESCOBOT ML")
        print("="*60)
        print("1. 📋 Ver todas las preguntas")
        print("2. 🥤 Ver todas las bebidas")
        print("3. ➕ Agregar nueva pregunta")
        print("4. ➕ Agregar nueva bebida")
        print("5. 📊 Ver estadísticas del sistema")
        print("6. 📤 Exportar datos")
        print("7. 🧹 Limpiar sesiones antiguas")
        print("8. ❌ Salir")
        print("="*60)
        
        opcion = input("Selecciona una opción (1-8): ").strip()
        return opcion
    
    async def listar_preguntas(self):
        """Lista todas las preguntas disponibles"""
        print("\n📋 LISTA DE PREGUNTAS:")
        print("-" * 80)
        
        preguntas = await self.db.preguntas.find().to_list(1000)
        
        for i, pregunta in enumerate(preguntas, 1):
            print(f"\n{i}. {'[FIJA]' if pregunta.get('es_fija') else '[ALEATORIA]'} {pregunta['texto']}")
            print(f"   Categoría: {pregunta.get('categoria', 'N/A')}")
            print(f"   Peso: {pregunta.get('peso_algoritmo', 1.0)}")
            print("   Opciones:")
            for j, opcion in enumerate(pregunta['opciones'], 1):
                print(f"     {j}. {opcion}")
        
        print(f"\n📊 Total: {len(preguntas)} preguntas")
        input("\nPresiona Enter para continuar...")
    
    async def listar_bebidas(self):
        """Lista todas las bebidas disponibles"""
        print("\n🥤 LISTA DE BEBIDAS:")
        print("-" * 80)
        
        bebidas = await self.db.bebidas.find().to_list(1000)
        
        for i, bebida in enumerate(bebidas, 1):
            print(f"\n{i}. {bebida['nombre']} - ${bebida['precio']}")
            print(f"   Tipo: {bebida['tipo']} | Sabor: {bebida['sabor_principal']}")
            print(f"   Carbonatada: {'Sí' if bebida['es_carbonatada'] else 'No'} | "
                  f"Azucarada: {'Sí' if bebida['es_azucarada'] else 'No'}")
            print(f"   Presentaciones: {', '.join(map(str, bebida['presentaciones_ml']))} ml")
            print(f"   Descripción: {bebida['descripcion']}")
            print(f"   Puntuación: {bebida['puntuacion_promedio']:.1f} "
                  f"({bebida['total_puntuaciones']} puntuaciones)")
        
        print(f"\n📊 Total: {len(bebidas)} bebidas")
        input("\nPresiona Enter para continuar...")
    
    async def agregar_pregunta(self):
        """Agrega una nueva pregunta al sistema"""
        print("\n➕ AGREGAR NUEVA PREGUNTA:")
        print("-" * 40)
        
        texto = input("Ingresa el texto de la pregunta: ").strip()
        if not texto:
            print("❌ El texto no puede estar vacío")
            return
        
        print("\nIngresa 5 opciones de respuesta:")
        opciones = []
        for i in range(5):
            opcion = input(f"Opción {i+1}: ").strip()
            if not opcion:
                print("❌ La opción no puede estar vacía")
                return
            opciones.append(opcion)
        
        es_fija = input("\n¿Es una pregunta fija? (s/n): ").lower().startswith('s')
        
        print("\nCategorías disponibles: rutina, estado_animo, preferencias, fisico, temporal")
        categoria = input("Categoría: ").strip() or "general"
        
        try:
            peso = float(input("Peso en el algoritmo (1.0-3.0): ") or "1.0")
        except ValueError:
            peso = 1.0
        
        nueva_pregunta = {
            "id": str(uuid.uuid4()),
            "texto": texto,
            "opciones": opciones,
            "es_fija": es_fija,
            "peso_algoritmo": peso,
            "categoria": categoria,
            "created_at": datetime.utcnow()
        }
        
        await self.db.preguntas.insert_one(nueva_pregunta)
        print("✅ Pregunta agregada exitosamente!")
        input("Presiona Enter para continuar...")
    
    async def agregar_bebida(self):
        """Agrega una nueva bebida al sistema"""
        print("\n➕ AGREGAR NUEVA BEBIDA:")
        print("-" * 40)
        
        nombre = input("Nombre de la bebida: ").strip()
        if not nombre:
            print("❌ El nombre no puede estar vacío")
            return
        
        descripcion = input("Descripción: ").strip()
        if not descripcion:
            print("❌ La descripción no puede estar vacía")
            return
        
        try:
            precio = float(input("Precio (MXN): "))
        except ValueError:
            print("❌ Precio inválido")
            return
        
        presentaciones_str = input("Presentaciones en ml (separadas por coma): ").strip()
        try:
            presentaciones_ml = [int(x.strip()) for x in presentaciones_str.split(',')]
        except ValueError:
            print("❌ Presentaciones inválidas")
            return
        
        imagen_local = input("Nombre del archivo de imagen (ej: nueva_bebida.jpg): ").strip()
        if not imagen_local:
            print("Error: Nombre de imagen es requerido")
            return
        
        print("\nTipos disponibles: refresco, agua, jugo, te, cafe, energetica")
        tipo = input("Tipo de bebida: ").strip() or "refresco"
        
        es_carbonatada = input("¿Es carbonatada? (s/n): ").lower().startswith('s')
        es_azucarada = input("¿Es azucarada? (s/n): ").lower().startswith('s')
        
        sabor_principal = input("Sabor principal: ").strip() or "general"
        
        nueva_bebida = {
            "id": str(uuid.uuid4()),
            "nombre": nombre,
            "descripcion": descripcion,
            "precio": precio,
            "presentaciones_ml": presentaciones_ml,
            "imagen_local": f"bebidas/{imagen_local}",
            "tipo": tipo,
            "es_carbonatada": es_carbonatada,
            "es_azucarada": es_azucarada,
            "sabor_principal": sabor_principal,
            "puntuacion_promedio": 0.0,
            "total_puntuaciones": 0,
            "created_at": datetime.utcnow()
        }
        
        await self.db.bebidas.insert_one(nueva_bebida)
        print("✅ Bebida agregada exitosamente!")
        print(f"💡 No olvides agregar la imagen: /app/backend/static/images/bebidas/{imagen_local}")
        input("Presiona Enter para continuar...")
    
    async def mostrar_estadisticas(self):
        """Muestra estadísticas del sistema"""
        print("\n📊 ESTADÍSTICAS DEL SISTEMA:")
        print("-" * 50)
        
        # Estadísticas básicas
        total_preguntas = await self.db.preguntas.count_documents({})
        preguntas_fijas = await self.db.preguntas.count_documents({"es_fija": True})
        total_bebidas = await self.db.bebidas.count_documents({})
        total_sesiones = await self.db.sesiones.count_documents({})
        sesiones_completadas = await self.db.sesiones.count_documents({"estado_sesion": "completada"})
        usuarios_curiosos = await self.db.sesiones.count_documents({"es_usuario_curioso": True})
        
        print(f"📝 Preguntas: {total_preguntas} ({preguntas_fijas} fijas, {total_preguntas - preguntas_fijas} aleatorias)")
        print(f"🥤 Bebidas: {total_bebidas}")
        print(f"👥 Sesiones totales: {total_sesiones}")
        print(f"✅ Sesiones completadas: {sesiones_completadas}")
        print(f"🤔 Usuarios curiosos detectados: {usuarios_curiosos}")
        
        if total_sesiones > 0:
            tasa_completado = (sesiones_completadas / total_sesiones) * 100
            print(f"📈 Tasa de completado: {tasa_completado:.1f}%")
        
        # Bebidas mejor puntuadas
        print("\n🏆 BEBIDAS MEJOR PUNTUADAS:")
        bebidas_top = await self.db.bebidas.find({
            "total_puntuaciones": {"$gt": 0}
        }).sort("puntuacion_promedio", -1).limit(5).to_list(5)
        
        for i, bebida in enumerate(bebidas_top, 1):
            print(f"{i}. {bebida['nombre']}: {bebida['puntuacion_promedio']:.1f} ⭐ "
                  f"({bebida['total_puntuaciones']} puntuaciones)")
        
        # Distribución por tipo de bebida
        print("\n📊 DISTRIBUCIÓN POR TIPO:")
        tipos = await self.db.bebidas.aggregate([
            {"$group": {"_id": "$tipo", "count": {"$sum": 1}}}
        ]).to_list(1000)
        
        for tipo in tipos:
            print(f"• {tipo['_id']}: {tipo['count']} bebidas")
        
        input("\nPresiona Enter para continuar...")
    
    async def exportar_datos(self):
        """Exporta datos a un archivo JSON"""
        print("\n📤 EXPORTAR DATOS:")
        print("-" * 30)
        
        # Obtener todos los datos
        preguntas = await self.db.preguntas.find().to_list(1000)
        bebidas = await self.db.bebidas.find().to_list(1000)
        
        datos_exportacion = {
            "exportado_en": datetime.utcnow().isoformat(),
            "preguntas": preguntas,
            "bebidas": bebidas
        }
        
        archivo = f"refrescobot_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos_exportacion, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ Datos exportados a: {archivo}")
        print(f"📊 Preguntas: {len(preguntas)}")
        print(f"📊 Bebidas: {len(bebidas)}")
        input("Presiona Enter para continuar...")
    
    async def limpiar_sesiones(self):
        """Limpia sesiones antiguas"""
        print("\n🧹 LIMPIAR SESIONES ANTIGUAS:")
        print("-" * 35)
        
        confirmacion = input("¿Estás seguro de eliminar todas las sesiones? (escribe 'CONFIRMAR'): ")
        if confirmacion != 'CONFIRMAR':
            print("❌ Operación cancelada")
            return
        
        resultado = await self.db.sesiones.delete_many({})
        print(f"✅ Eliminadas {resultado.deleted_count} sesiones")
        input("Presiona Enter para continuar...")
    
    async def ejecutar(self):
        """Ejecuta el panel de administración"""
        try:
            while True:
                opcion = await self.mostrar_menu()
                
                if opcion == '1':
                    await self.listar_preguntas()
                elif opcion == '2':
                    await self.listar_bebidas()
                elif opcion == '3':
                    await self.agregar_pregunta()
                elif opcion == '4':
                    await self.agregar_bebida()
                elif opcion == '5':
                    await self.mostrar_estadisticas()
                elif opcion == '6':
                    await self.exportar_datos()
                elif opcion == '7':
                    await self.limpiar_sesiones()
                elif opcion == '8':
                    print("\n👋 ¡Gracias por usar RefrescoBot ML!")
                    break
                else:
                    print("\n❌ Opción no válida. Intenta de nuevo.")
                    
        except KeyboardInterrupt:
            print("\n\n👋 Panel cerrado por el usuario")
        finally:
            self.client.close()

if __name__ == "__main__":
    print("🚀 Iniciando Panel de Administración...")
    panel = AdminPanel()
    asyncio.run(panel.ejecutar())