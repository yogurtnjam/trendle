#!/usr/bin/env python3
"""
Backend Test Suite for Director System with LangGraph Workflow
Tests the Director endpoints, viral format matching, and LangGraph workflow execution
"""

import requests
import json
import uuid
from datetime import datetime
import sys
import time

# Backend URL from frontend/.env
BACKEND_URL = "https://trend-workspace.preview.emergentagent.com/api"

class DirectorSystemTester:
    def __init__(self):
        self.project_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if not success or details:
            print(f"   Details: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        print()
    
    def test_1_create_chat_session(self):
        """Test 1: Create Chat Session"""
        print("=== Test 1: Create Chat Session ===")
        
        try:
            # Test data
            payload = {"user_id": "sarah_entrepreneur_123"}
            
            # Make request
            response = requests.post(
                f"{BACKEND_URL}/chat/session",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            # Check status code
            if response.status_code != 200:
                self.log_test("Create Chat Session", False, 
                            f"Expected status 200, got {response.status_code}. Response: {response.text}")
                return False
            
            # Parse response
            data = response.json()
            
            # Validate response structure
            if "session_id" not in data or "created_at" not in data:
                self.log_test("Create Chat Session", False, 
                            f"Missing required fields. Response: {data}")
                return False
            
            # Validate session_id is UUID format
            try:
                uuid.UUID(data["session_id"])
            except ValueError:
                self.log_test("Create Chat Session", False, 
                            f"session_id is not a valid UUID: {data['session_id']}")
                return False
            
            # Validate created_at is ISO timestamp
            try:
                datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
            except ValueError:
                self.log_test("Create Chat Session", False, 
                            f"created_at is not a valid ISO timestamp: {data['created_at']}")
                return False
            
            # Store session_id for subsequent tests
            self.session_id = data["session_id"]
            
            self.log_test("Create Chat Session", True, 
                        f"Session created successfully. ID: {self.session_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("Create Chat Session", False, f"Request failed: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Create Chat Session", False, f"Unexpected error: {str(e)}")
            return False
    
    def test_2_send_first_message(self):
        """Test 2: Send First Message to ProfileAgent"""
        print("=== Test 2: Send First Message to ProfileAgent ===")
        
        if not self.session_id:
            self.log_test("Send First Message", False, "No session_id available from previous test")
            return False
        
        try:
            # Test data - realistic message about language learning app
            payload = {
                "session_id": self.session_id,
                "message": "I'm building a language learning app for working professionals",
                "conversation_history": []
            }
            
            # Make request
            response = requests.post(
                f"{BACKEND_URL}/chat/message",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60  # Longer timeout for LLM processing
            )
            
            # Check status code
            if response.status_code != 200:
                self.log_test("Send First Message", False, 
                            f"Expected status 200, got {response.status_code}. Response: {response.text}")
                return False
            
            # Parse response
            data = response.json()
            
            # Validate response structure
            required_fields = ["session_id", "message", "confidence_scores"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                self.log_test("Send First Message", False, 
                            f"Missing required fields: {missing_fields}. Response: {data}")
                return False
            
            # Validate session_id matches
            if data["session_id"] != self.session_id:
                self.log_test("Send First Message", False, 
                            f"Session ID mismatch. Expected: {self.session_id}, Got: {data['session_id']}")
                return False
            
            # Validate agent response exists and is meaningful
            agent_message = data["message"]
            if not agent_message or len(agent_message.strip()) < 10:
                self.log_test("Send First Message", False, 
                            f"Agent response too short or empty: '{agent_message}'")
                return False
            
            # Validate confidence_scores structure
            confidence_scores = data["confidence_scores"]
            expected_fields = ["target_customer", "product", "audience", "platform", "vibes", "overall"]
            missing_confidence_fields = [field for field in expected_fields if field not in confidence_scores]
            if missing_confidence_fields:
                self.log_test("Send First Message", False, 
                            f"Missing confidence score fields: {missing_confidence_fields}")
                return False
            
            # Check that agent asks strategic questions (should mention platform and vibes)
            agent_lower = agent_message.lower()
            strategic_keywords = ["platform", "vibe", "style", "tone", "tiktok", "instagram", "professional", "casual"]
            if not any(keyword in agent_lower for keyword in strategic_keywords):
                self.log_test("Send First Message", False, 
                            f"Agent response doesn't seem to ask strategic follow-up questions about platform/vibes: '{agent_message}'")
                return False
            
            # Store conversation history for next test
            self.conversation_history = [
                {"role": "user", "content": payload["message"]},
                {"role": "assistant", "content": agent_message}
            ]
            
            self.log_test("Send First Message", True, 
                        f"Agent responded appropriately. Confidence scores: {confidence_scores}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("Send First Message", False, f"Request failed: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Send First Message", False, f"Unexpected error: {str(e)}")
            return False
    
    def test_3_send_followup_message(self):
        """Test 3: Send Follow-up Message"""
        print("=== Test 3: Send Follow-up Message ===")
        
        if not self.session_id or not self.conversation_history:
            self.log_test("Send Follow-up Message", False, "No session_id or conversation_history available")
            return False
        
        try:
            # Test data - follow-up message with platform and vibes info
            payload = {
                "session_id": self.session_id,
                "message": "I'm targeting TikTok and Instagram with a professional but approachable vibe",
                "conversation_history": self.conversation_history
            }
            
            # Make request
            response = requests.post(
                f"{BACKEND_URL}/chat/message",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            # Check status code
            if response.status_code != 200:
                self.log_test("Send Follow-up Message", False, 
                            f"Expected status 200, got {response.status_code}. Response: {response.text}")
                return False
            
            # Parse response
            data = response.json()
            
            # Validate response structure
            if "confidence_scores" not in data:
                self.log_test("Send Follow-up Message", False, 
                            f"Missing confidence_scores in response: {data}")
                return False
            
            # Check that confidence scores have increased for platform and vibes
            confidence_scores = data["confidence_scores"]
            platform_confidence = confidence_scores.get("platform", 0)
            vibes_confidence = confidence_scores.get("vibes", 0)
            
            if platform_confidence < 30:  # Should have some confidence after mentioning TikTok/Instagram
                self.log_test("Send Follow-up Message", False, 
                            f"Platform confidence too low after mentioning platforms: {platform_confidence}")
                return False
            
            if vibes_confidence < 30:  # Should have some confidence after mentioning professional/approachable
                self.log_test("Send Follow-up Message", False, 
                            f"Vibes confidence too low after mentioning vibes: {vibes_confidence}")
                return False
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": payload["message"]})
            self.conversation_history.append({"role": "assistant", "content": data["message"]})
            
            self.log_test("Send Follow-up Message", True, 
                        f"Confidence scores updated appropriately. Platform: {platform_confidence}, Vibes: {vibes_confidence}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("Send Follow-up Message", False, f"Request failed: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Send Follow-up Message", False, f"Unexpected error: {str(e)}")
            return False
    
    def test_4_retrieve_session_data(self):
        """Test 4: Retrieve Session Data"""
        print("=== Test 4: Retrieve Session Data ===")
        
        if not self.session_id:
            self.log_test("Retrieve Session Data", False, "No session_id available")
            return False
        
        try:
            # Make request
            response = requests.get(
                f"{BACKEND_URL}/chat/session/{self.session_id}",
                timeout=30
            )
            
            # Check status code
            if response.status_code != 200:
                self.log_test("Retrieve Session Data", False, 
                            f"Expected status 200, got {response.status_code}. Response: {response.text}")
                return False
            
            # Parse response
            data = response.json()
            
            # Validate session data structure
            required_fields = ["session_id", "profile_data", "confidence_scores", "conversation_history"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                self.log_test("Retrieve Session Data", False, 
                            f"Missing required fields: {missing_fields}")
                return False
            
            # Validate session_id matches
            if data["session_id"] != self.session_id:
                self.log_test("Retrieve Session Data", False, 
                            f"Session ID mismatch. Expected: {self.session_id}, Got: {data['session_id']}")
                return False
            
            # Check that conversation history is populated
            conversation_history = data["conversation_history"]
            if not conversation_history or len(conversation_history) < 2:
                self.log_test("Retrieve Session Data", False, 
                            f"Conversation history should have at least 2 messages, got: {len(conversation_history)}")
                return False
            
            # Check that profile_data has some information
            profile_data = data["profile_data"]
            if not profile_data:
                self.log_test("Retrieve Session Data", False, 
                            "Profile data should contain some extracted information")
                return False
            
            self.log_test("Retrieve Session Data", True, 
                        f"Session data retrieved successfully. Profile fields: {list(profile_data.keys())}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("Retrieve Session Data", False, f"Request failed: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Retrieve Session Data", False, f"Unexpected error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting ProfileAgent Chat API Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Run tests in order
        tests = [
            self.test_1_create_chat_session,
            self.test_2_send_first_message,
            self.test_3_send_followup_message,
            self.test_4_retrieve_session_data
        ]
        
        for test_func in tests:
            success = test_func()
            if not success:
                print("❌ Test failed, stopping execution")
                break
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
        
        print(f"\nResults: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! ProfileAgent Chat API is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Check the details above.")
            return False

def main():
    """Main test execution"""
    tester = ProfileAgentTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()