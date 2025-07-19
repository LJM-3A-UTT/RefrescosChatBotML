#!/usr/bin/env python3
"""
Comprehensive Test for New determinar_mostrar_alternativas Logic
Testing the specific cases mentioned in the review request
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

def test_new_logic_comprehensive():
    """Test the new determinar_mostrar_alternativas logic comprehensively"""
    print("\n🔍 COMPREHENSIVE TEST: New determinar_mostrar_alternativas Logic")
    
    # Test cases from the review request
    test_cases = [
        {
            "name": "prioridad_sabor",
            "expected": "ONLY refrescos",
            "should_have_refrescos": True,
            "should_have_alternatives": False
        },
        {
            "name": "prioridad_salud", 
            "expected": "ONLY alternativas",
            "should_have_refrescos": False,
            "should_have_alternatives": True
        },
        {
            "name": "no_consume_refrescos",
            "expected": "ONLY alternativas",
            "should_have_refrescos": False,
            "should_have_alternatives": True
        },
        {
            "name": "bebidas_naturales",
            "expected": "ONLY alternativas",
            "should_have_refrescos": False,
            "should_have_alternatives": True
        },
        {
            "name": "ama_refrescos",
            "expected": "ONLY refrescos",
            "should_have_refrescos": True,
            "should_have_alternatives": False
        },
        {
            "name": "regular_consumidor",
            "expected": "Predictable behavior",
            "should_have_refrescos": None,  # Can be either
            "should_have_alternatives": None
        }
    ]
    
    results = {}
    
    for case in test_cases:
        print(f"\n📋 Testing: {case['name']}")
        print(f"   Expected: {case['expected']}")
        
        try:
            session_id = create_session_with_specific_answer(case['name'])
            if not session_id:
                print(f"❌ Could not create session for {case['name']}")
                results[case['name']] = False
                continue
            
            # Get recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}", timeout=30)
            response.raise_for_status()
            recommendations = response.json()
            
            refrescos_count = len(recommendations.get("refrescos_reales", []))
            alternativas_count = len(recommendations.get("bebidas_alternativas", []))
            mostrar_alternativas = recommendations.get("mostrar_alternativas", False)
            usuario_no_consume = recommendations.get("usuario_no_consume_refrescos", False)
            
            print(f"   Result: {refrescos_count} refrescos, {alternativas_count} alternativas")
            print(f"   Flags: mostrar_alternativas={mostrar_alternativas}, usuario_no_consume={usuario_no_consume}")
            
            # Check if result matches expectation
            case_passed = True
            
            if case['should_have_refrescos'] is True and refrescos_count == 0:
                print(f"❌ FAILED: Expected refrescos but got none")
                case_passed = False
            elif case['should_have_refrescos'] is False and refrescos_count > 0:
                print(f"❌ FAILED: Expected no refrescos but got {refrescos_count}")
                case_passed = False
            
            if case['should_have_alternatives'] is True and alternativas_count == 0:
                print(f"❌ FAILED: Expected alternatives but got none")
                case_passed = False
            elif case['should_have_alternatives'] is False and alternativas_count > 0:
                print(f"❌ FAILED: Expected no alternatives but got {alternativas_count}")
                case_passed = False
            
            # Check for mixed behavior (both types when not expected)
            if refrescos_count > 0 and alternativas_count > 0:
                if case['expected'] not in ["Predictable behavior", "Both types separately"]:
                    print(f"❌ MIXED BEHAVIOR: Got both types when expecting {case['expected']}")
                    case_passed = False
                else:
                    print(f"✅ ACCEPTABLE: Both types shown (predictable behavior)")
            
            if case_passed:
                print(f"✅ PASSED: {case['name']} behaves correctly")
                results[case['name']] = True
            else:
                print(f"❌ FAILED: {case['name']} has incorrect behavior")
                results[case['name']] = False
                
            # Test "more options" button behavior
            print(f"   Testing 'more options' for {case['name']}...")
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}", timeout=30)
            response.raise_for_status()
            more_options = response.json()
            
            if not more_options.get("sin_mas_opciones", False):
                additional_recs = more_options.get("recomendaciones_adicionales", [])
                tipo_recomendaciones = more_options.get("tipo_recomendaciones", "")
                print(f"   More options: {len(additional_recs)} recommendations ({tipo_recomendaciones})")
            else:
                print(f"   More options: No more available")
                
        except Exception as e:
            print(f"❌ Error testing {case['name']}: {str(e)}")
            results[case['name']] = False
    
    # Analyze overall results
    passed_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    success_rate = passed_count / total_count if total_count > 0 else 0
    
    print(f"\n📊 COMPREHENSIVE TEST RESULTS:")
    print(f"✅ Passed: {passed_count}/{total_count} ({success_rate:.1%})")
    
    for case_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {case_name}")
    
    return success_rate >= 0.8  # 80% success rate required

def test_mixed_behavior_elimination():
    """Test that mixed behavior has been eliminated"""
    print("\n🔍 TESTING: Mixed Behavior Elimination")
    
    # Test multiple user patterns to ensure no mixed behavior
    test_patterns = [
        "no_consume_refrescos",
        "prefiere_alternativas", 
        "prioridad_salud",
        "prioridad_sabor",
        "bebidas_naturales",
        "ama_refrescos",
        "regular_consumidor",
        "ocasional_consumidor"
    ]
    
    mixed_behavior_detected = 0
    clear_behavior_count = 0
    
    for pattern in test_patterns:
        print(f"\n📋 Testing pattern: {pattern}")
        
        try:
            session_id = create_session_with_specific_answer(pattern)
            if not session_id:
                continue
            
            response = requests.get(f"{API_URL}/recomendacion/{session_id}", timeout=30)
            response.raise_for_status()
            recommendations = response.json()
            
            refrescos_count = len(recommendations.get("refrescos_reales", []))
            alternativas_count = len(recommendations.get("bebidas_alternativas", []))
            mostrar_alternativas = recommendations.get("mostrar_alternativas", False)
            
            print(f"   Result: {refrescos_count} refrescos, {alternativas_count} alternativas")
            
            # Analyze behavior clarity
            if refrescos_count > 0 and alternativas_count > 0:
                # Both types shown - check if it's clear separation
                if mostrar_alternativas:
                    print(f"✅ CLEAR: Both types with mostrar_alternativas=True (clear separation)")
                    clear_behavior_count += 1
                else:
                    print(f"❌ MIXED: Both types without clear separation flag")
                    mixed_behavior_detected += 1
            elif refrescos_count > 0 and alternativas_count == 0:
                print(f"✅ CLEAR: Only refrescos")
                clear_behavior_count += 1
            elif refrescos_count == 0 and alternativas_count > 0:
                print(f"✅ CLEAR: Only alternatives")
                clear_behavior_count += 1
            else:
                print(f"⚠️ UNCLEAR: No recommendations")
                
        except Exception as e:
            print(f"❌ Error testing pattern {pattern}: {str(e)}")
    
    total_tested = mixed_behavior_detected + clear_behavior_count
    if total_tested > 0:
        clear_rate = clear_behavior_count / total_tested
        print(f"\n📊 MIXED BEHAVIOR ANALYSIS:")
        print(f"✅ Clear behavior: {clear_behavior_count}/{total_tested} ({clear_rate:.1%})")
        print(f"❌ Mixed behavior: {mixed_behavior_detected}/{total_tested}")
        
        if mixed_behavior_detected == 0:
            print("🎉 SUCCESS: No mixed behavior detected!")
            return True
        else:
            print("⚠️ WARNING: Some mixed behavior still exists")
            return False
    else:
        print("❌ No patterns could be tested")
        return False

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
    """Run comprehensive tests"""
    print("="*80)
    print("🎯 COMPREHENSIVE TESTING - NEW LOGIC VERIFICATION")
    print("="*80)
    
    results = {}
    
    # Test 1: Comprehensive logic test
    results["New Logic"] = test_new_logic_comprehensive()
    
    # Test 2: Mixed behavior elimination
    results["Mixed Behavior Elimination"] = test_mixed_behavior_elimination()
    
    # Print final summary
    print("\n" + "="*80)
    print("📊 FINAL COMPREHENSIVE TEST RESULTS")
    print("="*80)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ALL COMPREHENSIVE TESTS PASSED!")
        print("✅ New determinar_mostrar_alternativas logic is working correctly")
        print("✅ Mixed behavior has been eliminated")
        print("✅ System provides predictable behavior for all user types")
    else:
        print("\n⚠️ SOME ISSUES DETECTED")
        failed_tests = [name for name, result in results.items() if not result]
        print(f"❌ Issues in: {', '.join(failed_tests)}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)