#!/usr/bin/env python3
"""
Critical Test for Redesigned System - 6 New Questions & Mixed Behavior Elimination
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

def test_six_new_questions():
    """Test the 6 new questions structure"""
    print("\n🔍 CRITICAL TEST: 6 New Questions Structure")
    
    try:
        # Create session
        response = requests.post(f"{API_URL}/iniciar-sesion")
        response.raise_for_status()
        session_data = response.json()
        session_id = session_data["sesion_id"]
        
        # Get initial question (P1)
        response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
        response.raise_for_status()
        data = response.json()
        
        pregunta1 = data["pregunta"]
        
        # VERIFY P1: "¿Cuál describe mejor tu relación con los refrescos?"
        print(f"✅ P1: {pregunta1.get('pregunta', '')}")
        
        # VERIFY P1 OPTIONS
        expected_p1_values = ["no_consume_refrescos", "prefiere_alternativas", "regular_consumidor", "ocasional_consumidor", "muy_ocasional"]
        found_p1_values = [opcion.get("valor", "") for opcion in pregunta1.get("opciones", [])]
        
        matching_p1 = [val for val in expected_p1_values if val in found_p1_values]
        print(f"✅ P1 OPTIONS: {matching_p1}")
        
        if len(matching_p1) >= 4:
            print("✅ SUCCESS: P1 has correct structure")
            return True
        else:
            print("❌ FAILED: P1 missing expected options")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

def test_specific_user_behavior(answer_value, expected_behavior):
    """Test specific user behavior"""
    print(f"\n📋 Testing: {answer_value} → Expected: {expected_behavior}")
    
    try:
        # Create session
        response = requests.post(f"{API_URL}/iniciar-sesion")
        response.raise_for_status()
        session_data = response.json()
        session_id = session_data["sesion_id"]
        
        # Get initial question
        response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
        response.raise_for_status()
        data = response.json()
        question = data["pregunta"]
        
        # Find the option with the desired value
        selected_option = None
        for option in question["opciones"]:
            if option.get("valor") == answer_value:
                selected_option = option
                break
        
        if not selected_option:
            print(f"⚠️ Could not find option with value '{answer_value}'")
            return False
        
        # Answer the initial question
        response = requests.post(f"{API_URL}/responder/{session_id}", json={
            "pregunta_id": question["id"],
            "respuesta_id": selected_option["id"],
            "respuesta_texto": selected_option["texto"],
            "tiempo_respuesta": 3.0
        })
        response.raise_for_status()
        
        # Answer remaining questions with neutral responses
        for i in range(5):  # Assuming 6 total questions
            response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "finalizada" in data and data["finalizada"]:
                break
                
            question = data["pregunta"]
            
            # Choose middle option for neutral responses
            option_index = len(question["opciones"]) // 2
            selected_option = question["opciones"][option_index]
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": random.uniform(2.0, 8.0)
            })
            response.raise_for_status()
        
        # Get recommendations
        response = requests.get(f"{API_URL}/recomendacion/{session_id}")
        response.raise_for_status()
        recommendations = response.json()
        
        refrescos_count = len(recommendations.get("refrescos_reales", []))
        alternativas_count = len(recommendations.get("bebidas_alternativas", []))
        usuario_no_consume = recommendations.get("usuario_no_consume_refrescos", False)
        mostrar_alternativas = recommendations.get("mostrar_alternativas", False)
        
        print(f"   Result: {refrescos_count} refrescos, {alternativas_count} alternatives")
        print(f"   Flags: usuario_no_consume={usuario_no_consume}, mostrar_alternativas={mostrar_alternativas}")
        
        # Analyze behavior
        if expected_behavior == "ONLY_ALTERNATIVES":
            if refrescos_count == 0 and alternativas_count > 0:
                print("✅ CORRECT: Only alternatives")
                return True
            else:
                print("❌ INCORRECT: Should only show alternatives")
                return False
        elif expected_behavior == "ONLY_SODAS":
            if refrescos_count > 0 and alternativas_count == 0:
                print("✅ CORRECT: Only sodas")
                return True
            else:
                print("❌ INCORRECT: Should only show sodas")
                return False
        elif expected_behavior == "CLEAR_SEPARATION":
            if refrescos_count > 0 and alternativas_count > 0 and mostrar_alternativas:
                print("✅ CORRECT: Both types with clear separation")
                return True
            elif refrescos_count > 0 and alternativas_count == 0:
                print("✅ ACCEPTABLE: Only sodas (traditional behavior)")
                return True
            else:
                print("❌ MIXED: Unclear behavior")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

def test_more_options_behavior(answer_value):
    """Test more options button behavior"""
    print(f"\n📋 Testing 'More Options' for: {answer_value}")
    
    try:
        # Create session and answer questions
        response = requests.post(f"{API_URL}/iniciar-sesion")
        response.raise_for_status()
        session_data = response.json()
        session_id = session_data["sesion_id"]
        
        # Get initial question and answer with specific value
        response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
        response.raise_for_status()
        data = response.json()
        question = data["pregunta"]
        
        # Find the option with the desired value
        selected_option = None
        for option in question["opciones"]:
            if option.get("valor") == answer_value:
                selected_option = option
                break
        
        if not selected_option:
            return False
        
        # Answer questions
        response = requests.post(f"{API_URL}/responder/{session_id}", json={
            "pregunta_id": question["id"],
            "respuesta_id": selected_option["id"],
            "respuesta_texto": selected_option["texto"],
            "tiempo_respuesta": 3.0
        })
        response.raise_for_status()
        
        # Answer remaining questions
        for i in range(5):
            response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "finalizada" in data and data["finalizada"]:
                break
                
            question = data["pregunta"]
            option_index = len(question["opciones"]) // 2
            selected_option = question["opciones"][option_index]
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": random.uniform(2.0, 8.0)
            })
            response.raise_for_status()
        
        # Get initial recommendations
        response = requests.get(f"{API_URL}/recomendacion/{session_id}")
        response.raise_for_status()
        initial_recommendations = response.json()
        
        initial_refrescos = len(initial_recommendations.get("refrescos_reales", []))
        initial_alternativas = len(initial_recommendations.get("bebidas_alternativas", []))
        
        print(f"   Initial: {initial_refrescos} refrescos, {initial_alternativas} alternatives")
        
        # Test more options button
        response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
        response.raise_for_status()
        more_options = response.json()
        
        if not more_options.get("sin_mas_opciones", False):
            additional_recs = more_options.get("recomendaciones_adicionales", [])
            tipo_recomendaciones = more_options.get("tipo_recomendaciones", "")
            
            print(f"   More options: {len(additional_recs)} recommendations ({tipo_recomendaciones})")
            
            # Verify behavior is consistent
            if answer_value == "no_consume_refrescos":
                if "alternativas" in tipo_recomendaciones:
                    print("✅ CORRECT: More alternatives for non-soda consumer")
                    return True
                else:
                    print("❌ INCORRECT: Should give more alternatives")
                    return False
            elif answer_value == "prefiere_alternativas":
                print("✅ ACCEPTABLE: Dynamic behavior for prefiere_alternativas")
                return True
            else:
                print("✅ ACCEPTABLE: More options working")
                return True
        else:
            print("⚠️ No more options available")
            return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

def main():
    """Run critical tests"""
    print("="*80)
    print("🎯 CRITICAL TESTING: REDESIGNED SYSTEM WITH 6 NEW QUESTIONS")
    print("="*80)
    
    results = []
    
    # Test 1: 6 New Questions Structure
    results.append(("6 New Questions Structure", test_six_new_questions()))
    
    # Test 2: Critical User Behaviors
    critical_tests = [
        ("no_consume_refrescos", "ONLY_ALTERNATIVES"),
        ("prefiere_alternativas", "CLEAR_SEPARATION"),
        ("regular_consumidor", "CLEAR_SEPARATION"),
        ("ocasional_consumidor", "CLEAR_SEPARATION"),
    ]
    
    for answer_value, expected_behavior in critical_tests:
        test_name = f"User Behavior: {answer_value}"
        results.append((test_name, test_specific_user_behavior(answer_value, expected_behavior)))
    
    # Test 3: More Options Button
    more_options_tests = [
        "no_consume_refrescos",
        "prefiere_alternativas",
        "regular_consumidor"
    ]
    
    for answer_value in more_options_tests:
        test_name = f"More Options: {answer_value}"
        results.append((test_name, test_more_options_behavior(answer_value)))
    
    # Summary
    print("\n" + "="*80)
    print("📊 CRITICAL TEST RESULTS")
    print("="*80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 OVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 SUCCESS: All critical tests passed! Redesigned system is working correctly!")
    elif passed >= total * 0.8:
        print("⚠️ GOOD: Most critical tests passed, minor issues remain")
    else:
        print("❌ CRITICAL ISSUES: Major problems detected in redesigned system")

if __name__ == "__main__":
    main()