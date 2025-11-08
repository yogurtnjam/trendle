import React from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { ArrowRight, Sparkles, Video, Wand2, Upload, TrendingUp, Target, Zap, MessageSquare, Check } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const LandingPage = () => {
  const navigate = useNavigate();

  const valueProps = [
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: 'Detect Formats',
      description: 'AI analyzes thousands of viral videos to identify trending content structures across platforms.',
      color: 'bg-primary',
      badge: '🔥 Hot'
    },
    {
      icon: <Wand2 className="w-6 h-6" />,
      title: 'Coach the Cut',
      description: 'Get real-time suggestions on hooks, beats, pacing, and captions to match what is working now.',
      color: 'bg-secondary',
      badge: '⚡ AI-Powered'
    },
    {
      icon: <Upload className="w-6 h-6" />,
      title: 'Export & Post',
      description: 'Format for TikTok, Instagram Reels, or YouTube Shorts with one click—captions, hashtags included.',
      color: 'bg-accent text-ink-black',
      badge: '✨ Magic'
    }
  ];

  const socialProof = [
    { name: 'TikTok', count: '2.3K', label: 'Creators' },
    { name: 'Instagram', count: '1.8K', label: 'Reels' },
    { name: 'YouTube', count: '956', label: 'Shorts' }
  ];

  const features = [
    'Trend intelligence updated daily',
    'Drag-and-drop beat builder',
    'AI-powered content coach',
    'Multi-platform export',
    'Caption & hashtag generator',
    'No watermarks'
  ];

  const handleGetStarted = () => {
    // Mock authentication check - in production, check if user is logged in
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    
    if (isLoggedIn) {
      navigate('/workspace');
    } else {
      navigate('/login');
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
        <div className="floating-sticker top-20 left-[10%] text-6xl animate-float" style={{ animationDelay: '0s' }}>✨</div>
        <div className="floating-sticker top-40 right-[15%] text-5xl animate-float" style={{ animationDelay: '1.5s' }}>🎬</div>
        <div className="floating-sticker bottom-40 left-[20%] text-5xl animate-float" style={{ animationDelay: '3s' }}>🚀</div>
        <div className="floating-sticker top-60 right-[25%] text-4xl animate-float" style={{ animationDelay: '2s' }}>💥</div>
        <div className="floating-sticker bottom-20 right-[10%] text-5xl animate-float" style={{ animationDelay: '2.5s' }}>⚡</div>
      </div>

      {/* Navigation */}
      <nav className="relative z-20 border-b border-border/50 bg-background/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-primary flex items-center justify-center">
                <Video className="w-6 h-6 text-primary-foreground" />
              </div>
              <span className="text-xl font-logo font-bold text-foreground">Trendle</span>
            </div>
            <div className="flex items-center gap-4">
              <Button variant="ghost" onClick={() => navigate('/login')} className="font-sans">
                Sign in
              </Button>
              <Button onClick={handleGetStarted} className="bg-gradient-primary hover:shadow-glow font-sans">
                Get Started
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-32">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left: Copy */}
          <div className="space-y-8 animate-slide-up">
            <Badge className="bg-accent/20 text-foreground border-accent/30 hover:bg-accent/30">
              <Sparkles className="w-3 h-3 mr-1" />
              Grammarly for Content Creators
            </Badge>
            
            <h1 className="text-6xl lg:text-7xl font-display font-bold leading-[1.1] text-foreground">
              Stop guessing.
              <br />
              <span className="marker-highlight">Go viral.</span>
            </h1>
            
            <p className="text-xl text-muted-foreground leading-relaxed max-w-xl font-sans">
              Get real-time feedback on your content based on actual trending formats we've indexed across TikTok, Instagram, and YouTube.
            </p>

            <div className="flex flex-wrap gap-4">
              <Button 
                size="lg" 
                onClick={handleGetStarted}
                className="bg-gradient-primary hover:shadow-glow text-lg h-14 px-8 font-sans font-semibold group"
              >
                Start Creating Free
                <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
              <Button 
                size="lg" 
                variant="outline"
                onClick={() => navigate('/login')}
                className="text-lg h-14 px-8 border-2 font-sans font-semibold"
              >
                Watch Demo
              </Button>
            </div>

            {/* Social Proof */}
            <div className="flex items-center gap-6 pt-4">
              {socialProof.map((item, i) => (
                <div key={i} className="text-center">
                  <div className="text-2xl font-bold text-foreground">{item.count}</div>
                  <div className="text-sm text-muted-foreground font-sans">{item.label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Right: Before/After Preview */}
          <div className="relative animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <div className="relative">
              {/* Before Frame */}
              <Card className="absolute top-0 left-0 w-64 transform -rotate-3 hover:rotate-0 transition-transform duration-300 card-lift z-10">
                <CardHeader className="pb-3">
                  <Badge variant="secondary" className="w-fit font-sans text-xs">Before</Badge>
                </CardHeader>
                <CardContent>
                  <div className="aspect-[9/16] bg-muted rounded-lg flex items-center justify-center relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-muted to-muted-foreground/10"></div>
                    <div className="relative text-center p-4">
                      <Video className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
                      <p className="text-sm text-muted-foreground font-sans">Generic content</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Arrow */}
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20">
                <div className="w-16 h-16 rounded-full bg-accent flex items-center justify-center animate-pulse-glow shadow-glow-neon">
                  <ArrowRight className="w-8 h-8 text-ink-black" />
                </div>
              </div>

              {/* After Frame */}
              <Card className="ml-auto w-64 transform rotate-3 hover:rotate-0 transition-transform duration-300 card-lift relative z-10" style={{ marginTop: '80px' }}>
                <CardHeader className="pb-3">
                  <Badge className="w-fit bg-primary text-primary-foreground font-sans text-xs">After</Badge>
                </CardHeader>
                <CardContent>
                  <div className="aspect-[9/16] bg-gradient-to-br from-primary/20 to-accent/20 rounded-lg flex items-center justify-center relative overflow-hidden border-2 border-primary/30">
                    <div className="absolute top-2 right-2">
                      <Badge className="bg-accent/90 text-ink-black border-0 font-sans text-xs">🔥 Trending</Badge>
                    </div>
                    <div className="text-center p-4">
                      <Sparkles className="w-12 h-12 text-primary mx-auto mb-2" />
                      <p className="text-sm font-semibold text-foreground font-sans">Viral-ready</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Value Props */}
      <section className="relative z-10 bg-background border-y border-border/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-display font-bold text-foreground mb-4">
              Your AI Content <span className="marker-highlight">Strategist</span>
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto font-sans">
              Stop guessing what works. Let AI analyze millions of videos and coach your content to match trending formats.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {valueProps.map((prop, i) => (
              <Card 
                key={i} 
                className="card-lift border-border/50 group relative overflow-hidden animate-slide-up"
                style={{ animationDelay: `${i * 0.1}s` }}
              >
                <CardHeader>
                  <div className="flex items-start justify-between mb-4">
                    <div className={`w-14 h-14 rounded-xl ${prop.color} flex items-center justify-center text-white shadow-md group-hover:scale-110 transition-transform`}>
                      {prop.icon}
                    </div>
                    <Badge variant="secondary" className="font-sans text-xs">{prop.badge}</Badge>
                  </div>
                  <CardTitle className="text-2xl font-display mb-2">{prop.title}</CardTitle>
                  <CardDescription className="text-base leading-relaxed font-sans">
                    {prop.description}
                  </CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Features List */}
      <section className="relative z-10 bg-gradient-sky">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <h2 className="text-4xl lg:text-5xl font-display font-bold text-foreground leading-tight">
                Everything you need to create <span className="marker-highlight">trending content</span>
              </h2>
              <p className="text-lg text-muted-foreground font-sans">
                Built for creators who want to move fast and stay ahead of trends.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {features.map((feature, i) => (
                <div 
                  key={i} 
                  className="flex items-center gap-3 p-4 bg-card rounded-xl border border-border/50 hover:border-primary/30 transition-colors animate-slide-up"
                  style={{ animationDelay: `${i * 0.05}s` }}
                >
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <Check className="w-5 h-5 text-primary" />
                  </div>
                  <span className="text-sm font-medium text-foreground font-sans">{feature}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 bg-foreground text-background">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-24 text-center">
          <h2 className="text-4xl lg:text-5xl font-display font-bold mb-6">
            Ready to go viral?
          </h2>
          <p className="text-xl opacity-90 mb-10 font-sans">
            Join thousands of creators using AI to make content that actually performs.
          </p>
          <Button 
            size="lg"
            onClick={handleGetStarted}
            className="bg-accent text-ink-black hover:bg-accent/90 text-lg h-14 px-10 font-sans font-semibold shadow-glow-neon group"
          >
            Get Early Access
            <Sparkles className="w-5 h-5 ml-2 group-hover:rotate-12 transition-transform" />
          </Button>
          <p className="text-sm opacity-70 mt-6 font-sans">No credit card required • Free forever plan</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-border/50 bg-background/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-primary flex items-center justify-center">
                <Video className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="text-lg font-display font-bold text-foreground">ContentFlow</span>
            </div>
            <div className="flex gap-6 text-sm text-muted-foreground font-sans">
              <button className="hover:text-foreground transition-colors">Privacy</button>
              <button className="hover:text-foreground transition-colors">Terms</button>
              <button className="hover:text-foreground transition-colors">Support</button>
            </div>
          </div>
          <div className="text-center text-sm text-muted-foreground mt-8 font-sans">
            © 2025 ContentFlow. Built for creators, by creators.
          </div>
        </div>
      </footer>
    </div>
  );
};