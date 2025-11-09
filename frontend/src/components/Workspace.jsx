import React, { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Sparkles, Upload, X, Send, Video, Image as ImageIcon, FileText, Paperclip, TrendingUp, Wand2, Zap, Rocket, Target } from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

export const Workspace = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hey there! 👋 I\'m your AI content strategist. Upload a video or image, tell me what you\'re creating, and I\'ll help you make it go viral.',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const quickPrompts = [
    { icon: <TrendingUp className="w-4 h-4" />, text: 'Analyze trending formats', color: 'bg-primary/10 text-primary border-primary/20' },
    { icon: <Wand2 className="w-4 h-4" />, text: 'Suggest hooks for this video', color: 'bg-secondary/10 text-secondary border-secondary/20' },
    { icon: <Zap className="w-4 h-4" />, text: 'Generate captions & hashtags', color: 'bg-accent/20 text-foreground border-accent/30' },
  ];

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files || []);
    handleFiles(files);
  };

  const handleFiles = (files) => {
    const validFiles = files.filter(file => {
      const isImage = file.type.startsWith('image/');
      const isVideo = file.type.startsWith('video/');
      return isImage || isVideo;
    });

    if (validFiles.length === 0) {
      toast.error('Please upload images or videos only');
      return;
    }

    const newFiles = validFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      name: file.name,
      type: file.type.startsWith('image/') ? 'image' : 'video',
      size: (file.size / 1024 / 1024).toFixed(2),
      url: URL.createObjectURL(file)
    }));

    setUploadedFiles(prev => [...prev, ...newFiles]);
    toast.success(`${newFiles.length} file(s) uploaded! 🎉`);
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
    handleFiles(files);
  };

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
    toast.success('File removed');
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() && uploadedFiles.length === 0) {
      toast.error('Please add a message or upload files');
      return;
    }

    const userMessage = {
      role: 'user',
      content: inputValue.trim(),
      files: uploadedFiles,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setUploadedFiles([]);
    setIsProcessing(true);

    // Mock AI response
    setTimeout(() => {
      const aiResponse = generateMockResponse(userMessage);
      setMessages(prev => [...prev, aiResponse]);
      setIsProcessing(false);
      toast.success('Analysis complete! 🎯', { description: 'Check out my suggestions below.' });
    }, 2000);
  };

  const generateMockResponse = (userMessage) => {
    const hasVideo = userMessage.files?.some(f => f.type === 'video');
    const hasImage = userMessage.files?.some(f => f.type === 'image');

    let response = '';

    if (hasVideo) {
      response = `🎬 **Video Analysis Complete!**\n\nI've analyzed your video against trending formats. Here's what I found:\n\n**📊 Trending Format Match: "Hook + Problem + Solution"**\n- Shelf-life: 🔥 2-3 weeks\n- Best for: TikTok, Instagram Reels\n\n**💡 Suggestions:**\n1. **Hook (0-3s):** Start with "I built X so you don't have to..." - this format is performing 3x better right now\n2. **B-roll timing:** Add cuts every 2-3 seconds to maintain attention\n3. **Caption placement:** Keep text in the center-top third\n\n**✨ Recommended Captions:**\n"POV: You found the hack everyone's been hiding"\n"This changed everything for me"\n\n**#️⃣ Hot Hashtags:**\n#contentcreator #viral #trending #tutorial\n\nWant me to generate a full script or export this for multiple platforms?`;
    } else if (hasImage) {
      response = `🖼️ **Image Analysis Complete!**\n\nGreat visual! Here's how to maximize engagement:\n\n**🎯 Content Strategy:**\n- This works best as a carousel post or Reels cover\n- Add text overlay with a hook question\n- Use bold, contrasting colors\n\n**💬 Caption Hooks:**\n1. "Stop scrolling. You need to see this."\n2. "Everyone's doing X wrong. Here's why."\n3. "This one trick changed my [niche]..."\n\n**📱 Platform Recommendations:**\n- Instagram: Carousel (swipe engagement +45%)\n- TikTok: Use as thumbnail with voiceover\n- YouTube Shorts: Combine with quick cuts\n\nReady to create the full post?`;
    } else {
      response = `👋 I'm ready to help! Here's what I can do:\n\n**🎯 Content Analysis:**\n- Analyze your videos against trending formats\n- Suggest hooks, beats, and pacing improvements\n- Generate captions and hashtags\n\n**💡 Trending Formats Right Now:**\n1. **"Episode 1 of X"** - Building series momentum (🔥 Hot)\n2. **"POV: "** - Relatable situations (⚡ Trending)\n3. **"I tested X so you don't have to"** - Tutorial style (✨ Rising)\n\n**📤 What I Need:**\nUpload a video or image, and tell me:\n- What platform you're targeting\n- Your niche/audience\n- What you want to achieve\n\nLet's make content that performs!`;
    }

    return {
      role: 'assistant',
      content: response,
      timestamp: new Date()
    };
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
                    Upload your content and I'll analyze it against trending formats, suggest improvements, and help you create viral-ready posts.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Chat Messages */}
          <div className="space-y-4 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            {messages.map((message, index) => (
              <div key={index} className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {message.role === 'assistant' && (
                  <Avatar className="w-10 h-10 border-2 border-primary/20 flex-shrink-0">
                    <AvatarFallback className="bg-gradient-primary text-primary-foreground">
                      <Sparkles className="w-5 h-5" />
                    </AvatarFallback>
                  </Avatar>
                )}
                
                <div className={`flex-1 max-w-3xl ${ message.role === 'user' ? 'flex flex-col items-end' : ''}`}>
                  <Card className={`${
                    message.role === 'user' 
                      ? 'bg-gradient-primary text-primary-foreground border-0 shadow-md' 
                      : 'bg-card/95 backdrop-blur-sm border-border/50 shadow-lg'
                  } card-lift`}>
                    <CardContent className="pt-4 pb-4">
                      {/* Uploaded Files */}
                      {message.files && message.files.length > 0 && (
                        <div className="mb-3 grid grid-cols-2 gap-2">
                          {message.files.map(file => (
                            <div key={file.id} className="relative rounded-lg overflow-hidden bg-muted/20 border border-border/30">
                              {file.type === 'image' ? (
                                <img src={file.url} alt={file.name} className="w-full h-32 object-cover" />
                              ) : (
                                <video src={file.url} className="w-full h-32 object-cover" />
                              )}
                              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-2">
                                <p className="text-xs text-white font-medium truncate">{file.name}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {/* Message Content */}
                      <div className={`prose prose-sm max-w-none ${
                        message.role === 'user' ? 'prose-invert' : ''
                      }`}>
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

            {/* Processing Indicator */}
            {isProcessing && (
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
                      <span className="text-sm text-muted-foreground font-sans">Analyzing your content...</span>
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
              {messages.length <= 2 && (
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

              {/* File Upload Area */}
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`mb-4 border-2 border-dashed rounded-xl p-6 transition-all duration-300 ${
                  isDragging 
                    ? 'border-primary bg-primary/5 scale-[1.01] shadow-glow' 
                    : 'border-border/50 hover:border-border hover:bg-muted/20'
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept="image/*,video/*"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                
                {uploadedFiles.length === 0 ? (
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full flex flex-col items-center justify-center gap-2 group"
                  >
                    <div className="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-all duration-300 group-hover:scale-110">
                      <Upload className="w-7 h-7 text-primary" />
                    </div>
                    <div className="text-center">
                      <p className="text-sm font-semibold text-foreground font-sans">Drop files here or click to browse</p>
                      <p className="text-xs text-muted-foreground mt-1 font-sans">Supports images and videos • Max 50MB</p>
                    </div>
                  </button>
                ) : (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between mb-3">
                      <p className="text-sm font-semibold text-foreground font-sans flex items-center gap-2">
                        <Badge variant="secondary" className="font-sans">{uploadedFiles.length}</Badge>
                        file(s) uploaded
                      </p>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => fileInputRef.current?.click()}
                        className="font-sans hover:bg-primary/10"
                      >
                        <Paperclip className="w-4 h-4 mr-1" />
                        Add more
                      </Button>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                      {uploadedFiles.map(file => (
                        <div key={file.id} className="relative group rounded-lg overflow-hidden border border-border/50 card-lift">
                          {file.type === 'image' ? (
                            <img src={file.url} alt={file.name} className="w-full h-24 object-cover" />
                          ) : (
                            <div className="w-full h-24 bg-muted flex items-center justify-center">
                              <Video className="w-8 h-8 text-muted-foreground" />
                            </div>
                          )}
                          <button
                            onClick={() => removeFile(file.id)}
                            className="absolute top-1 right-1 w-6 h-6 rounded-full bg-destructive text-destructive-foreground opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center hover:scale-110"
                          >
                            <X className="w-4 h-4" />
                          </button>
                          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-1.5">
                            <p className="text-xs text-white font-medium truncate">{file.name}</p>
                            <p className="text-xs text-white/70">{file.size} MB</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Text Input */}
              <div className="flex gap-2">
                <Textarea
                  ref={textareaRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Tell me what you want to create... (e.g., 'I'm 21, building a language app, need TikTok content ideas')"
                  className="min-h-[80px] resize-none focus:ring-primary font-sans text-base"
                  disabled={isProcessing}
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={isProcessing || (!inputValue.trim() && uploadedFiles.length === 0)}
                  className="bg-gradient-primary hover:shadow-glow self-end px-5 h-[80px] transition-all duration-300"
                >
                  <Send className="w-5 h-5" />
                </Button>
              </div>

              <p className="text-xs text-muted-foreground mt-2 font-sans">
                <kbd className="px-1.5 py-0.5 rounded bg-muted text-muted-foreground text-xs">Enter</kbd> to send, <kbd className="px-1.5 py-0.5 rounded bg-muted text-muted-foreground text-xs">Shift + Enter</kbd> for new line
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};