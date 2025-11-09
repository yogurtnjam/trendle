#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Trendle Platform
Tests all backend APIs including video upload, AI analysis, suggestions, and chat.
"""

import asyncio
import httpx
import json
import base64
import uuid
import os
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Backend URL from environment
BACKEND_URL = "https://content-coach-6.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class TrendleAPITester:
    """Comprehensive API tester for Trendle backend."""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.video_id = None
        self.suggestion_id = None
        self.test_results = {
            "health_check": False,
            "trends_api": False,
            "video_upload": False,
            "video_analysis": False,
            "suggestions_api": False,
            "chat_api": False
        }
        self.errors = []
    
    async def run_all_tests(self):
        """Run all backend tests."""
        logger.info(f"Starting comprehensive backend tests for session: {self.session_id}")
        logger.info(f"Backend URL: {BACKEND_URL}")
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Test 1: Health Check
            await self.test_health_check(client)
            
            # Test 2: Trends API (already verified working)
            await self.test_trends_api(client)
            
            # Test 3: Video Upload Flow
            await self.test_video_upload_flow(client)
            
            # Test 4: Video Analysis (AI Integration)
            if self.video_id:
                await self.test_video_analysis(client)
            
            # Test 5: Suggestions Management
            if self.video_id:
                await self.test_suggestions_api(client)
            
            # Test 6: Chat API
            await self.test_chat_api(client)
        
        # Print results
        self.print_test_results()
    
    async def test_health_check(self, client: httpx.AsyncClient):
        """Test health check endpoints."""
        logger.info("Testing health check endpoints...")
        
        try:
            # Test root endpoint
            response = await client.get(f"{API_BASE}/")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Root endpoint: {data}")
                
                # Test health endpoint
                response = await client.get(f"{API_BASE}/health")
                if response.status_code == 200:
                    health_data = response.json()
                    logger.info(f"Health check: {health_data}")
                    self.test_results["health_check"] = True
                else:
                    self.errors.append(f"Health endpoint failed: {response.status_code}")
            else:
                self.errors.append(f"Root endpoint failed: {response.status_code}")
                
        except Exception as e:
            self.errors.append(f"Health check error: {str(e)}")
            logger.error(f"Health check failed: {str(e)}")
    
    async def test_trends_api(self, client: httpx.AsyncClient):
        """Test trends API endpoints."""
        logger.info("Testing trends API...")
        
        try:
            # Test current trends
            response = await client.get(f"{API_BASE}/trends/current")
            if response.status_code == 200:
                trends_data = response.json()
                logger.info(f"Current trends: {len(trends_data.get('hashtags', []))} hashtags, {len(trends_data.get('formats', []))} formats")
                
                # Test individual endpoints
                hashtags_resp = await client.get(f"{API_BASE}/trends/hashtags")
                formats_resp = await client.get(f"{API_BASE}/trends/formats")
                
                if hashtags_resp.status_code == 200 and formats_resp.status_code == 200:
                    self.test_results["trends_api"] = True
                    logger.info("Trends API: ✅ All endpoints working")
                else:
                    self.errors.append("Individual trends endpoints failed")
            else:
                self.errors.append(f"Trends API failed: {response.status_code}")
                
        except Exception as e:
            self.errors.append(f"Trends API error: {str(e)}")
            logger.error(f"Trends API failed: {str(e)}")
    
    def create_test_video_file(self) -> bytes:
        """Create a small test video file (dummy data)."""
        # Create a minimal MP4-like file (just dummy bytes for testing)
        # In real scenario, this would be actual video data
        dummy_video_data = b"FAKE_MP4_DATA_FOR_TESTING" * 100  # ~2.5KB
        return dummy_video_data
    
    async def test_video_upload_flow(self, client: httpx.AsyncClient):
        """Test chunked video upload flow."""
        logger.info("Testing video upload flow...")
        
        try:
            # Create test video data
            video_data = self.create_test_video_file()
            filename = "test_video.mp4"
            
            # Split into chunks (simulate chunked upload)
            chunk_size = 1024  # 1KB chunks
            chunks = [video_data[i:i+chunk_size] for i in range(0, len(video_data), chunk_size)]
            total_chunks = len(chunks)
            
            logger.info(f"Uploading {len(video_data)} bytes in {total_chunks} chunks")
            
            # Upload each chunk
            for i, chunk in enumerate(chunks):
                chunk_data = base64.b64encode(chunk).decode('utf-8')
                
                payload = {
                    "chunk_index": i,
                    "total_chunks": total_chunks,
                    "chunk_data": chunk_data,
                    "session_id": self.session_id,
                    "filename": filename
                }
                
                response = await client.post(f"{API_BASE}/videos/upload-chunk", json=payload)
                
                if response.status_code != 200:
                    self.errors.append(f"Chunk upload failed: {response.status_code} - {response.text}")
                    return
                
                result = response.json()
                logger.info(f"Chunk {i+1}/{total_chunks}: {result.get('message')}")
                
                # If upload completed, save video_id
                if result.get("status") == "completed":
                    self.video_id = result.get("video_id")
                    logger.info(f"Upload completed! Video ID: {self.video_id}")
            
            # Test video listing
            if self.video_id:
                list_response = await client.get(f"{API_BASE}/videos/list/{self.session_id}")
                if list_response.status_code == 200:
                    videos = list_response.json()
                    logger.info(f"Video list: {videos.get('count')} videos found")
                    
                    # Test get specific video
                    video_response = await client.get(f"{API_BASE}/videos/{self.video_id}")
                    if video_response.status_code == 200:
                        video_data = video_response.json()
                        logger.info(f"Video details: {video_data.get('filename')}")
                        self.test_results["video_upload"] = True
                        logger.info("Video Upload: ✅ All upload endpoints working")
                    else:
                        self.errors.append(f"Get video failed: {video_response.status_code}")
                else:
                    self.errors.append(f"List videos failed: {list_response.status_code}")
            else:
                self.errors.append("Video upload completed but no video_id returned")
                
        except Exception as e:
            self.errors.append(f"Video upload error: {str(e)}")
            logger.error(f"Video upload failed: {str(e)}")
    
    async def test_video_analysis(self, client: httpx.AsyncClient):
        """Test AI video analysis."""
        logger.info("Testing AI video analysis...")
        
        try:
            analysis_payload = {
                "video_id": self.video_id,
                "user_context": "Content creator looking to optimize video for TikTok engagement",
                "target_platform": "TikTok",
                "target_audience": "Gen Z creators and entrepreneurs"
            }
            
            logger.info(f"Starting analysis for video: {self.video_id}")
            response = await client.post(f"{API_BASE}/videos/analyze", json=analysis_payload)
            
            if response.status_code == 200:
                analysis_result = response.json()
                logger.info(f"Analysis completed: {analysis_result.get('success')}")
                logger.info(f"Recommended format: {analysis_result.get('recommended_format', {}).get('name')}")
                logger.info(f"Suggestions count: {len(analysis_result.get('suggestions', []))}")
                
                # Save first suggestion ID for later testing
                suggestions = analysis_result.get('suggestions', [])
                if suggestions:
                    self.suggestion_id = suggestions[0].get('id')
                
                self.test_results["video_analysis"] = True
                logger.info("Video Analysis: ✅ AI analysis working")
            else:
                self.errors.append(f"Video analysis failed: {response.status_code} - {response.text}")
                logger.error(f"Analysis failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.errors.append(f"Video analysis error: {str(e)}")
            logger.error(f"Video analysis failed: {str(e)}")
    
    async def test_suggestions_api(self, client: httpx.AsyncClient):
        """Test suggestions management API."""
        logger.info("Testing suggestions API...")
        
        try:
            # Get suggestions for video
            response = await client.get(f"{API_BASE}/suggestions/{self.video_id}")
            
            if response.status_code == 200:
                suggestions_data = response.json()
                logger.info(f"Retrieved suggestions: {suggestions_data.get('count')} suggestions")
                
                # Get a suggestion ID from the response
                suggestions = suggestions_data.get('suggestions', [])
                if suggestions and len(suggestions) > 0:
                    # Get first suggestion from first document
                    first_doc = suggestions[0]
                    if 'suggestions' in first_doc and len(first_doc['suggestions']) > 0:
                        self.suggestion_id = first_doc['suggestions'][0]['id']
                        logger.info(f"Using suggestion ID: {self.suggestion_id}")
                        
                        # Test accept suggestion
                        accept_payload = {
                            "suggestion_id": self.suggestion_id,
                            "action": "accept",
                            "feedback": "This suggestion looks great for improving engagement!"
                        }
                        
                        accept_response = await client.post(f"{API_BASE}/suggestions/action", json=accept_payload)
                        
                        if accept_response.status_code == 200:
                            accept_result = accept_response.json()
                            logger.info(f"Suggestion accepted: {accept_result.get('message')}")
                            
                            # Test suggestions status
                            status_response = await client.get(f"{API_BASE}/suggestions/status/{self.video_id}")
                            
                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                logger.info(f"Suggestions status: {status_data.get('status_summary')}")
                                self.test_results["suggestions_api"] = True
                                logger.info("Suggestions API: ✅ All endpoints working")
                            else:
                                self.errors.append(f"Suggestions status failed: {status_response.status_code}")
                        else:
                            self.errors.append(f"Accept suggestion failed: {accept_response.status_code}")
                    else:
                        logger.error(f"No suggestions found in document structure: {first_doc.keys()}")
                        self.errors.append("No suggestions found in response structure")
                        return
                else:
                    self.errors.append("No suggestions documents found")
            else:
                self.errors.append(f"Get suggestions failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.errors.append(f"Suggestions API error: {str(e)}")
            logger.error(f"Suggestions API failed: {str(e)}")
    
    async def test_chat_api(self, client: httpx.AsyncClient):
        """Test chat API with AI context."""
        logger.info("Testing chat API...")
        
        try:
            # Test general chat (without video context)
            general_chat_payload = {
                "session_id": self.session_id,
                "message": "What are the best practices for creating viral TikTok content?",
                "context": {"user_type": "content_creator"}
            }
            
            response = await client.post(f"{API_BASE}/chat/message", json=general_chat_payload)
            
            if response.status_code == 200:
                chat_result = response.json()
                logger.info(f"General chat response received: {len(chat_result.get('response', ''))} characters")
                
                # Test contextualized chat (with video)
                if self.video_id:
                    video_chat_payload = {
                        "session_id": self.session_id,
                        "message": "How can I improve this specific video based on the analysis?",
                        "video_id": self.video_id,
                        "context": {"request_type": "video_improvement"}
                    }
                    
                    video_response = await client.post(f"{API_BASE}/chat/message", json=video_chat_payload)
                    
                    if video_response.status_code == 200:
                        video_chat_result = video_response.json()
                        logger.info(f"Video-contextualized chat response: {len(video_chat_result.get('response', ''))} characters")
                
                # Test chat history
                history_response = await client.get(f"{API_BASE}/chat/history/{self.session_id}")
                
                if history_response.status_code == 200:
                    history_data = history_response.json()
                    logger.info(f"Chat history: {history_data.get('count')} messages")
                    
                    self.test_results["chat_api"] = True
                    logger.info("Chat API: ✅ All endpoints working")
                else:
                    self.errors.append(f"Chat history failed: {history_response.status_code}")
            else:
                self.errors.append(f"Chat message failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.errors.append(f"Chat API error: {str(e)}")
            logger.error(f"Chat API failed: {str(e)}")
    
    def print_test_results(self):
        """Print comprehensive test results."""
        logger.info("\n" + "="*60)
        logger.info("TRENDLE BACKEND API TEST RESULTS")
        logger.info("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(self.test_results.values())
        
        for test_name, passed in self.test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
        
        logger.info(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if self.errors:
            logger.info(f"\nErrors encountered ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                logger.info(f"{i}. {error}")
        
        logger.info("="*60)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "test_results": self.test_results,
            "errors": self.errors
        }

async def main():
    """Main test runner."""
    tester = TrendleAPITester()
    results = await tester.run_all_tests()
    
    # Return results for programmatic access
    return results

if __name__ == "__main__":
    asyncio.run(main())