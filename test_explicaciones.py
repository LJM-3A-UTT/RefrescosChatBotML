#!/usr/bin/env python3
"""
Script para probar las explicaciones del sistema
"""

import requests
import json
import time

# URL de tu backend local
API_URL = "http://localhost:8001/api"

def test_explicaciones():
    print("🧪 PROBANDO EXPLICACIONES DEL SISTEMA")
    print("="*50)
    
    try:
        # 1. Crear sesión
        print("1. Creando sesión...")
        response = requests.post(f"{API_URL}/iniciar-sesion")
        if response.status_code != 200:
            print(f"❌ Error creando sesión: {response.status_code}")
            return
        
        session_data = response.json()
        session_id = session_data['sesion_id']
        print(f"✅ Sesión creada: {session_id}")
        
        # 2. Obtener primera pregunta
        print("\n2. Obteniendo primera pregunta...")
        response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
        if response.status_code != 200:
            print(f"❌ Error obteniendo pregunta: {response.status_code}")
            return
        
        pregunta_inicial = response.json()
        print(f"✅ Primera pregunta: {pregunta_inicial['pregunta']['pregunta']}")
        
        # 3. Responder todas las preguntas
        print("\n3. Respondiendo preguntas...")
        
        # Respuesta para usuario regular que consume refrescos y es activo
        respuestas_ejemplo = [
            {
                "pregunta_id": pregunta_inicial['pregunta']['id'],
                "respuesta_id": 2,  # "Varias veces por semana"
                "respuesta_texto": "Varias veces por semana",
                "tiempo_respuesta": 5.0
            }
        ]
        
        # Responder primera pregunta
        response = requests.post(f"{API_URL}/responder/{session_id}", json=respuestas_ejemplo[0])
        if response.status_code != 200:
            print(f"❌ Error respondiendo primera pregunta: {response.status_code}")
            return
        
        # Responder las siguientes 5 preguntas
        for i in range(5):
            # Obtener siguiente pregunta
            response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
            if response.status_code != 200:
                print(f"❌ Error obteniendo pregunta {i+2}: {response.status_code}")
                continue
            
            pregunta_data = response.json()
            if pregunta_data.get('finalizada'):
                print("✅ Preguntas completadas")
                break
            
            pregunta = pregunta_data['pregunta']
            
            # Responder con opciones específicas para generar un perfil interesante
            respuesta_id = 2  # Generalmente la segunda opción
            if "activ" in pregunta['pregunta'].lower():
                respuesta_id = 2  # Activo
            elif "dulce" in pregunta['pregunta'].lower():
                respuesta_id = 2  # Dulce moderado
            elif "salud" in pregunta['pregunta'].lower():
                respuesta_id = 3  # Moderadamente importante
            elif "estilo" in pregunta['pregunta'].lower():
                respuesta_id = 2  # Ocupado pero manejable
            
            respuesta = {
                "pregunta_id": pregunta['id'],
                "respuesta_id": respuesta_id,
                "respuesta_texto": pregunta['opciones'][respuesta_id-1]['texto'],
                "tiempo_respuesta": 4.0 + i * 0.5  # Tiempo normal
            }
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json=respuesta)
            if response.status_code != 200:
                print(f"❌ Error respondiendo pregunta {i+2}: {response.status_code}")
                continue
            
            print(f"✅ Respondido: {pregunta['pregunta'][:50]}...")
        
        # 4. Obtener recomendaciones
        print("\n4. Obteniendo recomendaciones...")
        response = requests.get(f"{API_URL}/recomendacion/{session_id}")
        if response.status_code != 200:
            print(f"❌ Error obteniendo recomendaciones: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return
        
        recomendaciones = response.json()
        print(f"✅ Recomendaciones obtenidas")
        
        # 5. Mostrar explicaciones
        print("\n5. EXPLICACIONES GENERADAS:")
        print("="*50)
        
        refrescos = recomendaciones.get('refrescos_reales', [])
        alternativas = recomendaciones.get('bebidas_alternativas', [])
        
        print(f"\n🥤 REFRESCOS REALES ({len(refrescos)}):")
        for i, bebida in enumerate(refrescos, 1):
            print(f"\n{i}. {bebida['nombre']} (Compatibilidad: {bebida.get('probabilidad', 0):.1f}%)")
            explicaciones = bebida.get('factores_explicativos', [])
            if explicaciones:
                print("   Razones:")
                for exp in explicaciones:
                    print(f"   • {exp}")
            else:
                print("   ❌ Sin explicaciones generadas")
        
        print(f"\n🌱 ALTERNATIVAS SALUDABLES ({len(alternativas)}):")
        for i, bebida in enumerate(alternativas, 1):
            print(f"\n{i}. {bebida['nombre']} (Compatibilidad: {bebida.get('probabilidad', 0):.1f}%)")
            explicaciones = bebida.get('factores_explicativos', [])
            if explicaciones:
                print("   Razones:")
                for exp in explicaciones:
                    print(f"   • {exp}")
            else:
                print("   ❌ Sin explicaciones generadas")
        
        # 6. Mostrar información de debug
        print(f"\n🔍 INFO DE DEBUG:")
        criterios = recomendaciones.get('criterios_ml', {})
        print(f"   • Tipo de usuario detectado: {criterios.get('tipo_usuario_detectado', 'N/A')}")
        print(f"   • Cluster asignado: {criterios.get('cluster_usuario', 'N/A')}")
        print(f"   • Tiempo promedio respuesta: {criterios.get('tiempo_promedio_respuesta', 0):.2f} seg")
        print(f"   • Modelo entrenado: {criterios.get('modelo_entrenado', False)}")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_explicaciones()