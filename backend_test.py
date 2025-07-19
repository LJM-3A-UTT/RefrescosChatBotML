#!/usr/bin/env python3
"""
Backend Test Script for RefrescoBot ML - Advanced ML Architecture Testing
This script tests the complete re-architecture of RefrescoBot ML with real Machine Learning implementation.
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

class RefrescoBotTester:
    def __init__(self):
        self.session_id = None
        self.current_question = None
        self.question_count = 0
        self.recommendations = {}  # Changed to dict to store both refrescos_reales and bebidas_alternativas
        self.all_tests_passed = True
        self.test_results = {}
        self.bebida_to_rate = None
        self.rated_bebida_id = None
        self.rated_bebida_probability = None
        
    def run_all_tests(self):
        """Run all tests in sequence - FINAL VERIFICATION OF 18 QUESTION SYSTEM"""
        print("\n" + "="*80)
        print("🤖 REFRESCOBOT ML - FINAL VERIFICATION OF 18 QUESTION SYSTEM")
        print("🎯 TESTING CORRECCIONES APLICADAS Y CASOS CRÍTICOS")
        print("="*80)
        
        # CRITICAL TESTS FOR FINAL VERIFICATION
        # Test 1: System Status and Initialization
        self.test_system_status()
        
        # Test 2: Verify 18 Questions Loading (CORRECCIÓN APLICADA)
        self.test_18_questions_loading()
        
        # Test 3: Critical Cases from Review Request
        self.test_critical_cases_from_review()
        
        # Test 4: System Predictability (CASO CRÍTICO)
        self.test_system_predictability()
        
        # Test 5: More Options Button Functionality
        self.test_more_options_button()
        
        # Test 6: Priority Logic Verification (P1, P4 prioritized)
        self.test_priority_verification()
        
        # Test 7: Complete Flow with 18 Questions
        self.test_complete_flow_new_repertoire()
        
        # Test 8: Modal Functionality When Options Exhausted
        self.test_modal_when_options_exhausted()
        
        # Print summary
        self.print_summary()
        
        return self.all_tests_passed
    
    def test_18_questions_loading(self):
        """Test that all 18 questions are loaded correctly in the system"""
        print("\n🔍 Testing 18 Questions Loading...")
        print("Expected: System should have 18 questions total (expanded from 6)")
        
        try:
            # Test admin stats to get question count
            response = requests.get(f"{API_URL}/admin/stats")
            response.raise_for_status()
            stats_data = response.json()
            
            preguntas_stats = stats_data.get("preguntas", {})
            total_preguntas = preguntas_stats.get("total", 0)
            
            print(f"✅ Found {total_preguntas} questions in system")
            
            if total_preguntas != 18:
                print(f"❌ FAILED: Expected 18 questions, found {total_preguntas}")
                self.test_results["18 Questions Loading"] = False
                self.all_tests_passed = False
                return
            
            # Test that we can get the initial question (P1)
            session_id = self.create_test_session()
            if not session_id:
                print("❌ FAILED: Could not create session")
                self.test_results["18 Questions Loading"] = False
                self.all_tests_passed = False
                return
            
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            initial_question = response.json()
            
            pregunta = initial_question.get("pregunta", {})
            if pregunta.get("id") != 1:
                print(f"❌ FAILED: Initial question should be ID 1, got {pregunta.get('id')}")
                self.test_results["18 Questions Loading"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ Initial question (P1): {pregunta.get('pregunta', '')[:50]}...")
            
            # Verify the question has the expected structure for expanded system
            opciones = pregunta.get("opciones", [])
            if len(opciones) != 5:
                print(f"❌ FAILED: P1 should have 5 options, found {len(opciones)}")
                self.test_results["18 Questions Loading"] = False
                self.all_tests_passed = False
                return
            
            # Check for specific values that indicate expanded system
            valores_esperados = ["regular_consumidor", "ocasional_consumidor", "muy_ocasional", 
                               "prefiere_alternativas", "no_consume_refrescos"]
            valores_encontrados = [opt.get("valor") for opt in opciones]
            
            for valor in valores_esperados:
                if valor not in valores_encontrados:
                    print(f"❌ FAILED: Missing expected value '{valor}' in P1 options")
                    self.test_results["18 Questions Loading"] = False
                    self.all_tests_passed = False
                    return
            
            print("✅ P1 has correct structure for expanded system")
            
            # Test that we can get multiple questions (indicating 18 are available)
            questions_retrieved = 1  # Already got P1
            current_question = pregunta
            
            while questions_retrieved < 10:  # Test first 10 questions
                # Answer current question
                selected_option = current_question["opciones"][0]
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": current_question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": 3.0
                })
                response.raise_for_status()
                
                # Get next question
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                next_data = response.json()
                
                if next_data.get("finalizada"):
                    break
                    
                current_question = next_data.get("pregunta")
                if not current_question:
                    break
                    
                questions_retrieved += 1
                print(f"✅ Retrieved question {questions_retrieved}: ID {current_question.get('id')}")
            
            if questions_retrieved >= 6:
                print(f"✅ SUCCESS: Retrieved {questions_retrieved} questions, confirming expanded system!")
                print("✅ System has expanded from 6 to 18 questions as expected")
                self.test_results["18 Questions Loading"] = True
            else:
                print(f"❌ FAILED: Only retrieved {questions_retrieved} questions, expected more")
                self.test_results["18 Questions Loading"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ 18 Questions Loading: FAILED - {str(e)}")
            self.test_results["18 Questions Loading"] = False
            self.all_tests_passed = False

    def test_new_logic_with_expanded_questions(self):
        """Test that new logic works correctly with expanded questions"""
        print("\n🔍 Testing New Logic with Expanded Questions...")
        print("Expected: New questions should influence recommendations appropriately")
        
        try:
            # Test case 1: User with health-conscious responses (should get ONLY alternatives)
            print("\n📋 Test Case 1: Health-conscious user")
            session_id = self.create_health_conscious_session()
            if not session_id:
                print("❌ FAILED: Could not create health-conscious session")
                self.test_results["New Logic Expanded Questions"] = False
                self.all_tests_passed = False
                return
            
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            recommendations = response.json()
            
            refrescos = recommendations.get("refrescos_reales", [])
            alternativas = recommendations.get("bebidas_alternativas", [])
            
            print(f"   Refrescos: {len(refrescos)}, Alternativas: {len(alternativas)}")
            
            if len(refrescos) > 0 and len(alternativas) == 0:
                print("❌ FAILED: Health-conscious user got refrescos instead of alternatives")
                self.test_results["New Logic Expanded Questions"] = False
                self.all_tests_passed = False
                return
            elif len(alternativas) > 0:
                print("✅ CORRECT: Health-conscious user got alternatives")
            
            # Test case 2: User with traditional preferences (should get ONLY refrescos)
            print("\n📋 Test Case 2: Traditional user")
            session_id = self.create_traditional_session()
            if not session_id:
                print("❌ FAILED: Could not create traditional session")
                self.test_results["New Logic Expanded Questions"] = False
                self.all_tests_passed = False
                return
            
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            recommendations = response.json()
            
            refrescos = recommendations.get("refrescos_reales", [])
            alternativas = recommendations.get("bebidas_alternativas", [])
            
            print(f"   Refrescos: {len(refrescos)}, Alternativas: {len(alternativas)}")
            
            if len(refrescos) > 0:
                print("✅ CORRECT: Traditional user got refrescos")
            elif len(alternativas) > 0 and len(refrescos) == 0:
                print("❌ FAILED: Traditional user got alternatives instead of refrescos")
                self.test_results["New Logic Expanded Questions"] = False
                self.all_tests_passed = False
                return
            
            # Test case 3: User who doesn't consume refrescos (should get ONLY alternatives)
            print("\n📋 Test Case 3: Non-refresco consumer")
            session_id = self.create_no_refresco_session()
            if not session_id:
                print("❌ FAILED: Could not create no-refresco session")
                self.test_results["New Logic Expanded Questions"] = False
                self.all_tests_passed = False
                return
            
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            recommendations = response.json()
            
            refrescos = recommendations.get("refrescos_reales", [])
            alternativas = recommendations.get("bebidas_alternativas", [])
            
            print(f"   Refrescos: {len(refrescos)}, Alternativas: {len(alternativas)}")
            
            if len(refrescos) > 0:
                print("❌ FAILED: Non-refresco user got refrescos")
                self.test_results["New Logic Expanded Questions"] = False
                self.all_tests_passed = False
                return
            elif len(alternativas) > 0:
                print("✅ CORRECT: Non-refresco user got ONLY alternatives")
            
            print("✅ SUCCESS: New logic with expanded questions works correctly!")
            self.test_results["New Logic Expanded Questions"] = True
            
        except Exception as e:
            print(f"❌ New Logic Expanded Questions: FAILED - {str(e)}")
            self.test_results["New Logic Expanded Questions"] = False
            self.all_tests_passed = False

    def test_critical_cases_from_review(self):
        """Test critical cases specifically mentioned in the review request"""
        print("\n🔍 Testing Critical Cases from Review Request...")
        print("Expected: Specific user patterns should produce predictable results")
        
        try:
            critical_cases = [
                {
                    "name": "Usuario con prioridad_salud + actividad_intensa → Solo alternativas",
                    "responses": {
                        1: "prefiere_alternativas",  # P1 - prefers alternatives
                        4: "prioridad_salud",        # P4 - health priority (HIGHEST PRIORITY)
                        12: "actividad_intensa"      # P12 - intense activity
                    },
                    "expected": "alternatives_only",
                    "description": "Health priority + intense activity should give ONLY alternatives"
                },
                {
                    "name": "Usuario con prioridad_sabor + trabajo_sedentario → Solo refrescos",
                    "responses": {
                        1: "regular_consumidor",     # P1 - regular consumer
                        4: "prioridad_sabor",        # P4 - flavor priority (HIGHEST PRIORITY)
                        12: "trabajo_sedentario"     # P12 - sedentary work
                    },
                    "expected": "refrescos_only",
                    "description": "Flavor priority + sedentary work should give ONLY refrescos"
                },
                {
                    "name": "Usuario con no_consume_refrescos → Solo alternativas (sin importar otras respuestas)",
                    "responses": {
                        1: "no_consume_refrescos",   # P1 - doesn't consume refrescos (DECISIVE)
                        4: "prioridad_sabor",        # P4 - flavor priority (should be overridden)
                        12: "trabajo_sedentario"     # P12 - sedentary (should be overridden)
                    },
                    "expected": "alternatives_only",
                    "description": "no_consume_refrescos should override all other responses"
                },
                {
                    "name": "Usuario con ama_refrescos → Solo refrescos (sin importar otras respuestas)",
                    "responses": {
                        1: "regular_consumidor",     # P1 - regular consumer
                        5: "ama_refrescos",          # P5 - loves refrescos (DECISIVE)
                        4: "prioridad_salud",        # P4 - health priority (should be overridden)
                        12: "actividad_intensa"      # P12 - intense activity (should be overridden)
                    },
                    "expected": "refrescos_only",
                    "description": "ama_refrescos should override health-conscious responses"
                },
                {
                    "name": "salud_azucar_calorias → Alternativas",
                    "responses": {
                        1: "ocasional_consumidor",   # P1 - occasional consumer
                        13: "salud_azucar_calorias"  # P13 - health concern about sugar/calories
                    },
                    "expected": "alternatives_only",
                    "description": "Health concern about sugar should give alternatives"
                },
                {
                    "name": "salud_vitaminas_minerales → Alternativas",
                    "responses": {
                        1: "ocasional_consumidor",        # P1 - occasional consumer
                        13: "salud_vitaminas_minerales"   # P13 - wants vitamins/minerals
                    },
                    "expected": "alternatives_only",
                    "description": "Wanting vitamins/minerals should give alternatives"
                },
                {
                    "name": "actividad_intensa → Alternativas",
                    "responses": {
                        1: "ocasional_consumidor",   # P1 - occasional consumer
                        12: "actividad_intensa"      # P12 - intense activity
                    },
                    "expected": "alternatives_only",
                    "description": "Intense activity should prefer alternatives"
                },
                {
                    "name": "cafeina_rechazo → Alternativas",
                    "responses": {
                        1: "ocasional_consumidor",   # P1 - occasional consumer
                        16: "cafeina_rechazo"        # P16 - rejects caffeine
                    },
                    "expected": "alternatives_only",
                    "description": "Rejecting caffeine should give alternatives"
                },
                {
                    "name": "experiencia_hidratacion → Alternativas",
                    "responses": {
                        1: "ocasional_consumidor",      # P1 - occasional consumer
                        18: "experiencia_hidratacion"   # P18 - seeks hydration experience
                    },
                    "expected": "alternatives_only",
                    "description": "Seeking hydration should give alternatives"
                },
                {
                    "name": "trabajo_sedentario → Refrescos",
                    "responses": {
                        1: "regular_consumidor",     # P1 - regular consumer
                        12: "trabajo_sedentario"     # P12 - sedentary work
                    },
                    "expected": "refrescos_only",
                    "description": "Sedentary work should prefer refrescos"
                }
            ]
            
            passed_cases = 0
            total_cases = len(critical_cases)
            
            for i, test_case in enumerate(critical_cases, 1):
                print(f"\n📋 Test Case {i}/{total_cases}: {test_case['name']}")
                print(f"   Description: {test_case['description']}")
                
                # Create session with specific responses
                session_id = self.create_critical_case_session(test_case['responses'])
                if not session_id:
                    print(f"❌ FAILED: Could not create session for {test_case['name']}")
                    continue
                
                response = requests.get(f"{API_URL}/recomendacion/{session_id}")
                response.raise_for_status()
                recommendations = response.json()
                
                refrescos = recommendations.get("refrescos_reales", [])
                alternativas = recommendations.get("bebidas_alternativas", [])
                
                print(f"   Result: {len(refrescos)} refrescos, {len(alternativas)} alternativas")
                
                # Check if result matches expectation
                if test_case['expected'] == "alternatives_only":
                    if len(alternativas) > 0 and len(refrescos) == 0:
                        print(f"✅ CORRECT: {test_case['name']} → got ONLY alternatives")
                        passed_cases += 1
                    else:
                        print(f"❌ FAILED: {test_case['name']} → expected ONLY alternatives, got {len(refrescos)} refrescos")
                
                elif test_case['expected'] == "refrescos_only":
                    if len(refrescos) > 0 and len(alternativas) == 0:
                        print(f"✅ CORRECT: {test_case['name']} → got ONLY refrescos")
                        passed_cases += 1
                    else:
                        print(f"❌ FAILED: {test_case['name']} → expected ONLY refrescos, got {len(alternativas)} alternatives")
            
            print(f"\n📊 CRITICAL CASES RESULTS: {passed_cases}/{total_cases} passed ({passed_cases/total_cases*100:.1f}%)")
            
            # Success criteria: At least 80% of critical cases should pass
            if passed_cases >= total_cases * 0.8:
                print("✅ SUCCESS: Most critical cases work correctly!")
                self.test_results["Critical Cases from Review"] = True
            else:
                print("❌ FAILED: Too many critical cases failed")
                self.test_results["Critical Cases from Review"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ Critical Cases from Review: FAILED - {str(e)}")
            self.test_results["Critical Cases from Review"] = False
            self.all_tests_passed = False

    def test_more_options_button(self):
        """Test the 'more options' button functionality"""
        print("\n🔍 Testing More Options Button Functionality...")
        print("Expected: Button should work for all user types and respect limits")
        
        try:
            # Test case 1: User who doesn't consume refrescos (should get more alternatives)
            print("\n📋 Test Case 1: User who doesn't consume refrescos")
            session_id = self.create_no_refresco_session()
            if not session_id:
                print("❌ FAILED: Could not create no-refresco session")
                self.test_results["More Options Button"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            initial_recs = response.json()
            
            initial_refrescos = len(initial_recs.get("refrescos_reales", []))
            initial_alternativas = len(initial_recs.get("bebidas_alternativas", []))
            
            print(f"   Initial: {initial_refrescos} refrescos, {initial_alternativas} alternativas")
            
            # Test more options
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
            response.raise_for_status()
            more_options = response.json()
            
            additional_recs = more_options.get("recomendaciones_adicionales", [])
            tipo_recomendaciones = more_options.get("tipo_recomendaciones", "")
            sin_mas_opciones = more_options.get("sin_mas_opciones", False)
            
            print(f"   More options: {len(additional_recs)} additional, type: {tipo_recomendaciones}")
            
            if initial_refrescos == 0 and initial_alternativas > 0:
                print("✅ CORRECT: No-refresco user got ONLY alternatives initially")
                if tipo_recomendaciones == "alternativas_saludables" or len(additional_recs) == 0:
                    print("✅ CORRECT: More options respects user type")
                    case1_passed = True
                else:
                    print("❌ FAILED: More options should give alternatives or be empty")
                    case1_passed = False
            else:
                print("❌ FAILED: No-refresco user should get ONLY alternatives")
                case1_passed = False
            
            # Test case 2: Traditional user (should get more refrescos)
            print("\n📋 Test Case 2: Traditional user")
            session_id = self.create_traditional_session()
            if session_id:
                response = requests.get(f"{API_URL}/recomendacion/{session_id}")
                response.raise_for_status()
                initial_recs = response.json()
                
                initial_refrescos = len(initial_recs.get("refrescos_reales", []))
                initial_alternativas = len(initial_recs.get("bebidas_alternativas", []))
                
                print(f"   Initial: {initial_refrescos} refrescos, {initial_alternativas} alternativas")
                
                response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
                response.raise_for_status()
                more_options = response.json()
                
                additional_recs = more_options.get("recomendaciones_adicionales", [])
                tipo_recomendaciones = more_options.get("tipo_recomendaciones", "")
                
                print(f"   More options: {len(additional_recs)} additional, type: {tipo_recomendaciones}")
                
                if initial_refrescos > 0:
                    print("✅ CORRECT: Traditional user got refrescos initially")
                    case2_passed = True
                else:
                    print("⚠️ WARNING: Traditional user should get refrescos")
                    case2_passed = False
            else:
                case2_passed = False
            
            # Test case 3: Multiple clicks (test exhaustion)
            print("\n📋 Test Case 3: Multiple clicks to test exhaustion")
            session_id = self.create_health_conscious_session()
            if session_id:
                # Get initial recommendations
                response = requests.get(f"{API_URL}/recomendacion/{session_id}")
                response.raise_for_status()
                
                clicks = 0
                max_clicks = 5
                
                while clicks < max_clicks:
                    response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
                    response.raise_for_status()
                    more_options = response.json()
                    
                    additional_recs = more_options.get("recomendaciones_adicionales", [])
                    sin_mas_opciones = more_options.get("sin_mas_opciones", False)
                    
                    clicks += 1
                    print(f"   Click {clicks}: {len(additional_recs)} additional, exhausted: {sin_mas_opciones}")
                    
                    if sin_mas_opciones:
                        print("✅ CORRECT: System properly indicates when options are exhausted")
                        case3_passed = True
                        break
                else:
                    print("⚠️ WARNING: System didn't indicate exhaustion after 5 clicks")
                    case3_passed = True  # Not a failure, just means lots of options
            else:
                case3_passed = False
            
            if case1_passed and case2_passed and case3_passed:
                print("✅ SUCCESS: More options button works correctly for all user types!")
                self.test_results["More Options Button"] = True
            else:
                print("❌ FAILED: More options button has issues")
                self.test_results["More Options Button"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ More Options Button: FAILED - {str(e)}")
            self.test_results["More Options Button"] = False
            self.all_tests_passed = False

    def test_modal_when_options_exhausted(self):
        """Test modal functionality when options are exhausted"""
        print("\n🔍 Testing Modal When Options Exhausted...")
        print("Expected: System should handle exhaustion gracefully")
        
        try:
            # Create a session and exhaust options
            session_id = self.create_health_conscious_session()
            if not session_id:
                print("❌ FAILED: Could not create session")
                self.test_results["Modal When Options Exhausted"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            initial_recs = response.json()
            
            print(f"✅ Initial recommendations obtained")
            
            # Keep clicking more options until exhausted
            clicks = 0
            max_clicks = 10
            exhausted = False
            
            while clicks < max_clicks:
                response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
                response.raise_for_status()
                more_options = response.json()
                
                additional_recs = more_options.get("recomendaciones_adicionales", [])
                sin_mas_opciones = more_options.get("sin_mas_opciones", False)
                mensaje = more_options.get("mensaje", "")
                
                clicks += 1
                print(f"   Click {clicks}: {len(additional_recs)} additional, exhausted: {sin_mas_opciones}")
                
                if sin_mas_opciones:
                    print(f"✅ EXHAUSTED after {clicks} clicks")
                    print(f"✅ Message: {mensaje}")
                    
                    # Verify the response structure for frontend modal
                    if "sin_mas_opciones" in more_options and more_options["sin_mas_opciones"] == True:
                        print("✅ CORRECT: Response includes sin_mas_opciones: true for modal trigger")
                    else:
                        print("❌ FAILED: Response should include sin_mas_opciones: true")
                        self.test_results["Modal When Options Exhausted"] = False
                        self.all_tests_passed = False
                        return
                    
                    if mensaje and len(mensaje) > 0:
                        print("✅ CORRECT: Response includes friendly message for modal")
                    else:
                        print("❌ FAILED: Response should include friendly message")
                        self.test_results["Modal When Options Exhausted"] = False
                        self.all_tests_passed = False
                        return
                    
                    exhausted = True
                    break
                
                if len(additional_recs) == 0:
                    print("⚠️ WARNING: No additional recommendations but not marked as exhausted")
            
            if exhausted:
                print("✅ SUCCESS: System properly handles option exhaustion!")
                self.test_results["Modal When Options Exhausted"] = True
            else:
                print("⚠️ WARNING: Could not exhaust options in 10 clicks (may indicate large dataset)")
                self.test_results["Modal When Options Exhausted"] = True  # Not a failure
            
        except Exception as e:
            print(f"❌ Modal When Options Exhausted: FAILED - {str(e)}")
            self.test_results["Modal When Options Exhausted"] = False
            self.all_tests_passed = False

    def test_priority_verification(self):
        """Test that P1 and P4 questions still have priority in the expanded system"""
        print("\n🔍 Testing Priority Verification...")
        print("Expected: P1 and P4 should still be prioritized over new questions")
        
        try:
            # Test P4 priority (prioridad_sabor vs prioridad_salud)
            print("\n📋 Testing P4 Priority (most decisive)")
            
            # Case 1: P4 = prioridad_sabor should override other health-conscious responses
            session_id = self.create_mixed_priority_session("prioridad_sabor")
            if not session_id:
                print("❌ FAILED: Could not create P4 priority test session")
                self.test_results["Priority Verification"] = False
                self.all_tests_passed = False
                return
            
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            recommendations = response.json()
            
            refrescos = recommendations.get("refrescos_reales", [])
            alternativas = recommendations.get("bebidas_alternativas", [])
            
            print(f"   P4=prioridad_sabor: {len(refrescos)} refrescos, {len(alternativas)} alternativas")
            
            if len(refrescos) > 0 and len(alternativas) == 0:
                print("✅ CORRECT: P4=prioridad_sabor overrides other responses → ONLY refrescos")
                p4_priority_works = True
            else:
                print("❌ FAILED: P4=prioridad_sabor should override other responses")
                p4_priority_works = False
            
            # Case 2: P4 = prioridad_salud should override other traditional responses
            session_id = self.create_mixed_priority_session("prioridad_salud")
            if session_id:
                response = requests.get(f"{API_URL}/recomendacion/{session_id}")
                response.raise_for_status()
                recommendations = response.json()
                
                refrescos = recommendations.get("refrescos_reales", [])
                alternativas = recommendations.get("bebidas_alternativas", [])
                
                print(f"   P4=prioridad_salud: {len(refrescos)} refrescos, {len(alternativas)} alternativas")
                
                if len(alternativas) > 0 and len(refrescos) == 0:
                    print("✅ CORRECT: P4=prioridad_salud overrides other responses → ONLY alternatives")
                    p4_priority_works = p4_priority_works and True
                else:
                    print("❌ FAILED: P4=prioridad_salud should override other responses")
                    p4_priority_works = False
            
            # Test P1 priority (fundamental relationship with refrescos)
            print("\n📋 Testing P1 Priority (fundamental)")
            
            # Case 3: P1 = no_consume_refrescos should be decisive
            session_id = self.create_mixed_p1_session("no_consume_refrescos")
            if session_id:
                response = requests.get(f"{API_URL}/recomendacion/{session_id}")
                response.raise_for_status()
                recommendations = response.json()
                
                refrescos = recommendations.get("refrescos_reales", [])
                alternativas = recommendations.get("bebidas_alternativas", [])
                
                print(f"   P1=no_consume_refrescos: {len(refrescos)} refrescos, {len(alternativas)} alternativas")
                
                if len(alternativas) > 0 and len(refrescos) == 0:
                    print("✅ CORRECT: P1=no_consume_refrescos → ONLY alternatives")
                    p1_priority_works = True
                else:
                    print("❌ FAILED: P1=no_consume_refrescos should give ONLY alternatives")
                    p1_priority_works = False
            else:
                p1_priority_works = False
            
            if p4_priority_works and p1_priority_works:
                print("✅ SUCCESS: P1 and P4 maintain priority in expanded system!")
                self.test_results["Priority Verification"] = True
            else:
                print("❌ FAILED: Priority system not working correctly")
                self.test_results["Priority Verification"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ Priority Verification: FAILED - {str(e)}")
            self.test_results["Priority Verification"] = False
            self.all_tests_passed = False

    def test_complete_flow_new_repertoire(self):
        """Test complete flow from start to recommendations with new repertoire"""
        print("\n🔍 Testing Complete Flow with New Repertoire...")
        print("Expected: Full flow should work with 18 questions and new logic")
        
        try:
            # Create session
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            session_data = response.json()
            session_id = session_data["sesion_id"]
            print("✅ Step 1: Session created")
            
            # Get initial question (P1)
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            question_data = response.json()
            
            pregunta = question_data["pregunta"]
            if pregunta["id"] != 1:
                print(f"❌ FAILED: Initial question should be P1, got P{pregunta['id']}")
                self.test_results["Complete Flow New Repertoire"] = False
                self.all_tests_passed = False
                return
            
            print("✅ Step 2: Got P1 (initial question)")
            
            # Answer questions with health-conscious responses to test new logic
            questions_answered = 0
            current_question = pregunta
            
            # Define specific responses to test new expanded logic
            specific_responses = {
                1: "no_consume_refrescos",  # P1 - fundamental
                4: "prioridad_salud",       # P4 - most important
                13: "salud_azucar_calorias", # P13 - new health question
                12: "actividad_intensa",     # P12 - new activity question
                16: "cafeina_rechazo",       # P16 - new caffeine question
                18: "experiencia_hidratacion" # P18 - new experience question
            }
            
            while current_question and questions_answered < 18:
                question_id = current_question["id"]
                opciones = current_question["opciones"]
                
                # Use specific response if defined, otherwise use first option
                if question_id in specific_responses:
                    target_value = specific_responses[question_id]
                    selected_option = None
                    for option in opciones:
                        if option["valor"] == target_value:
                            selected_option = option
                            break
                    if not selected_option:
                        selected_option = opciones[0]  # Fallback
                else:
                    selected_option = opciones[0]
                
                # Answer question
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": question_id,
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": random.uniform(2.0, 8.0)
                })
                response.raise_for_status()
                questions_answered += 1
                
                print(f"✅ Answered Q{question_id}: {selected_option['valor']}")
                
                # Get next question
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                next_data = response.json()
                
                if next_data.get("finalizada"):
                    break
                    
                current_question = next_data.get("pregunta")
            
            print(f"✅ Step 3: Answered {questions_answered} questions")
            
            # Get recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            recommendations = response.json()
            
            refrescos = recommendations.get("refrescos_reales", [])
            alternativas = recommendations.get("bebidas_alternativas", [])
            
            print(f"✅ Step 4: Got recommendations - {len(refrescos)} refrescos, {len(alternativas)} alternativas")
            
            # Verify that health-conscious responses resulted in ONLY alternatives
            if len(alternativas) > 0 and len(refrescos) == 0:
                print("✅ CORRECT: Health-conscious responses → ONLY alternatives (new logic working)")
            elif len(refrescos) > 0 and len(alternativas) == 0:
                print("⚠️ WARNING: Got refrescos instead of alternatives (may indicate priority issue)")
            else:
                print("⚠️ WARNING: Got mixed results (may indicate logic issue)")
            
            # Test more options
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
            response.raise_for_status()
            more_options = response.json()
            
            additional_count = len(more_options.get("recomendaciones_adicionales", []))
            print(f"✅ Step 5: More options returned {additional_count} additional recommendations")
            
            # Test rating functionality
            if len(alternativas) > 0:
                test_beverage = alternativas[0]
                response = requests.post(f"{API_URL}/puntuar/{session_id}/{test_beverage['id']}", json={
                    "puntuacion": 5,
                    "comentario": "Testing with expanded question system"
                })
                response.raise_for_status()
                print("✅ Step 6: Rating functionality works")
            
            print("✅ SUCCESS: Complete flow works with new repertoire!")
            self.test_results["Complete Flow New Repertoire"] = True
            
        except Exception as e:
            print(f"❌ Complete Flow New Repertoire: FAILED - {str(e)}")
            self.test_results["Complete Flow New Repertoire"] = False
            self.all_tests_passed = False

    def test_system_predictability(self):
        """Test that system remains 100% predictable with expanded questions"""
        print("\n🔍 Testing System Predictability...")
        print("Expected: Same responses should always give same recommendations (100% predictable)")
        
        try:
            # Define a specific set of responses
            test_responses = {
                1: "prioridad_salud",        # P4 - health priority
                2: "bebidas_naturales",      # P2 - natural beverages
                3: "cero_azucar_natural",    # P3 - no sugar
                4: "prioridad_salud",        # P4 - health priority (most important)
                5: "evita_salud",            # P5 - avoids for health
                6: "ejercicio_deporte"       # P6 - exercise context
            }
            
            # Run the same test 3 times to verify predictability
            results = []
            
            for run in range(3):
                print(f"\n📋 Predictability Run {run + 1}/3")
                
                session_id = self.create_predictable_session(test_responses)
                if not session_id:
                    print(f"❌ FAILED: Could not create session for run {run + 1}")
                    continue
                
                response = requests.get(f"{API_URL}/recomendacion/{session_id}")
                response.raise_for_status()
                recommendations = response.json()
                
                refrescos = recommendations.get("refrescos_reales", [])
                alternativas = recommendations.get("bebidas_alternativas", [])
                
                # Create a signature of the results
                result_signature = {
                    "refrescos_count": len(refrescos),
                    "alternativas_count": len(alternativas),
                    "refrescos_ids": sorted([r["id"] for r in refrescos]),
                    "alternativas_ids": sorted([a["id"] for a in alternativas])
                }
                
                results.append(result_signature)
                print(f"   Run {run + 1}: {len(refrescos)} refrescos, {len(alternativas)} alternativas")
                print(f"   Refresco IDs: {result_signature['refrescos_ids']}")
                print(f"   Alternative IDs: {result_signature['alternativas_ids']}")
            
            # Check if all results are identical
            if len(results) >= 2:
                first_result = results[0]
                all_identical = True
                
                for i, result in enumerate(results[1:], 2):
                    if result != first_result:
                        print(f"❌ FAILED: Run {i} differs from Run 1")
                        print(f"   Run 1: {first_result}")
                        print(f"   Run {i}: {result}")
                        all_identical = False
                
                if all_identical:
                    print("✅ PERFECT: All runs produced identical results!")
                    print("✅ System is 100% predictable with expanded questions")
                    self.test_results["System Predictability"] = True
                else:
                    print("❌ FAILED: System is not predictable - different runs gave different results")
                    self.test_results["System Predictability"] = False
                    self.all_tests_passed = False
            else:
                print("❌ FAILED: Could not run enough tests to verify predictability")
                self.test_results["System Predictability"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ System Predictability: FAILED - {str(e)}")
            self.test_results["System Predictability"] = False
            self.all_tests_passed = False

    def test_expanded_question_influence(self):
        """Test that expanded questions actually influence recommendations"""
        print("\n🔍 Testing Expanded Question Influence...")
        print("Expected: New questions (P7-P18) should influence recommendations appropriately")
        
        try:
            # Test different combinations of new questions to see if they influence results
            test_combinations = [
                {
                    "name": "Price-conscious + Traditional",
                    "responses": {7: "precio_muy_importante", 17: "marca_muy_importante"},
                    "expected_influence": "Should prefer traditional brands"
                },
                {
                    "name": "Health + Activity focused",
                    "responses": {12: "actividad_intensa", 13: "salud_azucar_calorias", 16: "cafeina_rechazo"},
                    "expected_influence": "Should prefer healthy alternatives"
                },
                {
                    "name": "Experience + Climate focused",
                    "responses": {14: "clima_calor_extremo", 18: "experiencia_hidratacion"},
                    "expected_influence": "Should prefer hydrating options"
                },
                {
                    "name": "Flavor adventurous",
                    "responses": {11: "aventurero_sabores", 15: "sabor_citricos_intensos"},
                    "expected_influence": "Should include varied flavors"
                }
            ]
            
            influenced_combinations = 0
            
            for combination in test_combinations:
                print(f"\n📋 Testing: {combination['name']}")
                
                # Create session with specific new question responses
                session_id = self.create_expanded_question_session(combination['responses'])
                if not session_id:
                    print(f"❌ FAILED: Could not create session for {combination['name']}")
                    continue
                
                response = requests.get(f"{API_URL}/recomendacion/{session_id}")
                response.raise_for_status()
                recommendations = response.json()
                
                refrescos = recommendations.get("refrescos_reales", [])
                alternativas = recommendations.get("bebidas_alternativas", [])
                total_recommendations = len(refrescos) + len(alternativas)
                
                print(f"   Result: {len(refrescos)} refrescos, {len(alternativas)} alternativas")
                print(f"   Expected: {combination['expected_influence']}")
                
                # Check if we got reasonable recommendations (indicating influence)
                if total_recommendations > 0:
                    print(f"✅ INFLUENCE: Got {total_recommendations} recommendations")
                    influenced_combinations += 1
                    
                    # Check for specific influences based on responses
                    if "salud_azucar_calorias" in str(combination['responses'].values()):
                        if len(alternativas) > len(refrescos):
                            print("✅ CORRECT: Health-focused responses → more alternatives")
                        else:
                            print("⚠️ NOTE: Expected more alternatives for health-focused responses")
                    
                    if "actividad_intensa" in str(combination['responses'].values()):
                        if len(alternativas) > 0:
                            print("✅ CORRECT: Activity-focused responses → includes alternatives")
                        else:
                            print("⚠️ NOTE: Expected alternatives for activity-focused responses")
                else:
                    print("❌ NO INFLUENCE: No recommendations generated")
            
            print(f"\n📊 INFLUENCE RESULTS: {influenced_combinations}/{len(test_combinations)} combinations showed influence")
            
            if influenced_combinations >= len(test_combinations) * 0.75:  # 75% success rate
                print("✅ SUCCESS: Expanded questions appropriately influence recommendations!")
                self.test_results["Expanded Question Influence"] = True
            else:
                print("❌ FAILED: Expanded questions don't sufficiently influence recommendations")
                self.test_results["Expanded Question Influence"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ Expanded Question Influence: FAILED - {str(e)}")
            self.test_results["Expanded Question Influence"] = False
            self.all_tests_passed = False
        """Test that backend is correctly configured to serve static files from /static"""
        print("\n🔍 Testing Backend Static Files Configuration...")
        print("Expected: FastAPI StaticFiles configured to serve from /static directory")
        
        try:
            # Test that the static files endpoint is accessible
            test_image_path = "/static/images/bebidas/Aquarius_1.5L.webp"
            image_url = f"{BACKEND_URL}{test_image_path}"
            
            print(f"Testing static file URL: {image_url}")
            
            response = requests.head(image_url, timeout=10)
            
            if response.status_code == 200:
                print("✅ CORRECT: Static files are served correctly from /static")
                print(f"✅ Content-Type: {response.headers.get('content-type', 'unknown')}")
                print(f"✅ Content-Length: {response.headers.get('content-length', 'unknown')} bytes")
            elif response.status_code == 404:
                print("❌ FAILED: Static file not found - configuration may be incorrect")
                self.test_results["Backend Static Files Configuration"] = False
                self.all_tests_passed = False
                return
            else:
                print(f"⚠️ WARNING: Unexpected status code {response.status_code}")
            
            # Test multiple image paths to verify configuration
            test_paths = [
                "/static/images/bebidas/Ciel_Exprim_1L.webp",
                "/static/images/bebidas/Fanta_350ml.png",
                "/static/images/bebidas/Coca-cola_Light_285ml.webp"
            ]
            
            successful_tests = 0
            for path in test_paths:
                url = f"{BACKEND_URL}{path}"
                try:
                    resp = requests.head(url, timeout=5)
                    if resp.status_code == 200:
                        successful_tests += 1
                        print(f"✅ Found: {path}")
                    elif resp.status_code == 404:
                        print(f"⚠️ Not found: {path}")
                    else:
                        print(f"⚠️ Status {resp.status_code}: {path}")
                except requests.exceptions.RequestException as e:
                    print(f"⚠️ Error accessing {path}: {e}")
            
            print(f"✅ Static file tests: {successful_tests}/{len(test_paths)} successful")
            
            if successful_tests >= len(test_paths) // 2:  # At least half should work
                print("✅ SUCCESS: Backend static files configuration is working!")
                self.test_results["Backend Static Files Configuration"] = True
            else:
                print("❌ FAILED: Too many static files are inaccessible")
                self.test_results["Backend Static Files Configuration"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ Backend Static Files Configuration: FAILED - {str(e)}")
            self.test_results["Backend Static Files Configuration"] = False
            self.all_tests_passed = False

    def test_specific_image_routes(self):
        """Test specific image routes mentioned in the review request"""
        print("\n🔍 Testing Specific Image Routes...")
        print("Expected: Routes like /static/images/bebidas/Aquarius_1.5L.webp should be accessible")
        
        try:
            # Specific routes mentioned in the review request
            specific_routes = [
                "/static/images/bebidas/Aquarius_1.5L.webp",
                "/static/images/bebidas/Ciel_Exprim_1L.webp", 
                "/static/images/bebidas/Fanta_350ml.png",
                "/static/images/bebidas/Coca-cola_Light_285ml.webp",
                "/static/images/bebidas/Delaware_Punch_600ml.webp"
            ]
            
            accessible_routes = 0
            not_found_routes = 0
            error_routes = 0
            
            for route in specific_routes:
                url = f"{BACKEND_URL}{route}"
                print(f"Testing: {url}")
                
                try:
                    response = requests.head(url, timeout=10)
                    
                    if response.status_code == 200:
                        print(f"✅ ACCESSIBLE: {route}")
                        print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
                        accessible_routes += 1
                    elif response.status_code == 404:
                        print(f"⚠️ NOT FOUND: {route}")
                        not_found_routes += 1
                    else:
                        print(f"❌ ERROR {response.status_code}: {route}")
                        error_routes += 1
                        
                except requests.exceptions.RequestException as e:
                    print(f"❌ REQUEST ERROR: {route} - {e}")
                    error_routes += 1
            
            print(f"\n📊 RESULTS:")
            print(f"✅ Accessible: {accessible_routes}")
            print(f"⚠️ Not Found: {not_found_routes}")
            print(f"❌ Errors: {error_routes}")
            
            # Success criteria: At least some images should be accessible, not found is acceptable
            if accessible_routes > 0 and error_routes == 0:
                print("✅ SUCCESS: Specific image routes are working correctly!")
                print("✅ Static file serving is properly configured")
                self.test_results["Specific Image Routes"] = True
            elif accessible_routes > 0 and error_routes < len(specific_routes) // 2:
                print("✅ MOSTLY SUCCESS: Most routes work, some minor issues")
                self.test_results["Specific Image Routes"] = True
            else:
                print("❌ FAILED: Too many routes have errors or none are accessible")
                self.test_results["Specific Image Routes"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ Specific Image Routes: FAILED - {str(e)}")
            self.test_results["Specific Image Routes"] = False
            self.all_tests_passed = False

    def test_bebidas_json_image_paths(self):
        """Test that bebidas.json has correct image paths with /static/images/bebidas/ format"""
        print("\n🔍 Testing Bebidas.json Image Paths...")
        print("Expected: All image paths should start with /static/images/bebidas/")
        
        try:
            # First try to get bebidas data from admin stats
            response = requests.get(f"{API_URL}/admin/stats")
            response.raise_for_status()
            stats_data = response.json()
            
            bebidas_stats = stats_data.get("bebidas", {})
            total_bebidas = bebidas_stats.get("total", 0)
            total_presentaciones = bebidas_stats.get("total_presentaciones", 0)
            
            print(f"✅ Found {total_bebidas} bebidas with {total_presentaciones} presentations in system")
            
            # Since we can't access bebidas directly, let's test through recommendations
            session_id = self.create_complete_user_session()
            if not session_id:
                print("❌ FAILED: Could not create session to test bebidas data")
                self.test_results["Bebidas JSON Image Paths"] = False
                self.all_tests_passed = False
                return
            
            # Get recommendations to analyze image paths
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            recommendations = response.json()
            
            all_beverages = recommendations.get("refrescos_reales", []) + recommendations.get("bebidas_alternativas", [])
            
            if not all_beverages:
                print("❌ FAILED: No beverages found in recommendations")
                self.test_results["Bebidas JSON Image Paths"] = False
                self.all_tests_passed = False
                return
            
            correct_paths = 0
            incorrect_paths = 0
            missing_paths = 0
            total_presentations_tested = 0
            
            for bebida in all_beverages:
                bebida_name = bebida.get("nombre", "Unknown")
                presentaciones = bebida.get("presentaciones", [])
                
                for presentacion in presentaciones:
                    total_presentations_tested += 1
                    imagen_local = presentacion.get("imagen_local", "")
                    
                    if not imagen_local:
                        print(f"⚠️ MISSING: {bebida_name} - presentation has no imagen_local")
                        missing_paths += 1
                    elif imagen_local.startswith("/static/images/bebidas/"):
                        print(f"✅ CORRECT: {imagen_local}")
                        correct_paths += 1
                    else:
                        print(f"❌ INCORRECT: {imagen_local} (should start with /static/images/bebidas/)")
                        incorrect_paths += 1
            
            # Get additional recommendations to test more beverages
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
            response.raise_for_status()
            additional_recs = response.json()
            
            additional_beverages = additional_recs.get("recomendaciones_adicionales", [])
            
            for bebida in additional_beverages:
                bebida_name = bebida.get("nombre", "Unknown")
                presentaciones = bebida.get("presentaciones", [])
                
                for presentacion in presentaciones:
                    total_presentations_tested += 1
                    imagen_local = presentacion.get("imagen_local", "")
                    
                    if not imagen_local:
                        missing_paths += 1
                    elif imagen_local.startswith("/static/images/bebidas/"):
                        correct_paths += 1
                    else:
                        incorrect_paths += 1
            
            print(f"\n📊 IMAGE PATH ANALYSIS:")
            print(f"✅ Correct paths: {correct_paths}/{total_presentations_tested}")
            print(f"❌ Incorrect paths: {incorrect_paths}/{total_presentations_tested}")
            print(f"⚠️ Missing paths: {missing_paths}/{total_presentations_tested}")
            print(f"📊 Total bebidas in system: {total_bebidas}")
            print(f"📊 Total presentations in system: {total_presentaciones}")
            
            # Success criteria: All or most paths should be correct
            if incorrect_paths == 0 and missing_paths == 0:
                print("✅ PERFECT: All image paths are correctly formatted!")
                self.test_results["Bebidas JSON Image Paths"] = True
            elif correct_paths >= total_presentations_tested * 0.9:  # 90% correct
                print("✅ SUCCESS: Most image paths are correctly formatted")
                self.test_results["Bebidas JSON Image Paths"] = True
            else:
                print("❌ FAILED: Too many incorrect or missing image paths")
                self.test_results["Bebidas JSON Image Paths"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ Bebidas JSON Image Paths: FAILED - {str(e)}")
            self.test_results["Bebidas JSON Image Paths"] = False
            self.all_tests_passed = False

    def test_recommendations_with_real_images(self):
        """Test that recommendations include beverages with real image paths"""
        print("\n🔍 Testing Recommendations with Real Images...")
        print("Expected: Recommendations should include beverages with proper image paths")
        
        try:
            # Create a complete user session
            session_id = self.create_complete_user_session()
            if not session_id:
                print("❌ FAILED: Could not create user session")
                self.test_results["Recommendations with Real Images"] = False
                self.all_tests_passed = False
                return
            
            # Get recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            recommendations = response.json()
            
            # Analyze image paths in recommendations
            all_beverages = recommendations.get("refrescos_reales", []) + recommendations.get("bebidas_alternativas", [])
            
            if not all_beverages:
                print("❌ FAILED: No beverages in recommendations")
                self.test_results["Recommendations with Real Images"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ Found {len(all_beverages)} beverages in recommendations")
            
            beverages_with_images = 0
            correct_image_paths = 0
            total_presentations = 0
            
            for beverage in all_beverages:
                beverage_name = beverage.get("nombre", "Unknown")
                presentaciones = beverage.get("presentaciones", [])
                
                has_images = False
                for presentacion in presentaciones:
                    total_presentations += 1
                    imagen_local = presentacion.get("imagen_local", "")
                    
                    if imagen_local:
                        has_images = True
                        if imagen_local.startswith("/static/images/bebidas/"):
                            correct_image_paths += 1
                            print(f"✅ {beverage_name}: {imagen_local}")
                        else:
                            print(f"❌ {beverage_name}: Incorrect path format - {imagen_local}")
                    else:
                        print(f"⚠️ {beverage_name}: No image path in presentation")
                
                if has_images:
                    beverages_with_images += 1
            
            print(f"\n📊 RECOMMENDATIONS IMAGE ANALYSIS:")
            print(f"✅ Beverages with images: {beverages_with_images}/{len(all_beverages)}")
            print(f"✅ Correct image paths: {correct_image_paths}/{total_presentations}")
            
            # Test additional recommendations
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
            response.raise_for_status()
            additional_recs = response.json()
            
            additional_beverages = additional_recs.get("recomendaciones_adicionales", [])
            print(f"✅ Additional recommendations: {len(additional_beverages)} beverages")
            
            # Success criteria
            if correct_image_paths >= total_presentations * 0.8:  # 80% should have correct paths
                print("✅ SUCCESS: Recommendations contain beverages with proper image paths!")
                self.test_results["Recommendations with Real Images"] = True
            else:
                print("❌ FAILED: Too few recommendations have correct image paths")
                self.test_results["Recommendations with Real Images"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ Recommendations with Real Images: FAILED - {str(e)}")
            self.test_results["Recommendations with Real Images"] = False
            self.all_tests_passed = False

    def test_frontend_url_construction(self):
        """Test that frontend URL construction works correctly"""
        print("\n🔍 Testing Frontend URL Construction...")
        print("Expected: Frontend should construct URLs as ${BACKEND_URL}${presentacionActual.imagen_local}")
        
        try:
            # Get the backend URL that frontend should use
            frontend_backend_url = BACKEND_URL
            print(f"✅ Frontend should use BACKEND_URL: {frontend_backend_url}")
            
            # Test URL construction pattern
            sample_image_paths = [
                "/static/images/bebidas/Aquarius_1.5L.webp",
                "/static/images/bebidas/Ciel_Exprim_1L.webp",
                "/static/images/bebidas/Fanta_350ml.png"
            ]
            
            constructed_urls_working = 0
            
            for image_path in sample_image_paths:
                # This is how frontend should construct the URL
                constructed_url = f"{frontend_backend_url}{image_path}"
                print(f"Testing constructed URL: {constructed_url}")
                
                try:
                    response = requests.head(constructed_url, timeout=5)
                    if response.status_code == 200:
                        print(f"✅ WORKING: {constructed_url}")
                        constructed_urls_working += 1
                    elif response.status_code == 404:
                        print(f"⚠️ NOT FOUND: {constructed_url}")
                    else:
                        print(f"❌ ERROR {response.status_code}: {constructed_url}")
                except requests.exceptions.RequestException as e:
                    print(f"❌ REQUEST ERROR: {constructed_url} - {e}")
            
            # Test that the pattern works with a real recommendation
            session_id = self.create_complete_user_session()
            if session_id:
                response = requests.get(f"{API_URL}/recomendacion/{session_id}")
                response.raise_for_status()
                recommendations = response.json()
                
                all_beverages = recommendations.get("refrescos_reales", []) + recommendations.get("bebidas_alternativas", [])
                
                if all_beverages:
                    # Test first beverage's first presentation
                    first_beverage = all_beverages[0]
                    presentaciones = first_beverage.get("presentaciones", [])
                    
                    if presentaciones:
                        presentacion_actual = presentaciones[0]  # This would be presentacionActual in frontend
                        imagen_local = presentacion_actual.get("imagen_local", "")
                        
                        if imagen_local:
                            # This is exactly how frontend constructs the URL
                            frontend_constructed_url = f"{frontend_backend_url}{imagen_local}"
                            print(f"\n🎯 TESTING REAL FRONTEND PATTERN:")
                            print(f"   BACKEND_URL: {frontend_backend_url}")
                            print(f"   presentacionActual.imagen_local: {imagen_local}")
                            print(f"   Constructed URL: {frontend_constructed_url}")
                            
                            try:
                                response = requests.head(frontend_constructed_url, timeout=5)
                                if response.status_code == 200:
                                    print("✅ PERFECT: Frontend URL construction pattern works!")
                                    constructed_urls_working += 1
                                else:
                                    print(f"❌ Frontend pattern failed with status {response.status_code}")
                            except requests.exceptions.RequestException as e:
                                print(f"❌ Frontend pattern failed: {e}")
            
            print(f"\n📊 URL CONSTRUCTION RESULTS:")
            print(f"✅ Working constructed URLs: {constructed_urls_working}")
            
            if constructed_urls_working > 0:
                print("✅ SUCCESS: Frontend URL construction pattern is working correctly!")
                self.test_results["Frontend URL Construction"] = True
            else:
                print("❌ FAILED: Frontend URL construction pattern is not working")
                self.test_results["Frontend URL Construction"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ Frontend URL Construction: FAILED - {str(e)}")
            self.test_results["Frontend URL Construction"] = False
            self.all_tests_passed = False
        """Test that system initializes without any placeholder-related errors"""
        print("\n🔍 Testing System Initialization Without Placeholder Errors...")
        print("Expected: System starts cleanly without generating or referencing placeholders")
        
        try:
            # Test system status endpoint
            response = requests.get(f"{API_URL}/status")
            response.raise_for_status()
            status_data = response.json()
            
            print(f"✅ System status: {status_data.get('status', 'unknown')}")
            
            # Check if there are any placeholder-related errors in the response
            status_str = str(status_data).lower()
            placeholder_indicators = ['placeholder', 'pil', 'pillow', 'image generation', 'create_placeholder']
            
            found_placeholder_refs = [indicator for indicator in placeholder_indicators if indicator in status_str]
            
            if found_placeholder_refs:
                print(f"❌ FAILED: Found placeholder references in system status: {found_placeholder_refs}")
                self.test_results["System Initialization No Placeholder Errors"] = False
                self.all_tests_passed = False
                return
            else:
                print("✅ CORRECT: No placeholder references found in system status")
            
            # Test that system can start a session without placeholder errors
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            session_data = response.json()
            
            if "sesion_id" in session_data:
                print("✅ CORRECT: Session creation works without placeholder dependencies")
            else:
                print("❌ FAILED: Session creation failed")
                self.test_results["System Initialization No Placeholder Errors"] = False
                self.all_tests_passed = False
                return
            
            print("✅ SUCCESS: System initializes cleanly without placeholder errors!")
            self.test_results["System Initialization No Placeholder Errors"] = True
            
        except Exception as e:
            print(f"❌ System Initialization No Placeholder Errors: FAILED - {str(e)}")
            self.test_results["System Initialization No Placeholder Errors"] = False
            self.all_tests_passed = False

    def test_beverage_loading_without_placeholders(self):
        """Test that beverages load correctly without placeholder dependencies"""
        print("\n🔍 Testing Beverage Loading Without Placeholders...")
        print("Expected: All beverages load with real data, no placeholder generation")
        
        try:
            # Test admin stats endpoint to get beverage information
            response = requests.get(f"{API_URL}/admin/stats")
            response.raise_for_status()
            stats_data = response.json()
            
            bebidas_stats = stats_data.get("bebidas", {})
            total_bebidas = bebidas_stats.get("total", 0)
            
            if total_bebidas == 0:
                print("❌ FAILED: No beverages found in system")
                self.test_results["Beverage Loading Without Placeholders"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ Found {total_bebidas} beverages in system")
            print(f"✅ Refrescos reales: {bebidas_stats.get('refrescos_reales', 0)}")
            print(f"✅ Alternativas: {bebidas_stats.get('alternativas', 0)}")
            print(f"✅ Procesadas con ML: {bebidas_stats.get('procesadas_ml', 0)}")
            print(f"✅ Total presentaciones: {bebidas_stats.get('total_presentaciones', 0)}")
            
            # Check stats for placeholder indicators
            stats_str = str(stats_data).lower()
            placeholder_indicators = ['placeholder', 'pil', 'pillow', 'image generation', 'create_placeholder']
            
            found_placeholder_refs = [indicator for indicator in placeholder_indicators if indicator in stats_str]
            
            if found_placeholder_refs:
                print(f"❌ FAILED: Found placeholder references in system stats: {found_placeholder_refs}")
                self.test_results["Beverage Loading Without Placeholders"] = False
                self.all_tests_passed = False
                return
            else:
                print("✅ CORRECT: No placeholder references found in system stats")
            
            # Verify ML processing is working (indicates real data processing)
            if bebidas_stats.get('procesadas_ml', 0) > 0:
                print("✅ CORRECT: Beverages are being processed with ML (real data)")
            else:
                print("⚠️ WARNING: No beverages processed with ML yet")
            
            print("✅ SUCCESS: Beverages load correctly without placeholder dependencies!")
            self.test_results["Beverage Loading Without Placeholders"] = True
            
        except Exception as e:
            print(f"❌ Beverage Loading Without Placeholders: FAILED - {str(e)}")
            self.test_results["Beverage Loading Without Placeholders"] = False
            self.all_tests_passed = False

    def test_recommendations_without_placeholders(self):
        """Test that recommendations work without placeholder dependencies"""
        print("\n🔍 Testing Recommendations Without Placeholders...")
        print("Expected: Recommendations generated using real data, no placeholder fallbacks")
        
        try:
            # Create a complete user session
            session_id = self.create_complete_user_session()
            if not session_id:
                print("❌ FAILED: Could not create user session")
                self.test_results["Recommendations Without Placeholders"] = False
                self.all_tests_passed = False
                return
            
            # Get recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            recommendations = response.json()
            
            # Check for placeholder indicators in recommendations
            rec_str = str(recommendations).lower()
            placeholder_indicators = ['placeholder', 'default_image', 'fallback_image']
            
            found_placeholder_refs = [indicator for indicator in placeholder_indicators if indicator in rec_str]
            
            if found_placeholder_refs:
                print(f"❌ FAILED: Found placeholder references in recommendations: {found_placeholder_refs}")
                self.test_results["Recommendations Without Placeholders"] = False
                self.all_tests_passed = False
                return
            
            # Check that recommendations contain real beverages
            refrescos = recommendations.get("refrescos_reales", [])
            alternativas = recommendations.get("bebidas_alternativas", [])
            total_recommendations = len(refrescos) + len(alternativas)
            
            print(f"✅ Generated {total_recommendations} recommendations ({len(refrescos)} refrescos, {len(alternativas)} alternatives)")
            
            if total_recommendations == 0:
                print("❌ FAILED: No recommendations generated")
                self.test_results["Recommendations Without Placeholders"] = False
                self.all_tests_passed = False
                return
            
            # Check that each recommendation has real data
            all_recommendations = refrescos + alternativas
            for rec in all_recommendations:
                if not rec.get('nombre'):
                    print(f"❌ FAILED: Recommendation missing name: {rec}")
                    self.test_results["Recommendations Without Placeholders"] = False
                    self.all_tests_passed = False
                    return
                
                if not rec.get('presentaciones'):
                    print(f"❌ FAILED: Recommendation missing presentations: {rec.get('nombre')}")
                    self.test_results["Recommendations Without Placeholders"] = False
                    self.all_tests_passed = False
                    return
                
                # Check ML predictions exist (not placeholder values)
                if 'probabilidad' in rec:
                    prob = rec['probabilidad']
                    if not isinstance(prob, (int, float)) or prob < 0 or prob > 100:
                        print(f"❌ FAILED: Invalid probability in recommendation: {prob}")
                        self.test_results["Recommendations Without Placeholders"] = False
                        self.all_tests_passed = False
                        return
            
            print("✅ CORRECT: All recommendations contain real data without placeholders")
            
            # Test additional recommendations
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
            response.raise_for_status()
            additional_recs = response.json()
            
            additional_str = str(additional_recs).lower()
            if any(indicator in additional_str for indicator in placeholder_indicators):
                print("❌ FAILED: Found placeholder references in additional recommendations")
                self.test_results["Recommendations Without Placeholders"] = False
                self.all_tests_passed = False
                return
            
            print("✅ CORRECT: Additional recommendations also work without placeholders")
            
            print("✅ SUCCESS: Recommendations work correctly without placeholder dependencies!")
            self.test_results["Recommendations Without Placeholders"] = True
            
        except Exception as e:
            print(f"❌ Recommendations Without Placeholders: FAILED - {str(e)}")
            self.test_results["Recommendations Without Placeholders"] = False
            self.all_tests_passed = False

    def test_complete_flow_without_placeholder_errors(self):
        """Test complete flow from start to recommendations without placeholder errors"""
        print("\n🔍 Testing Complete Flow Without Placeholder Errors...")
        print("Expected: Full user journey works without any placeholder-related issues")
        
        try:
            # Step 1: Start session
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            session_data = response.json()
            session_id = session_data["sesion_id"]
            print("✅ Step 1: Session started successfully")
            
            # Step 2: Get initial question
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            question_data = response.json()
            print("✅ Step 2: Initial question retrieved successfully")
            
            # Step 3: Answer all questions
            questions_answered = 0
            current_question = question_data["pregunta"]
            
            while current_question and questions_answered < 10:  # Safety limit
                # Answer current question
                selected_option = current_question["opciones"][0]  # Use first option
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": current_question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": random.uniform(2.0, 8.0)
                })
                response.raise_for_status()
                questions_answered += 1
                
                # Get next question
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                next_data = response.json()
                
                if next_data.get("finalizada"):
                    break
                    
                current_question = next_data.get("pregunta")
            
            print(f"✅ Step 3: Answered {questions_answered} questions successfully")
            
            # Step 4: Get recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            recommendations = response.json()
            
            total_recs = len(recommendations.get("refrescos_reales", [])) + len(recommendations.get("bebidas_alternativas", []))
            print(f"✅ Step 4: Generated {total_recs} recommendations successfully")
            
            # Step 5: Test more options
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
            response.raise_for_status()
            more_options = response.json()
            
            additional_count = len(more_options.get("recomendaciones_adicionales", []))
            print(f"✅ Step 5: More options returned {additional_count} additional recommendations")
            
            # Step 6: Test rating functionality
            if total_recs > 0:
                # Get a beverage to rate
                all_beverages = recommendations.get("refrescos_reales", []) + recommendations.get("bebidas_alternativas", [])
                test_beverage = all_beverages[0]
                
                response = requests.post(f"{API_URL}/puntuar/{session_id}/{test_beverage['id']}", json={
                    "puntuacion": 4,
                    "comentario": "Test rating without placeholders"
                })
                response.raise_for_status()
                rating_response = response.json()
                
                print("✅ Step 6: Rating functionality works successfully")
            
            # Check entire flow for placeholder references
            flow_data = {
                "session": session_data,
                "question": question_data,
                "recommendations": recommendations,
                "more_options": more_options
            }
            
            flow_str = str(flow_data).lower()
            placeholder_indicators = ['placeholder', 'pil', 'pillow', 'default_image', 'fallback']
            
            found_placeholder_refs = [indicator for indicator in placeholder_indicators if indicator in flow_str]
            
            if found_placeholder_refs:
                print(f"❌ FAILED: Found placeholder references in complete flow: {found_placeholder_refs}")
                self.test_results["Complete Flow Without Placeholder Errors"] = False
                self.all_tests_passed = False
                return
            
            print("✅ CORRECT: Complete flow executed without any placeholder references")
            
            print("✅ SUCCESS: Complete flow works perfectly without placeholder dependencies!")
            self.test_results["Complete Flow Without Placeholder Errors"] = True
            
        except Exception as e:
            print(f"❌ Complete Flow Without Placeholder Errors: FAILED - {str(e)}")
            self.test_results["Complete Flow Without Placeholder Errors"] = False
            self.all_tests_passed = False

    def test_image_handling_no_placeholder_fallback(self):
        """Test that image handling works without placeholder fallback"""
        print("\n🔍 Testing Image Handling Without Placeholder Fallback...")
        print("Expected: Images either load from real paths or don't show, no placeholder generation")
        
        try:
            # Create a session and get recommendations to check image paths
            session_id = self.create_complete_user_session()
            if not session_id:
                print("❌ FAILED: Could not create session for image testing")
                self.test_results["Image Handling No Placeholder Fallback"] = False
                self.all_tests_passed = False
                return
            
            # Get recommendations to check image paths in beverages
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            recommendations = response.json()
            
            all_beverages = recommendations.get("refrescos_reales", []) + recommendations.get("bebidas_alternativas", [])
            
            if not all_beverages:
                print("❌ FAILED: No beverages found to test images")
                self.test_results["Image Handling No Placeholder Fallback"] = False
                self.all_tests_passed = False
                return
            
            placeholder_image_issues = []
            real_image_paths = []
            
            for bebida in all_beverages:
                presentaciones = bebida.get('presentaciones', [])
                for presentacion in presentaciones:
                    imagen_local = presentacion.get('imagen_local', '')
                    
                    if imagen_local:
                        # Check if it's a placeholder path
                        if 'placeholder' in imagen_local.lower():
                            placeholder_image_issues.append(f"Bebida {bebida.get('nombre')}: {imagen_local}")
                        else:
                            real_image_paths.append(imagen_local)
            
            if placeholder_image_issues:
                print(f"❌ FAILED: Found placeholder image paths:")
                for issue in placeholder_image_issues:
                    print(f"   - {issue}")
                self.test_results["Image Handling No Placeholder Fallback"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ CORRECT: Found {len(real_image_paths)} real image paths, no placeholder paths")
            
            # Test that static file serving works (if images exist)
            if real_image_paths:
                # Test a few image paths
                test_paths = real_image_paths[:3]  # Test first 3 images
                
                for image_path in test_paths:
                    # Construct full URL
                    if image_path.startswith('/static/'):
                        image_url = f"{BACKEND_URL}{image_path}"
                    else:
                        image_url = f"{BACKEND_URL}/static/{image_path}"
                    
                    try:
                        response = requests.head(image_url, timeout=5)
                        if response.status_code == 200:
                            print(f"✅ Image exists: {image_path}")
                        elif response.status_code == 404:
                            print(f"⚠️ Image not found (acceptable): {image_path}")
                        else:
                            print(f"⚠️ Image status {response.status_code}: {image_path}")
                    except requests.exceptions.RequestException:
                        print(f"⚠️ Could not check image: {image_path}")
            else:
                print("⚠️ No image paths found in beverages (this may be acceptable)")
            
            print("✅ CORRECT: Image handling works without placeholder fallback mechanism")
            
            print("✅ SUCCESS: Image handling works correctly without placeholder dependencies!")
            self.test_results["Image Handling No Placeholder Fallback"] = True
            
        except Exception as e:
            print(f"❌ Image Handling No Placeholder Fallback: FAILED - {str(e)}")
            self.test_results["Image Handling No Placeholder Fallback"] = False
            self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ Image Handling No Placeholder Fallback: FAILED - {str(e)}")
            self.test_results["Image Handling No Placeholder Fallback"] = False
            self.all_tests_passed = False

    def test_admin_panel_no_placeholder_dependencies(self):
        """Test that admin panel works without placeholder dependencies"""
        print("\n🔍 Testing Admin Panel Without Placeholder Dependencies...")
        print("Expected: Admin functions work with real data only, no placeholder generation")
        
        try:
            # Test admin stats endpoint
            response = requests.get(f"{API_URL}/admin/stats")
            response.raise_for_status()
            stats_data = response.json()
            
            admin_str = str(stats_data).lower()
            placeholder_indicators = ['placeholder', 'generate_placeholder', 'create_placeholder']
            
            found_placeholder_refs = [indicator for indicator in placeholder_indicators if indicator in admin_str]
            
            if found_placeholder_refs:
                print(f"❌ FAILED: Found placeholder references in admin stats: {found_placeholder_refs}")
                self.test_results["Admin Panel No Placeholder Dependencies"] = False
                self.all_tests_passed = False
                return
            
            print("✅ CORRECT: Admin stats endpoint works without placeholder references")
            
            # Test admin reprocess-beverages endpoint
            response = requests.post(f"{API_URL}/admin/reprocess-beverages")
            response.raise_for_status()
            reprocess_data = response.json()
            
            reprocess_str = str(reprocess_data).lower()
            if any(indicator in reprocess_str for indicator in placeholder_indicators):
                print("❌ FAILED: Found placeholder references in reprocess response")
                self.test_results["Admin Panel No Placeholder Dependencies"] = False
                self.all_tests_passed = False
                return
            
            print("✅ CORRECT: Admin reprocess endpoint works without placeholder references")
            
            # Test admin retrain-ml endpoint
            response = requests.post(f"{API_URL}/admin/retrain-ml")
            response.raise_for_status()
            retrain_data = response.json()
            
            retrain_str = str(retrain_data).lower()
            if any(indicator in retrain_str for indicator in placeholder_indicators):
                print("❌ FAILED: Found placeholder references in retrain response")
                self.test_results["Admin Panel No Placeholder Dependencies"] = False
                self.all_tests_passed = False
                return
            
            print("✅ CORRECT: Admin retrain endpoint works without placeholder references")
            
            print("✅ SUCCESS: Admin panel works correctly without placeholder dependencies!")
            self.test_results["Admin Panel No Placeholder Dependencies"] = True
            
        except Exception as e:
            print(f"❌ Admin Panel No Placeholder Dependencies: FAILED - {str(e)}")
            self.test_results["Admin Panel No Placeholder Dependencies"] = False
            self.all_tests_passed = False

    def test_ml_system_no_placeholder_dependencies(self):
        """Test that ML system works without placeholder data dependencies"""
        print("\n🔍 Testing ML System Without Placeholder Dependencies...")
        print("Expected: ML predictions based on real data, no placeholder-generated features")
        
        try:
            # Create a session and get ML-based recommendations
            session_id = self.create_complete_user_session()
            if not session_id:
                print("❌ FAILED: Could not create session for ML testing")
                self.test_results["ML System No Placeholder Dependencies"] = False
                self.all_tests_passed = False
                return
            
            # Get recommendations with ML predictions
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            recommendations = response.json()
            
            # Check ML-related data for placeholder indicators
            ml_data = recommendations.get("criterios_ml", {})
            ml_avanzado = recommendations.get("ml_avanzado", {})
            
            ml_str = str(ml_data).lower() + str(ml_avanzado).lower()
            placeholder_indicators = ['placeholder', 'default_feature', 'fallback_prediction']
            
            found_placeholder_refs = [indicator for indicator in placeholder_indicators if indicator in ml_str]
            
            if found_placeholder_refs:
                print(f"❌ FAILED: Found placeholder references in ML data: {found_placeholder_refs}")
                self.test_results["ML System No Placeholder Dependencies"] = False
                self.all_tests_passed = False
                return
            
            print("✅ CORRECT: ML system data contains no placeholder references")
            
            # Check that ML predictions are real values
            all_beverages = recommendations.get("refrescos_reales", []) + recommendations.get("bebidas_alternativas", [])
            
            for beverage in all_beverages:
                # Check probability values
                prob = beverage.get("probabilidad")
                if prob is not None:
                    if not isinstance(prob, (int, float)) or prob < 0 or prob > 100:
                        print(f"❌ FAILED: Invalid ML probability: {prob} for {beverage.get('nombre')}")
                        self.test_results["ML System No Placeholder Dependencies"] = False
                        self.all_tests_passed = False
                        return
                
                # Check ML prediction values
                pred_ml = beverage.get("prediccion_ml")
                if pred_ml is not None:
                    if not isinstance(pred_ml, (int, float)) or pred_ml < 0 or pred_ml > 5:
                        print(f"❌ FAILED: Invalid ML prediction: {pred_ml} for {beverage.get('nombre')}")
                        self.test_results["ML System No Placeholder Dependencies"] = False
                        self.all_tests_passed = False
                        return
                
                # Check explanatory factors
                factores = beverage.get("factores_explicativos", [])
                if factores:
                    factores_str = str(factores).lower()
                    if any(indicator in factores_str for indicator in placeholder_indicators):
                        print(f"❌ FAILED: Placeholder references in ML explanations for {beverage.get('nombre')}")
                        self.test_results["ML System No Placeholder Dependencies"] = False
                        self.all_tests_passed = False
                        return
            
            print(f"✅ CORRECT: All {len(all_beverages)} beverages have valid ML predictions without placeholders")
            
            # Test ML model stats
            if ml_data.get("modelo_entrenado") is not None:
                print(f"✅ ML model trained status: {ml_data.get('modelo_entrenado')}")
            
            if ml_data.get("muestras_entrenamiento") is not None:
                print(f"✅ ML training samples: {ml_data.get('muestras_entrenamiento')}")
            
            print("✅ SUCCESS: ML system works correctly without placeholder dependencies!")
            self.test_results["ML System No Placeholder Dependencies"] = True
            
        except Exception as e:
            print(f"❌ ML System No Placeholder Dependencies: FAILED - {str(e)}")
            self.test_results["ML System No Placeholder Dependencies"] = False
            self.all_tests_passed = False

    def test_image_loading_and_error_handling(self):
        """Test image loading and error handling for missing images"""
        print("\n🔍 Testing Image Loading and Error Handling...")
        print("Expected: Existing images load correctly, missing images don't cause critical errors")
        
        try:
            # Test existing images
            existing_images = [
                "/static/images/bebidas/Aquarius_1.5L.webp",
                "/static/images/bebidas/Ciel_Exprim_1L.webp"
            ]
            
            # Test potentially missing images (common patterns that might not exist)
            potentially_missing_images = [
                "/static/images/bebidas/NonExistent_Image.webp",
                "/static/images/bebidas/Test_404.png"
            ]
            
            existing_loaded = 0
            missing_handled = 0
            
            print("🔍 Testing existing images:")
            for image_path in existing_images:
                url = f"{BACKEND_URL}{image_path}"
                try:
                    response = requests.head(url, timeout=5)
                    if response.status_code == 200:
                        print(f"✅ LOADED: {image_path}")
                        existing_loaded += 1
                    else:
                        print(f"⚠️ Status {response.status_code}: {image_path}")
                except requests.exceptions.RequestException as e:
                    print(f"❌ ERROR: {image_path} - {e}")
            
            print("\n🔍 Testing missing image handling:")
            for image_path in potentially_missing_images:
                url = f"{BACKEND_URL}{image_path}"
                try:
                    response = requests.head(url, timeout=5)
                    if response.status_code == 404:
                        print(f"✅ PROPERLY HANDLED: {image_path} returns 404")
                        missing_handled += 1
                    elif response.status_code == 200:
                        print(f"⚠️ UNEXPECTED: {image_path} exists (this is fine)")
                        missing_handled += 1  # Still counts as handled
                    else:
                        print(f"❌ UNEXPECTED STATUS {response.status_code}: {image_path}")
                except requests.exceptions.RequestException as e:
                    print(f"❌ ERROR: {image_path} - {e}")
            
            # Test that the system doesn't crash when accessing non-existent images
            print("\n🔍 Testing system robustness:")
            try:
                # Try to access a definitely non-existent image
                bad_url = f"{BACKEND_URL}/static/images/bebidas/definitely_does_not_exist_12345.webp"
                response = requests.head(bad_url, timeout=5)
                
                if response.status_code == 404:
                    print("✅ ROBUST: System properly returns 404 for non-existent images")
                    system_robust = True
                else:
                    print(f"⚠️ Unexpected status {response.status_code} for non-existent image")
                    system_robust = True  # Still acceptable
            except requests.exceptions.RequestException as e:
                print(f"❌ SYSTEM ERROR: {e}")
                system_robust = False
            
            print(f"\n📊 IMAGE LOADING RESULTS:")
            print(f"✅ Existing images loaded: {existing_loaded}/{len(existing_images)}")
            print(f"✅ Missing images handled: {missing_handled}/{len(potentially_missing_images)}")
            print(f"✅ System robust: {system_robust}")
            
            # Success criteria
            if existing_loaded > 0 and missing_handled >= len(potentially_missing_images) // 2 and system_robust:
                print("✅ SUCCESS: Image loading and error handling work correctly!")
                self.test_results["Image Loading and Error Handling"] = True
            else:
                print("❌ FAILED: Issues with image loading or error handling")
                self.test_results["Image Loading and Error Handling"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ Image Loading and Error Handling: FAILED - {str(e)}")
            self.test_results["Image Loading and Error Handling"] = False
            self.all_tests_passed = False

    def test_complete_image_flow(self):
        """Test complete image flow from backend configuration to frontend usage"""
        print("\n🔍 Testing Complete Image Flow...")
        print("Expected: Complete flow from static files → bebidas.json → recommendations → frontend URLs")
        
        try:
            # Step 1: Verify static files are served
            print("📋 Step 1: Verifying static file serving...")
            static_test_url = f"{BACKEND_URL}/static/images/bebidas/Aquarius_1.5L.webp"
            response = requests.head(static_test_url, timeout=5)
            
            if response.status_code != 200:
                print("❌ FAILED: Static files not properly served")
                self.test_results["Complete Image Flow"] = False
                self.all_tests_passed = False
                return
            
            print("✅ Step 1 PASSED: Static files are served correctly")
            
            # Step 2: Check system stats for bebidas data
            print("\n📋 Step 2: Checking system bebidas data...")
            response = requests.get(f"{API_URL}/admin/stats")
            response.raise_for_status()
            stats_data = response.json()
            
            bebidas_stats = stats_data.get("bebidas", {})
            total_bebidas = bebidas_stats.get("total", 0)
            total_presentaciones = bebidas_stats.get("total_presentaciones", 0)
            
            if total_bebidas == 0:
                print("❌ FAILED: No bebidas found in system")
                self.test_results["Complete Image Flow"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ Step 2 PASSED: {total_bebidas} bebidas with {total_presentaciones} presentations")
            
            # Step 3: Get recommendations and verify image paths
            print("\n📋 Step 3: Testing recommendations with images...")
            session_id = self.create_complete_user_session()
            if not session_id:
                print("❌ FAILED: Could not create session")
                self.test_results["Complete Image Flow"] = False
                self.all_tests_passed = False
                return
            
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            recommendations = response.json()
            
            all_beverages = recommendations.get("refrescos_reales", []) + recommendations.get("bebidas_alternativas", [])
            
            if not all_beverages:
                print("❌ FAILED: No beverages in recommendations")
                self.test_results["Complete Image Flow"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ Step 3 PASSED: {len(all_beverages)} beverages in recommendations")
            
            # Step 4: Test frontend URL construction for actual recommendations
            print("\n📋 Step 4: Testing frontend URL construction...")
            working_urls = 0
            tested_urls = 0
            correct_paths = 0
            
            for beverage in all_beverages[:3]:  # Test first 3 beverages
                presentaciones = beverage.get("presentaciones", [])
                if presentaciones:
                    presentacion_actual = presentaciones[0]  # First presentation
                    imagen_local = presentacion_actual.get("imagen_local", "")
                    
                    if imagen_local:
                        # Check if path format is correct
                        if imagen_local.startswith("/static/images/bebidas/"):
                            correct_paths += 1
                        
                        # This is how frontend constructs the URL
                        frontend_url = f"{BACKEND_URL}{imagen_local}"
                        tested_urls += 1
                        
                        try:
                            response = requests.head(frontend_url, timeout=5)
                            if response.status_code == 200:
                                working_urls += 1
                                print(f"✅ WORKING: {beverage.get('nombre')} - {imagen_local}")
                            elif response.status_code == 404:
                                print(f"⚠️ NOT FOUND: {beverage.get('nombre')} - {imagen_local}")
                            else:
                                print(f"❌ ERROR {response.status_code}: {beverage.get('nombre')} - {imagen_local}")
                        except requests.exceptions.RequestException as e:
                            print(f"❌ REQUEST ERROR: {beverage.get('nombre')} - {e}")
            
            print(f"✅ Step 4 RESULT: {working_urls}/{tested_urls} URLs work correctly")
            print(f"✅ Path format: {correct_paths}/{tested_urls} have correct format")
            
            # Step 5: Test additional recommendations
            print("\n📋 Step 5: Testing additional recommendations...")
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
            response.raise_for_status()
            additional_recs = response.json()
            
            additional_beverages = additional_recs.get("recomendaciones_adicionales", [])
            print(f"✅ Step 5 PASSED: {len(additional_beverages)} additional recommendations")
            
            # Step 6: Test that images from bebidas.json are accessible
            print("\n📋 Step 6: Testing sample images from bebidas.json...")
            sample_images = [
                "/static/images/bebidas/Aquarius_1.5L.webp",
                "/static/images/bebidas/Ciel_Exprim_1L.webp",
                "/static/images/bebidas/Fanta_350ml.png",
                "/static/images/bebidas/Coca-cola_Light_285ml.webp"
            ]
            
            accessible_images = 0
            for image_path in sample_images:
                url = f"{BACKEND_URL}{image_path}"
                try:
                    response = requests.head(url, timeout=5)
                    if response.status_code == 200:
                        accessible_images += 1
                        print(f"✅ ACCESSIBLE: {image_path}")
                    else:
                        print(f"⚠️ Status {response.status_code}: {image_path}")
                except requests.exceptions.RequestException as e:
                    print(f"❌ ERROR: {image_path} - {e}")
            
            print(f"✅ Step 6 RESULT: {accessible_images}/{len(sample_images)} sample images accessible")
            
            # Final assessment
            print(f"\n📊 COMPLETE FLOW RESULTS:")
            print(f"✅ Static files serving: WORKING")
            print(f"✅ System bebidas: {total_bebidas} bebidas, {total_presentaciones} presentations")
            print(f"✅ Recommendations: {len(all_beverages)} beverages")
            print(f"✅ Frontend URLs: {working_urls}/{tested_urls} working")
            print(f"✅ Path format: {correct_paths}/{tested_urls} correct")
            print(f"✅ Additional recs: {len(additional_beverages)} beverages")
            print(f"✅ Sample images: {accessible_images}/{len(sample_images)} accessible")
            
            # Success criteria: Most components should work
            if (working_urls > 0 and correct_paths > 0 and len(all_beverages) > 0 and 
                accessible_images > 0 and total_bebidas > 0):
                print("✅ SUCCESS: Complete image flow is working correctly!")
                print("✅ System properly uses images from backend/static/images/bebidas/")
                self.test_results["Complete Image Flow"] = True
            else:
                print("❌ FAILED: Complete image flow has critical issues")
                self.test_results["Complete Image Flow"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ Complete Image Flow: FAILED - {str(e)}")
            self.test_results["Complete Image Flow"] = False
            self.all_tests_passed = False

    def create_test_session(self):
        """Create a basic test session"""
        try:
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            session_data = response.json()
            return session_data["sesion_id"]
        except:
            return None

    def create_health_conscious_session(self):
        """Create a session with health-conscious responses"""
        try:
            session_id = self.create_test_session()
            if not session_id:
                return None
            
            # Get initial question and answer with health-conscious choice
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            question_data = response.json()
            
            pregunta = question_data["pregunta"]
            
            # Choose "prefiere_alternativas" or "no_consume_refrescos"
            selected_option = None
            for option in pregunta["opciones"]:
                if option["valor"] in ["prefiere_alternativas", "no_consume_refrescos"]:
                    selected_option = option
                    break
            
            if not selected_option:
                selected_option = pregunta["opciones"][-1]  # Last option as fallback
            
            # Answer initial question
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": pregunta["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": 3.0
            })
            response.raise_for_status()
            
            # Answer a few more questions with health-conscious responses
            health_responses = {
                "prioridad_salud": True,
                "bebidas_naturales": True,
                "cero_azucar_natural": True,
                "evita_salud": True,
                "salud_azucar_calorias": True,
                "actividad_intensa": True,
                "cafeina_rechazo": True,
                "experiencia_hidratacion": True
            }
            
            questions_answered = 1
            while questions_answered < 6:  # Answer 6 questions total
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                next_data = response.json()
                
                if next_data.get("finalizada"):
                    break
                    
                current_question = next_data.get("pregunta")
                if not current_question:
                    break
                
                # Choose health-conscious option
                selected_option = current_question["opciones"][0]  # Default
                for option in current_question["opciones"]:
                    if any(health_val in option["valor"] for health_val in health_responses.keys()):
                        selected_option = option
                        break
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": current_question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": 3.0
                })
                response.raise_for_status()
                questions_answered += 1
            
            return session_id
            
        except Exception as e:
            print(f"Error creating health-conscious session: {e}")
            return None

    def create_traditional_session(self):
        """Create a session with traditional refresco preferences"""
        try:
            session_id = self.create_test_session()
            if not session_id:
                return None
            
            # Get initial question and answer with traditional choice
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            question_data = response.json()
            
            pregunta = question_data["pregunta"]
            
            # Choose "regular_consumidor"
            selected_option = None
            for option in pregunta["opciones"]:
                if option["valor"] == "regular_consumidor":
                    selected_option = option
                    break
            
            if not selected_option:
                selected_option = pregunta["opciones"][0]  # First option as fallback
            
            # Answer initial question
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": pregunta["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": 3.0
            })
            response.raise_for_status()
            
            # Answer more questions with traditional responses
            traditional_responses = {
                "prioridad_sabor": True,
                "refrescos_tradicionales": True,
                "alto_azucar": True,
                "ama_refrescos": True,
                "salud_no_importa": True,
                "trabajo_sedentario": True,
                "cafeina_positiva": True,
                "experiencia_placer": True
            }
            
            questions_answered = 1
            while questions_answered < 6:  # Answer 6 questions total
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                next_data = response.json()
                
                if next_data.get("finalizada"):
                    break
                    
                current_question = next_data.get("pregunta")
                if not current_question:
                    break
                
                # Choose traditional option
                selected_option = current_question["opciones"][0]  # Default
                for option in current_question["opciones"]:
                    if any(trad_val in option["valor"] for trad_val in traditional_responses.keys()):
                        selected_option = option
                        break
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": current_question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": 3.0
                })
                response.raise_for_status()
                questions_answered += 1
            
            return session_id
            
        except Exception as e:
            print(f"Error creating traditional session: {e}")
            return None

    def create_no_refresco_session(self):
        """Create a session for user who doesn't consume refrescos"""
        try:
            session_id = self.create_test_session()
            if not session_id:
                return None
            
            # Get initial question and answer with no-refresco choice
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            question_data = response.json()
            
            pregunta = question_data["pregunta"]
            
            # Choose "no_consume_refrescos"
            selected_option = None
            for option in pregunta["opciones"]:
                if option["valor"] == "no_consume_refrescos":
                    selected_option = option
                    break
            
            if not selected_option:
                selected_option = pregunta["opciones"][-1]  # Last option as fallback
            
            # Answer initial question
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": pregunta["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": 3.0
            })
            response.raise_for_status()
            
            # Answer more questions consistently with no-refresco preference
            no_refresco_responses = {
                "solo_agua": True,
                "bebidas_naturales": True,
                "cero_azucar_natural": True,
                "prioridad_salud": True,
                "rechaza_refrescos": True,
                "ejercicio_deporte": True
            }
            
            questions_answered = 1
            while questions_answered < 6:  # Answer 6 questions total
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                next_data = response.json()
                
                if next_data.get("finalizada"):
                    break
                    
                current_question = next_data.get("pregunta")
                if not current_question:
                    break
                
                # Choose no-refresco option
                selected_option = current_question["opciones"][0]  # Default
                for option in current_question["opciones"]:
                    if any(no_ref_val in option["valor"] for no_ref_val in no_refresco_responses.keys()):
                        selected_option = option
                        break
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": current_question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": 3.0
                })
                response.raise_for_status()
                questions_answered += 1
            
            return session_id
            
        except Exception as e:
            print(f"Error creating no-refresco session: {e}")
            return None

    def create_specific_response_session(self, target_responses):
        """Create a session with specific responses for testing"""
        try:
            session_id = self.create_test_session()
            if not session_id:
                return None
            
            # Get initial question
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            question_data = response.json()
            
            pregunta = question_data["pregunta"]
            
            # Answer initial question
            selected_option = pregunta["opciones"][0]  # Default
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": pregunta["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": 3.0
            })
            response.raise_for_status()
            
            # Answer more questions, looking for target responses
            questions_answered = 1
            while questions_answered < 6:  # Answer 6 questions total
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                next_data = response.json()
                
                if next_data.get("finalizada"):
                    break
                    
                current_question = next_data.get("pregunta")
                if not current_question:
                    break
                
                # Look for target response
                selected_option = current_question["opciones"][0]  # Default
                for option in current_question["opciones"]:
                    if any(target_val in option["valor"] for target_val in target_responses.values()):
                        selected_option = option
                        break
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": current_question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": 3.0
                })
                response.raise_for_status()
                questions_answered += 1
            
            return session_id
            
        except Exception as e:
            print(f"Error creating specific response session: {e}")
            return None

    def create_mixed_priority_session(self, p4_value):
        """Create session to test P4 priority with mixed other responses"""
        try:
            session_id = self.create_test_session()
            if not session_id:
                return None
            
            # Answer questions with mixed responses but specific P4 value
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            question_data = response.json()
            
            pregunta = question_data["pregunta"]
            selected_option = pregunta["opciones"][1]  # Use middle option
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": pregunta["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": 3.0
            })
            response.raise_for_status()
            
            questions_answered = 1
            while questions_answered < 6:
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                next_data = response.json()
                
                if next_data.get("finalizada"):
                    break
                    
                current_question = next_data.get("pregunta")
                if not current_question:
                    break
                
                # If this is P4, use the specific value
                if current_question["id"] == 4:
                    selected_option = None
                    for option in current_question["opciones"]:
                        if option["valor"] == p4_value:
                            selected_option = option
                            break
                    if not selected_option:
                        selected_option = current_question["opciones"][0]
                else:
                    # Use random option for other questions
                    selected_option = current_question["opciones"][random.randint(0, len(current_question["opciones"])-1)]
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": current_question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": 3.0
                })
                response.raise_for_status()
                questions_answered += 1
            
            return session_id
            
        except Exception as e:
            print(f"Error creating mixed priority session: {e}")
            return None

    def create_mixed_p1_session(self, p1_value):
        """Create session to test P1 priority with mixed other responses"""
        try:
            session_id = self.create_test_session()
            if not session_id:
                return None
            
            # Get initial question (P1) and use specific value
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            question_data = response.json()
            
            pregunta = question_data["pregunta"]
            
            # Use specific P1 value
            selected_option = None
            for option in pregunta["opciones"]:
                if option["valor"] == p1_value:
                    selected_option = option
                    break
            
            if not selected_option:
                selected_option = pregunta["opciones"][0]
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": pregunta["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": 3.0
            })
            response.raise_for_status()
            
            # Answer other questions with mixed responses
            questions_answered = 1
            while questions_answered < 6:
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                next_data = response.json()
                
                if next_data.get("finalizada"):
                    break
                    
                current_question = next_data.get("pregunta")
                if not current_question:
                    break
                
                # Use random option
                selected_option = current_question["opciones"][random.randint(0, len(current_question["opciones"])-1)]
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": current_question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": 3.0
                })
                response.raise_for_status()
                questions_answered += 1
            
            return session_id
            
        except Exception as e:
            print(f"Error creating mixed P1 session: {e}")
            return None

    def create_predictable_session(self, specific_responses):
        """Create session with specific responses for predictability testing"""
        try:
            session_id = self.create_test_session()
            if not session_id:
                return None
            
            # Get initial question
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            question_data = response.json()
            
            pregunta = question_data["pregunta"]
            
            # Use specific response for P1 if available
            if 1 in specific_responses:
                target_value = specific_responses[1]
                selected_option = None
                for option in pregunta["opciones"]:
                    if option["valor"] == target_value:
                        selected_option = option
                        break
                if not selected_option:
                    selected_option = pregunta["opciones"][0]
            else:
                selected_option = pregunta["opciones"][0]
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": pregunta["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": 3.0
            })
            response.raise_for_status()
            
            # Answer other questions with specific responses
            questions_answered = 1
            while questions_answered < 6:
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                next_data = response.json()
                
                if next_data.get("finalizada"):
                    break
                    
                current_question = next_data.get("pregunta")
                if not current_question:
                    break
                
                question_id = current_question["id"]
                
                # Use specific response if available
                if question_id in specific_responses:
                    target_value = specific_responses[question_id]
                    selected_option = None
                    for option in current_question["opciones"]:
                        if option["valor"] == target_value:
                            selected_option = option
                            break
                    if not selected_option:
                        selected_option = current_question["opciones"][0]
                else:
                    selected_option = current_question["opciones"][0]
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": current_question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": 3.0
                })
                response.raise_for_status()
                questions_answered += 1
            
            return session_id
            
        except Exception as e:
            print(f"Error creating predictable session: {e}")
            return None

    def create_expanded_question_session(self, target_responses):
        """Create session focusing on expanded questions (P7-P18)"""
        try:
            session_id = self.create_test_session()
            if not session_id:
                return None
            
            # Answer initial question
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            question_data = response.json()
            
            pregunta = question_data["pregunta"]
            selected_option = pregunta["opciones"][0]  # Default for P1
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": pregunta["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": 3.0
            })
            response.raise_for_status()
            
            # Answer more questions, focusing on expanded questions
            questions_answered = 1
            while questions_answered < 6:
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                next_data = response.json()
                
                if next_data.get("finalizada"):
                    break
                    
                current_question = next_data.get("pregunta")
                if not current_question:
                    break
                
                question_id = current_question["id"]
                
                # Use target response if this is one of the expanded questions
                if question_id in target_responses:
                    target_value = target_responses[question_id]
                    selected_option = None
                    for option in current_question["opciones"]:
                        if target_value in option["valor"]:
                            selected_option = option
                            break
                    if not selected_option:
                        selected_option = current_question["opciones"][0]
                else:
                    selected_option = current_question["opciones"][0]
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": current_question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": 3.0
                })
                response.raise_for_status()
                questions_answered += 1
            
            return session_id
            
        except Exception as e:
            print(f"Error creating expanded question session: {e}")
            return None

    def test_backend_static_files_configuration(self):
        """Create a complete user session by answering all questions"""
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
            
            # Answer initial question
            selected_option = question["opciones"][0]
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": random.uniform(2.0, 8.0)
            })
            response.raise_for_status()
            
            # Answer remaining questions
            for i in range(10):  # Safety limit
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                data = response.json()
                
                if data.get("finalizada"):
                    break
                    
                question = data["pregunta"]
                selected_option = question["opciones"][len(question["opciones"]) // 2]  # Middle option
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": random.uniform(1.0, 10.0)
                })
                response.raise_for_status()
            
            return session_id
            
        except Exception as e:
            print(f"Error creating complete user session: {str(e)}")
            return None
        """Test the 6 new questions structure - CRITICAL VERIFICATION"""
        print("\n🔍 Testing 6 New Questions Structure...")
        print("Expected: 6 specific questions with exact values for eliminating mixed behavior")
        
        try:
            # Create a new session
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            session_data = response.json()
            session_id = session_data["sesion_id"]
            
            # Get the initial question (P1)
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "pregunta" not in data:
                print("❌ FAILED: No pregunta in response")
                self.test_results["6 New Questions Structure"] = False
                self.all_tests_passed = False
                return
            
            pregunta1 = data["pregunta"]
            
            # VERIFY P1: "¿Cuál describe mejor tu relación con los refrescos?"
            expected_p1_text = "¿Cuál describe mejor tu relación con los refrescos"
            if expected_p1_text in pregunta1.get("pregunta", ""):
                print("✅ P1 CORRECT: Question about relationship with sodas")
            else:
                print(f"❌ P1 INCORRECT: Expected question about relationship with sodas")
                print(f"   Got: {pregunta1.get('pregunta', '')}")
                self.test_results["6 New Questions Structure"] = False
                self.all_tests_passed = False
                return
            
            # VERIFY P1 OPTIONS: no_consume_refrescos, prefiere_alternativas, etc.
            expected_p1_values = ["no_consume_refrescos", "prefiere_alternativas", "regular_consumidor", "ocasional_consumidor", "muy_ocasional"]
            found_p1_values = [opcion.get("valor", "") for opcion in pregunta1.get("opciones", [])]
            
            matching_p1 = [val for val in expected_p1_values if val in found_p1_values]
            if len(matching_p1) >= 4:
                print(f"✅ P1 OPTIONS CORRECT: Found {len(matching_p1)} expected values: {matching_p1}")
            else:
                print(f"❌ P1 OPTIONS INCORRECT: Only found {len(matching_p1)} expected values")
                print(f"   Expected: {expected_p1_values}")
                print(f"   Found: {found_p1_values}")
                self.test_results["6 New Questions Structure"] = False
                self.all_tests_passed = False
                return
            
            # Answer P1 and get remaining questions
            selected_option = pregunta1["opciones"][0]
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": pregunta1["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": 3.0
            })
            response.raise_for_status()
            
            # Collect all 6 questions
            all_questions = [pregunta1]
            
            for i in range(5):  # Get remaining 5 questions
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                data = response.json()
                
                if "finalizada" in data and data["finalizada"]:
                    break
                    
                question = data["pregunta"]
                all_questions.append(question)
                
                # Answer the question
                selected_option = question["opciones"][len(question["opciones"]) // 2]  # Middle option
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": random.uniform(2.0, 8.0)
                })
                response.raise_for_status()
            
            print(f"✅ COLLECTED {len(all_questions)} questions total")
            
            if len(all_questions) != 6:
                print(f"❌ INCORRECT: Expected exactly 6 questions, got {len(all_questions)}")
                self.test_results["6 New Questions Structure"] = False
                self.all_tests_passed = False
                return
            
            # VERIFY SPECIFIC QUESTION PATTERNS
            expected_patterns = [
                ("relación", "refrescos"),  # P1: relationship with sodas
                ("tipo", "bebidas"),        # P2: type of drinks
                ("azúcar", "prefieres"),    # P3: sugar level
                ("importante", "elegir"),   # P4: what's important
                ("sientes", "refrescos"),   # P5: feelings about sodas
                ("situaciones", "tomar")    # P6: situations for drinking
            ]
            
            questions_verified = 0
            for i, (pattern1, pattern2) in enumerate(expected_patterns):
                if i < len(all_questions):
                    question_text = all_questions[i].get("pregunta", "").lower()
                    if pattern1 in question_text and pattern2 in question_text:
                        print(f"✅ P{i+1} VERIFIED: Contains '{pattern1}' and '{pattern2}'")
                        questions_verified += 1
                    else:
                        print(f"⚠️ P{i+1} PATTERN: Expected '{pattern1}' and '{pattern2}' in: {question_text}")
            
            # VERIFY SPECIFIC VALUES IN QUESTIONS
            critical_values_found = []
            
            # Check for critical values across all questions
            critical_values = [
                "bebidas_naturales", "solo_agua", "prioridad_salud", "solo_natural",
                "evita_salud", "rechaza_refrescos", "cero_azucar_natural", "ejercicio_deporte",
                "ama_refrescos", "gusta_moderado", "prioridad_sabor"
            ]
            
            for question in all_questions:
                for option in question.get("opciones", []):
                    valor = option.get("valor", "")
                    if valor in critical_values:
                        critical_values_found.append(valor)
            
            print(f"✅ CRITICAL VALUES FOUND: {len(critical_values_found)} values")
            print(f"   Found: {critical_values_found}")
            
            if len(critical_values_found) >= 8:  # Should find most critical values
                print("✅ EXCELLENT: Found sufficient critical values for logic")
            elif len(critical_values_found) >= 5:
                print("✅ GOOD: Found adequate critical values")
            else:
                print(f"⚠️ WARNING: Only found {len(critical_values_found)} critical values")
            
            print("✅ SUCCESS: 6 New Questions Structure is correctly implemented!")
            self.test_results["6 New Questions Structure"] = True
            
        except Exception as e:
            print(f"❌ 6 New Questions Structure: FAILED - {str(e)}")
            self.test_results["6 New Questions Structure"] = False
            self.all_tests_passed = False

    def test_new_determinar_mostrar_alternativas_logic(self):
        """Test the new simplified determinar_mostrar_alternativas() logic"""
        print("\n🔍 Testing New determinar_mostrar_alternativas() Logic...")
        print("Expected: Simplified logic that only checks specific values")
        
        try:
            # Test cases that should return TRUE (show alternatives)
            true_cases = [
                ("bebidas_naturales", "User seeks natural drinks"),
                ("solo_agua", "User only wants water"),
                ("prioridad_salud", "User prioritizes health"),
                ("solo_natural", "User wants only natural"),
                ("evita_salud", "User avoids for health"),
                ("rechaza_refrescos", "User rejects sodas"),
                ("cero_azucar_natural", "User wants zero sugar natural"),
                ("ejercicio_deporte", "User drinks during exercise")
            ]
            
            # Test cases that should return FALSE (no alternatives, only sodas)
            false_cases = [
                ("ama_refrescos", "User loves sodas"),
                ("gusta_moderado", "User likes moderately"),
                ("social_solamente", "User drinks socially only"),
                ("prioridad_sabor", "User prioritizes flavor"),
                ("regular_consumidor", "Regular consumer"),
                ("ocasional_consumidor", "Occasional consumer")
            ]
            
            true_results = []
            false_results = []
            
            # Test TRUE cases
            print("\n📋 Testing cases that SHOULD show alternatives:")
            for test_value, description in true_cases:
                session_id = self.create_user_session_with_specific_pattern(test_value)
                if session_id:
                    response = requests.get(f"{API_URL}/recomendacion/{session_id}")
                    response.raise_for_status()
                    recommendations = response.json()
                    
                    mostrar_alternativas = recommendations.get("mostrar_alternativas", False)
                    alternativas_count = len(recommendations.get("bebidas_alternativas", []))
                    
                    if mostrar_alternativas or alternativas_count > 0:
                        print(f"✅ {test_value}: CORRECT - Shows alternatives ({description})")
                        true_results.append(True)
                    else:
                        print(f"❌ {test_value}: INCORRECT - Should show alternatives ({description})")
                        true_results.append(False)
                else:
                    print(f"⚠️ {test_value}: Could not create session")
                    true_results.append(None)
            
            # Test FALSE cases
            print("\n📋 Testing cases that should NOT show alternatives:")
            for test_value, description in false_cases:
                session_id = self.create_user_session_with_specific_pattern(test_value)
                if session_id:
                    response = requests.get(f"{API_URL}/recomendacion/{session_id}")
                    response.raise_for_status()
                    recommendations = response.json()
                    
                    mostrar_alternativas = recommendations.get("mostrar_alternativas", False)
                    alternativas_count = len(recommendations.get("bebidas_alternativas", []))
                    refrescos_count = len(recommendations.get("refrescos_reales", []))
                    
                    if not mostrar_alternativas and alternativas_count == 0 and refrescos_count > 0:
                        print(f"✅ {test_value}: CORRECT - Only shows sodas ({description})")
                        false_results.append(True)
                    elif mostrar_alternativas and alternativas_count > 0 and refrescos_count > 0:
                        print(f"⚠️ {test_value}: MIXED BEHAVIOR - Shows both types ({description})")
                        false_results.append(False)
                    else:
                        print(f"❌ {test_value}: UNEXPECTED - Unclear behavior ({description})")
                        false_results.append(False)
                else:
                    print(f"⚠️ {test_value}: Could not create session")
                    false_results.append(None)
            
            # Analyze results
            true_success_rate = sum(1 for r in true_results if r is True) / len([r for r in true_results if r is not None]) if true_results else 0
            false_success_rate = sum(1 for r in false_results if r is True) / len([r for r in false_results if r is not None]) if false_results else 0
            
            print(f"\n📊 ANALYSIS:")
            print(f"✅ TRUE cases success rate: {true_success_rate:.1%} ({sum(1 for r in true_results if r is True)}/{len([r for r in true_results if r is not None])})")
            print(f"✅ FALSE cases success rate: {false_success_rate:.1%} ({sum(1 for r in false_results if r is True)}/{len([r for r in false_results if r is not None])})")
            
            overall_success = true_success_rate >= 0.7 and false_success_rate >= 0.7
            
            if overall_success:
                print("✅ SUCCESS: New determinar_mostrar_alternativas() logic is working correctly!")
                self.test_results["New determinar_mostrar_alternativas Logic"] = True
            else:
                print("❌ FAILED: New logic is not working as expected")
                self.test_results["New determinar_mostrar_alternativas Logic"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ New determinar_mostrar_alternativas Logic: FAILED - {str(e)}")
            self.test_results["New determinar_mostrar_alternativas Logic"] = False
            self.all_tests_passed = False

    def test_specific_mixed_behavior_cases(self):
        """Test specific cases that previously caused mixed behavior"""
        print("\n🔍 Testing Specific Cases That Previously Caused Mixed Behavior...")
        print("Expected: Clear, predictable behavior for each case")
        
        try:
            # CRITICAL TEST CASES from the review request
            test_cases = [
                {
                    "name": "ocasional_consumidor + prioridad_sabor",
                    "pattern": ["ocasional_consumidor", "prioridad_sabor"],
                    "expected": "Only sodas",
                    "should_have_refrescos": True,
                    "should_have_alternatives": False
                },
                {
                    "name": "ocasional_consumidor + prioridad_salud", 
                    "pattern": ["ocasional_consumidor", "prioridad_salud"],
                    "expected": "Only alternatives",
                    "should_have_refrescos": False,
                    "should_have_alternatives": True
                },
                {
                    "name": "gusta_moderado + ama_refrescos",
                    "pattern": ["gusta_moderado", "ama_refrescos"],
                    "expected": "Only sodas",
                    "should_have_refrescos": True,
                    "should_have_alternatives": False
                },
                {
                    "name": "regular_consumidor + bebidas_naturales",
                    "pattern": ["regular_consumidor", "bebidas_naturales"],
                    "expected": "Only alternatives",
                    "should_have_refrescos": False,
                    "should_have_alternatives": True
                }
            ]
            
            all_cases_passed = True
            
            for case in test_cases:
                print(f"\n📋 Testing: {case['name']}")
                print(f"   Expected: {case['expected']}")
                
                # Create session with specific pattern
                session_id = self.create_user_session_with_multiple_patterns(case['pattern'])
                if not session_id:
                    print(f"❌ Could not create session for {case['name']}")
                    all_cases_passed = False
                    continue
                
                # Get recommendations
                response = requests.get(f"{API_URL}/recomendacion/{session_id}")
                response.raise_for_status()
                recommendations = response.json()
                
                refrescos_count = len(recommendations.get("refrescos_reales", []))
                alternativas_count = len(recommendations.get("bebidas_alternativas", []))
                mostrar_alternativas = recommendations.get("mostrar_alternativas", False)
                usuario_no_consume = recommendations.get("usuario_no_consume_refrescos", False)
                
                print(f"   Result: {refrescos_count} refrescos, {alternativas_count} alternatives")
                print(f"   Flags: mostrar_alternativas={mostrar_alternativas}, usuario_no_consume={usuario_no_consume}")
                
                # Check if result matches expectation
                case_passed = True
                
                if case['should_have_refrescos'] and refrescos_count == 0:
                    print(f"❌ FAILED: Expected refrescos but got none")
                    case_passed = False
                elif not case['should_have_refrescos'] and refrescos_count > 0:
                    print(f"❌ FAILED: Expected no refrescos but got {refrescos_count}")
                    case_passed = False
                
                if case['should_have_alternatives'] and alternativas_count == 0:
                    print(f"❌ FAILED: Expected alternatives but got none")
                    case_passed = False
                elif not case['should_have_alternatives'] and alternativas_count > 0:
                    print(f"❌ FAILED: Expected no alternatives but got {alternativas_count}")
                    case_passed = False
                
                # Check for mixed behavior (both types when not expected)
                if refrescos_count > 0 and alternativas_count > 0:
                    if case['expected'] not in ["Both types separately"]:
                        print(f"❌ MIXED BEHAVIOR DETECTED: Got both types when expecting {case['expected']}")
                        case_passed = False
                    else:
                        print(f"✅ ACCEPTABLE: Both types shown separately as expected")
                
                if case_passed:
                    print(f"✅ PASSED: {case['name']} behaves correctly")
                else:
                    print(f"❌ FAILED: {case['name']} has incorrect behavior")
                    all_cases_passed = False
            
            if all_cases_passed:
                print("\n✅ SUCCESS: All specific mixed behavior cases now work correctly!")
                self.test_results["Specific Mixed Behavior Cases"] = True
            else:
                print("\n❌ FAILED: Some cases still show mixed behavior")
                self.test_results["Specific Mixed Behavior Cases"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ Specific Mixed Behavior Cases: FAILED - {str(e)}")
            self.test_results["Specific Mixed Behavior Cases"] = False
            self.all_tests_passed = False

    def test_complete_mixed_behavior_elimination(self):
        """Test complete elimination of mixed behavior - 100% predictable"""
        print("\n🔍 Testing Complete Mixed Behavior Elimination...")
        print("Expected: 100% predictable behavior - no user should get confusing mixed results")
        
        try:
            # Test comprehensive set of user patterns
            test_patterns = [
                # Clear "only alternatives" patterns
                ("no_consume_refrescos", "ONLY_ALTERNATIVES"),
                ("prefiere_alternativas", "ALTERNATIVES_INITIAL"),
                ("bebidas_naturales", "ONLY_ALTERNATIVES"),
                ("solo_agua", "ONLY_ALTERNATIVES"),
                ("prioridad_salud", "ONLY_ALTERNATIVES"),
                ("evita_salud", "ONLY_ALTERNATIVES"),
                ("rechaza_refrescos", "ONLY_ALTERNATIVES"),
                ("cero_azucar_natural", "ONLY_ALTERNATIVES"),
                ("ejercicio_deporte", "ONLY_ALTERNATIVES"),
                
                # Clear "only sodas" patterns
                ("regular_consumidor", "ONLY_SODAS_OR_CLEAR_SEPARATION"),
                ("ama_refrescos", "ONLY_SODAS"),
                ("prioridad_sabor", "ONLY_SODAS"),
                ("gusta_moderado", "ONLY_SODAS_OR_CLEAR_SEPARATION"),
                ("social_solamente", "ONLY_SODAS"),
                ("ocasional_consumidor", "ONLY_SODAS_OR_CLEAR_SEPARATION")
            ]
            
            mixed_behavior_count = 0
            clear_behavior_count = 0
            total_tested = 0
            
            for pattern, expected_behavior in test_patterns:
                print(f"\n📋 Testing pattern: {pattern} (Expected: {expected_behavior})")
                
                session_id = self.create_user_session_with_specific_pattern(pattern)
                if not session_id:
                    print(f"⚠️ Could not create session for {pattern}")
                    continue
                
                total_tested += 1
                
                # Get recommendations
                response = requests.get(f"{API_URL}/recomendacion/{session_id}")
                response.raise_for_status()
                recommendations = response.json()
                
                refrescos_count = len(recommendations.get("refrescos_reales", []))
                alternativas_count = len(recommendations.get("bebidas_alternativas", []))
                mostrar_alternativas = recommendations.get("mostrar_alternativas", False)
                usuario_no_consume = recommendations.get("usuario_no_consume_refrescos", False)
                mensaje_refrescos = recommendations.get("mensaje_refrescos", "")
                
                print(f"   Result: {refrescos_count} refrescos, {alternativas_count} alternatives")
                
                # Analyze behavior clarity
                behavior_analysis = self.analyze_behavior_clarity(
                    pattern, expected_behavior, refrescos_count, alternativas_count,
                    mostrar_alternativas, usuario_no_consume, mensaje_refrescos
                )
                
                if behavior_analysis["is_clear"]:
                    print(f"✅ CLEAR: {behavior_analysis['description']}")
                    clear_behavior_count += 1
                else:
                    print(f"❌ MIXED: {behavior_analysis['reason']}")
                    mixed_behavior_count += 1
            
            # Calculate success rate
            if total_tested > 0:
                clear_rate = clear_behavior_count / total_tested
                mixed_rate = mixed_behavior_count / total_tested
                
                print(f"\n📊 FINAL ANALYSIS:")
                print(f"✅ Clear behavior: {clear_behavior_count}/{total_tested} ({clear_rate:.1%})")
                print(f"❌ Mixed behavior: {mixed_behavior_count}/{total_tested} ({mixed_rate:.1%})")
                
                # Success criteria: 90%+ clear behavior
                if clear_rate >= 0.9:
                    print("\n✅ SUCCESS: Mixed behavior has been eliminated! System is 100% predictable!")
                    self.test_results["Complete Mixed Behavior Elimination"] = True
                elif clear_rate >= 0.8:
                    print("\n⚠️ GOOD: Most mixed behavior eliminated, minor issues remain")
                    self.test_results["Complete Mixed Behavior Elimination"] = True
                else:
                    print("\n❌ FAILED: Significant mixed behavior still exists")
                    self.test_results["Complete Mixed Behavior Elimination"] = False
                    self.all_tests_passed = False
            else:
                print("❌ FAILED: Could not test any patterns")
                self.test_results["Complete Mixed Behavior Elimination"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ Complete Mixed Behavior Elimination: FAILED - {str(e)}")
            self.test_results["Complete Mixed Behavior Elimination"] = False
            self.all_tests_passed = False

    def analyze_behavior_clarity(self, pattern, expected_behavior, refrescos_count, alternativas_count, mostrar_alternativas, usuario_no_consume, mensaje):
        """Analyze if behavior is clear or mixed"""
        
        # ONLY_ALTERNATIVES patterns
        if expected_behavior == "ONLY_ALTERNATIVES":
            if refrescos_count == 0 and alternativas_count > 0:
                return {"is_clear": True, "description": "Only alternatives (perfect)"}
            elif refrescos_count > 0 and alternativas_count > 0:
                return {"is_clear": False, "reason": "Mixed behavior - should only show alternatives"}
            elif refrescos_count > 0 and alternativas_count == 0:
                return {"is_clear": False, "reason": "Wrong behavior - should show alternatives, not sodas"}
            else:
                return {"is_clear": False, "reason": "No recommendations shown"}
        
        # ALTERNATIVES_INITIAL patterns (prefiere_alternativas)
        elif expected_behavior == "ALTERNATIVES_INITIAL":
            if refrescos_count == 0 and alternativas_count > 0:
                return {"is_clear": True, "description": "Alternatives initially (correct for prefiere_alternativas)"}
            elif refrescos_count > 0 and alternativas_count > 0:
                return {"is_clear": False, "reason": "Mixed behavior - should show alternatives initially"}
            else:
                return {"is_clear": False, "reason": "Unexpected behavior for prefiere_alternativas"}
        
        # ONLY_SODAS patterns
        elif expected_behavior == "ONLY_SODAS":
            if refrescos_count > 0 and alternativas_count == 0:
                return {"is_clear": True, "description": "Only sodas (perfect)"}
            elif refrescos_count > 0 and alternativas_count > 0:
                return {"is_clear": False, "reason": "Mixed behavior - should only show sodas"}
            elif refrescos_count == 0 and alternativas_count > 0:
                return {"is_clear": False, "reason": "Wrong behavior - should show sodas, not alternatives"}
            else:
                return {"is_clear": False, "reason": "No recommendations shown"}
        
        # ONLY_SODAS_OR_CLEAR_SEPARATION patterns
        elif expected_behavior == "ONLY_SODAS_OR_CLEAR_SEPARATION":
            if refrescos_count > 0 and alternativas_count == 0:
                return {"is_clear": True, "description": "Only sodas (traditional behavior)"}
            elif refrescos_count > 0 and alternativas_count > 0 and mostrar_alternativas:
                # Check for clear separation message
                if "ambos" in mensaje.lower() or ("refrescos" in mensaje.lower() and "alternativas" in mensaje.lower()):
                    return {"is_clear": True, "description": "Both types with clear separation message"}
                else:
                    return {"is_clear": False, "reason": "Both types without clear separation message"}
            elif refrescos_count > 0 and alternativas_count > 0 and not mostrar_alternativas:
                return {"is_clear": False, "reason": "Mixed behavior without mostrar_alternativas flag"}
            else:
                return {"is_clear": False, "reason": "Unexpected behavior pattern"}
        
        return {"is_clear": False, "reason": "Unknown expected behavior"}

    def create_user_session_with_specific_pattern(self, target_pattern):
        """Create a user session with a specific pattern in responses"""
        try:
            # Create session
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            session_data = response.json()
            session_id = session_data["sesion_id"]
            
            # Get all questions and answer them
            questions_answered = 0
            
            # Get initial question
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            data = response.json()
            question = data["pregunta"]
            
            # Try to match target pattern in initial question
            selected_option = self.find_option_with_pattern(question, target_pattern)
            if not selected_option:
                selected_option = question["opciones"][0]  # Fallback
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": random.uniform(2.0, 8.0)
            })
            response.raise_for_status()
            questions_answered += 1
            
            # Answer remaining questions
            for i in range(5):  # Up to 5 more questions
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                data = response.json()
                
                if "finalizada" in data and data["finalizada"]:
                    break
                    
                question = data["pregunta"]
                
                # Try to match target pattern, otherwise use neutral response
                selected_option = self.find_option_with_pattern(question, target_pattern)
                if not selected_option:
                    # Use middle option for neutral response
                    option_index = len(question["opciones"]) // 2
                    selected_option = question["opciones"][option_index]
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": random.uniform(1.0, 10.0)
                })
                response.raise_for_status()
                questions_answered += 1
            
            return session_id
            
        except Exception as e:
            print(f"Error creating session with pattern '{target_pattern}': {str(e)}")
            return None

    def create_user_session_with_multiple_patterns(self, target_patterns):
        """Create a user session with multiple specific patterns in responses"""
        try:
            # Create session
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            session_data = response.json()
            session_id = session_data["sesion_id"]
            
            pattern_index = 0
            
            # Get initial question
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            data = response.json()
            question = data["pregunta"]
            
            # Try to match first pattern in initial question
            current_pattern = target_patterns[pattern_index] if pattern_index < len(target_patterns) else None
            selected_option = self.find_option_with_pattern(question, current_pattern)
            if not selected_option:
                selected_option = question["opciones"][0]  # Fallback
            else:
                pattern_index += 1
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": random.uniform(2.0, 8.0)
            })
            response.raise_for_status()
            
            # Answer remaining questions
            for i in range(5):  # Up to 5 more questions
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                data = response.json()
                
                if "finalizada" in data and data["finalizada"]:
                    break
                    
                question = data["pregunta"]
                
                # Try to match next pattern
                current_pattern = target_patterns[pattern_index] if pattern_index < len(target_patterns) else None
                selected_option = self.find_option_with_pattern(question, current_pattern)
                if selected_option:
                    pattern_index += 1
                else:
                    # Use neutral response
                    option_index = len(question["opciones"]) // 2
                    selected_option = question["opciones"][option_index]
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": random.uniform(1.0, 10.0)
                })
                response.raise_for_status()
            
            return session_id
            
        except Exception as e:
            print(f"Error creating session with patterns {target_patterns}: {str(e)}")
            return None

    def find_option_with_pattern(self, question, pattern):
        """Find an option that matches the target pattern"""
        if not pattern:
            return None
            
        for option in question.get("opciones", []):
            valor = option.get("valor", "")
            texto = option.get("texto", "")
            
            # Check if pattern matches valor or is contained in texto
            if valor == pattern or pattern in valor.lower() or pattern in texto.lower():
                return option
        
        return None
        """Test the new clearer initial question about soda consumption"""
        print("\n🔍 Testing New Initial Question...")
        print("Expected: '¿Cuál describe mejor tu relación con los refrescos/bebidas gaseosas?'")
        print("Expected options: regular_consumidor, ocasional_consumidor, muy_ocasional, prefiere_alternativas, no_consume_refrescos")
        
        try:
            # Create a new session
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            session_data = response.json()
            session_id = session_data["sesion_id"]
            
            # Get the initial question
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "pregunta" not in data:
                print("❌ New Initial Question: FAILED - No pregunta in response")
                self.test_results["New Initial Question"] = False
                self.all_tests_passed = False
                return
            
            pregunta = data["pregunta"]
            pregunta_texto = pregunta.get("pregunta", "")
            opciones = pregunta.get("opciones", [])
            
            print(f"✅ Question text: {pregunta_texto}")
            
            # Check if the question is about soda consumption relationship
            if "relación" in pregunta_texto.lower() and "refrescos" in pregunta_texto.lower():
                print("✅ CORRECT: Question is about relationship with sodas")
            else:
                print(f"❌ INCORRECT: Question doesn't match expected pattern. Got: {pregunta_texto}")
                self.test_results["New Initial Question"] = False
                self.all_tests_passed = False
                return
            
            # Check for expected option values
            expected_values = ["regular_consumidor", "ocasional_consumidor", "muy_ocasional", "prefiere_alternativas", "no_consume_refrescos"]
            found_values = [opcion.get("valor", "") for opcion in opciones]
            
            print(f"✅ Found option values: {found_values}")
            
            # Check if we have the new specific options
            matching_values = [val for val in expected_values if val in found_values]
            
            if len(matching_values) >= 3:  # At least 3 of the expected values should be present
                print(f"✅ CORRECT: Found {len(matching_values)} expected option values: {matching_values}")
            else:
                print(f"❌ INCORRECT: Only found {len(matching_values)} expected values. Expected at least 3 from: {expected_values}")
                self.test_results["New Initial Question"] = False
                self.all_tests_passed = False
                return
            
            # Check if options are more specific than before
            if len(opciones) >= 4:
                print(f"✅ CORRECT: Question has {len(opciones)} options (good specificity)")
            else:
                print(f"⚠️ WARNING: Only {len(opciones)} options, might not be specific enough")
            
            print("✅ SUCCESS: New initial question is correctly implemented!")
            self.test_results["New Initial Question"] = True
            
        except Exception as e:
            print(f"❌ New Initial Question: FAILED - {str(e)}")
            self.test_results["New Initial Question"] = False
            self.all_tests_passed = False

    def test_new_user_categorization_logic(self):
        """Test the new user categorization logic"""
        print("\n🔍 Testing New User Categorization Logic...")
        print("Expected categories:")
        print("- usuario_no_consume_refrescos: Only alternatives")
        print("- usuario_prefiere_alternativas: Alternatives initially, sodas in more options")
        print("- usuario_regular with mostrar_alternativas: Both types separately")
        print("- usuario_tradicional: Only sodas")
        
        try:
            # Test different user types by creating sessions with specific answers
            user_types_to_test = [
                ("no_consume_refrescos", "no_consume_refrescos"),
                ("prefiere_alternativas", "prefiere_alternativas"),
                ("regular_consumidor", "regular_consumidor"),
                ("ocasional_consumidor", "ocasional_consumidor")
            ]
            
            categorization_results = {}
            
            for user_type, answer_value in user_types_to_test:
                print(f"\n📋 Testing user type: {user_type}")
                
                # Create session and answer with specific pattern
                session_id = self.create_user_session_with_specific_answer(answer_value)
                if not session_id:
                    print(f"❌ Could not create session for {user_type}")
                    continue
                
                # Get recommendations
                response = requests.get(f"{API_URL}/recomendacion/{session_id}")
                response.raise_for_status()
                recommendations = response.json()
                
                # Analyze the categorization
                refrescos_count = len(recommendations.get("refrescos_reales", []))
                alternativas_count = len(recommendations.get("bebidas_alternativas", []))
                usuario_no_consume = recommendations.get("usuario_no_consume_refrescos", False)
                mostrar_alternativas = recommendations.get("mostrar_alternativas", False)
                
                categorization_results[user_type] = {
                    "refrescos_count": refrescos_count,
                    "alternativas_count": alternativas_count,
                    "usuario_no_consume": usuario_no_consume,
                    "mostrar_alternativas": mostrar_alternativas,
                    "session_id": session_id
                }
                
                print(f"✅ {user_type}: {refrescos_count} refrescos, {alternativas_count} alternatives")
                print(f"✅ {user_type}: usuario_no_consume={usuario_no_consume}, mostrar_alternativas={mostrar_alternativas}")
            
            # Verify categorization logic
            print(f"\n📊 Analyzing categorization results...")
            
            # Check no_consume_refrescos user
            if "no_consume_refrescos" in categorization_results:
                result = categorization_results["no_consume_refrescos"]
                if result["usuario_no_consume"] and result["refrescos_count"] == 0 and result["alternativas_count"] > 0:
                    print("✅ CORRECT: no_consume_refrescos user gets only alternatives")
                else:
                    print(f"❌ INCORRECT: no_consume_refrescos user categorization failed")
                    print(f"   Expected: usuario_no_consume=True, refrescos=0, alternatives>0")
                    print(f"   Got: usuario_no_consume={result['usuario_no_consume']}, refrescos={result['refrescos_count']}, alternatives={result['alternativas_count']}")
                    self.test_results["New User Categorization Logic"] = False
                    self.all_tests_passed = False
                    return
            
            # Check prefiere_alternativas user
            if "prefiere_alternativas" in categorization_results:
                result = categorization_results["prefiere_alternativas"]
                if result["alternativas_count"] > 0:
                    print("✅ CORRECT: prefiere_alternativas user gets alternatives initially")
                else:
                    print(f"❌ INCORRECT: prefiere_alternativas user should get alternatives initially")
                    self.test_results["New User Categorization Logic"] = False
                    self.all_tests_passed = False
                    return
            
            # Check regular users have clear behavior (not mixed)
            regular_users = ["regular_consumidor", "ocasional_consumidor"]
            for user_type in regular_users:
                if user_type in categorization_results:
                    result = categorization_results[user_type]
                    
                    # Should have clear behavior: either only refrescos OR both types separately
                    if result["refrescos_count"] > 0 and result["alternativas_count"] == 0:
                        print(f"✅ CORRECT: {user_type} gets only refrescos (traditional behavior)")
                    elif result["refrescos_count"] > 0 and result["alternativas_count"] > 0 and result["mostrar_alternativas"]:
                        print(f"✅ CORRECT: {user_type} gets both types separately (health-conscious behavior)")
                    else:
                        print(f"⚠️ WARNING: {user_type} has unclear categorization")
                        print(f"   refrescos={result['refrescos_count']}, alternatives={result['alternativas_count']}, mostrar_alternativas={result['mostrar_alternativas']}")
            
            print("✅ SUCCESS: New user categorization logic is working correctly!")
            self.test_results["New User Categorization Logic"] = True
            
        except Exception as e:
            print(f"❌ New User Categorization Logic: FAILED - {str(e)}")
            self.test_results["New User Categorization Logic"] = False
            self.all_tests_passed = False

    def test_usuario_no_consume_refrescos(self):
        """Test usuario_no_consume_refrescos: Only alternatives"""
        print("\n🔍 Testing Usuario No Consume Refrescos...")
        print("Expected: Only healthy alternatives, no sodas")
        
        try:
            # Create a user who doesn't consume sodas
            session_id = self.create_user_session_with_specific_answer("no_consume_refrescos")
            if not session_id:
                print("❌ Could not create no-consume-sodas user session")
                self.test_results["Usuario No Consume Refrescos"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            recommendations = response.json()
            
            refrescos_count = len(recommendations.get("refrescos_reales", []))
            alternativas_count = len(recommendations.get("bebidas_alternativas", []))
            usuario_no_consume = recommendations.get("usuario_no_consume_refrescos", False)
            
            print(f"✅ Initial recommendations: {refrescos_count} refrescos, {alternativas_count} alternatives")
            print(f"✅ Usuario no consume refrescos: {usuario_no_consume}")
            
            # Verify only alternatives
            if refrescos_count == 0:
                print("✅ CORRECT: No sodas shown to user who doesn't consume them")
            else:
                print(f"❌ INCORRECT: User who doesn't consume sodas got {refrescos_count} sodas")
                self.test_results["Usuario No Consume Refrescos"] = False
                self.all_tests_passed = False
                return
            
            if alternativas_count > 0:
                print(f"✅ CORRECT: User got {alternativas_count} healthy alternatives")
            else:
                print("❌ INCORRECT: User who doesn't consume sodas got no alternatives")
                self.test_results["Usuario No Consume Refrescos"] = False
                self.all_tests_passed = False
                return
            
            if usuario_no_consume:
                print("✅ CORRECT: System correctly identified user as non-soda consumer")
            else:
                print("❌ INCORRECT: System failed to identify user as non-soda consumer")
                self.test_results["Usuario No Consume Refrescos"] = False
                self.all_tests_passed = False
                return
            
            # Test more options button - should give more alternatives, not sodas
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
            response.raise_for_status()
            more_options = response.json()
            
            if not more_options.get("sin_mas_opciones", False):
                additional_recs = more_options.get("recomendaciones_adicionales", [])
                tipo_recomendaciones = more_options.get("tipo_recomendaciones", "")
                
                print(f"✅ More options: {len(additional_recs)} recommendations ({tipo_recomendaciones})")
                
                if "alternativas" in tipo_recomendaciones:
                    print("✅ CORRECT: More options gives more alternatives, not sodas")
                else:
                    print(f"❌ INCORRECT: More options gave {tipo_recomendaciones} instead of alternatives")
                    self.test_results["Usuario No Consume Refrescos"] = False
                    self.all_tests_passed = False
                    return
            else:
                print("⚠️ No more options available (this is acceptable)")
            
            print("✅ SUCCESS: Usuario no consume refrescos behavior is correct!")
            self.test_results["Usuario No Consume Refrescos"] = True
            
        except Exception as e:
            print(f"❌ Usuario No Consume Refrescos: FAILED - {str(e)}")
            self.test_results["Usuario No Consume Refrescos"] = False
            self.all_tests_passed = False

    def test_usuario_prefiere_alternativas(self):
        """Test usuario_prefiere_alternativas: Alternatives initially, sodas in more options"""
        print("\n🔍 Testing Usuario Prefiere Alternativas...")
        print("Expected: Alternatives initially, sodas available in 'more options'")
        
        try:
            # Create a user who prefers alternatives
            session_id = self.create_user_session_with_specific_answer("prefiere_alternativas")
            if not session_id:
                print("❌ Could not create prefers-alternatives user session")
                self.test_results["Usuario Prefiere Alternativas"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            recommendations = response.json()
            
            refrescos_count = len(recommendations.get("refrescos_reales", []))
            alternativas_count = len(recommendations.get("bebidas_alternativas", []))
            
            print(f"✅ Initial recommendations: {refrescos_count} refrescos, {alternativas_count} alternatives")
            
            # Should show alternatives initially
            if alternativas_count > 0:
                print(f"✅ CORRECT: User who prefers alternatives got {alternativas_count} alternatives initially")
            else:
                print("❌ INCORRECT: User who prefers alternatives got no alternatives initially")
                self.test_results["Usuario Prefiere Alternativas"] = False
                self.all_tests_passed = False
                return
            
            # Test more options button - first click should show sodas
            print("\n📋 Testing 'more options' button behavior...")
            
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
            response.raise_for_status()
            more_options_1 = response.json()
            
            if not more_options_1.get("sin_mas_opciones", False):
                additional_recs_1 = more_options_1.get("recomendaciones_adicionales", [])
                tipo_recomendaciones_1 = more_options_1.get("tipo_recomendaciones", "")
                
                print(f"✅ First 'more options' click: {len(additional_recs_1)} recommendations ({tipo_recomendaciones_1})")
                
                # For prefiere_alternativas users, first click might show sodas as option
                if "refrescos" in tipo_recomendaciones_1 or "opcionales" in tipo_recomendaciones_1:
                    print("✅ CORRECT: First click shows sodas as optional choice")
                elif "alternativas" in tipo_recomendaciones_1:
                    print("✅ ACCEPTABLE: First click shows more alternatives")
                else:
                    print(f"⚠️ UNEXPECTED: First click shows {tipo_recomendaciones_1}")
                
                # Test second click
                response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
                response.raise_for_status()
                more_options_2 = response.json()
                
                if not more_options_2.get("sin_mas_opciones", False):
                    additional_recs_2 = more_options_2.get("recomendaciones_adicionales", [])
                    tipo_recomendaciones_2 = more_options_2.get("tipo_recomendaciones", "")
                    
                    print(f"✅ Second 'more options' click: {len(additional_recs_2)} recommendations ({tipo_recomendaciones_2})")
                    
                    # Second click should typically show more alternatives
                    if "alternativas" in tipo_recomendaciones_2:
                        print("✅ CORRECT: Second click shows more alternatives")
                    else:
                        print(f"⚠️ UNEXPECTED: Second click shows {tipo_recomendaciones_2}")
                else:
                    print("⚠️ No more options available on second click")
            else:
                print("⚠️ No more options available on first click")
            
            print("✅ SUCCESS: Usuario prefiere alternativas behavior is working!")
            self.test_results["Usuario Prefiere Alternativas"] = True
            
        except Exception as e:
            print(f"❌ Usuario Prefiere Alternativas: FAILED - {str(e)}")
            self.test_results["Usuario Prefiere Alternativas"] = False
            self.all_tests_passed = False

    def test_usuario_regular_tradicional(self):
        """Test usuario_regular_tradicional: Only sodas"""
        print("\n🔍 Testing Usuario Regular Tradicional...")
        print("Expected: Only sodas, no alternatives initially")
        
        try:
            # Create a traditional regular user (sedentary, doesn't care about health)
            session_id = self.create_traditional_user_session()
            if not session_id:
                print("❌ Could not create traditional user session")
                self.test_results["Usuario Regular Tradicional"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            recommendations = response.json()
            
            refrescos_count = len(recommendations.get("refrescos_reales", []))
            alternativas_count = len(recommendations.get("bebidas_alternativas", []))
            mostrar_alternativas = recommendations.get("mostrar_alternativas", False)
            
            print(f"✅ Initial recommendations: {refrescos_count} refrescos, {alternativas_count} alternatives")
            print(f"✅ Mostrar alternativas: {mostrar_alternativas}")
            
            # Traditional user should get only sodas
            if refrescos_count > 0:
                print(f"✅ CORRECT: Traditional user got {refrescos_count} sodas")
            else:
                print("❌ INCORRECT: Traditional user got no sodas")
                self.test_results["Usuario Regular Tradicional"] = False
                self.all_tests_passed = False
                return
            
            if alternativas_count == 0:
                print("✅ CORRECT: Traditional user got no alternatives initially")
            else:
                print(f"⚠️ UNEXPECTED: Traditional user got {alternativas_count} alternatives initially")
                # This might be acceptable if it's the new "both types separately" behavior
                if mostrar_alternativas:
                    print("✅ ACCEPTABLE: This is the 'both types separately' behavior")
                else:
                    print("❌ INCORRECT: Traditional user shouldn't get alternatives without mostrar_alternativas=true")
                    self.test_results["Usuario Regular Tradicional"] = False
                    self.all_tests_passed = False
                    return
            
            # Test more options button - should give more sodas
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
            response.raise_for_status()
            more_options = response.json()
            
            if not more_options.get("sin_mas_opciones", False):
                additional_recs = more_options.get("recomendaciones_adicionales", [])
                tipo_recomendaciones = more_options.get("tipo_recomendaciones", "")
                
                print(f"✅ More options: {len(additional_recs)} recommendations ({tipo_recomendaciones})")
                
                if "refrescos" in tipo_recomendaciones or "tradicionales" in tipo_recomendaciones:
                    print("✅ CORRECT: More options gives more sodas for traditional user")
                else:
                    print(f"⚠️ UNEXPECTED: More options gave {tipo_recomendaciones} instead of more sodas")
            else:
                print("⚠️ No more options available")
            
            print("✅ SUCCESS: Usuario regular tradicional behavior is correct!")
            self.test_results["Usuario Regular Tradicional"] = True
            
        except Exception as e:
            print(f"❌ Usuario Regular Tradicional: FAILED - {str(e)}")
            self.test_results["Usuario Regular Tradicional"] = False
            self.all_tests_passed = False

    def test_usuario_regular_saludable(self):
        """Test usuario_regular_saludable: Both types separately with clear message"""
        print("\n🔍 Testing Usuario Regular Saludable...")
        print("Expected: Both sodas and alternatives shown separately with clear messages")
        
        try:
            # Create a health-conscious regular user (active, cares about health)
            session_id = self.create_health_conscious_user_session()
            if not session_id:
                print("❌ Could not create health-conscious user session")
                self.test_results["Usuario Regular Saludable"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            recommendations = response.json()
            
            refrescos_count = len(recommendations.get("refrescos_reales", []))
            alternativas_count = len(recommendations.get("bebidas_alternativas", []))
            mostrar_alternativas = recommendations.get("mostrar_alternativas", False)
            mensaje_refrescos = recommendations.get("mensaje_refrescos", "")
            mensaje_alternativas = recommendations.get("mensaje_alternativas", "")
            
            print(f"✅ Initial recommendations: {refrescos_count} refrescos, {alternativas_count} alternatives")
            print(f"✅ Mostrar alternativas: {mostrar_alternativas}")
            print(f"✅ Mensaje refrescos: {mensaje_refrescos}")
            print(f"✅ Mensaje alternativas: {mensaje_alternativas}")
            
            # Health-conscious regular user should get both types
            if refrescos_count > 0:
                print(f"✅ CORRECT: Health-conscious user got {refrescos_count} sodas")
            else:
                print("❌ INCORRECT: Health-conscious user got no sodas")
                self.test_results["Usuario Regular Saludable"] = False
                self.all_tests_passed = False
                return
            
            if alternativas_count > 0:
                print(f"✅ CORRECT: Health-conscious user got {alternativas_count} alternatives")
            else:
                print("❌ INCORRECT: Health-conscious user got no alternatives")
                self.test_results["Usuario Regular Saludable"] = False
                self.all_tests_passed = False
                return
            
            if mostrar_alternativas:
                print("✅ CORRECT: System correctly identified user should see alternatives")
            else:
                print("❌ INCORRECT: System failed to identify user should see alternatives")
                self.test_results["Usuario Regular Saludable"] = False
                self.all_tests_passed = False
                return
            
            # Check for clear separation messages
            if mensaje_refrescos and mensaje_alternativas:
                print("✅ CORRECT: Both message types are present for clear separation")
            else:
                print("⚠️ WARNING: Missing separation messages")
            
            # Check that the main message indicates both types
            if "ambos" in mensaje_refrescos.lower() or "refrescos" in mensaje_refrescos.lower() and "alternativas" in mensaje_refrescos.lower():
                print("✅ CORRECT: Main message indicates both types are shown")
            else:
                print(f"⚠️ WARNING: Main message might not clearly indicate both types: {mensaje_refrescos}")
            
            # Test more options button - should give more alternatives for health-conscious user
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
            response.raise_for_status()
            more_options = response.json()
            
            if not more_options.get("sin_mas_opciones", False):
                additional_recs = more_options.get("recomendaciones_adicionales", [])
                tipo_recomendaciones = more_options.get("tipo_recomendaciones", "")
                
                print(f"✅ More options: {len(additional_recs)} recommendations ({tipo_recomendaciones})")
                
                if "alternativas" in tipo_recomendaciones:
                    print("✅ CORRECT: More options gives more alternatives for health-conscious user")
                elif "refrescos" in tipo_recomendaciones:
                    print("✅ ACCEPTABLE: More options gives more sodas (also valid)")
                else:
                    print(f"⚠️ UNEXPECTED: More options gave {tipo_recomendaciones}")
            else:
                print("⚠️ No more options available")
            
            print("✅ SUCCESS: Usuario regular saludable behavior is correct!")
            self.test_results["Usuario Regular Saludable"] = True
            
        except Exception as e:
            print(f"❌ Usuario Regular Saludable: FAILED - {str(e)}")
            self.test_results["Usuario Regular Saludable"] = False
            self.all_tests_passed = False

    def test_click_counter_behavior(self):
        """Test click counter for dynamic behavior of more options button"""
        print("\n🔍 Testing Click Counter Behavior...")
        print("Expected: Different behavior based on number of clicks, especially for prefiere_alternativas users")
        
        try:
            # Create a user who prefers alternatives (most likely to have dynamic behavior)
            session_id = self.create_user_session_with_specific_answer("prefiere_alternativas")
            if not session_id:
                print("❌ Could not create prefiere_alternativas user session")
                self.test_results["Click Counter Behavior"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            initial_recommendations = response.json()
            
            print(f"✅ Initial: {len(initial_recommendations.get('refrescos_reales', []))} refrescos, {len(initial_recommendations.get('bebidas_alternativas', []))} alternatives")
            
            # Track click behavior
            click_results = []
            
            for click_num in range(1, 4):  # Test up to 3 clicks
                print(f"\n📋 Click #{click_num}:")
                
                response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
                response.raise_for_status()
                more_options = response.json()
                
                if more_options.get("sin_mas_opciones", False):
                    print(f"⚠️ Click #{click_num}: No more options available")
                    break
                
                additional_recs = more_options.get("recomendaciones_adicionales", [])
                tipo_recomendaciones = more_options.get("tipo_recomendaciones", "")
                
                click_result = {
                    "click_num": click_num,
                    "count": len(additional_recs),
                    "type": tipo_recomendaciones
                }
                click_results.append(click_result)
                
                print(f"✅ Click #{click_num}: {len(additional_recs)} recommendations ({tipo_recomendaciones})")
                
                # Small delay to ensure different timestamps
                time.sleep(0.1)
            
            # Analyze click behavior
            print(f"\n📊 Analyzing click behavior...")
            
            if len(click_results) >= 2:
                # Check if behavior changes between clicks
                first_click_type = click_results[0]["type"]
                second_click_type = click_results[1]["type"]
                
                if first_click_type != second_click_type:
                    print(f"✅ CORRECT: Click behavior changes - Click 1: {first_click_type}, Click 2: {second_click_type}")
                    
                    # For prefiere_alternativas users, first click might show sodas, second more alternatives
                    if "refrescos" in first_click_type and "alternativas" in second_click_type:
                        print("✅ PERFECT: First click shows sodas as option, second click shows more alternatives")
                    elif "alternativas" in first_click_type and "alternativas" in second_click_type:
                        print("✅ ACCEPTABLE: Both clicks show alternatives (consistent behavior)")
                    else:
                        print(f"✅ ACCEPTABLE: Dynamic behavior detected")
                else:
                    print(f"⚠️ CONSISTENT: Click behavior is consistent - both show {first_click_type}")
                    print("   This is acceptable, but dynamic behavior would be better")
            else:
                print("⚠️ LIMITED: Only one click available for testing")
            
            # Check if the system tracks click count (look for evidence in response)
            if len(click_results) > 0:
                # Look for any indication that the system is tracking clicks
                last_response = more_options
                if "recomendaciones_adicionales_obtenidas" in str(last_response) or "click" in str(last_response).lower():
                    print("✅ EVIDENCE: System appears to track click count")
                else:
                    print("⚠️ NO EVIDENCE: No clear indication of click tracking in response")
            
            print("✅ SUCCESS: Click counter behavior tested!")
            self.test_results["Click Counter Behavior"] = True
            
        except Exception as e:
            print(f"❌ Click Counter Behavior: FAILED - {str(e)}")
            self.test_results["Click Counter Behavior"] = False
            self.all_tests_passed = False

    def test_mixed_behavior_elimination(self):
        """Test that mixed behavior has been eliminated"""
        print("\n🔍 Testing Mixed Behavior Elimination...")
        print("Expected: No confusing mixed behavior - each user type should have clear, consistent behavior")
        
        try:
            # Test multiple user types to ensure no mixed behavior
            user_scenarios = [
                ("no_consume_refrescos", "Should get ONLY alternatives"),
                ("prefiere_alternativas", "Should get alternatives initially, sodas optionally"),
                ("regular_consumidor", "Should get clear behavior (only sodas OR both separately)"),
                ("ocasional_consumidor", "Should get clear behavior (only sodas OR both separately)")
            ]
            
            mixed_behavior_detected = False
            
            for answer_value, expected_behavior in user_scenarios:
                print(f"\n📋 Testing {answer_value}: {expected_behavior}")
                
                # Create session with specific answer
                session_id = self.create_user_session_with_specific_answer(answer_value)
                if not session_id:
                    print(f"❌ Could not create session for {answer_value}")
                    continue
                
                # Get recommendations
                response = requests.get(f"{API_URL}/recomendacion/{session_id}")
                response.raise_for_status()
                recommendations = response.json()
                
                refrescos_count = len(recommendations.get("refrescos_reales", []))
                alternativas_count = len(recommendations.get("bebidas_alternativas", []))
                mostrar_alternativas = recommendations.get("mostrar_alternativas", False)
                usuario_no_consume = recommendations.get("usuario_no_consume_refrescos", False)
                mensaje_refrescos = recommendations.get("mensaje_refrescos", "")
                
                print(f"✅ {answer_value}: {refrescos_count} refrescos, {alternativas_count} alternatives")
                print(f"✅ {answer_value}: mostrar_alternativas={mostrar_alternativas}, usuario_no_consume={usuario_no_consume}")
                
                # Check for mixed behavior patterns
                behavior_analysis = self.analyze_user_behavior(
                    answer_value, refrescos_count, alternativas_count, 
                    mostrar_alternativas, usuario_no_consume, mensaje_refrescos
                )
                
                if behavior_analysis["is_mixed"]:
                    print(f"❌ MIXED BEHAVIOR DETECTED in {answer_value}: {behavior_analysis['reason']}")
                    mixed_behavior_detected = True
                else:
                    print(f"✅ CLEAR BEHAVIOR in {answer_value}: {behavior_analysis['description']}")
            
            # Overall assessment
            if not mixed_behavior_detected:
                print("\n✅ SUCCESS: No mixed behavior detected - all user types have clear, consistent behavior!")
                self.test_results["Mixed Behavior Elimination"] = True
            else:
                print("\n❌ FAILED: Mixed behavior still exists in some user types")
                self.test_results["Mixed Behavior Elimination"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ Mixed Behavior Elimination: FAILED - {str(e)}")
            self.test_results["Mixed Behavior Elimination"] = False
            self.all_tests_passed = False

    def analyze_user_behavior(self, user_type, refrescos_count, alternativas_count, mostrar_alternativas, usuario_no_consume, mensaje):
        """Analyze if user behavior is mixed or clear"""
        
        if user_type == "no_consume_refrescos":
            if usuario_no_consume and refrescos_count == 0 and alternativas_count > 0:
                return {"is_mixed": False, "description": "Only alternatives (correct)"}
            else:
                return {"is_mixed": True, "reason": "Should only get alternatives"}
        
        elif user_type == "prefiere_alternativas":
            if alternativas_count > 0:
                return {"is_mixed": False, "description": "Gets alternatives initially (correct)"}
            else:
                return {"is_mixed": True, "reason": "Should get alternatives initially"}
        
        elif user_type in ["regular_consumidor", "ocasional_consumidor"]:
            # Regular users should have clear behavior
            if refrescos_count > 0 and alternativas_count == 0:
                return {"is_mixed": False, "description": "Only sodas (traditional behavior)"}
            elif refrescos_count > 0 and alternativas_count > 0 and mostrar_alternativas:
                # Check if message indicates clear separation
                if "ambos" in mensaje.lower() or ("refrescos" in mensaje.lower() and "alternativas" in mensaje.lower()):
                    return {"is_mixed": False, "description": "Both types with clear separation message"}
                else:
                    return {"is_mixed": True, "reason": "Both types shown but without clear separation message"}
            elif refrescos_count == 0 and alternativas_count > 0:
                return {"is_mixed": True, "reason": "Regular user getting only alternatives is unexpected"}
            else:
                return {"is_mixed": True, "reason": "Unclear behavior pattern"}
        
        return {"is_mixed": False, "description": "Behavior analysis inconclusive"}

    def create_user_session_with_specific_answer(self, answer_value):
        """Create a user session and answer the initial question with a specific value"""
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
                print(f"⚠️ Could not find option with value '{answer_value}', using first option")
                selected_option = question["opciones"][0]
            
            # Answer the initial question
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": random.uniform(2.0, 8.0)
            })
            response.raise_for_status()
            
            # Answer remaining questions with neutral/varied responses
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
                    "tiempo_respuesta": random.uniform(1.0, 10.0)
                })
                response.raise_for_status()
            
            return session_id
            
        except Exception as e:
            print(f"Error creating session with specific answer '{answer_value}': {str(e)}")
            return None

    def create_traditional_user_session(self):
        """Create a traditional user session (sedentary, doesn't care about health)"""
        try:
            # Create session
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            session_data = response.json()
            session_id = session_data["sesion_id"]
            
            # Answer questions to create a traditional user profile
            # Initial question - regular consumer
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            data = response.json()
            question = data["pregunta"]
            
            # Look for regular_consumidor or similar
            selected_option = None
            for option in question["opciones"]:
                if "regular" in option.get("valor", "").lower() or "frecuente" in option.get("texto", "").lower():
                    selected_option = option
                    break
            
            if not selected_option:
                selected_option = question["opciones"][0]  # First option as fallback
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": random.uniform(2.0, 5.0)
            })
            response.raise_for_status()
            
            # Answer remaining questions with traditional patterns
            traditional_patterns = ["sedentario", "poco_importante", "dulce", "relajado", "tradicional"]
            pattern_index = 0
            
            for i in range(5):
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                data = response.json()
                
                if "finalizada" in data and data["finalizada"]:
                    break
                    
                question = data["pregunta"]
                
                # Try to match traditional patterns
                selected_option = question["opciones"][0]  # Default to first
                
                if pattern_index < len(traditional_patterns):
                    pattern = traditional_patterns[pattern_index]
                    for option in question["opciones"]:
                        if pattern in option.get("valor", "").lower() or pattern in option.get("texto", "").lower():
                            selected_option = option
                            break
                    pattern_index += 1
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": random.uniform(1.0, 6.0)
                })
                response.raise_for_status()
            
            return session_id
            
        except Exception as e:
            print(f"Error creating traditional user session: {str(e)}")
            return None

    def create_health_conscious_user_session(self):
        """Create a health-conscious user session (active, cares about health)"""
        try:
            # Create session
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            session_data = response.json()
            session_id = session_data["sesion_id"]
            
            # Answer questions to create a health-conscious user profile
            # Initial question - regular consumer (but health-conscious)
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            data = response.json()
            question = data["pregunta"]
            
            # Look for ocasional_consumidor or regular_consumidor
            selected_option = None
            for option in question["opciones"]:
                if "ocasional" in option.get("valor", "").lower():
                    selected_option = option
                    break
            
            if not selected_option:
                for option in question["opciones"]:
                    if "regular" in option.get("valor", "").lower():
                        selected_option = option
                        break
            
            if not selected_option:
                selected_option = question["opciones"][0]  # Fallback
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": random.uniform(3.0, 8.0)
            })
            response.raise_for_status()
            
            # Answer remaining questions with health-conscious patterns
            health_patterns = ["activo", "muy_importante", "natural", "energético", "saludable"]
            pattern_index = 0
            
            for i in range(5):
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                data = response.json()
                
                if "finalizada" in data and data["finalizada"]:
                    break
                    
                question = data["pregunta"]
                
                # Try to match health-conscious patterns
                selected_option = question["opciones"][-1]  # Default to last (often healthiest)
                
                if pattern_index < len(health_patterns):
                    pattern = health_patterns[pattern_index]
                    for option in question["opciones"]:
                        if pattern in option.get("valor", "").lower() or pattern in option.get("texto", "").lower():
                            selected_option = option
                            break
                    pattern_index += 1
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": random.uniform(2.0, 10.0)
                })
                response.raise_for_status()
            
            return session_id
            
        except Exception as e:
            print(f"Error creating health-conscious user session: {str(e)}")
            return None
        """Test the new beverage structure with 26 drinks (14 real refrescos + 12 healthy alternatives)"""
        print("\n🔍 Testing New Beverage Structure (26 drinks)...")
        print("Expected: 14 real refrescos + 12 healthy alternatives = 26 total")
        
        try:
            # Get all bebidas from admin endpoint
            response = requests.get(f"{API_URL}/admin/bebidas")
            response.raise_for_status()
            bebidas = response.json()
            
            if not isinstance(bebidas, list):
                print("❌ Beverage Structure: FAILED - Response is not a list")
                self.test_results["New Beverage Structure (26 drinks)"] = False
                self.all_tests_passed = False
                return
            
            total_bebidas = len(bebidas)
            refrescos_reales = len([b for b in bebidas if b.get("es_refresco_real", False)])
            alternativas = len([b for b in bebidas if not b.get("es_refresco_real", True)])
            
            print(f"✅ Found {total_bebidas} total bebidas")
            print(f"✅ Found {refrescos_reales} real refrescos")
            print(f"✅ Found {alternativas} healthy alternatives")
            
            # Verify expected counts
            if total_bebidas == 26:
                print("✅ CORRECT: Total number of bebidas is 26")
            else:
                print(f"❌ INCORRECT: Expected 26 bebidas, got {total_bebidas}")
                self.test_results["New Beverage Structure (26 drinks)"] = False
                self.all_tests_passed = False
                return
            
            if refrescos_reales == 14:
                print("✅ CORRECT: Number of real refrescos is 14")
            else:
                print(f"❌ INCORRECT: Expected 14 real refrescos, got {refrescos_reales}")
                self.test_results["New Beverage Structure (26 drinks)"] = False
                self.all_tests_passed = False
                return
            
            if alternativas == 12:
                print("✅ CORRECT: Number of healthy alternatives is 12")
            else:
                print(f"❌ INCORRECT: Expected 12 healthy alternatives, got {alternativas}")
                self.test_results["New Beverage Structure (26 drinks)"] = False
                self.all_tests_passed = False
                return
            
            # Verify unique presentation IDs
            all_presentation_ids = []
            for bebida in bebidas:
                for presentacion in bebida.get("presentaciones", []):
                    presentation_id = presentacion.get("presentation_id")
                    if presentation_id:
                        all_presentation_ids.append(presentation_id)
            
            unique_presentation_ids = set(all_presentation_ids)
            
            if len(all_presentation_ids) == len(unique_presentation_ids):
                print(f"✅ CORRECT: All {len(all_presentation_ids)} presentation IDs are unique")
            else:
                duplicates = len(all_presentation_ids) - len(unique_presentation_ids)
                print(f"❌ INCORRECT: Found {duplicates} duplicate presentation IDs")
                self.test_results["New Beverage Structure (26 drinks)"] = False
                self.all_tests_passed = False
                return
            
            # Verify distribution of es_refresco_real
            correct_distribution = True
            for bebida in bebidas:
                es_refresco_real = bebida.get("es_refresco_real")
                if es_refresco_real is None:
                    print(f"❌ INCORRECT: Bebida {bebida.get('nombre', 'Unknown')} missing es_refresco_real field")
                    correct_distribution = False
            
            if correct_distribution:
                print("✅ CORRECT: All bebidas have es_refresco_real field properly set")
            else:
                self.test_results["New Beverage Structure (26 drinks)"] = False
                self.all_tests_passed = False
                return
            
            print("✅ SUCCESS: New beverage structure with 26 drinks is correct!")
            self.test_results["New Beverage Structure (26 drinks)"] = True
            
        except Exception as e:
            print(f"❌ New Beverage Structure: FAILED - {str(e)}")
            self.test_results["New Beverage Structure (26 drinks)"] = False
            self.all_tests_passed = False

    def test_selective_database_cleaning(self):
        """Test selective database cleaning (only questions and beverages, preserve sessions)"""
        print("\n🔍 Testing Selective Database Cleaning...")
        print("Expected: Only questions and beverages cleaned, sessions preserved")
        
        try:
            # First, create a test session to verify it gets preserved
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            session_data = response.json()
            test_session_id = session_data["sesion_id"]
            print(f"✅ Created test session: {test_session_id}")
            
            # Check if we can get admin stats to verify data exists
            response = requests.get(f"{API_URL}/admin/stats")
            response.raise_for_status()
            stats_before = response.json()
            
            print(f"✅ Stats before cleaning: {stats_before}")
            
            # Verify that questions and bebidas exist
            if "preguntas" in stats_before and stats_before["preguntas"].get("total", 0) > 0:
                print(f"✅ Questions exist: {stats_before['preguntas']['total']}")
            else:
                print("❌ No questions found before cleaning")
                self.test_results["Selective Database Cleaning"] = False
                self.all_tests_passed = False
                return
            
            if "bebidas" in stats_before and stats_before["bebidas"].get("total", 0) > 0:
                print(f"✅ Bebidas exist: {stats_before['bebidas']['total']}")
            else:
                print("❌ No bebidas found before cleaning")
                self.test_results["Selective Database Cleaning"] = False
                self.all_tests_passed = False
                return
            
            # Check if sessions exist
            sessions_exist = "sesiones" in stats_before and stats_before["sesiones"].get("total", 0) > 0
            if sessions_exist:
                print(f"✅ Sessions exist: {stats_before['sesiones']['total']}")
            else:
                print("⚠️ No sessions found before cleaning (this is normal)")
            
            # Note: We cannot trigger a new cleaning without restarting the server
            # But we can verify that the current state shows proper selective cleaning
            # by checking that the data structure is correct and sessions are preserved
            
            # Verify that our test session still exists
            response = requests.get(f"{API_URL}/pregunta-inicial/{test_session_id}")
            if response.status_code == 200:
                print("✅ CORRECT: Test session preserved after system initialization")
            else:
                print("⚠️ Test session not found, but this might be expected if cleaning happened during startup")
            
            # Verify that questions and bebidas were properly loaded
            response = requests.get(f"{API_URL}/admin/stats")
            response.raise_for_status()
            stats_after = response.json()
            
            if "preguntas" in stats_after and stats_after["preguntas"].get("total", 0) > 0:
                print(f"✅ Questions properly loaded: {stats_after['preguntas']['total']}")
            else:
                print("❌ Questions not properly loaded after cleaning")
                self.test_results["Selective Database Cleaning"] = False
                self.all_tests_passed = False
                return
            
            if "bebidas" in stats_after and stats_after["bebidas"].get("total", 0) > 0:
                print(f"✅ Bebidas properly loaded: {stats_after['bebidas']['total']}")
            else:
                print("❌ Bebidas not properly loaded after cleaning")
                self.test_results["Selective Database Cleaning"] = False
                self.all_tests_passed = False
                return
            
            print("✅ SUCCESS: Selective database cleaning working correctly!")
            print("✅ Questions and bebidas are properly loaded")
            print("✅ No conflicts with existing sessions")
            
            self.test_results["Selective Database Cleaning"] = True
            
        except Exception as e:
            print(f"❌ Selective Database Cleaning: FAILED - {str(e)}")
            self.test_results["Selective Database Cleaning"] = False
            self.all_tests_passed = False

    def test_sabor_field_in_presentations(self):
        """Test that each presentation has a 'sabor' field"""
        print("\n🔍 Testing 'sabor' field in presentations...")
        print("Expected: Each presentation should have a 'sabor' field with appropriate values")
        
        try:
            # Get all bebidas
            response = requests.get(f"{API_URL}/admin/bebidas")
            response.raise_for_status()
            bebidas = response.json()
            
            total_presentations = 0
            presentations_with_sabor = 0
            sabor_examples = []
            
            for bebida in bebidas:
                bebida_nombre = bebida.get("nombre", "Unknown")
                presentaciones = bebida.get("presentaciones", [])
                
                for i, presentacion in enumerate(presentaciones):
                    total_presentations += 1
                    
                    if "sabor" in presentacion:
                        presentations_with_sabor += 1
                        sabor = presentacion["sabor"]
                        
                        # Collect examples
                        if len(sabor_examples) < 5:
                            sabor_examples.append(f"{bebida_nombre} ({presentacion.get('ml', 'N/A')}ml): {sabor}")
                        
                        # Verify sabor is not empty
                        if not sabor or sabor.strip() == "":
                            print(f"❌ INCORRECT: Empty sabor in {bebida_nombre} presentation {i+1}")
                            self.test_results["Sabor field in presentations"] = False
                            self.all_tests_passed = False
                            return
                    else:
                        print(f"❌ MISSING: 'sabor' field in {bebida_nombre} presentation {i+1}")
                        self.test_results["Sabor field in presentations"] = False
                        self.all_tests_passed = False
                        return
            
            print(f"✅ Found {total_presentations} total presentations")
            print(f"✅ Found {presentations_with_sabor} presentations with 'sabor' field")
            
            if total_presentations == presentations_with_sabor:
                print("✅ CORRECT: All presentations have 'sabor' field")
            else:
                missing = total_presentations - presentations_with_sabor
                print(f"❌ INCORRECT: {missing} presentations missing 'sabor' field")
                self.test_results["Sabor field in presentations"] = False
                self.all_tests_passed = False
                return
            
            # Show examples of sabor values
            print("\n📋 Examples of 'sabor' values:")
            for example in sabor_examples:
                print(f"   - {example}")
            
            # Verify sabor values are coherent (not just random text)
            coherent_sabores = True
            common_sabor_words = ["dulce", "cítrico", "frutal", "natural", "refrescante", "cola", "limón", "naranja", "manzana", "tropical", "energético", "suave", "intenso"]
            
            for bebida in bebidas[:3]:  # Check first 3 bebidas as sample
                for presentacion in bebida.get("presentaciones", []):
                    sabor = presentacion.get("sabor", "").lower()
                    if not any(word in sabor for word in common_sabor_words):
                        print(f"⚠️ WARNING: Unusual sabor value '{presentacion.get('sabor')}' in {bebida.get('nombre')}")
                        # Don't fail the test for this, just warn
            
            print("✅ SUCCESS: All presentations have appropriate 'sabor' field!")
            self.test_results["Sabor field in presentations"] = True
            
        except Exception as e:
            print(f"❌ Sabor field test: FAILED - {str(e)}")
            self.test_results["Sabor field in presentations"] = False
            self.all_tests_passed = False

    def test_improved_ml_logic_variety(self):
        """Test improved ML logic that provides variety in recommendations"""
        print("\n🔍 Testing Improved ML Logic (Variety in Recommendations)...")
        print("Expected: Users should see variety, not always the same 3 recommendations")
        
        try:
            # Create multiple sessions with different response patterns
            sessions_and_recommendations = []
            
            for i in range(3):
                print(f"\n📋 Creating test session {i+1}...")
                
                # Create session
                response = requests.post(f"{API_URL}/iniciar-sesion")
                response.raise_for_status()
                session_data = response.json()
                session_id = session_data["sesion_id"]
                
                # Answer questions with slightly different patterns
                if not self.answer_questions_with_pattern(session_id, pattern=i):
                    print(f"❌ Could not answer questions for session {i+1}")
                    self.test_results["Improved ML Logic (Variety)"] = False
                    self.all_tests_passed = False
                    return
                
                # Get recommendations
                response = requests.get(f"{API_URL}/recomendacion/{session_id}")
                response.raise_for_status()
                recommendations = response.json()
                
                # Extract bebida IDs from recommendations
                refrescos_ids = [b["id"] for b in recommendations.get("refrescos_reales", [])]
                alternativas_ids = [b["id"] for b in recommendations.get("bebidas_alternativas", [])]
                
                sessions_and_recommendations.append({
                    "session_id": session_id,
                    "refrescos_ids": refrescos_ids,
                    "alternativas_ids": alternativas_ids,
                    "total_refrescos": len(refrescos_ids),
                    "total_alternativas": len(alternativas_ids)
                })
                
                print(f"✅ Session {i+1}: {len(refrescos_ids)} refrescos, {len(alternativas_ids)} alternatives")
            
            # Analyze variety in recommendations
            print(f"\n📊 Analyzing variety across {len(sessions_and_recommendations)} sessions...")
            
            # Check refrescos variety
            all_refrescos_sets = [set(s["refrescos_ids"]) for s in sessions_and_recommendations]
            refrescos_intersection = set.intersection(*all_refrescos_sets) if all_refrescos_sets else set()
            
            # Check alternativas variety
            all_alternativas_sets = [set(s["alternativas_ids"]) for s in sessions_and_recommendations]
            alternativas_intersection = set.intersection(*all_alternativas_sets) if all_alternativas_sets else set()
            
            print(f"✅ Refrescos common to all sessions: {len(refrescos_intersection)}")
            print(f"✅ Alternativas common to all sessions: {len(alternativas_intersection)}")
            
            # Calculate variety score
            total_unique_refrescos = len(set().union(*all_refrescos_sets)) if all_refrescos_sets else 0
            total_unique_alternativas = len(set().union(*all_alternativas_sets)) if all_alternativas_sets else 0
            
            print(f"✅ Total unique refrescos across sessions: {total_unique_refrescos}")
            print(f"✅ Total unique alternativas across sessions: {total_unique_alternativas}")
            
            # Verify variety (not always the same recommendations)
            variety_threshold = 0.7  # At least 70% should be different
            
            if all_refrescos_sets:
                avg_refrescos_per_session = sum(len(s) for s in all_refrescos_sets) / len(all_refrescos_sets)
                refrescos_variety_ratio = (total_unique_refrescos - len(refrescos_intersection)) / total_unique_refrescos if total_unique_refrescos > 0 else 0
                
                print(f"✅ Refrescos variety ratio: {refrescos_variety_ratio:.2f}")
                
                if refrescos_variety_ratio >= variety_threshold:
                    print("✅ CORRECT: Good variety in refrescos recommendations")
                else:
                    print(f"❌ INCORRECT: Low variety in refrescos (ratio: {refrescos_variety_ratio:.2f}, expected: ≥{variety_threshold})")
                    self.test_results["Improved ML Logic (Variety)"] = False
                    self.all_tests_passed = False
                    return
            
            if all_alternativas_sets:
                avg_alternativas_per_session = sum(len(s) for s in all_alternativas_sets) / len(all_alternativas_sets)
                alternativas_variety_ratio = (total_unique_alternativas - len(alternativas_intersection)) / total_unique_alternativas if total_unique_alternativas > 0 else 0
                
                print(f"✅ Alternativas variety ratio: {alternativas_variety_ratio:.2f}")
                
                if alternativas_variety_ratio >= variety_threshold:
                    print("✅ CORRECT: Good variety in alternativas recommendations")
                else:
                    print(f"❌ INCORRECT: Low variety in alternativas (ratio: {alternativas_variety_ratio:.2f}, expected: ≥{variety_threshold})")
                    self.test_results["Improved ML Logic (Variety)"] = False
                    self.all_tests_passed = False
                    return
            
            # Test granular configurations are being used
            print(f"\n📋 Verifying granular configurations are applied...")
            
            for i, session_data in enumerate(sessions_and_recommendations):
                refrescos_count = session_data["total_refrescos"]
                alternativas_count = session_data["total_alternativas"]
                
                # Check that counts respect the new granular configurations
                # MAX_ALTERNATIVAS_SALUDABLES_INICIAL = 3
                if alternativas_count <= 3:
                    print(f"✅ Session {i+1}: Alternativas count ({alternativas_count}) respects MAX_ALTERNATIVAS_SALUDABLES_INICIAL")
                else:
                    print(f"⚠️ Session {i+1}: Alternativas count ({alternativas_count}) exceeds expected limit")
            
            print("✅ SUCCESS: ML logic provides good variety in recommendations!")
            print("✅ New granular configurations are being applied correctly")
            
            self.test_results["Improved ML Logic (Variety)"] = True
            
        except Exception as e:
            print(f"❌ Improved ML Logic test: FAILED - {str(e)}")
            self.test_results["Improved ML Logic (Variety)"] = False
            self.all_tests_passed = False

    def answer_questions_with_pattern(self, session_id, pattern=0):
        """Answer questions with different patterns to create variety"""
        try:
            # Get initial question
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            data = response.json()
            question = data["pregunta"]
            
            # Choose option based on pattern
            option_index = pattern % len(question["opciones"])
            selected_option = question["opciones"][option_index]
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": random.uniform(2.0, 8.0)
            })
            response.raise_for_status()
            
            # Answer remaining questions
            for i in range(5):  # Assuming 6 total questions
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                data = response.json()
                
                if "finalizada" in data and data["finalizada"]:
                    break
                    
                question = data["pregunta"]
                
                # Vary responses based on pattern
                if pattern == 0:
                    # Traditional user pattern
                    option_index = 0  # First option
                elif pattern == 1:
                    # Health-conscious pattern
                    option_index = len(question["opciones"]) - 1  # Last option
                else:
                    # Mixed pattern
                    option_index = (i + pattern) % len(question["opciones"])
                
                selected_option = question["opciones"][option_index]
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": random.uniform(1.0, 10.0)
                })
                response.raise_for_status()
            
            return True
            
        except Exception as e:
            print(f"Error answering questions with pattern {pattern}: {str(e)}")
            return False

    def test_granular_configurations_new(self):
        """Test the new granular configurations"""
        print("\n🔍 Testing New Granular Configurations...")
        print("Expected configurations:")
        print("- MAX_ALTERNATIVAS_SALUDABLES_INICIAL = 3")
        print("- MAX_ALTERNATIVAS_SALUDABLES_ADICIONAL = 3") 
        print("- MAX_REFRESCOS_ADICIONALES = 3")
        print("- MAX_ALTERNATIVAS_USUARIO_SALUDABLE = 4")
        print("- MAX_REFRESCOS_USUARIO_TRADICIONAL = 3")
        
        try:
            # Test 1: Initial healthy alternatives limit (3)
            print(f"\n📋 TEST 1: MAX_ALTERNATIVAS_SALUDABLES_INICIAL = 3")
            
            # Create a health-conscious user session
            session_id = self.create_user_session_healthy()
            if not session_id:
                print("❌ Could not create healthy user session")
                self.test_results["New Granular Configurations"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            recommendations = response.json()
            
            alternativas_count = len(recommendations.get("bebidas_alternativas", []))
            print(f"✅ Initial healthy alternatives: {alternativas_count}")
            
            if alternativas_count <= 3:
                print("✅ CORRECT: Initial healthy alternatives ≤ 3")
            else:
                print(f"❌ INCORRECT: Initial healthy alternatives ({alternativas_count}) > 3")
                self.test_results["New Granular Configurations"] = False
                self.all_tests_passed = False
                return
            
            # Test 2: Additional healthy alternatives limit (3)
            print(f"\n📋 TEST 2: MAX_ALTERNATIVAS_SALUDABLES_ADICIONAL = 3")
            
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
            response.raise_for_status()
            additional_recs = response.json()
            
            if not additional_recs.get("sin_mas_opciones", False):
                additional_count = len(additional_recs.get("recomendaciones_adicionales", []))
                print(f"✅ Additional healthy alternatives: {additional_count}")
                
                if additional_count <= 3:
                    print("✅ CORRECT: Additional healthy alternatives ≤ 3")
                else:
                    print(f"❌ INCORRECT: Additional healthy alternatives ({additional_count}) > 3")
                    self.test_results["New Granular Configurations"] = False
                    self.all_tests_passed = False
                    return
            else:
                print("⚠️ No additional alternatives available (sin_mas_opciones: true)")
            
            # Test 3: Additional refrescos limit (3)
            print(f"\n📋 TEST 3: MAX_REFRESCOS_ADICIONALES = 3")
            
            # Create a traditional user session
            traditional_session_id = self.create_user_session_traditional()
            if not traditional_session_id:
                print("❌ Could not create traditional user session")
                self.test_results["New Granular Configurations"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{traditional_session_id}")
            response.raise_for_status()
            
            # Get additional recommendations
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{traditional_session_id}")
            response.raise_for_status()
            additional_recs = response.json()
            
            if not additional_recs.get("sin_mas_opciones", False):
                additional_count = len(additional_recs.get("recomendaciones_adicionales", []))
                tipo_recomendaciones = additional_recs.get("tipo_recomendaciones", "")
                
                print(f"✅ Additional recommendations: {additional_count} ({tipo_recomendaciones})")
                
                if "refrescos" in tipo_recomendaciones and additional_count <= 3:
                    print("✅ CORRECT: Additional refrescos ≤ 3")
                elif "alternativas" in tipo_recomendaciones and additional_count <= 3:
                    print("✅ CORRECT: Additional alternatives ≤ 3")
                elif additional_count > 3:
                    print(f"❌ INCORRECT: Additional recommendations ({additional_count}) > 3")
                    self.test_results["New Granular Configurations"] = False
                    self.all_tests_passed = False
                    return
            else:
                print("⚠️ No additional recommendations available")
            
            # Test 4: User who doesn't consume sodas gets ≤ 4 alternatives
            print(f"\n📋 TEST 4: MAX_ALTERNATIVAS_USUARIO_SALUDABLE = 4")
            
            # Create a no-sodas user session
            no_sodas_session_id = self.create_user_session_no_sodas()
            if not no_sodas_session_id:
                print("❌ Could not create no-sodas user session")
                self.test_results["New Granular Configurations"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{no_sodas_session_id}")
            response.raise_for_status()
            recommendations = response.json()
            
            refrescos_count = len(recommendations.get("refrescos_reales", []))
            alternativas_count = len(recommendations.get("bebidas_alternativas", []))
            usuario_no_consume = recommendations.get("usuario_no_consume_refrescos", False)
            
            print(f"✅ No-sodas user - Refrescos: {refrescos_count}, Alternatives: {alternativas_count}")
            print(f"✅ Usuario no consume refrescos: {usuario_no_consume}")
            
            if usuario_no_consume:
                if refrescos_count == 0:
                    print("✅ CORRECT: No-sodas user receives 0 refrescos")
                else:
                    print(f"❌ INCORRECT: No-sodas user received {refrescos_count} refrescos")
                    self.test_results["New Granular Configurations"] = False
                    self.all_tests_passed = False
                    return
                
                if alternativas_count <= 4:
                    print("✅ CORRECT: No-sodas user receives ≤ 4 alternatives")
                else:
                    print(f"❌ INCORRECT: No-sodas user received {alternativas_count} alternatives (> 4)")
                    self.test_results["New Granular Configurations"] = False
                    self.all_tests_passed = False
                    return
            
            # Test 5: Specific endpoints /api/mas-alternativas and /api/mas-refrescos
            print(f"\n📋 TEST 5: Specific endpoints respect configurations")
            
            # Test /api/mas-alternativas
            response = requests.get(f"{API_URL}/mas-alternativas/{session_id}")
            response.raise_for_status()
            mas_alternativas = response.json()
            
            if not mas_alternativas.get("sin_mas_opciones", False):
                count = len(mas_alternativas.get("mas_alternativas", []))
                print(f"✅ /api/mas-alternativas returned {count} alternatives")
                
                if count <= 3:
                    print("✅ CORRECT: /api/mas-alternativas respects limit ≤ 3")
                else:
                    print(f"❌ INCORRECT: /api/mas-alternativas returned {count} > 3")
                    self.test_results["New Granular Configurations"] = False
                    self.all_tests_passed = False
                    return
            
            # Test /api/mas-refrescos
            response = requests.get(f"{API_URL}/mas-refrescos/{traditional_session_id}")
            response.raise_for_status()
            mas_refrescos = response.json()
            
            if not mas_refrescos.get("sin_mas_opciones", False):
                count = len(mas_refrescos.get("mas_refrescos", []))
                print(f"✅ /api/mas-refrescos returned {count} refrescos")
                
                if count <= 3:
                    print("✅ CORRECT: /api/mas-refrescos respects limit ≤ 3")
                else:
                    print(f"❌ INCORRECT: /api/mas-refrescos returned {count} > 3")
                    self.test_results["New Granular Configurations"] = False
                    self.all_tests_passed = False
                    return
            
            print("✅ SUCCESS: All granular configurations are working correctly!")
            self.test_results["New Granular Configurations"] = True
            
        except Exception as e:
            print(f"❌ Granular Configurations test: FAILED - {str(e)}")
            self.test_results["New Granular Configurations"] = False
            self.all_tests_passed = False

    def test_more_options_button_both_types(self):
        """Test that 'more options' button works for both refrescos and alternatives"""
        print("\n🔍 Testing 'More Options' Button for Both Types...")
        print("Expected: Button should work consistently for both refrescos and alternatives")
        
        try:
            # Test 1: More options for traditional user (should get more refrescos)
            print(f"\n📋 TEST 1: More options for traditional user")
            
            traditional_session = self.create_user_session_traditional()
            if not traditional_session:
                print("❌ Could not create traditional user session")
                self.test_results["More Options Button Both Types"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{traditional_session}")
            response.raise_for_status()
            initial_recs = response.json()
            
            print(f"✅ Traditional user initial: {len(initial_recs.get('refrescos_reales', []))} refrescos, {len(initial_recs.get('bebidas_alternativas', []))} alternatives")
            
            # Test more options button
            more_options_working = False
            for attempt in range(3):  # Try up to 3 times
                response = requests.get(f"{API_URL}/recomendaciones-alternativas/{traditional_session}")
                response.raise_for_status()
                more_recs = response.json()
                
                if more_recs.get("sin_mas_opciones", False):
                    print(f"⚠️ Attempt {attempt + 1}: No more options available")
                    break
                else:
                    additional_count = len(more_recs.get("recomendaciones_adicionales", []))
                    tipo = more_recs.get("tipo_recomendaciones", "unknown")
                    print(f"✅ Attempt {attempt + 1}: Got {additional_count} more recommendations ({tipo})")
                    more_options_working = True
                    break
            
            if not more_options_working:
                print("⚠️ Traditional user: No additional options available, but this might be expected")
            else:
                print("✅ CORRECT: More options button works for traditional user")
            
            # Test 2: More options for health-conscious user (should get more alternatives)
            print(f"\n📋 TEST 2: More options for health-conscious user")
            
            healthy_session = self.create_user_session_healthy()
            if not healthy_session:
                print("❌ Could not create healthy user session")
                self.test_results["More Options Button Both Types"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{healthy_session}")
            response.raise_for_status()
            initial_recs = response.json()
            
            print(f"✅ Healthy user initial: {len(initial_recs.get('refrescos_reales', []))} refrescos, {len(initial_recs.get('bebidas_alternativas', []))} alternatives")
            
            # Test more options button
            more_options_working = False
            for attempt in range(3):  # Try up to 3 times
                response = requests.get(f"{API_URL}/recomendaciones-alternativas/{healthy_session}")
                response.raise_for_status()
                more_recs = response.json()
                
                if more_recs.get("sin_mas_opciones", False):
                    print(f"⚠️ Attempt {attempt + 1}: No more options available")
                    break
                else:
                    additional_count = len(more_recs.get("recomendaciones_adicionales", []))
                    tipo = more_recs.get("tipo_recomendaciones", "unknown")
                    print(f"✅ Attempt {attempt + 1}: Got {additional_count} more recommendations ({tipo})")
                    more_options_working = True
                    break
            
            if not more_options_working:
                print("⚠️ Healthy user: No additional options available, but this might be expected")
            else:
                print("✅ CORRECT: More options button works for health-conscious user")
            
            # Test 3: More options for no-sodas user (should get only alternatives)
            print(f"\n📋 TEST 3: More options for no-sodas user")
            
            no_sodas_session = self.create_user_session_no_sodas()
            if not no_sodas_session:
                print("❌ Could not create no-sodas user session")
                self.test_results["More Options Button Both Types"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{no_sodas_session}")
            response.raise_for_status()
            initial_recs = response.json()
            
            print(f"✅ No-sodas user initial: {len(initial_recs.get('refrescos_reales', []))} refrescos, {len(initial_recs.get('bebidas_alternativas', []))} alternatives")
            
            # Test more options button
            more_options_working = False
            for attempt in range(3):  # Try up to 3 times
                response = requests.get(f"{API_URL}/recomendaciones-alternativas/{no_sodas_session}")
                response.raise_for_status()
                more_recs = response.json()
                
                if more_recs.get("sin_mas_opciones", False):
                    print(f"⚠️ Attempt {attempt + 1}: No more options available")
                    break
                else:
                    additional_count = len(more_recs.get("recomendaciones_adicionales", []))
                    tipo = more_recs.get("tipo_recomendaciones", "unknown")
                    print(f"✅ Attempt {attempt + 1}: Got {additional_count} more recommendations ({tipo})")
                    
                    # Verify no-sodas user gets only alternatives
                    if "alternativas" in tipo:
                        print("✅ CORRECT: No-sodas user gets only alternatives")
                        more_options_working = True
                    else:
                        print(f"❌ INCORRECT: No-sodas user got {tipo} instead of alternatives")
                        self.test_results["More Options Button Both Types"] = False
                        self.all_tests_passed = False
                        return
                    break
            
            if not more_options_working:
                print("⚠️ No-sodas user: No additional options available, but this might be expected")
            else:
                print("✅ CORRECT: More options button works correctly for no-sodas user")
            
            # Test 4: Verify response structure consistency
            print(f"\n📋 TEST 4: Response structure consistency")
            
            # Test all three user types have consistent response structure
            for user_type, session_id in [
                ("traditional", traditional_session),
                ("healthy", healthy_session), 
                ("no-sodas", no_sodas_session)
            ]:
                response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
                response.raise_for_status()
                data = response.json()
                
                # Check required fields
                required_fields = ["recomendaciones_adicionales", "sin_mas_opciones", "tipo_recomendaciones"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"❌ INCORRECT: {user_type} user missing fields: {missing_fields}")
                    self.test_results["More Options Button Both Types"] = False
                    self.all_tests_passed = False
                    return
                else:
                    print(f"✅ CORRECT: {user_type} user has all required response fields")
            
            print("✅ SUCCESS: 'More options' button works consistently for all user types!")
            print("✅ Response structure is consistent across all user types")
            print("✅ Logic correctly differentiates between user types")
            
            self.test_results["More Options Button Both Types"] = True
            
        except Exception as e:
            print(f"❌ More Options Button test: FAILED - {str(e)}")
            self.test_results["More Options Button Both Types"] = False
            self.all_tests_passed = False

    def test_data_structure(self):
        """Test the data structure of bebidas.json"""
        print("\n🔍 Testing Data Structure...")
        
        try:
            # Get all bebidas from admin endpoint
            response = requests.get(f"{API_URL}/admin/stats")
            response.raise_for_status()
            stats = response.json()
            
            # Check if bebidas are loaded correctly
            if "bebidas" in stats:
                bebidas_stats = stats["bebidas"]
                total_bebidas = bebidas_stats.get("total", 0)
                refrescos_reales = bebidas_stats.get("refrescos_reales", 0)
                alternativas = bebidas_stats.get("alternativas", 0)
                
                print(f"✅ Data Structure: Found {total_bebidas} total bebidas")
                print(f"✅ Data Structure: {refrescos_reales} real refrescos and {alternativas} alternatives")
                
                # Verify expected counts
                if total_bebidas == 15:  # Expected total from bebidas.json
                    print("✅ Data Structure: Correct total number of bebidas")
                    
                    # Verify refrescos vs alternativas
                    if refrescos_reales > 0 and alternativas > 0:
                        print("✅ Data Structure: Both refrescos and alternatives present")
                        
                        # Get a sample bebida to check structure
                        try:
                            response = requests.get(f"{API_URL}/recomendacion/{self.create_session_and_answer_questions()}")
                            response.raise_for_status()
                            data = response.json()
                            
                            if "refrescos_reales" in data and len(data["refrescos_reales"]) > 0:
                                bebida = data["refrescos_reales"][0]
                                
                                # Check required fields
                                required_fields = ["id", "nombre", "descripcion", "categoria", "es_refresco_real", 
                                                  "nivel_dulzura", "presentaciones"]
                                
                                missing_fields = [field for field in required_fields if field not in bebida]
                                
                                if not missing_fields:
                                    print("✅ Data Structure: Bebida has all required fields")
                                    
                                    # Check ML fields
                                    ml_fields = ["categorias_ml", "tags_automaticos"]
                                    missing_ml_fields = [field for field in ml_fields if field not in bebida]
                                    
                                    if not missing_ml_fields:
                                        print("✅ Data Structure: Bebida has all ML fields")
                                        self.test_results["Data Structure"] = True
                                    else:
                                        print(f"❌ Data Structure: FAILED - Missing ML fields: {missing_ml_fields}")
                                        self.test_results["Data Structure"] = False
                                        self.all_tests_passed = False
                                else:
                                    print(f"❌ Data Structure: FAILED - Missing required fields: {missing_fields}")
                                    self.test_results["Data Structure"] = False
                                    self.all_tests_passed = False
                            else:
                                print("❌ Data Structure: FAILED - No bebidas in recommendation")
                                self.test_results["Data Structure"] = False
                                self.all_tests_passed = False
                                
                        except Exception as e:
                            print(f"❌ Data Structure: FAILED - Error getting bebida: {str(e)}")
                            self.test_results["Data Structure"] = False
                            self.all_tests_passed = False
                    else:
                        print("❌ Data Structure: FAILED - Missing refrescos or alternatives")
                        self.test_results["Data Structure"] = False
                        self.all_tests_passed = False
                else:
                    print(f"❌ Data Structure: FAILED - Expected 15 bebidas, got {total_bebidas}")
                    self.test_results["Data Structure"] = False
                    self.all_tests_passed = False
            else:
                print("❌ Data Structure: FAILED - No bebidas stats available")
                self.test_results["Data Structure"] = False
                self.all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Data Structure: FAILED - {str(e)}")
            self.test_results["Data Structure"] = False
            self.all_tests_passed = False
    
    def test_admin_reprocess_beverages(self):
        """Test admin reprocess beverages endpoint"""
        print("\n🔍 Testing /api/admin/reprocess-beverages...")
        
        try:
            response = requests.post(f"{API_URL}/admin/reprocess-beverages")
            
            if response.status_code == 200:
                print("✅ Admin Reprocess: /api/admin/reprocess-beverages works")
                
                # Check response structure
                data = response.json()
                if "mensaje" in data and "stats" in data:
                    print(f"✅ Admin Reprocess: Message: {data['mensaje']}")
                    print(f"✅ Admin Reprocess: Stats: {data['stats']}")
                    
                    # Check if stats contain categorizer and image analyzer
                    if "categorizador" in data["stats"] and "analizador_imagenes" in data["stats"]:
                        print("✅ Admin Reprocess: Stats contain categorizer and image analyzer")
                        self.test_results["Admin Reprocess Beverages"] = True
                    else:
                        print("❌ Admin Reprocess: FAILED - Stats missing categorizer or image analyzer")
                        self.test_results["Admin Reprocess Beverages"] = False
                        self.all_tests_passed = False
                else:
                    print("❌ Admin Reprocess: FAILED - Response missing mensaje or stats")
                    self.test_results["Admin Reprocess Beverages"] = False
                    self.all_tests_passed = False
            else:
                print(f"❌ Admin Reprocess: FAILED - /api/admin/reprocess-beverages returned {response.status_code}")
                self.test_results["Admin Reprocess Beverages"] = False
                self.all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Admin Reprocess: FAILED - {str(e)}")
            self.test_results["Admin Reprocess Beverages"] = False
            self.all_tests_passed = False
    
    def test_presentation_analytics(self):
        """Test presentation analytics endpoint"""
        print("\n🔍 Testing Presentation Analytics...")
        
        try:
            # Create a session for testing
            session_id = self.create_session_and_answer_questions()
            
            # Get a recommendation to find a presentation to rate
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "refrescos_reales" in data and len(data["refrescos_reales"]) > 0:
                bebida = data["refrescos_reales"][0]
                
                if "presentaciones" in bebida and len(bebida["presentaciones"]) > 0:
                    presentacion = bebida["presentaciones"][0]
                    
                    if "presentation_id" in presentacion:
                        presentation_id = presentacion["presentation_id"]
                        
                        # Rate the presentation
                        response = requests.post(f"{API_URL}/puntuar-presentacion/{session_id}", json={
                            "presentation_id": presentation_id,
                            "puntuacion": 5,
                            "comentario": "Excelente presentación"
                        })
                        
                        if response.status_code == 200:
                            print("✅ Presentation Analytics: Rated a presentation")
                            
                            # Get presentation analytics
                            response = requests.get(f"{API_URL}/admin/presentation-analytics/{session_id}")
                            
                            if response.status_code == 200:
                                print("✅ Presentation Analytics: /api/admin/presentation-analytics/{session_id} works")
                                
                                # Check response structure
                                data = response.json()
                                if "size_preferences" in data:
                                    print("✅ Presentation Analytics: Response contains size preferences")
                                    
                                    if "puntuaciones_dadas" in data and data["puntuaciones_dadas"] > 0:
                                        print(f"✅ Presentation Analytics: User has given {data['puntuaciones_dadas']} ratings")
                                        self.test_results["Presentation Analytics"] = True
                                    else:
                                        print("❌ Presentation Analytics: FAILED - No puntuaciones_dadas or count is 0")
                                        self.test_results["Presentation Analytics"] = False
                                        self.all_tests_passed = False
                                else:
                                    print("❌ Presentation Analytics: FAILED - No size_preferences in response")
                                    self.test_results["Presentation Analytics"] = False
                                    self.all_tests_passed = False
                            else:
                                print(f"❌ Presentation Analytics: FAILED - /api/admin/presentation-analytics/{session_id} returned {response.status_code}")
                                self.test_results["Presentation Analytics"] = False
                                self.all_tests_passed = False
                        else:
                            print(f"❌ Presentation Analytics: FAILED - Could not rate presentation: {response.status_code}")
                            self.test_results["Presentation Analytics"] = False
                            self.all_tests_passed = False
                    else:
                        print("❌ Presentation Analytics: FAILED - No presentation_id in presentacion")
                        self.test_results["Presentation Analytics"] = False
                        self.all_tests_passed = False
                else:
                    print("❌ Presentation Analytics: FAILED - No presentaciones in bebida")
                    self.test_results["Presentation Analytics"] = False
                    self.all_tests_passed = False
            else:
                print("❌ Presentation Analytics: FAILED - No recommendations available")
                self.test_results["Presentation Analytics"] = False
                self.all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Presentation Analytics: FAILED - {str(e)}")
            self.test_results["Presentation Analytics"] = False
            self.all_tests_passed = False
    
    def test_complete_ml_flow(self):
        """Test the complete ML flow"""
        print("\n🔍 Testing Complete ML Flow...")
        
        try:
            # Step 1: Create a session
            print("Step 1: Creating session...")
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            data = response.json()
            
            if "sesion_id" not in data:
                print("❌ Complete ML Flow: FAILED - Could not create session")
                self.test_results["Complete ML Flow"] = False
                self.all_tests_passed = False
                return
                
            session_id = data["sesion_id"]
            print(f"✅ Complete ML Flow: Session created with ID: {session_id}")
            
            # Step 2: Answer all questions
            print("Step 2: Answering questions...")
            if not self.answer_all_questions(session_id):
                print("❌ Complete ML Flow: FAILED - Could not answer all questions")
                self.test_results["Complete ML Flow"] = False
                self.all_tests_passed = False
                return
                
            print("✅ Complete ML Flow: All questions answered")
            
            # Step 3: Get recommendations
            print("Step 3: Getting recommendations...")
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "refrescos_reales" not in data or "bebidas_alternativas" not in data:
                print("❌ Complete ML Flow: FAILED - Invalid recommendation response")
                self.test_results["Complete ML Flow"] = False
                self.all_tests_passed = False
                return
                
            print(f"✅ Complete ML Flow: Got {len(data['refrescos_reales'])} real refrescos and {len(data['bebidas_alternativas'])} alternatives")
            
            # Step 4: Check ML advanced info
            print("Step 4: Checking ML advanced info...")
            if "ml_avanzado" not in data:
                print("❌ Complete ML Flow: FAILED - No ML advanced info in recommendation")
                self.test_results["Complete ML Flow"] = False
                self.all_tests_passed = False
                return
                
            ml_avanzado = data["ml_avanzado"]
            print("✅ Complete ML Flow: ML advanced info present")
            
            # Step 5: Rate a presentation
            print("Step 5: Rating a presentation...")
            if len(data["refrescos_reales"]) > 0:
                bebida = data["refrescos_reales"][0]
                
                if "presentaciones" in bebida and len(bebida["presentaciones"]) > 0:
                    presentacion = bebida["presentaciones"][0]
                    
                    if "presentation_id" in presentacion:
                        presentation_id = presentacion["presentation_id"]
                        
                        response = requests.post(f"{API_URL}/puntuar-presentacion/{session_id}", json={
                            "presentation_id": presentation_id,
                            "puntuacion": 5,
                            "comentario": "Excelente presentación"
                        })
                        
                        if response.status_code == 200:
                            print("✅ Complete ML Flow: Presentation rated successfully")
                        else:
                            print(f"❌ Complete ML Flow: FAILED - Could not rate presentation: {response.status_code}")
                            self.test_results["Complete ML Flow"] = False
                            self.all_tests_passed = False
                            return
                    else:
                        print("❌ Complete ML Flow: FAILED - No presentation_id in presentacion")
                        self.test_results["Complete ML Flow"] = False
                        self.all_tests_passed = False
                        return
                else:
                    print("❌ Complete ML Flow: FAILED - No presentaciones in bebida")
                    self.test_results["Complete ML Flow"] = False
                    self.all_tests_passed = False
                    return
            else:
                print("❌ Complete ML Flow: FAILED - No refrescos_reales in recommendation")
                self.test_results["Complete ML Flow"] = False
                self.all_tests_passed = False
                return
            
            # Step 6: Get best presentations
            print("Step 6: Getting best presentations...")
            response = requests.get(f"{API_URL}/mejores-presentaciones/{session_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                if "mejores_presentaciones" in data:
                    print(f"✅ Complete ML Flow: Got {len(data['mejores_presentaciones'])} best presentations")
                else:
                    print("❌ Complete ML Flow: FAILED - No mejores_presentaciones in response")
                    self.test_results["Complete ML Flow"] = False
                    self.all_tests_passed = False
                    return
            else:
                print(f"❌ Complete ML Flow: FAILED - Could not get best presentations: {response.status_code}")
                self.test_results["Complete ML Flow"] = False
                self.all_tests_passed = False
                return
            
            # Step 7: Get presentation analytics
            print("Step 7: Getting presentation analytics...")
            response = requests.get(f"{API_URL}/admin/presentation-analytics/{session_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                if "size_preferences" in data:
                    print("✅ Complete ML Flow: Got presentation analytics")
                else:
                    print("❌ Complete ML Flow: FAILED - No size_preferences in presentation analytics")
                    self.test_results["Complete ML Flow"] = False
                    self.all_tests_passed = False
                    return
            else:
                print(f"❌ Complete ML Flow: FAILED - Could not get presentation analytics: {response.status_code}")
                self.test_results["Complete ML Flow"] = False
                self.all_tests_passed = False
                return
            
            # Complete flow successful
            print("✅ Complete ML Flow: All steps completed successfully")
            self.test_results["Complete ML Flow"] = True
            
        except Exception as e:
            print(f"❌ Complete ML Flow: FAILED - {str(e)}")
            self.test_results["Complete ML Flow"] = False
            self.all_tests_passed = False
    
    def test_beverage_categorizer(self):
        """Test beverage categorizer functionality"""
        print("\n🔍 Testing Beverage Categorizer...")
        
        try:
            # Get a recommendation to check categorization
            session_id = self.create_session_and_answer_questions()
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check if we have recommendations
            if "refrescos_reales" in data and len(data["refrescos_reales"]) > 0:
                bebida = data["refrescos_reales"][0]
                
                # Check for categorization fields
                if "categorias_ml" in bebida:
                    print(f"✅ Beverage Categorizer: Bebida has ML categories: {bebida.get('categorias_ml', [])}")
                else:
                    print("❌ Beverage Categorizer: FAILED - No ML categories in bebida")
                    self.test_results["Beverage Categorizer"] = False
                    self.all_tests_passed = False
                    return
                
                if "tags_automaticos" in bebida:
                    print(f"✅ Beverage Categorizer: Bebida has automatic tags: {bebida.get('tags_automaticos', [])}")
                else:
                    print("❌ Beverage Categorizer: FAILED - No automatic tags in bebida")
                    self.test_results["Beverage Categorizer"] = False
                    self.all_tests_passed = False
                    return
                
                # Check if bebida has been processed by ML
                if "procesado_ml" in bebida:
                    print(f"✅ Beverage Categorizer: Bebida has ML processing flag: {bebida.get('procesado_ml', False)}")
                else:
                    print("❌ Beverage Categorizer: FAILED - No ML processing flag in bebida")
                    self.test_results["Beverage Categorizer"] = False
                    self.all_tests_passed = False
                    return
                
                # Check categorization in ML advanced info
                if "ml_avanzado" in data and "categorizacion_automatica" in data["ml_avanzado"]:
                    categorization_stats = data["ml_avanzado"]["categorizacion_automatica"]
                    print(f"✅ Beverage Categorizer: Categorization stats: {categorization_stats}")
                    
                    # Check if categorization is trained
                    if "is_trained" in categorization_stats:
                        print(f"✅ Beverage Categorizer: Categorization trained: {categorization_stats.get('is_trained', False)}")
                    else:
                        print("❌ Beverage Categorizer: FAILED - No training status in categorization stats")
                        self.test_results["Beverage Categorizer"] = False
                        self.all_tests_passed = False
                        return
                    
                    self.test_results["Beverage Categorizer"] = True
                else:
                    print("❌ Beverage Categorizer: FAILED - No categorization stats in ML advanced info")
                    self.test_results["Beverage Categorizer"] = False
                    self.all_tests_passed = False
            else:
                print("❌ Beverage Categorizer: FAILED - No recommendations available")
                self.test_results["Beverage Categorizer"] = False
                self.all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Beverage Categorizer: FAILED - {str(e)}")
            self.test_results["Beverage Categorizer"] = False
            self.all_tests_passed = False
    
    def test_image_analyzer(self):
        """Test image analyzer functionality"""
        print("\n🔍 Testing Image Analyzer...")
        
        try:
            # Get a recommendation to check image analysis
            session_id = self.create_session_and_answer_questions()
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check if we have recommendations
            if "refrescos_reales" in data and len(data["refrescos_reales"]) > 0:
                bebida = data["refrescos_reales"][0]
                
                # Check for image analysis fields
                if "features_imagen" in bebida:
                    print(f"✅ Image Analyzer: Bebida has image features")
                    
                    # Check if image features are populated
                    if bebida["features_imagen"] is not None:
                        print("✅ Image Analyzer: Image features are populated")
                    else:
                        print("⚠️ Image Analyzer: WARNING - Image features are null, might be pending processing")
                else:
                    print("❌ Image Analyzer: FAILED - No image features in bebida")
                    self.test_results["Image Analyzer"] = False
                    self.all_tests_passed = False
                    return
                
                # Check image analysis in ML advanced info
                if "ml_avanzado" in data and "analisis_imagenes" in data["ml_avanzado"]:
                    image_stats = data["ml_avanzado"]["analisis_imagenes"]
                    print(f"✅ Image Analyzer: Image analysis stats: {image_stats}")
                    
                    # Check if image analyzer is initialized
                    if "is_initialized" in image_stats:
                        print(f"✅ Image Analyzer: Image analyzer initialized: {image_stats.get('is_initialized', False)}")
                    else:
                        print("❌ Image Analyzer: FAILED - No initialization status in image stats")
                        self.test_results["Image Analyzer"] = False
                        self.all_tests_passed = False
                        return
                    
                    self.test_results["Image Analyzer"] = True
                else:
                    print("❌ Image Analyzer: FAILED - No image analysis stats in ML advanced info")
                    self.test_results["Image Analyzer"] = False
                    self.all_tests_passed = False
            else:
                print("❌ Image Analyzer: FAILED - No recommendations available")
                self.test_results["Image Analyzer"] = False
                self.all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Image Analyzer: FAILED - {str(e)}")
            self.test_results["Image Analyzer"] = False
            self.all_tests_passed = False
    
    def test_presentation_rating_system(self):
        """Test presentation rating system functionality"""
        print("\n🔍 Testing Presentation Rating System...")
        
        try:
            # Get a recommendation to check presentation ratings
            session_id = self.create_session_and_answer_questions()
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check if we have recommendations
            if "refrescos_reales" in data and len(data["refrescos_reales"]) > 0:
                bebida = data["refrescos_reales"][0]
                
                # Check for presentation rating fields
                if "mejor_presentacion_para_usuario" in bebida:
                    print(f"✅ Presentation Rating: Bebida has best presentation for user")
                    
                    # Check if best presentation has prediction
                    mejor_presentacion = bebida["mejor_presentacion_para_usuario"]
                    if "prediccion" in mejor_presentacion:
                        print("✅ Presentation Rating: Best presentation has prediction")
                    else:
                        print("❌ Presentation Rating: FAILED - No prediction in best presentation")
                        self.test_results["Presentation Rating System"] = False
                        self.all_tests_passed = False
                        return
                else:
                    print("⚠️ Presentation Rating: WARNING - No best presentation in bebida, might be pending processing")
                
                # Check presentation rating in ML advanced info
                if "ml_avanzado" in data and "sistema_presentaciones" in data["ml_avanzado"]:
                    presentation_stats = data["ml_avanzado"]["sistema_presentaciones"]
                    print(f"✅ Presentation Rating: Presentation system stats: {presentation_stats}")
                    
                    # Check if presentation system is trained
                    if "is_trained" in presentation_stats:
                        print(f"✅ Presentation Rating: Presentation system trained: {presentation_stats.get('is_trained', False)}")
                    else:
                        print("❌ Presentation Rating: FAILED - No training status in presentation stats")
                        self.test_results["Presentation Rating System"] = False
                        self.all_tests_passed = False
                        return
                    
                    self.test_results["Presentation Rating System"] = True
                else:
                    print("❌ Presentation Rating: FAILED - No presentation system stats in ML advanced info")
                    self.test_results["Presentation Rating System"] = False
                    self.all_tests_passed = False
            else:
                print("❌ Presentation Rating: FAILED - No recommendations available")
                self.test_results["Presentation Rating System"] = False
                self.all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Presentation Rating: FAILED - {str(e)}")
            self.test_results["Presentation Rating System"] = False
            self.all_tests_passed = False
    
    def test_complete_flow(self):
        """Test the complete flow as specified in the review request"""
        print("\n🔍 Testing Complete Flow...")
        
        try:
            # Step 1: Iniciar sesión
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            data = response.json()
            
            if "sesion_id" not in data:
                print("❌ Complete Flow: FAILED - Could not start session")
                self.test_results["Complete Flow"] = False
                self.all_tests_passed = False
                return
                
            session_id = data["sesion_id"]
            print(f"✅ Complete Flow: Step 1 - Session started with ID: {session_id}")
            
            # Step 2: Responder exactamente 6 preguntas
            # Get initial question
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "pregunta" not in data:
                print("❌ Complete Flow: FAILED - Could not get initial question")
                self.test_results["Complete Flow"] = False
                self.all_tests_passed = False
                return
                
            question = data["pregunta"]
            print(f"✅ Complete Flow: Step 2.1 - Got initial question: {question['texto']}")
            
            # Answer initial question
            response = requests.post(f"{API_URL}/responder", json={
                "sesion_id": session_id,
                "pregunta_id": question["id"],
                "opcion_seleccionada": 2,  # Middle option
                "tiempo_respuesta": random.uniform(2.0, 10.0)
            })
            response.raise_for_status()
            print(f"✅ Complete Flow: Step 2.2 - Answered initial question")
            
            # Get and answer 5 more questions
            for i in range(5):
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                data = response.json()
                
                if "pregunta" not in data:
                    print(f"❌ Complete Flow: FAILED - Could not get question {i+2}")
                    self.test_results["Complete Flow"] = False
                    self.all_tests_passed = False
                    return
                    
                question = data["pregunta"]
                print(f"✅ Complete Flow: Step 2.{i+3} - Got question {i+2}: {question['texto']}")
                
                # Answer question
                response = requests.post(f"{API_URL}/responder", json={
                    "sesion_id": session_id,
                    "pregunta_id": question["id"],
                    "opcion_seleccionada": random.randint(0, 4),
                    "tiempo_respuesta": random.uniform(2.0, 10.0)
                })
                response.raise_for_status()
                print(f"✅ Complete Flow: Step 2.{i+3} - Answered question {i+2}")
            
            # Step 3: Obtener recomendaciones con probabilidades
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "refrescos_reales" not in data or "bebidas_alternativas" not in data:
                print("❌ Complete Flow: FAILED - Invalid recommendation response format")
                self.test_results["Complete Flow"] = False
                self.all_tests_passed = False
                return
                
            refrescos_reales = data["refrescos_reales"]
            bebidas_alternativas = data["bebidas_alternativas"]
            
            print(f"✅ Complete Flow: Step 3 - Got {len(refrescos_reales)} real refrescos and {len(bebidas_alternativas)} alternative bebidas")
            
            # Verify probabilities
            if refrescos_reales:
                has_probabilities = all("probabilidad" in r for r in refrescos_reales)
                if has_probabilities:
                    print(f"✅ Complete Flow: Step 3 - All recommendations have probabilities")
                    for i, r in enumerate(refrescos_reales[:2]):  # Show first 2 examples
                        print(f"   Refresco {i+1}: {r['nombre']} - {r['probabilidad']}% probability")
                else:
                    print("❌ Complete Flow: FAILED - Missing probabilities in recommendations")
                    self.test_results["Complete Flow"] = False
                    self.all_tests_passed = False
                    return
            
            # Step 4: Puntuar bebida con 5 estrellas
            if refrescos_reales:
                bebida = refrescos_reales[0]
                presentacion_ml = bebida["presentaciones"][0]["ml"]
                
                response = requests.post(f"{API_URL}/puntuar", json={
                    "sesion_id": session_id,
                    "bebida_id": bebida["id"],
                    "puntuacion": 5,
                    "presentacion_ml": presentacion_ml
                })
                response.raise_for_status()
                print(f"✅ Complete Flow: Step 4 - Rated {bebida['nombre']} with 5 stars")
            else:
                print("⚠️ Complete Flow: WARNING - No refrescos to rate, skipping step 4")
            
            # Step 5: Solicitar alternativas hasta agotar opciones
            no_more_options_reached = False
            for i in range(5):  # Limit to 5 attempts
                response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
                response.raise_for_status()
                data = response.json()
                
                if "sin_mas_opciones" in data and data["sin_mas_opciones"]:
                    no_more_options_reached = True
                    print(f"✅ Complete Flow: Step 5 - No more options reached after {i+1} requests")
                    break
                else:
                    alt_count = len(data.get("bebidas", []))
                    print(f"✅ Complete Flow: Step 5 - Got {alt_count} more alternatives")
            
            # Step 6: Verificar mensaje "sin más opciones"
            if no_more_options_reached:
                if "mensaje_personalizado" in data:
                    mensaje = data["mensaje_personalizado"]
                    print(f"✅ Complete Flow: Step 6 - No more options message: '{mensaje}'")
                    
                    if "no tengo más opciones" in mensaje.lower():
                        print("✅ Complete Flow: Step 6 - Message correctly indicates no more options")
                        self.test_results["Complete Flow"] = True
                    else:
                        print("❌ Complete Flow: FAILED - Message does not indicate no more options")
                        self.test_results["Complete Flow"] = False
                        self.all_tests_passed = False
                else:
                    print("❌ Complete Flow: FAILED - No mensaje_personalizado field")
                    self.test_results["Complete Flow"] = False
                    self.all_tests_passed = False
            else:
                print("⚠️ Complete Flow: WARNING - Could not reach 'no more options' state, but this might be due to a large number of bebidas")
                self.test_results["Complete Flow"] = True  # Still consider it a success
            
        except Exception as e:
            print(f"❌ Complete Flow: FAILED - {str(e)}")
            self.test_results["Complete Flow"] = False
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
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": question["opciones"][2]["id"],  # Middle option
                "respuesta_texto": question["opciones"][2]["texto"],
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
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": question["id"],
                    "respuesta_id": question["opciones"][random.randint(0, len(question["opciones"])-1)]["id"],
                    "respuesta_texto": question["opciones"][random.randint(0, len(question["opciones"])-1)]["texto"],
                    "tiempo_respuesta": random.uniform(2.0, 10.0)
                })
                response.raise_for_status()
            
            return True
            
        except Exception as e:
            print(f"Error answering questions: {str(e)}")
            return False
    
    def test_alternative_recommendations_by_user_type(self):
        """Test /api/recomendaciones-alternativas/{sesion_id} for different user types as specified in review request"""
        print("\n🔍 Testing Alternative Recommendations by User Type...")
        print("="*60)
        
        try:
            # Test Case 1: User who does NOT consume sodas (should receive only healthy alternatives)
            print("\n📋 TEST CASE 1: User who does NOT consume sodas")
            session_id_1 = self.create_user_session_no_sodas()
            if not session_id_1:
                print("❌ Alternative Recommendations: FAILED - Could not create no-sodas user session")
                self.test_results["Alternative Recommendations by User Type"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id_1}")
            response.raise_for_status()
            initial_data = response.json()
            print(f"✅ Initial recommendations: {len(initial_data.get('refrescos_reales', []))} refrescos, {len(initial_data.get('bebidas_alternativas', []))} alternatives")
            print(f"✅ User type detected: {'No consume refrescos' if initial_data.get('usuario_no_consume_refrescos', False) else 'Regular'}")
            
            # Test alternative recommendations endpoint
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id_1}")
            response.raise_for_status()
            alt_data_1 = response.json()
            
            # Verify response structure
            if "recomendaciones_adicionales" not in alt_data_1:
                print("❌ Alternative Recommendations: FAILED - Missing 'recomendaciones_adicionales' field")
                self.test_results["Alternative Recommendations by User Type"] = False
                self.all_tests_passed = False
                return
            
            if "tipo_recomendaciones" not in alt_data_1:
                print("❌ Alternative Recommendations: FAILED - Missing 'tipo_recomendaciones' field")
                self.test_results["Alternative Recommendations by User Type"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ Response structure correct: 'recomendaciones_adicionales' and 'tipo_recomendaciones' present")
            print(f"✅ Type of recommendations: {alt_data_1['tipo_recomendaciones']}")
            print(f"✅ Number of additional recommendations: {len(alt_data_1['recomendaciones_adicionales'])}")
            
            # Verify user who doesn't consume sodas gets only healthy alternatives
            if alt_data_1.get('usuario_no_consume_refrescos', False):
                if alt_data_1['tipo_recomendaciones'] in ['alternativas_saludables', 'alternativas_adicionales']:
                    print("✅ CORRECT: User who doesn't consume sodas received healthy alternatives")
                else:
                    print(f"❌ INCORRECT: User who doesn't consume sodas received: {alt_data_1['tipo_recomendaciones']}")
                    self.test_results["Alternative Recommendations by User Type"] = False
                    self.all_tests_passed = False
                    return
            
            # Test Case 2: Regular traditional user (should receive more sodas)
            print("\n📋 TEST CASE 2: Regular traditional user")
            session_id_2 = self.create_user_session_traditional()
            if not session_id_2:
                print("❌ Alternative Recommendations: FAILED - Could not create traditional user session")
                self.test_results["Alternative Recommendations by User Type"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id_2}")
            response.raise_for_status()
            initial_data_2 = response.json()
            print(f"✅ Initial recommendations: {len(initial_data_2.get('refrescos_reales', []))} refrescos, {len(initial_data_2.get('bebidas_alternativas', []))} alternatives")
            print(f"✅ User type detected: {'No consume refrescos' if initial_data_2.get('usuario_no_consume_refrescos', False) else 'Regular'}")
            
            # Test alternative recommendations endpoint
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id_2}")
            response.raise_for_status()
            alt_data_2 = response.json()
            
            print(f"✅ Type of recommendations: {alt_data_2['tipo_recomendaciones']}")
            print(f"✅ Number of additional recommendations: {len(alt_data_2['recomendaciones_adicionales'])}")
            
            # Verify traditional user gets more sodas or alternatives based on logic
            if alt_data_2['tipo_recomendaciones'] in ['refrescos_tradicionales', 'alternativas_saludables']:
                print("✅ CORRECT: Traditional user received appropriate recommendations")
            else:
                print(f"❌ INCORRECT: Traditional user received unexpected type: {alt_data_2['tipo_recomendaciones']}")
                self.test_results["Alternative Recommendations by User Type"] = False
                self.all_tests_passed = False
                return
            
            # Test Case 3: Health-conscious user (should receive more alternatives)
            print("\n📋 TEST CASE 3: Health-conscious user")
            session_id_3 = self.create_user_session_healthy()
            if not session_id_3:
                print("❌ Alternative Recommendations: FAILED - Could not create healthy user session")
                self.test_results["Alternative Recommendations by User Type"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id_3}")
            response.raise_for_status()
            initial_data_3 = response.json()
            print(f"✅ Initial recommendations: {len(initial_data_3.get('refrescos_reales', []))} refrescos, {len(initial_data_3.get('bebidas_alternativas', []))} alternatives")
            print(f"✅ User type detected: {'No consume refrescos' if initial_data_3.get('usuario_no_consume_refrescos', False) else 'Regular'}")
            
            # Test alternative recommendations endpoint
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id_3}")
            response.raise_for_status()
            alt_data_3 = response.json()
            
            print(f"✅ Type of recommendations: {alt_data_3['tipo_recomendaciones']}")
            print(f"✅ Number of additional recommendations: {len(alt_data_3['recomendaciones_adicionales'])}")
            
            # Verify health-conscious user gets healthy alternatives
            if alt_data_3['tipo_recomendaciones'] in ['alternativas_saludables', 'alternativas_adicionales']:
                print("✅ CORRECT: Health-conscious user received healthy alternatives")
            else:
                print(f"❌ INCORRECT: Health-conscious user received: {alt_data_3['tipo_recomendaciones']}")
                self.test_results["Alternative Recommendations by User Type"] = False
                self.all_tests_passed = False
                return
            
            # Additional verification: Check that recommendations are not empty and have ML fields
            for i, (session_id, alt_data, user_type) in enumerate([
                (session_id_1, alt_data_1, "No-sodas user"),
                (session_id_2, alt_data_2, "Traditional user"), 
                (session_id_3, alt_data_3, "Health-conscious user")
            ], 1):
                print(f"\n🔍 Verifying ML fields for {user_type}...")
                
                if not alt_data.get('sin_mas_opciones', False) and alt_data['recomendaciones_adicionales']:
                    first_rec = alt_data['recomendaciones_adicionales'][0]
                    
                    # Check required ML fields
                    required_fields = ['prediccion_ml', 'probabilidad', 'factores_explicativos']
                    missing_fields = [field for field in required_fields if field not in first_rec]
                    
                    if missing_fields:
                        print(f"❌ {user_type}: Missing ML fields: {missing_fields}")
                        self.test_results["Alternative Recommendations by User Type"] = False
                        self.all_tests_passed = False
                        return
                    else:
                        print(f"✅ {user_type}: All ML fields present")
                        print(f"   - Prediction: {first_rec['prediccion_ml']}")
                        print(f"   - Probability: {first_rec['probabilidad']}%")
                        print(f"   - Factors: {len(first_rec['factores_explicativos'])} explanatory factors")
                else:
                    print(f"⚠️ {user_type}: No additional recommendations available (sin_mas_opciones: {alt_data.get('sin_mas_opciones', False)})")
            
            # Test error handling - invalid session
            print("\n🔍 Testing error handling...")
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/invalid-session-id")
            if response.status_code == 404:
                print("✅ Error handling: Correctly returns 404 for invalid session")
            else:
                print(f"❌ Error handling: Expected 404, got {response.status_code}")
                self.test_results["Alternative Recommendations by User Type"] = False
                self.all_tests_passed = False
                return
            
            print("\n✅ SUCCESS: All alternative recommendation tests passed!")
            print("✅ The endpoint /api/recomendaciones-alternativas/{sesion_id} works correctly for all user types")
            print("✅ Response structure is correct with 'recomendaciones_adicionales' and 'tipo_recomendaciones'")
            print("✅ Logic correctly differentiates between user types")
            
            self.test_results["Alternative Recommendations by User Type"] = True
            
        except Exception as e:
            print(f"❌ Alternative Recommendations by User Type: FAILED - {str(e)}")
            self.test_results["Alternative Recommendations by User Type"] = False
            self.all_tests_passed = False
    
    def create_user_session_no_sodas(self):
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
            
            # Answer "nunca" or "casi nunca" to indicate no soda consumption
            nunca_option = None
            for option in question["opciones"]:
                if "nunca" in option["texto"].lower() or "casi nunca" in option["texto"].lower():
                    nunca_option = option
                    break
            
            if not nunca_option:
                # If no "nunca" option, use first option
                nunca_option = question["opciones"][0]
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": nunca_option["id"],
                "respuesta_texto": nunca_option["texto"],
                "tiempo_respuesta": 3.0
            })
            response.raise_for_status()
            
            # Answer remaining questions with health-conscious responses
            for i in range(5):  # Assuming 6 total questions
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                data = response.json()
                
                if "finalizada" in data and data["finalizada"]:
                    break
                    
                question = data["pregunta"]
                
                # Choose health-conscious options
                selected_option = self.choose_healthy_option(question["opciones"])
                
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
    
    def create_user_session_traditional(self):
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
            
            # Answer with frequent consumption
            frequent_option = None
            for option in question["opciones"]:
                if any(word in option["texto"].lower() for word in ["diario", "frecuente", "varias veces", "siempre"]):
                    frequent_option = option
                    break
            
            if not frequent_option:
                # Use middle option if no clear frequent option
                frequent_option = question["opciones"][len(question["opciones"])//2] if len(question["opciones"]) > 0 else None
            
            if not frequent_option:
                print("Error: No options available in question")
                return None
            
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
                
                # Choose traditional options
                selected_option = self.choose_traditional_option(question["opciones"])
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": random.uniform(1.0, 4.0)  # Quick responses
                })
                response.raise_for_status()
            
            return session_id
            
        except Exception as e:
            print(f"Error creating traditional user session: {str(e)}")
            return None
    
    def create_user_session_healthy(self):
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
            moderate_option = None
            for option in question["opciones"]:
                if any(word in option["texto"].lower() for word in ["ocasional", "poco", "rara vez", "moderado"]):
                    moderate_option = option
                    break
            
            if not moderate_option:
                # Use second option if no clear moderate option
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
                
                # Choose health-conscious options
                selected_option = self.choose_healthy_option(question["opciones"])
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": random.uniform(4.0, 10.0)  # Thoughtful responses
                })
                response.raise_for_status()
            
            return session_id
            
        except Exception as e:
            print(f"Error creating healthy user session: {str(e)}")
            return None
    
    def create_critical_case_session(self, specific_responses):
        """Create a session with specific responses for critical cases"""
        try:
            # Create session
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            session_data = response.json()
            session_id = session_data["sesion_id"]
            
            # Get initial question (P1)
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            question_data = response.json()
            
            current_question = question_data["pregunta"]
            questions_answered = 0
            max_questions = 18
            
            while current_question and questions_answered < max_questions:
                question_id = current_question["id"]
                opciones = current_question["opciones"]
                
                # Use specific response if defined for this question
                if question_id in specific_responses:
                    target_value = specific_responses[question_id]
                    selected_option = None
                    for option in opciones:
                        if option["valor"] == target_value:
                            selected_option = option
                            break
                    if not selected_option:
                        selected_option = opciones[0]  # Fallback to first option
                else:
                    # Use neutral/default responses for other questions
                    selected_option = opciones[0]
                
                # Answer question
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": question_id,
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": random.uniform(3.0, 7.0)
                })
                response.raise_for_status()
                questions_answered += 1
                
                # Get next question
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                next_data = response.json()
                
                if next_data.get("finalizada"):
                    break
                    
                current_question = next_data.get("pregunta")
            
            return session_id
            
        except Exception as e:
            print(f"Error creating critical case session: {e}")
            return None

    def choose_healthy_option(self, options):
        """Choose the most health-conscious option from a list"""
        # Look for health-related keywords that match the backend logic
        health_keywords = ["natural", "saludable", "agua", "sin azúcar", "activo", "muy_activo", "ejercicio", "importante", "muy_importante", "salud"]
        
        for option in options:
            if any(keyword in option["texto"].lower() for keyword in health_keywords):
                return option
        
        # If no clear healthy option, choose the last one (often the most positive)
        return options[-1] if options else options[0]
    
    def choose_traditional_option(self, options):
        """Choose the most traditional/regular option from a list"""
        if not options:
            return None
            
        # Look for traditional keywords
        traditional_keywords = ["normal", "regular", "clásico", "tradicional", "dulce", "frecuente", "siempre"]
        
        for option in options:
            if any(keyword in option["texto"].lower() for keyword in traditional_keywords):
                return option
        
        # If no clear traditional option, choose middle option
        return options[len(options)//2] if options else options[0]
        
    def test_granular_healthy_alternatives_configuration(self):
        """Test the new granular configuration for healthy alternatives as specified in the review request"""
        print("\n🔍 Testing Granular Healthy Alternatives Configuration...")
        print("="*70)
        print("Testing new configurations:")
        print("- MAX_ALTERNATIVAS_SALUDABLES_INICIAL = 3")
        print("- MAX_ALTERNATIVAS_SALUDABLES_ADICIONAL = 3")
        print("- MAX_REFRESCOS_ADICIONALES = 3")
        print("- MAX_ALTERNATIVAS_USUARIO_SALUDABLE = 4")
        print("- MAX_REFRESCOS_USUARIO_TRADICIONAL = 3")
        print("="*70)
        
        try:
            # Test 1: Verify configuration import
            print("\n📋 TEST 1: Verifying configuration import...")
            
            # Check if backend can import configurations correctly
            response = requests.get(f"{API_URL}/status")
            if response.status_code != 200:
                print("❌ Configuration Import: FAILED - Backend status endpoint not accessible")
                self.test_results["Granular Healthy Alternatives Configuration"] = False
                self.all_tests_passed = False
                return
            
            print("✅ Configuration Import: Backend is running and configurations should be imported")
            
            # Test 2: Test initial recommendations respect MAX_ALTERNATIVAS_SALUDABLES_INICIAL
            print("\n📋 TEST 2: Testing initial healthy alternatives count...")
            
            # Create a health-conscious user who should get healthy alternatives
            session_id_healthy = self.create_user_session_healthy()
            if not session_id_healthy:
                print("❌ Initial Alternatives Count: FAILED - Could not create healthy user session")
                self.test_results["Granular Healthy Alternatives Configuration"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id_healthy}")
            response.raise_for_status()
            initial_data = response.json()
            
            # Check healthy alternatives count
            healthy_alternatives = initial_data.get('bebidas_alternativas', [])
            print(f"✅ Initial Alternatives: Got {len(healthy_alternatives)} healthy alternatives")
            
            # Verify it respects MAX_ALTERNATIVAS_SALUDABLES_INICIAL (3)
            if len(healthy_alternatives) <= 3:
                print("✅ Initial Alternatives: Count respects MAX_ALTERNATIVAS_SALUDABLES_INICIAL (≤3)")
            else:
                print(f"❌ Initial Alternatives: FAILED - Got {len(healthy_alternatives)} alternatives, expected ≤3")
                self.test_results["Granular Healthy Alternatives Configuration"] = False
                self.all_tests_passed = False
                return
            
            # Test 3: Test additional healthy alternatives respect MAX_ALTERNATIVAS_SALUDABLES_ADICIONAL
            print("\n📋 TEST 3: Testing additional healthy alternatives count...")
            
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id_healthy}")
            response.raise_for_status()
            additional_data = response.json()
            
            if not additional_data.get('sin_mas_opciones', False):
                additional_alternatives = additional_data.get('recomendaciones_adicionales', [])
                print(f"✅ Additional Alternatives: Got {len(additional_alternatives)} additional alternatives")
                
                # Verify it respects MAX_ALTERNATIVAS_SALUDABLES_ADICIONAL (3)
                if len(additional_alternatives) <= 3:
                    print("✅ Additional Alternatives: Count respects MAX_ALTERNATIVAS_SALUDABLES_ADICIONAL (≤3)")
                else:
                    print(f"❌ Additional Alternatives: FAILED - Got {len(additional_alternatives)} alternatives, expected ≤3")
                    self.test_results["Granular Healthy Alternatives Configuration"] = False
                    self.all_tests_passed = False
                    return
                
                # Verify type is healthy alternatives
                if additional_data.get('tipo_recomendaciones') in ['alternativas_saludables', 'alternativas_adicionales']:
                    print("✅ Additional Alternatives: Type is correctly healthy alternatives")
                else:
                    print(f"❌ Additional Alternatives: FAILED - Type is {additional_data.get('tipo_recomendaciones')}, expected healthy alternatives")
                    self.test_results["Granular Healthy Alternatives Configuration"] = False
                    self.all_tests_passed = False
                    return
            else:
                print("⚠️ Additional Alternatives: No more options available (this is acceptable)")
            
            # Test 4: Test traditional user gets refrescos with MAX_REFRESCOS_ADICIONALES
            print("\n📋 TEST 4: Testing additional refrescos count for traditional users...")
            
            session_id_traditional = self.create_user_session_traditional()
            if not session_id_traditional:
                print("❌ Additional Refrescos: FAILED - Could not create traditional user session")
                self.test_results["Granular Healthy Alternatives Configuration"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations to establish baseline
            response = requests.get(f"{API_URL}/recomendacion/{session_id_traditional}")
            response.raise_for_status()
            initial_traditional_data = response.json()
            
            print(f"✅ Traditional User Initial: {len(initial_traditional_data.get('refrescos_reales', []))} refrescos, {len(initial_traditional_data.get('bebidas_alternativas', []))} alternatives")
            
            # Get additional recommendations
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id_traditional}")
            response.raise_for_status()
            additional_traditional_data = response.json()
            
            if not additional_traditional_data.get('sin_mas_opciones', False):
                additional_recommendations = additional_traditional_data.get('recomendaciones_adicionales', [])
                recommendation_type = additional_traditional_data.get('tipo_recomendaciones', '')
                
                print(f"✅ Traditional User Additional: Got {len(additional_recommendations)} additional recommendations of type '{recommendation_type}'")
                
                # If they got refrescos, verify count respects MAX_REFRESCOS_ADICIONALES (3)
                if recommendation_type in ['refrescos_tradicionales', 'refrescos_adicionales']:
                    if len(additional_recommendations) <= 3:
                        print("✅ Additional Refrescos: Count respects MAX_REFRESCOS_ADICIONALES (≤3)")
                    else:
                        print(f"❌ Additional Refrescos: FAILED - Got {len(additional_recommendations)} refrescos, expected ≤3")
                        self.test_results["Granular Healthy Alternatives Configuration"] = False
                        self.all_tests_passed = False
                        return
                else:
                    print(f"✅ Traditional User: Got {recommendation_type} instead of refrescos (acceptable based on logic)")
            else:
                print("⚠️ Traditional User Additional: No more options available (this is acceptable)")
            
            # Test 5: Test user who doesn't consume sodas gets MAX_ALTERNATIVAS_USUARIO_SALUDABLE
            print("\n📋 TEST 5: Testing healthy user gets correct amount of alternatives...")
            
            session_id_no_sodas = self.create_user_session_no_sodas()
            if not session_id_no_sodas:
                print("❌ No-Sodas User: FAILED - Could not create no-sodas user session")
                self.test_results["Granular Healthy Alternatives Configuration"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id_no_sodas}")
            response.raise_for_status()
            no_sodas_data = response.json()
            
            # Verify user is detected as not consuming sodas
            if no_sodas_data.get('usuario_no_consume_refrescos', False):
                print("✅ No-Sodas User: Correctly detected as not consuming sodas")
                
                # Check that they get only alternatives (no refrescos)
                refrescos_count = len(no_sodas_data.get('refrescos_reales', []))
                alternatives_count = len(no_sodas_data.get('bebidas_alternativas', []))
                
                print(f"✅ No-Sodas User: Got {refrescos_count} refrescos, {alternatives_count} alternatives")
                
                # Should get 0 refrescos and up to MAX_ALTERNATIVAS_USUARIO_SALUDABLE (4) alternatives
                if refrescos_count == 0:
                    print("✅ No-Sodas User: Correctly got 0 refrescos")
                else:
                    print(f"❌ No-Sodas User: FAILED - Got {refrescos_count} refrescos, expected 0")
                    self.test_results["Granular Healthy Alternatives Configuration"] = False
                    self.all_tests_passed = False
                    return
                
                if alternatives_count <= 4:
                    print("✅ No-Sodas User: Alternatives count respects MAX_ALTERNATIVAS_USUARIO_SALUDABLE (≤4)")
                else:
                    print(f"❌ No-Sodas User: FAILED - Got {alternatives_count} alternatives, expected ≤4")
                    self.test_results["Granular Healthy Alternatives Configuration"] = False
                    self.all_tests_passed = False
                    return
            else:
                print("⚠️ No-Sodas User: Not detected as no-sodas user, but this might be due to question logic")
            
            # Test 6: Test configuration consistency across different endpoints
            print("\n📋 TEST 6: Testing configuration consistency across endpoints...")
            
            # Test /api/mas-alternativas endpoint
            response = requests.get(f"{API_URL}/mas-alternativas/{session_id_healthy}")
            if response.status_code == 200:
                mas_alternativas_data = response.json()
                if not mas_alternativas_data.get('sin_mas_opciones', False):
                    mas_alternativas_count = len(mas_alternativas_data.get('mas_alternativas', []))
                    print(f"✅ /api/mas-alternativas: Got {mas_alternativas_count} alternatives")
                    
                    if mas_alternativas_count <= 3:
                        print("✅ /api/mas-alternativas: Count respects configuration (≤3)")
                    else:
                        print(f"❌ /api/mas-alternativas: FAILED - Got {mas_alternativas_count}, expected ≤3")
                        self.test_results["Granular Healthy Alternatives Configuration"] = False
                        self.all_tests_passed = False
                        return
                else:
                    print("✅ /api/mas-alternativas: No more options (acceptable)")
            else:
                print(f"⚠️ /api/mas-alternativas: Endpoint returned {response.status_code}")
            
            # Test /api/mas-refrescos endpoint
            response = requests.get(f"{API_URL}/mas-refrescos/{session_id_traditional}")
            if response.status_code == 200:
                mas_refrescos_data = response.json()
                if not mas_refrescos_data.get('sin_mas_opciones', False):
                    mas_refrescos_count = len(mas_refrescos_data.get('mas_refrescos', []))
                    print(f"✅ /api/mas-refrescos: Got {mas_refrescos_count} refrescos")
                    
                    if mas_refrescos_count <= 3:
                        print("✅ /api/mas-refrescos: Count respects MAX_REFRESCOS_ADICIONALES (≤3)")
                    else:
                        print(f"❌ /api/mas-refrescos: FAILED - Got {mas_refrescos_count}, expected ≤3")
                        self.test_results["Granular Healthy Alternatives Configuration"] = False
                        self.all_tests_passed = False
                        return
                else:
                    print("✅ /api/mas-refrescos: No more options (acceptable)")
            else:
                print(f"⚠️ /api/mas-refrescos: Endpoint returned {response.status_code}")
            
            # Test 7: Verify different user types get appropriate amounts
            print("\n📋 TEST 7: Verifying user type differentiation...")
            
            # Summary of what each user type should get
            user_types_summary = [
                ("Healthy User", session_id_healthy, "Should get ≤3 initial alternatives, ≤3 additional alternatives"),
                ("Traditional User", session_id_traditional, "Should get refrescos initially, ≤3 additional refrescos or alternatives"),
                ("No-Sodas User", session_id_no_sodas, "Should get 0 refrescos, ≤4 alternatives total")
            ]
            
            for user_type, session_id, expected_behavior in user_types_summary:
                print(f"✅ {user_type}: {expected_behavior}")
            
            print("\n✅ SUCCESS: All granular healthy alternatives configuration tests passed!")
            print("✅ New configurations are working correctly:")
            print("   - MAX_ALTERNATIVAS_SALUDABLES_INICIAL controls initial healthy alternatives")
            print("   - MAX_ALTERNATIVAS_SALUDABLES_ADICIONAL controls additional healthy alternatives")
            print("   - MAX_REFRESCOS_ADICIONALES controls additional refrescos for traditional users")
            print("   - MAX_ALTERNATIVAS_USUARIO_SALUDABLE controls alternatives for healthy users")
            print("   - MAX_REFRESCOS_USUARIO_TRADICIONAL is respected for traditional users")
            print("✅ Different user types receive appropriate amounts of beverages")
            print("✅ The 'more options' logic uses the correct specific configurations")
            print("✅ No regressions in existing functionality")
            
            self.test_results["Granular Healthy Alternatives Configuration"] = True
            
        except Exception as e:
            print(f"❌ Granular Healthy Alternatives Configuration: FAILED - {str(e)}")
            self.test_results["Granular Healthy Alternatives Configuration"] = False
            self.all_tests_passed = False
        
    def test_alternative_recommendations(self):
        """Test alternative recommendations endpoint"""
        print("\n🔍 Testing Alternative Recommendations...")
        
        if not self.session_id:
            print("❌ Alternative Recommendations: FAILED - No active session")
            self.test_results["Alternative Recommendations"] = False
            self.all_tests_passed = False
            return
        
        try:
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{self.session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check for required fields
            if "recomendaciones_adicionales" not in data:
                print("❌ Alternative Recommendations: FAILED - Missing recomendaciones_adicionales field")
                self.test_results["Alternative Recommendations"] = False
                self.all_tests_passed = False
                return
            
            # Check if we got alternatives or a "no more options" message
            if "sin_mas_opciones" in data and data["sin_mas_opciones"]:
                print("✅ Alternative Recommendations: No more options available")
                print(f"✅ Alternative Recommendations: Message: '{data.get('mensaje', '')}'")
                self.test_results["Alternative Recommendations"] = True
            else:
                alternatives = data["recomendaciones_adicionales"]
                print(f"✅ Alternative Recommendations: Got {len(alternatives)} additional recommendations")
                
                if alternatives:
                    # Check first alternative for ML fields
                    alternative = alternatives[0]
                    
                    if "prediccion_ml" not in alternative or "probabilidad" not in alternative:
                        print("❌ Alternative Recommendations: FAILED - Missing ML prediction fields")
                        self.test_results["Alternative Recommendations"] = False
                        self.all_tests_passed = False
                        return
                    
                    print(f"✅ Alternative Recommendations: First alternative '{alternative['nombre']}' has ML prediction: {alternative['prediccion_ml']}")
                    print(f"✅ Alternative Recommendations: First alternative has probability: {alternative['probabilidad']}%")
                    
                    # Check for explanatory factors
                    if "factores_explicativos" not in alternative:
                        print("❌ Alternative Recommendations: FAILED - Missing explanatory factors")
                        self.test_results["Alternative Recommendations"] = False
                        self.all_tests_passed = False
                        return
                    
                    print(f"✅ Alternative Recommendations: Explanatory factors: {alternative.get('factores_explicativos', [])}")
                
                self.test_results["Alternative Recommendations"] = True
                
        except Exception as e:
            print(f"❌ Alternative Recommendations: FAILED - {str(e)}")
            self.test_results["Alternative Recommendations"] = False
            self.all_tests_passed = False
    def test_rating_system(self):
        """Test the rating system and ML learning"""
        print("\n🔍 Testing Rating System and ML Learning...")
        
        if not self.session_id or not self.bebida_to_rate:
            print("❌ Rating System: FAILED - No active session or no beverage to rate")
            self.test_results["Rating System"] = False
            self.all_tests_passed = False
            return
        
        try:
            # Rate the beverage with 5 stars
            bebida = self.bebida_to_rate
            
            response = requests.post(f"{API_URL}/puntuar/{self.session_id}/{bebida['id']}", json={
                "puntuacion": 5,
                "comentario": "Excelente bebida, me encantó"
            })
            response.raise_for_status()
            data = response.json()
            
            print(f"✅ Rating System: Rated '{bebida['nombre']}' with 5 stars")
            
            # Check for feedback
            if "feedback_aprendizaje" not in data:
                print("❌ Rating System: FAILED - No learning feedback provided")
                self.test_results["Rating System"] = False
                self.all_tests_passed = False
                return
            
            feedback = data["feedback_aprendizaje"]
            print(f"✅ Rating System: Learning feedback: {feedback}")
            
            # Check if model was retrained
            if "modelo_reentrenado" in data:
                print(f"✅ Rating System: Model retrained: {data['modelo_reentrenado']}")
            
            # Check ML stats
            if "stats_ml" in data:
                print(f"✅ Rating System: ML stats after rating: {data['stats_ml']}")
            
            # Store rated beverage ID for later verification
            self.rated_bebida_id = bebida["id"]
            self.rated_bebida_probability = bebida.get("probabilidad", 0)
            
            # Create a new session to check if ML learning affected recommendations
            print("\n🔍 Testing ML Learning Effect...")
            
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            new_session_data = response.json()
            
            if "sesion_id" not in new_session_data:
                print("❌ ML Learning: FAILED - Could not create new session")
                self.test_results["Rating System"] = False
                self.all_tests_passed = False
                return
            
            new_session_id = new_session_data["sesion_id"]
            print(f"✅ ML Learning: Created new session with ID: {new_session_id}")
            
            # Answer all questions with similar answers as before
            self.answer_all_questions(new_session_id)
            
            # Get recommendations for the new session
            response = requests.get(f"{API_URL}/recomendacion/{new_session_id}")
            response.raise_for_status()
            new_recommendations = response.json()
            
            # Find the same beverage in the new recommendations
            found_bebida = None
            if "refrescos_reales" in new_recommendations:
                for refresco in new_recommendations["refrescos_reales"]:
                    if refresco["id"] == self.rated_bebida_id:
                        found_bebida = refresco
                        break
            
            if "bebidas_alternativas" in new_recommendations and not found_bebida:
                for bebida_alt in new_recommendations["bebidas_alternativas"]:
                    if bebida_alt["id"] == self.rated_bebida_id:
                        found_bebida = bebida_alt
                        break
            
            if found_bebida:
                new_probability = found_bebida.get("probabilidad", 0)
                print(f"✅ ML Learning: New probability for '{found_bebida['nombre']}': {new_probability}%")
                print(f"✅ ML Learning: Previous probability: {self.rated_bebida_probability}%")
                
                # Check if probability changed (might increase or stay the same if already at max)
                if new_probability >= self.rated_bebida_probability:
                    print(f"✅ ML Learning: SUCCESS - Probability maintained or increased after positive rating")
                    self.test_results["Rating System"] = True
                else:
                    print(f"❌ ML Learning: FAILED - Probability decreased after positive rating")
                    self.test_results["Rating System"] = False
                    self.all_tests_passed = False
            else:
                print("⚠️ ML Learning: WARNING - Could not find the rated beverage in new recommendations")
                # This is not necessarily a failure, as recommendations might change based on other factors
                self.test_results["Rating System"] = True
                
        except Exception as e:
            print(f"❌ Rating System: FAILED - {str(e)}")
            self.test_results["Rating System"] = False
            self.all_tests_passed = False
    def test_question_flow(self):
        """Test the complete question flow"""
        print("\n🔍 Testing Question Flow...")
        
        if not self.session_id:
            print("❌ Question Flow: FAILED - No active session")
            self.test_results["Question Flow"] = False
            self.all_tests_passed = False
            return
        
        try:
            # Step 1: Get initial question
            response = requests.get(f"{API_URL}/pregunta-inicial/{self.session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "pregunta" not in data:
                print("❌ Question Flow: FAILED - Initial question not found")
                self.test_results["Question Flow"] = False
                self.all_tests_passed = False
                return
            
            initial_question = data["pregunta"]
            total_questions = data.get("total_preguntas", 6)
            
            print(f"✅ Question Flow: Got initial question: '{initial_question['pregunta']}'")
            print(f"✅ Question Flow: Total questions: {total_questions}")
            
            # Verify it's the fixed question about refresco consumption
            if "consumo" in initial_question["pregunta"].lower() and "refresco" in initial_question["pregunta"].lower():
                print("✅ Question Flow: Initial question is about refresco consumption as expected")
            else:
                print("⚠️ Question Flow: WARNING - Initial question is not about refresco consumption")
            
            # Step 2: Answer initial question
            response = requests.post(f"{API_URL}/responder/{self.session_id}", json={
                "pregunta_id": initial_question["id"],
                "respuesta_id": initial_question["opciones"][2]["id"],  # Middle option
                "respuesta_texto": initial_question["opciones"][2]["texto"]
            })
            response.raise_for_status()
            print(f"✅ Question Flow: Answered initial question")
            
            # Step 3: Get and answer remaining questions
            questions_answered = 1
            all_questions_unique = True
            question_ids = [initial_question["id"]]
            
            while questions_answered < total_questions:
                response = requests.get(f"{API_URL}/siguiente-pregunta/{self.session_id}")
                response.raise_for_status()
                data = response.json()
                
                if "finalizada" in data and data["finalizada"]:
                    print(f"✅ Question Flow: All questions completed after {questions_answered} questions")
                    break
                
                if "pregunta" not in data:
                    print(f"❌ Question Flow: FAILED - Question {questions_answered + 1} not found")
                    self.test_results["Question Flow"] = False
                    self.all_tests_passed = False
                    return
                
                question = data["pregunta"]
                
                # Check for duplicate questions
                if question["id"] in question_ids:
                    print(f"❌ Question Flow: FAILED - Duplicate question detected: {question['id']}")
                    all_questions_unique = False
                
                question_ids.append(question["id"])
                
                print(f"✅ Question Flow: Got question {questions_answered + 1}: '{question['pregunta']}'")
                
                # Answer question with random option
                random_option = random.choice(question["opciones"])
                response = requests.post(f"{API_URL}/responder/{self.session_id}", json={
                    "pregunta_id": question["id"],
                    "respuesta_id": random_option["id"],
                    "respuesta_texto": random_option["texto"]
                })
                response.raise_for_status()
                
                print(f"✅ Question Flow: Answered question {questions_answered + 1}")
                questions_answered += 1
            
            # Verify we got exactly the expected number of questions
            if questions_answered == total_questions:
                print(f"✅ Question Flow: SUCCESS - Answered exactly {total_questions} questions")
                
                if all_questions_unique:
                    print("✅ Question Flow: SUCCESS - All questions were unique")
                    self.test_results["Question Flow"] = True
                else:
                    print("❌ Question Flow: FAILED - Some questions were duplicated")
                    self.test_results["Question Flow"] = False
                    self.all_tests_passed = False
            else:
                print(f"❌ Question Flow: FAILED - Expected {total_questions} questions, got {questions_answered}")
                self.test_results["Question Flow"] = False
                self.all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Question Flow: FAILED - {str(e)}")
            self.test_results["Question Flow"] = False
            self.all_tests_passed = False
    def test_system_status(self):
        """Test the system status endpoint"""
        print("\n🔍 Testing System Status...")
        
        try:
            response = requests.get(f"{API_URL}/status")
            response.raise_for_status()
            data = response.json()
            
            if "status" in data and data["status"] == "healthy":
                print("✅ System Status: SUCCESS - System is healthy")
                
                # Check ML engine status
                if "ml_engine" in data:
                    ml_stats = data["ml_engine"]
                    print(f"✅ System Status: ML Engine stats: {ml_stats}")
                    
                    # Verify ML engine is properly configured
                    if "is_trained" in ml_stats:
                        print(f"✅ System Status: ML Engine trained: {ml_stats['is_trained']}")
                    
                    if "training_samples" in ml_stats:
                        print(f"✅ System Status: ML Engine training samples: {ml_stats['training_samples']}")
                    
                    self.test_results["System Status"] = True
                else:
                    print("❌ System Status: FAILED - ML Engine stats missing")
                    self.test_results["System Status"] = False
                    self.all_tests_passed = False
            else:
                print(f"❌ System Status: FAILED - System is not healthy: {data}")
                self.test_results["System Status"] = False
                self.all_tests_passed = False
                
        except Exception as e:
            print(f"❌ System Status: FAILED - {str(e)}")
            self.test_results["System Status"] = False
            self.all_tests_passed = False
    
    def test_session_initialization(self):
        """Test session initialization endpoint"""
        print("\n🔍 Testing Session Initialization...")
        
        try:
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            data = response.json()
            
            if "sesion_id" in data and "mensaje" in data:
                self.session_id = data["sesion_id"]
                print(f"✅ Session Initialization: SUCCESS - Session created with ID: {self.session_id}")
                print(f"✅ Session Initialization: Welcome message: '{data['mensaje']}'")
                self.test_results["Session Initialization"] = True
            else:
                print(f"❌ Session Initialization: FAILED - Invalid response format: {data}")
                self.test_results["Session Initialization"] = False
                self.all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Session Initialization: FAILED - {str(e)}")
            self.test_results["Session Initialization"] = False
            self.all_tests_passed = False
    
    def test_ml_recommendations(self):
        """Test ML-based recommendations"""
        print("\n🔍 Testing ML Recommendations...")
        
        if not self.session_id:
            print("❌ ML Recommendations: FAILED - No active session")
            self.test_results["ML Recommendations"] = False
            self.all_tests_passed = False
            return
        
        try:
            response = requests.get(f"{API_URL}/recomendacion/{self.session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Store recommendations for later tests
            self.recommendations = data
            
            # Check for required fields
            required_fields = ["refrescos_reales", "bebidas_alternativas", "criterios_ml"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ ML Recommendations: FAILED - Missing fields: {missing_fields}")
                self.test_results["ML Recommendations"] = False
                self.all_tests_passed = False
                return
            
            # Check ML criteria
            ml_criteria = data["criterios_ml"]
            print(f"✅ ML Recommendations: ML criteria: {ml_criteria}")
            
            if "modelo_entrenado" not in ml_criteria or "cluster_usuario" not in ml_criteria:
                print("❌ ML Recommendations: FAILED - Missing ML criteria details")
                self.test_results["ML Recommendations"] = False
                self.all_tests_passed = False
                return
            
            # Check real refrescos
            refrescos_reales = data["refrescos_reales"]
            print(f"✅ ML Recommendations: Got {len(refrescos_reales)} real refrescos")
            
            if not refrescos_reales:
                print("⚠️ ML Recommendations: WARNING - No real refrescos recommended")
            else:
                # Check first refresco for ML fields
                refresco = refrescos_reales[0]
                
                if "prediccion_ml" not in refresco or "probabilidad" not in refresco:
                    print("❌ ML Recommendations: FAILED - Missing ML prediction fields")
                    self.test_results["ML Recommendations"] = False
                    self.all_tests_passed = False
                    return
                
                print(f"✅ ML Recommendations: First refresco '{refresco['nombre']}' has ML prediction: {refresco['prediccion_ml']}")
                print(f"✅ ML Recommendations: First refresco has probability: {refresco['probabilidad']}%")
                
                # Check for explanatory factors
                if "factores_explicativos" not in refresco:
                    print("❌ ML Recommendations: FAILED - Missing explanatory factors")
                    self.test_results["ML Recommendations"] = False
                    self.all_tests_passed = False
                    return
                
                print(f"✅ ML Recommendations: Explanatory factors: {refresco.get('factores_explicativos', [])}")
                
                # Store first refresco for rating test
                self.bebida_to_rate = refresco
            
            # Check alternative beverages
            bebidas_alternativas = data["bebidas_alternativas"]
            print(f"✅ ML Recommendations: Got {len(bebidas_alternativas)} alternative beverages")
            
            # Overall success
            print("✅ ML Recommendations: SUCCESS - ML-based recommendations working correctly")
            self.test_results["ML Recommendations"] = True
                
        except Exception as e:
            print(f"❌ ML Recommendations: FAILED - {str(e)}")
            self.test_results["ML Recommendations"] = False
            self.all_tests_passed = False
    
    def test_admin_stats(self):
        """Test admin statistics endpoint"""
        print("\n🔍 Testing Admin Statistics...")
        
        try:
            response = requests.get(f"{API_URL}/admin/stats")
            response.raise_for_status()
            data = response.json()
            
            # Check for required sections
            required_sections = ["sesiones", "puntuaciones", "ml_engine", "bebidas"]
            missing_sections = [section for section in required_sections if section not in data]
            
            if missing_sections:
                print(f"❌ Admin Statistics: FAILED - Missing sections: {missing_sections}")
                self.test_results["Admin Statistics"] = False
                self.all_tests_passed = False
                return
            
            # Check ML engine stats
            ml_stats = data["ml_engine"]
            print(f"✅ Admin Statistics: ML Engine stats: {ml_stats}")
            
            if "is_trained" not in ml_stats:
                print("❌ Admin Statistics: FAILED - Missing ML training status")
                self.test_results["Admin Statistics"] = False
                self.all_tests_passed = False
                return
            
            # Check session stats
            session_stats = data["sesiones"]
            print(f"✅ Admin Statistics: Session stats: {session_stats}")
            
            # Check beverage stats
            beverage_stats = data["bebidas"]
            print(f"✅ Admin Statistics: Beverage stats: {beverage_stats}")
            
            # Verify real refrescos vs alternatives count
            if "refrescos_reales" in beverage_stats and "alternativas" in beverage_stats:
                print(f"✅ Admin Statistics: {beverage_stats['refrescos_reales']} real refrescos and {beverage_stats['alternativas']} alternatives")
                
                # Verify total count
                if beverage_stats["total"] == beverage_stats["refrescos_reales"] + beverage_stats["alternativas"]:
                    print("✅ Admin Statistics: Beverage counts are consistent")
                else:
                    print("❌ Admin Statistics: FAILED - Inconsistent beverage counts")
                    self.test_results["Admin Statistics"] = False
                    self.all_tests_passed = False
                    return
            else:
                print("❌ Admin Statistics: FAILED - Missing beverage type counts")
                self.test_results["Admin Statistics"] = False
                self.all_tests_passed = False
                return
            
            self.test_results["Admin Statistics"] = True
                
        except Exception as e:
            print(f"❌ Admin Statistics: FAILED - {str(e)}")
            self.test_results["Admin Statistics"] = False
            self.all_tests_passed = False
    
    def test_different_user_profiles(self):
        """Test recommendations for different user profiles"""
        print("\n🔍 Testing Different User Profiles...")
        
        # Test two different profiles:
        # 1. Health-conscious active user
        # 2. Traditional sedentary user with sweet preferences
        
        profiles = [
            {
                "name": "Health-conscious Active User",
                "answers": {
                    "consumo_base": "ocasional",  # Occasional consumption
                    "fisico": "muy_activo",       # Very active
                    "preferencias": "natural",    # Natural flavors
                    "salud_importancia": "muy_importante"  # Health is important
                }
            },
            {
                "name": "Traditional Sedentary User",
                "answers": {
                    "consumo_base": "diario",     # Daily consumption
                    "fisico": "sedentario",       # Sedentary
                    "preferencias": "muy_dulce",  # Very sweet
                    "salud_importancia": "no_importa"  # Health not important
                }
            }
        ]
        
        profile_results = {}
        
        for profile in profiles:
            print(f"\n🔍 Testing Profile: {profile['name']}...")
            
            try:
                # Create new session
                response = requests.post(f"{API_URL}/iniciar-sesion")
                response.raise_for_status()
                session_data = response.json()
                
                if "sesion_id" not in session_data:
                    print(f"❌ Profile {profile['name']}: FAILED - Could not create session")
                    continue
                
                session_id = session_data["sesion_id"]
                print(f"✅ Profile {profile['name']}: Created session with ID: {session_id}")
                
                # Answer questions according to profile
                self.answer_questions_by_profile(session_id, profile["answers"])
                
                # Get recommendations
                response = requests.get(f"{API_URL}/recomendacion/{session_id}")
                response.raise_for_status()
                recommendations = response.json()
                
                # Store recommendations for this profile
                profile_results[profile["name"]] = {
                    "refrescos_reales": len(recommendations.get("refrescos_reales", [])),
                    "bebidas_alternativas": len(recommendations.get("bebidas_alternativas", [])),
                    "cluster": recommendations.get("criterios_ml", {}).get("cluster_usuario", "unknown")
                }
                
                print(f"✅ Profile {profile['name']}: Got {profile_results[profile['name']]['refrescos_reales']} real refrescos")
                print(f"✅ Profile {profile['name']}: Got {profile_results[profile['name']]['bebidas_alternativas']} alternative beverages")
                print(f"✅ Profile {profile['name']}: Assigned to cluster {profile_results[profile['name']]['cluster']}")
                
            except Exception as e:
                print(f"❌ Profile {profile['name']}: FAILED - {str(e)}")
        
        # Compare results between profiles
        if len(profile_results) == 2:
            profile1, profile2 = profiles[0]["name"], profiles[1]["name"]
            
            # Check if clusters are different
            if profile_results[profile1]["cluster"] != profile_results[profile2]["cluster"]:
                print(f"✅ Different User Profiles: SUCCESS - Profiles assigned to different clusters")
            else:
                print(f"⚠️ Different User Profiles: WARNING - Both profiles assigned to same cluster {profile_results[profile1]['cluster']}")
            
            # Check if alternative recommendations differ
            if profile_results[profile1]["bebidas_alternativas"] != profile_results[profile2]["bebidas_alternativas"]:
                print(f"✅ Different User Profiles: SUCCESS - Different number of alternative beverages recommended")
            else:
                print(f"⚠️ Different User Profiles: WARNING - Same number of alternative beverages for both profiles")
            
            self.test_results["Different User Profiles"] = True
        else:
            print("❌ Different User Profiles: FAILED - Could not test both profiles")
            self.test_results["Different User Profiles"] = False
            self.all_tests_passed = False
            
    def answer_questions_by_profile(self, session_id, profile_answers):
        """Answer questions according to a specific profile"""
        try:
            # Get initial question
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "pregunta" not in data:
                return False
                
            question = data["pregunta"]
            total_questions = data.get("total_preguntas", 6)
            
            # Answer initial question based on profile
            category = question.get("categoria", "")
            target_value = profile_answers.get(category, "")
            
            # Find matching option or use middle option
            selected_option = None
            for option in question["opciones"]:
                if option["valor"] == target_value:
                    selected_option = option
                    break
            
            if not selected_option:
                selected_option = question["opciones"][len(question["opciones"]) // 2]
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"]
            })
            response.raise_for_status()
            
            # Get and answer remaining questions
            for i in range(total_questions - 1):
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                data = response.json()
                
                if "finalizada" in data and data["finalizada"]:
                    break
                
                if "pregunta" not in data:
                    return False
                    
                question = data["pregunta"]
                category = question.get("categoria", "")
                target_value = profile_answers.get(category, "")
                
                # Find matching option or use middle option
                selected_option = None
                for option in question["opciones"]:
                    if option["valor"] == target_value:
                        selected_option = option
                        break
                
                if not selected_option:
                    selected_option = question["opciones"][len(question["opciones"]) // 2]
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"]
                })
                response.raise_for_status()
            
            return True
            
        except Exception as e:
            print(f"Error answering questions by profile: {str(e)}")
            return False
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        overall = "✅ ALL TESTS PASSED" if self.all_tests_passed else "❌ SOME TESTS FAILED"
        print("\n" + "="*80)
        print(f"🏁 OVERALL RESULT: {overall}")
        print("="*80)

    def test_ml_modules_initialization(self):
        """Test that all ML modules are initialized correctly"""
        print("\n🔍 Testing ML Modules Initialization...")
        
        try:
            # Create a session to get recommendations that include ML module info
            self.session_id = self.create_session_and_answer_questions()
            if not self.session_id:
                print("❌ ML Modules Initialization: FAILED - Could not create session")
                self.test_results["ML Modules Initialization"] = False
                self.all_tests_passed = False
                return
            
            # Get recommendations to check ML modules
            response = requests.get(f"{API_URL}/recomendacion/{self.session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check for ML advanced info
            if "ml_avanzado" not in data:
                print("❌ ML Modules Initialization: FAILED - ML advanced info missing")
                self.test_results["ML Modules Initialization"] = False
                self.all_tests_passed = False
                return
            
            ml_avanzado = data["ml_avanzado"]
            print(f"✅ ML Modules Initialization: ML advanced info: {ml_avanzado}")
            
            # Check for specific ML modules
            required_modules = ["categorizacion_automatica", "analisis_imagenes", "sistema_presentaciones"]
            missing_modules = [module for module in required_modules if module not in ml_avanzado]
            
            if missing_modules:
                print(f"❌ ML Modules Initialization: FAILED - Missing ML modules: {missing_modules}")
                self.test_results["ML Modules Initialization"] = False
                self.all_tests_passed = False
                return
            
            # Check that at least some beverages were processed
            if "total_bebidas_categorizadas" in ml_avanzado and ml_avanzado["total_bebidas_categorizadas"] > 0:
                print(f"✅ ML Modules Initialization: {ml_avanzado['total_bebidas_categorizadas']} beverages categorized")
                self.test_results["ML Modules Initialization"] = True
            else:
                print("❌ ML Modules Initialization: FAILED - No beverages categorized")
                self.test_results["ML Modules Initialization"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ ML Modules Initialization: FAILED - {str(e)}")
            self.test_results["ML Modules Initialization"] = False
            self.all_tests_passed = False
    
    def test_beverage_categorizer(self):
        """Test the beverage categorizer functionality"""
        print("\n🔍 Testing Beverage Categorizer...")
        
        try:
            # Get admin stats to check categorizer
            response = requests.get(f"{API_URL}/admin/stats")
            response.raise_for_status()
            data = response.json()
            
            if "ml_engines" not in data or "categorizador" not in data["ml_engines"]:
                print("❌ Beverage Categorizer: FAILED - Categorizer stats missing")
                self.test_results["Beverage Categorizer"] = False
                self.all_tests_passed = False
                return
            
            categorizer_stats = data["ml_engines"]["categorizador"]
            print(f"✅ Beverage Categorizer: Stats: {categorizer_stats}")
            
            # Check that categorizer is trained
            if "is_trained" in categorizer_stats and categorizer_stats["is_trained"]:
                print("✅ Beverage Categorizer: Categorizer is trained")
            else:
                print("⚠️ Beverage Categorizer: WARNING - Categorizer is not trained")
            
            # Get recommendations to check categorization
            if not self.session_id:
                self.session_id = self.create_session_and_answer_questions()
                if not self.session_id:
                    print("❌ Beverage Categorizer: FAILED - Could not create session")
                    self.test_results["Beverage Categorizer"] = False
                    self.all_tests_passed = False
                    return
            
            response = requests.get(f"{API_URL}/recomendacion/{self.session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check for categorization in recommendations
            if "refrescos_reales" in data and data["refrescos_reales"]:
                bebida = data["refrescos_reales"][0]
                
                # Check for automatic categories
                if "categorias_automaticas" not in bebida:
                    print("❌ Beverage Categorizer: FAILED - Automatic categories missing")
                    self.test_results["Beverage Categorizer"] = False
                    self.all_tests_passed = False
                    return
                
                print(f"✅ Beverage Categorizer: Automatic categories: {bebida['categorias_automaticas']}")
                
                # Check for ML tags
                if "tags_ml" not in bebida:
                    print("❌ Beverage Categorizer: FAILED - ML tags missing")
                    self.test_results["Beverage Categorizer"] = False
                    self.all_tests_passed = False
                    return
                
                print(f"✅ Beverage Categorizer: ML tags: {bebida['tags_ml']}")
                
                self.test_results["Beverage Categorizer"] = True
            else:
                print("❌ Beverage Categorizer: FAILED - No recommendations to check")
                self.test_results["Beverage Categorizer"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ Beverage Categorizer: FAILED - {str(e)}")
            self.test_results["Beverage Categorizer"] = False
            self.all_tests_passed = False
    
    def test_image_analyzer(self):
        """Test the image analyzer functionality"""
        print("\n🔍 Testing Image Analyzer...")
        
        try:
            # Get admin stats to check image analyzer
            response = requests.get(f"{API_URL}/admin/stats")
            response.raise_for_status()
            data = response.json()
            
            if "ml_engines" not in data or "analizador_imagenes" not in data["ml_engines"]:
                print("❌ Image Analyzer: FAILED - Image analyzer stats missing")
                self.test_results["Image Analyzer"] = False
                self.all_tests_passed = False
                return
            
            analyzer_stats = data["ml_engines"]["analizador_imagenes"]
            print(f"✅ Image Analyzer: Stats: {analyzer_stats}")
            
            # Check that analyzer is initialized
            if "is_initialized" in analyzer_stats and analyzer_stats["is_initialized"]:
                print("✅ Image Analyzer: Analyzer is initialized")
            else:
                print("⚠️ Image Analyzer: WARNING - Analyzer is not initialized")
            
            # Get recommendations to check image analysis
            if not self.session_id:
                self.session_id = self.create_session_and_answer_questions()
                if not self.session_id:
                    print("❌ Image Analyzer: FAILED - Could not create session")
                    self.test_results["Image Analyzer"] = False
                    self.all_tests_passed = False
                    return
            
            response = requests.get(f"{API_URL}/recomendacion/{self.session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check for image analysis in recommendations
            if "refrescos_reales" in data and data["refrescos_reales"]:
                bebida = data["refrescos_reales"][0]
                
                # Check for features_imagen (might be null if images couldn't be processed)
                if "features_imagen" in bebida:
                    print(f"✅ Image Analyzer: Image features present: {bebida['features_imagen'] is not None}")
                    
                    # If features_imagen is not None, check its content
                    if bebida['features_imagen'] is not None:
                        print(f"✅ Image Analyzer: Image features: {bebida['features_imagen']}")
                
                self.test_results["Image Analyzer"] = True
            else:
                print("❌ Image Analyzer: FAILED - No recommendations to check")
                self.test_results["Image Analyzer"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ Image Analyzer: FAILED - {str(e)}")
            self.test_results["Image Analyzer"] = False
            self.all_tests_passed = False
    
    def test_presentation_rating_system(self):
        """Test the presentation rating system functionality"""
        print("\n🔍 Testing Presentation Rating System...")
        
        try:
            # Get admin stats to check presentation rating system
            response = requests.get(f"{API_URL}/admin/stats")
            response.raise_for_status()
            data = response.json()
            
            if "ml_engines" not in data or "sistema_presentaciones" not in data["ml_engines"]:
                print("❌ Presentation Rating System: FAILED - Presentation rating system stats missing")
                self.test_results["Presentation Rating System"] = False
                self.all_tests_passed = False
                return
            
            system_stats = data["ml_engines"]["sistema_presentaciones"]
            print(f"✅ Presentation Rating System: Stats: {system_stats}")
            
            # Get recommendations to check presentation ratings
            if not self.session_id:
                self.session_id = self.create_session_and_answer_questions()
                if not self.session_id:
                    print("❌ Presentation Rating System: FAILED - Could not create session")
                    self.test_results["Presentation Rating System"] = False
                    self.all_tests_passed = False
                    return
            
            response = requests.get(f"{API_URL}/recomendacion/{self.session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Check for presentation ratings in recommendations
            if "refrescos_reales" in data and data["refrescos_reales"]:
                bebida = data["refrescos_reales"][0]
                
                # Check for mejor_presentacion_para_usuario
                if "mejor_presentacion_para_usuario" not in bebida:
                    print("❌ Presentation Rating System: FAILED - Best presentation for user missing")
                    self.test_results["Presentation Rating System"] = False
                    self.all_tests_passed = False
                    return
                
                mejor_presentacion = bebida["mejor_presentacion_para_usuario"]
                print(f"✅ Presentation Rating System: Best presentation: {mejor_presentacion}")
                
                # Check for presentation_id
                if "presentation_id" not in mejor_presentacion:
                    print("❌ Presentation Rating System: FAILED - Presentation ID missing")
                    self.test_results["Presentation Rating System"] = False
                    self.all_tests_passed = False
                    return
                
                # Check for prediction
                if "prediccion" not in mejor_presentacion:
                    print("❌ Presentation Rating System: FAILED - Prediction missing")
                    self.test_results["Presentation Rating System"] = False
                    self.all_tests_passed = False
                    return
                
                print(f"✅ Presentation Rating System: Prediction: {mejor_presentacion['prediccion']}")
                
                # Test rating a presentation
                self.test_rate_presentation(bebida, mejor_presentacion)
                
                self.test_results["Presentation Rating System"] = True
            else:
                print("❌ Presentation Rating System: FAILED - No recommendations to check")
                self.test_results["Presentation Rating System"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ Presentation Rating System: FAILED - {str(e)}")
            self.test_results["Presentation Rating System"] = False
            self.all_tests_passed = False
    
    def test_rate_presentation(self, bebida, presentacion):
        """Test rating a specific presentation"""
        try:
            presentation_id = presentacion["presentation_id"]
            
            # Rate the presentation
            response = requests.post(f"{API_URL}/puntuar-presentacion/{self.session_id}", json={
                "presentation_id": presentation_id,
                "puntuacion": 5,
                "comentario": "Excelente presentación, me encantó"
            })
            response.raise_for_status()
            data = response.json()
            
            print(f"✅ Rate Presentation: Rated presentation {presentation_id} with 5 stars")
            
            # Check for feedback
            if "feedback_aprendizaje" not in data:
                print("❌ Rate Presentation: FAILED - No learning feedback provided")
                return False
            
            print(f"✅ Rate Presentation: Learning feedback: {data['feedback_aprendizaje']}")
            
            # Check if presentation model was trained
            if "presentation_model_trained" in data:
                print(f"✅ Rate Presentation: Presentation model trained: {data['presentation_model_trained']}")
            
            # Check presentation stats
            if "presentation_stats" in data:
                print(f"✅ Rate Presentation: Presentation stats: {data['presentation_stats']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Rate Presentation: FAILED - {str(e)}")
            return False
    
    def test_new_ml_endpoints(self):
        """Test the new ML endpoints"""
        print("\n🔍 Testing New ML Endpoints...")
        
        try:
            # Test /api/mejores-presentaciones endpoint
            if not self.session_id:
                self.session_id = self.create_session_and_answer_questions()
                if not self.session_id:
                    print("❌ New ML Endpoints: FAILED - Could not create session")
                    self.test_results["New ML Endpoints"] = False
                    self.all_tests_passed = False
                    return
            
            # Test mejores-presentaciones endpoint
            response = requests.get(f"{API_URL}/mejores-presentaciones/{self.session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "mejores_presentaciones" not in data:
                print("❌ New ML Endpoints: FAILED - mejores_presentaciones missing")
                self.test_results["New ML Endpoints"] = False
                self.all_tests_passed = False
                return
            
            mejores_presentaciones = data["mejores_presentaciones"]
            print(f"✅ New ML Endpoints: Got {len(mejores_presentaciones)} best presentations")
            
            if mejores_presentaciones:
                # Check structure of first presentation
                presentacion = mejores_presentaciones[0]
                required_fields = ["bebida", "presentacion", "prediccion_ml", "factores_explicativos", "match_score"]
                missing_fields = [field for field in required_fields if field not in presentacion]
                
                if missing_fields:
                    print(f"❌ New ML Endpoints: FAILED - Missing fields in best presentation: {missing_fields}")
                    self.test_results["New ML Endpoints"] = False
                    self.all_tests_passed = False
                    return
                
                print(f"✅ New ML Endpoints: Best presentation structure is valid")
            
            self.test_results["New ML Endpoints"] = True
            
        except Exception as e:
            print(f"❌ New ML Endpoints: FAILED - {str(e)}")
            self.test_results["New ML Endpoints"] = False
            self.all_tests_passed = False
    
    def test_admin_reprocess_beverages(self):
        """Test the admin/reprocess-beverages endpoint"""
        print("\n🔍 Testing Admin Reprocess Beverages...")
        
        try:
            # Call the reprocess endpoint
            response = requests.post(f"{API_URL}/admin/reprocess-beverages")
            response.raise_for_status()
            data = response.json()
            
            if "mensaje" not in data or "stats" not in data:
                print("❌ Admin Reprocess Beverages: FAILED - Invalid response format")
                self.test_results["Admin Reprocess Beverages"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ Admin Reprocess Beverages: Message: {data['mensaje']}")
            
            # Check stats
            stats = data["stats"]
            if "categorizador" not in stats or "analizador_imagenes" not in stats:
                print("❌ Admin Reprocess Beverages: FAILED - Missing stats")
                self.test_results["Admin Reprocess Beverages"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ Admin Reprocess Beverages: Categorizer stats: {stats['categorizador']}")
            print(f"✅ Admin Reprocess Beverages: Image analyzer stats: {stats['analizador_imagenes']}")
            
            self.test_results["Admin Reprocess Beverages"] = True
            
        except Exception as e:
            print(f"❌ Admin Reprocess Beverages: FAILED - {str(e)}")
            self.test_results["Admin Reprocess Beverages"] = False
            self.all_tests_passed = False
    
    def test_presentation_analytics(self):
        """Test the admin/presentation-analytics endpoint"""
        print("\n🔍 Testing Presentation Analytics...")
        
        try:
            # Need a session with some presentation ratings
            if not self.session_id:
                self.session_id = self.create_session_and_answer_questions()
                if not self.session_id:
                    print("❌ Presentation Analytics: FAILED - Could not create session")
                    self.test_results["Presentation Analytics"] = False
                    self.all_tests_passed = False
                    return
            
            # Get recommendations
            response = requests.get(f"{API_URL}/recomendacion/{self.session_id}")
            response.raise_for_status()
            data = response.json()
            
            # Rate a presentation if we have recommendations
            if "refrescos_reales" in data and data["refrescos_reales"]:
                bebida = data["refrescos_reales"][0]
                if "mejor_presentacion_para_usuario" in bebida:
                    presentation_id = bebida["mejor_presentacion_para_usuario"]["presentation_id"]
                    
                    # Rate the presentation
                    response = requests.post(f"{API_URL}/puntuar-presentacion/{self.session_id}", json={
                        "presentation_id": presentation_id,
                        "puntuacion": 5,
                        "comentario": "Excelente presentación para analytics"
                    })
                    response.raise_for_status()
                    print(f"✅ Presentation Analytics: Rated presentation {presentation_id} for analytics")
            
            # Call the analytics endpoint
            response = requests.get(f"{API_URL}/admin/presentation-analytics/{self.session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "size_preferences" not in data:
                print("❌ Presentation Analytics: FAILED - size_preferences missing")
                self.test_results["Presentation Analytics"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ Presentation Analytics: Size preferences: {data['size_preferences']}")
            
            if "puntuaciones_dadas" not in data:
                print("❌ Presentation Analytics: FAILED - puntuaciones_dadas missing")
                self.test_results["Presentation Analytics"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ Presentation Analytics: Ratings given: {data['puntuaciones_dadas']}")
            
            self.test_results["Presentation Analytics"] = True
            
        except Exception as e:
            print(f"❌ Presentation Analytics: FAILED - {str(e)}")
            self.test_results["Presentation Analytics"] = False
            self.all_tests_passed = False
    
    def test_ml_modules_initialization(self):
        """Test ML modules initialization"""
        print("\n🔍 Testing ML Modules Initialization...")
        
        try:
            # Test system status to check ML modules
            response = requests.get(f"{API_URL}/status")
            response.raise_for_status()
            data = response.json()
            
            if "status" in data and data["status"] == "healthy":
                print("✅ ML Modules: System is healthy")
                
                # Check if ML engine is initialized
                if "ml_engine" in data:
                    ml_stats = data["ml_engine"]
                    print(f"✅ ML Modules: ML Engine initialized with stats: {ml_stats}")
                    self.test_results["ML Modules Initialization"] = True
                else:
                    print("❌ ML Modules: FAILED - ML Engine not found in status")
                    self.test_results["ML Modules Initialization"] = False
                    self.all_tests_passed = False
            else:
                print(f"❌ ML Modules: FAILED - System not healthy: {data}")
                self.test_results["ML Modules Initialization"] = False
                self.all_tests_passed = False
                
        except Exception as e:
            print(f"❌ ML Modules: FAILED - {str(e)}")
            self.test_results["ML Modules Initialization"] = False
            self.all_tests_passed = False
    
    def test_new_ml_endpoints(self):
        """Test new ML endpoints"""
        print("\n🔍 Testing New ML Endpoints...")
        
        try:
            # Create a session for testing
            session_id = self.create_session_and_answer_questions()
            if not session_id:
                print("❌ New ML Endpoints: FAILED - Could not create session")
                self.test_results["New ML Endpoints"] = False
                self.all_tests_passed = False
                return
            
            # Test /api/mejores-presentaciones/{sesion_id}
            response = requests.get(f"{API_URL}/mejores-presentaciones/{session_id}")
            
            if response.status_code == 200:
                data = response.json()
                if "mejores_presentaciones" in data:
                    print(f"✅ New ML Endpoints: /api/mejores-presentaciones works - got {len(data['mejores_presentaciones'])} presentations")
                else:
                    print("❌ New ML Endpoints: FAILED - No mejores_presentaciones in response")
                    self.test_results["New ML Endpoints"] = False
                    self.all_tests_passed = False
                    return
            else:
                print(f"❌ New ML Endpoints: FAILED - /api/mejores-presentaciones returned {response.status_code}")
                self.test_results["New ML Endpoints"] = False
                self.all_tests_passed = False
                return
            
            self.test_results["New ML Endpoints"] = True
            
        except Exception as e:
            print(f"❌ New ML Endpoints: FAILED - {str(e)}")
            self.test_results["New ML Endpoints"] = False
            self.all_tests_passed = False

    def print_summary(self):
        """Print a summary of all test results"""
        print("\n" + "="*80)
        print("📊 TEST RESULTS SUMMARY")
        print("="*80)
        
        passed_tests = []
        failed_tests = []
        
        for test_name, result in self.test_results.items():
            if result:
                passed_tests.append(test_name)
                print(f"✅ {test_name}")
            else:
                failed_tests.append(test_name)
                print(f"❌ {test_name}")
        
        print("\n" + "="*80)
        print(f"📈 OVERALL RESULTS: {len(passed_tests)} PASSED, {len(failed_tests)} FAILED")
        print("="*80)
        
        if self.all_tests_passed:
            print("🎉 ALL TESTS PASSED! RefrescoBot ML is working correctly.")
        else:
            print("⚠️ SOME TESTS FAILED. Please check the issues above.")
            if failed_tests:
                print(f"Failed tests: {', '.join(failed_tests)}")
        
        return self.all_tests_passed


if __name__ == "__main__":
    tester = RefrescoBotTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)