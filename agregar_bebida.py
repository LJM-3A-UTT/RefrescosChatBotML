#!/usr/bin/env python3
"""
Script para agregar nuevas bebidas fácilmente
Uso: python agregar_bebida.py
"""

import json
from datetime import datetime
from pathlib import Path

def agregar_bebida_interactiva():
    """Agrega una bebida nueva de forma interactiva"""
    
    # Cargar bebidas existentes
    bebidas_file = Path("/app/backend/data/bebidas.json")
    with open(bebidas_file, 'r', encoding='utf-8') as f:
        bebidas = json.load(f)
    
    # Obtener siguiente ID
    max_id = max([b["id"] for b in bebidas])
    nuevo_id = max_id + 1
    
    print(f"🍹 AGREGANDO NUEVA BEBIDA (ID: {nuevo_id})")
    print("=" * 50)
    
    # Recopilar información básica
    nombre = input("📝 Nombre de la bebida: ")
    descripcion = input("📄 Descripción: ")
    
    # Categoría
    print("\n📂 Categorías disponibles:")
    categorias = ["cola", "citricos", "frutales", "energeticas", "agua", "jugos", "tes"]
    for i, cat in enumerate(categorias, 1):
        print(f"  {i}. {cat}")
    
    cat_idx = int(input("Selecciona categoría (1-7): ")) - 1
    categoria = categorias[cat_idx]
    
    # Tipo de bebida
    es_refresco = input("🥤 ¿Es refresco real? (s/n): ").lower() == 's'
    
    # Características
    nivel_dulzura = int(input("🍯 Nivel de dulzura (0-10): "))
    es_energizante = input("⚡ ¿Es energizante? (s/n): ").lower() == 's'
    
    # Perfil de sabor
    print("\n🎨 Perfiles de sabor:")
    perfiles = ["dulce_clasico", "citrico_refrescante", "frutal_tropical", 
                "energetico_frutal", "natural_puro", "herbal_refrescante"]
    for i, perfil in enumerate(perfiles, 1):
        print(f"  {i}. {perfil}")
    
    perfil_idx = int(input("Selecciona perfil (1-6): ")) - 1
    perfil_sabor = perfiles[perfil_idx]
    
    # Calorías
    print("\n🔥 Contenido calórico:")
    calorias_opciones = ["cero", "bajo", "medio", "alto"]
    for i, cal in enumerate(calorias_opciones, 1):
        print(f"  {i}. {cal}")
    
    cal_idx = int(input("Selecciona calorías (1-4): ")) - 1
    contenido_calorias = calorias_opciones[cal_idx]
    
    precio_base = float(input("💰 Precio base: $"))
    
    # Presentaciones
    print("\n📦 Agregando presentaciones...")
    presentaciones = []
    
    while True:
        ml = int(input("  📏 Mililitros: "))
        precio = float(input("  💵 Precio: $"))
        imagen = input("  🖼️  Ruta imagen (ej: /static/images/bebidas/Bebida_500ml.webp): ")
        
        # Determinar categoría por tamaño
        if ml <= 250:
            cat_pres = "mini"
        elif ml <= 400:
            cat_pres = "individual"
        elif ml <= 750:
            cat_pres = "personal"
        else:
            cat_pres = "familiar"
        
        presentacion = {
            "presentation_id": f"{nuevo_id}_{ml}",
            "ml": ml,
            "precio": precio,
            "imagen_local": imagen,
            "puntuacion_promedio": 3.0,
            "total_puntuaciones": 0,
            "categoria_presentacion": cat_pres
        }
        
        presentaciones.append(presentacion)
        
        if input("  ➕ ¿Agregar otra presentación? (s/n): ").lower() != 's':
            break
    
    # Crear bebida completa
    nueva_bebida = {
        "id": nuevo_id,
        "nombre": nombre,
        "descripcion": descripcion,
        "categoria": categoria,
        "es_refresco_real": es_refresco,
        "nivel_dulzura": nivel_dulzura,
        "es_energizante": es_energizante,
        "perfil_sabor": perfil_sabor,
        "contenido_calorias": contenido_calorias,
        "precio_base": precio_base,
        "presentaciones": presentaciones,
        "categorias_ml": [],
        "tags_automaticos": [],
        "cluster_id": None,
        "features_imagen": None,
        "fecha_agregado": datetime.now().isoformat(),
        "procesado_ml": False
    }
    
    # Agregar a la lista
    bebidas.append(nueva_bebida)
    
    # Guardar archivo
    with open(bebidas_file, 'w', encoding='utf-8') as f:
        json.dump(bebidas, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Bebida '{nombre}' agregada exitosamente!")
    print(f"🔄 Reinicia el backend para procesamiento ML automático")
    print(f"📊 Total de bebidas: {len(bebidas)}")

if __name__ == "__main__":
    agregar_bebida_interactiva()