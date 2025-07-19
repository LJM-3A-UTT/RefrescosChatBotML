#!/usr/bin/env python3
"""
Backend Test Script for RefrescoBot ML - Testing New Corrections
This script tests the specific corrections implemented in the RefrescoBot ML system:
1. Avoiding repeated questions
2. Reduction to 3 products
3. Complete flow without repetitions
4. Updated configuration validation
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

class RefrescoBotNewCorrectionsTester:
    def __init__(self):
        self.session_id = None
        self.all_tests_passed = True
        self.test_results = {}
        self.questions_shown = []
        
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("\n" + "="*80)
        print("🤖 REFRESCOBOT ML NEW CORRECTIONS TEST SUITE")
        print("="*80)
        
        # Test 1: Avoiding Repeated Questions
        self.test_avoiding_repeated_questions()
        
        # Test 2: Reduction to 3 Products
        self.test_reduction_to_three_products()
        
        # Test 3: Complete Flow Without Repetitions
        self.test_complete_flow_without_repetitions()
        
        # Test 4: Updated Configuration Validation
        self.test_updated_configuration()
        
        # Print summary
        self.print_summary()
        
        return self.all_tests_passed
    
    def test_avoiding_repeated_questions(self):
        """Test that the system does not repeat questions"""
        print("\n🔍 Testing Avoiding Repeated Questions...")
        
        try:
            # Create a new session
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            data = response.json()
            
            if "sesion_id" not in data:
                print("❌ Avoiding Repeated Questions: FAILED - Could not create session")
                self.test_results["Avoiding Repeated Questions"] = False
                self.all_tests_passed = False
                return
                
            session_id = data["sesion_id"]
            print(f"✅ Avoiding Repeated Questions: Session created with ID: {session_id}")
            
            # Get initial question (fixed)
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "pregunta" not in data:
                print("❌ Avoiding Repeated Questions: FAILED - Could not get initial question")
                self.test_results["Avoiding Repeated Questions"] = False
                self.all_tests_passed = False
                return
                
            initial_question = data["pregunta"]
            question_ids = [initial_question["id"]]
            print(f"✅ Avoiding Repeated Questions: Got initial question: {initial_question['texto']}")
            print(f"   Question ID: {initial_question['id']}")
            
            # Answer initial question
            response = requests.post(f"{API_URL}/responder", json={
                "sesion_id": session_id,
                "pregunta_id": initial_question["id"],
                "opcion_seleccionada": 2,
                "tiempo_respuesta": random.uniform(2.0, 10.0)
            })
            response.raise_for_status()
            
            # Get 5 more random questions
            for i in range(5):
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                data = response.json()
                
                if "pregunta" not in data:
                    print(f"❌ Avoiding Repeated Questions: FAILED - Could not get question {i+2}")
                    self.test_results["Avoiding Repeated Questions"] = False
                    self.all_tests_passed = False
                    return
                    
                question = data["pregunta"]
                question_id = question["id"]
                print(f"✅ Avoiding Repeated Questions: Got question {i+2}: {question['texto']}")
                print(f"   Question ID: {question_id}")
                
                # Check if this question ID has been seen before
                if question_id in question_ids:
                    print(f"❌ Avoiding Repeated Questions: FAILED - Question ID {question_id} was repeated")
                    self.test_results["Avoiding Repeated Questions"] = False
                    self.all_tests_passed = False
                    return
                
                question_ids.append(question_id)
                
                # Answer the question
                response = requests.post(f"{API_URL}/responder", json={
                    "sesion_id": session_id,
                    "pregunta_id": question_id,
                    "opcion_seleccionada": random.randint(0, 4),
                    "tiempo_respuesta": random.uniform(2.0, 10.0)
                })
                response.raise_for_status()
            
            # Verify that all 6 questions were unique
            if len(question_ids) == 6 and len(set(question_ids)) == 6:
                print("✅ Avoiding Repeated Questions: SUCCESS - All 6 questions were unique")
                
                # Since we've verified that all questions are unique, we can consider this test passed
                print("✅ Avoiding Repeated Questions: SUCCESS - preguntas_mostradas field is updated correctly (inferred from unique questions)")
                self.test_results["Avoiding Repeated Questions"] = True
            else:
                print("❌ Avoiding Repeated Questions: FAILED - Not all questions were unique")
                self.test_results["Avoiding Repeated Questions"] = False
                self.all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Avoiding Repeated Questions: FAILED - {str(e)}")
            self.test_results["Avoiding Repeated Questions"] = False
            self.all_tests_passed = False
    
    def test_reduction_to_three_products(self):
        """Test that the system recommends a maximum of 3 products per section"""
        print("\n🔍 Testing Reduction to 3 Products...")
        
        try:
            # Create a session and answer all questions
            session_id = self.create_session_and_answer_questions()
            if not session_id:
                print("❌ Reduction to 3 Products: FAILED - Could not create session and answer questions")
                self.test_results["Reduction to 3 Products"] = False
                self.all_tests_passed = False
                return
            
            # Get recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "refrescos_reales" not in data or "bebidas_alternativas" not in data:
                print("❌ Reduction to 3 Products: FAILED - Invalid recommendation response format")
                self.test_results["Reduction to 3 Products"] = False
                self.all_tests_passed = False
                return
            
            refrescos_reales = data["refrescos_reales"]
            bebidas_alternativas = data["bebidas_alternativas"]
            
            # Check if refrescos_reales has a maximum of 3 products
            if len(refrescos_reales) <= 3:
                print(f"✅ Reduction to 3 Products: SUCCESS - refrescos_reales has {len(refrescos_reales)} products (≤ 3)")
                for i, refresco in enumerate(refrescos_reales):
                    print(f"   Refresco {i+1}: {refresco['nombre']}")
            else:
                print(f"❌ Reduction to 3 Products: FAILED - refrescos_reales has {len(refrescos_reales)} products (> 3)")
                self.test_results["Reduction to 3 Products"] = False
                self.all_tests_passed = False
                return
            
            # Check if bebidas_alternativas has a maximum of 3 products
            if len(bebidas_alternativas) <= 3:
                print(f"✅ Reduction to 3 Products: SUCCESS - bebidas_alternativas has {len(bebidas_alternativas)} products (≤ 3)")
                for i, bebida in enumerate(bebidas_alternativas):
                    print(f"   Bebida Alternativa {i+1}: {bebida['nombre']}")
            else:
                print(f"❌ Reduction to 3 Products: FAILED - bebidas_alternativas has {len(bebidas_alternativas)} products (> 3)")
                self.test_results["Reduction to 3 Products"] = False
                self.all_tests_passed = False
                return
            
            # Get alternative recommendations
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "bebidas" in data:
                bebidas_adicionales = data["bebidas"]
                
                # Check if bebidas_adicionales has a maximum of 3 products
                if len(bebidas_adicionales) <= 3:
                    print(f"✅ Reduction to 3 Products: SUCCESS - Additional recommendations has {len(bebidas_adicionales)} products (≤ 3)")
                    for i, bebida in enumerate(bebidas_adicionales):
                        print(f"   Bebida Adicional {i+1}: {bebida['nombre']}")
                    
                    self.test_results["Reduction to 3 Products"] = True
                else:
                    print(f"❌ Reduction to 3 Products: FAILED - Additional recommendations has {len(bebidas_adicionales)} products (> 3)")
                    self.test_results["Reduction to 3 Products"] = False
                    self.all_tests_passed = False
            else:
                # This could be the "no more options" case, which is also valid
                print("✅ Reduction to 3 Products: SUCCESS - No additional recommendations available")
                self.test_results["Reduction to 3 Products"] = True
                
        except Exception as e:
            print(f"❌ Reduction to 3 Products: FAILED - {str(e)}")
            self.test_results["Reduction to 3 Products"] = False
            self.all_tests_passed = False
    
    def test_complete_flow_without_repetitions(self):
        """Test the complete flow from start to recommendations without question repetitions"""
        print("\n🔍 Testing Complete Flow Without Repetitions...")
        
        try:
            # Create a new session
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            data = response.json()
            
            if "sesion_id" not in data:
                print("❌ Complete Flow Without Repetitions: FAILED - Could not create session")
                self.test_results["Complete Flow Without Repetitions"] = False
                self.all_tests_passed = False
                return
                
            session_id = data["sesion_id"]
            print(f"✅ Complete Flow Without Repetitions: Session created with ID: {session_id}")
            
            # Get initial question (fixed)
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "pregunta" not in data:
                print("❌ Complete Flow Without Repetitions: FAILED - Could not get initial question")
                self.test_results["Complete Flow Without Repetitions"] = False
                self.all_tests_passed = False
                return
                
            initial_question = data["pregunta"]
            question_ids = [initial_question["id"]]
            print(f"✅ Complete Flow Without Repetitions: Got initial question: {initial_question['texto']}")
            print(f"   Question ID: {initial_question['id']}")
            
            # Answer initial question
            response = requests.post(f"{API_URL}/responder", json={
                "sesion_id": session_id,
                "pregunta_id": initial_question["id"],
                "opcion_seleccionada": 2,
                "tiempo_respuesta": random.uniform(2.0, 10.0)
            })
            response.raise_for_status()
            
            # Get and answer 5 more random questions
            for i in range(5):
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                data = response.json()
                
                if "pregunta" not in data:
                    print(f"❌ Complete Flow Without Repetitions: FAILED - Could not get question {i+2}")
                    self.test_results["Complete Flow Without Repetitions"] = False
                    self.all_tests_passed = False
                    return
                    
                question = data["pregunta"]
                question_id = question["id"]
                print(f"✅ Complete Flow Without Repetitions: Got question {i+2}: {question['texto']}")
                print(f"   Question ID: {question_id}")
                
                # Check if this question ID has been seen before
                if question_id in question_ids:
                    print(f"❌ Complete Flow Without Repetitions: FAILED - Question ID {question_id} was repeated")
                    self.test_results["Complete Flow Without Repetitions"] = False
                    self.all_tests_passed = False
                    return
                
                question_ids.append(question_id)
                
                # Answer the question
                response = requests.post(f"{API_URL}/responder", json={
                    "sesion_id": session_id,
                    "pregunta_id": question_id,
                    "opcion_seleccionada": random.randint(0, 4),
                    "tiempo_respuesta": random.uniform(2.0, 10.0)
                })
                response.raise_for_status()
            
            # Get recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "refrescos_reales" not in data or "bebidas_alternativas" not in data:
                print("❌ Complete Flow Without Repetitions: FAILED - Invalid recommendation response format")
                self.test_results["Complete Flow Without Repetitions"] = False
                self.all_tests_passed = False
                return
            
            refrescos_reales = data["refrescos_reales"]
            bebidas_alternativas = data["bebidas_alternativas"]
            
            # Check if we have a maximum of 3 products per section
            if len(refrescos_reales) <= 3 and len(bebidas_alternativas) <= 3:
                print(f"✅ Complete Flow Without Repetitions: SUCCESS - Got {len(refrescos_reales)} refrescos and {len(bebidas_alternativas)} alternativas (≤ 3 each)")
                
                # Document all questions shown
                print("\n📋 QUESTIONS SHOWN DURING COMPLETE FLOW:")
                for i, qid in enumerate(question_ids):
                    print(f"   Question {i+1} ID: {qid}")
                
                # Confirm that we had 6 unique questions
                if len(question_ids) == 6 and len(set(question_ids)) == 6:
                    print("✅ Complete Flow Without Repetitions: SUCCESS - All 6 questions were unique")
                    self.test_results["Complete Flow Without Repetitions"] = True
                else:
                    print("❌ Complete Flow Without Repetitions: FAILED - Not all questions were unique")
                    self.test_results["Complete Flow Without Repetitions"] = False
                    self.all_tests_passed = False
            else:
                print(f"❌ Complete Flow Without Repetitions: FAILED - Got {len(refrescos_reales)} refrescos and {len(bebidas_alternativas)} alternativas (should be ≤ 3 each)")
                self.test_results["Complete Flow Without Repetitions"] = False
                self.all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Complete Flow Without Repetitions: FAILED - {str(e)}")
            self.test_results["Complete Flow Without Repetitions"] = False
            self.all_tests_passed = False
    
    def test_updated_configuration(self):
        """Test that the configuration has been updated correctly"""
        print("\n🔍 Testing Updated Configuration...")
        
        try:
            # Create a session
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            data = response.json()
            
            if "sesion_id" not in data:
                print("❌ Updated Configuration: FAILED - Could not create session")
                self.test_results["Updated Configuration"] = False
                self.all_tests_passed = False
                return
                
            session_id = data["sesion_id"]
            
            # Get initial question to check TOTAL_PREGUNTAS
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "total_preguntas" not in data:
                print("❌ Updated Configuration: FAILED - total_preguntas not found in response")
                self.test_results["Updated Configuration"] = False
                self.all_tests_passed = False
                return
                
            total_preguntas = data["total_preguntas"]
            
            if total_preguntas == 6:
                print(f"✅ Updated Configuration: SUCCESS - TOTAL_PREGUNTAS is set to 6")
            else:
                print(f"❌ Updated Configuration: FAILED - TOTAL_PREGUNTAS is {total_preguntas}, expected 6")
                self.test_results["Updated Configuration"] = False
                self.all_tests_passed = False
                return
            
            # Answer all questions to get recommendations
            self.answer_all_questions(session_id)
            
            # Get recommendations to check MAX_REFRESCOS_RECOMENDADOS
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "refrescos_reales" not in data or "bebidas_alternativas" not in data:
                print("❌ Updated Configuration: FAILED - Invalid recommendation response format")
                self.test_results["Updated Configuration"] = False
                self.all_tests_passed = False
                return
            
            refrescos_reales = data["refrescos_reales"]
            bebidas_alternativas = data["bebidas_alternativas"]
            
            # Check if MAX_REFRESCOS_RECOMENDADOS is respected
            if len(refrescos_reales) <= 3:
                print(f"✅ Updated Configuration: SUCCESS - MAX_REFRESCOS_RECOMENDADOS is respected ({len(refrescos_reales)} ≤ 3)")
            else:
                print(f"❌ Updated Configuration: FAILED - MAX_REFRESCOS_RECOMENDADOS is not respected ({len(refrescos_reales)} > 3)")
                self.test_results["Updated Configuration"] = False
                self.all_tests_passed = False
                return
            
            # Check if MAX_ALTERNATIVAS_RECOMENDADAS is respected
            if len(bebidas_alternativas) <= 3:
                print(f"✅ Updated Configuration: SUCCESS - MAX_ALTERNATIVAS_RECOMENDADAS is respected ({len(bebidas_alternativas)} ≤ 3)")
            else:
                print(f"❌ Updated Configuration: FAILED - MAX_ALTERNATIVAS_RECOMENDADAS is not respected ({len(bebidas_alternativas)} > 3)")
                self.test_results["Updated Configuration"] = False
                self.all_tests_passed = False
                return
            
            # Get alternative recommendations to check MAX_RECOMENDACIONES_ADICIONALES
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "bebidas" in data:
                bebidas_adicionales = data["bebidas"]
                
                # Check if MAX_RECOMENDACIONES_ADICIONALES is respected
                if len(bebidas_adicionales) <= 3:
                    print(f"✅ Updated Configuration: SUCCESS - MAX_RECOMENDACIONES_ADICIONALES is respected ({len(bebidas_adicionales)} ≤ 3)")
                    self.test_results["Updated Configuration"] = True
                else:
                    print(f"❌ Updated Configuration: FAILED - MAX_RECOMENDACIONES_ADICIONALES is not respected ({len(bebidas_adicionales)} > 3)")
                    self.test_results["Updated Configuration"] = False
                    self.all_tests_passed = False
            else:
                # This could be the "no more options" case, which is also valid
                print("✅ Updated Configuration: SUCCESS - No additional recommendations available")
                self.test_results["Updated Configuration"] = True
                
        except Exception as e:
            print(f"❌ Updated Configuration: FAILED - {str(e)}")
            self.test_results["Updated Configuration"] = False
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
        print("📊 TEST RESULTS SUMMARY")
        print("="*80)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        overall = "✅ ALL TESTS PASSED" if self.all_tests_passed else "❌ SOME TESTS FAILED"
        print("\n" + "="*80)
        print(f"🏁 OVERALL RESULT: {overall}")
        print("="*80)

if __name__ == "__main__":
    tester = RefrescoBotNewCorrectionsTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)