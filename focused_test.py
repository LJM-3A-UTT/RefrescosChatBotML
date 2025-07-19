#!/usr/bin/env python3
"""
Focused Test Script for RefrescoBot ML - Testing Recomendaciones Alternativas
This script tests the specific endpoints for alternative recommendations.
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

def setup_user_session(user_type):
    """Set up a user session with the specified profile"""
    session_id = create_session()
    print(f"Created session with ID: {session_id}")
    
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
    elif user_type == "regular":
        # Find "frecuentemente" or "diario" option
        option_index = len(question["opciones"]) - 1
        for i, opcion in enumerate(question["opciones"]):
            if "frecuentemente" in opcion["texto"].lower() or "diario" in opcion["texto"].lower():
                option_index = i
                break
    else:  # saludable
        # Find "ocasionalmente" option
        option_index = len(question["opciones"]) // 2
        for i, opcion in enumerate(question["opciones"]):
            if "ocasionalmente" in opcion["texto"].lower():
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
        if user_type == "no_consume":
            # For non-consumers, look for healthy options
            option_index = 0
            for i, opcion in enumerate(question["opciones"]):
                texto_lower = opcion["texto"].lower()
                if any(word in texto_lower for word in ["saludable", "natural", "activo", "importante"]):
                    option_index = i
                    break
        elif user_type == "regular":
            # For regular users, look for traditional options
            option_index = len(question["opciones"]) - 1
            for i, opcion in enumerate(question["opciones"]):
                texto_lower = opcion["texto"].lower()
                if any(word in texto_lower for word in ["dulce", "sedentario", "no_importante", "tradicional"]):
                    option_index = i
                    break
        else:  # saludable
            # For health-conscious users, look for healthy options
            option_index = 0
            for i, opcion in enumerate(question["opciones"]):
                texto_lower = opcion["texto"].lower()
                if any(word in texto_lower for word in ["saludable", "natural", "activo", "importante"]):
                    option_index = i
                    break
        
        # Answer question
        answer_question(session_id, question, option_index)
    
    print(f"Completed all questions for {user_type} user")
    return session_id

def test_recomendaciones_alternativas():
    """Test the /api/recomendaciones-alternativas/{sesion_id} endpoint"""
    print("\n🔍 Testing /api/recomendaciones-alternativas Endpoint...")
    
    # Test for user who doesn't consume refrescos
    print("\nTesting for user who doesn't consume refrescos:")
    session_id = setup_user_session("no_consume")
    
    # Get initial recommendations
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
    
    # Test for regular user
    print("\nTesting for regular user:")
    session_id = create_session()
    print(f"Created session with ID: {session_id}")
    
    # Get initial question
    response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
    response.raise_for_status()
    question = response.json()["pregunta"]
    
    # Find "frecuentemente" or "diario" option
    option_index = len(question["opciones"]) - 1
    for i, opcion in enumerate(question["opciones"]):
        if "frecuentemente" in opcion["texto"].lower() or "diario" in opcion["texto"].lower() or "varias veces" in opcion["texto"].lower():
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
        
        # Look for traditional options
        option_index = len(question["opciones"]) - 1
        for i, opcion in enumerate(question["opciones"]):
            texto_lower = opcion["texto"].lower()
            if any(word in texto_lower for word in ["dulce", "sedentario", "no_importante", "tradicional"]):
                option_index = i
                break
        
        # Answer question
        answer_question(session_id, question, option_index)
    
    print("Completed all questions for regular user")
    
    # Get initial recommendations
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
    
    # Check mostrar_alternativas value
    if "mostrar_alternativas" in data:
        print(f"ℹ️ mostrar_alternativas: {data['mostrar_alternativas']}")
    
    # Test recomendaciones-alternativas endpoint
    response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
    response.raise_for_status()
    data = response.json()
    
    # Print tipo_recomendaciones value
    print(f"ℹ️ tipo_recomendaciones: {data.get('tipo_recomendaciones', 'missing')}")
    
    # Check if recommendations match tipo_recomendaciones
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
    
    # Test for health-conscious user
    print("\nTesting for health-conscious user:")
    session_id = create_session()
    print(f"Created session with ID: {session_id}")
    
    # Get initial question
    response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
    response.raise_for_status()
    question = response.json()["pregunta"]
    
    # Find "ocasionalmente" option
    option_index = len(question["opciones"]) // 2
    for i, opcion in enumerate(question["opciones"]):
        if "ocasionalmente" in opcion["texto"].lower() or "una vez" in opcion["texto"].lower():
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
        
        # Look for health-conscious options
        option_index = 0
        for i, opcion in enumerate(question["opciones"]):
            texto_lower = opcion["texto"].lower()
            if any(word in texto_lower for word in ["saludable", "natural", "activo", "importante"]):
                option_index = i
                break
        
        # Answer question
        answer_question(session_id, question, option_index)
    
    print("Completed all questions for health-conscious user")
    
    # Get initial recommendations
    response = requests.get(f"{API_URL}/recomendacion/{session_id}")
    response.raise_for_status()
    data = response.json()
    
    # Check if usuario_no_consume_refrescos is false
    if "usuario_no_consume_refrescos" in data and not data["usuario_no_consume_refrescos"]:
        print("✅ usuario_no_consume_refrescos correctly detected as false")
    else:
        print("❌ usuario_no_consume_refrescos should be false or is missing")
    
    # Check if bebidas_alternativas are shown
    if "bebidas_alternativas" in data and len(data["bebidas_alternativas"]) > 0:
        print(f"✅ {len(data['bebidas_alternativas'])} bebidas_alternativas shown")
    else:
        print("❌ bebidas_alternativas should not be empty")
    
    # Check mostrar_alternativas value
    if "mostrar_alternativas" in data:
        print(f"ℹ️ mostrar_alternativas: {data['mostrar_alternativas']}")
    
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
            print("❌ Found real refrescos in recomendaciones_adicionales")

def test_mas_refrescos():
    """Test the /api/mas-refrescos/{sesion_id} endpoint"""
    print("\n🔍 Testing /api/mas-refrescos Endpoint...")
    
    # Create session for regular user
    session_id = create_session()
    print(f"Created session with ID: {session_id}")
    
    # Get initial question
    response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
    response.raise_for_status()
    question = response.json()["pregunta"]
    
    # Find "frecuentemente" or "diario" option
    option_index = len(question["opciones"]) - 1
    for i, opcion in enumerate(question["opciones"]):
        if "frecuentemente" in opcion["texto"].lower() or "diario" in opcion["texto"].lower() or "varias veces" in opcion["texto"].lower():
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
        
        # Look for traditional options
        option_index = len(question["opciones"]) - 1
        for i, opcion in enumerate(question["opciones"]):
            texto_lower = opcion["texto"].lower()
            if any(word in texto_lower for word in ["dulce", "sedentario", "no_importante", "tradicional"]):
                option_index = i
                break
        
        # Answer question
        answer_question(session_id, question, option_index)
    
    print("Completed all questions for regular user")
    
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

def test_mas_alternativas():
    """Test the /api/mas-alternativas/{sesion_id} endpoint"""
    print("\n🔍 Testing /api/mas-alternativas Endpoint...")
    
    # Create session for health-conscious user
    session_id = create_session()
    print(f"Created session with ID: {session_id}")
    
    # Get initial question
    response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
    response.raise_for_status()
    question = response.json()["pregunta"]
    
    # Find "ocasionalmente" option
    option_index = len(question["opciones"]) // 2
    for i, opcion in enumerate(question["opciones"]):
        if "ocasionalmente" in opcion["texto"].lower() or "una vez" in opcion["texto"].lower():
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
        
        # Look for health-conscious options
        option_index = 0
        for i, opcion in enumerate(question["opciones"]):
            texto_lower = opcion["texto"].lower()
            if any(word in texto_lower for word in ["saludable", "natural", "activo", "importante"]):
                option_index = i
                break
        
        # Answer question
        answer_question(session_id, question, option_index)
    
    print("Completed all questions for health-conscious user")
    
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

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("🤖 REFRESCOBOT ML RECOMENDACIONES ALTERNATIVAS TEST SUITE")
    print("="*80)
    
    test_recomendaciones_alternativas()
    test_mas_refrescos()
    test_mas_alternativas()
    
    print("\n" + "="*80)
    print("🎉 TESTS COMPLETED")
    print("="*80)

if __name__ == "__main__":
    run_all_tests()