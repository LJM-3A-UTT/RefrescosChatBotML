#!/usr/bin/env python3
"""
Quick test for specific flavor priority case
"""

import requests
import json
import random
import os
from dotenv import load_dotenv

load_dotenv("/app/frontend/.env")
BACKEND_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001")
API_URL = f"{BACKEND_URL}/api"

def test_flavor_priority():
    """Test user who prioritizes flavor should get only sodas"""
    print("🔍 Testing: User who prioritizes flavor (should get ONLY sodas)")
    
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
        
        # Answer with "regular_consumidor"
        selected_option = None
        for option in question["opciones"]:
            if option.get("valor") == "regular_consumidor":
                selected_option = option
                break
        
        response = requests.post(f"{API_URL}/responder/{session_id}", json={
            "pregunta_id": question["id"],
            "respuesta_id": selected_option["id"],
            "respuesta_texto": selected_option["texto"],
            "tiempo_respuesta": 3.0
        })
        response.raise_for_status()
        
        # Get next question and look for flavor priority
        response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
        response.raise_for_status()
        data = response.json()
        question = data["pregunta"]
        
        print(f"Q2: {question.get('pregunta', '')}")
        
        # Look for "prioridad_sabor" option
        selected_option = None
        for option in question["opciones"]:
            if "prioridad_sabor" in option.get("valor", "") or "sabor" in option.get("texto", "").lower():
                selected_option = option
                print(f"Found flavor priority option: {option}")
                break
        
        if not selected_option:
            # Use first option as fallback
            selected_option = question["opciones"][0]
            print(f"Using fallback option: {selected_option}")
        
        response = requests.post(f"{API_URL}/responder/{session_id}", json={
            "pregunta_id": question["id"],
            "respuesta_id": selected_option["id"],
            "respuesta_texto": selected_option["texto"],
            "tiempo_respuesta": 3.0
        })
        response.raise_for_status()
        
        # Answer remaining questions with neutral responses
        for i in range(4):
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
        
        # Get recommendations
        response = requests.get(f"{API_URL}/recomendacion/{session_id}")
        response.raise_for_status()
        recommendations = response.json()
        
        refrescos_count = len(recommendations.get("refrescos_reales", []))
        alternativas_count = len(recommendations.get("bebidas_alternativas", []))
        mostrar_alternativas = recommendations.get("mostrar_alternativas", False)
        
        print(f"Result: {refrescos_count} refrescos, {alternativas_count} alternatives")
        print(f"mostrar_alternativas: {mostrar_alternativas}")
        
        if refrescos_count > 0 and alternativas_count == 0:
            print("✅ SUCCESS: User who prioritizes flavor gets only sodas")
            return True
        elif refrescos_count == 0 and alternativas_count > 0:
            print("❌ INCORRECT: User who prioritizes flavor should get sodas, not alternatives")
            return False
        else:
            print("❌ MIXED: User getting both types (mixed behavior)")
            return False
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_flavor_priority()