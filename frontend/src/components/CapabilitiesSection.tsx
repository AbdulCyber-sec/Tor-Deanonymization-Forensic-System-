import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Zap, Shield, Database, BarChart3, FileText, Globe, Clock, CheckCircle2 } from "lucide-react";

export function CapabilitiesSection() {
  const capabilities = [
    {
      icon: Zap,
      title: "Real-Time Prediction",
      description: "2-5ms inference latency enables live TOR traffic monitoring",
      metrics: "312 predictions/second on single CPU core"
    },
    {
      icon: Database,
      title: "Automated Topology Mapping",
      description: "Continuous scraping of TOR relay consensus documents",
      metrics: "7,000+ relay support with hourly updates"
    },
    {
      icon: BarChart3,
      title: "Probabilistic Ranking",
      description: "Top-K predictions with confidence scores and probability distributions",
      metrics: "Narrows 500 guards → 5-10 suspects"
    },
    {
      icon: FileText,
      title: "Forensic Report Generation",
      description: "Exportable court-ready reports with prediction evidence",
      metrics: "PDF/JSON formats with digital signatures"
    },
    {
      icon: Globe,
      title: "Geographic Correlation",
      description: "Relay location analysis and country-level routing patterns",
      metrics: "180+ countries tracked"
    },
    {
      icon: Clock,
      title: "Historical Analysis",
      description: "Guard-exit pair frequency and temporal usage patterns",
      metrics: "50,000+ circuit database"
    },
    {
      icon: Shield,
      title: "Privacy-Compliant",
      description: "Uses only publicly available TOR relay metadata",
      metrics: "No encryption breaking or packet inspection"
    },
    {
      icon: CheckCircle2,
      title: "Explainable Predictions",
      description: "SHAP analysis reveals feature contributions for transparency",
      metrics: "Court-admissible evidence trail"
    }
  ];

  return (
    <div className="py-24 px-4 sm:px-6 lg:px-8 bg-surface-1">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <Badge className="mb-4" variant="outline">System Features</Badge>
          <h2 className="text-4xl font-bold mb-4">Core Capabilities</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Production-ready features designed for law enforcement investigative workflows
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {capabilities.map((capability, idx) => {
            const Icon = capability.icon;
            return (
              <Card key={idx} className="border-border hover:border-primary/50 transition-colors">
                <CardHeader>
                  <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 rounded-lg bg-primary/10">
                      <Icon className="w-5 h-5 text-primary" />
                    </div>
                  </div>
                  <CardTitle className="text-base">{capability.title}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    {capability.description}
                  </p>
                  <div className="text-xs font-mono text-primary pt-2 border-t border-border">
                    {capability.metrics}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        <Card className="mt-12 border-primary/30 bg-primary/5">
          <CardContent className="py-8">
            <div className="text-center space-y-4">
              <h3 className="text-2xl font-semibold">REST API Integration</h3>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                TGNP exposes a FastAPI-based REST endpoint for seamless integration with existing
                cybercrime monitoring systems, case management tools, and forensic analysis platforms.
              </p>
              <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
                <Badge variant="outline">OpenAPI 3.0</Badge>
                <Badge variant="outline">JSON/XML Output</Badge>
                <Badge variant="outline">OAuth2 Auth</Badge>
                <Badge variant="outline">Docker Ready</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
