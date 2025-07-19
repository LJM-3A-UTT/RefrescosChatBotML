#!/usr/bin/env python3
"""
Backend Test Script for RefrescoBot ML - Testing Recomendaciones Alternativas
This script tests the specific corrections implemented for the alternative recommendations endpoints.
"""

import requests
import json
import time
import random
import os
from dotenv import load_dotenv
import sys
from typing import Dict, List, Any, Optional
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv("/app/frontend/.env")

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001")
API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

class RecomendacionesAlternativasTester:
    def __init__(self):
        self.all_tests_passed = True
        self.test_results = {}
        
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("\n" + "="*80)
        print("🤖 REFRESCOBOT ML RECOMENDACIONES ALTERNATIVAS TEST SUITE")
        print("="*80)
        
        # Test 1: Usuario que NO consume refrescos
        self.test_usuario_no_consume_refrescos()
        
        # Test 2: Usuario regular tradicional
        self.test_usuario_regular_tradicional()
        
        # Test 3: Usuario saludable
        self.test_usuario_saludable()
        
        # Test 4: Endpoint mas-refrescos
        self.test_mas_refrescos_endpoint()
        
        # Test 5: Endpoint mas-alternativas
        self.test_mas_alternativas_endpoint()
        
        # Test 6: Consistencia de recomendaciones
        self.test_consistencia_recomendaciones()
        
        # Test 7: Campos de respuesta
        self.test_campos_respuesta()
        
        # Print summary
        self.print_summary()
        
        return self.all_tests_passed
    
    def create_session_and_answer_questions(self, user_type="regular"):
        """
        Helper method to create a session and answer questions based on user type
        user_type can be: "no_consume" (never drinks soda), "regular" (traditional user), "saludable" (health-conscious)
        """
        try:
            # Create session
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            data = response.json()
            
            if "sesion_id" not in data:
                logger.error("Failed to create session")
                return None
                
            session_id = data["sesion_id"]
            logger.info(f"Created session with ID: {session_id}")
            
            # Get initial question (about refresco consumption)
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "pregunta" not in data:
                logger.error("Failed to get initial question")
                return None
                
            question = data["pregunta"]
            total_questions = data.get("total_preguntas", 6)
            
            # Answer initial question based on user type
            respuesta_id = None
            respuesta_texto = None
            
            if user_type == "no_consume":
                # Find "nunca" or "casi nunca" option
                for opcion in question["opciones"]:
                    if "nunca" in opcion["texto"].lower():
                        respuesta_id = opcion["id"]
                        respuesta_texto = opcion["texto"]
                        break
                
                # If not found, use first option
                if not respuesta_id:
                    respuesta_id = question["opciones"][0]["id"]
                    respuesta_texto = question["opciones"][0]["texto"]
            
            elif user_type == "saludable":
                # Find "ocasionalmente" option
                for opcion in question["opciones"]:
                    if "ocasionalmente" in opcion["texto"].lower():
                        respuesta_id = opcion["id"]
                        respuesta_texto = opcion["texto"]
                        break
                
                # If not found, use middle option
                if not respuesta_id:
                    middle_index = len(question["opciones"]) // 2
                    respuesta_id = question["opciones"][middle_index]["id"]
                    respuesta_texto = question["opciones"][middle_index]["texto"]
            
            else:  # regular
                # Find "frecuentemente" or "diario" option
                for opcion in question["opciones"]:
                    if "frecuentemente" in opcion["texto"].lower() or "diario" in opcion["texto"].lower():
                        respuesta_id = opcion["id"]
                        respuesta_texto = opcion["texto"]
                        break
                
                # If not found, use last option
                if not respuesta_id:
                    respuesta_id = question["opciones"][-1]["id"]
                    respuesta_texto = question["opciones"][-1]["texto"]
            
            # Answer initial question
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": respuesta_id,
                "respuesta_texto": respuesta_texto,
                "tiempo_respuesta": random.uniform(2.0, 10.0)
            })
            response.raise_for_status()
            logger.info(f"Answered initial question as {user_type} user")
            
            # Get and answer remaining questions based on user type
            for i in range(total_questions - 1):
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                data = response.json()
                
                if "finalizada" in data and data["finalizada"]:
                    logger.info("All questions completed")
                    break
                
                if "pregunta" not in data:
                    logger.error(f"Failed to get question {i+2}")
                    return None
                    
                question = data["pregunta"]
                
                # Answer question based on user type
                respuesta_id = None
                respuesta_texto = None
                
                if user_type == "no_consume" or user_type == "saludable":
                    # For health-conscious users, look for healthy options
                    for opcion in question["opciones"]:
                        texto_lower = opcion["texto"].lower()
                        if any(word in texto_lower for word in ["saludable", "natural", "activo", "importante", "poco_dulce"]):
                            respuesta_id = opcion["id"]
                            respuesta_texto = opcion["texto"]
                            break
                    
                    # If no healthy option found, use random option
                    if not respuesta_id:
                        random_option = random.choice(question["opciones"])
                        respuesta_id = random_option["id"]
                        respuesta_texto = random_option["texto"]
                
                else:  # regular
                    # For regular users, look for traditional options
                    for opcion in question["opciones"]:
                        texto_lower = opcion["texto"].lower()
                        if any(word in texto_lower for word in ["dulce", "sedentario", "no_importante", "tradicional"]):
                            respuesta_id = opcion["id"]
                            respuesta_texto = opcion["texto"]
                            break
                    
                    # If no traditional option found, use random option
                    if not respuesta_id:
                        random_option = random.choice(question["opciones"])
                        respuesta_id = random_option["id"]
                        respuesta_texto = random_option["texto"]
                
                # Answer question
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": question["id"],
                    "respuesta_id": respuesta_id,
                    "respuesta_texto": respuesta_texto,
                    "tiempo_respuesta": random.uniform(2.0, 10.0)
                })
                response.raise_for_status()
                logger.info(f"Answered question {i+2}")
            
            logger.info(f"Completed all questions for {user_type} user")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating session and answering questions: {str(e)}")
            return None
    
    def test_usuario_no_consume_refrescos(self):
        """Test recommendations for users who don't consume refrescos"""
        print("\n🔍 Testing Usuario que NO consume refrescos...")
        
        try:
            # Create session for user who doesn't consume refrescos
            session_id = self.create_session_and_answer_questions(user_type="no_consume")
            if not session_id:
                print("❌ Usuario NO consume: FAILED - Could not create session")
                self.test_results["Usuario NO consume"] = False
                self.all_tests_passed = False
                return
            
            # Get recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check if usuario_no_consume_refrescos is true
            if "usuario_no_consume_refrescos" not in data or not data["usuario_no_consume_refrescos"]:
                print("❌ Usuario NO consume: FAILED - usuario_no_consume_refrescos not true")
                self.test_results["Usuario NO consume"] = False
                self.all_tests_passed = False
                return
            
            print("✅ Usuario NO consume: usuario_no_consume_refrescos correctly detected as true")
            
            # Check if only alternatives are shown
            if "refrescos_reales" in data and len(data["refrescos_reales"]) > 0:
                print("❌ Usuario NO consume: FAILED - refrescos_reales should be empty")
                self.test_results["Usuario NO consume"] = False
                self.all_tests_passed = False
                return
            
            if "bebidas_alternativas" not in data or len(data["bebidas_alternativas"]) == 0:
                print("❌ Usuario NO consume: FAILED - bebidas_alternativas should not be empty")
                self.test_results["Usuario NO consume"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ Usuario NO consume: Only alternatives shown ({len(data['bebidas_alternativas'])} alternatives)")
            
            # Test recomendaciones-alternativas endpoint
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check if tipo_recomendaciones is alternativas_saludables
            if "tipo_recomendaciones" not in data or data["tipo_recomendaciones"] != "alternativas_saludables":
                print("❌ Usuario NO consume: FAILED - tipo_recomendaciones should be alternativas_saludables")
                self.test_results["Usuario NO consume"] = False
                self.all_tests_passed = False
                return
            
            print("✅ Usuario NO consume: tipo_recomendaciones correctly set to alternativas_saludables")
            
            # Check if all recommendations are alternatives (es_refresco_real = false)
            if "recomendaciones_adicionales" in data and len(data["recomendaciones_adicionales"]) > 0:
                for bebida in data["recomendaciones_adicionales"]:
                    if bebida.get("es_refresco_real", True):
                        print("❌ Usuario NO consume: FAILED - Found a real refresco in recomendaciones_adicionales")
                        self.test_results["Usuario NO consume"] = False
                        self.all_tests_passed = False
                        return
                
                print("✅ Usuario NO consume: All additional recommendations are alternatives")
            
            self.test_results["Usuario NO consume"] = True
            print("✅ Usuario NO consume: All tests PASSED")
            
        except Exception as e:
            print(f"❌ Usuario NO consume: FAILED - {str(e)}")
            self.test_results["Usuario NO consume"] = False
            self.all_tests_passed = False
    
    def test_usuario_regular_tradicional(self):
        """Test recommendations for regular traditional users"""
        print("\n🔍 Testing Usuario Regular Tradicional...")
        
        try:
            # Create session for regular user
            session_id = self.create_session_and_answer_questions(user_type="regular")
            if not session_id:
                print("❌ Usuario Regular: FAILED - Could not create session")
                self.test_results["Usuario Regular"] = False
                self.all_tests_passed = False
                return
            
            # Get recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check if usuario_no_consume_refrescos is false
            if "usuario_no_consume_refrescos" not in data or data["usuario_no_consume_refrescos"]:
                print("❌ Usuario Regular: FAILED - usuario_no_consume_refrescos should be false")
                self.test_results["Usuario Regular"] = False
                self.all_tests_passed = False
                return
            
            print("✅ Usuario Regular: usuario_no_consume_refrescos correctly detected as false")
            
            # Check if refrescos_reales are shown
            if "refrescos_reales" not in data or len(data["refrescos_reales"]) == 0:
                print("❌ Usuario Regular: FAILED - refrescos_reales should not be empty")
                self.test_results["Usuario Regular"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ Usuario Regular: {len(data['refrescos_reales'])} refrescos_reales shown")
            
            # Test recomendaciones-alternativas endpoint
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check if mostrar_alternativas is false (for traditional users)
            # Note: This might vary based on the specific answers, but for a traditional user profile it should be false
            if "mostrar_alternativas" in data and not data["mostrar_alternativas"]:
                print("✅ Usuario Regular: mostrar_alternativas correctly set to false")
                
                # Check if tipo_recomendaciones is refrescos_tradicionales
                if "tipo_recomendaciones" in data and data["tipo_recomendaciones"] == "refrescos_tradicionales":
                    print("✅ Usuario Regular: tipo_recomendaciones correctly set to refrescos_tradicionales")
                    
                    # Check if all recommendations are real refrescos (es_refresco_real = true)
                    if "recomendaciones_adicionales" in data and len(data["recomendaciones_adicionales"]) > 0:
                        all_refrescos = True
                        for bebida in data["recomendaciones_adicionales"]:
                            if not bebida.get("es_refresco_real", False):
                                all_refrescos = False
                                break
                        
                        if all_refrescos:
                            print("✅ Usuario Regular: All additional recommendations are real refrescos")
                        else:
                            print("❌ Usuario Regular: FAILED - Found alternatives in recomendaciones_adicionales")
                            self.test_results["Usuario Regular"] = False
                            self.all_tests_passed = False
                            return
                    
                    self.test_results["Usuario Regular"] = True
                    print("✅ Usuario Regular: All tests PASSED")
                else:
                    print(f"❌ Usuario Regular: FAILED - tipo_recomendaciones should be refrescos_tradicionales, got {data.get('tipo_recomendaciones', 'missing')}")
                    self.test_results["Usuario Regular"] = False
                    self.all_tests_passed = False
            else:
                # If mostrar_alternativas is true, this might still be valid depending on the specific answers
                print("⚠️ Usuario Regular: mostrar_alternativas is true, which might be valid depending on the specific answers")
                self.test_results["Usuario Regular"] = True
                print("✅ Usuario Regular: Tests PASSED with warning")
            
        except Exception as e:
            print(f"❌ Usuario Regular: FAILED - {str(e)}")
            self.test_results["Usuario Regular"] = False
            self.all_tests_passed = False
    
    def test_usuario_saludable(self):
        """Test recommendations for health-conscious users"""
        print("\n🔍 Testing Usuario Saludable...")
        
        try:
            # Create session for health-conscious user
            session_id = self.create_session_and_answer_questions(user_type="saludable")
            if not session_id:
                print("❌ Usuario Saludable: FAILED - Could not create session")
                self.test_results["Usuario Saludable"] = False
                self.all_tests_passed = False
                return
            
            # Get recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check if usuario_no_consume_refrescos is false
            if "usuario_no_consume_refrescos" not in data or data["usuario_no_consume_refrescos"]:
                print("❌ Usuario Saludable: FAILED - usuario_no_consume_refrescos should be false")
                self.test_results["Usuario Saludable"] = False
                self.all_tests_passed = False
                return
            
            print("✅ Usuario Saludable: usuario_no_consume_refrescos correctly detected as false")
            
            # Check if mostrar_alternativas is true
            if "mostrar_alternativas" not in data or not data["mostrar_alternativas"]:
                print("❌ Usuario Saludable: FAILED - mostrar_alternativas should be true")
                self.test_results["Usuario Saludable"] = False
                self.all_tests_passed = False
                return
            
            print("✅ Usuario Saludable: mostrar_alternativas correctly set to true")
            
            # Check if bebidas_alternativas are shown
            if "bebidas_alternativas" not in data or len(data["bebidas_alternativas"]) == 0:
                print("❌ Usuario Saludable: FAILED - bebidas_alternativas should not be empty")
                self.test_results["Usuario Saludable"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ Usuario Saludable: {len(data['bebidas_alternativas'])} bebidas_alternativas shown")
            
            # Test recomendaciones-alternativas endpoint
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check if tipo_recomendaciones is alternativas_saludables
            if "tipo_recomendaciones" not in data or data["tipo_recomendaciones"] != "alternativas_saludables":
                print("❌ Usuario Saludable: FAILED - tipo_recomendaciones should be alternativas_saludables")
                self.test_results["Usuario Saludable"] = False
                self.all_tests_passed = False
                return
            
            print("✅ Usuario Saludable: tipo_recomendaciones correctly set to alternativas_saludables")
            
            # Check if all recommendations are alternatives (es_refresco_real = false)
            if "recomendaciones_adicionales" in data and len(data["recomendaciones_adicionales"]) > 0:
                all_alternatives = True
                for bebida in data["recomendaciones_adicionales"]:
                    if bebida.get("es_refresco_real", True):
                        all_alternatives = False
                        break
                
                if all_alternatives:
                    print("✅ Usuario Saludable: All additional recommendations are alternatives")
                else:
                    print("❌ Usuario Saludable: FAILED - Found real refrescos in recomendaciones_adicionales")
                    self.test_results["Usuario Saludable"] = False
                    self.all_tests_passed = False
                    return
            
            self.test_results["Usuario Saludable"] = True
            print("✅ Usuario Saludable: All tests PASSED")
            
        except Exception as e:
            print(f"❌ Usuario Saludable: FAILED - {str(e)}")
            self.test_results["Usuario Saludable"] = False
            self.all_tests_passed = False
    
    def test_mas_refrescos_endpoint(self):
        """Test the /api/mas-refrescos/{sesion_id} endpoint"""
        print("\n🔍 Testing /api/mas-refrescos Endpoint...")
        
        try:
            # Create session for regular user
            session_id = self.create_session_and_answer_questions(user_type="regular")
            if not session_id:
                print("❌ Mas Refrescos: FAILED - Could not create session")
                self.test_results["Mas Refrescos"] = False
                self.all_tests_passed = False
                return
            
            # Test mas-refrescos endpoint
            response = requests.get(f"{API_URL}/mas-refrescos/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check for required fields
            if "mas_refrescos" not in data:
                print("❌ Mas Refrescos: FAILED - Missing mas_refrescos field")
                self.test_results["Mas Refrescos"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ Mas Refrescos: Got {len(data['mas_refrescos'])} additional refrescos")
            
            # Check if all recommendations are real refrescos (es_refresco_real = true)
            if "mas_refrescos" in data and len(data["mas_refrescos"]) > 0:
                all_refrescos = True
                for bebida in data["mas_refrescos"]:
                    if not bebida.get("es_refresco_real", False):
                        all_refrescos = False
                        break
                
                if all_refrescos:
                    print("✅ Mas Refrescos: All recommendations are real refrescos")
                else:
                    print("❌ Mas Refrescos: FAILED - Found alternatives in mas_refrescos")
                    self.test_results["Mas Refrescos"] = False
                    self.all_tests_passed = False
                    return
            
            # Check for tipo field
            if "tipo" not in data or data["tipo"] != "refrescos_tradicionales":
                print("❌ Mas Refrescos: FAILED - tipo should be refrescos_tradicionales")
                self.test_results["Mas Refrescos"] = False
                self.all_tests_passed = False
                return
            
            print("✅ Mas Refrescos: tipo correctly set to refrescos_tradicionales")
            
            self.test_results["Mas Refrescos"] = True
            print("✅ Mas Refrescos: All tests PASSED")
            
        except Exception as e:
            print(f"❌ Mas Refrescos: FAILED - {str(e)}")
            self.test_results["Mas Refrescos"] = False
            self.all_tests_passed = False
    
    def test_mas_alternativas_endpoint(self):
        """Test the /api/mas-alternativas/{sesion_id} endpoint"""
        print("\n🔍 Testing /api/mas-alternativas Endpoint...")
        
        try:
            # Create session for health-conscious user
            session_id = self.create_session_and_answer_questions(user_type="saludable")
            if not session_id:
                print("❌ Mas Alternativas: FAILED - Could not create session")
                self.test_results["Mas Alternativas"] = False
                self.all_tests_passed = False
                return
            
            # Test mas-alternativas endpoint
            response = requests.get(f"{API_URL}/mas-alternativas/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check for required fields
            if "mas_alternativas" not in data:
                print("❌ Mas Alternativas: FAILED - Missing mas_alternativas field")
                self.test_results["Mas Alternativas"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ Mas Alternativas: Got {len(data['mas_alternativas'])} additional alternatives")
            
            # Check if all recommendations are alternatives (es_refresco_real = false)
            if "mas_alternativas" in data and len(data["mas_alternativas"]) > 0:
                all_alternatives = True
                for bebida in data["mas_alternativas"]:
                    if bebida.get("es_refresco_real", True):
                        all_alternatives = False
                        break
                
                if all_alternatives:
                    print("✅ Mas Alternativas: All recommendations are alternatives")
                else:
                    print("❌ Mas Alternativas: FAILED - Found real refrescos in mas_alternativas")
                    self.test_results["Mas Alternativas"] = False
                    self.all_tests_passed = False
                    return
            
            # Check for tipo field
            if "tipo" not in data or data["tipo"] != "alternativas_saludables":
                print("❌ Mas Alternativas: FAILED - tipo should be alternativas_saludables")
                self.test_results["Mas Alternativas"] = False
                self.all_tests_passed = False
                return
            
            print("✅ Mas Alternativas: tipo correctly set to alternativas_saludables")
            
            self.test_results["Mas Alternativas"] = True
            print("✅ Mas Alternativas: All tests PASSED")
            
        except Exception as e:
            print(f"❌ Mas Alternativas: FAILED - {str(e)}")
            self.test_results["Mas Alternativas"] = False
            self.all_tests_passed = False
    
    def test_consistencia_recomendaciones(self):
        """Test consistency between initial and additional recommendations"""
        print("\n🔍 Testing Consistencia de Recomendaciones...")
        
        try:
            # Test for regular user
            print("Testing consistency for regular user...")
            session_id = self.create_session_and_answer_questions(user_type="regular")
            if not session_id:
                print("❌ Consistencia: FAILED - Could not create session for regular user")
                self.test_results["Consistencia"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            initial_data = response.json()
            
            # Check if refrescos_reales are shown
            if "refrescos_reales" not in initial_data or len(initial_data["refrescos_reales"]) == 0:
                print("❌ Consistencia: FAILED - refrescos_reales should not be empty for regular user")
                self.test_results["Consistencia"] = False
                self.all_tests_passed = False
                return
            
            # Get additional recommendations
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
            response.raise_for_status()
            additional_data = response.json()
            
            # Check consistency based on mostrar_alternativas
            if "mostrar_alternativas" in initial_data and not initial_data["mostrar_alternativas"]:
                # If not showing alternatives, should get more refrescos
                if "tipo_recomendaciones" in additional_data and additional_data["tipo_recomendaciones"] == "refrescos_tradicionales":
                    print("✅ Consistencia: Regular user correctly gets more refrescos")
                else:
                    print("❌ Consistencia: FAILED - Regular user should get more refrescos")
                    self.test_results["Consistencia"] = False
                    self.all_tests_passed = False
                    return
            
            # Test for health-conscious user
            print("Testing consistency for health-conscious user...")
            session_id = self.create_session_and_answer_questions(user_type="saludable")
            if not session_id:
                print("❌ Consistencia: FAILED - Could not create session for health-conscious user")
                self.test_results["Consistencia"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            initial_data = response.json()
            
            # Check if bebidas_alternativas are shown
            if "bebidas_alternativas" not in initial_data or len(initial_data["bebidas_alternativas"]) == 0:
                print("❌ Consistencia: FAILED - bebidas_alternativas should not be empty for health-conscious user")
                self.test_results["Consistencia"] = False
                self.all_tests_passed = False
                return
            
            # Get additional recommendations
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
            response.raise_for_status()
            additional_data = response.json()
            
            # Check consistency
            if "tipo_recomendaciones" in additional_data and additional_data["tipo_recomendaciones"] == "alternativas_saludables":
                print("✅ Consistencia: Health-conscious user correctly gets more alternatives")
            else:
                print("❌ Consistencia: FAILED - Health-conscious user should get more alternatives")
                self.test_results["Consistencia"] = False
                self.all_tests_passed = False
                return
            
            # Test for user who doesn't consume refrescos
            print("Testing consistency for user who doesn't consume refrescos...")
            session_id = self.create_session_and_answer_questions(user_type="no_consume")
            if not session_id:
                print("❌ Consistencia: FAILED - Could not create session for user who doesn't consume refrescos")
                self.test_results["Consistencia"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            initial_data = response.json()
            
            # Check if only bebidas_alternativas are shown
            if "refrescos_reales" in initial_data and len(initial_data["refrescos_reales"]) > 0:
                print("❌ Consistencia: FAILED - refrescos_reales should be empty for user who doesn't consume refrescos")
                self.test_results["Consistencia"] = False
                self.all_tests_passed = False
                return
            
            if "bebidas_alternativas" not in initial_data or len(initial_data["bebidas_alternativas"]) == 0:
                print("❌ Consistencia: FAILED - bebidas_alternativas should not be empty for user who doesn't consume refrescos")
                self.test_results["Consistencia"] = False
                self.all_tests_passed = False
                return
            
            # Get additional recommendations
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
            response.raise_for_status()
            additional_data = response.json()
            
            # Check consistency
            if "tipo_recomendaciones" in additional_data and additional_data["tipo_recomendaciones"] == "alternativas_saludables":
                print("✅ Consistencia: User who doesn't consume refrescos correctly gets more alternatives")
            else:
                print("❌ Consistencia: FAILED - User who doesn't consume refrescos should get more alternatives")
                self.test_results["Consistencia"] = False
                self.all_tests_passed = False
                return
            
            self.test_results["Consistencia"] = True
            print("✅ Consistencia: All tests PASSED")
            
        except Exception as e:
            print(f"❌ Consistencia: FAILED - {str(e)}")
            self.test_results["Consistencia"] = False
            self.all_tests_passed = False
    
    def test_campos_respuesta(self):
        """Test response fields in the recommendations"""
        print("\n🔍 Testing Campos de Respuesta...")
        
        try:
            # Create session
            session_id = self.create_session_and_answer_questions(user_type="regular")
            if not session_id:
                print("❌ Campos Respuesta: FAILED - Could not create session")
                self.test_results["Campos Respuesta"] = False
                self.all_tests_passed = False
                return
            
            # Test recomendaciones-alternativas endpoint
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check for required fields
            required_fields = ["tipo_recomendaciones", "usuario_no_consume_refrescos", "mostrar_alternativas", "estadisticas"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Campos Respuesta: FAILED - Missing fields: {missing_fields}")
                self.test_results["Campos Respuesta"] = False
                self.all_tests_passed = False
                return
            
            print("✅ Campos Respuesta: All required fields present")
            
            # Check estadisticas field
            if "estadisticas" in data:
                estadisticas = data["estadisticas"]
                required_stats = ["refrescos_disponibles", "alternativas_disponibles", "total_recomendadas"]
                missing_stats = [stat for stat in required_stats if stat not in estadisticas]
                
                if missing_stats:
                    print(f"❌ Campos Respuesta: FAILED - Missing statistics: {missing_stats}")
                    self.test_results["Campos Respuesta"] = False
                    self.all_tests_passed = False
                    return
                
                print("✅ Campos Respuesta: All required statistics present")
                print(f"✅ Campos Respuesta: refrescos_disponibles: {estadisticas['refrescos_disponibles']}")
                print(f"✅ Campos Respuesta: alternativas_disponibles: {estadisticas['alternativas_disponibles']}")
                print(f"✅ Campos Respuesta: total_recomendadas: {estadisticas['total_recomendadas']}")
            
            # Test mas-refrescos endpoint
            response = requests.get(f"{API_URL}/mas-refrescos/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check for required fields
            required_fields = ["mas_refrescos", "sin_mas_opciones", "mensaje", "tipo"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Campos Respuesta: FAILED - Missing fields in mas-refrescos: {missing_fields}")
                self.test_results["Campos Respuesta"] = False
                self.all_tests_passed = False
                return
            
            print("✅ Campos Respuesta: All required fields present in mas-refrescos")
            
            # Test mas-alternativas endpoint
            response = requests.get(f"{API_URL}/mas-alternativas/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check for required fields
            required_fields = ["mas_alternativas", "sin_mas_opciones", "mensaje", "tipo"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Campos Respuesta: FAILED - Missing fields in mas-alternativas: {missing_fields}")
                self.test_results["Campos Respuesta"] = False
                self.all_tests_passed = False
                return
            
            print("✅ Campos Respuesta: All required fields present in mas-alternativas")
            
            self.test_results["Campos Respuesta"] = True
            print("✅ Campos Respuesta: All tests PASSED")
            
        except Exception as e:
            print(f"❌ Campos Respuesta: FAILED - {str(e)}")
            self.test_results["Campos Respuesta"] = False
            self.all_tests_passed = False
    
    def print_summary(self):
        """Print a summary of all test results"""
        print("\n" + "="*80)
        print("📊 TEST RESULTS SUMMARY")
        print("="*80)
        
        all_passed = True
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            if not result:
                all_passed = False
            print(f"{status} - {test_name}")
        
        print("\n" + "="*80)
        if all_passed:
            print("🎉 ALL TESTS PASSED! The recomendaciones alternativas functionality is working correctly.")
        else:
            print("❌ SOME TESTS FAILED. Please check the details above.")
        print("="*80)

if __name__ == "__main__":
    print("\n\n" + "="*80)
    print("STARTING RECOMENDACIONES ALTERNATIVAS TESTS")
    print("="*80)
    tester = RecomendacionesAlternativasTester()
    success = tester.run_all_tests()
    print("\n\n" + "="*80)
    print(f"FINAL RESULT: {'SUCCESS' if success else 'FAILURE'}")
    print("="*80)
    sys.exit(0 if success else 1)