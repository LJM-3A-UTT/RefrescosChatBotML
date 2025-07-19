#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir la estructura de bebidas.json
Corrige presentation_ids duplicados, datos inconsistentes y agrega campo sabor
"""

import json
import os
import sys
from pathlib import Path

# Configurar codificación para la consola de Windows
sys.stdout.reconfigure(encoding='utf-8') if sys.version_info >= (3, 7) else None

def fix_bebidas_structure():
    """Corrige problemas en la estructura de bebidas"""
    
    # Cargar bebidas.json
    base_dir = Path(__file__).parent
    bebidas_path = base_dir / "backend" / "data" / "bebidas.json"
    
    with open(bebidas_path, 'r', encoding='utf-8') as f:
        bebidas = json.load(f)
    
    print(f"[INFO] Analizando {len(bebidas)} bebidas...")
    
    # Estadísticas
    total_refrescos = 0
    total_alternativas = 0
    total_presentaciones = 0
    presentation_ids_corregidos = 0
    sabores_agregados = 0
    
    # Mapeo de sabores por categoría y nombre
    sabores_map = {
        'citricos': {
            'Fanta': 'Naranja',
            'Fanta sin Azúcar': 'Naranja',
            'Squirt': 'Toronja',
            'Orange Crush': 'Naranja',
            'Peñafiel Twist': 'Limón'
        },
        'cola': {
            'Coca-cola Light': 'Cola Original',
            'Coca-cola sin Azúcar': 'Cola Original', 
            'Coca-cola Zero': 'Cola Original'
        },
        'frutales': {
            'Delaware Punch': 'Frutas Mixtas',
            'Sidral Mundet': 'Manzana',
            'Peñafiel Adas': 'Frutas Cítricas',
            'Peñafiel Adas Sin calorías': 'Frutas Cítricas',
            'Peñafiel Sabores': 'Frutas Variadas',
            'Peñafiel Sabores Sin Azúcar': 'Frutas Variadas'
        },
        'agua': {
            'Ciel Exprim': 'Frutas Naturales',
            'Aquarius': 'Natural',
            'Aquarius Cero': 'Natural',
            'Limón & Nada': 'Limón',
            'Naranja & Nada': 'Naranja',
            'Ciel Mineralizada': 'Natural',
            'Schweppes': 'Tónica',
            'Peñafiel': 'Natural',
            'Peñafiel con agua de coco': 'Coco',
            'Peñafiel Purezza': 'Natural',
            'Peñafiel SOFT': 'Frutas Suaves'
        },
        'jugos': {
            'Del Valle': 'Frutas Naturales'
        }
    }
    
    for bebida in bebidas:
        # Contar tipos de bebidas
        if bebida['es_refresco_real']:
            total_refrescos += 1
        else:
            total_alternativas += 1
        
        # Corregir presentation_ids y agregar sabores
        for i, presentacion in enumerate(bebida['presentaciones']):
            total_presentaciones += 1
            
            # Corregir presentation_id
            ml = presentacion['ml']
            nuevo_id = f"{bebida['id']}_{ml}_{i+1}"
            
            if presentacion['presentation_id'] != nuevo_id:
                presentacion['presentation_id'] = nuevo_id
                presentation_ids_corregidos += 1
            
            # Agregar campo sabor si no existe
            if 'sabor' not in presentacion:
                categoria = bebida['categoria']
                nombre = bebida['nombre']
                
                # Buscar sabor específico
                sabor = 'Original'
                if categoria in sabores_map and nombre in sabores_map[categoria]:
                    sabor = sabores_map[categoria][nombre]
                elif categoria == 'citricos':
                    sabor = 'Cítrico'
                elif categoria == 'frutales':
                    sabor = 'Frutal'
                elif categoria == 'agua':
                    sabor = 'Natural'
                elif categoria == 'cola':
                    sabor = 'Cola'
                elif categoria == 'jugos':
                    sabor = 'Frutas Naturales'
                
                presentacion['sabor'] = sabor
                sabores_agregados += 1
            
            # Verificar descripción de presentación si no existe
            if 'descripcion_presentacion' not in presentacion:
                if ml <= 250:
                    descripcion = f"Presentación mini de {ml}ml, perfecta para probar"
                elif ml <= 400:
                    descripcion = f"Presentación individual de {ml}ml, ideal para consumo personal"
                elif ml <= 750:
                    descripcion = f"Presentación personal de {ml}ml, para hidratación extendida"
                else:
                    descripcion = f"Presentación familiar de {ml}ml, perfecta para compartir"
                
                presentacion['descripcion_presentacion'] = descripcion
    
    # Verificar imágenes existentes
    imagenes_faltantes = []
    imagenes_path = base_dir / "backend" / "static" / "images" / "bebidas"
    
    for bebida in bebidas:
        for presentacion in bebida['presentaciones']:
            imagen_local = presentacion['imagen_local']
            # Remover el prefijo /static/images/
            imagen_file = imagen_local.replace('/static/images/', '')
            imagen_full_path = imagenes_path / imagen_file.replace('bebidas/', '')
            
            if not imagen_full_path.exists():
                imagenes_faltantes.append(imagen_local)
    
    # Guardar bebidas corregidas
    with open(bebidas_path, 'w', encoding='utf-8') as f:
        json.dump(bebidas, f, indent=2, ensure_ascii=False)
    
# Mostrar estadísticas SIN EMOJIS
    print("\n[ESTADISTICAS] ESTADÍSTICAS DE CORRECCIÓN:")
    print(f"  - Total bebidas: {len(bebidas)}")
    print(f"  - Refrescos reales: {total_refrescos}")
    print(f"  - Alternativas saludables: {total_alternativas}")
    print(f"  - Total presentaciones: {total_presentaciones}")
    print(f"  - Presentation IDs corregidos: {presentation_ids_corregidos}")
    print(f"  - Sabores agregados: {sabores_agregados}")
    
    if imagenes_faltantes:
        print(f"\n[ADVERTENCIA] IMÁGENES FALTANTES ({len(imagenes_faltantes)}):")
        for imagen in imagenes_faltantes[:5]:
            print(f"  - {imagen}")
        if len(imagenes_faltantes) > 5:
            print(f"  ... y {len(imagenes_faltantes) - 5} más")
    else:
        print("\n[OK] Todas las imágenes están presentes")
    
    print(f"\n[COMPLETADO] Estructura corregida y guardada en {bebidas_path}")
    
    return {
        'total_bebidas': len(bebidas),
        'refrescos': total_refrescos,
        'alternativas': total_alternativas,
        'presentaciones': total_presentaciones,
        'ids_corregidos': presentation_ids_corregidos,
        'sabores_agregados': sabores_agregados,
        'imagenes_faltantes': len(imagenes_faltantes)
    }

if __name__ == "__main__":
    fix_bebidas_structure()