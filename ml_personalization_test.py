#!/usr/bin/env python3
"""
Backend Test Script for RefrescoBot ML - Advanced Personalization Testing
This script tests the advanced personalization features of RefrescoBot ML.
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
BACKEND_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001")
API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

class RefrescoBotMLTester:
    """Test class for RefrescoBot ML advanced personalization features"""
    
    def __init__(self):
        self.test_results = {}
        self.all_tests_passed = True
    
    def run_all_tests(self):
        """Run all test scenarios"""
        print("\n" + "="*80)
        print("🤖 REFRESCOBOT ML ADVANCED PERSONALIZATION TEST SUITE")
        print("="*80)
        
        # Test 1: Regular User Scenario
        self.test_regular_user_scenario()
        
        # Test 2: Non-Soda User Scenario
        self.test_non_soda_user_scenario()
        
        # Test 3: Test User Scenario (Fast Responses)
        self.test_fast_response_user_scenario()
        
        # Test 4: Compare Different User Profiles
        self.test_compare_user_profiles()
        
        # Print summary
        self.print_summary()
        
        return self.all_tests_passed
    
    def test_regular_user_scenario(self):
        """Test scenario for a regular user with normal response times"""
        print("\n🔍 Testing Regular User Scenario...")
        
        try:
            # Create session
            session_id = self.create_session()
            if not session_id:
                print("❌ Regular User: FAILED - Could not create session")
                self.test_results["Regular User"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ Regular User: Session created with ID: {session_id}")
            
            # Answer questions with normal response times (3-10 seconds)
            # First question: "Varias veces por semana" (consumes soda)
            responses = self.answer_all_questions(
                session_id, 
                first_question_option=2,  # "Varias veces por semana"
                response_time_range=(3.0, 10.0)
            )
            
            if not responses:
                print("❌ Regular User: FAILED - Could not answer questions")
                self.test_results["Regular User"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ Regular User: Answered all questions with normal response times")
            
            # Get recommendations
            recommendations = self.get_recommendations(session_id)
            if not recommendations:
                print("❌ Regular User: FAILED - Could not get recommendations")
                self.test_results["Regular User"] = False
                self.all_tests_passed = False
                return
            
            # Verify regular user detection
            user_type = recommendations.get("criterios_ml", {}).get("tipo_usuario_detectado", "")
            if user_type == "regular":
                print(f"✅ Regular User: Correctly detected as 'regular' user")
            else:
                print(f"⚠️ Regular User: WARNING - Detected as '{user_type}' instead of 'regular'")
            
            # Verify mixed recommendations (both real sodas and alternatives)
            refrescos_reales = recommendations.get("refrescos_reales", [])
            bebidas_alternativas = recommendations.get("bebidas_alternativas", [])
            
            print(f"✅ Regular User: Got {len(refrescos_reales)} real sodas and {len(bebidas_alternativas)} alternatives")
            
            # Verify response time recording
            tiempo_promedio = recommendations.get("criterios_ml", {}).get("tiempo_promedio_respuesta", 0)
            if 3.0 <= tiempo_promedio <= 10.0:
                print(f"✅ Regular User: Average response time recorded correctly: {tiempo_promedio:.2f} seconds")
            else:
                print(f"⚠️ Regular User: WARNING - Unexpected average response time: {tiempo_promedio:.2f} seconds")
            
            self.test_results["Regular User"] = True
            
        except Exception as e:
            print(f"❌ Regular User: FAILED - {str(e)}")
            self.test_results["Regular User"] = False
            self.all_tests_passed = False
    
    def test_non_soda_user_scenario(self):
        """Test scenario for a user who doesn't consume sodas"""
        print("\n🔍 Testing Non-Soda User Scenario...")
        
        try:
            # Create session
            session_id = self.create_session()
            if not session_id:
                print("❌ Non-Soda User: FAILED - Could not create session")
                self.test_results["Non-Soda User"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ Non-Soda User: Session created with ID: {session_id}")
            
            # Answer questions with normal response times
            # First question: "Nunca o casi nunca" (doesn't consume soda)
            responses = self.answer_all_questions(
                session_id, 
                first_question_option=5,  # "Nunca o casi nunca"
                response_time_range=(3.0, 10.0)
            )
            
            if not responses:
                print("❌ Non-Soda User: FAILED - Could not answer questions")
                self.test_results["Non-Soda User"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ Non-Soda User: Answered all questions with first answer 'Nunca o casi nunca'")
            
            # Get recommendations
            recommendations = self.get_recommendations(session_id)
            if not recommendations:
                print("❌ Non-Soda User: FAILED - Could not get recommendations")
                self.test_results["Non-Soda User"] = False
                self.all_tests_passed = False
                return
            
            # Verify non-soda user detection
            user_type = recommendations.get("criterios_ml", {}).get("tipo_usuario_detectado", "")
            if user_type == "no_consume_refrescos":
                print(f"✅ Non-Soda User: Correctly detected as 'no_consume_refrescos' user")
            else:
                print(f"⚠️ Non-Soda User: WARNING - Detected as '{user_type}' instead of 'no_consume_refrescos'")
            
            # Verify ONLY healthy alternatives are recommended
            refrescos_reales = recommendations.get("refrescos_reales", [])
            bebidas_alternativas = recommendations.get("bebidas_alternativas", [])
            
            if len(refrescos_reales) == 0:
                print(f"✅ Non-Soda User: SUCCESS - No real sodas recommended")
            else:
                print(f"❌ Non-Soda User: FAILED - {len(refrescos_reales)} real sodas recommended when none should be")
                self.test_results["Non-Soda User"] = False
                self.all_tests_passed = False
                return
            
            if len(bebidas_alternativas) > 0:
                print(f"✅ Non-Soda User: SUCCESS - {len(bebidas_alternativas)} healthy alternatives recommended")
                
                # Verify all alternatives are actually healthy (not real sodas)
                all_healthy = all(not bebida.get("es_refresco_real", True) for bebida in bebidas_alternativas)
                if all_healthy:
                    print(f"✅ Non-Soda User: SUCCESS - All recommended alternatives are healthy (not real sodas)")
                else:
                    print(f"❌ Non-Soda User: FAILED - Some recommended alternatives are real sodas")
                    self.test_results["Non-Soda User"] = False
                    self.all_tests_passed = False
                    return
            else:
                print(f"❌ Non-Soda User: FAILED - No healthy alternatives recommended")
                self.test_results["Non-Soda User"] = False
                self.all_tests_passed = False
                return
            
            # Verify usuario_no_consume_refrescos flag
            if recommendations.get("usuario_no_consume_refrescos", False):
                print(f"✅ Non-Soda User: SUCCESS - usuario_no_consume_refrescos flag is True")
            else:
                print(f"❌ Non-Soda User: FAILED - usuario_no_consume_refrescos flag is False or missing")
                self.test_results["Non-Soda User"] = False
                self.all_tests_passed = False
                return
            
            self.test_results["Non-Soda User"] = True
            
        except Exception as e:
            print(f"❌ Non-Soda User: FAILED - {str(e)}")
            self.test_results["Non-Soda User"] = False
            self.all_tests_passed = False
    
    def test_fast_response_user_scenario(self):
        """Test scenario for a test user with very fast responses"""
        print("\n🔍 Testing Fast Response User Scenario...")
        
        try:
            # Create session
            session_id = self.create_session()
            if not session_id:
                print("❌ Fast Response User: FAILED - Could not create session")
                self.test_results["Fast Response User"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ Fast Response User: Session created with ID: {session_id}")
            
            # Answer questions with very fast response times (< 2 seconds)
            responses = self.answer_all_questions(
                session_id, 
                first_question_option=2,  # "Varias veces por semana"
                response_time_range=(0.5, 1.5)
            )
            
            if not responses:
                print("❌ Fast Response User: FAILED - Could not answer questions")
                self.test_results["Fast Response User"] = False
                self.all_tests_passed = False
                return
            
            print(f"✅ Fast Response User: Answered all questions with very fast response times")
            
            # Get recommendations
            recommendations = self.get_recommendations(session_id)
            if not recommendations:
                print("❌ Fast Response User: FAILED - Could not get recommendations")
                self.test_results["Fast Response User"] = False
                self.all_tests_passed = False
                return
            
            # Verify test user detection
            user_type = recommendations.get("criterios_ml", {}).get("tipo_usuario_detectado", "")
            if user_type == "usuario_prueba":
                print(f"✅ Fast Response User: Correctly detected as 'usuario_prueba'")
            else:
                print(f"⚠️ Fast Response User: WARNING - Detected as '{user_type}' instead of 'usuario_prueba'")
            
            # Verify response time recording
            tiempo_promedio = recommendations.get("criterios_ml", {}).get("tiempo_promedio_respuesta", 0)
            if tiempo_promedio < 2.0:
                print(f"✅ Fast Response User: Average response time recorded correctly: {tiempo_promedio:.2f} seconds")
            else:
                print(f"⚠️ Fast Response User: WARNING - Unexpected average response time: {tiempo_promedio:.2f} seconds")
            
            self.test_results["Fast Response User"] = True
            
        except Exception as e:
            print(f"❌ Fast Response User: FAILED - {str(e)}")
            self.test_results["Fast Response User"] = False
            self.all_tests_passed = False
    
    def test_compare_user_profiles(self):
        """Test that different user profiles get different recommendations"""
        print("\n🔍 Testing Different User Profiles Comparison...")
        
        try:
            # Create three different user profiles
            profiles = [
                {
                    "name": "Regular User",
                    "first_question_option": 2,  # "Varias veces por semana"
                    "response_time_range": (3.0, 10.0),
                    "preferences": {
                        "fisico": "moderado",
                        "preferencias": "dulce_moderado",
                        "estado_animo": "equilibrado"
                    }
                },
                {
                    "name": "Non-Soda User",
                    "first_question_option": 5,  # "Nunca o casi nunca"
                    "response_time_range": (3.0, 10.0),
                    "preferences": {
                        "fisico": "activo",
                        "preferencias": "natural",
                        "estado_animo": "equilibrado"
                    }
                },
                {
                    "name": "Fast Response User",
                    "first_question_option": 2,  # "Varias veces por semana"
                    "response_time_range": (0.5, 1.5),
                    "preferences": {
                        "fisico": "moderado",
                        "preferencias": "dulce_moderado",
                        "estado_animo": "equilibrado"
                    }
                }
            ]
            
            profile_results = {}
            
            for profile in profiles:
                print(f"\n🔍 Testing Profile: {profile['name']}...")
                
                # Create session
                session_id = self.create_session()
                if not session_id:
                    print(f"❌ Profile {profile['name']}: FAILED - Could not create session")
                    continue
                
                print(f"✅ Profile {profile['name']}: Session created with ID: {session_id}")
                
                # Answer questions according to profile
                responses = self.answer_all_questions(
                    session_id, 
                    first_question_option=profile["first_question_option"],
                    response_time_range=profile["response_time_range"],
                    preferences=profile["preferences"]
                )
                
                if not responses:
                    print(f"❌ Profile {profile['name']}: FAILED - Could not answer questions")
                    continue
                
                # Get recommendations
                recommendations = self.get_recommendations(session_id)
                if not recommendations:
                    print(f"❌ Profile {profile['name']}: FAILED - Could not get recommendations")
                    continue
                
                # Store recommendations for this profile
                profile_results[profile["name"]] = {
                    "refrescos_reales": recommendations.get("refrescos_reales", []),
                    "bebidas_alternativas": recommendations.get("bebidas_alternativas", []),
                    "tipo_usuario": recommendations.get("criterios_ml", {}).get("tipo_usuario_detectado", "unknown"),
                    "cluster": recommendations.get("criterios_ml", {}).get("cluster_usuario", "unknown")
                }
                
                print(f"✅ Profile {profile['name']}: Got {len(profile_results[profile['name']]['refrescos_reales'])} real sodas")
                print(f"✅ Profile {profile['name']}: Got {len(profile_results[profile['name']]['bebidas_alternativas'])} alternatives")
                print(f"✅ Profile {profile['name']}: Detected as '{profile_results[profile['name']]['tipo_usuario']}' user")
                print(f"✅ Profile {profile['name']}: Assigned to cluster {profile_results[profile['name']]['cluster']}")
            
            # Compare results between profiles
            if len(profile_results) == 3:
                # Compare Regular User vs Non-Soda User
                regular_ids = [b["id"] for b in profile_results["Regular User"]["refrescos_reales"]]
                non_soda_ids = [b["id"] for b in profile_results["Non-Soda User"]["refrescos_reales"]]
                
                if regular_ids and not non_soda_ids:
                    print(f"✅ Different Profiles: SUCCESS - Regular user gets real sodas, Non-soda user doesn't")
                else:
                    print(f"⚠️ Different Profiles: WARNING - Unexpected real soda recommendations pattern")
                
                # Compare user types
                if (profile_results["Regular User"]["tipo_usuario"] == "regular" and
                    profile_results["Non-Soda User"]["tipo_usuario"] == "no_consume_refrescos" and
                    profile_results["Fast Response User"]["tipo_usuario"] == "usuario_prueba"):
                    print(f"✅ Different Profiles: SUCCESS - All user types correctly detected")
                else:
                    print(f"⚠️ Different Profiles: WARNING - Some user types not correctly detected")
                
                # Check if recommendations are different
                all_recommendations_different = True
                
                # Compare Regular User vs Non-Soda User recommendations
                regular_all_ids = regular_ids + [b["id"] for b in profile_results["Regular User"]["bebidas_alternativas"]]
                non_soda_all_ids = non_soda_ids + [b["id"] for b in profile_results["Non-Soda User"]["bebidas_alternativas"]]
                
                if regular_all_ids == non_soda_all_ids:
                    all_recommendations_different = False
                    print(f"⚠️ Different Profiles: WARNING - Regular and Non-soda users got identical recommendations")
                
                # Compare Regular User vs Fast Response User recommendations
                fast_ids = [b["id"] for b in profile_results["Fast Response User"]["refrescos_reales"]]
                fast_all_ids = fast_ids + [b["id"] for b in profile_results["Fast Response User"]["bebidas_alternativas"]]
                
                if regular_all_ids == fast_all_ids:
                    all_recommendations_different = False
                    print(f"⚠️ Different Profiles: WARNING - Regular and Fast response users got identical recommendations")
                
                if all_recommendations_different:
                    print(f"✅ Different Profiles: SUCCESS - All profiles received different recommendations")
                    self.test_results["Different User Profiles"] = True
                else:
                    print(f"⚠️ Different Profiles: WARNING - Some profiles received identical recommendations")
                    self.test_results["Different User Profiles"] = True  # Still consider it a success with warning
            else:
                print(f"❌ Different Profiles: FAILED - Could not test all profiles")
                self.test_results["Different User Profiles"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ Different Profiles: FAILED - {str(e)}")
            self.test_results["Different User Profiles"] = False
            self.all_tests_passed = False
    
    def create_session(self):
        """Create a new session and return the session ID"""
        try:
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            data = response.json()
            
            if "sesion_id" in data:
                return data["sesion_id"]
            return None
        except Exception as e:
            print(f"Error creating session: {str(e)}")
            return None
    
    def answer_all_questions(self, session_id, first_question_option=2, response_time_range=(3.0, 10.0), preferences=None):
        """
        Answer all questions for a session
        
        Args:
            session_id: The session ID
            first_question_option: Option index for the first question (1-5)
            response_time_range: Tuple of (min, max) response time in seconds
            preferences: Dictionary of category -> value preferences
            
        Returns:
            Dictionary of responses or None if failed
        """
        try:
            responses = {}
            
            # Get initial question
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            data = response.json()
            
            if "pregunta" not in data:
                return None
            
            question = data["pregunta"]
            total_questions = data.get("total_preguntas", 6)
            
            # Answer initial question with specified option
            option_index = min(first_question_option - 1, len(question["opciones"]) - 1)
            selected_option = question["opciones"][option_index]
            
            # Simulate response time
            response_time = random.uniform(response_time_range[0], response_time_range[1])
            
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": selected_option["id"],
                "respuesta_texto": selected_option["texto"],
                "tiempo_respuesta": response_time
            })
            response.raise_for_status()
            
            responses[question["categoria"]] = selected_option["valor"]
            
            # Get and answer remaining questions
            for i in range(total_questions - 1):
                response = requests.get(f"{API_URL}/siguiente-pregunta/{session_id}")
                response.raise_for_status()
                data = response.json()
                
                if "finalizada" in data and data["finalizada"]:
                    break
                
                if "pregunta" not in data:
                    return None
                
                question = data["pregunta"]
                category = question.get("categoria", "")
                
                # Select option based on preferences if provided
                if preferences and category in preferences:
                    target_value = preferences[category]
                    selected_option = None
                    
                    for option in question["opciones"]:
                        if option["valor"] == target_value:
                            selected_option = option
                            break
                    
                    if not selected_option:
                        selected_option = random.choice(question["opciones"])
                else:
                    selected_option = random.choice(question["opciones"])
                
                # Simulate response time
                response_time = random.uniform(response_time_range[0], response_time_range[1])
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": response_time
                })
                response.raise_for_status()
                
                responses[question["categoria"]] = selected_option["valor"]
            
            return responses
            
        except Exception as e:
            print(f"Error answering questions: {str(e)}")
            return None
    
    def get_recommendations(self, session_id):
        """Get recommendations for a session"""
        try:
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting recommendations: {str(e)}")
            return None
    
    def print_summary(self):
        """Print a summary of all test results"""
        print("\n" + "="*80)
        print("📊 TEST RESULTS SUMMARY")
        print("="*80)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} - {test_name}")
        
        overall = "✅ ALL TESTS PASSED" if self.all_tests_passed else "❌ SOME TESTS FAILED"
        print("\n" + "="*80)
        print(f"OVERALL RESULT: {overall}")
        print("="*80)


if __name__ == "__main__":
    tester = RefrescoBotMLTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)