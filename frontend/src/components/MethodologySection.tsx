import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";
import { Badge } from "../ui/badge";
import { Database, GitBranch, Cpu, BarChart3 } from "lucide-react";

export function MethodologySection() {
  return (
    <div className="py-24 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <Badge className="mb-4" variant="outline">How It Works</Badge>
          <h2 className="text-4xl font-bold mb-4">Methodology</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Combining automated data collection, advanced feature engineering,
            and machine-learning-driven prediction
          </p>
        </div>

        <Tabs defaultValue="data" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="data">Data Collection</TabsTrigger>
            <TabsTrigger value="features">Feature Engineering</TabsTrigger>
            <TabsTrigger value="model">ML Architecture</TabsTrigger>
            <TabsTrigger value="prediction">Prediction Process</TabsTrigger>
          </TabsList>

          <TabsContent value="data" className="mt-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="w-5 h-5 text-primary" />
                  Automated TOR Data Collection
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <h4 className="font-semibold">Public Data Sources</h4>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2" />
                        TOR relay descriptors (fingerprints, bandwidth, flags)
                      </li>
                      <li className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2" />
                        Consensus documents (updated hourly)
                      </li>
                      <li className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2" />
                        Geographic metadata (country, network)
                      </li>
                      <li className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2" />
                        Historical uptime and bandwidth statistics
                      </li>
                    </ul>
                  </div>
                  
                  <div className="space-y-3">
                    <h4 className="font-semibold">Circuit Observation</h4>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2" />
                        Exit node activity monitoring (with legal authorization)
                      </li>
                      <li className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2" />
                        Circuit timing and bandwidth measurements
                      </li>
                      <li className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2" />
                        Stream counts and connection metadata
                      </li>
                      <li className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2" />
                        Real-time relay status updates
                      </li>
                    </ul>
                  </div>
                </div>

                <div className="bg-muted/30 p-4 rounded-lg border border-border">
                  <p className="text-sm text-muted-foreground">
                    <strong className="text-foreground">Legal Compliance:</strong> All data
                    collection uses publicly available TOR relay information and lawfully
                    monitored exit node activity—no encryption breaking or privacy violations.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="features" className="mt-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <GitBranch className="w-5 h-5 text-primary" />
                  Feature Engineering Pipeline
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <p className="text-muted-foreground">
                  Transforms 23 raw TOR attributes into <strong className="text-foreground">50 analytical features</strong> that
                  capture network behavior patterns
                </p>

                <div className="grid md:grid-cols-3 gap-4">
                  <div className="p-4 border border-border rounded-lg">
                    <div className="text-primary font-semibold mb-2">Bandwidth Features (7)</div>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Guard/middle/exit ratios</li>
                      <li>• Total circuit bandwidth</li>
                      <li>• Min/max/std statistics</li>
                    </ul>
                  </div>

                  <div className="p-4 border border-border rounded-lg">
                    <div className="text-primary font-semibold mb-2">Geographic Features (5)</div>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Same-country flags</li>
                      <li>• Country diversity score</li>
                      <li>• Five Eyes detection</li>
                    </ul>
                  </div>

                  <div className="p-4 border border-border rounded-lg">
                    <div className="text-primary font-semibold mb-2">Historical Features (8)</div>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Usage frequencies</li>
                      <li>• Guard-exit pair patterns</li>
                      <li>• Country preferences</li>
                    </ul>
                  </div>

                  <div className="p-4 border border-border rounded-lg">
                    <div className="text-primary font-semibold mb-2">Encoded Features (5)</div>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Fingerprint encoding</li>
                      <li>• Country encoding</li>
                      <li>• Consistent mappings</li>
                    </ul>
                  </div>

                  <div className="p-4 border border-border rounded-lg">
                    <div className="text-primary font-semibold mb-2">Interaction Features (2)</div>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Bandwidth × setup time</li>
                      <li>• Total BW × bytes</li>
                    </ul>
                  </div>

                  <div className="p-4 border border-border rounded-lg bg-primary/5">
                    <div className="text-primary font-semibold mb-2">Target Variable</div>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Guard node label (0-499)</li>
                      <li>• Multi-class prediction</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="model" className="mt-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Cpu className="w-5 h-5 text-primary" />
                  Machine Learning Architecture
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold mb-2">XGBoost Classifier</h4>
                      <p className="text-sm text-muted-foreground">
                        Gradient boosting algorithm optimized for multi-class classification
                        with 500 guard node classes
                      </p>
                    </div>

                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between border-b border-border pb-1">
                        <span className="text-muted-foreground">Max Depth</span>
                        <span className="font-mono">10</span>
                      </div>
                      <div className="flex justify-between border-b border-border pb-1">
                        <span className="text-muted-foreground">Learning Rate</span>
                        <span className="font-mono">0.1</span>
                      </div>
                      <div className="flex justify-between border-b border-border pb-1">
                        <span className="text-muted-foreground">N Estimators</span>
                        <span className="font-mono">300</span>
                      </div>
                      <div className="flex justify-between border-b border-border pb-1">
                        <span className="text-muted-foreground">Subsample</span>
                        <span className="font-mono">0.8</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Objective</span>
                        <span className="font-mono text-xs">multi:softprob</span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold mb-2">Training Strategy</h4>
                      <ul className="text-sm text-muted-foreground space-y-2">
                        <li className="flex items-start gap-2">
                          <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2" />
                          70/15/15 stratified train/val/test split
                        </li>
                        <li className="flex items-start gap-2">
                          <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2" />
                          Early stopping (20 rounds) to prevent overfitting
                        </li>
                        <li className="flex items-start gap-2">
                          <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2" />
                          Balanced class distribution maintained
                        </li>
                        <li className="flex items-start gap-2">
                          <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2" />
                          Trained on 25,000 simulated circuits
                        </li>
                      </ul>
                    </div>

                    <div className="bg-primary/5 p-4 rounded-lg border border-primary/20">
                      <h4 className="font-semibold mb-2 text-sm">Why XGBoost?</h4>
                      <ul className="text-xs text-muted-foreground space-y-1">
                        <li>✓ Handles class imbalance naturally</li>
                        <li>✓ Resistant to overfitting</li>
                        <li>✓ Fast inference (2-5ms)</li>
                        <li>✓ Probability outputs for ranking</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="prediction" className="mt-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-primary" />
                  Real-Time Prediction Process
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="flex items-start gap-4">
                    <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/10 text-primary font-bold flex-shrink-0">
                      1
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold mb-1">Exit Event Input</h4>
                      <p className="text-sm text-muted-foreground">
                        Investigator provides exit node fingerprint, country, bandwidth,
                        and timing metadata from monitoring systems
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-4">
                    <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/10 text-primary font-bold flex-shrink-0">
                      2
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold mb-1">Feature Extraction</h4>
                      <p className="text-sm text-muted-foreground">
                        System generates 50 engineered features including bandwidth ratios,
                        geographic patterns, historical frequencies, and interaction metrics
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-4">
                    <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/10 text-primary font-bold flex-shrink-0">
                      3
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold mb-1">Model Inference</h4>
                      <p className="text-sm text-muted-foreground">
                        XGBoost model processes feature vector and outputs probability
                        distribution across all 500 guard nodes (2-5ms latency)
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-4">
                    <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/10 text-primary font-bold flex-shrink-0">
                      4
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold mb-1">Ranked Output</h4>
                      <p className="text-sm text-muted-foreground">
                        Top-K guard nodes returned with confidence scores, fingerprints,
                        IP addresses, and feature importance explanations
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-4">
                    <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/10 text-primary font-bold flex-shrink-0">
                      5
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold mb-1">Investigative Action</h4>
                      <p className="text-sm text-muted-foreground">
                        Investigators use top predictions to request ISP logs, prepare
                        court orders, and focus resources on high-probability suspects
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
