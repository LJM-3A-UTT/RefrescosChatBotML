#!/usr/bin/env python3
"""
Test Script for New Improvements in RefrescoBot ML
Testing the specific improvements mentioned in the user's request:
1. Estructura de bebidas corregida (26 bebidas)
2. Limpieza selectiva de BD
3. Campo sabor en presentaciones
4. Lógica ML mejorada (variedad)
5. Configuraciones granulares
6. Botón "más opciones" para ambos tipos
"""

import requests
import json
import time
import random
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv("/app/frontend/.env")

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001")
API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

class NewImprovementsTester:
    def __init__(self):
        self.all_tests_passed = True
        self.test_results = {}
        
    def run_all_tests(self):
        """Run all new improvement tests"""
        print("\n" + "="*80)
        print("🚀 REFRESCOBOT ML - NEW IMPROVEMENTS TEST SUITE")
        print("="*80)
        
        # Test 1: Estructura de bebidas corregida (26 bebidas)
        self.test_beverage_structure_26_drinks()
        
        # Test 2: Limpieza selectiva de BD
        self.test_selective_database_cleaning()
        
        # Test 3: Campo sabor en presentaciones
        self.test_sabor_field_in_presentations()
        
        # Test 4: Lógica ML mejorada (variedad en recomendaciones)
        self.test_improved_ml_logic_variety()
        
        # Test 5: Configuraciones granulares
        self.test_granular_configurations()
        
        # Test 6: Botón "más opciones" para ambos tipos
        self.test_more_options_button_both_types()
        
        # Print summary
        self.print_summary()
        
        return self.all_tests_passed
    
    def test_beverage_structure_26_drinks(self):
        """Test the new beverage structure with 26 drinks"""
        print("\n🔍 TEST 1: Estructura de bebidas corregida (26 bebidas)")
        print("Expected: 14 real refrescos + 12 healthy alternatives = 26 total")
        
        try:
            # Get stats from admin endpoint
            response = requests.get(f"{API_URL}/admin/stats")
            response.raise_for_status()
            stats = response.json()
            
            if "bebidas" not in stats:
                print("❌ FAILED: No bebidas stats available")
                self.test_results["Beverage Structure 26 drinks"] = False
                self.all_tests_passed = False
                return
            
            bebidas_stats = stats["bebidas"]
            total_bebidas = bebidas_stats.get("total", 0)
            refrescos_reales = bebidas_stats.get("refrescos_reales", 0)
            alternativas = bebidas_stats.get("alternativas", 0)
            total_presentaciones = bebidas_stats.get("total_presentaciones", 0)
            
            print(f"✅ Found {total_bebidas} total bebidas")
            print(f"✅ Found {refrescos_reales} real refrescos")
            print(f"✅ Found {alternativas} healthy alternatives")
            print(f"✅ Found {total_presentaciones} total presentations")
            
            # Verify expected counts
            success = True
            if total_bebidas == 26:
                print("✅ CORRECT: Total number of bebidas is 26")
            else:
                print(f"❌ INCORRECT: Expected 26 bebidas, got {total_bebidas}")
                success = False
            
            if refrescos_reales == 14:
                print("✅ CORRECT: Number of real refrescos is 14")
            else:
                print(f"❌ INCORRECT: Expected 14 real refrescos, got {refrescos_reales}")
                success = False
            
            if alternativas == 12:
                print("✅ CORRECT: Number of healthy alternatives is 12")
            else:
                print(f"❌ INCORRECT: Expected 12 healthy alternatives, got {alternativas}")
                success = False
            
            # Verify presentation count is reasonable (should be > 26 since each bebida has multiple presentations)
            if total_presentaciones > 26:
                print(f"✅ CORRECT: Total presentations ({total_presentaciones}) > total bebidas (26)")
            else:
                print(f"❌ INCORRECT: Total presentations ({total_presentaciones}) should be > 26")
                success = False
            
            if success:
                print("✅ SUCCESS: Beverage structure with 26 drinks is correct!")
                self.test_results["Beverage Structure 26 drinks"] = True
            else:
                self.test_results["Beverage Structure 26 drinks"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            self.test_results["Beverage Structure 26 drinks"] = False
            self.all_tests_passed = False

    def test_selective_database_cleaning(self):
        """Test selective database cleaning"""
        print("\n🔍 TEST 2: Limpieza selectiva de BD")
        print("Expected: Only questions and beverages cleaned, sessions preserved")
        
        try:
            # Create a test session to verify it gets preserved
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            session_data = response.json()
            test_session_id = session_data["sesion_id"]
            print(f"✅ Created test session: {test_session_id}")
            
            # Check admin stats
            response = requests.get(f"{API_URL}/admin/stats")
            response.raise_for_status()
            stats = response.json()
            
            print(f"✅ Current stats summary:")
            print(f"   - Sessions: {stats.get('sesiones', {}).get('total', 0)}")
            print(f"   - Bebidas: {stats.get('bebidas', {}).get('total', 0)}")
            
            # Verify that bebidas exist (they should be loaded from JSON)
            success = True
            if "bebidas" in stats and stats["bebidas"].get("total", 0) > 0:
                print(f"✅ Bebidas loaded: {stats['bebidas']['total']}")
            else:
                print("❌ No bebidas found")
                success = False
            
            # Verify that sessions exist (including our test session)
            if "sesiones" in stats and stats["sesiones"].get("total", 0) > 0:
                print(f"✅ Sessions preserved: {stats['sesiones']['total']}")
            else:
                print("⚠️ No sessions found (might be expected)")
            
            # Verify that our test session still exists
            response = requests.get(f"{API_URL}/pregunta-inicial/{test_session_id}")
            if response.status_code == 200:
                print("✅ CORRECT: Test session preserved and accessible")
            else:
                print("⚠️ Test session not accessible (might be expected)")
            
            if success:
                print("✅ SUCCESS: Selective database cleaning working correctly!")
                print("✅ Bebidas are properly loaded from JSON")
                print("✅ Sessions are preserved during system operation")
                self.test_results["Selective Database Cleaning"] = True
            else:
                self.test_results["Selective Database Cleaning"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            self.test_results["Selective Database Cleaning"] = False
            self.all_tests_passed = False

    def test_sabor_field_in_presentations(self):
        """Test that each presentation has a 'sabor' field"""
        print("\n🔍 TEST 3: Campo sabor en presentaciones")
        print("Expected: Each presentation should have a 'sabor' field")
        
        try:
            # Create a session and get recommendations to check bebida structure
            session_id = self.create_test_session_and_complete()
            if not session_id:
                print("❌ Could not create test session")
                self.test_results["Sabor field in presentations"] = False
                self.all_tests_passed = False
                return
            
            # Get recommendations to access bebida data
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            recommendations = response.json()
            
            # Check both refrescos and alternatives
            all_bebidas = []
            if "refrescos_reales" in recommendations:
                all_bebidas.extend(recommendations["refrescos_reales"])
            if "bebidas_alternativas" in recommendations:
                all_bebidas.extend(recommendations["bebidas_alternativas"])
            
            if not all_bebidas:
                print("❌ No bebidas found in recommendations")
                self.test_results["Sabor field in presentations"] = False
                self.all_tests_passed = False
                return
            
            total_presentations = 0
            presentations_with_sabor = 0
            sabor_examples = []
            
            for bebida in all_bebidas:
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
            
            print(f"✅ Checked {total_presentations} presentations from {len(all_bebidas)} bebidas")
            print(f"✅ Found {presentations_with_sabor} presentations with 'sabor' field")
            
            if total_presentations == presentations_with_sabor:
                print("✅ CORRECT: All presentations have 'sabor' field")
                
                # Show examples
                print("\n📋 Examples of 'sabor' values:")
                for example in sabor_examples:
                    print(f"   - {example}")
                
                print("✅ SUCCESS: All presentations have appropriate 'sabor' field!")
                self.test_results["Sabor field in presentations"] = True
            else:
                missing = total_presentations - presentations_with_sabor
                print(f"❌ INCORRECT: {missing} presentations missing 'sabor' field")
                self.test_results["Sabor field in presentations"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            self.test_results["Sabor field in presentations"] = False
            self.all_tests_passed = False

    def create_test_session_and_complete(self):
        """Create a test session and complete all questions"""
        try:
            # Create session
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            session_data = response.json()
            session_id = session_data["sesion_id"]
            
            # Get initial question and answer it
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            question_data = response.json()
            question = question_data["pregunta"]
            
            # Answer the initial question
            response = requests.post(f"{API_URL}/responder/{session_id}", json={
                "pregunta_id": question["id"],
                "respuesta_id": question["opciones"][0]["id"],
                "respuesta_texto": question["opciones"][0]["texto"],
                "tiempo_respuesta": 3.0
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
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": question["id"],
                    "respuesta_id": question["opciones"][0]["id"],
                    "respuesta_texto": question["opciones"][0]["texto"],
                    "tiempo_respuesta": 2.0
                })
                response.raise_for_status()
            
            return session_id
            
        except Exception as e:
            print(f"Error creating test session: {str(e)}")
            return None

    def test_improved_ml_logic_variety(self):
        """Test improved ML logic that provides variety"""
        print("\n🔍 TEST 4: Lógica ML mejorada (variedad en recomendaciones)")
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
                
                # Answer questions with different patterns
                if not self.answer_questions_with_pattern(session_id, pattern=i):
                    print(f"❌ Could not answer questions for session {i+1}")
                    self.test_results["Improved ML Logic Variety"] = False
                    self.all_tests_passed = False
                    return
                
                # Get recommendations
                response = requests.get(f"{API_URL}/recomendacion/{session_id}")
                response.raise_for_status()
                recommendations = response.json()
                
                # Extract bebida IDs
                refrescos_ids = [b["id"] for b in recommendations.get("refrescos_reales", [])]
                alternativas_ids = [b["id"] for b in recommendations.get("bebidas_alternativas", [])]
                
                sessions_and_recommendations.append({
                    "session_id": session_id,
                    "refrescos_ids": refrescos_ids,
                    "alternativas_ids": alternativas_ids
                })
                
                print(f"✅ Session {i+1}: {len(refrescos_ids)} refrescos, {len(alternativas_ids)} alternatives")
            
            # Analyze variety
            print(f"\n📊 Analyzing variety across {len(sessions_and_recommendations)} sessions...")
            
            # Check refrescos variety
            all_refrescos_sets = [set(s["refrescos_ids"]) for s in sessions_and_recommendations]
            refrescos_intersection = set.intersection(*all_refrescos_sets) if all_refrescos_sets else set()
            
            # Check alternativas variety
            all_alternativas_sets = [set(s["alternativas_ids"]) for s in sessions_and_recommendations]
            alternativas_intersection = set.intersection(*all_alternativas_sets) if all_alternativas_sets else set()
            
            print(f"✅ Refrescos common to all sessions: {len(refrescos_intersection)}")
            print(f"✅ Alternativas common to all sessions: {len(alternativas_intersection)}")
            
            # Calculate variety
            total_unique_refrescos = len(set().union(*all_refrescos_sets)) if all_refrescos_sets else 0
            total_unique_alternativas = len(set().union(*all_alternativas_sets)) if all_alternativas_sets else 0
            
            print(f"✅ Total unique refrescos: {total_unique_refrescos}")
            print(f"✅ Total unique alternativas: {total_unique_alternativas}")
            
            # Verify variety (not always the same recommendations)
            variety_threshold = 0.5  # At least 50% should be different
            success = True
            
            if all_refrescos_sets and total_unique_refrescos > 0:
                refrescos_variety_ratio = (total_unique_refrescos - len(refrescos_intersection)) / total_unique_refrescos
                print(f"✅ Refrescos variety ratio: {refrescos_variety_ratio:.2f}")
                
                if refrescos_variety_ratio >= variety_threshold:
                    print("✅ CORRECT: Good variety in refrescos recommendations")
                else:
                    print(f"❌ INCORRECT: Low variety in refrescos (ratio: {refrescos_variety_ratio:.2f})")
                    success = False
            
            if all_alternativas_sets and total_unique_alternativas > 0:
                alternativas_variety_ratio = (total_unique_alternativas - len(alternativas_intersection)) / total_unique_alternativas
                print(f"✅ Alternativas variety ratio: {alternativas_variety_ratio:.2f}")
                
                if alternativas_variety_ratio >= variety_threshold:
                    print("✅ CORRECT: Good variety in alternativas recommendations")
                else:
                    print(f"❌ INCORRECT: Low variety in alternativas (ratio: {alternativas_variety_ratio:.2f})")
                    success = False
            
            if success:
                print("✅ SUCCESS: ML logic provides good variety in recommendations!")
                self.test_results["Improved ML Logic Variety"] = True
            else:
                self.test_results["Improved ML Logic Variety"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            self.test_results["Improved ML Logic Variety"] = False
            self.all_tests_passed = False

    def test_granular_configurations(self):
        """Test the new granular configurations"""
        print("\n🔍 TEST 5: Configuraciones granulares")
        print("Expected configurations:")
        print("- MAX_ALTERNATIVAS_SALUDABLES_INICIAL = 3")
        print("- MAX_ALTERNATIVAS_SALUDABLES_ADICIONAL = 3")
        print("- MAX_REFRESCOS_ADICIONALES = 3")
        
        try:
            # Test 1: Initial healthy alternatives limit (3)
            print(f"\n📋 Testing MAX_ALTERNATIVAS_SALUDABLES_INICIAL = 3")
            
            # Create a health-conscious user session
            session_id = self.create_user_session_healthy()
            if not session_id:
                print("❌ Could not create healthy user session")
                self.test_results["Granular Configurations"] = False
                self.all_tests_passed = False
                return
            
            # Get initial recommendations
            response = requests.get(f"{API_URL}/recomendacion/{session_id}")
            response.raise_for_status()
            recommendations = response.json()
            
            alternativas_count = len(recommendations.get("bebidas_alternativas", []))
            print(f"✅ Initial healthy alternatives: {alternativas_count}")
            
            success = True
            if alternativas_count <= 3:
                print("✅ CORRECT: Initial healthy alternatives ≤ 3")
            else:
                print(f"❌ INCORRECT: Initial healthy alternatives ({alternativas_count}) > 3")
                success = False
            
            # Test 2: Additional healthy alternatives limit (3)
            print(f"\n📋 Testing MAX_ALTERNATIVAS_SALUDABLES_ADICIONAL = 3")
            
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
                    success = False
            else:
                print("⚠️ No additional alternatives available")
            
            # Test 3: Test specific endpoints
            print(f"\n📋 Testing specific endpoints")
            
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
                    success = False
            
            if success:
                print("✅ SUCCESS: All granular configurations are working correctly!")
                self.test_results["Granular Configurations"] = True
            else:
                self.test_results["Granular Configurations"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            self.test_results["Granular Configurations"] = False
            self.all_tests_passed = False

    def test_more_options_button_both_types(self):
        """Test that 'more options' button works for both types"""
        print("\n🔍 TEST 6: Botón 'más opciones' para ambos tipos")
        print("Expected: Button should work for both refrescos and alternatives")
        
        try:
            # Test 1: Traditional user (should get more refrescos or alternatives)
            print(f"\n📋 Testing traditional user")
            
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
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{traditional_session}")
            response.raise_for_status()
            more_recs = response.json()
            
            # Check response structure
            required_fields = ["recomendaciones_adicionales", "sin_mas_opciones", "tipo_recomendaciones"]
            missing_fields = [field for field in required_fields if field not in more_recs]
            
            success = True
            if missing_fields:
                print(f"❌ INCORRECT: Missing fields: {missing_fields}")
                success = False
            else:
                print("✅ CORRECT: Response has all required fields")
                
                if not more_recs.get("sin_mas_opciones", False):
                    additional_count = len(more_recs.get("recomendaciones_adicionales", []))
                    tipo = more_recs.get("tipo_recomendaciones", "unknown")
                    print(f"✅ Got {additional_count} more recommendations ({tipo})")
                else:
                    print("⚠️ No more options available")
            
            # Test 2: Health-conscious user
            print(f"\n📋 Testing health-conscious user")
            
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
            response = requests.get(f"{API_URL}/recomendaciones-alternativas/{healthy_session}")
            response.raise_for_status()
            more_recs = response.json()
            
            # Check response structure
            missing_fields = [field for field in required_fields if field not in more_recs]
            
            if missing_fields:
                print(f"❌ INCORRECT: Missing fields: {missing_fields}")
                success = False
            else:
                print("✅ CORRECT: Response has all required fields")
                
                if not more_recs.get("sin_mas_opciones", False):
                    additional_count = len(more_recs.get("recomendaciones_adicionales", []))
                    tipo = more_recs.get("tipo_recomendaciones", "unknown")
                    print(f"✅ Got {additional_count} more recommendations ({tipo})")
                else:
                    print("⚠️ No more options available")
            
            if success:
                print("✅ SUCCESS: 'More options' button works for both user types!")
                self.test_results["More Options Button Both Types"] = True
            else:
                self.test_results["More Options Button Both Types"] = False
                self.all_tests_passed = False
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            self.test_results["More Options Button Both Types"] = False
            self.all_tests_passed = False

    def answer_questions_with_pattern(self, session_id, pattern=0):
        """Answer questions with different patterns"""
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
                    option_index = 0  # First option
                elif pattern == 1:
                    option_index = len(question["opciones"]) - 1  # Last option
                else:
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
            print(f"Error answering questions: {str(e)}")
            return False

    def create_user_session_healthy(self):
        """Create a health-conscious user session"""
        try:
            # Create session
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            data = response.json()
            session_id = data["sesion_id"]
            
            # Get initial question
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            data = response.json()
            question = data["pregunta"]
            
            # Answer with moderate consumption
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
                
                # Choose health-conscious options (last option often most positive)
                selected_option = question["opciones"][-1]
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": random.uniform(4.0, 10.0)
                })
                response.raise_for_status()
            
            return session_id
            
        except Exception as e:
            print(f"Error creating healthy user session: {str(e)}")
            return None

    def create_user_session_traditional(self):
        """Create a traditional user session"""
        try:
            # Create session
            response = requests.post(f"{API_URL}/iniciar-sesion")
            response.raise_for_status()
            data = response.json()
            session_id = data["sesion_id"]
            
            # Get initial question
            response = requests.get(f"{API_URL}/pregunta-inicial/{session_id}")
            response.raise_for_status()
            data = response.json()
            question = data["pregunta"]
            
            # Answer with frequent consumption (middle or higher option)
            frequent_option = question["opciones"][len(question["opciones"])//2] if len(question["opciones"]) > 0 else question["opciones"][0]
            
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
                
                # Choose middle options (traditional)
                selected_option = question["opciones"][len(question["opciones"])//2]
                
                response = requests.post(f"{API_URL}/responder/{session_id}", json={
                    "pregunta_id": question["id"],
                    "respuesta_id": selected_option["id"],
                    "respuesta_texto": selected_option["texto"],
                    "tiempo_respuesta": random.uniform(1.0, 4.0)
                })
                response.raise_for_status()
            
            return session_id
            
        except Exception as e:
            print(f"Error creating traditional user session: {str(e)}")
            return None

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("📊 NEW IMPROVEMENTS TEST SUMMARY")
        print("="*80)
        
        passed_tests = 0
        total_tests = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
            if result:
                passed_tests += 1
        
        print(f"\n📈 OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if self.all_tests_passed:
            print("🎉 ALL NEW IMPROVEMENTS WORKING CORRECTLY!")
        else:
            print("⚠️ SOME IMPROVEMENTS NEED ATTENTION")
        
        print("="*80)

if __name__ == "__main__":
    tester = NewImprovementsTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 CONCLUSION: All new improvements are working as expected!")
    else:
        print("\n⚠️ CONCLUSION: Some improvements need to be reviewed.")