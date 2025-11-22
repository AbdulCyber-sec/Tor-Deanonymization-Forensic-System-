import { useEffect, useState, useCallback } from 'react';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { Activity, RefreshCcw } from 'lucide-react';
import { Button } from '../ui/button';
import { Skeleton } from '../ui/skeleton';
import * as d3 from 'd3';

interface TopologyNode {
  id: string;
  fingerprint: string;
  nickname: string;
  role: 'guard' | 'middle' | 'exit';
  country: string;
  bandwidth: number;
  degree: number;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

interface TopologyLink {
  source: string;
  target: string;
  circuit_weight: number;
  latency_ms: number;
}

interface TopologyResponse {
  generated_at: string;
  node_count: number;
  link_count: number;
  nodes: TopologyNode[];
  links: TopologyLink[];
  note: string;
}

const ROLE_COLOR: Record<string, string> = {
  guard: 'hsl(var(--primary))',
  middle: 'hsl(var(--accent))',
  exit: 'hsl(var(--warning))'
};

const ROLE_SIZE: Record<string, number> = {
  guard: 18,
  middle: 12,
  exit: 16
};

export function TopologyGraph({ limit = 40 }: { limit?: number }) {
  const [data, setData] = useState<TopologyResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`http://localhost:8000/api/topology?limit=${limit}`);
      if (!res.ok) throw new Error(await res.text());
      const json = await res.json();
      setData(json);
    } catch (e: any) {
      setError(e.message || 'Failed to load topology');
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => { fetchData(); }, [fetchData, refreshKey]);

  // Pre-compute static layout using d3-force (no ongoing animation for performance)
  const [layoutNodes, setLayoutNodes] = useState<TopologyNode[]>([]);
  const [layoutLinks, setLayoutLinks] = useState<{ source: TopologyNode; target: TopologyNode; }[]>([]);

  useEffect(() => {
    if (!data) return;
    // Clone nodes to avoid mutating original state
    const simNodes: TopologyNode[] = data.nodes.map(n => ({ ...n }));
    // Map node id to reference
    const nodeMap: Record<string, TopologyNode> = Object.fromEntries(simNodes.map(n => [n.id, n]));
    const simLinks = data.links.map(l => ({ source: nodeMap[l.source], target: nodeMap[l.target] }));

    const simulation = d3.forceSimulation(simNodes as any)
      .force('link', d3.forceLink(simLinks as any).id((d: any) => d.id).distance(90).strength(0.5))
      .force('charge', d3.forceManyBody().strength(-220))
      .force('center', d3.forceCenter(350 / 2, 300 / 2))
      .stop();

    // Run fixed number of ticks synchronously
    for (let i = 0; i < 180; i++) simulation.tick();

    setLayoutNodes(simNodes);
    setLayoutLinks(simLinks);
  }, [data]);

  return (
    <Card className="border border-border/50">
      <CardContent className="pt-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-primary" />
            <span className="font-semibold text-sm">Relay Topology Graph</span>
            {data && (
              <Badge variant="outline" className="text-xs">{data.node_count} nodes</Badge>
            )}
          </div>
          <Button variant="outline" size="sm" onClick={() => setRefreshKey(k => k + 1)} className="gap-1">
            <RefreshCcw className="w-3 h-3" /> Refresh
          </Button>
        </div>
        {loading && (
          <div className="space-y-2">
            <Skeleton className="h-6 w-40" />
            <Skeleton className="h-[300px] w-full" />
          </div>
        )}
        {error && (
          <div className="text-sm text-red-500">{error}</div>
        )}
        {!loading && data && (
          <div className="space-y-3">
            <svg width={350} height={300} className="w-full h-[300px] bg-card/30 border border-border/40 rounded-md">
              {/* Links */}
              <g stroke="hsl(var(--border))" strokeOpacity={0.4} strokeWidth={1}>
                {layoutLinks.map((l, i) => (
                  <line
                    key={i}
                    x1={l.source.x}
                    y1={l.source.y}
                    x2={l.target.x}
                    y2={l.target.y}
                  />
                ))}
              </g>
              {/* Nodes */}
              <g>
                {layoutNodes.map(n => (
                  <g key={n.id}>
                    <circle
                      cx={n.x}
                      cy={n.y}
                      r={ROLE_SIZE[n.role]}
                      fill={ROLE_COLOR[n.role]}
                      fillOpacity={0.85}
                      stroke="hsl(var(--background))"
                      strokeWidth={1.5}
                    />
                    <text
                      x={n.x ?? 0}
                      y={(n.y ?? 0) + ROLE_SIZE[n.role] + 10}
                      textAnchor="middle"
                      className="text-[10px] font-medium"
                      fill="hsl(var(--foreground))"
                    >
                      {n.nickname}
                    </text>
                  </g>
                ))}
              </g>
            </svg>
            <div className="flex flex-wrap gap-3 text-xs">
              <div className="flex items-center gap-1">
                <span className="inline-block w-3 h-3 rounded-sm" style={{ background: ROLE_COLOR.guard }} /> Guard
              </div>
              <div className="flex items-center gap-1">
                <span className="inline-block w-3 h-3 rounded-sm" style={{ background: ROLE_COLOR.middle }} /> Middle
              </div>
              <div className="flex items-center gap-1">
                <span className="inline-block w-3 h-3 rounded-sm" style={{ background: ROLE_COLOR.exit }} /> Exit
              </div>
              <div className="text-muted-foreground">Static layout • synthetic demo</div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default TopologyGraph;
