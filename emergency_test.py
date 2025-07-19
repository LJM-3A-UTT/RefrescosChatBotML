#!/usr/bin/env python3
"""
Emergency Testing for Critical Errors
Testing the specific issues mentioned in the review request
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

def test_numpy_error():
    """Test for numpy encoding errors during system initialization"""
    print("\n🔍 TESTING: Numpy Encoding Error")
    
    try:
        # Test session creation (would trigger numpy errors)
        response = requests.post(f"{API_URL}/iniciar-sesion", timeout=30)
        if response.status_code == 200:
            print("✅ Session creation successful - no numpy encoding errors")
            return True
        else:
            print(f"❌ Session creation failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Numpy error test failed: {str(e)}")
        return False

def test_400_errors():
    """Test for 400 Bad Request errors in recommendation endpoints"""
    print("\n🔍 TESTING: 400 Bad Request Errors")
    
    try:
        # Create and complete a session
        session_id = create_complete_session()
        if not session_id:
            print("❌ Could not create session")
            return False
        
        # Test main recommendation endpoint
        print("📋 Testing /api/recomendacion endpoint...")
        response = requests.get(f"{API_URL}/recomendacion/{session_id}", timeout=30)
        
        if response.status_code == 400:
            print("❌ CRITICAL: /api/recomendacion returns 400 Bad Request")
            print(f"Error response: {response.text}")
            return False
        elif response.status_code == 200:
            print("✅ /api/recomendacion returns 200 OK")
        else:
            print(f"⚠️ /api/recomendacion returns {response.status_code}")
        
        # Test additional recommendations endpoint
        print("📋 Testing /api/recomendaciones-alternativas endpoint...")
        response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}", timeout=30)
        
        if response.status_code == 400:
            print("❌ CRITICAL: /api/recomendaciones-alternativas returns 400 Bad Request")
            print(f"Error response: {response.text}")
            return False
        elif response.status_code == 200:
            print("✅ /api/recomendaciones-alternativas returns 200 OK")
        else:
            print(f"⚠️ /api/recomendaciones-alternativas returns {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ 400 error test failed: {str(e)}")
        return False

def test_critical_cases():
    """Test the critical cases mentioned in the review request"""
    print("\n🔍 TESTING: Critical User Cases")
    
    critical_cases = [
        ("prioridad_sabor", "Should show ONLY refrescos (no error 400)"),
        ("prioridad_salud", "Should show ONLY alternativas (no error 400)"),
        ("no_consume_refrescos", "Should show ONLY alternativas (no error 400)")
    ]
    
    all_passed = True
    
    for case_value, expected in critical_cases:
        print(f"\n📋 Testing: {case_value}")
        print(f"   Expected: {expected}")
        
        try:
            session_id = create_session_with_specific_answer(case_value)
            if not session_id:
                print(f"❌ Could not create session for {case_value}")
                all_passed = False
                continue
            
            # Test recommendation endpoint
            response = requests.get(f"{API_URL}/recomendacion/{session_id}", timeout=30)
            
            if response.status_code == 400:
                print(f"❌ CRITICAL: {case_value} causes 400 Bad Request")
                print(f"   Error: {response.text}")
                all_passed = False
            elif response.status_code == 200:
                print(f"✅ {case_value} returns 200 OK (no 400 error)")
                
                # Analyze the response
                data = response.json()
                refrescos_count = len(data.get("refrescos_reales", []))
                alternativas_count = len(data.get("bebidas_alternativas", []))
                
                print(f"   Result: {refrescos_count} refrescos, {alternativas_count} alternativas")
                
                # Check if behavior matches expectation
                if case_value == "prioridad_sabor":
                    if refrescos_count > 0 and alternativas_count == 0:
                        print("✅ CORRECT: Only refrescos for prioridad_sabor")
                    else:
                        print("⚠️ BEHAVIOR: Mixed or unexpected result")
                elif case_value in ["prioridad_salud", "no_consume_refrescos"]:
                    if refrescos_count == 0 and alternativas_count > 0:
                        print("✅ CORRECT: Only alternativas for health-focused user")
                    else:
                        print("⚠️ BEHAVIOR: Mixed or unexpected result")
            else:
                print(f"⚠️ {case_value} returns {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing {case_value}: {str(e)}")
            all_passed = False
    
    return all_passed

def test_questions_json():
    """Test that the 6 new questions load correctly from JSON"""
    print("\n🔍 TESTING: Questions JSON Loading")
    
    try:
        # Create session and get initial question
        response = requests.post(f"{API_URL}/iniciar-sesion", timeout=30)
        response.raise_for_status()
        session_data = response.json()
        session_id = session_data["sesion_id"]
        
        # Get initial question
        response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}", timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if "pregunta" not in data:
            print("❌ Initial question not loaded")
            return False
        
        pregunta = data["pregunta"]
        print(f"✅ Initial question loaded: {pregunta.get('pregunta', '')[:60]}...")
        
        # Check if it's the expected new question about soda relationship
        if "relación" in pregunta.get("pregunta", "").lower() and "refrescos" in pregunta.get("pregunta", "").lower():
            print("✅ Question is about relationship with sodas (new structure)")
        else:
            print("⚠️ Question might not be the expected new structure")
        
        # Check for expected option values
        opciones = pregunta.get("opciones", [])
        valores = [opcion.get("valor", "") for opcion in opciones]
        
        expected_values = ["no_consume_refrescos", "prefiere_alternativas", "prioridad_salud", "prioridad_sabor"]
        found_expected = [val for val in expected_values if any(val in v for v in valores)]
        
        if len(found_expected) >= 2:
            print(f"✅ Found expected values: {found_expected}")
        else:
            print(f"⚠️ Few expected values found: {found_expected}")
        
        # Try to load all 6 questions
        questions_loaded = 1
        
        # Answer initial question
        selected_option = opciones[0] if opciones else None
        if selected_option:
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": pregunta["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": 3.0
            }, timeout=30)
            response.raise_for_status()
        
        # Get remaining questions
        for i in range(5):
            response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}", timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "finalizada" in data and data["finalizada"]:
                break
                
            if "pregunta" in data:
                questions_loaded += 1
                question = data["pregunta"]
                print(f"✅ Question {questions_loaded} loaded")
                
                # Answer the question
                opciones = question.get("opciones", [])
                if opciones:
                    selected_option = opciones[0]
                    response = requests.post(f"{API_URL}/responder/{session_id}", json={
                        "pregunta_id": question["id"],
                        "respuesta_id": selected_option["id"],
                        "respuesta_texto": selected_option["texto"],
                        "tiempo_respuesta": random.uniform(2.0, 8.0)
                    }, timeout=30)
                    response.raise_for_status()
        
        if questions_loaded == 6:
            print("✅ All 6 questions loaded successfully from JSON")
            return True
        else:
            print(f"⚠️ Only {questions_loaded} questions loaded (expected 6)")
            return False
            
    except Exception as e:
        print(f"❌ Questions JSON test failed: {str(e)}")
        return False

def create_complete_session():
    """Create a complete session by answering all questions"""
    try:
        # Create session
        response = requests.post(f"{API_URL}/iniciar-sesion", timeout=30)
        response.raise_for_status()
        session_data = response.json()
        session_id = session_data["sesion_id"]
        
        # Get and answer initial question
        response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}", timeout=30)
        response.raise_for_status()
        data = response.json()
        question = data["pregunta"]
        
        selected_option = question["opciones"][0]
        response = requests.post(f"{API_URL}/responder/{session_id}", json={
            "pregunta_id": question["id"],
            "respuesta_id": selected_option["id"],
            "respuesta_texto": selected_option["texto"],
            "tiempo_respuesta": 3.0
        }, timeout=30)
        response.raise_for_status()
        
        # Answer remaining questions
        for i in range(5):
            response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}", timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "finalizada" in data and data["finalizada"]:
                break
                
            question = data["pregunta"]
            selected_option = question["opciones"][len(question["opciones"]) // 2]
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": random.uniform(2.0, 8.0)
            }, timeout=30)
            response.raise_for_status()
        
        return session_id
        
    except Exception as e:
        print(f"Error creating complete session: {str(e)}")
        return None

def create_session_with_specific_answer(target_value):
    """Create a session with a specific answer value"""
    try:
        # Create session
        response = requests.post(f"{API_URL}/iniciar-sesion", timeout=30)
        response.raise_for_status()
        session_data = response.json()
        session_id = session_data["sesion_id"]
        
        # Get and answer initial question
        response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}", timeout=30)
        response.raise_for_status()
        data = response.json()
        question = data["pregunta"]
        
        # Try to find option with target value
        selected_option = None
        for option in question["opciones"]:
            if option.get("valor") == target_value or target_value in option.get("valor", ""):
                selected_option = option
                break
        
        if not selected_option:
            selected_option = question["opciones"][0]
        
        response = requests.post(f"{API_URL}/responder/{session_id}", json={
            "pregunta_id": question["id"],
            "respuesta_id": selected_option["id"],
            "respuesta_texto": selected_option["texto"],
            "tiempo_respuesta": 3.0
        }, timeout=30)
        response.raise_for_status()
        
        # Answer remaining questions, trying to match target value
        for i in range(5):
            response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}", timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "finalizada" in data and data["finalizada"]:
                break
                
            question = data["pregunta"]
            
            # Try to find option with target value
            selected_option = None
            for option in question["opciones"]:
                if option.get("valor") == target_value or target_value in option.get("valor", ""):
                    selected_option = option
                    break
            
            if not selected_option:
                selected_option = question["opciones"][len(question["opciones"]) // 2]
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": random.uniform(2.0, 8.0)
            }, timeout=30)
            response.raise_for_status()
        
        return session_id
        
    except Exception as e:
        print(f"Error creating session with answer '{target_value}': {str(e)}")
        return None

def main():
    """Run all emergency tests"""
    print("="*80)
    print("🚨 EMERGENCY TESTING - CRITICAL ERRORS VERIFICATION")
    print("="*80)
    
    results = {}
    
    # Test 1: Numpy encoding error
    results["Numpy Error"] = test_numpy_error()
    
    # Test 2: Questions JSON loading
    results["Questions JSON"] = test_questions_json()
    
    # Test 3: 400 Bad Request errors
    results["400 Errors"] = test_400_errors()
    
    # Test 4: Critical user cases
    results["Critical Cases"] = test_critical_cases()
    
    # Print summary
    print("\n" + "="*80)
    print("📊 EMERGENCY TEST RESULTS")
    print("="*80)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ALL EMERGENCY TESTS PASSED!")
        print("✅ System is working correctly")
    else:
        print("\n🚨 CRITICAL ISSUES DETECTED!")
        failed_tests = [name for name, result in results.items() if not result]
        print(f"❌ Failed tests: {', '.join(failed_tests)}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)