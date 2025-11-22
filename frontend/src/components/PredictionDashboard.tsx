import { useState } from "react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";
import { Alert, AlertDescription } from "../ui/alert";
import { Badge } from "../ui/badge";
import { Progress } from "../ui/progress";
import { Skeleton } from "../ui/skeleton";
import { 
  Activity, 
  AlertCircle, 
  CheckCircle2, 
  Download, 
  Loader2, 
  Shield, 
  TrendingUp,
  Globe,
  BarChart3,
  Network
} from "lucide-react";
import TopologyGraph from "./TopologyGraph";
import GeographicMap from "./GeographicMap";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "../ui/chart";
import {
  BarChart as ReBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  LabelList
} from "recharts";

interface PredictionResult {
  guard_fingerprint: string;
  guard_nickname: string;
  guard_address: string;
  guard_country: string;
  confidence: number;
  rank: number;
}

interface ExplainabilityData {
  top_features: Array<{
    feature: string;
    importance: number;
    value: any;
    impact: string;
  }>;
  shap_values?: any;
}

interface PredictionResponse {
  predictions: PredictionResult[];
  prediction_time_ms: number;
  model_version: string;
  explainability?: ExplainabilityData;
}

export function PredictionDashboard() {
  const [exitFingerprint, setExitFingerprint] = useState("");
  const [exitCountry, setExitCountry] = useState("");
  const [bandwidth, setBandwidth] = useState("");
  const [setupTime, setSetupTime] = useState("");
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch("http://localhost:8000/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          exit_fingerprint: exitFingerprint,
          exit_country: exitCountry,
          bandwidth: parseFloat(bandwidth) || 0,
          setup_time: parseFloat(setupTime) || 0,
        }),
      });

      if (!response.ok) {
        throw new Error(`Prediction failed: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "An error occurred during prediction");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    if (!result) return;
    
    const exportData = {
      timestamp: new Date().toISOString(),
      input: {
        exit_fingerprint: exitFingerprint,
        exit_country: exitCountry,
        bandwidth,
        setup_time: setupTime,
      },
      predictions: result.predictions,
      metadata: {
        model_version: result.model_version,
        prediction_time_ms: result.prediction_time_ms,
      },
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `tgnp-prediction-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.7) return "text-green-500";
    if (confidence >= 0.5) return "text-yellow-500";
    return "text-red-500";
  };

  const getConfidenceBadge = (confidence: number) => {
    if (confidence >= 0.7) return "bg-green-500/10 text-green-500";
    if (confidence >= 0.5) return "bg-yellow-500/10 text-yellow-500";
    return "bg-red-500/10 text-red-500";
  };

  return (
    <div className="min-h-screen bg-background py-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Activity className="w-10 h-10 text-primary" />
            <h1 className="text-4xl font-bold">Live Prediction Dashboard</h1>
          </div>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Input TOR exit event metadata to receive ranked guard node predictions
            with confidence scores in real-time (2–5ms latency).
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Form */}
          <Card className="lg:sticky lg:top-20 h-fit">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Exit Event Input
              </CardTitle>
              <CardDescription>
                Enter observed TOR exit node information from your monitoring system
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="exit-fingerprint">
                  Exit Node Fingerprint *
                </Label>
                <Input
                  id="exit-fingerprint"
                  placeholder="A2B5C7D9E1F3..."
                  value={exitFingerprint}
                  onChange={(e) => setExitFingerprint(e.target.value)}
                  className="font-mono"
                />
                <p className="text-xs text-muted-foreground">
                  40-character hexadecimal TOR relay fingerprint
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="exit-country">Exit Node Country *</Label>
                <Input
                  id="exit-country"
                  placeholder="Germany"
                  value={exitCountry}
                  onChange={(e) => setExitCountry(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="bandwidth">Observed Bandwidth (MB/s)</Label>
                <Input
                  id="bandwidth"
                  type="number"
                  step="0.1"
                  placeholder="7.5"
                  value={bandwidth}
                  onChange={(e) => setBandwidth(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="setup-time">Circuit Setup Time (seconds)</Label>
                <Input
                  id="setup-time"
                  type="number"
                  step="0.1"
                  placeholder="2.3"
                  value={setupTime}
                  onChange={(e) => setSetupTime(e.target.value)}
                />
              </div>

              <Button
                onClick={handlePredict}
                disabled={loading || !exitFingerprint || !exitCountry}
                className="w-full"
                size="lg"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Predicting...
                  </>
                ) : (
                  <>
                    <TrendingUp className="w-4 h-4 mr-2" />
                    Predict Guard Nodes
                  </>
                )}
              </Button>

              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="w-4 h-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Results Panel */}
          <div className="space-y-6">
            {loading && (
              <Card>
                <CardHeader>
                  <Skeleton className="h-6 w-48" />
                  <Skeleton className="h-4 w-64" />
                </CardHeader>
                <CardContent className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-24 w-full" />
                  ))}
                </CardContent>
              </Card>
            )}

            {result && !loading && (
              <>
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center gap-2">
                        <CheckCircle2 className="w-5 h-5 text-green-500" />
                        Prediction Complete
                      </CardTitle>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleExport}
                        className="gap-2"
                      >
                        <Download className="w-4 h-4" />
                        Export Report
                      </Button>
                    </div>
                    <CardDescription>
                      Processed in {result.prediction_time_ms}ms • Model v{result.model_version}
                    </CardDescription>
                  </CardHeader>
                </Card>

                <Tabs defaultValue="predictions" className="w-full">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="predictions">
                      Top Predictions
                    </TabsTrigger>
                    <TabsTrigger value="explainability">
                      Why These Guards?
                    </TabsTrigger>
                    <TabsTrigger value="visualizations">
                      Visualizations
                    </TabsTrigger>
                  </TabsList>

                  <TabsContent value="predictions" className="space-y-4">
                    {result.predictions.map((pred, idx) => (
                      <Card key={idx} className="border-l-4" style={{
                        borderLeftColor: idx === 0 ? 'hsl(var(--primary))' : 'hsl(var(--border))'
                      }}>
                        <CardHeader className="pb-3">
                          <div className="flex items-start justify-between">
                            <div className="space-y-1">
                              <div className="flex items-center gap-2">
                                <Badge variant="outline">Rank #{pred.rank}</Badge>
                                <Badge className={getConfidenceBadge(pred.confidence)}>
                                  {(pred.confidence * 100).toFixed(1)}% Confidence
                                </Badge>
                              </div>
                              <CardTitle className="text-lg font-mono">
                                {pred.guard_nickname}
                              </CardTitle>
                            </div>
                            <Globe className="w-5 h-5 text-muted-foreground" />
                          </div>
                        </CardHeader>
                        <CardContent className="space-y-3">
                          <div className="space-y-2">
                            <div className="flex items-center justify-between text-sm">
                              <span className="text-muted-foreground">Confidence</span>
                              <span className={getConfidenceColor(pred.confidence)}>
                                {(pred.confidence * 100).toFixed(1)}%
                              </span>
                            </div>
                            <Progress 
                              value={pred.confidence * 100} 
                              className="h-2"
                            />
                          </div>

                          <div className="grid grid-cols-2 gap-4 text-sm pt-2 border-t">
                            <div>
                              <p className="text-muted-foreground">Fingerprint</p>
                              <p className="font-mono text-xs break-all">
                                {pred.guard_fingerprint}
                              </p>
                            </div>
                            <div>
                              <p className="text-muted-foreground">Country</p>
                              <p className="font-medium">{pred.guard_country}</p>
                            </div>
                            <div className="col-span-2">
                              <p className="text-muted-foreground">IP Address</p>
                              <p className="font-mono">{pred.guard_address}</p>
                            </div>
                          </div>

                          <div className="flex gap-2 pt-2">
                            <Button variant="outline" size="sm" className="flex-1">
                              ISP Lookup
                            </Button>
                            <Button variant="outline" size="sm" className="flex-1">
                              Court Order Template
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </TabsContent>

                  <TabsContent value="explainability" className="space-y-4">
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <BarChart3 className="w-5 h-5" />
                          Feature Importance Analysis
                        </CardTitle>
                        <CardDescription>
                          Key factors that influenced the top prediction
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        {result.explainability?.top_features ? (
                          <div className="space-y-4">
                            {result.explainability.top_features.map((feature, idx) => (
                              <div key={idx} className="space-y-2">
                                <div className="flex items-center justify-between text-sm">
                                  <span className="font-medium">{feature.feature}</span>
                                  <Badge variant="outline" className="text-xs">
                                    {feature.impact}
                                  </Badge>
                                </div>
                                <div className="flex items-center gap-3">
                                  <Progress 
                                    value={feature.importance * 100} 
                                    className="h-2 flex-1"
                                  />
                                  <span className="text-xs text-muted-foreground w-12">
                                    {(feature.importance * 100).toFixed(0)}%
                                  </span>
                                </div>
                                <p className="text-xs text-muted-foreground">
                                  Value: {typeof feature.value === 'number' 
                                    ? feature.value.toFixed(2) 
                                    : String(feature.value)}
                                </p>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-sm text-muted-foreground">
                            Explainability data will be available in the next update.
                            The model uses 50 engineered features including bandwidth ratios,
                            geographic patterns, and historical co-occurrence frequencies.
                          </p>
                        )}
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="visualizations" className="space-y-6">
                    <div className="grid gap-6 lg:grid-cols-2">
                      <Card>
                        <CardHeader>
                          <CardTitle className="flex items-center gap-2 text-lg font-semibold">
                            <TrendingUp className="w-5 h-5 text-primary" /> Confidence Distribution
                          </CardTitle>
                          <CardDescription>Relative confidence for each ranked guard</CardDescription>
                        </CardHeader>
                        <CardContent>
                          {result?.predictions?.length ? (
                            <ChartContainer
                              config={result.predictions.reduce((acc, p) => {
                                acc[p.guard_fingerprint] = { label: `#${p.rank}` };
                                return acc;
                              }, {} as Record<string, { label: string }>)}
                              className="w-full h-64"
                            >
                              <ResponsiveContainer>
                                <ReBarChart data={result.predictions}>
                                  <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.15} />
                                  <XAxis
                                    dataKey="rank"
                                    tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                                  />
                                  <YAxis
                                    domain={[0, 1]}
                                    tickFormatter={(v: number) => `${Math.round(v * 100)}%`}
                                    tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                                  />
                                  <Bar
                                    dataKey="confidence"
                                    fill="hsl(var(--primary))"
                                    radius={[4, 4, 0, 0]}
                                  >
                                    <LabelList
                                      dataKey="confidence"
                                      position="top"
                                      formatter={(v: number) => `${(v * 100).toFixed(1)}%`}
                                      className="text-xs fill-foreground"
                                    />
                                  </Bar>
                                  <ChartTooltip content={<ChartTooltipContent hideLabel />} />
                                </ReBarChart>
                              </ResponsiveContainer>
                            </ChartContainer>
                          ) : (
                            <div className="text-center py-8 text-muted-foreground">Run a prediction to view confidence chart.</div>
                          )}
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader>
                          <CardTitle className="flex items-center gap-2 text-lg font-semibold">
                            <BarChart3 className="w-5 h-5 text-primary" /> Feature Importance Chart
                          </CardTitle>
                          <CardDescription>Visualization of top contributing features</CardDescription>
                        </CardHeader>
                        <CardContent>
                          {result?.explainability?.top_features?.length ? (
                            <ChartContainer
                              config={result.explainability.top_features.reduce((acc, f) => {
                                acc[f.feature] = { label: f.feature };
                                return acc;
                              }, {} as Record<string, { label: string }>)}
                              className="w-full h-64"
                            >
                              <ResponsiveContainer>
                                <ReBarChart
                                  data={result.explainability.top_features.map(f => ({
                                    feature: f.feature,
                                    importance: Number((f.importance * 100).toFixed(2)),
                                  }))}
                                  layout="vertical"
                                >
                                  <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.15} />
                                  <XAxis type="number" domain={[0, 100]} tickFormatter={(v: number) => `${v}%`} tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} />
                                  <YAxis dataKey="feature" type="category" width={120} tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} />
                                  <Bar dataKey="importance" fill="hsl(var(--accent))" radius={[0, 4, 4, 0]}> 
                                    <LabelList dataKey="importance" position="right" formatter={(v: number) => `${v}%`} className="text-xs fill-foreground" />
                                  </Bar>
                                  <ChartTooltip content={<ChartTooltipContent hideLabel />} />
                                </ReBarChart>
                              </ResponsiveContainer>
                            </ChartContainer>
                          ) : (
                            <div className="text-center py-8 text-muted-foreground">Run a prediction to view feature importance chart.</div>
                          )}
                        </CardContent>
                      </Card>
                    </div>

                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-lg font-semibold">
                          <Activity className="w-5 h-5 text-primary" /> Accuracy Metrics Snapshot
                        </CardTitle>
                        <CardDescription>Model test vs real-world expected performance</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                          {[
                            { label: "Test Top-1", value: 99.79 },
                            { label: "Real Top-1", value: 55 },
                            { label: "Real Top-5", value: 87 },
                            { label: "Real Top-10", value: 93 },
                          ].map((m, i) => (
                            <div key={i} className="space-y-2 p-3 rounded-lg border border-border/40 bg-card/50">
                              <div className="flex justify-between text-xs font-medium">
                                <span>{m.label}</span>
                                <span>{m.value}%</span>
                              </div>
                              <Progress value={m.value} className="h-2" />
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>

                    <div className="grid gap-6 lg:grid-cols-2">
                      <Card>
                        <CardHeader>
                          <CardTitle className="flex items-center gap-2 text-lg font-semibold">
                            <Network className="w-5 h-5 text-primary" /> Relay Topology
                          </CardTitle>
                          <CardDescription>Synthetic guard→middle→exit interaction graph</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="py-2">
                            {/* Topology Graph Component */}
                            <TopologyGraph limit={42} />
                          </div>
                        </CardContent>
                      </Card>

                      <GeographicMap />
                    </div>
                  </TabsContent>
                </Tabs>
              </>
            )}

            {!loading && !result && !error && (
              <Card className="border-dashed">
                <CardContent className="flex flex-col items-center justify-center py-16">
                  <Activity className="w-16 h-16 text-muted-foreground mb-4" />
                  <p className="text-lg font-medium mb-2">Ready for Prediction</p>
                  <p className="text-sm text-muted-foreground text-center max-w-sm">
                    Fill out the exit event form and click "Predict Guard Nodes"
                    to see real-time predictions with confidence scores.
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
