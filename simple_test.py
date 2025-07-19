#!/usr/bin/env python3
"""
Simple Test Script for RefrescoBot ML - Testing Recomendaciones Alternativas
This script tests the specific corrections implemented for the alternative recommendations endpoints.
"""

import requests
import json
import time
import random
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv("/app/frontend/.env")

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001")
API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

def create_session():
    """Create a new session"""
    response = requests.post(f"{API_URL}/iniciar-sesion")
    response.raise_for_status()
    data = response.json()
    return data["sesion_id"]

def answer_question(session_id, question, option_index=0):
    """Answer a question with the specified option index"""
    response = requests.post(f"{API_URL}/responder/{session_id}", json={
        "pregunta_id": question["id"],
        "respuesta_id": question["opciones"][option_index]["id"],
        "respuesta_texto": question["opciones"][option_index]["texto"],
        "tiempo_respuesta": random.uniform(2.0, 10.0)
    })
    response.raise_for_status()
    return response.json()

def complete_questions(session_id, user_type="regular"):
    """Complete all questions for a session"""
    # Get initial question
    response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
    response.raise_for_status()
    question = response.json()["pregunta"]
    
    # Answer initial question based on user type
    if user_type == "no_consume":
        # Find "nunca" or "casi nunca" option
        option_index = 0
        for i, opcion in enumerate(question["opciones"]):
            if "nunca" in opcion["texto"].lower():
                option_index = i
                break
    elif user_type == "saludable":
        # Find "ocasionalmente" option
        option_index = len(question["opciones"]) // 2
        for i, opcion in enumerate(question["opciones"]):
            if "ocasionalmente" in opcion["texto"].lower():
                option_index = i
                break
    else:  # regular
        # Find "frecuentemente" or "diario" option
        option_index = len(question["opciones"]) - 1
        for i, opcion in enumerate(question["opciones"]):
            if "frecuentemente" in opcion["texto"].lower() or "diario" in opcion["texto"].lower():
                option_index = i
                break
    
    # Answer initial question
    answer_question(session_id, question, option_index)
    print(f"Answered initial question with option: {question['opciones'][option_index]['texto']}")
    
    # Answer remaining questions
    for i in range(5):  # 5 more questions
        response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
        response.raise_for_status()
        data = response.json()
        
        if "finalizada" in data and data["finalizada"]:
            break
        
        if "pregunta" not in data:
            break
        
        question = data["pregunta"]
        
        # Answer based on user type
        if user_type == "no_consume" or user_type == "saludable":
            # For health-conscious users, look for healthy options
            option_index = 0
            for i, opcion in enumerate(question["opciones"]):
                texto_lower = opcion["texto"].lower()
                if any(word in texto_lower for word in ["saludable", "natural", "activo", "importante", "poco_dulce"]):
                    option_index = i
                    break
        else:  # regular
            # For regular users, look for traditional options
            option_index = len(question["opciones"]) - 1
            for i, opcion in enumerate(question["opciones"]):
                texto_lower = opcion["texto"].lower()
                if any(word in texto_lower for word in ["dulce", "sedentario", "no_importante", "tradicional"]):
                    option_index = i
                    break
        
        # Answer question
        answer_question(session_id, question, option_index)
        print(f"Answered question {i+2} with option: {question['opciones'][option_index]['texto']}")

