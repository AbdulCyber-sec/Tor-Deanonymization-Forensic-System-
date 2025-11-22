import { Card, CardContent } from "../ui/card";
import { Badge } from "../ui/badge";
import { Shield, Users, Mail } from "lucide-react";

export function TeamSection() {
  return (
    <div className="py-24 px-4 sm:px-6 lg:px-8 bg-surface-1">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-16">
          <Badge className="mb-4" variant="outline">About Us</Badge>
          <h2 className="text-4xl font-bold mb-4">Team & Contact</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Built for TN Police Hackathon 2025 – TOR Unveil: Peel the Onion
          </p>
        </div>

        <Card className="mb-8">
          <CardContent className="py-8 space-y-6">
            <div className="flex items-start gap-4">
              <div className="p-3 rounded-lg bg-primary/10 flex-shrink-0">
                <Shield className="w-6 h-6 text-primary" />
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-semibold mb-2">Project Mission</h3>
                <p className="text-muted-foreground">
                  Provide Tamil Nadu Police Cyber Crime Wing with a modern, data-driven tool
                  that enhances both proactive monitoring and post-incident investigation of
                  TOR network abuse. TGNP bridges the gap between TOR's privacy protections
                  and legitimate law enforcement needs through ethical, legally-compliant
                  machine learning.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="p-3 rounded-lg bg-primary/10 flex-shrink-0">
                <Users className="w-6 h-6 text-primary" />
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-semibold mb-2">Team Commitment</h3>
                <ul className="text-sm text-muted-foreground space-y-2">
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                    <span>Live demonstration of working prototype with web interface</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                    <span>Complete source code under open-source license (if selected)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                    <span>3 months free technical support post-deployment</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                    <span>Hands-on training sessions for cyber crime wing officers</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                    <span>Comprehensive documentation (user manual, API docs, deployment guide)</span>
                  </li>
                </ul>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="p-3 rounded-lg bg-primary/10 flex-shrink-0">
                <Mail className="w-6 h-6 text-primary" />
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-semibold mb-2">Contact Information</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  For technical queries, collaboration opportunities, or demo requests:
                </p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">Email:</span>
                    <span className="font-mono">tgnp-team@hackathon2025.in</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">Project:</span>
                    <span>TN Police Hackathon 2025</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">Category:</span>
                    <span>TOR – Unveil: Peel the Onion</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-primary/30 bg-primary/5">
          <CardContent className="py-6">
            <div className="text-center space-y-2">
              <p className="text-sm font-semibold">Ethical Stance</p>
              <p className="text-sm text-muted-foreground max-w-2xl mx-auto">
                This system operates exclusively on publicly available data and does not break
                encryption, violate privacy laws, or interfere with TOR's legitimate anonymity
                use cases. TGNP provides investigative leads, not conclusive evidence—standard
                legal procedures (warrants, ISP cooperation) are still required.
              </p>
            </div>
          </CardContent>
        </Card>

        <div className="text-center mt-8 text-sm text-muted-foreground">
          <p>© 2025 TGNP System. For law enforcement and authorized investigative use only.</p>
          <p className="mt-2">Document Version 1.0 • Last Updated: November 2025</p>
        </div>
      </div>
    </div>
  );
}
