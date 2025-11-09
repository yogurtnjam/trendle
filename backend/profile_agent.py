"""
ProfileAgent using LangChain tools with custom tools for user profiling.
This agent extracts target customer, product, audience, platform, and vibes information
from user conversations with minimal back-and-forth.
"""

# Removed langchain_core.tools import - using regular functions instead
from emergentintegrations.llm.chat import LlmChat, UserMessage
from motor.motor_asyncio import AsyncIOMotorDatabase
import os
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid


# MongoDB helper functions
async def get_session_from_db(db: AsyncIOMotorDatabase, session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve session from MongoDB"""
    session = await db.profile_sessions.find_one({"session_id": session_id}, {"_id": 0})
    return session


async def save_session_to_db(db: AsyncIOMotorDatabase, session_data: Dict[str, Any]):
    """Save or update session in MongoDB"""
    session_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    await db.profile_sessions.update_one(
        {"session_id": session_data["session_id"]},
        {"$set": session_data},
        upsert=True
    )


# Profile Agent Tools (converted from LangChain tools to regular functions)
async def calculate_confidence_score(session_id: str, db: AsyncIOMotorDatabase) -> Dict[str, float]:
    """
    Analyzes the current conversation data and returns confidence scores (0-100) 
    for each required field: target_customer, product, audience, platform, vibes.
    
    Args:
        session_id: The session ID to analyze
        db: MongoDB database instance
    
    Returns:
        Dictionary with confidence scores for each field
    """
    session = await get_session_from_db(db, session_id)
    if not session:
        return {
            "target_customer": 0,
            "product": 0,
            "audience": 0,
            "platform": 0,
            "vibes": 0,
            "overall": 0
        }
    
    profile_data = session.get("profile_data", {})
    scores = {}
    
    # Calculate confidence based on completeness and detail
    for field in ["target_customer", "product", "audience", "platform", "vibes"]:
        value = profile_data.get(field, "")
        if not value or value.strip() == "":
            scores[field] = 0
        elif len(value) < 10:
            scores[field] = 30  # Too brief
        elif len(value) < 30:
            scores[field] = 60  # Moderate detail
        else:
            scores[field] = 90  # Good detail
    
    # Calculate overall confidence
    scores["overall"] = sum(scores.values()) / 5 if scores else 0
    
    return scores


async def check_confidence_score(session_id: str, db: AsyncIOMotorDatabase) -> Dict[str, Any]:
    """
    Retrieves the current confidence scores from MongoDB for the session.
    
    Args:
        session_id: The session ID to check
        db: MongoDB database instance
    
    Returns:
        Dictionary with current confidence scores and profile data
    """
    session = await get_session_from_db(db, session_id)
    if not session:
        return {
            "confidence_scores": {
                "target_customer": 0,
                "product": 0,
                "audience": 0,
                "platform": 0,
                "vibes": 0,
                "overall": 0
            },
            "profile_data": {}
        }
    
    return {
        "confidence_scores": session.get("confidence_scores", {}),
        "profile_data": session.get("profile_data", {})
    }


async def save_profile_data(
    session_id: str,
    db: AsyncIOMotorDatabase,
    target_customer: Optional[str] = None,
    product: Optional[str] = None,
    audience: Optional[str] = None,
    platform: Optional[str] = None,
    vibes: Optional[str] = None
) -> Dict[str, str]:
    """
    Saves extracted profile information to MongoDB session.
    Only updates fields that are provided (non-None).
    
    Args:
        session_id: The session ID
        db: MongoDB database instance
        target_customer: Target customer description
        product: Product/service description
        audience: Target audience details
        platform: Platform preferences (TikTok, Instagram, YouTube, etc.)
        vibes: Content vibes/style preferences
    
    Returns:
        Success message with updated fields
    """
    session = await get_session_from_db(db, session_id)
    if not session:
        # Create new session if it doesn't exist
        session = {
            "session_id": session_id,
            "profile_data": {},
            "confidence_scores": {},
            "conversation_history": [],
            "profile_summary": "",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    
    profile_data = session.get("profile_data", {})
    updated_fields = []
    
    if target_customer is not None:
        profile_data["target_customer"] = target_customer
        updated_fields.append("target_customer")
    if product is not None:
        profile_data["product"] = product
        updated_fields.append("product")
    if audience is not None:
        profile_data["audience"] = audience
        updated_fields.append("audience")
    if platform is not None:
        profile_data["platform"] = platform
        updated_fields.append("platform")
    if vibes is not None:
        profile_data["vibes"] = vibes
        updated_fields.append("vibes")
    
    session["profile_data"] = profile_data
    
    # Recalculate confidence scores
    scores = await calculate_confidence_score(session_id, db)
    session["confidence_scores"] = scores
    
    await save_session_to_db(db, session)
    
    return {
        "status": "success",
        "updated_fields": ", ".join(updated_fields),
        "message": f"Saved profile data for: {', '.join(updated_fields)}"
    }


@tool
async def get_profile_data(session_id: str, db: AsyncIOMotorDatabase) -> Dict[str, Any]:
    """
    Retrieves current profile data from MongoDB for the session.
    
    Args:
        session_id: The session ID
        db: MongoDB database instance
    
    Returns:
        Current profile data
    """
    session = await get_session_from_db(db, session_id)
    if not session:
        return {}
    
    return session.get("profile_data", {})


@tool
async def generate_summary(session_id: str, db: AsyncIOMotorDatabase) -> Dict[str, Any]:
    """
    Generates a final summary of the user's profile when all confidence thresholds are met.
    This summary is used by downstream agents (like MatchingAgent) to understand the user's needs.
    
    Args:
        session_id: The session ID
        db: MongoDB database instance
    
    Returns:
        Profile summary and status
    """
    session = await get_session_from_db(db, session_id)
    if not session:
        return {"status": "error", "message": "Session not found"}
    
    profile_data = session.get("profile_data", {})
    confidence_scores = session.get("confidence_scores", {})
    
    # Check if all fields meet minimum confidence threshold (60%)
    required_fields = ["target_customer", "product", "audience", "platform", "vibes"]
    low_confidence_fields = [
        field for field in required_fields 
        if confidence_scores.get(field, 0) < 60
    ]
    
    if low_confidence_fields:
        return {
            "status": "incomplete",
            "message": f"Need more information about: {', '.join(low_confidence_fields)}",
            "confidence_scores": confidence_scores
        }
    
    # Generate structured summary
    summary = {
        "target_customer": profile_data.get("target_customer", ""),
        "product": profile_data.get("product", ""),
        "audience": profile_data.get("audience", ""),
        "platform": profile_data.get("platform", ""),
        "vibes": profile_data.get("vibes", ""),
        "confidence_scores": confidence_scores,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
    
    session["profile_summary"] = summary
    session["summary_generated"] = True
    await save_session_to_db(db, session)
    
    return {
        "status": "complete",
        "summary": summary,
        "message": "Profile complete! Ready for content matching."
    }


class ProfileAgent:
    """
    LangChain-based ProfileAgent that uses Claude Sonnet 4.5 via Emergent LLM key.
    The agent uses custom tools to extract and validate user profile information.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase, api_key: str):
        self.db = db
        self.api_key = api_key
        self.llm_chat = None
        
    async def initialize_llm(self, session_id: str):
        """Initialize LLM chat with Claude Sonnet 4.5"""
        self.llm_chat = LlmChat(
            api_key=self.api_key,
            session_id=session_id,
            system_message=self._get_system_prompt()
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
    def _get_system_prompt(self) -> str:
        """Returns the system prompt for the ProfileAgent"""
        return """You are a ProfileAgent for Trendle, an AI-powered content creation platform.

Your goal is to efficiently extract the following information from users with minimal conversation:

1. **Target Customer**: Who is the user trying to reach? (age, demographics, interests)
2. **Product**: What product/service/brand is the user promoting or creating content about?
3. **Audience**: What is their target audience's pain points, desires, behaviors?
4. **Platform**: Which platform(s) will they create content for? (TikTok, Instagram, YouTube, etc.)
5. **Vibes**: What style/tone/energy should the content have? (professional, playful, edgy, educational, etc.)

**Your Approach:**
- Start by asking 1-2 strategic questions that can reveal multiple pieces of information at once
- Use the tools to save information as you extract it
- Use calculate_confidence_score to check what information you still need
- Ask targeted follow-up questions ONLY for low-confidence fields
- Once all confidence scores are above 60%, use generate_summary to create the final profile
- Keep responses warm, concise, and conversational (2-3 sentences max per response)
- Avoid asking obvious questions if the user has already provided the information

**Available Tools:**
- save_profile_data: Save extracted information
- calculate_confidence_score: Check confidence levels
- check_confidence_score: Retrieve current scores
- get_profile_data: Get current profile data
- generate_summary: Generate final summary when ready

**Example Flow:**
User: "I'm building a language learning app for working professionals"
You: Great! 🎯 I can see you're targeting working professionals with a language learning product. Quick question: which platform are you planning to create content for (TikTok, Instagram, LinkedIn?), and what vibe should your content have - professional and trustworthy, or more casual and fun?

Remember: Be efficient, warm, and strategic in your questioning. Your goal is high confidence in 3-5 conversational turns."""

    async def process_message(
        self, 
        session_id: str, 
        user_message: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Process a user message and return agent response.
        
        Args:
            session_id: The session ID
            user_message: The user's message
            conversation_history: Previous conversation messages
        
        Returns:
            Agent response with message and metadata
        """
        if not self.llm_chat:
            await self.initialize_llm(session_id)
        
        # Create a simple wrapper that calls our async tools
        # Note: LangChain tools need to be synchronous for the agent executor
        # For now, we'll implement a simplified flow without full LangChain agent
        
        # Get current session state
        session = await get_session_from_db(self.db, session_id)
        if not session:
            # Create new session
            session = {
                "session_id": session_id,
                "profile_data": {},
                "confidence_scores": {},
                "conversation_history": [],
                "profile_summary": "",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await save_session_to_db(self.db, session)
        
        # Add user message to conversation history
        conversation_history.append({"role": "user", "content": user_message})
        session["conversation_history"] = conversation_history
        await save_session_to_db(self.db, session)
        
        # Build context for the LLM
        profile_data = session.get("profile_data", {})
        confidence_scores = session.get("confidence_scores", {})
        
        # Create enhanced prompt with current state
        enhanced_message = f"""Current Profile Data:
Target Customer: {profile_data.get('target_customer', 'Not yet collected')}
Product: {profile_data.get('product', 'Not yet collected')}
Audience: {profile_data.get('audience', 'Not yet collected')}
Platform: {profile_data.get('platform', 'Not yet collected')}
Vibes: {profile_data.get('vibes', 'Not yet collected')}

Confidence Scores:
{confidence_scores}

User Message: {user_message}

Instructions:
1. Extract any new information from the user's message
2. Update profile data as needed
3. Check what information is still missing or has low confidence
4. If overall confidence is below 60%, ask 1-2 strategic follow-up questions
5. If overall confidence is above 60%, generate the summary and confirm with the user
6. Be warm, concise, and efficient

Your Response:"""

        # Get LLM response
        llm_message = UserMessage(text=enhanced_message)
        agent_response = await self.llm_chat.send_message(llm_message)
        
        # Extract information from the conversation using simple heuristics
        await self._extract_and_save_info(session_id, user_message, agent_response)
        
        # Recalculate confidence
        new_scores = await calculate_confidence_score(session_id, self.db)
        
        # Check if we should generate summary
        summary_status = None
        if new_scores.get("overall", 0) >= 60:
            summary_result = await generate_summary(session_id, self.db)
            summary_status = summary_result.get("status")
        
        # Add agent response to conversation history
        conversation_history.append({"role": "assistant", "content": agent_response})
        session["conversation_history"] = conversation_history
        await save_session_to_db(self.db, session)
        
        return {
            "message": agent_response,
            "confidence_scores": new_scores,
            "summary_status": summary_status,
            "profile_data": profile_data
        }
    
    async def _extract_and_save_info(self, session_id: str, user_message: str, agent_response: str):
        """
        Extract information from user message using keyword detection and context.
        This is a simplified extraction - in production, you might use more sophisticated NLP.
        """
        user_lower = user_message.lower()
        extracted_data = {}
        
        # Platform detection
        platforms = ["tiktok", "instagram", "youtube", "linkedin", "twitter", "facebook"]
        detected_platforms = [p for p in platforms if p in user_lower]
        if detected_platforms:
            extracted_data["platform"] = ", ".join(detected_platforms).title()
        
        # Vibe detection
        vibes = ["professional", "casual", "fun", "playful", "edgy", "educational", 
                 "trustworthy", "authentic", "energetic", "calm", "inspiring"]
        detected_vibes = [v for v in vibes if v in user_lower]
        if detected_vibes:
            extracted_data["vibes"] = ", ".join(detected_vibes).title()
        
        # Product/service detection (look for keywords like "app", "service", "product", "brand")
        if any(keyword in user_lower for keyword in ["app", "service", "product", "brand", "business", "company"]):
            # Extract a phrase around these keywords (simplified)
            extracted_data["product"] = user_message[:100]  # First 100 chars as a rough extraction
        
        # Audience detection (look for "professional", "students", "young", "adults", age ranges)
        audience_keywords = ["professional", "students", "young", "adults", "teenagers", 
                            "working", "entrepreneurs", "parents"]
        if any(keyword in user_lower for keyword in audience_keywords):
            extracted_data["audience"] = user_message[:100]
        
        # Target customer (similar to audience)
        if any(keyword in user_lower for keyword in ["targeting", "for", "age", "demographic"]):
            extracted_data["target_customer"] = user_message[:100]
        
        # Save any extracted data
        if extracted_data:
            await save_profile_data(
                session_id=session_id,
                db=self.db,
                **extracted_data
            )
