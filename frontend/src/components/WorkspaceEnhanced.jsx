import React, { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Avatar, AvatarFallback } from './ui/avatar';
import { 
  Sparkles, Upload, X, Send, Video, CheckCircle, XCircle, 
  TrendingUp, Wand2, Zap, Loader2, AlertCircle, ThumbsUp, ThumbsDown
} from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import {
  uploadVideoChunked,
  analyzeVideo,
  sendChatMessage,
  getChatHistory,
  handleSuggestionAction
} from '../utils/api';

export const WorkspaceEnhanced = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [uploadedVideo, setUploadedVideo] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [currentSuggestions, setCurrentSuggestions] = useState([]);
  const [trendingFormat, setTrendingFormat] = useState(null);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load chat history on mount
  useEffect(() => {
    loadChatHistory();
  }, []);

  const loadChatHistory = async () => {
    try {
      const history = await getChatHistory();
      if (history.messages && history.messages.length > 0) {
        const formattedMessages = history.messages.map(msg => ({
          role: msg.role,
          content: msg.content,
          timestamp: new Date(msg.timestamp)
        }));
        setMessages(formattedMessages);
      } else {
        // Add welcome message if no history
        setMessages([{
          role: 'assistant',
          content: '👋 Hey there! I\'m your AI content strategist. Upload a video, tell me about your content goals, and I\'ll analyze it against trending formats to give you actionable suggestions.',
          timestamp: new Date()
        }]);
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
      setMessages([{
        role: 'assistant',
        content: '👋 Hey there! I\'m your AI content strategist. Upload a video and let\'s make it viral!',
        timestamp: new Date()
      }]);
    }
  };

  const quickPrompts = [
    { icon: <TrendingUp className="w-4 h-4" />, text: 'Show me trending formats', color: 'bg-primary/10 text-primary border-primary/20' },
    { icon: <Wand2 className="w-4 h-4" />, text: 'Analyze my video for TikTok', color: 'bg-secondary/10 text-secondary border-secondary/20' },
    { icon: <Zap className="w-4 h-4" />, text: 'What hooks work best right now?', color: 'bg-accent/20 text-foreground border-accent/30' },
  ];

  const handleFileSelect = async (e) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      await handleVideoUpload(files[0]);
    }
  };

  const handleVideoUpload = async (file) => {
    if (!file.type.startsWith('video/')) {
      toast.error('Please upload a video file');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      const result = await uploadVideoChunked(file, (progress) => {
        setUploadProgress(progress.percentage);
      });

      setUploadedVideo({
        id: result.video_metadata.id,
        name: file.name,
        size: (file.size / 1024 / 1024).toFixed(2),
        url: URL.createObjectURL(file)
      });

      toast.success('Video uploaded! 🎉', {
        description: 'Ready for AI analysis'
      });

      // Add system message
      const systemMessage = {
        role: 'system',
        content: `📹 Video "${file.name}" (${(file.size / 1024 / 1024).toFixed(2)} MB) uploaded successfully! Ready to analyze.`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, systemMessage]);

    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Upload failed', {
        description: error.message || 'Please try again'
      });
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0 && files[0].type.startsWith('video/')) {
      handleVideoUpload(files[0]);
    } else {
      toast.error('Please drop a video file');
    }
  };

  const removeVideo = () => {
    setUploadedVideo(null);
    setCurrentSuggestions([]);
    setTrendingFormat(null);
    toast.success('Video removed');
  };

  const handleAnalyzeVideo = async () => {
    if (!uploadedVideo) {
      toast.error('Please upload a video first');
      return;
    }

    if (!inputValue.trim()) {
      toast.error('Please describe your content goals');
      return;
    }

    setIsAnalyzing(true);
    setIsProcessing(true);

    // Add user message
    const userMessage = {
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');

    try {
      toast.loading('Analyzing your video...', { id: 'analysis' });

      const result = await analyzeVideo(
        uploadedVideo.id,
        inputValue.trim(),
        null
      );

      toast.success('Analysis complete! 🎯', { id: 'analysis' });

      // Format AI response
      const aiResponse = formatAnalysisResponse(result);
      const aiMessage = {
        role: 'assistant',
        content: aiResponse,
        timestamp: new Date(),
        suggestions: result.suggestions,
        format: result.recommended_format
      };
      setMessages(prev => [...prev, aiMessage]);

      // Store suggestions
      setCurrentSuggestions(result.suggestions || []);
      setTrendingFormat(result.recommended_format);

    } catch (error) {
      console.error('Analysis error:', error);
      toast.error('Analysis failed', { id: 'analysis', description: error.message });
      
      const errorMessage = {
        role: 'assistant',
        content: '❌ Sorry, I encountered an error analyzing your video. Please try again or contact support if the issue persists.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsAnalyzing(false);
      setIsProcessing(false);
    }
  };

  const formatAnalysisResponse = (result) => {
    const format = result.recommended_format;
    const reasoning = result.format_reasoning;
    const suggestions = result.suggestions || [];
    const hashtags = result.trending_hashtags_used || [];

    let response = `🎬 **Video Analysis Complete!**\n\n`;
    response += `📊 **Recommended Format: "${format?.name || 'Custom'}"**\n`;
    response += `${reasoning}\n\n`;
    response += `**Format Structure:** ${format?.structure || 'N/A'}\n\n`;
    response += `💡 **AI Suggestions (${suggestions.length}):**\n`;
    response += `I've generated ${suggestions.length} actionable suggestions below. Review each one and accept the ones that resonate with your vision!\n\n`;
    
    if (hashtags.length > 0) {
      response += `🔥 **Trending Hashtags:**\n`;
      response += hashtags.map(h => `#${h.hashtag}`).join(' ') + '\n\n';
    }

    response += `👇 Scroll down to see all suggestions with accept/reject buttons.`;

    return response;
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) {
      return;
    }

    // If video is uploaded but not analyzed yet, trigger analysis
    if (uploadedVideo && currentSuggestions.length === 0) {
      handleAnalyzeVideo();
      return;
    }

    setIsProcessing(true);

    const userMessage = {
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');

    try {
      const result = await sendChatMessage(
        userMessage.content,
        uploadedVideo?.id
      );

      const aiMessage = {
        role: 'assistant',
        content: result.response,
        timestamp: new Date(result.timestamp)
      };
      setMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      console.error('Chat error:', error);
      toast.error('Failed to send message');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSuggestionAccept = async (suggestion) => {
    try {
      await handleSuggestionAction(suggestion.id, 'accept');
      
      // Update local state
      setCurrentSuggestions(prev =>
        prev.map(s => s.id === suggestion.id ? { ...s, status: 'accepted' } : s)
      );

      toast.success('Suggestion accepted! ✅', {
        description: suggestion.title
      });
    } catch (error) {
      toast.error('Failed to accept suggestion');
    }
  };

  const handleSuggestionReject = async (suggestion) => {
    try {
      await handleSuggestionAction(suggestion.id, 'reject');
      
      // Update local state
      setCurrentSuggestions(prev =>
        prev.map(s => s.id === suggestion.id ? { ...s, status: 'rejected' } : s)
      );

      toast.success('Suggestion rejected', {
        description: 'Removed from your list'
      });
    } catch (error) {
      toast.error('Failed to reject suggestion');
    }
  };

  const handleQuickPrompt = (promptText) => {
    setInputValue(promptText);
    textareaRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getSuggestionIcon = (type) => {
    switch (type) {
      case 'script': return '📝';
      case 'text_overlay': return '💬';
      case 'shot': return '🎥';
      case 'timestamp': return '⏱️';
      case 'format': return '🎬';
      default: return '✨';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-sky relative overflow-hidden gradient-bg-dynamic">
      {/* Dynamic gradient orbs */}
      <div className="gradient-orb-1"></div>
      <div className="gradient-orb-2"></div>
      <div className="gradient-orb-3"></div>
      
      {/* Floating decorative stickers */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden z-10">
        <div className="floating-sticker top-20 left-[8%] text-5xl animate-float" style={{ animationDelay: '0s' }}>✨</div>
        <div className="floating-sticker top-32 right-[12%] text-4xl animate-float" style={{ animationDelay: '1.5s' }}>🎬</div>
        <div className="floating-sticker bottom-32 left-[15%] text-4xl animate-float" style={{ animationDelay: '3s' }}>🚀</div>
        <div className="floating-sticker top-[45%] right-[20%] text-3xl animate-float" style={{ animationDelay: '2s' }}>💡</div>
        <div className="floating-sticker bottom-24 right-[8%] text-4xl animate-float" style={{ animationDelay: '2.5s' }}>⚡</div>
        <div className="floating-sticker top-[60%] left-[5%] text-3xl animate-float" style={{ animationDelay: '1s' }}>🎯</div>
      </div>

      {/* Navigation */}
      <nav className="border-b border-border/50 bg-background/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <button onClick={() => navigate('/')} className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <span className="text-3xl font-logo font-bold text-foreground">Trendle</span>
            </button>
            <div className="flex items-center gap-4">
              <Badge className="hidden sm:flex bg-accent/20 text-foreground border-accent/30 hover:bg-accent/30 font-sans">
                <Sparkles className="w-3 h-3 mr-1" />
                AI Workspace
              </Badge>
              <Avatar className="w-9 h-9 border-2 border-primary/20">
                <AvatarFallback className="bg-gradient-primary text-primary-foreground font-semibold">U</AvatarFallback>
              </Avatar>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        <div className="space-y-6">
          {/* Welcome Card */}
          <Card className="border-border/50 shadow-xl bg-card/95 backdrop-blur-sm animate-slide-up relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-3xl"></div>
            <CardContent className="pt-6 relative">
              <div className="flex items-start gap-4">
                <div className="w-14 h-14 rounded-xl bg-gradient-primary flex items-center justify-center flex-shrink-0 shadow-md">
                  <Sparkles className="w-7 h-7 text-primary-foreground" />
                </div>
                <div className="flex-1">
                  <h2 className="text-3xl font-display font-bold text-foreground mb-2">Your AI Content Studio</h2>
                  <p className="text-muted-foreground leading-relaxed text-lg font-sans">
                    Upload your video and describe your goals. I'll analyze it against real trending formats and give you specific, actionable suggestions to boost engagement.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Video Upload Area */}
          {!uploadedVideo && (
            <Card className="border-border/50 shadow-xl bg-card/95 backdrop-blur-sm animate-slide-up">
              <CardContent className="pt-6">
                <div
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  className={`border-2 border-dashed rounded-xl p-8 transition-all duration-300 ${
                    isDragging 
                      ? 'border-primary bg-primary/5 scale-[1.01] shadow-glow' 
                      : 'border-border/50 hover:border-border hover:bg-muted/20'
                  }`}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="video/*"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  
                  {isUploading ? (
                    <div className="flex flex-col items-center justify-center gap-4">
                      <Loader2 className="w-12 h-12 text-primary animate-spin" />
                      <div className="text-center w-full max-w-xs">
                        <p className="text-sm font-semibold text-foreground mb-2">Uploading video...</p>
                        <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
                          <div 
                            className="h-full bg-gradient-primary transition-all duration-300"
                            style={{ width: `${uploadProgress}%` }}
                          ></div>
                        </div>
                        <p className="text-xs text-muted-foreground mt-2">{uploadProgress}%</p>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="w-full flex flex-col items-center justify-center gap-3 group"
                    >
                      <div className="w-16 h-16 rounded-xl bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-all duration-300 group-hover:scale-110">
                        <Upload className="w-8 h-8 text-primary" />
                      </div>
                      <div className="text-center">
                        <p className="text-base font-semibold text-foreground font-sans">Drop your video here or click to browse</p>
                        <p className="text-sm text-muted-foreground mt-1 font-sans">Supports MP4, MOV, AVI • Max 100MB</p>
                      </div>
                    </button>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Uploaded Video Display */}
          {uploadedVideo && (
            <Card className="border-border/50 shadow-xl bg-card/95 backdrop-blur-sm animate-slide-up">
              <CardContent className="pt-6">
                <div className="flex items-start gap-4">
                  <div className="w-20 h-20 rounded-lg bg-muted flex items-center justify-center flex-shrink-0">
                    <Video className="w-10 h-10 text-muted-foreground" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className="font-semibold text-foreground truncate">{uploadedVideo.name}</p>
                        <p className="text-sm text-muted-foreground">{uploadedVideo.size} MB</p>
                        {currentSuggestions.length > 0 && (
                          <Badge className="mt-2 bg-primary/10 text-primary border-primary/20">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            {currentSuggestions.length} suggestions generated
                          </Badge>
                        )}
                      </div>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={removeVideo}
                        className="text-destructive hover:text-destructive hover:bg-destructive/10"
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Chat Messages */}
          <div className="space-y-4 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            {messages.map((message, index) => (
              <div key={index} className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {(message.role === 'assistant' || message.role === 'system') && (
                  <Avatar className="w-10 h-10 border-2 border-primary/20 flex-shrink-0">
                    <AvatarFallback className="bg-gradient-primary text-primary-foreground">
                      {message.role === 'system' ? <AlertCircle className="w-5 h-5" /> : <Sparkles className="w-5 h-5" />}
                    </AvatarFallback>
                  </Avatar>
                )}
                
                <div className={`flex-1 max-w-3xl ${message.role === 'user' ? 'flex flex-col items-end' : ''}`}>
                  <Card className={`${
                    message.role === 'user' 
                      ? 'bg-gradient-primary text-primary-foreground border-0 shadow-md' 
                      : message.role === 'system'
                      ? 'bg-accent/10 border-accent/30 shadow-md'
                      : 'bg-card/95 backdrop-blur-sm border-border/50 shadow-lg'
                  } card-lift`}>
                    <CardContent className="pt-4 pb-4">
                      <div className={`prose prose-sm max-w-none ${message.role === 'user' ? 'prose-invert' : ''}`}>
                        {message.content.split('\n').map((line, i) => (
                          <p key={i} className="mb-2 last:mb-0 whitespace-pre-wrap font-sans leading-relaxed">{line}</p>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                  <span className="text-xs text-muted-foreground mt-1.5 font-sans">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>

                {message.role === 'user' && (
                  <Avatar className="w-10 h-10 border-2 border-primary/20 flex-shrink-0">
                    <AvatarFallback className="bg-muted text-muted-foreground font-semibold">U</AvatarFallback>
                  </Avatar>
                )}
              </div>
            ))}

            {/* Suggestions Display */}
            {currentSuggestions.length > 0 && (
              <div className="space-y-3 animate-slide-up">
                <h3 className="text-lg font-semibold text-foreground font-display flex items-center gap-2">
                  <Wand2 className="w-5 h-5 text-primary" />
                  AI-Generated Suggestions
                </h3>
                {currentSuggestions.map((suggestion, idx) => (
                  <Card 
                    key={suggestion.id} 
                    className={`border-border/50 shadow-md bg-card/95 backdrop-blur-sm card-lift ${
                      suggestion.status === 'accepted' ? 'border-green-500/50 bg-green-50/10' :
                      suggestion.status === 'rejected' ? 'opacity-50' : ''
                    }`}
                  >
                    <CardContent className="pt-4 pb-4">
                      <div className="flex items-start gap-3">
                        <div className="text-3xl flex-shrink-0">{getSuggestionIcon(suggestion.type)}</div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-2 mb-2">
                            <div className="flex-1">
                              <h4 className="font-semibold text-foreground font-display">{suggestion.title}</h4>
                              <Badge variant="secondary" className="mt-1 text-xs">{suggestion.type}</Badge>
                            </div>
                            {suggestion.status === 'pending' && (
                              <div className="flex gap-1">
                                <Button
                                  size="sm"
                                  onClick={() => handleSuggestionAccept(suggestion)}
                                  className="bg-green-500 hover:bg-green-600 text-white"
                                >
                                  <ThumbsUp className="w-4 h-4" />
                                </Button>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => handleSuggestionReject(suggestion)}
                                  className="border-destructive/50 text-destructive hover:bg-destructive/10"
                                >
                                  <ThumbsDown className="w-4 h-4" />
                                </Button>
                              </div>
                            )}
                            {suggestion.status === 'accepted' && (
                              <Badge className="bg-green-500/10 text-green-700 border-green-500/30">
                                <CheckCircle className="w-3 h-3 mr-1" />
                                Accepted
                              </Badge>
                            )}
                            {suggestion.status === 'rejected' && (
                              <Badge variant="secondary" className="bg-muted">
                                <XCircle className="w-3 h-3 mr-1" />
                                Rejected
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground mb-2 font-sans">{suggestion.description}</p>
                          <div className="bg-muted/30 rounded-lg p-3 mb-2">
                            <p className="text-sm text-foreground font-mono">{suggestion.content}</p>
                          </div>
                          <div className="flex items-center justify-between">
                            <p className="text-xs text-muted-foreground italic font-sans">💡 {suggestion.reasoning}</p>
                            <Badge variant="outline" className="text-xs">
                              {Math.round(suggestion.confidence_score * 100)}% confidence
                            </Badge>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}

            {/* Processing Indicator */}
            {(isProcessing || isAnalyzing) && (
              <div className="flex gap-3 justify-start animate-bounce-in">
                <Avatar className="w-10 h-10 border-2 border-primary/20">
                  <AvatarFallback className="bg-gradient-primary text-primary-foreground">
                    <Sparkles className="w-5 h-5" />
                  </AvatarFallback>
                </Avatar>
                <Card className="bg-card/95 backdrop-blur-sm border-border/50 shadow-lg">
                  <CardContent className="pt-4 pb-4">
                    <div className="flex items-center gap-2">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0s' }}></div>
                        <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                      </div>
                      <span className="text-sm text-muted-foreground font-sans">
                        {isAnalyzing ? 'Analyzing your video...' : 'Thinking...'}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <Card className="border-border/50 shadow-xl bg-card/95 backdrop-blur-sm sticky bottom-4 animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <CardContent className="pt-6">
              {/* Quick Prompts */}
              {messages.length <= 2 && !uploadedVideo && (
                <div className="mb-4">
                  <p className="text-sm text-muted-foreground mb-3 font-sans font-medium">Quick prompts:</p>
                  <div className="flex flex-wrap gap-2">
                    {quickPrompts.map((prompt, i) => (
                      <Button
                        key={i}
                        variant="outline"
                        size="sm"
                        onClick={() => handleQuickPrompt(prompt.text)}
                        className={`${prompt.color} hover:scale-105 transition-all duration-300 font-sans`}
                      >
                        {prompt.icon}
                        <span className="ml-1.5">{prompt.text}</span>
                      </Button>
                    ))}
                  </div>
                </div>
              )}

              {/* Text Input */}
              <div className="flex gap-2">
                <Textarea
                  ref={textareaRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={
                    uploadedVideo && currentSuggestions.length === 0
                      ? "Describe your content goals... (e.g., 'I'm building a language app for college students, targeting TikTok')"
                      : "Ask me anything about your content..."
                  }
                  className="min-h-[80px] resize-none focus:ring-primary font-sans text-base"
                  disabled={isProcessing || isAnalyzing || isUploading}
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={isProcessing || isAnalyzing || isUploading || !inputValue.trim()}
                  className="bg-gradient-primary hover:shadow-glow self-end px-5 h-[80px] transition-all duration-300"
                >
                  <Send className="w-5 h-5" />
                </Button>
              </div>

              <p className="text-xs text-muted-foreground mt-2 font-sans">
                {uploadedVideo && currentSuggestions.length === 0 ? (
                  <span className="flex items-center gap-1">
                    <Sparkles className="w-3 h-3" />
                    Describe your goals and press Enter to analyze your video with AI
                  </span>
                ) : (
                  <>
                    <kbd className="px-1.5 py-0.5 rounded bg-muted text-muted-foreground text-xs">Enter</kbd> to send, 
                    <kbd className="px-1.5 py-0.5 rounded bg-muted text-muted-foreground text-xs ml-1">Shift + Enter</kbd> for new line
                  </>
                )}
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
