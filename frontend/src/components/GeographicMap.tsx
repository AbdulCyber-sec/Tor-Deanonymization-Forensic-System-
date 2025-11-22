import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Badge } from '../ui/badge';
import { Globe, Loader2 } from 'lucide-react';
import 'leaflet/dist/leaflet.css';

interface RelayLocation {
  fingerprint: string;
  nickname: string;
  role: 'guard' | 'middle' | 'exit';
  country: string;
  lat: number;
  lng: number;
  bandwidth: number;
}

// Country coordinates mapping (capitals for demo)
const COUNTRY_COORDS: Record<string, [number, number]> = {
  US: [38.9072, -77.0369],
  DE: [52.5200, 13.4050],
  FR: [48.8566, 2.3522],
  GB: [51.5074, -0.1278],
  NL: [52.3676, 4.9041],
  CA: [45.4215, -75.6972],
  SE: [59.3293, 18.0686],
  NO: [59.9139, 10.7522],
  CH: [46.9481, 7.4474],
  JP: [35.6762, 139.6503],
};

const ROLE_COLOR: Record<string, string> = {
  guard: '#00bcd4',
  middle: '#8b5cf6',
  exit: '#f59e0b',
};

function MapUpdater({ locations }: { locations: RelayLocation[] }) {
  const map = useMap();
  
  useEffect(() => {
    if (locations.length > 0) {
      const bounds = locations.map(l => [l.lat, l.lng] as [number, number]);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [locations, map]);

  return null;
}

export function GeographicMap() {
  const [locations, setLocations] = useState<RelayLocation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch topology data and convert to geographic coordinates
    const fetchLocations = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/topology?limit=50');
        if (!res.ok) throw new Error('Failed to fetch topology');
        const data = await res.json();

        // Map nodes to geographic locations
        const geoLocations: RelayLocation[] = data.nodes
          .filter((n: any) => COUNTRY_COORDS[n.country])
          .map((n: any) => {
            const [lat, lng] = COUNTRY_COORDS[n.country];
            // Add small random offset to prevent exact overlap
            const jitter = () => (Math.random() - 0.5) * 0.5;
            return {
              fingerprint: n.fingerprint,
              nickname: n.nickname,
              role: n.role,
              country: n.country,
              lat: lat + jitter(),
              lng: lng + jitter(),
              bandwidth: n.bandwidth,
            };
          });

        setLocations(geoLocations);
      } catch (e) {
        console.error('Failed to load geographic data:', e);
      } finally {
        setLoading(false);
      }
    };

    fetchLocations();
  }, []);

  return (
    <Card className="border border-border/50">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg font-semibold">
          <Globe className="w-5 h-5 text-primary" /> Geographic Relay Distribution
        </CardTitle>
        <CardDescription>
          {loading ? 'Loading relay locations...' : `${locations.length} relay nodes mapped globally`}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="h-[400px] flex items-center justify-center">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : (
          <div className="space-y-3">
            <div className="h-[400px] rounded-lg overflow-hidden border border-border/40">
              <MapContainer
                center={[30, 0]}
                zoom={2}
                style={{ height: '100%', width: '100%' }}
                scrollWheelZoom={false}
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  className="map-tiles"
                />
                <MapUpdater locations={locations} />
                {locations.map((loc, idx) => (
                  <CircleMarker
                    key={idx}
                    center={[loc.lat, loc.lng]}
                    radius={8}
                    pathOptions={{
                      fillColor: ROLE_COLOR[loc.role],
                      fillOpacity: 0.7,
                      color: '#fff',
                      weight: 2,
                    }}
                  >
                    <Popup>
                      <div className="text-sm space-y-1 min-w-[180px]">
                        <div className="font-semibold">{loc.nickname}</div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-xs">
                            {loc.role}
                          </Badge>
                          <span className="text-xs text-gray-600">{loc.country}</span>
                        </div>
                        <div className="text-xs text-gray-500">
                          Bandwidth: {loc.bandwidth.toFixed(1)} MB/s
                        </div>
                        <div className="text-xs text-gray-400 font-mono break-all">
                          {loc.fingerprint.slice(0, 16)}...
                        </div>
                      </div>
                    </Popup>
                  </CircleMarker>
                ))}
              </MapContainer>
            </div>
            <div className="flex flex-wrap gap-3 text-xs">
              <div className="flex items-center gap-1">
                <span
                  className="inline-block w-3 h-3 rounded-full"
                  style={{ background: ROLE_COLOR.guard }}
                />{' '}
                Guard Nodes
              </div>
              <div className="flex items-center gap-1">
                <span
                  className="inline-block w-3 h-3 rounded-full"
                  style={{ background: ROLE_COLOR.middle }}
                />{' '}
                Middle Nodes
              </div>
              <div className="flex items-center gap-1">
                <span
                  className="inline-block w-3 h-3 rounded-full"
                  style={{ background: ROLE_COLOR.exit }}
                />{' '}
                Exit Nodes
              </div>
              <div className="text-muted-foreground ml-auto">Click markers for details</div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default GeographicMap;
