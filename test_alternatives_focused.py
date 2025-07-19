#!/usr/bin/env python3
"""
Focused test for /api/recomendaciones-alternativas/{sesion_id} endpoint
"""

import requests
import json
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("/app/frontend/.env")

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001")
API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

def create_and_complete_session(consumption_level="moderate"):
    """Create a session and complete all questions"""
    try:
        # Create session
        response = requests.post(f"{API_URL}/iniciar-sesion")
        response.raise_for_status()
        data = response.json()
        session_id = data["sesion_id"]
        print(f"✅ Created session: {session_id}")
        
        # Get initial question (about soda consumption)
        response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
        response.raise_for_status()
        data = response.json()
        question = data["pregunta"]
        
        print(f"Initial question: {question['pregunta']}")
        for i, option in enumerate(question["opciones"]):
            print(f"  {i}: {option['texto']}")
        
        # Choose consumption level
        if consumption_level == "never":
            # Choose "Nunca o casi nunca"
            selected_option = question["opciones"][4]  # Last option is usually "never"
        elif consumption_level == "frequent":
            # Choose "Todos los días" or "Varias veces por semana"
            selected_option = question["opciones"][1]  # Frequent consumption
        else:  # moderate
            # Choose "De vez en cuando"
            selected_option = question["opciones"][3]  # Moderate consumption
        
        print(f"Selected: {selected_option['texto']}")
        
        # Answer initial question
        response = requests.post(f"{API_URL}/responder/{session_id}", json={
            "pregunta_id": question["id"],
            "respuesta_id": selected_option["id"],
            "respuesta_texto": selected_option["texto"],
            "tiempo_respuesta": 5.0
        })
        response.raise_for_status()
        
        # Answer remaining questions
        questions_answered = 1
        while questions_answered < 6:  # Total 6 questions
            response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "finalizada" in data and data["finalizada"]:
                break
                
            if "pregunta" not in data:
                break
                
            question = data["pregunta"]
            
            # Choose health-conscious options for health-conscious users
            if consumption_level == "never":
                # Choose options that indicate health consciousness
                selected_option = choose_health_conscious_option(question["opciones"])
            elif consumption_level == "frequent":
                # Choose traditional options
                selected_option = choose_traditional_option(question["opciones"])
            else:
                # Choose moderate options
                selected_option = question["opciones"][len(question["opciones"])//2]
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": random.uniform(3.0, 8.0)
            })
            response.raise_for_status()
            
            questions_answered += 1
        
        print(f"✅ Completed {questions_answered} questions")
        return session_id
        
    except Exception as e:
        print(f"❌ Error creating session: {str(e)}")
        return None

def choose_health_conscious_option(options):
    """Choose health-conscious options"""
    health_keywords = ["natural", "saludable", "agua", "sin azúcar", "activo", "muy_activo", "ejercicio", "importante", "muy_importante", "salud"]
    
    for option in options:
        if any(keyword in option["texto"].lower() for keyword in health_keywords):
            return option
    
    # If no clear healthy option, choose the last one
    return options[-1] if options else options[0]

def choose_traditional_option(options):
    """Choose traditional options"""
    traditional_keywords = ["normal", "regular", "clásico", "tradicional", "dulce", "frecuente", "siempre", "todos los días"]
    
    for option in options:
        if any(keyword in option["texto"].lower() for keyword in traditional_keywords):
            return option
    
    # If no clear traditional option, choose first option
    return options[0] if options else options[0]

