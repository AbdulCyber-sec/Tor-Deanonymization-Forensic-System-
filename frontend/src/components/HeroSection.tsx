import { Button } from "../ui/button";
import { Shield, ArrowRight, Activity } from "lucide-react";

type Section = 
  | "hero"
  | "problem"
  | "methodology"
  | "dashboard"
  | "capabilities"
  | "validation"
  | "team";

interface HeroSectionProps {
  onNavigate: (section: Section) => void;
}

export function HeroSection({ onNavigate }: HeroSectionProps) {
  return (
    <div className="relative min-h-[90vh] flex items-center justify-center bg-gradient-to-b from-background to-surface-1 px-4">
      {/* Background grid pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_110%)] opacity-20" />
      
      <div className="relative max-w-5xl mx-auto text-center space-y-8">
        {/* Logo and Title */}
        <div className="flex items-center justify-center gap-4 mb-6">
          <div className="p-4 rounded-2xl bg-primary/10 border border-primary/20">
            <Shield className="w-16 h-16 text-primary" />
          </div>
        </div>

        <div className="space-y-4">
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight">
            TOR Guard Node
            <br />
            <span className="text-primary">Prediction System</span>
          </h1>
          
          <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto">
            AI-powered investigative intelligence for law enforcement and cybercrime investigators
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto pt-8">
          <div className="p-6 rounded-lg bg-card border border-border">
            <div className="text-3xl font-bold text-primary mb-2">99.79%</div>
            <div className="text-sm text-muted-foreground">Top-1 Accuracy</div>
          </div>
          <div className="p-6 rounded-lg bg-card border border-border">
            <div className="text-3xl font-bold text-primary mb-2">2-5ms</div>
            <div className="text-sm text-muted-foreground">Prediction Latency</div>
          </div>
          <div className="p-6 rounded-lg bg-card border border-border">
            <div className="text-3xl font-bold text-primary mb-2">500+</div>
            <div className="text-sm text-muted-foreground">Guard Nodes Tracked</div>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-8">
          <Button
            size="lg"
            onClick={() => onNavigate("dashboard")}
            className="gap-2 text-lg px-8"
          >
            <Activity className="w-5 h-5" />
            Try Live Dashboard
            <ArrowRight className="w-5 h-5" />
          </Button>
          
          <Button
            size="lg"
            variant="outline"
            onClick={() => onNavigate("methodology")}
            className="text-lg px-8"
          >
            Learn How It Works
          </Button>
        </div>

        {/* Trust Badge */}
        <div className="pt-12">
          <p className="text-sm text-muted-foreground mb-4">
            Built for TN Police Hackathon 2025
          </p>
          <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
            <Shield className="w-4 h-4" />
            <span>Operates on publicly available data • Privacy-compliant • Court-admissible</span>
          </div>
        </div>
      </div>
    </div>
  );
}
