#!/usr/bin/env python3
"""
Controlled test for specific priority cases
"""

import requests
import json
import random
import os
from dotenv import load_dotenv

load_dotenv("/app/frontend/.env")
BACKEND_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001")
API_URL = f"{BACKEND_URL}/api"

def test_priority_cases():
    """Test specific priority cases with controlled answers"""
    
    test_cases = [
        {
            "name": "Priority Flavor (should get ONLY sodas)",
            "target_answers": {"prioridad_sabor": "P4"},
            "expected_refrescos": "> 0",
            "expected_alternatives": "= 0"
        },
        {
            "name": "Priority Health (should get ONLY alternatives)",
            "target_answers": {"prioridad_salud": "P4"},
            "expected_refrescos": "= 0", 
            "expected_alternatives": "> 0"
        },
        {
            "name": "Loves Sodas (should get ONLY sodas)",
            "target_answers": {"ama_refrescos": "P5"},
            "expected_refrescos": "> 0",
            "expected_alternatives": "= 0"
        },
        {
            "name": "Seeks Natural Drinks (should get ONLY alternatives)",
            "target_answers": {"bebidas_naturales": "P2"},
            "expected_refrescos": "= 0",
            "expected_alternatives": "> 0"
        }
    ]
    
    results = []
    
    for case in test_cases:
        print(f"\n🔍 Testing: {case['name']}")
        print(f"   Target answers: {case['target_answers']}")
        
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
            question = data["pregunta"]
            
            # Answer P1 with neutral response
            selected_option = question["opciones"][1]  # "ocasional_consumidor"
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": 3.0
            })
            response.raise_for_status()
            
            # Answer remaining questions (P2-P6)
            for i in range(5):
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                data = response.json()
                
                if "finalizada" in data and data["finalizada"]:
                    break
                    
                question = data["pregunta"]
                question_text = question.get("pregunta", "").lower()
                
                # Try to match target answer for this question
                selected_option = None
                for target_value, question_hint in case["target_answers"].items():
                    # Check if this is the right question for this target answer
                    if (target_value in ["prioridad_sabor", "prioridad_salud"] and "importante" in question_text) or \
                       (target_value in ["ama_refrescos", "evita_salud"] and "sientes" in question_text) or \
                       (target_value in ["bebidas_naturales", "refrescos_tradicionales"] and "tipo" in question_text):
                        
                        # Find the option with this value
                        for option in question["opciones"]:
                            if target_value in option.get("valor", ""):
                                selected_option = option
                                print(f"   ✅ Found target answer: {target_value} in {option['texto']}")
                                break
                        break
                
                if not selected_option:
                    # Use neutral response
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
            mostrar_alternativas = recommendations.get("mostrar_alternativas", False)
            
            print(f"   Result: {refrescos_count} refrescos, {alternativas_count} alternatives")
            print(f"   mostrar_alternativas: {mostrar_alternativas}")
            
            # Check if result matches expectation
            refrescos_ok = False
            alternatives_ok = False
            
            if case["expected_refrescos"] == "> 0":
                refrescos_ok = refrescos_count > 0
            elif case["expected_refrescos"] == "= 0":
                refrescos_ok = refrescos_count == 0
            
            if case["expected_alternatives"] == "> 0":
                alternatives_ok = alternativas_count > 0
            elif case["expected_alternatives"] == "= 0":
                alternatives_ok = alternativas_count == 0
            
            if refrescos_ok and alternatives_ok:
                print(f"   ✅ SUCCESS: Matches expected behavior")
                results.append(True)
            else:
                print(f"   ❌ FAILED: Expected {case['expected_refrescos']} refrescos, {case['expected_alternatives']} alternatives")
                results.append(False)
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 PRIORITY LOGIC TEST RESULTS:")
    print(f"   Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 SUCCESS: All priority cases work correctly!")
    elif passed >= total * 0.75:
        print("⚠️ GOOD: Most priority cases work correctly")
    else:
        print("❌ CRITICAL: Priority logic needs more work")
    
    return passed == total

if __name__ == "__main__":
    test_priority_cases()