import React from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { ArrowRight, Sparkles, Video, Wand2, Upload, TrendingUp, Target, Zap, MessageSquare, Check, Scissors, Film } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const LandingPage = () => {
  const navigate = useNavigate();

  const valueProps = [
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: 'Detect Viral Patterns',
      description: 'AI analyzes thousands of viral videos to understand exactly what makes content explode across platforms.',
      color: 'bg-primary',
      badge: '🔥 Real-Time'
    },
    {
      icon: <Scissors className="w-6 h-6" />,
      title: 'Direct Every Cut',
      description: 'Get step-by-step coaching on hooks, pacing, transitions, and creative decisions as you build your video.',
      color: 'bg-secondary',
      badge: '⚡ AI Director'
    },
    {
      icon: <Film className="w-6 h-6" />,
      title: 'Coach to Viral',
      description: 'From first frame to final export, our AI guides your creative process to match proven viral formulas.',
      color: 'bg-accent text-ink-black',
      badge: '✨ Step-by-Step'
    }
  ];

  const socialProof = [
    { name: 'TikTok', count: '2.3K', label: 'Creators' },
    { name: 'Instagram', count: '1.8K', label: 'Reels' },
    { name: 'YouTube', count: '956', label: 'Shorts' }
  ];

  const features = [
    'AI-directed shot decisions',
    'Real-time creative coaching',
    'Viral format templates',
    'Multi-platform optimization',
    'Caption & hashtag generation',
    'Step-by-step guidance'
  ];

  const handleGetStarted = () => {
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
              <span className="text-5xl font-logo font-bold text-foreground">Trendle</span>
            </div>
            <div className="flex items-center gap-4">
              <button onClick={handleGetStarted} className="font-sans text-base hover:opacity-80 transition-opacity">
                <span className="marker-highlight-small">Try Now</span>
              </button>
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
              AI Director for Content Creators
            </Badge>
            
            <h1 className="text-6xl lg:text-7xl font-display font-bold leading-[1.1] text-foreground">
              Stop guessing.
              <br />
              <span className="marker-highlight">Go viral.</span>
            </h1>
            
            <p className="text-xl text-muted-foreground leading-relaxed max-w-xl font-sans">
              AI that doesn't just analyze—it directs. Get coached through every cut, transition, and creative decision based on proven viral formats.
            </p>

            <div className="flex flex-wrap gap-4">
              <button 
                onClick={handleGetStarted}
                className="px-8 py-4 rounded-xl bg-card border-2 border-border hover:border-primary/50 transition-all duration-300 shadow-md hover:shadow-lg group"
              >
                <span className="marker-highlight-small text-foreground">Start Creating Free</span>
              </button>
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
                      <p className="text-sm text-muted-foreground font-sans">Guessing</p>
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
                      <Badge className="bg-accent/90 text-ink-black border-0 font-sans text-xs">🔥 Viral</Badge>
                    </div>
                    <div className="text-center p-4">
                      <Sparkles className="w-12 h-12 text-primary mx-auto mb-2" />
                      <p className="text-sm font-semibold text-foreground font-sans">AI-Directed</p>
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
              Your AI Content <span className="marker-highlight">Director</span>
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto font-sans">
              Stop guessing. Let AI direct your content creation—from first shot to final cut—based on millions of viral videos.
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
                AI that <span className="marker-highlight">directs</span> your creative process
              </h2>
              <p className="text-lg text-muted-foreground font-sans">
                Every cut, every transition, every creative decision—coached by AI that knows what works.
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
            Ready for AI direction?
          </h2>
          <p className="text-xl opacity-90 mb-10 font-sans">
            Join thousands of creators who stopped guessing and started making viral content with AI coaching.
          </p>
          <button 
            onClick={handleGetStarted}
            className="px-10 py-4 rounded-xl bg-card border-2 border-border hover:border-primary/50 transition-all duration-300 shadow-lg hover:shadow-xl group"
          >
            <span className="marker-highlight-small text-foreground text-lg">Start Creating Now</span>
          </button>
          <p className="text-sm opacity-70 mt-6 font-sans">No credit card required • Free forever plan</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-border/50 bg-background/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-5xl font-logo font-bold text-foreground">Trendle</span>
            </div>
            <div className="flex gap-6 text-sm text-muted-foreground font-sans">
              <button className="hover:text-foreground transition-colors">Privacy</button>
              <button className="hover:text-foreground transition-colors">Terms</button>
              <button className="hover:text-foreground transition-colors">Support</button>
            </div>
          </div>
          <div className="text-center text-sm text-muted-foreground mt-8 font-sans">
            © 2025 Trendle. Built for creators, by creators.
          </div>
        </div>
      </footer>
    </div>
  );
};