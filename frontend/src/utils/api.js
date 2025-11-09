const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Helper function to generate session ID
export const getSessionId = () => {
  let sessionId = localStorage.getItem('trendle_session_id');
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('trendle_session_id', sessionId);
  }
  return sessionId;
};

// Chunked video upload
export const uploadVideoChunked = async (file, onProgress) => {
  const CHUNK_SIZE = 1024 * 1024; // 1MB chunks
  const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
  const sessionId = getSessionId();
  
  for (let i = 0; i < totalChunks; i++) {
    const start = i * CHUNK_SIZE;
    const end = Math.min(start + CHUNK_SIZE, file.size);
    const chunk = file.slice(start, end);
    
    // Convert chunk to base64
    const base64Chunk = await new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = () => {
        const base64 = reader.result.split(',')[1];
        resolve(base64);
      };
      reader.readAsDataURL(chunk);
    });
    
    // Upload chunk
    const response = await fetch(`${API_BASE_URL}/api/videos/upload-chunk`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chunk_index: i,
        total_chunks: totalChunks,
        chunk_data: base64Chunk,
        session_id: sessionId,
        filename: file.name
      })
    });
    
    const result = await response.json();
    
    if (onProgress) {
      onProgress({
        uploaded: i + 1,
        total: totalChunks,
        percentage: Math.round(((i + 1) / totalChunks) * 100)
      });
    }
    
    // Return video metadata on completion
    if (result.status === 'completed') {
      return result;
    }
  }
};

// Get trending data
export const getTrendingData = async () => {
  const response = await fetch(`${API_BASE_URL}/api/trends/current?hashtag_limit=20`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
};

// Analyze video
export const analyzeVideo = async (videoId, userContext, targetAudience) => {
  const response = await fetch(`${API_BASE_URL}/api/videos/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      video_id: videoId,
      user_context: userContext,
      target_platform: 'TikTok',
      target_audience: targetAudience
    })
  });
  return response.json();
};

// Get suggestions for video
export const getSuggestions = async (videoId) => {
  const response = await fetch(`${API_BASE_URL}/api/suggestions/${videoId}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
};

// Accept/reject suggestion
export const handleSuggestionAction = async (suggestionId, action, feedback = null) => {
  const response = await fetch(`${API_BASE_URL}/api/suggestions/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      suggestion_id: suggestionId,
      action: action,
      feedback: feedback
    })
  });
  return response.json();
};

// Send chat message
export const sendChatMessage = async (message, videoId = null) => {
  const sessionId = getSessionId();
  const response = await fetch(`${API_BASE_URL}/api/chat/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      message: message,
      video_id: videoId
    })
  });
  return response.json();
};

// Get chat history
export const getChatHistory = async () => {
  const sessionId = getSessionId();
  const response = await fetch(`${API_BASE_URL}/api/chat/history/${sessionId}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
};

// List videos for session
export const listVideos = async () => {
  const sessionId = getSessionId();
  const response = await fetch(`${API_BASE_URL}/api/videos/list/${sessionId}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
};