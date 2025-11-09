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
    
    def test_3_get_project_details(self):
        """Test 3: Get Project Details - Tests project state persistence"""
        print("=== Test 3: Get Project Details ===")
        
        if not self.project_id:
            self.log_test("Get Project Details", False, "No project_id available from previous test")
            return False
        
        try:
            # Make request
            response = requests.get(
                f"{BACKEND_URL}/director/project/{self.project_id}",
                timeout=30
            )
            
            # Check status code
            if response.status_code != 200:
                self.log_test("Get Project Details", False, 
                            f"Expected status 200, got {response.status_code}. Response: {response.text}")
                return False
            
            # Parse response
            data = response.json()
            
            # Validate project data structure
            required_fields = ["project_id", "user_goal", "matched_format", "shot_list", "current_step", "uploaded_segments"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                self.log_test("Get Project Details", False, 
                            f"Missing required fields: {missing_fields}")
                return False
            
            # Validate project_id matches
            if data["project_id"] != self.project_id:
                self.log_test("Get Project Details", False, 
                            f"Project ID mismatch. Expected: {self.project_id}, Got: {data['project_id']}")
                return False
            
            # Validate user_goal is preserved
            if "AI language learning app" not in data["user_goal"]:
                self.log_test("Get Project Details", False, 
                            f"User goal not preserved correctly: {data['user_goal']}")
                return False
            
            # Validate matched_format is present and correct
            matched_format = data["matched_format"]
            if not matched_format or matched_format.get("format_id") != "yc_demo_classic":
                self.log_test("Get Project Details", False, 
                            f"Matched format not preserved correctly: {matched_format}")
                return False
            
            # Validate shot_list is present and structured
            shot_list = data["shot_list"]
            if not shot_list or len(shot_list) < 3:
                self.log_test("Get Project Details", False, 
                            f"Shot list not preserved correctly: {len(shot_list) if shot_list else 0} segments")
                return False
            
            # Validate uploaded_segments is empty array (no uploads yet)
            uploaded_segments = data["uploaded_segments"]
            if not isinstance(uploaded_segments, list):
                self.log_test("Get Project Details", False, 
                            f"uploaded_segments should be a list, got: {type(uploaded_segments)}")
                return False
            
            # Validate current_step is appropriate
            current_step = data["current_step"]
            valid_steps = ["initial", "format_matched", "script_planned", "recording_guide", "segments_uploaded", "video_edited", "complete"]
            if current_step not in valid_steps:
                self.log_test("Get Project Details", False, 
                            f"Invalid current_step: {current_step}")
                return False
            
            self.log_test("Get Project Details", True, 
                        f"Project data retrieved successfully. Step: {current_step}, Segments: {len(shot_list)}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("Get Project Details", False, f"Request failed: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Get Project Details", False, f"Unexpected error: {str(e)}")
            return False
    
    def test_4_verify_viral_formats_seeded(self):
        """Test 4: Verify Viral Formats Seeded - Tests database seeding"""
        print("=== Test 4: Verify Viral Formats Seeded ===")
        
        try:
            # Test by creating another project with different parameters
            # This will trigger format matching and verify formats are available
            payload = {
                "user_goal": "I want to create a fast-paced product launch video like Cluely",
                "product_type": "consumer app",
                "target_platform": "TikTok"
            }
            
            # Make request
            response = requests.post(
                f"{BACKEND_URL}/director/project",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            # Check status code
            if response.status_code != 200:
                self.log_test("Verify Viral Formats Seeded", False, 
                            f"Expected status 200, got {response.status_code}. Response: {response.text}")
                return False
            
            # Parse response
            data = response.json()
            
            # Validate matched_format is present
            if "matched_format" not in data or not data["matched_format"]:
                self.log_test("Verify Viral Formats Seeded", False, 
                            f"No format matched - viral formats may not be seeded properly")
                return False
            
            matched_format = data["matched_format"]
            
            # Should match Cluely Launch format for TikTok consumer app
            expected_format_id = "cluely_launch"
            if matched_format.get("format_id") != expected_format_id:
                # Check if it's at least a valid format
                valid_format_ids = ["yc_demo_classic", "cluely_launch", "educational_tutorial", "before_after_transformation"]
                if matched_format.get("format_id") not in valid_format_ids:
                    self.log_test("Verify Viral Formats Seeded", False, 
                                f"Invalid format_id: {matched_format.get('format_id')}")
                    return False
            
            # Validate format structure
            required_format_fields = ["format_id", "name", "description", "platform_fit", "structure"]
            missing_format_fields = [field for field in required_format_fields if field not in matched_format]
            if missing_format_fields:
                self.log_test("Verify Viral Formats Seeded", False, 
                            f"Format missing fields: {missing_format_fields}")
                return False
            
            # Validate structure has segments
            structure = matched_format.get("structure", [])
            if not structure or len(structure) < 3:
                self.log_test("Verify Viral Formats Seeded", False, 
                            f"Format structure should have at least 3 segments, got: {len(structure)}")
                return False
            
            # Validate platform fit includes TikTok
            platform_fit = matched_format.get("platform_fit", [])
            if "TikTok" not in platform_fit:
                self.log_test("Verify Viral Formats Seeded", False, 
                            f"Format should support TikTok, platform_fit: {platform_fit}")
                return False
            
            self.log_test("Verify Viral Formats Seeded", True, 
                        f"Viral formats properly seeded. Matched: {matched_format['name']} ({matched_format['format_id']})")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("Verify Viral Formats Seeded", False, f"Request failed: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Verify Viral Formats Seeded", False, f"Unexpected error: {str(e)}")
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