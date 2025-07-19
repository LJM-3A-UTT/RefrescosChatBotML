#!/usr/bin/env python3
"""
Debug the determinar_mostrar_alternativas function
"""

import requests
import json
import random
import os
from dotenv import load_dotenv

load_dotenv("/app/frontend/.env")
BACKEND_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001")
API_URL = f"{BACKEND_URL}/api"

def debug_user_responses():
    """Debug what responses are being sent to determinar_mostrar_alternativas"""
    print("🔍 Debugging user responses and logic")
    
    try:
        # Create session
        response = requests.post(f"{API_URL}/iniciar-sesion")
        response.raise_for_status()
        session_data = response.json()
        session_id = session_data["sesion_id"]
        
        # Answer questions with specific pattern
        questions_and_answers = []
        
        # Get initial question
        response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
        response.raise_for_status()
        data = response.json()
        question = data["pregunta"]
        
        # Answer with "regular_consumidor"
        selected_option = None
        for option in question["opciones"]:
            if option.get("valor") == "regular_consumidor":
                selected_option = option
                break
        
        questions_and_answers.append((question["pregunta"], selected_option["texto"], selected_option["valor"]))
        
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
            
            # For question about what's important, choose flavor priority
            if "importante" in question.get("pregunta", "").lower():
                selected_option = None
                for option in question["opciones"]:
                    if "prioridad_sabor" in option.get("valor", "") or "sabor" in option.get("texto", "").lower():
                        selected_option = option
                        break
                if not selected_option:
                    selected_option = question["opciones"][0]
            else:
                # Use neutral response for other questions
                option_index = len(question["opciones"]) // 2
                selected_option = question["opciones"][option_index]
            
            questions_and_answers.append((question["pregunta"], selected_option["texto"], selected_option["valor"]))
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": random.uniform(2.0, 8.0)
            })
            response.raise_for_status()
        
        print("\n📋 Questions and Answers:")
        for i, (q, a, v) in enumerate(questions_and_answers, 1):
            print(f"Q{i}: {q}")
            print(f"A{i}: {a} (valor: {v})")
            print()
        
        # Get recommendations to see the result
        response = requests.get(f"{API_URL}/recomendacion/{session_id}")
        response.raise_for_status()
        recommendations = response.json()
        
        refrescos_count = len(recommendations.get("refrescos_reales", []))
        alternativas_count = len(recommendations.get("bebidas_alternativas", []))
        mostrar_alternativas = recommendations.get("mostrar_alternativas", False)
        
        print(f"📊 Final Result:")
        print(f"   Refrescos: {refrescos_count}")
        print(f"   Alternatives: {alternativas_count}")
        print(f"   mostrar_alternativas: {mostrar_alternativas}")
        
        # Check what values would be in the response_str
        valores = [v for _, _, v in questions_and_answers]
        response_str = str(valores).lower()
        print(f"\n🔍 Response string that determinar_mostrar_alternativas sees:")
        print(f"   {response_str}")
        
        # Check specific conditions
        print(f"\n🔍 Checking conditions:")
        print(f"   'bebidas_naturales' in response_str: {'bebidas_naturales' in response_str}")
        print(f"   'prioridad_salud' in response_str: {'prioridad_salud' in response_str}")
        print(f"   'prioridad_sabor' in response_str: {'prioridad_sabor' in response_str}")
        print(f"   'ama_refrescos' in response_str: {'ama_refrescos' in response_str}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    debug_user_responses()