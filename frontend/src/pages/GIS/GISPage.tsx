import React, { useState, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { MapPin, Layers, RefreshCw, AlertOctagon, ShieldAlert, Activity, Radio, Building2, Cpu, Triangle, AlertTriangle, Users, Bus, AlertCircle } from 'lucide-react';
import {
  MapContainer, TileLayer, CircleMarker, Marker, Popup,
  Tooltip as MapTooltip, Polygon, Polyline, useMap
} from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { apiClient } from '../../services/api/apiClient';
import { Node, SensorReading } from '../../types';
import { Link, useSearchParams } from 'react-router-dom';

// ──────────────────── Mine Working Panel Centre ──────────────────────────
// Cluster 11 & Cluster 7 (BCCL) Coal Mines, Jharia Coalfield
const MINE_CENTER: [number, number] = [23.7695, 86.4045];

// Underground Coal Working Panel Boundary (Cluster 11 Panel Alpha)
const MINE_PANEL_POLYGON: [number, number][] = [
  [23.7718, 86.4020],
  [23.7718, 86.4078],
  [23.7672, 86.4078],
  [23.7672, 86.4020],
];

// ──────────────────── Custom Leaflet DivIcons ─────────────────────────────
function makeDivIcon(html: string, className = '') {
  return L.divIcon({ html, className, iconSize: undefined, iconAnchor: [0, 0] });
}

const MineSiteIcon = makeDivIcon(`
  <div style="position:relative;width:34px;height:34px;transform:translate(-17px,-17px)">
    <div style="position:absolute;inset:0;border-radius:50%;background:#d97706;opacity:0.25;animation:ping 1.5s cubic-bezier(0,0,0.2,1) infinite"></div>
    <div style="position:absolute;inset:3px;border-radius:50%;background:#f59e0b;border:2px solid #92400e;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 6px rgba(0,0,0,0.25)">
      <span style="font-size:12px">⛏️</span>
    </div>
  </div>
`);

const GatewayIcon = makeDivIcon(`
  <div style="position:relative;width:30px;height:30px;transform:translate(-15px,-15px)">
    <div style="width:30px;height:30px;background:#4f46e5;border:2px solid #312e81;border-radius:6px;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 6px rgba(0,0,0,0.25)">
      <span style="font-size:13px">📡</span>
    </div>
  </div>
`);

function makePublicInfraIcon(assetType: string, isAffected: boolean, criticality: string) {
  const emojiMap: Record<string, string> = {
    HIGHWAY: '🛣️',
    RESIDENTIAL_AREA: '🏘️',
    WATER_SUPPLY: '🚰',
    RAILWAY: '🚆',
    POWER_GRID: '⚡',
    HOSPITAL: '🏥',
    SCHOOL: '🏫',
    BRIDGE: '🌉',
    COMMERCIAL_AREA: '🏪',
    MAIN_ENTRANCE: '🚧',
    TUNNEL: '🕳️',
    OTHER: '🏛️',
  };
  const emoji = emojiMap[assetType] || '🏛️';
  const border = isAffected ? '#dc2626' : (criticality === 'CRITICAL' ? '#ea580c' : '#0284c7');
  const bg = isAffected ? '#fef2f2' : '#ffffff';
  const animation = isAffected ? 'animation: pulse 1s infinite;' : '';

  return makeDivIcon(`
    <div style="transform:translate(-16px,-16px);width:32px;height:32px;background:${bg};border:2px solid ${border};border-radius:8px;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(0,0,0,0.2);${animation}">
      <span style="font-size:14px">${emoji}</span>
    </div>
  `);
}

// ──────────────────── Map Recenter ────────────────────────────────────────
const MapRecenter: React.FC<{ center: [number, number]; zoom?: number }> = ({ center, zoom = 16 }) => {
  const map = useMap();
  useEffect(() => { map.setView(center, zoom); }, [center, zoom, map]);
  return null;
};

// ──────────────────── Node color ─────────────────────────────────────────
function getNodeColor(node: any): string {
  const level = node.risk_level || 'NORMAL';
  if (level === 'CRITICAL') return '#ef4444';
  if (level === 'HIGH')     return '#f97316';
  if (level === 'MODERATE') return '#eab308';
  return '#22c55e';
}

function assetTypeLabel(t: string): string {
  const map: Record<string, string> = {
    HIGHWAY: 'National Highway',
    RESIDENTIAL_AREA: 'Residential Colony',
    WATER_SUPPLY: 'Potable Water Pipeline',
    RAILWAY: 'Railway Track / Freight Siding',
    POWER_GRID: 'Public Power Substation',
    HOSPITAL: 'Community Hospital',
    SCHOOL: 'School Campus',
    BRIDGE: 'Road Overbridge',
    COMMERCIAL_AREA: 'Market / Commercial Bazaar',
    MAIN_ENTRANCE: 'Mine Access Portal',
    TUNNEL: 'Underground Drift',
  };
  return map[t] || t;
}

function impactBadgeClass(level: string): string {
  if (level === 'CRITICAL') return 'bg-red-100 text-red-800 border border-red-300';
  if (level === 'HIGH')     return 'bg-orange-100 text-orange-800 border border-orange-200';
  if (level === 'MEDIUM')   return 'bg-amber-100 text-amber-800 border border-amber-200';
  return 'bg-blue-50 text-blue-700 border border-blue-200';
}

export const GISPage: React.FC = () => {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const focusNodeId = searchParams.get('focus');

  const [nodes, setNodes] = useState<Node[]>([]);
  const [telemetryMap, setTelemetryMap] = useState<Record<string, SensorReading>>({});
  const [spatialAnalysis, setSpatialAnalysis] = useState<any>(null);
  const [mineSite, setMineSite] = useState<any>(null);
  const [gatewayData, setGatewayData] = useState<any>(null);
  const [infrastructure, setInfrastructure] = useState<any[]>([]);
  const [impactData, setImpactData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'map' | 'impact'>('map');

  const fetchGISData = async () => {
    try {
      setLoading(true);
      const [nodesRes, telRes, spatialRes, mineRes, gwRes, infraRes, impactRes] = await Promise.all([
        apiClient.get('/nodes'),
        apiClient.get('/telemetry?limit=50'),
        apiClient.get('/ai/spatial-analysis').catch(() => ({ data: null })),
        apiClient.get('/infrastructure/gis/site').catch(() => ({ data: null })),
        apiClient.get('/infrastructure/gis/gateway').catch(() => ({ data: null })),
        apiClient.get('/infrastructure/gis/infrastructure').catch(() => ({ data: { features: [] } })),
        apiClient.get('/infrastructure/gis/impact').catch(() => ({ data: null })),
      ]);

      const fetchedNodes: Node[] = nodesRes.data || [];
      setNodes(fetchedNodes);

      const telObj: Record<string, SensorReading> = {};
      if (Array.isArray(telRes.data)) {
        telRes.data.forEach((r: SensorReading) => {
          const key = (r as any).node_id || (r as any).node_code;
          if (key && !telObj[key]) telObj[key] = r;
        });
      }
      setTelemetryMap(telObj);
      setSpatialAnalysis(spatialRes.data);
      setMineSite(mineRes.data);
      setGatewayData(gwRes.data);
      setInfrastructure(infraRes.data?.features || []);
      setImpactData(impactRes.data);
    } catch (err) {
      console.error('GIS fetch error', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchGISData(); }, []);

  const impactPolygons = useMemo(() => {
    if (!spatialAnalysis?.active_impact_zones?.length) return [];
    return spatialAnalysis.active_impact_zones.map((zone: any, idx: number) => {
      const poly = zone.zone_polygon;
      if (!poly?.coordinates?.[0]) return null;
      const positions: [number, number][] = poly.coordinates[0].map((c: number[]) => [c[1], c[0]]);
      return { ...zone, positions, id: idx };
    }).filter(Boolean);
  }, [spatialAnalysis]);

  const correlationLines = useMemo(() => {
    if (!spatialAnalysis?.correlation_edges?.length) return [];
    const nodeMap: Record<string, Node> = {};
    nodes.forEach(n => { nodeMap[n.node_id || ''] = n; });
    return spatialAnalysis.correlation_edges.map((edge: any, idx: number) => {
      const src = nodeMap[edge.source];
      const tgt = nodeMap[edge.target];
      if (!src?.latitude || !tgt?.latitude) return null;
      return {
        id: idx,
        positions: [[src.latitude, src.longitude], [tgt.latitude, tgt.longitude]] as [number, number][],
        ...edge,
      };
    }).filter(Boolean);
  }, [spatialAnalysis, nodes]);

  const mapCenter: [number, number] = useMemo(() => {
    if (focusNodeId) {
      const focused = nodes.find(n => n.node_id === focusNodeId || n.node_code === focusNodeId);
      if (focused?.latitude && focused?.longitude) return [Number(focused.latitude), Number(focused.longitude)];
    }
    return MINE_CENTER;
  }, [focusNodeId, nodes]);

  const evacuationActive = spatialAnalysis?.evacuation_active || impactData?.evacuation_recommended;
  const affectedInfra: any[] = impactData?.affected_infrastructure || [];

  return (
    <div className="space-y-5 max-w-full overflow-x-hidden">
      {/* Evacuation Alert Banner */}
      {evacuationActive && (
        <div className="bg-red-50 border-2 border-red-500 rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-lg animate-in fade-in-50">
          <div className="flex items-start gap-3">
            <AlertOctagon className="h-7 w-7 text-red-600 shrink-0 mt-0.5 animate-pulse" />
            <div>
              <div className="text-sm font-black text-red-900 uppercase tracking-wide flex items-center gap-2">
                <span>🚨 PUBLIC SAFETY & INFRASTRUCTURE EVACUATION ADVISORY</span>
                <span className="px-2 py-0.5 rounded bg-red-600 text-white text-[10px] font-extrabold">DGMS LEVEL 3</span>
              </div>
              <p className="text-xs text-red-800 mt-1 font-semibold leading-relaxed">
                {impactData?.recommendation || 'Underground strata subsidence detected. Public infrastructure along highway and residential perimeter requires immediate precaution/evacuation.'}
              </p>
              {affectedInfra.length > 0 && (
                <div className="mt-2 text-[11px] font-bold text-red-900 bg-white/80 p-2 rounded-xl border border-red-200">
                  Threatened Public Assets: {affectedInfra.map(a => `${a.name} (${a.distance_from_zone_center_m || a.distance_m}m)`).join(' • ')}
                </div>
              )}
            </div>
          </div>
          <Link to="/app/alerts" className="px-4 py-2.5 bg-red-600 text-white hover:bg-red-700 text-xs font-bold rounded-xl whitespace-nowrap self-start sm:self-auto transition shadow-sm flex items-center gap-1.5 shrink-0">
            View Active Alarms →
          </Link>
        </div>
      )}

      {/* Header */}
      <div className="bg-white rounded-2xl p-4 sm:p-6 border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="p-3 bg-blue-50 text-blue-700 rounded-xl">
            <MapPin className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-lg sm:text-xl font-bold text-slate-900">GIS Spatial Mine Monitoring & Public Infrastructure Impact</h1>
            <p className="text-xs text-slate-500 mt-0.5">Cluster 11 & 7 (BCCL) Coal Mines • Jharia Coalfield • PostGIS WGS84</p>
          </div>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {focusNodeId && (
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-amber-50 border border-amber-200 text-xs font-mono text-amber-800">
              <span className="h-2 w-2 rounded-full bg-amber-500 animate-ping" />
              <span>Focused: {focusNodeId}</span>
            </div>
          )}
          <button onClick={fetchGISData} className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl transition flex items-center gap-2">
            <RefreshCw className={loading ? 'h-3.5 w-3.5 animate-spin' : 'h-3.5 w-3.5'} /> {t('common.refresh')}
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex gap-2">
        <button
          onClick={() => setActiveTab('map')}
          className={`px-4 py-2.5 rounded-xl text-xs font-bold transition flex items-center gap-2 ${activeTab === 'map' ? 'bg-slate-900 text-white shadow-sm' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'}`}
        >
          <Layers className="h-4 w-4" /> Live GIS Spatial Map
        </button>
        <button
          onClick={() => setActiveTab('impact')}
          className={`px-4 py-2.5 rounded-xl text-xs font-bold transition flex items-center gap-2 ${activeTab === 'impact' ? 'bg-red-600 text-white shadow-md' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'}`}
        >
          <Building2 className="h-4 w-4" />
          Public Infrastructure Impact & Evacuation
          {affectedInfra.length > 0 && (
            <span className={`px-1.5 py-0.5 rounded-full text-[10px] font-black ${activeTab === 'impact' ? 'bg-white text-red-600' : 'bg-red-100 text-red-700'}`}>
              {affectedInfra.length}
            </span>
          )}
        </button>
      </div>

      {activeTab === 'map' && (
        <div className="bg-white rounded-2xl p-4 sm:p-6 border border-slate-200 shadow-sm space-y-4">
          {/* Legend */}
          <div className="flex flex-wrap items-center justify-between gap-3 text-xs border-b pb-3">
            <div className="flex items-center gap-2 font-bold text-slate-800">
              <span className="h-3 w-3 rounded bg-amber-500/20 border border-amber-500 inline-block" />
              <span>Coal Extraction Panel (Underground Fleet)</span>
            </div>
            <div className="flex items-center gap-3 flex-wrap text-[11px] font-semibold text-slate-600">
              <span className="flex items-center gap-1"><span className="text-base">🛣️</span> Highway NH-218</span>
              <span className="flex items-center gap-1"><span className="text-base">🏘️</span> Civilian Colony</span>
              <span className="flex items-center gap-1"><span className="text-base">🚆</span> Railway Track</span>
              <span className="flex items-center gap-1"><span className="text-base">🚰</span> Water Supply</span>
              <span className="flex items-center gap-1"><span className="h-2.5 w-2.5 rounded-full bg-emerald-500 inline-block" /> Stable Station</span>
              <span className="flex items-center gap-1"><span className="h-2.5 w-2.5 rounded-full bg-red-500 inline-block animate-pulse" /> Sinking / Anomaly</span>
            </div>
          </div>

          {/* Map Frame */}
          <div className="h-[520px] sm:h-[580px] w-full rounded-xl overflow-hidden border border-slate-200 relative z-0">
            <MapContainer center={mapCenter} zoom={16} scrollWheelZoom style={{ height: '100%', width: '100%' }}>
              <MapRecenter center={mapCenter} zoom={focusNodeId ? 18 : 16} />
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              {/* ── COAL MINE UNDERGROUND EXTRACTION SEAM POLYGON ── */}
              <Polygon
                positions={MINE_PANEL_POLYGON}
                pathOptions={{
                  color: '#b45309',
                  fillColor: '#f59e0b',
                  fillOpacity: 0.08,
                  weight: 2,
                  dashArray: '4 4'
                }}
              >
                <MapTooltip direction="center">
                  <span className="font-bold text-xs text-amber-900">Cluster 11 & 7 (BCCL) Coal Extraction Seam</span>
                </MapTooltip>
              </Polygon>

              {/* ── MINE SITE ANCHOR MARKER ── */}
              <Marker position={MINE_CENTER} icon={MineSiteIcon}>
                <MapTooltip direction="top" offset={[0, -18]}>
                  <div className="font-bold text-xs text-amber-900">⛏️ Cluster 11 & 7 Coal Mines (Center)</div>
                </MapTooltip>
              </Marker>

              {/* ── MAIN GATEWAY MARKER ── */}
              {gatewayData?.configured && (
                <Marker position={[gatewayData.latitude, gatewayData.longitude]} icon={GatewayIcon}>
                  <MapTooltip direction="top" offset={[0, -16]}>
                    <div className="font-bold text-xs text-indigo-900">📡 Gateway (Surface Office)</div>
                  </MapTooltip>
                  <Popup>
                    <div className="p-1 text-xs space-y-1">
                      <div className="font-bold text-indigo-800">📡 Central LoRa Gateway</div>
                      <div>Status: <strong>{gatewayData.status}</strong></div>
                      <div>Telemetry sync: <strong>ACTIVE</strong></div>
                    </div>
                  </Popup>
                </Marker>
              )}

              {/* ── PUBLIC INFRASTRUCTURE MARKERS ── */}
              {infrastructure.map((feature: any) => {
                const { id, name, asset_type, criticality, status, description } = feature.properties;
                const [lon, lat] = feature.geometry.coordinates;
                const isAffected = affectedInfra.some((a: any) => a.id === id || a.name === name);
                const affectedEntry = affectedInfra.find((a: any) => a.id === id || a.name === name);
                const icon = makePublicInfraIcon(asset_type, isAffected, criticality);

                return (
                  <Marker key={`pub-infra-${id}`} position={[lat, lon]} icon={icon}>
                    <MapTooltip direction="top" offset={[0, -18]}>
                      <div className="text-xs font-bold text-slate-900">
                        {isAffected ? '⚠️ ' : ''}{name}
                      </div>
                    </MapTooltip>
                    <Popup>
                      <div className="p-2 space-y-1.5 text-xs min-w-[240px]">
                        <div className={`font-extrabold border-b pb-1 flex items-center justify-between ${isAffected ? 'text-red-700' : 'text-slate-900'}`}>
                          <span>{name}</span>
                          <span className={`px-1.5 py-0.5 rounded text-[10px] ${isAffected ? 'bg-red-100 text-red-800' : 'bg-slate-100 text-slate-700'}`}>
                            {assetTypeLabel(asset_type)}
                          </span>
                        </div>
                        <div className="text-slate-600 text-[11px]">{description}</div>
                        {isAffected && affectedEntry && (
                          <div className="bg-red-50 p-2 rounded-xl border border-red-200 text-[11px] text-red-800 space-y-1 mt-1">
                            <div className="font-extrabold text-red-900 flex items-center gap-1">
                              <span>⚠️ SUBSIDENCE THREAT ZONE</span>
                            </div>
                            <div>Distance to sinking hazard: <strong>{affectedEntry.distance_from_zone_center_m || affectedEntry.distance_m}m</strong></div>
                            <div>Public Action: <strong>{criticality === 'CRITICAL' ? 'EVACUATION & CLOSURE REQUIRED' : 'SURVEILLANCE & ACCESS RESTRICTION'}</strong></div>
                          </div>
                        )}
                      </div>
                    </Popup>
                  </Marker>
                );
              })}

              {/* ── UNDERGROUND SENSOR NODES (Located inside Coal Mine Seam) ── */}
              {nodes.map((node) => {
                const lat = Number(node.latitude);
                const lon = Number(node.longitude);
                if (!lat || !lon) return null;
                const reading = telemetryMap[node.node_code || node.node_id];
                const color = getNodeColor(node);
                const isCritical = color === '#ef4444';
                const isFocused = focusNodeId === node.node_id || focusNodeId === node.node_code;

                return (
                  <CircleMarker
                    key={node.id}
                    center={[lat, lon]}
                    radius={isFocused ? 12 : isCritical ? 10 : 7}
                    pathOptions={{
                      color: isFocused ? '#3b82f6' : isCritical ? '#991b1b' : '#0f172a',
                      fillColor: color,
                      fillOpacity: 0.9,
                      weight: isFocused ? 3.5 : isCritical ? 2.5 : 1.5
                    }}
                  >
                    <MapTooltip direction="top" offset={[0, -8]}>
                      <span className="font-mono text-xs font-bold">{node.node_code || node.node_id} ({node.risk_level || 'NORMAL'})</span>
                    </MapTooltip>
                    <Popup>
                      <div className="p-1.5 space-y-1.5 min-w-[210px] text-xs">
                        <div className="flex items-center justify-between border-b pb-1">
                          <span className="font-bold font-mono text-slate-900">
                            {node.node_code || node.node_id}
                          </span>
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-bold" style={{ backgroundColor: color + '20', color }}>
                            {node.risk_level || 'NORMAL'}
                          </span>
                        </div>
                        <div className="grid grid-cols-2 gap-1 text-[11px] font-mono text-slate-700">
                          <div>Disp: <strong>{(reading?.displacement ?? 0.15).toFixed(2)} mm</strong></div>
                          <div>Tilt: <strong>{(reading?.tilt_x ?? 0.25).toFixed(2)}°</strong></div>
                          <div>Crack: <strong>{(reading?.crack_width ?? 0.0).toFixed(2)} mm</strong></div>
                          <div>Batt: <strong>{node.battery_level || 95}%</strong></div>
                        </div>
                        <div className="pt-1 flex items-center justify-between border-t text-[10px]">
                          <span className="font-mono text-slate-400">{lat.toFixed(4)}°N, {lon.toFixed(4)}°E</span>
                          <Link to={`/app/nodes/${node.node_id || node.node_code}`} className="text-blue-600 font-bold">Details →</Link>
                        </div>
                      </div>
                    </Popup>
                  </CircleMarker>
                );
              })}

              {/* ── Impact Zone Polygons ── */}
              {impactPolygons.map((poly) => (
                <Polygon key={`poly-${poly.id}`} positions={poly.positions}
                  pathOptions={{ color: '#dc2626', fillColor: '#fca5a5', fillOpacity: 0.22, weight: 2.5, dashArray: '5 5' }}>
                  <Popup>
                    <div className="p-1.5 text-xs space-y-1 min-w-[200px]">
                      <div className="font-extrabold text-red-700 border-b pb-1">⚠️ PREDICTED SUBSIDENCE CONE</div>
                      <p className="text-[11px] text-red-800 font-medium">{poly.recommendedAction || 'Evacuate public structures within perimeter.'}</p>
                    </div>
                  </Popup>
                </Polygon>
              ))}

              {/* ── Correlation Lines ── */}
              {correlationLines.map((line) => (
                <Polyline key={`edge-${line.id}`} positions={line.positions}
                  pathOptions={{ color: '#dc2626', weight: 2.5, dashArray: '4 4', opacity: 0.8 }}
                />
              ))}
            </MapContainer>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-500 border-t pt-2">
            <span>🗺️ Coordinates: Cluster 11/7 Coal Mines Seam (23.7695°N, 86.4045°E)</span>
            <span>{nodes.length} Underground Stations • {infrastructure.length} Public & Civilian Assets Monitored</span>
          </div>
        </div>
      )}

      {/* Public Infrastructure Impact Tab */}
      {activeTab === 'impact' && (
        <div className="bg-white rounded-2xl p-4 sm:p-6 border border-slate-200 shadow-sm space-y-5">
          <div className="flex items-center justify-between flex-wrap gap-3 border-b pb-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-red-50 text-red-700 rounded-xl">
                <Building2 className="h-6 w-6" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-slate-900">Public & Civilian Infrastructure Threat Assessment</h2>
                <p className="text-xs text-slate-500">Real-time spatial correlation between underground sinking nodes and nearby public structures</p>
              </div>
            </div>
            <button onClick={fetchGISData} className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl transition flex items-center gap-2">
              <RefreshCw className={loading ? 'h-3.5 w-3.5 animate-spin' : 'h-3.5 w-3.5'} /> Refresh Threat Matrix
            </button>
          </div>

          {/* Sinking Scenario Explanation Card */}
          <div className="bg-blue-50 border border-blue-200 rounded-2xl p-4 flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-blue-600 shrink-0 mt-0.5" />
            <div className="text-xs text-blue-900 space-y-1">
              <div className="font-extrabold text-sm text-blue-950">How Public Infrastructure Evacuation Works:</div>
              <p>
                When an underground sensor node (e.g. <strong>Node 3</strong> at the eastern extraction seam) begins sinking or tilting downward due to strata void collapse, the AI hazard engine computes the <strong>geotechnical angle of draw and surface propagation radius</strong>. It continuously cross-references nearby <strong>National Highways, Railway Tracks, Potable Water Pipelines, and Residential Settlements</strong> to issue preemptive public evacuation orders before catastrophic sinkhole formation occurs.
              </p>
            </div>
          </div>

          {!impactData?.hazard_active ? (
            <div className="text-center py-10">
              <ShieldAlert className="h-12 w-12 text-emerald-500 mx-auto mb-2" />
              <div className="text-base font-bold text-emerald-800">All Surrounding Public Infrastructure Stable</div>
              <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
                Underground sensor fleet is currently operating within safe DGMS kinematic thresholds. No civilian structures or public transit routes threatened.
              </p>
            </div>
          ) : (
            <div className="space-y-5">
              {/* Summary KPIs */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-center">
                  <div className="text-2xl font-black text-red-700">{affectedInfra.length}</div>
                  <div className="text-[10px] font-bold text-red-600 uppercase mt-0.5">Public Assets at Risk</div>
                </div>
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-center">
                  <div className="text-2xl font-black text-amber-700">{impactData?.predicted_zone?.radius_m?.toFixed(0) || '150'}m</div>
                  <div className="text-[10px] font-bold text-amber-600 uppercase mt-0.5">Hazard Radius</div>
                </div>
                <div className="bg-orange-50 border border-orange-200 rounded-xl p-3 text-center">
                  <div className="text-2xl font-black text-orange-700">{impactData?.predicted_zone?.max_risk_score?.toFixed(0) || '95'}</div>
                  <div className="text-[10px] font-bold text-orange-600 uppercase mt-0.5">Max Sinking Risk</div>
                </div>
                <div className="bg-red-100 border border-red-300 rounded-xl p-3 text-center">
                  <div className="text-sm font-black text-red-800">IMMEDIATE</div>
                  <div className="text-[10px] font-bold text-red-600 uppercase mt-0.5">Evacuation Priority</div>
                </div>
              </div>

              {/* Public Assets Table */}
              <div>
                <h3 className="text-xs font-extrabold text-slate-800 uppercase tracking-wide mb-3 flex items-center gap-2">
                  <span>Public & Civilian Structures in Subsidence Path</span>
                  <span className="px-2 py-0.5 rounded-full bg-red-100 text-red-800 text-[10px] font-bold">
                    {affectedInfra.length} Threatened
                  </span>
                </h3>
                <div className="space-y-2.5">
                  {affectedInfra.map((a: any, idx: number) => {
                    const iconMap: Record<string, string> = {
                      HIGHWAY: '🛣️', RESIDENTIAL_AREA: '🏘️', WATER_SUPPLY: '🚰', RAILWAY: '🚆',
                      POWER_GRID: '⚡', HOSPITAL: '🏥', SCHOOL: '🏫', BRIDGE: '🌉', COMMERCIAL_AREA: '🏪'
                    };
                    const icon = iconMap[a.asset_type] || '🏛️';
                    return (
                      <div key={idx} className="p-3.5 rounded-xl border border-red-200 bg-white hover:bg-red-50/30 transition shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                        <div className="flex items-start gap-3 min-w-0">
                          <span className="text-2xl shrink-0 mt-0.5">{icon}</span>
                          <div className="min-w-0">
                            <div className="font-bold text-sm text-slate-900 flex items-center gap-2 flex-wrap">
                              <span>{a.name}</span>
                              <span className="text-[10px] font-extrabold px-2 py-0.5 rounded bg-red-100 text-red-700">
                                {a.impact_level} THREAT
                              </span>
                            </div>
                            <div className="text-xs text-slate-600 mt-0.5">{assetTypeLabel(a.asset_type)} • Criticality: {a.criticality}</div>
                            <div className="text-[11px] text-red-700 font-medium mt-1">{a.reason}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-3 shrink-0 self-start sm:self-center">
                          <span className="text-xs font-mono font-bold text-slate-900 bg-slate-100 px-3 py-1 rounded-lg">
                            {a.distance_from_zone_center_m || a.distance_m}m from hazard
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* DGMS Evacuation Directives */}
              <div className="bg-red-50 border-2 border-red-300 rounded-xl p-4 flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-red-600 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <div className="font-bold text-red-950 text-sm">Mandatory Public Protection Protocol</div>
                  <p className="text-xs text-red-800 leading-relaxed">
                    1. <strong>Traffic Diversion</strong>: Close National Highway NH-218 and reroute passenger vehicles via MDR-059.<br />
                    2. <strong>Civilian Evacuation</strong>: Alert civil administration to evacuate resident families in New Delhi Colony.<br />
                    3. <strong>Utility Safeguard</strong>: Shut off the municipal potable water pump main to avoid hydrostatic pipe burst.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default GISPage;