def test_alternative_recommendations():
    """Test the alternative recommendations endpoint for different user types"""
    print("\n" + "="*80)
    print("🔍 TESTING /api/recomendaciones-alternativas/{sesion_id}")
    print("="*80)
    
    # Test Case 1: User who never consumes sodas
    print("\n📋 TEST CASE 1: User who NEVER consumes sodas")
    session_id_1 = create_and_complete_session("never")
    if not session_id_1:
        print("❌ Failed to create never-consumer session")
        return False
    
    # Get initial recommendations
    response = requests.get(f"{API_URL}/recomendacion/{session_id_1}")
    response.raise_for_status()
    initial_data = response.json()
    
    print(f"Initial recommendations:")
    print(f"  - Refrescos reales: {len(initial_data.get('refrescos_reales', []))}")
    print(f"  - Bebidas alternativas: {len(initial_data.get('bebidas_alternativas', []))}")
    print(f"  - Usuario no consume refrescos: {initial_data.get('usuario_no_consume_refrescos', False)}")
    
    # Test alternative recommendations
    response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id_1}")
    response.raise_for_status()
    alt_data = response.json()
    
    print(f"Alternative recommendations:")
    print(f"  - Recomendaciones adicionales: {len(alt_data.get('recomendaciones_adicionales', []))}")
    print(f"  - Tipo de recomendaciones: {alt_data.get('tipo_recomendaciones', 'N/A')}")
    print(f"  - Sin más opciones: {alt_data.get('sin_mas_opciones', False)}")
    print(f"  - Usuario no consume refrescos: {alt_data.get('usuario_no_consume_refrescos', False)}")
    
    # Verify structure
    if "recomendaciones_adicionales" not in alt_data:
        print("❌ Missing 'recomendaciones_adicionales' field")
        return False
    
    if "tipo_recomendaciones" not in alt_data:
        print("❌ Missing 'tipo_recomendaciones' field")
        return False
    
    print("✅ Response structure is correct")
    
    # Test Case 2: User who frequently consumes sodas
    print("\n📋 TEST CASE 2: User who FREQUENTLY consumes sodas")
    session_id_2 = create_and_complete_session("frequent")
    if not session_id_2:
        print("❌ Failed to create frequent-consumer session")
        return False
    
    # Get initial recommendations
    response = requests.get(f"{API_URL}/recomendacion/{session_id_2}")
    response.raise_for_status()
    initial_data = response.json()
    
    print(f"Initial recommendations:")
    print(f"  - Refrescos reales: {len(initial_data.get('refrescos_reales', []))}")
    print(f"  - Bebidas alternativas: {len(initial_data.get('bebidas_alternativas', []))}")
    print(f"  - Usuario no consume refrescos: {initial_data.get('usuario_no_consume_refrescos', False)}")
    
    # Test alternative recommendations
    response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id_2}")
    response.raise_for_status()
    alt_data = response.json()
    
    print(f"Alternative recommendations:")
    print(f"  - Recomendaciones adicionales: {len(alt_data.get('recomendaciones_adicionales', []))}")
    print(f"  - Tipo de recomendaciones: {alt_data.get('tipo_recomendaciones', 'N/A')}")
    print(f"  - Sin más opciones: {alt_data.get('sin_mas_opciones', False)}")
    print(f"  - Usuario no consume refrescos: {alt_data.get('usuario_no_consume_refrescos', False)}")
    
    # Test Case 3: Moderate user
    print("\n📋 TEST CASE 3: User with MODERATE consumption")
    session_id_3 = create_and_complete_session("moderate")
    if not session_id_3:
        print("❌ Failed to create moderate-consumer session")
        return False
    
    # Get initial recommendations
    response = requests.get(f"{API_URL}/recomendacion/{session_id_3}")
    response.raise_for_status()
    initial_data = response.json()
    
    print(f"Initial recommendations:")
    print(f"  - Refrescos reales: {len(initial_data.get('refrescos_reales', []))}")
    print(f"  - Bebidas alternativas: {len(initial_data.get('bebidas_alternativas', []))}")
    print(f"  - Usuario no consume refrescos: {initial_data.get('usuario_no_consume_refrescos', False)}")
    
    # Test alternative recommendations
    response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id_3}")
    response.raise_for_status()
    alt_data = response.json()
    
    print(f"Alternative recommendations:")
    print(f"  - Recomendaciones adicionales: {len(alt_data.get('recomendaciones_adicionales', []))}")
    print(f"  - Tipo de recomendaciones: {alt_data.get('tipo_recomendaciones', 'N/A')}")
    print(f"  - Sin más opciones: {alt_data.get('sin_mas_opciones', False)}")
    print(f"  - Usuario no consume refrescos: {alt_data.get('usuario_no_consume_refrescos', False)}")
    
    # Test error handling
    print("\n📋 TEST CASE 4: Error handling")
    response = requests.get(f"{API_URL}/recomendaciones-alternativas/invalid-session-id")
    if response.status_code == 404:
        print("✅ Correctly returns 404 for invalid session")
    else:
        print(f"❌ Expected 404, got {response.status_code}")
        return False
    
    print("\n✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("✅ The /api/recomendaciones-alternativas/{sesion_id} endpoint is working correctly")
    return True

if __name__ == "__main__":
    success = test_alternative_recommendations()
    exit(0 if success else 1)