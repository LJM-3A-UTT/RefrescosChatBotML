#!/usr/bin/env python3
"""
Backend Test Script for RefrescoBot ML - Testing Transparency and Logic Corrections
This script tests the specific transparency and logic improvements implemented in the RefrescoBot ML system.
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

# Load environment variables
load_dotenv("/app/frontend/.env")

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get("REACT_APP_BACKEND_URL")
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

# Ensure the URL ends with /api
API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

class RefrescoBotTransparencyTester:
    def __init__(self):
        self.session_id = None
        self.all_tests_passed = True
        self.test_results = {}
        
    def run_all_tests(self):
        """Run all transparency and logic tests in sequence"""
        print("\n" + "="*80)
        print("🤖 REFRESCOBOT ML TRANSPARENCY AND LOGIC TEST SUITE")
        print("="*80)
        
        # Test 1: Feedback de Puntuaciones
        self.test_rating_feedback()
        
        # Test 2: Lógica Inteligente de Alternativas - Traditional User
        self.test_alternatives_logic_traditional()
        
        # Test 3: Lógica Inteligente de Alternativas - Health-conscious User
        self.test_alternatives_logic_healthy()
        
        # Test 4: Análisis de Preferencias Saludables
        self.test_healthy_preferences_analysis()
        
        # Test 5: Estructura de Respuesta Completa
        self.test_complete_response_structure()
        
        # Print summary
        self.print_summary()
        
        return self.all_tests_passed
    
    def test_rating_feedback(self):
        """Test that rating a beverage provides detailed feedback about learning impact"""
        print("\n🔍 Testing Rating Feedback...")
        
        # Create a session and get to the recommendation stage
        self.session_id = self.create_session_and_answer_questions()
        if not self.session_id:
            print("❌ Rating Feedback: FAILED - Could not create session")
            self.test_results["Rating Feedback"] = False
            self.all_tests_passed = False
            return
        
        # Get recommendations
        try:
            response = requests.get(f"{API_URL}/recomendacion/{self.session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "refrescos_reales" in data and len(data["refrescos_reales"]) > 0:
                bebida = data["refrescos_reales"][0]
                
                # Rate the bebida with 5 stars
                presentacion_ml = bebida["presentaciones"][0]["ml"]
                response = requests.post(f"{API_URL}/puntuar", json={
                    "sesion_id": self.session_id,
                    "bebida_id": bebida["id"],
                    "puntuacion": 5,
                    "presentacion_ml": presentacion_ml
                })
                response.raise_for_status()
                rating_data = response.json()
                
                print(f"✅ Rating Feedback: Rated {bebida['nombre']} with 5 stars")
                
                # Check for feedback_aprendizaje field
                if "feedback_aprendizaje" in rating_data:
                    feedback = rating_data["feedback_aprendizaje"]
                    print(f"✅ Rating Feedback: Received feedback: {json.dumps(feedback, indent=2)}")
                    
                    # Check for required fields
                    required_fields = [
                        "mensaje_principal", 
                        "impacto_futuro", 
                        "bebidas_similares_afectadas", 
                        "nueva_puntuacion_promedio"
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in feedback]
                    
                    if not missing_fields:
                        print("✅ Rating Feedback: All required feedback fields are present")
                        
                        # Rate another bebida with 1 star to check for different message
                        if len(data["refrescos_reales"]) > 1:
                            bebida2 = data["refrescos_reales"][1]
                            presentacion_ml2 = bebida2["presentaciones"][0]["ml"]
                            
                            response = requests.post(f"{API_URL}/puntuar", json={
                                "sesion_id": self.session_id,
                                "bebida_id": bebida2["id"],
                                "puntuacion": 1,
                                "presentacion_ml": presentacion_ml2
                            })
                            response.raise_for_status()
                            rating_data2 = response.json()
                            
                            print(f"✅ Rating Feedback: Rated {bebida2['nombre']} with 1 star")
                            
                            if "feedback_aprendizaje" in rating_data2:
                                feedback2 = rating_data2["feedback_aprendizaje"]
                                
                                # Check if messages are different
                                if feedback["mensaje_principal"] != feedback2["mensaje_principal"]:
                                    print("✅ Rating Feedback: Different messages for 5-star vs 1-star ratings")
                                    print(f"   5-star message: '{feedback['mensaje_principal']}'")
                                    print(f"   1-star message: '{feedback2['mensaje_principal']}'")
                                    self.test_results["Rating Feedback"] = True
                                else:
                                    print("❌ Rating Feedback: Same message for different ratings")
                                    self.test_results["Rating Feedback"] = False
                                    self.all_tests_passed = False
                            else:
                                print("❌ Rating Feedback: Missing feedback for second rating")
                                self.test_results["Rating Feedback"] = False
                                self.all_tests_passed = False
                        else:
                            print("⚠️ Rating Feedback: Only one refresco available, can't test different rating messages")
                            self.test_results["Rating Feedback"] = True  # Still pass the test
                    else:
                        print(f"❌ Rating Feedback: Missing required fields: {missing_fields}")
                        self.test_results["Rating Feedback"] = False
                        self.all_tests_passed = False
                else:
                    print("❌ Rating Feedback: No feedback_aprendizaje field in response")
                    self.test_results["Rating Feedback"] = False
                    self.all_tests_passed = False
            else:
                print("❌ Rating Feedback: No recommendations received")
                self.test_results["Rating Feedback"] = False
                self.all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Rating Feedback: FAILED - {str(e)}")
            self.test_results["Rating Feedback"] = False
            self.all_tests_passed = False
    
    def test_alternatives_logic_traditional(self):
        """Test that traditional soda preferences result in not showing alternatives"""
        print("\n🔍 Testing Alternatives Logic - Traditional User...")
        
        # Create a new session
        try:
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            data = response.json()
            
            if "sesion_id" not in data:
                print("❌ Alternatives Logic (Traditional): FAILED - Could not create session")
                self.test_results["Alternatives Logic (Traditional)"] = False
                self.all_tests_passed = False
                return
                
            session_id = data["sesion_id"]
            
            # Get initial question (about soda consumption)
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "pregunta" not in data:
                print("❌ Alternatives Logic (Traditional): FAILED - Could not get initial question")
                self.test_results["Alternatives Logic (Traditional)"] = False
                self.all_tests_passed = False
                return
                
            question = data["pregunta"]
            
            # Answer initial question - indicating regular soda consumption (option 0 or 1)
            response = requests.post(f"{API_URL}/responder", json={
                "sesion_id": session_id,
                "pregunta_id": question["id"],
                "opcion_seleccionada": 0,  # Regular soda consumer
                "tiempo_respuesta": random.uniform(2.0, 10.0)
            })
            response.raise_for_status()
            
            # Get and answer remaining questions with preferences for sweet, sedentary lifestyle
            for i in range(5):  # 5 more questions to reach 6 total
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                data = response.json()
                
                if "pregunta" not in data:
                    print(f"❌ Alternatives Logic (Traditional): FAILED - Could not get question {i+2}")
                    self.test_results["Alternatives Logic (Traditional)"] = False
                    self.all_tests_passed = False
                    return
                    
                question = data["pregunta"]
                categoria = question.get("categoria", "")
                
                # Select options that indicate traditional preferences
                opcion = 0  # Default
                
                if categoria == "preferencias":
                    opcion = 0  # Prefer sweet
                elif categoria == "rutina":
                    opcion = 4  # Sedentary lifestyle
                
                response = requests.post(f"{API_URL}/responder", json={
                    "sesion_id": session_id,
                    "pregunta_id": question["id"],
                    "opcion_seleccionada": opcion,
                    "tiempo_respuesta": random.uniform(2.0, 10.0)
                })
                response.raise_for_status()
            
            # Get recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check if mostrar_alternativas is false
            if "mostrar_alternativas" in data:
                mostrar_alternativas = data["mostrar_alternativas"]
                print(f"✅ Alternatives Logic (Traditional): mostrar_alternativas = {mostrar_alternativas}")
                
                if not mostrar_alternativas:
                    print("✅ Alternatives Logic (Traditional): SUCCESS - Alternatives not shown for traditional user")
                    
                    # Check if criterios_alternativas explains why
                    if "criterios_alternativas" in data:
                        criterios = data["criterios_alternativas"]
                        print(f"✅ Alternatives Logic (Traditional): criterios_alternativas = {criterios}")
                        
                        if criterios and any("tradicionales" in criterio.lower() for criterio in criterios):
                            print("✅ Alternatives Logic (Traditional): SUCCESS - Criteria explains why alternatives are not shown")
                            self.test_results["Alternatives Logic (Traditional)"] = True
                        else:
                            print("❌ Alternatives Logic (Traditional): FAILED - Criteria does not explain why alternatives are not shown")
                            self.test_results["Alternatives Logic (Traditional)"] = False
                            self.all_tests_passed = False
                    else:
                        print("❌ Alternatives Logic (Traditional): FAILED - criterios_alternativas field missing")
                        self.test_results["Alternatives Logic (Traditional)"] = False
                        self.all_tests_passed = False
                else:
                    print("❌ Alternatives Logic (Traditional): FAILED - Alternatives shown for traditional user")
                    self.test_results["Alternatives Logic (Traditional)"] = False
                    self.all_tests_passed = False
            else:
                print("❌ Alternatives Logic (Traditional): FAILED - mostrar_alternativas field missing")
                self.test_results["Alternatives Logic (Traditional)"] = False
                self.all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Alternatives Logic (Traditional): FAILED - {str(e)}")
            self.test_results["Alternatives Logic (Traditional)"] = False
            self.all_tests_passed = False
    
    def test_alternatives_logic_healthy(self):
        """Test that health-conscious preferences result in showing alternatives"""
        print("\n🔍 Testing Alternatives Logic - Health-conscious User...")
        
        # Create a new session
        try:
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            data = response.json()
            
            if "sesion_id" not in data:
                print("❌ Alternatives Logic (Healthy): FAILED - Could not create session")
                self.test_results["Alternatives Logic (Healthy)"] = False
                self.all_tests_passed = False
                return
                
            session_id = data["sesion_id"]
            
            # Get initial question (about soda consumption)
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "pregunta" not in data:
                print("❌ Alternatives Logic (Healthy): FAILED - Could not get initial question")
                self.test_results["Alternatives Logic (Healthy)"] = False
                self.all_tests_passed = False
                return
                
            question = data["pregunta"]
            
            # Answer initial question - indicating moderate soda consumption (option 2)
            response = requests.post(f"{API_URL}/responder", json={
                "sesion_id": session_id,
                "pregunta_id": question["id"],
                "opcion_seleccionada": 2,  # Moderate soda consumer
                "tiempo_respuesta": random.uniform(2.0, 10.0)
            })
            response.raise_for_status()
            
            # Get and answer remaining questions with preferences for natural, active lifestyle
            for i in range(5):  # 5 more questions to reach 6 total
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                data = response.json()
                
                if "pregunta" not in data:
                    print(f"❌ Alternatives Logic (Healthy): FAILED - Could not get question {i+2}")
                    self.test_results["Alternatives Logic (Healthy)"] = False
                    self.all_tests_passed = False
                    return
                    
                question = data["pregunta"]
                categoria = question.get("categoria", "")
                
                # Select options that indicate health-conscious preferences
                opcion = 2  # Default
                
                if categoria == "preferencias":
                    opcion = 4  # Prefer natural flavors
                elif categoria == "rutina":
                    opcion = 0  # Active lifestyle
                
                response = requests.post(f"{API_URL}/responder", json={
                    "sesion_id": session_id,
                    "pregunta_id": question["id"],
                    "opcion_seleccionada": opcion,
                    "tiempo_respuesta": random.uniform(2.0, 10.0)
                })
                response.raise_for_status()
            
            # Get recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check if mostrar_alternativas is true
            if "mostrar_alternativas" in data:
                mostrar_alternativas = data["mostrar_alternativas"]
                print(f"✅ Alternatives Logic (Healthy): mostrar_alternativas = {mostrar_alternativas}")
                
                if mostrar_alternativas:
                    print("✅ Alternatives Logic (Healthy): SUCCESS - Alternatives shown for health-conscious user")
                    
                    # Check if criterios_alternativas explains why
                    if "criterios_alternativas" in data:
                        criterios = data["criterios_alternativas"]
                        print(f"✅ Alternatives Logic (Healthy): criterios_alternativas = {criterios}")
                        
                        if criterios:
                            print("✅ Alternatives Logic (Healthy): SUCCESS - Criteria explains why alternatives are shown")
                            
                            # Check if usuario_puede_ocultar is true
                            if "usuario_puede_ocultar" in data:
                                usuario_puede_ocultar = data["usuario_puede_ocultar"]
                                print(f"✅ Alternatives Logic (Healthy): usuario_puede_ocultar = {usuario_puede_ocultar}")
                                
                                if usuario_puede_ocultar:
                                    print("✅ Alternatives Logic (Healthy): SUCCESS - User can hide alternatives")
                                    self.test_results["Alternatives Logic (Healthy)"] = True
                                else:
                                    print("❌ Alternatives Logic (Healthy): FAILED - User cannot hide alternatives")
                                    self.test_results["Alternatives Logic (Healthy)"] = False
                                    self.all_tests_passed = False
                            else:
                                print("❌ Alternatives Logic (Healthy): FAILED - usuario_puede_ocultar field missing")
                                self.test_results["Alternatives Logic (Healthy)"] = False
                                self.all_tests_passed = False
                        else:
                            print("❌ Alternatives Logic (Healthy): FAILED - Empty criteria")
                            self.test_results["Alternatives Logic (Healthy)"] = False
                            self.all_tests_passed = False
                    else:
                        print("❌ Alternatives Logic (Healthy): FAILED - criterios_alternativas field missing")
                        self.test_results["Alternatives Logic (Healthy)"] = False
                        self.all_tests_passed = False
                else:
                    print("❌ Alternatives Logic (Healthy): FAILED - Alternatives not shown for health-conscious user")
                    self.test_results["Alternatives Logic (Healthy)"] = False
                    self.all_tests_passed = False
            else:
                print("❌ Alternatives Logic (Healthy): FAILED - mostrar_alternativas field missing")
                self.test_results["Alternatives Logic (Healthy)"] = False
                self.all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Alternatives Logic (Healthy): FAILED - {str(e)}")
            self.test_results["Alternatives Logic (Healthy)"] = False
            self.all_tests_passed = False
    
    def test_healthy_preferences_analysis(self):
        """Test that score_saludable is calculated correctly based on user responses"""
        print("\n🔍 Testing Healthy Preferences Analysis...")
        
        # Create a new session
        try:
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            data = response.json()
            
            if "sesion_id" not in data:
                print("❌ Healthy Preferences Analysis: FAILED - Could not create session")
                self.test_results["Healthy Preferences Analysis"] = False
                self.all_tests_passed = False
                return
                
            session_id = data["sesion_id"]
            
            # Get initial question (about soda consumption)
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "pregunta" not in data:
                print("❌ Healthy Preferences Analysis: FAILED - Could not get initial question")
                self.test_results["Healthy Preferences Analysis"] = False
                self.all_tests_passed = False
                return
                
            question = data["pregunta"]
            
            # Answer initial question - indicating NO soda consumption (option 4)
            response = requests.post(f"{API_URL}/responder", json={
                "sesion_id": session_id,
                "pregunta_id": question["id"],
                "opcion_seleccionada": 4,  # No soda consumption
                "tiempo_respuesta": random.uniform(2.0, 10.0)
            })
            response.raise_for_status()
            
            # Get and answer remaining questions with very health-conscious preferences
            for i in range(5):  # 5 more questions to reach 6 total
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                data = response.json()
                
                if "pregunta" not in data:
                    print(f"❌ Healthy Preferences Analysis: FAILED - Could not get question {i+2}")
                    self.test_results["Healthy Preferences Analysis"] = False
                    self.all_tests_passed = False
                    return
                    
                question = data["pregunta"]
                categoria = question.get("categoria", "")
                
                # Select options that indicate very health-conscious preferences
                opcion = 2  # Default
                
                if categoria == "preferencias":
                    opcion = 4  # Strongly prefer natural flavors
                elif categoria == "rutina":
                    opcion = 0  # Very active lifestyle
                elif categoria == "fisico":
                    opcion = 0  # Good physical condition
                
                response = requests.post(f"{API_URL}/responder", json={
                    "sesion_id": session_id,
                    "pregunta_id": question["id"],
                    "opcion_seleccionada": opcion,
                    "tiempo_respuesta": random.uniform(2.0, 10.0)
                })
                response.raise_for_status()
            
            # Get recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check if score_saludable is present and positive
            if "score_saludable" in data:
                score_saludable = data["score_saludable"]
                print(f"✅ Healthy Preferences Analysis: score_saludable = {score_saludable}")
                
                if score_saludable > 0:
                    print("✅ Healthy Preferences Analysis: SUCCESS - Positive health score for health-conscious user")
                    
                    # For non-soda drinkers, check if usuario_puede_ocultar is false
                    if "usuario_puede_ocultar" in data:
                        usuario_puede_ocultar = data["usuario_puede_ocultar"]
                        print(f"✅ Healthy Preferences Analysis: usuario_puede_ocultar = {usuario_puede_ocultar}")
                        
                        if not usuario_puede_ocultar:
                            print("✅ Healthy Preferences Analysis: SUCCESS - Non-soda drinker cannot hide alternatives")
                            
                            # Check if only alternatives are shown (refrescos_reales should be empty)
                            if "refrescos_reales" in data and "bebidas_alternativas" in data:
                                refrescos_count = len(data["refrescos_reales"])
                                alternativas_count = len(data["bebidas_alternativas"])
                                
                                print(f"✅ Healthy Preferences Analysis: {refrescos_count} refrescos, {alternativas_count} alternatives")
                                
                                if refrescos_count == 0 and alternativas_count > 0:
                                    print("✅ Healthy Preferences Analysis: SUCCESS - Only alternatives shown for non-soda drinker")
                                    self.test_results["Healthy Preferences Analysis"] = True
                                else:
                                    print("❌ Healthy Preferences Analysis: FAILED - Expected only alternatives for non-soda drinker")
                                    self.test_results["Healthy Preferences Analysis"] = False
                                    self.all_tests_passed = False
                            else:
                                print("❌ Healthy Preferences Analysis: FAILED - Missing refrescos_reales or bebidas_alternativas")
                                self.test_results["Healthy Preferences Analysis"] = False
                                self.all_tests_passed = False
                        else:
                            print("❌ Healthy Preferences Analysis: FAILED - Non-soda drinker can hide alternatives")
                            self.test_results["Healthy Preferences Analysis"] = False
                            self.all_tests_passed = False
                    else:
                        print("❌ Healthy Preferences Analysis: FAILED - usuario_puede_ocultar field missing")
                        self.test_results["Healthy Preferences Analysis"] = False
                        self.all_tests_passed = False
                else:
                    print("❌ Healthy Preferences Analysis: FAILED - Non-positive health score for health-conscious user")
                    self.test_results["Healthy Preferences Analysis"] = False
                    self.all_tests_passed = False
            else:
                print("❌ Healthy Preferences Analysis: FAILED - score_saludable field missing")
                self.test_results["Healthy Preferences Analysis"] = False
                self.all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Healthy Preferences Analysis: FAILED - {str(e)}")
            self.test_results["Healthy Preferences Analysis"] = False
            self.all_tests_passed = False
    
    def test_complete_response_structure(self):
        """Test that /api/recomendacion includes all the new fields"""
        print("\n🔍 Testing Complete Response Structure...")
        
        # Create a session and get to the recommendation stage
        self.session_id = self.create_session_and_answer_questions()
        if not self.session_id:
            print("❌ Complete Response Structure: FAILED - Could not create session")
            self.test_results["Complete Response Structure"] = False
            self.all_tests_passed = False
            return
        
        # Get recommendations
        try:
            response = requests.get(f"{API_URL}/recomendacion/{self.session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check for all required fields
            required_fields = [
                "refrescos_reales",
                "bebidas_alternativas",
                "mensaje_refrescos",
                "mensaje_alternativas",
                "mostrar_alternativas",
                "criterios_alternativas",
                "usuario_puede_ocultar",
                "score_saludable"
            ]
            
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ Complete Response Structure: SUCCESS - All required fields are present")
                
                # Check for logical consistency
                mostrar_alternativas = data["mostrar_alternativas"]
                usuario_puede_ocultar = data["usuario_puede_ocultar"]
                criterios = data["criterios_alternativas"]
                
                print(f"✅ Complete Response Structure: mostrar_alternativas = {mostrar_alternativas}")
                print(f"✅ Complete Response Structure: usuario_puede_ocultar = {usuario_puede_ocultar}")
                print(f"✅ Complete Response Structure: criterios_alternativas = {criterios}")
                
                # Check logical consistency
                if mostrar_alternativas and not criterios:
                    print("❌ Complete Response Structure: FAILED - mostrar_alternativas is true but criterios is empty")
                    self.test_results["Complete Response Structure"] = False
                    self.all_tests_passed = False
                elif not mostrar_alternativas and usuario_puede_ocultar:
                    print("❌ Complete Response Structure: FAILED - mostrar_alternativas is false but usuario_puede_ocultar is true")
                    self.test_results["Complete Response Structure"] = False
                    self.all_tests_passed = False
                else:
                    print("✅ Complete Response Structure: SUCCESS - Logical consistency between fields")
                    self.test_results["Complete Response Structure"] = True
            else:
                print(f"❌ Complete Response Structure: FAILED - Missing required fields: {missing_fields}")
                self.test_results["Complete Response Structure"] = False
                self.all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Complete Response Structure: FAILED - {str(e)}")
            self.test_results["Complete Response Structure"] = False
            self.all_tests_passed = False
    
    def create_session_and_answer_questions(self):
        """Helper method to create a session and answer all questions"""
        try:
            # Create session
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            data = response.json()
            
            if "sesion_id" not in data:
                return None
                
            session_id = data["sesion_id"]
            
            # Answer all questions
            self.answer_all_questions(session_id)
            
            return session_id
            
        except Exception as e:
            print(f"Error creating session and answering questions: {str(e)}")
            return None
    
    def answer_all_questions(self, session_id):
        """Answer all questions for a given session"""
        try:
            # Get initial question
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "pregunta" not in data:
                return False
                
            question = data["pregunta"]
            total_questions = data.get("total_preguntas", 6)  # Default to 6 if not specified
            
            # Answer initial question
            response = requests.post(f"{API_URL}/responder", json={
                "sesion_id": session_id,
                "pregunta_id": question["id"],
                "opcion_seleccionada": 2,  # Middle option
                "tiempo_respuesta": random.uniform(2.0, 10.0)
            })
            response.raise_for_status()
            
            # Get and answer remaining questions
            for i in range(total_questions - 1):
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                data = response.json()
                
                if "pregunta" not in data:
                    return False
                    
                question = data["pregunta"]
                
                # Answer question
                response = requests.post(f"{API_URL}/responder", json={
                    "sesion_id": session_id,
                    "pregunta_id": question["id"],
                    "opcion_seleccionada": random.randint(0, 4),
                    "tiempo_respuesta": random.uniform(2.0, 10.0)
                })
                response.raise_for_status()
            
            return True
            
        except Exception as e:
            print(f"Error answering questions: {str(e)}")
            return False
    
    def print_summary(self):
        """Print a summary of all test results"""
        print("\n" + "="*80)
        print("📊 TRANSPARENCY AND LOGIC TEST RESULTS SUMMARY")
        print("="*80)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        overall = "✅ ALL TESTS PASSED" if self.all_tests_passed else "❌ SOME TESTS FAILED"
        print("\n" + "="*80)
        print(f"🏁 OVERALL RESULT: {overall}")
        print("="*80)

if __name__ == "__main__":
    tester = RefrescoBotTransparencyTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)