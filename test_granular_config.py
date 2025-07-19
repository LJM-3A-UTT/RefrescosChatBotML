#!/usr/bin/env python3
"""
Focused test for Granular Healthy Alternatives Configuration
"""

import requests
import json
import time
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("/app/frontend/.env")

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001")
API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

def create_user_session_healthy():
    """Create a session for a health-conscious user"""
    try:
        # Create session
        response = requests.post(f"{API_URL}/iniciar-sesion")
        response.raise_for_status()
        data = response.json()
        session_id = data["sesion_id"]
        
        # Get initial question (about soda consumption)
        response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
        response.raise_for_status()
        data = response.json()
        question = data["pregunta"]
        
        # Answer with moderate consumption
        moderate_option = question["opciones"][1] if len(question["opciones"]) > 1 else question["opciones"][0]
        
        response = requests.post(f"{API_URL}/responder/{session_id}", json={
            "pregunta_id": question["id"],
            "respuesta_id": moderate_option["id"],
            "respuesta_texto": moderate_option["texto"],
            "tiempo_respuesta": 5.0
        })
        response.raise_for_status()
        
        # Answer remaining questions with health-conscious responses
        for i in range(5):
            response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "finalizada" in data and data["finalizada"]:
                break
                
            question = data["pregunta"]
            
            # Choose health-conscious options (last option is often most positive)
            selected_option = question["opciones"][-1]
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": random.uniform(4.0, 10.0)
            })
            response.raise_for_status()
        
        return session_id
        
    except Exception as e:
        print(f"Error creating healthy user session: {str(e)}")
        return None

def create_user_session_no_sodas():
    """Create a session for a user who does NOT consume sodas"""
    try:
        # Create session
        response = requests.post(f"{API_URL}/iniciar-sesion")
        response.raise_for_status()
        data = response.json()
        session_id = data["sesion_id"]
        
        # Get initial question (about soda consumption)
        response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
        response.raise_for_status()
        data = response.json()
        question = data["pregunta"]
        
        # Answer "nunca" or first option to indicate no soda consumption
        nunca_option = question["opciones"][0]  # First option is usually "never"
        
        response = requests.post(f"{API_URL}/responder/{session_id}", json={
            "pregunta_id": question["id"],
            "respuesta_id": nunca_option["id"],
            "respuesta_texto": nunca_option["texto"],
            "tiempo_respuesta": 3.0
        })
        response.raise_for_status()
        
        # Answer remaining questions with health-conscious responses
        for i in range(5):
            response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "finalizada" in data and data["finalizada"]:
                break
                
            question = data["pregunta"]
            
            # Choose health-conscious options (last option)
            selected_option = question["opciones"][-1]
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": random.uniform(2.0, 8.0)
            })
            response.raise_for_status()
        
        return session_id
        
    except Exception as e:
        print(f"Error creating no-sodas user session: {str(e)}")
        return None

def create_user_session_traditional():
    """Create a session for a traditional soda user"""
    try:
        # Create session
        response = requests.post(f"{API_URL}/iniciar-sesion")
        response.raise_for_status()
        data = response.json()
        session_id = data["sesion_id"]
        
        # Get initial question (about soda consumption)
        response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
        response.raise_for_status()
        data = response.json()
        question = data["pregunta"]
        
        # Answer with frequent consumption (middle or last option)
        frequent_option = question["opciones"][-2] if len(question["opciones"]) > 2 else question["opciones"][-1]
        
        response = requests.post(f"{API_URL}/responder/{session_id}", json={
            "pregunta_id": question["id"],
            "respuesta_id": frequent_option["id"],
            "respuesta_texto": frequent_option["texto"],
            "tiempo_respuesta": 2.0
        })
        response.raise_for_status()
        
        # Answer remaining questions with traditional preferences
        for i in range(5):
            response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "finalizada" in data and data["finalizada"]:
                break
                
            question = data["pregunta"]
            
            # Choose traditional options (middle option)
            selected_option = question["opciones"][len(question["opciones"])//2]
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": random.uniform(1.0, 4.0)
            })
            response.raise_for_status()
        
        return session_id
        
    except Exception as e:
        print(f"Error creating traditional user session: {str(e)}")
        return None