def test_usuario_no_consume_refrescos():
    """Test recommendations for users who don't consume refrescos"""
    print("\n🔍 Testing Usuario que NO consume refrescos...")
    
    # Create session
    session_id = create_session()
    print(f"Created session with ID: {session_id}")
    
    # Complete questions as user who doesn't consume refrescos
    complete_questions(session_id, user_type="no_consume")
    print("Completed all questions")
    
    # Get recommendations
    response = requests.get(f"{API_URL}/recomendacion/{session_id}")
    response.raise_for_status()
    data = response.json()
    
    # Check if usuario_no_consume_refrescos is true
    if "usuario_no_consume_refrescos" in data and data["usuario_no_consume_refrescos"]:
        print("✅ usuario_no_consume_refrescos correctly detected as true")
    else:
        print("❌ usuario_no_consume_refrescos not true or missing")
    
    # Check if only alternatives are shown
    if "refrescos_reales" in data and len(data["refrescos_reales"]) > 0:
        print("❌ refrescos_reales should be empty")
    else:
        print("✅ refrescos_reales correctly empty")
    
    if "bebidas_alternativas" in data and len(data["bebidas_alternativas"]) > 0:
        print(f"✅ {len(data['bebidas_alternativas'])} alternatives shown")
    else:
        print("❌ bebidas_alternativas should not be empty")
    
    # Test recomendaciones-alternativas endpoint
    response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
    response.raise_for_status()
    data = response.json()
    
    # Check if tipo_recomendaciones is alternativas_saludables
    if "tipo_recomendaciones" in data and data["tipo_recomendaciones"] == "alternativas_saludables":
        print("✅ tipo_recomendaciones correctly set to alternativas_saludables")
    else:
        print(f"❌ tipo_recomendaciones should be alternativas_saludables, got {data.get('tipo_recomendaciones', 'missing')}")
    
    # Check if all recommendations are alternatives (es_refresco_real = false)
    if "recomendaciones_adicionales" in data and len(data["recomendaciones_adicionales"]) > 0:
        all_alternatives = True
        for bebida in data["recomendaciones_adicionales"]:
            if bebida.get("es_refresco_real", True):
                all_alternatives = False
                break
        
        if all_alternatives:
            print("✅ All additional recommendations are alternatives")
        else:
            print("❌ Found a real refresco in recomendaciones_adicionales")
    else:
        print("ℹ️ No additional recommendations available")

def test_usuario_regular_tradicional():
    """Test recommendations for regular traditional users"""
    print("\n🔍 Testing Usuario Regular Tradicional...")
    
    # Create session
    session_id = create_session()
    print(f"Created session with ID: {session_id}")
    
    # Complete questions as regular user
    complete_questions(session_id, user_type="regular")
    print("Completed all questions")
    
    # Get recommendations
    response = requests.get(f"{API_URL}/recomendacion/{session_id}")
    response.raise_for_status()
    data = response.json()
    
    # Check if usuario_no_consume_refrescos is false
    if "usuario_no_consume_refrescos" in data and not data["usuario_no_consume_refrescos"]:
        print("✅ usuario_no_consume_refrescos correctly detected as false")
    else:
        print("❌ usuario_no_consume_refrescos should be false or is missing")
    
    # Check if refrescos_reales are shown
    if "refrescos_reales" in data and len(data["refrescos_reales"]) > 0:
        print(f"✅ {len(data['refrescos_reales'])} refrescos_reales shown")
    else:
        print("❌ refrescos_reales should not be empty")
    
    # Test recomendaciones-alternativas endpoint
    response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
    response.raise_for_status()
    data = response.json()
    
    # Print mostrar_alternativas value
    print(f"ℹ️ mostrar_alternativas: {data.get('mostrar_alternativas', 'missing')}")
    
    # Print tipo_recomendaciones value
    print(f"ℹ️ tipo_recomendaciones: {data.get('tipo_recomendaciones', 'missing')}")
    
    # Check if recommendations are consistent with tipo_recomendaciones
    if "recomendaciones_adicionales" in data and len(data["recomendaciones_adicionales"]) > 0:
        tipo = data.get("tipo_recomendaciones", "")
        
        if tipo == "refrescos_tradicionales":
            # Check if all are real refrescos
            all_refrescos = True
            for bebida in data["recomendaciones_adicionales"]:
                if not bebida.get("es_refresco_real", False):
                    all_refrescos = False
                    break
            
            if all_refrescos:
                print("✅ All additional recommendations are real refrescos")
            else:
                print("❌ Found alternatives in recomendaciones_adicionales")
        
        elif tipo == "alternativas_saludables":
            # Check if all are alternatives
            all_alternatives = True
            for bebida in data["recomendaciones_adicionales"]:
                if bebida.get("es_refresco_real", True):
                    all_alternatives = False
                    break
            
            if all_alternatives:
                print("✅ All additional recommendations are alternatives")
            else:
                print("❌ Found real refrescos in recomendaciones_adicionales")
    else:
        print("ℹ️ No additional recommendations available")

