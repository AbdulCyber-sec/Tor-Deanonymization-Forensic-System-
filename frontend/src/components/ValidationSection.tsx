import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Progress } from "../ui/progress";
import { TrendingUp, Target, BarChart3 } from "lucide-react";

export function ValidationSection() {
  const testMetrics = [
    { name: "Top-1 Accuracy", value: 99.79, color: "text-green-500" },
    { name: "Top-3 Accuracy", value: 100.0, color: "text-green-500" },
    { name: "Top-5 Accuracy", value: 100.0, color: "text-green-500" },
    { name: "Top-10 Accuracy", value: 100.0, color: "text-green-500" },
  ];

  const topFeatures = [
    { name: "Guard Average Bandwidth", importance: 22.84 },
    { name: "Guard Bandwidth", importance: 22.44 },
    { name: "Guard Usage Frequency", importance: 21.29 },
    { name: "Guard Country (Encoded)", importance: 15.87 },
    { name: "Minimum Bandwidth", importance: 4.64 },
  ];

  return (
    <div className="py-24 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <Badge className="mb-4" variant="outline">Performance</Badge>
          <h2 className="text-4xl font-bold mb-4">Validation Results</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Tested on 3,750 holdout circuits with stratified sampling
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Accuracy Metrics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5 text-primary" />
                Test Set Accuracy
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {testMetrics.map((metric, idx) => (
                <div key={idx} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">{metric.name}</span>
                    <span className={`font-bold ${metric.color}`}>
                      {metric.value.toFixed(2)}%
                    </span>
                  </div>
                  <Progress value={metric.value} className="h-2" />
                </div>
              ))}

              <div className="pt-4 border-t border-border space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Mean Reciprocal Rank (MRR@50)</span>
                  <span className="font-bold text-primary">0.9989</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Average Prediction Time</span>
                  <span className="font-mono">3.2ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">95th Percentile</span>
                  <span className="font-mono">4.8ms</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Feature Importance */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-primary" />
                Top Feature Importance
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {topFeatures.map((feature, idx) => (
                <div key={idx} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">{feature.name}</span>
                    <span className="text-primary font-bold">{feature.importance}%</span>
                  </div>
                  <Progress value={feature.importance * 4.5} className="h-2" />
                </div>
              ))}

              <div className="pt-4 border-t border-border">
                <p className="text-xs text-muted-foreground">
                  Top 3 features account for <strong className="text-foreground">66.57%</strong> of
                  predictive power, showing strong signal in bandwidth and usage patterns.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Real-World Expectations */}
        <Card className="mt-8 border-yellow-500/30 bg-yellow-500/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-yellow-500" />
              Real-World Performance Expectations
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              While simulated data achieves near-perfect accuracy, real TOR network deployment
              will face inherent randomness. Expected performance with live data:
            </p>

            <div className="grid md:grid-cols-3 gap-4">
              <div className="p-4 border border-border rounded-lg text-center">
                <div className="text-2xl font-bold text-yellow-500 mb-1">45-55%</div>
                <div className="text-sm text-muted-foreground">Top-1 Accuracy</div>
                <div className="text-xs text-muted-foreground mt-1">(250-300x better than random)</div>
              </div>
              <div className="p-4 border border-border rounded-lg text-center">
                <div className="text-2xl font-bold text-green-500 mb-1">79-87%</div>
                <div className="text-sm text-muted-foreground">Top-5 Accuracy</div>
                <div className="text-xs text-muted-foreground mt-1">(Narrows to 5 suspects)</div>
              </div>
              <div className="p-4 border border-border rounded-lg text-center">
                <div className="text-2xl font-bold text-green-500 mb-1">88-93%</div>
                <div className="text-sm text-muted-foreground">Top-10 Accuracy</div>
                <div className="text-xs text-muted-foreground mt-1">(Covers 90%+ cases)</div>
              </div>
            </div>

            <div className="bg-muted/30 p-4 rounded-lg border border-border">
              <h4 className="font-semibold mb-2 text-sm">Why Accuracy Drops (50-60% ceiling)</h4>
              <ul className="text-xs text-muted-foreground space-y-1">
                <li>• TOR's intentional randomness in guard selection (privacy-by-design)</li>
                <li>• Limited observable features (no packet contents or timing attacks)</li>
                <li>• Many-to-one problem: 500 guards route to same exit simultaneously</li>
                <li>• Class imbalance: top 10 guards = 35-40% traffic, bottom 200 = 5-8%</li>
                <li>• Bandwidth variation: ±20% minute-to-minute fluctuations</li>
              </ul>
            </div>

            <div className="text-center pt-4">
              <p className="text-sm text-muted-foreground">
                <strong className="text-foreground">50-60% is exceptional</strong> for an anonymity network
                designed to prevent tracing. Still provides 10x investigative value by narrowing suspects.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