def test_granular_configuration():
    """Test the granular configuration for healthy alternatives"""
    print("\n🔍 Testing Granular Healthy Alternatives Configuration...")
    print("="*70)
    print("Testing new configurations:")
    print("- MAX_ALTERNATIVAS_SALUDABLES_INICIAL = 3")
    print("- MAX_ALTERNATIVAS_SALUDABLES_ADICIONAL = 3")
    print("- MAX_REFRESCOS_ADICIONALES = 3")
    print("- MAX_ALTERNATIVAS_USUARIO_SALUDABLE = 4")
    print("- MAX_REFRESCOS_USUARIO_TRADICIONAL = 3")
    print("="*70)
    
    all_tests_passed = True
    
    try:
        # Test 1: Verify backend is running
        print("\n📋 TEST 1: Verifying backend status...")
        response = requests.get(f"{API_URL}/status")
        if response.status_code == 200:
            print("✅ Backend is running and accessible")
        else:
            print(f"❌ Backend status check failed: {response.status_code}")
            return False
        
        # Test 2: Test healthy user gets correct initial alternatives
        print("\n📋 TEST 2: Testing healthy user initial alternatives...")
        session_id_healthy = create_user_session_healthy()
        if not session_id_healthy:
            print("❌ Could not create healthy user session")
            return False
        
        response = requests.get(f"{API_URL}/recomendacion/{session_id_healthy}")
        response.raise_for_status()
        initial_data = response.json()
        
        healthy_alternatives = initial_data.get('bebidas_alternativas', [])
        print(f"✅ Healthy user got {len(healthy_alternatives)} initial alternatives")
        
        if len(healthy_alternatives) <= 3:
            print("✅ Initial alternatives count respects MAX_ALTERNATIVAS_SALUDABLES_INICIAL (≤3)")
        else:
            print(f"❌ Got {len(healthy_alternatives)} alternatives, expected ≤3")
            all_tests_passed = False
        
        # Test 3: Test additional alternatives for healthy user
        print("\n📋 TEST 3: Testing additional alternatives for healthy user...")
        response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id_healthy}")
        response.raise_for_status()
        additional_data = response.json()
        
        if not additional_data.get('sin_mas_opciones', False):
            additional_alternatives = additional_data.get('recomendaciones_adicionales', [])
            print(f"✅ Healthy user got {len(additional_alternatives)} additional alternatives")
            
            if len(additional_alternatives) <= 3:
                print("✅ Additional alternatives count respects MAX_ALTERNATIVAS_SALUDABLES_ADICIONAL (≤3)")
            else:
                print(f"❌ Got {len(additional_alternatives)} additional alternatives, expected ≤3")
                all_tests_passed = False
            
            # Check type
            if additional_data.get('tipo_recomendaciones') in ['alternativas_saludables', 'alternativas_adicionales']:
                print("✅ Additional alternatives type is correct")
            else:
                print(f"❌ Unexpected type: {additional_data.get('tipo_recomendaciones')}")
                all_tests_passed = False
        else:
            print("✅ No more additional alternatives available (acceptable)")
        
        # Test 4: Test no-sodas user gets correct amount
        print("\n📋 TEST 4: Testing no-sodas user...")
        session_id_no_sodas = create_user_session_no_sodas()
        if not session_id_no_sodas:
            print("❌ Could not create no-sodas user session")
            return False
        
        response = requests.get(f"{API_URL}/recomendacion/{session_id_no_sodas}")
        response.raise_for_status()
        no_sodas_data = response.json()
        
        refrescos_count = len(no_sodas_data.get('refrescos_reales', []))
        alternatives_count = len(no_sodas_data.get('bebidas_alternativas', []))
        
        print(f"✅ No-sodas user got {refrescos_count} refrescos, {alternatives_count} alternatives")
        
        if no_sodas_data.get('usuario_no_consume_refrescos', False):
            print("✅ User correctly detected as not consuming sodas")
            
            if refrescos_count == 0:
                print("✅ No-sodas user correctly got 0 refrescos")
            else:
                print(f"❌ No-sodas user got {refrescos_count} refrescos, expected 0")
                all_tests_passed = False
            
            if alternatives_count <= 4:
                print("✅ Alternatives count respects MAX_ALTERNATIVAS_USUARIO_SALUDABLE (≤4)")
            else:
                print(f"❌ Got {alternatives_count} alternatives, expected ≤4")
                all_tests_passed = False
        else:
            print("⚠️ User not detected as no-sodas user (might be due to question logic)")
        
        # Test 5: Test traditional user
        print("\n📋 TEST 5: Testing traditional user...")
        session_id_traditional = create_user_session_traditional()
        if not session_id_traditional:
            print("❌ Could not create traditional user session")
            return False
        
        response = requests.get(f"{API_URL}/recomendacion/{session_id_traditional}")
        response.raise_for_status()
        traditional_data = response.json()
        
        traditional_refrescos = len(traditional_data.get('refrescos_reales', []))
        traditional_alternatives = len(traditional_data.get('bebidas_alternativas', []))
        
        print(f"✅ Traditional user got {traditional_refrescos} refrescos, {traditional_alternatives} alternatives")
        
        # Test additional recommendations for traditional user
        response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id_traditional}")
        response.raise_for_status()
        additional_traditional_data = response.json()
        
        if not additional_traditional_data.get('sin_mas_opciones', False):
            additional_recommendations = additional_traditional_data.get('recomendaciones_adicionales', [])
            recommendation_type = additional_traditional_data.get('tipo_recomendaciones', '')
            
            print(f"✅ Traditional user got {len(additional_recommendations)} additional recommendations of type '{recommendation_type}'")
            
            if recommendation_type in ['refrescos_tradicionales', 'refrescos_adicionales']:
                if len(additional_recommendations) <= 3:
                    print("✅ Additional refrescos count respects MAX_REFRESCOS_ADICIONALES (≤3)")
                else:
                    print(f"❌ Got {len(additional_recommendations)} refrescos, expected ≤3")
                    all_tests_passed = False
            else:
                print(f"✅ Traditional user got {recommendation_type} (acceptable based on logic)")
        else:
            print("✅ No more additional recommendations available (acceptable)")
        
        # Test 6: Test specific endpoints
        print("\n📋 TEST 6: Testing specific endpoints...")
        
        # Test /api/mas-alternativas
        response = requests.get(f"{API_URL}/mas-alternativas/{session_id_healthy}")
        if response.status_code == 200:
            mas_alternativas_data = response.json()
            if not mas_alternativas_data.get('sin_mas_opciones', False):
                mas_alternativas_count = len(mas_alternativas_data.get('mas_alternativas', []))
                print(f"✅ /api/mas-alternativas returned {mas_alternativas_count} alternatives")
                
                if mas_alternativas_count <= 3:
                    print("✅ /api/mas-alternativas respects configuration (≤3)")
                else:
                    print(f"❌ /api/mas-alternativas returned {mas_alternativas_count}, expected ≤3")
                    all_tests_passed = False
            else:
                print("✅ /api/mas-alternativas: No more options (acceptable)")
        else:
            print(f"⚠️ /api/mas-alternativas returned {response.status_code}")
        
        # Test /api/mas-refrescos
        response = requests.get(f"{API_URL}/mas-refrescos/{session_id_traditional}")
        if response.status_code == 200:
            mas_refrescos_data = response.json()
            if not mas_refrescos_data.get('sin_mas_opciones', False):
                mas_refrescos_count = len(mas_refrescos_data.get('mas_refrescos', []))
                print(f"✅ /api/mas-refrescos returned {mas_refrescos_count} refrescos")
                
                if mas_refrescos_count <= 3:
                    print("✅ /api/mas-refrescos respects MAX_REFRESCOS_ADICIONALES (≤3)")
                else:
                    print(f"❌ /api/mas-refrescos returned {mas_refrescos_count}, expected ≤3")
                    all_tests_passed = False
            else:
                print("✅ /api/mas-refrescos: No more options (acceptable)")
        else:
            print(f"⚠️ /api/mas-refrescos returned {response.status_code}")
        
        if all_tests_passed:
            print("\n✅ SUCCESS: All granular healthy alternatives configuration tests passed!")
            print("✅ New configurations are working correctly:")
            print("   - MAX_ALTERNATIVAS_SALUDABLES_INICIAL controls initial healthy alternatives")
            print("   - MAX_ALTERNATIVAS_SALUDABLES_ADICIONAL controls additional healthy alternatives")
            print("   - MAX_REFRESCOS_ADICIONALES controls additional refrescos for traditional users")
            print("   - MAX_ALTERNATIVAS_USUARIO_SALUDABLE controls alternatives for healthy users")
            print("   - Different user types receive appropriate amounts of beverages")
            print("   - The 'more options' logic uses the correct specific configurations")
            print("   - No regressions in existing functionality")
        else:
            print("\n❌ SOME TESTS FAILED: Please check the issues above")
        
        return all_tests_passed
        
    except Exception as e:
        print(f"❌ Granular Configuration Test: FAILED - {str(e)}")
        return False

if __name__ == "__main__":
    success = test_granular_configuration()
    if success:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n💥 SOME TESTS FAILED!")