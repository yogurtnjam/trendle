import logging
import os
from typing import List, Dict, Optional
import json
from emergentintegrations.llm.chat import LlmChat, UserMessage
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class AIContentAnalyzer:
    """Service for AI-powered content analysis using OpenAI GPT-5."""
    
    def __init__(self):
        self.api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
        
        self.session_chats = {}  # Store chat instances per session
    
    def _get_or_create_chat(self, session_id: str, system_message: str = None) -> LlmChat:
        """Get existing or create new chat instance for session."""
        if session_id not in self.session_chats:
            default_system = (
                "You are an expert content strategist for TikTok and social media. "
                "You analyze videos and provide actionable suggestions based on trending formats. "
                "Your advice is practical, specific, and optimized for virality. "
                "Always structure your suggestions as JSON with clear reasoning."
            )
            # Use GPT-4 as fallback due to GPT-5 timeout issues in 2025
            self.session_chats[session_id] = LlmChat(
                api_key=self.api_key,
                session_id=session_id,
                system_message=system_message or default_system
            ).with_model("openai", "gpt-4")
        
        return self.session_chats[session_id]
    
    async def analyze_video_with_trends(
        self,
        session_id: str,
        video_metadata: Dict,
        user_context: str,
        trending_formats: List[Dict],
        trending_hashtags: List[Dict]
    ) -> Dict:
        """Analyze video and generate suggestions based on trends."""
        try:
            chat = self._get_or_create_chat(session_id)
            
            # Construct detailed prompt
            prompt = self._construct_analysis_prompt(
                video_metadata,
                user_context,
                trending_formats,
                trending_hashtags
            )
            
            logger.info(f"Sending analysis request for video {video_metadata.get('id')}")
            
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            # Parse AI response
            suggestions = self._parse_ai_response(response, trending_formats)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            raise
    
    def _construct_analysis_prompt(
        self,
        video_metadata: Dict,
        user_context: str,
        trending_formats: List[Dict],
        trending_hashtags: List[Dict]
    ) -> str:
        """Construct detailed analysis prompt."""
        
        formats_summary = "\n".join([
            f"{i+1}. {f['name']}: {f['description']}\n   Structure: {f['structure']}\n   Performance: {f['performance_metrics']}"
            for i, f in enumerate(trending_formats[:3])
        ])
        
        hashtags_summary = ", ".join([h['hashtag'] for h in trending_hashtags[:10]])
        
        prompt = f"""
You are analyzing a video for content optimization.

**USER'S CONTEXT:**
{user_context}

**VIDEO INFO:**
- Filename: {video_metadata.get('filename')}
- Duration: {video_metadata.get('duration', 'unknown')} seconds
- Upload Date: {video_metadata.get('uploaded_at')}

**TOP TRENDING FORMATS RIGHT NOW:**
{formats_summary}

**TRENDING HASHTAGS:**
{hashtags_summary}

**YOUR TASK:**
Analyze this video and provide specific, actionable suggestions to make it more viral on TikTok.

1. **Recommend the BEST trending format** this content should follow (from the list above)
2. **Generate specific suggestions** in these categories:
   - Script rewrites or voice-over improvements
   - Text overlays to add (with exact timing)
   - Shot recommendations (what to re-record or emphasize)
   - Timestamp cuts (what to trim or rearrange)
   - Format structure (how to reorganize content)

**IMPORTANT:** Each suggestion must:
- Be specific and actionable (not generic advice)
- Include reasoning based on current trends
- Have a confidence score (0.0-1.0)
- Be something the user can accept or reject

Respond in this JSON format:
{{
  "recommended_format": {{
    "id": "format-id-from-list",
    "name": "Format Name",
    "reasoning": "Why this format fits their content"
  }},
  "suggestions": [
    {{
      "type": "script|text_overlay|shot|timestamp|format",
      "title": "Brief title",
      "description": "What to do",
      "content": "Exact text/script/action",
      "reasoning": "Why this will improve performance",
      "confidence_score": 0.85
    }}
  ]
}}

Provide 5-8 diverse, high-value suggestions.
"""
        return prompt
    
    def _parse_ai_response(self, response: str, trending_formats: List[Dict]) -> Dict:
        """Parse AI response and structure it."""
        try:
            # Try to extract JSON from response
            response_text = response.strip()
            
            # Find JSON in response (AI might add text before/after)
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = response_text[start:end]
                parsed = json.loads(json_str)
                
                # Validate and enrich response
                if "recommended_format" in parsed and "suggestions" in parsed:
                    # Find full format details
                    format_id = parsed["recommended_format"].get("id")
                    format_details = next(
                        (f for f in trending_formats if f["id"] == format_id),
                        trending_formats[0] if trending_formats else {}
                    )
                    
                    return {
                        "recommended_format": format_details,
                        "format_reasoning": parsed["recommended_format"].get("reasoning"),
                        "suggestions": parsed["suggestions"]
                    }
            
            # Fallback if parsing fails
            logger.warning("Failed to parse AI response as JSON, using fallback")
            return self._create_fallback_suggestions(trending_formats)
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return self._create_fallback_suggestions(trending_formats)
    
    def _create_fallback_suggestions(self, trending_formats: List[Dict]) -> Dict:
        """Create fallback suggestions if parsing fails."""
        return {
            "recommended_format": trending_formats[0] if trending_formats else {},
            "format_reasoning": "This format has the highest engagement rates currently.",
            "suggestions": [
                {
                    "type": "script",
                    "title": "Add Hook",
                    "description": "Start with attention-grabbing statement",
                    "content": "Open with 'Stop scrolling!' or surprising fact",
                    "reasoning": "First 3 seconds determine if viewers keep watching",
                    "confidence_score": 0.85
                },
                {
                    "type": "text_overlay",
                    "title": "Add Key Points",
                    "description": "Overlay text for main message",
                    "content": "Use bold text at 0:05, 0:15, 0:25",
                    "reasoning": "80% of TikTok is watched without sound",
                    "confidence_score": 0.90
                }
            ]
        }
    
    async def chat_with_context(
        self,
        session_id: str,
        message: str,
        video_context: Optional[Dict] = None
    ) -> str:
        """Handle conversational chat with context."""
        try:
            chat = self._get_or_create_chat(session_id)
            
            # Add video context if provided
            if video_context:
                context_note = f"\n\n[Context: User is working on video '{video_context.get('filename')}']\n\n"
                message = context_note + message
            
            user_message = UserMessage(text=message)
            response = await chat.send_message(user_message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            raise

# Global instance
ai_service = AIContentAnalyzer()