def test_mas_refrescos_endpoint():
    """Test the /api/mas-refrescos/{sesion_id} endpoint"""
    print("\n🔍 Testing /api/mas-refrescos Endpoint...")
    
    # Create session
    session_id = create_session()
    print(f"Created session with ID: {session_id}")
    
    # Complete questions as regular user
    complete_questions(session_id, user_type="regular")
    print("Completed all questions")
    
    # Test mas-refrescos endpoint
    response = requests.get(f"{API_URL}/mas-refrescos/{session_id}")
    response.raise_for_status()
    data = response.json()
    
    # Check for required fields
    if "mas_refrescos" in data:
        print(f"✅ Got {len(data['mas_refrescos'])} additional refrescos")
    else:
        print("❌ Missing mas_refrescos field")
    
    # Check if all recommendations are real refrescos (es_refresco_real = true)
    if "mas_refrescos" in data and len(data["mas_refrescos"]) > 0:
        all_refrescos = True
        for bebida in data["mas_refrescos"]:
            if not bebida.get("es_refresco_real", False):
                all_refrescos = False
                break
        
        if all_refrescos:
            print("✅ All recommendations are real refrescos")
        else:
            print("❌ Found alternatives in mas_refrescos")
    
    # Check for tipo field
    if "tipo" in data and data["tipo"] == "refrescos_tradicionales":
        print("✅ tipo correctly set to refrescos_tradicionales")
    else:
        print(f"❌ tipo should be refrescos_tradicionales, got {data.get('tipo', 'missing')}")

def test_mas_alternativas_endpoint():
    """Test the /api/mas-alternativas/{sesion_id} endpoint"""
    print("\n🔍 Testing /api/mas-alternativas Endpoint...")
    
    # Create session
    session_id = create_session()
    print(f"Created session with ID: {session_id}")
    
    # Complete questions as health-conscious user
    complete_questions(session_id, user_type="saludable")
    print("Completed all questions")
    
    # Test mas-alternativas endpoint
    response = requests.get(f"{API_URL}/mas-alternativas/{session_id}")
    response.raise_for_status()
    data = response.json()
    
    # Check for required fields
    if "mas_alternativas" in data:
        print(f"✅ Got {len(data['mas_alternativas'])} additional alternatives")
    else:
        print("❌ Missing mas_alternativas field")
    
    # Check if all recommendations are alternatives (es_refresco_real = false)
    if "mas_alternativas" in data and len(data["mas_alternativas"]) > 0:
        all_alternatives = True
        for bebida in data["mas_alternativas"]:
            if bebida.get("es_refresco_real", True):
                all_alternatives = False
                break
        
        if all_alternatives:
            print("✅ All recommendations are alternatives")
        else:
            print("❌ Found real refrescos in mas_alternativas")
    
    # Check for tipo field
    if "tipo" in data and data["tipo"] == "alternativas_saludables":
        print("✅ tipo correctly set to alternativas_saludables")
    else:
        print(f"❌ tipo should be alternativas_saludables, got {data.get('tipo', 'missing')}")

def test_campos_respuesta():
    """Test response fields in the recommendations"""
    print("\n🔍 Testing Campos de Respuesta...")
    
    # Create session
    session_id = create_session()
    print(f"Created session with ID: {session_id}")
    
    # Complete questions
    complete_questions(session_id)
    print("Completed all questions")
    
    # Test recomendaciones-alternativas endpoint
    response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
    response.raise_for_status()
    data = response.json()
    
    # Check for required fields
    required_fields = ["tipo_recomendaciones", "usuario_no_consume_refrescos", "mostrar_alternativas", "estadisticas"]
    missing_fields = [field for field in required_fields if field not in data]
    
    if not missing_fields:
        print("✅ All required fields present")
    else:
        print(f"❌ Missing fields: {missing_fields}")
    
    # Check estadisticas field
    if "estadisticas" in data:
        estadisticas = data["estadisticas"]
        required_stats = ["refrescos_disponibles", "alternativas_disponibles", "total_recomendadas"]
        missing_stats = [stat for stat in required_stats if stat not in estadisticas]
        
        if not missing_stats:
            print("✅ All required statistics present")
            print(f"✅ refrescos_disponibles: {estadisticas['refrescos_disponibles']}")
            print(f"✅ alternativas_disponibles: {estadisticas['alternativas_disponibles']}")
            print(f"✅ total_recomendadas: {estadisticas['total_recomendadas']}")
        else:
            print(f"❌ Missing statistics: {missing_stats}")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("🤖 REFRESCOBOT ML RECOMENDACIONES ALTERNATIVAS TEST SUITE")
    print("="*80)
    
    test_usuario_no_consume_refrescos()
    test_usuario_regular_tradicional()
    test_mas_refrescos_endpoint()
    test_mas_alternativas_endpoint()
    test_campos_respuesta()
    
    print("\n" + "="*80)
    print("🎉 TESTS COMPLETED")
    print("="*80)

if __name__ == "__main__":
    run_all_tests()