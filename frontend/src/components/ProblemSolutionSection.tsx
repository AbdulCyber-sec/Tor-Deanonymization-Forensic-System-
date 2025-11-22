import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { AlertCircle, CheckCircle2, Target, Zap } from "lucide-react";

export function ProblemSolutionSection() {
  return (
    <div className="py-24 px-4 sm:px-6 lg:px-8 bg-surface-1">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <Badge className="mb-4" variant="outline">The Challenge</Badge>
          <h2 className="text-4xl font-bold mb-4">TOR – Unveil: Peel the Onion</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Tracing TOR network users by correlating activity patterns and node data
            to identify probable origin IPs behind TOR-based traffic
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Problem Card */}
          <Card className="border-destructive/20">
            <CardHeader>
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="w-5 h-5 text-destructive" />
                <CardTitle className="text-destructive">The Problem</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">
                TOR provides strong anonymity through multi-layered encryption across guard,
                middle, and exit nodes. Law enforcement faces critical challenges:
              </p>
              
              <ul className="space-y-3">
                <li className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-destructive mt-2" />
                  <span className="text-sm">
                    <strong>500+ possible guard nodes</strong> for any exit activity
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-destructive mt-2" />
                  <span className="text-sm">
                    <strong>40-80 hours</strong> of manual analysis per case
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-destructive mt-2" />
                  <span className="text-sm">
                    Traditional methods: timing attacks, deep packet inspection (often <strong>impractical or illegal</strong>)
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-destructive mt-2" />
                  <span className="text-sm">
                    No actionable starting point for ISP cooperation or court orders
                  </span>
                </li>
              </ul>
            </CardContent>
          </Card>

          {/* Solution Card */}
          <Card className="border-primary/20">
            <CardHeader>
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle2 className="w-5 h-5 text-primary" />
                <CardTitle className="text-primary">Our Solution</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">
                TGNP uses machine learning to predict probable guard nodes based on
                publicly available relay metadata and traffic patterns:
              </p>
              
              <ul className="space-y-3">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">
                    <strong>Narrows search from 500 → 5-10</strong> high-probability guards
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">
                    <strong>Real-time predictions</strong> in 2-5 milliseconds
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">
                    <strong>Legally compliant:</strong> uses only public relay data
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">
                    <strong>45-55% real-world accuracy</strong> (250-300x better than random)
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                  <span className="text-sm">
                    <strong>Explainable predictions</strong> for court admissibility
                  </span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>

        {/* Key Innovation */}
        <Card className="mt-8 border-primary/30 bg-primary/5">
          <CardContent className="py-8">
            <div className="flex flex-col md:flex-row items-center gap-6">
              <div className="flex-shrink-0">
                <div className="p-4 rounded-xl bg-primary/10 border border-primary/20">
                  <Zap className="w-10 h-10 text-primary" />
                </div>
              </div>
              <div className="flex-1 text-center md:text-left">
                <h3 className="text-xl font-semibold mb-2">Paradigm Shift in TOR Investigation</h3>
                <p className="text-muted-foreground">
                  Instead of attempting deterministic tracing (breaking encryption), TGNP uses
                  <strong className="text-foreground"> probabilistic analysis</strong> of relay behavior patterns—providing
                  actionable investigative leads while respecting privacy boundaries.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Impact Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <div className="text-center">
            <Target className="w-8 h-8 text-primary mx-auto mb-3" />
            <div className="text-2xl font-bold mb-1">90% Reduction</div>
            <div className="text-sm text-muted-foreground">In suspect list size</div>
          </div>
          <div className="text-center">
            <CheckCircle2 className="w-8 h-8 text-primary mx-auto mb-3" />
            <div className="text-2xl font-bold mb-1">95% Faster</div>
            <div className="text-sm text-muted-foreground">Than manual analysis</div>
          </div>
          <div className="text-center">
            <Zap className="w-8 h-8 text-primary mx-auto mb-3" />
            <div className="text-2xl font-bold mb-1">80%+ Top-5</div>
            <div className="text-sm text-muted-foreground">Accuracy on real TOR</div>
          </div>
        </div>
      </div>
    </div>
  );
}
