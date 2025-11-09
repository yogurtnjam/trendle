"""
LangGraph Director Workflow - Orchestrates video creation from concept to final export.
Manages multiple specialized agents for format matching, script planning, and video editing.
"""

from typing import TypedDict, Annotated, Sequence, List, Dict, Any, Optional
import operator
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from emergentintegrations.llm.chat import LlmChat, UserMessage
from motor.motor_asyncio import AsyncIOMotorDatabase
import json
from datetime import datetime, timezone

from viral_formats import (
    query_viral_formats, 
    calculate_format_match_score,
    get_format_by_id
)
from video_tools import (
    ffmpeg_merge_videos,
    ffmpeg_cut_video,
    ffmpeg_add_subtitles,
    get_video_metadata,
    optimize_for_platform
)


# Define the state that will be passed through the graph
class DirectorState(TypedDict):
    """State object for the Director workflow"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    project_id: str
    user_goal: str
    product_type: str
    target_platform: str
    matched_format: Optional[Dict[str, Any]]
    shot_list: Optional[List[Dict[str, Any]]]
    uploaded_segments: List[Dict[str, Any]]
    edited_video_path: Optional[str]
    current_step: str
    user_input_needed: bool
    next_instruction: str


class DirectorWorkflow:
    """
    Main Director Workflow using LangGraph.
    Coordinates all agents to guide users through video creation.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase, api_key: str):
        self.db = db
        self.api_key = api_key
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(DirectorState)
        
        # Add nodes for each agent
        workflow.add_node("director", self.director_agent)
        workflow.add_node("format_matcher", self.format_matcher_agent)
        workflow.add_node("script_planner", self.script_planner_agent)
        workflow.add_node("recording_guide", self.recording_guide_agent)
        workflow.add_node("video_editor", self.video_editor_agent)
        workflow.add_node("export", self.export_agent)
        
        # Define the workflow edges
        workflow.set_entry_point("director")
        
        # Director routes to appropriate agent based on current step
        workflow.add_conditional_edges(
            "director",
            self.route_from_director,
            {
                "format_matcher": "format_matcher",
                "script_planner": "script_planner",
                "recording_guide": "recording_guide",
                "video_editor": "video_editor",
                "export": "export",
                "end": END
            }
        )
        
        # Agents route back to director only when needed
        workflow.add_edge("format_matcher", "director")
        workflow.add_edge("script_planner", END)  # End after script planning for user interaction
        workflow.add_edge("recording_guide", END)
        workflow.add_edge("video_editor", "director")
        workflow.add_edge("export", END)
        
        return workflow.compile()
    
    def route_from_director(self, state: DirectorState) -> str:
        """Determine which agent to route to next"""
        current_step = state.get("current_step", "initial")
        messages = state.get("messages", [])
        
        # Check if there's a new user message that needs processing
        has_new_user_message = any(isinstance(m, HumanMessage) for m in messages[-2:])
        
        # For initial project creation, go through format matching and script planning
        if current_step == "initial":
            return "format_matcher"
        elif current_step == "format_matched":
            return "script_planner"
        elif current_step == "script_planned":
            # If user sent a new message, provide recording guidance
            if has_new_user_message:
                return "recording_guide"
            return "end"
        elif current_step == "segments_uploaded":
            return "video_editor"
        elif current_step == "video_edited":
            return "export"
        else:
            return "end"
    
    async def director_agent(self, state: DirectorState) -> DirectorState:
        """
        Director Agent - Main orchestrator that understands user goals
        and coordinates other agents.
        """
        current_step = state.get("current_step", "initial")
        
        # For initial setup, just coordinate - don't call LLM unnecessarily
        if current_step == "initial":
            # Just pass through to format matcher
            return state
        elif current_step in ["format_matched", "script_planned"]:
            # Just coordinate the workflow
            return state
        
        # For other steps that need director input, use LLM
        messages = state.get("messages", [])
        
        # Initialize LLM
        llm = LlmChat(
            api_key=self.api_key,
            session_id=state.get("project_id", "default"),
            system_message=self._get_director_prompt()
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        # Get last user message
        last_message = messages[-1].content if messages else ""
        
        # Build context for director
        context = self._build_director_context(state)
        director_input = f"{context}\n\nUser: {last_message}\n\nWhat should we do next?"
        
        # Get director's decision
        response = await llm.send_message(UserMessage(text=director_input))
        
        # Parse director's response and update state
        state["messages"].append(AIMessage(content=response))
        
        # Update project state in database
        await self._save_project_state(state)
        
        return state
    
    async def format_matcher_agent(self, state: DirectorState) -> DirectorState:
        """
        Format Matcher Agent - Matches user's goal with viral formats.
        """
        user_goal = state.get("user_goal", "")
        product_type = state.get("product_type", "")
        target_platform = state.get("target_platform", "")
        
        # Query viral formats from database
        formats = await query_viral_formats(
            self.db,
            platform=target_platform
        )
        
        # Calculate match scores
        format_scores = []
        for fmt in formats:
            score = await calculate_format_match_score(
                user_goal, product_type, target_platform, fmt
            )
            format_scores.append((fmt, score))
        
        # Sort by score and get best match
        format_scores.sort(key=lambda x: x[1], reverse=True)
        best_format = format_scores[0][0] if format_scores else None
        
        if best_format:
            state["matched_format"] = best_format
            state["current_step"] = "format_matched"
            
            # Create message about matched format
            format_message = f"""🎯 Perfect! I found the ideal format for your video: **{best_format['name']}**

{best_format['description']}

This format typically performs well on {', '.join(best_format['platform_fit'])} and includes {len(best_format['structure'])} key segments:
{self._format_structure_summary(best_format['structure'])}

This format has a viral score of {best_format['success_metrics']['viral_score']}/100 based on past performance.

Ready to move forward with this format?"""
            
            state["messages"].append(AIMessage(content=format_message))
        else:
            state["messages"].append(AIMessage(content="I couldn't find a perfect format match. Let me create a custom format for you..."))
        
        # Save project state to database
        await self._save_project_state(state)
        
        return state
    
    async def script_planner_agent(self, state: DirectorState) -> DirectorState:
        """
        Script Planner Agent - Creates detailed shot list and scripts.
        """
        matched_format = state.get("matched_format")
        user_goal = state.get("user_goal", "")
        
        if not matched_format:
            return state
        
        # Generate customized shot list based on format structure
        shot_list = []
        for segment in matched_format["structure"]:
            shot = {
                "segment_name": segment["segment"],
                "duration": segment["duration"],
                "script": segment["script_template"],
                "visual_guide": segment["visual_guide"],
                "required": segment["required"],
                "uploaded": False
            }
            shot_list.append(shot)
        
        state["shot_list"] = shot_list
        state["current_step"] = "script_planned"
        
        # Create detailed shot list message
        shot_list_message = f"""📝 Here's your complete shot list for the video:

{self._format_shot_list(shot_list)}

**Total Duration:** ~{sum(s['duration'] for s in shot_list)} seconds

I'll guide you through recording each segment step by step. Ready to start?"""
        
        state["messages"].append(AIMessage(content=shot_list_message))
        
        # Save project state to database
        await self._save_project_state(state)
        
        return state
    
    async def recording_guide_agent(self, state: DirectorState) -> DirectorState:
        """
        Recording Guide Agent - Provides step-by-step recording instructions.
        """
        shot_list = state.get("shot_list", [])
        uploaded_segments = state.get("uploaded_segments", [])
        
        # Find next segment to record
        next_segment = None
        for shot in shot_list:
            if not shot.get("uploaded", False):
                next_segment = shot
                break
        
        if next_segment:
            guide_message = f"""🎬 Let's record: **{next_segment['segment_name'].upper()}**

⏱️ **Duration:** {next_segment['duration']} seconds

📝 **Script:**
{next_segment['script']}

🎥 **How to film this:**
{next_segment['visual_guide']}

**Tips:**
• Film in good lighting
• Hold your phone steady (or use a tripod)
• Speak clearly and with energy
• Keep it within {next_segment['duration']} seconds

Upload your video when ready, and I'll validate it before we move to the next segment!"""
            
            state["messages"].append(AIMessage(content=guide_message))
            state["user_input_needed"] = True
            state["next_instruction"] = "upload_segment"
        else:
            # All segments uploaded
            state["current_step"] = "segments_uploaded"
            state["messages"].append(AIMessage(content="✅ All segments recorded! Now let's edit them together..."))
        
        return state
    
    async def video_editor_agent(self, state: DirectorState) -> DirectorState:
        """
        Video Editor Agent - Performs video editing using FFMPEG tools.
        """
        uploaded_segments = state.get("uploaded_segments", [])
        shot_list = state.get("shot_list", [])
        
        if not uploaded_segments:
            return state
        
        editing_steps = []
        
        # Step 1: Merge all segments
        video_files = [seg["file_path"] for seg in uploaded_segments]
        merge_result = await ffmpeg_merge_videos(
            input_files=video_files,
            output_file=f"merged_{state['project_id']}.mp4"
        )
        
        if merge_result["success"]:
            editing_steps.append("✅ Merged all segments")
            merged_path = merge_result["output_file"]
            
            # Step 2: Add subtitles (placeholder - would need actual subtitle data)
            # For MVP, we'll skip complex subtitle generation
            
            # Step 3: Add transitions (if needed)
            # This would require more complex logic
            
            state["edited_video_path"] = merged_path
            state["current_step"] = "video_edited"
            
            edit_message = f"""🎞️ Video editing complete!

Editing steps performed:
{chr(10).join(editing_steps)}

Your video is ready for final optimization and export. Which platform should we optimize it for?"""
            
            state["messages"].append(AIMessage(content=edit_message))
        else:
            state["messages"].append(AIMessage(content=f"❌ Video editing failed: {merge_result['error']}"))
        
        return state
    
    async def export_agent(self, state: DirectorState) -> DirectorState:
        """
        Export Agent - Optimizes and exports final video for platform.
        """
        edited_video = state.get("edited_video_path")
        target_platform = state.get("target_platform", "youtube")
        
        if not edited_video:
            return state
        
        # Optimize for platform
        export_result = await optimize_for_platform(
            input_file=edited_video,
            output_file=f"final_{state['project_id']}_{target_platform}.mp4",
            platform=target_platform
        )
        
        if export_result["success"]:
            state["current_step"] = "complete"
            
            final_message = f"""🎉 Your video is ready!

✅ Optimized for {target_platform}
📁 **Download:** {export_result['output_file']}

Your video is now perfectly formatted for {target_platform} with the right dimensions, bitrate, and compression.

Want to export for other platforms too?"""
            
            state["messages"].append(AIMessage(content=final_message))
        else:
            state["messages"].append(AIMessage(content=f"❌ Export failed: {export_result['error']}"))
        
        return state
    
    # Helper methods
    
    def _get_director_prompt(self) -> str:
        """System prompt for Director Agent"""
        return """You are a Director AI for Trendle, a video creation platform. Your role is to:

1. Understand the user's video goals (what they want to create, for which platform)
2. Coordinate specialized agents to help them create viral-worthy content
3. Guide users through each step of the video creation process
4. Make decisions about which agent to involve next

You have access to these specialized agents:
- Format Matcher: Finds the best viral video format for the user's goal
- Script Planner: Creates detailed shot lists and scripts
- Recording Guide: Provides step-by-step filming instructions
- Video Editor: Performs all video editing operations
- Export Agent: Optimizes and exports the final video

Be encouraging, clear, and strategic. Break complex tasks into simple steps."""
    
    def _build_director_context(self, state: DirectorState) -> str:
        """Build context summary for director"""
        context_parts = [f"Current Step: {state.get('current_step', 'initial')}"]
        
        if state.get("user_goal"):
            context_parts.append(f"User Goal: {state['user_goal']}")
        
        if state.get("matched_format"):
            context_parts.append(f"Format: {state['matched_format']['name']}")
        
        if state.get("shot_list"):
            completed = sum(1 for s in state['shot_list'] if s.get('uploaded'))
            total = len(state['shot_list'])
            context_parts.append(f"Recording Progress: {completed}/{total} segments")
        
        return "\n".join(context_parts)
    
    def _format_structure_summary(self, structure: List[Dict]) -> str:
        """Format structure summary for display"""
        summary = []
        for i, seg in enumerate(structure, 1):
            summary.append(f"{i}. **{seg['segment'].title()}** ({seg['duration']}s): {seg['script_template'][:50]}...")
        return "\n".join(summary)
    
    def _format_shot_list(self, shot_list: List[Dict]) -> str:
        """Format shot list for display"""
        formatted = []
        for i, shot in enumerate(shot_list, 1):
            status = "✅" if shot.get("uploaded") else "⏳"
            formatted.append(
                f"{status} **Segment {i}: {shot['segment_name'].title()}** ({shot['duration']}s)\n"
                f"   Script: {shot['script']}\n"
                f"   Visual: {shot['visual_guide']}"
            )
        return "\n\n".join(formatted)
    
    async def _save_project_state(self, state: DirectorState):
        """Save project state to MongoDB"""
        project_data = {
            "project_id": state["project_id"],
            "user_goal": state.get("user_goal", ""),
            "product_type": state.get("product_type", ""),
            "target_platform": state.get("target_platform", ""),
            "matched_format": state.get("matched_format"),
            "shot_list": state.get("shot_list"),
            "uploaded_segments": state.get("uploaded_segments", []),
            "edited_video_path": state.get("edited_video_path"),
            "current_step": state.get("current_step"),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.video_projects.update_one(
            {"project_id": state["project_id"]},
            {"$set": project_data},
            upsert=True
        )
