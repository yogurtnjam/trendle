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
    
    def test_1_create_video_project(self):
        """Test 1: Create Video Project - Tests Director workflow initialization"""
        print("=== Test 1: Create Video Project ===")
        
        try:
            # Test data - YC-style demo video request
            payload = {
                "user_goal": "I want to create a YC-style demo video for my AI language learning app",
                "product_type": "b2b saas",
                "target_platform": "YouTube"
            }
            
            # Make request
            response = requests.post(
                f"{BACKEND_URL}/director/project",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60  # Longer timeout for LLM processing
            )
            
            # Check status code
            if response.status_code != 200:
                self.log_test("Create Video Project", False, 
                            f"Expected status 200, got {response.status_code}. Response: {response.text}")
                return False
            
            # Parse response
            data = response.json()
            
            # Validate response structure
            required_fields = ["project_id", "message", "current_step"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                self.log_test("Create Video Project", False, 
                            f"Missing required fields: {missing_fields}. Response: {data}")
                return False
            
            # Validate project_id is UUID format
            try:
                uuid.UUID(data["project_id"])
            except ValueError:
                self.log_test("Create Video Project", False, 
                            f"project_id is not a valid UUID: {data['project_id']}")
                return False
            
            # Validate agent message exists and mentions format matching
            agent_message = data["message"]
            if not agent_message or len(agent_message.strip()) < 10:
                self.log_test("Create Video Project", False, 
                            f"Agent response too short or empty: '{agent_message}'")
                return False
            
            # Check for format matching keywords
            message_lower = agent_message.lower()
            format_keywords = ["format", "yc", "demo", "classic", "viral"]
            if not any(keyword in message_lower for keyword in format_keywords):
                self.log_test("Create Video Project", False, 
                            f"Agent response doesn't mention format matching: '{agent_message}'")
                return False
            
            # Validate matched_format is present (should be YC Demo Classic)
            if "matched_format" not in data or not data["matched_format"]:
                self.log_test("Create Video Project", False, 
                            f"matched_format should be present after format matching")
                return False
            
            matched_format = data["matched_format"]
            if matched_format.get("format_id") != "yc_demo_classic":
                self.log_test("Create Video Project", False, 
                            f"Expected YC Demo Classic format, got: {matched_format.get('format_id')}")
                return False
            
            # Validate current_step progression
            if data["current_step"] not in ["format_matched", "script_planned"]:
                self.log_test("Create Video Project", False, 
                            f"Expected current_step to be format_matched or script_planned, got: {data['current_step']}")
                return False
            
            # Store project_id for subsequent tests
            self.project_id = data["project_id"]
            
            self.log_test("Create Video Project", True, 
                        f"Project created successfully. ID: {self.project_id}, Format: {matched_format['name']}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("Create Video Project", False, f"Request failed: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Create Video Project", False, f"Unexpected error: {str(e)}")
            return False
    
    def test_2_send_followup_message(self):
        """Test 2: Send Follow-up Message - Tests Director workflow progression"""
        print("=== Test 2: Send Follow-up Message ===")
        
        if not self.project_id:
            self.log_test("Send Follow-up Message", False, "No project_id available from previous test")
            return False
        
        try:
            # Test data - user confirms format choice
            payload = {
                "project_id": self.project_id,
                "message": "Yes, let's proceed with that format"
            }
            
            # Make request
            response = requests.post(
                f"{BACKEND_URL}/director/message",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60  # Longer timeout for LLM processing
            )
            
            # Check status code
            if response.status_code != 200:
                self.log_test("Send Follow-up Message", False, 
                            f"Expected status 200, got {response.status_code}. Response: {response.text}")
                return False
            
            # Parse response
            data = response.json()
            
            # Validate response structure
            required_fields = ["project_id", "message", "current_step"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                self.log_test("Send Follow-up Message", False, 
                            f"Missing required fields: {missing_fields}. Response: {data}")
                return False
            
            # Validate project_id matches
            if data["project_id"] != self.project_id:
                self.log_test("Send Follow-up Message", False, 
                            f"Project ID mismatch. Expected: {self.project_id}, Got: {data['project_id']}")
                return False
            
            # Validate shot_list is generated
            if "shot_list" not in data or not data["shot_list"]:
                self.log_test("Send Follow-up Message", False, 
                            f"shot_list should be generated after format confirmation")
                return False
            
            shot_list = data["shot_list"]
            if not isinstance(shot_list, list) or len(shot_list) < 3:
                self.log_test("Send Follow-up Message", False, 
                            f"shot_list should be a list with at least 3 segments, got: {len(shot_list) if isinstance(shot_list, list) else 'not a list'}")
                return False
            
            # Validate shot_list structure
            for i, shot in enumerate(shot_list):
                required_shot_fields = ["segment_name", "duration", "script", "visual_guide"]
                missing_shot_fields = [field for field in required_shot_fields if field not in shot]
                if missing_shot_fields:
                    self.log_test("Send Follow-up Message", False, 
                                f"Shot {i+1} missing fields: {missing_shot_fields}")
                    return False
            
            # Validate current_step advancement
            if data["current_step"] not in ["script_planned", "recording_guide"]:
                self.log_test("Send Follow-up Message", False, 
                            f"Expected current_step to advance to script_planned or recording_guide, got: {data['current_step']}")
                return False
            
            # Validate message describes shot list
            agent_message = data["message"]
            message_lower = agent_message.lower()
            shot_keywords = ["shot", "segment", "script", "record", "film"]
            if not any(keyword in message_lower for keyword in shot_keywords):
                self.log_test("Send Follow-up Message", False, 
                            f"Agent message should describe shot list: '{agent_message}'")
                return False
            
            self.log_test("Send Follow-up Message", True, 
                        f"Shot list generated with {len(shot_list)} segments. Current step: {data['current_step']}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("Send Follow-up Message", False, f"Request failed: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Send Follow-up Message", False, f"Unexpected error: {str(e)}")
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