import { useState, useEffect } from 'react';
import { Shield, AlertTriangle, Clock, User, Activity, Wifi, Lock, ChevronDown, ChevronRight, ExternalLink } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Incident {
  alert_id: string;
  user_id: string;
  timestamp: string;
  risk_score: number;
  severity: string;
  explanation: any;
  status: string;
}

interface IncidentData {
  incidents: Incident[];
  total_incidents: number;
  severity_breakdown: Record<string, number>;
  scenario_breakdown: Record<string, number>;
  auth_context: { total_events: number; failed: number; recent: any[] };
  network_context: { total_metrics: number; recent: any[] };
}

const SCENARIO_META: Record<string, { label: string; icon: any; color: string; desc: string }> = {
  brute_force: { label: 'Brute Force Attack', icon: Lock, color: '#EF4444', desc: 'Repeated failed authentication attempts detected from single source IP targeting user accounts.' },
  password_spray: { label: 'Password Spray', icon: Lock, color: '#F97316', desc: 'Single password tested across multiple user accounts from a single source — classic lateral credential attack.' },
  impossible_travel: { label: 'Impossible Travel', icon: Activity, color: '#A855F7', desc: 'User authenticated from geographically distant locations within an impossibly short timeframe.' },
  ddos: { label: 'DDoS Attack', icon: Wifi, color: '#EF4444', desc: 'Volumetric distributed denial-of-service attack detected — inbound traffic exceeds baseline by 25×.' },
  exfiltration: { label: 'Data Exfiltration', icon: AlertTriangle, color: '#F59E0B', desc: 'Abnormal outbound data transfer volume detected — potential unauthorized data extraction in progress.' },
  credential_stuffing: { label: 'Credential Stuffing', icon: Lock, color: '#EC4899', desc: 'Automated login attempts using known breached credential pairs from rotating IP addresses.' },
};

const SEV_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  critical: { bg: 'rgba(239,68,68,0.1)', text: '#EF4444', border: 'rgba(239,68,68,0.3)' },
  high: { bg: 'rgba(249,115,22,0.1)', text: '#F97316', border: 'rgba(249,115,22,0.3)' },
  medium: { bg: 'rgba(245,158,11,0.1)', text: '#F59E0B', border: 'rgba(245,158,11,0.3)' },
  low: { bg: 'rgba(16,185,129,0.1)', text: '#10B981', border: 'rgba(16,185,129,0.3)' },
};

export function IncidentResponse() {
  const [data, setData] = useState<IncidentData | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [filterSev, setFilterSev] = useState('all');

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  async function fetchData() {
    try {
      const res = await fetch(`${API_BASE}/api/demo/incidents`);
      if (res.ok) setData(await res.json());
    } catch { /* backend offline */ }
    finally { setLoading(false); }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[70vh]">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-[#EF4444] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-[#94A3B8] text-sm">Loading incident data...</p>
        </div>
      </div>
    );
  }

  if (!data || data.total_incidents === 0) {
    return (
      <div className="flex items-center justify-center h-[70vh]">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 bg-[#10B981]/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <Shield className="w-8 h-8 text-[#10B981]" />
          </div>
          <h2 className="text-[#F8FAFC] text-xl font-semibold mb-2">No Active Incidents</h2>
          <p className="text-[#94A3B8] text-sm mb-4">
            Run attack scenarios from the <strong>Live Demo</strong> page to generate security incidents.
            All events pass through the full detection pipeline and appear here as real-world incidents.
          </p>
        </div>
      </div>
    );
  }

  const incidents = data.incidents.filter(
    i => filterSev === 'all' || i.severity === filterSev
  );

  const sevBreak = data.severity_breakdown;
  const scenBreak = data.scenario_breakdown;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-[#F8FAFC] text-2xl font-bold tracking-tight flex items-center gap-3">
            <div className="w-9 h-9 bg-gradient-to-br from-[#EF4444] to-[#F97316] rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            Incident Response Center
          </h1>
          <p className="text-[#94A3B8] text-sm mt-1">
            Real-time security incidents from detection pipeline — {data.total_incidents} active incidents
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-[#EF4444]/10 border border-[#EF4444]/20 rounded-lg">
            <div className="w-2 h-2 rounded-full bg-[#EF4444] animate-pulse" />
            <span className="text-[#EF4444] text-xs font-semibold">LIVE MONITORING</span>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-5 gap-3">
        <SummaryCard label="Total Incidents" value={data.total_incidents} color="#3B82F6" />
        <SummaryCard label="Critical" value={sevBreak.critical || 0} color="#EF4444" />
        <SummaryCard label="High" value={sevBreak.high || 0} color="#F97316" />
        <SummaryCard label="Medium" value={sevBreak.medium || 0} color="#F59E0B" />
        <SummaryCard label="Auth Failures (24h)" value={data.auth_context.failed} color="#EC4899" />
      </div>

      {/* Attack Vector Breakdown */}
      <div className="bg-[#111827]/60 backdrop-blur-sm border border-[#1E293B] rounded-xl p-5">
        <h3 className="text-[#F8FAFC] font-semibold text-sm mb-3">Attack Vector Distribution</h3>
        <div className="flex flex-wrap gap-3">
          {Object.entries(scenBreak).map(([scenario, count]) => {
            const meta = SCENARIO_META[scenario];
            const color = meta?.color || '#94A3B8';
            return (
              <div key={scenario} className="flex items-center gap-2 px-3 py-2 rounded-lg border" style={{ background: `${color}08`, borderColor: `${color}25` }}>
                <div className="w-2 h-2 rounded-full" style={{ background: color }} />
                <span className="text-xs font-medium text-[#F8FAFC]">{meta?.label || scenario}</span>
                <span className="text-xs font-bold px-1.5 py-0.5 rounded" style={{ background: `${color}20`, color }}>{count}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex items-center gap-2">
        <span className="text-[#64748B] text-xs font-semibold uppercase tracking-wider mr-2">Filter:</span>
        {['all', 'critical', 'high', 'medium', 'low'].map(sev => (
          <button
            key={sev}
            onClick={() => setFilterSev(sev)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              filterSev === sev ? 'bg-[#3B82F6] text-white' : 'bg-[#1E293B] text-[#94A3B8] hover:bg-[#334155]'
            }`}
          >{sev === 'all' ? 'All' : sev.charAt(0).toUpperCase() + sev.slice(1)}</button>
        ))}
        <span className="ml-auto text-[#64748B] text-xs">{incidents.length} incidents shown</span>
      </div>

      {/* Incidents List */}
      <div className="space-y-3">
        {incidents.map(incident => (
          <IncidentCard
            key={incident.alert_id}
            incident={incident}
            expanded={expandedId === incident.alert_id}
            onToggle={() => setExpandedId(expandedId === incident.alert_id ? null : incident.alert_id)}
          />
        ))}
      </div>
    </div>
  );
}

/* ─── Sub-components ──────────────────────────────────────────────── */

function SummaryCard({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="border rounded-xl p-4" style={{ background: `${color}06`, borderColor: `${color}20` }}>
      <p className="text-2xl font-bold text-[#F8FAFC]">{value}</p>
      <p className="text-[10px] font-semibold uppercase tracking-wider mt-1" style={{ color }}>{label}</p>
    </div>
  );
}

function IncidentCard({ incident, expanded, onToggle }: { incident: Incident; expanded: boolean; onToggle: () => void }) {
  const sev = SEV_STYLES[incident.severity] || SEV_STYLES.medium;
  const explanation = typeof incident.explanation === 'string' ? JSON.parse(incident.explanation) : incident.explanation;
  const summary = explanation?.summary || 'Security incident detected';
  const riskFactors = explanation?.risk_factors || [];
  const behavioralChanges = explanation?.behavioral_changes || [];
  const recommendedActions = explanation?.recommended_actions || [];

  // Extract scenario from alert_id
  const parts = incident.alert_id.split('-');
  const scenarioKey = parts.length >= 2 ? parts[1].toLowerCase() : '';
  const meta = SCENARIO_META[scenarioKey];

  return (
    <div className="border rounded-xl overflow-hidden transition-all duration-200" style={{ borderColor: sev.border, background: sev.bg }}>
      {/* Header - always visible */}
      <button onClick={onToggle} className="w-full px-5 py-4 flex items-center gap-4 text-left hover:bg-white/[0.02] transition-colors">
        <div className="flex-shrink-0">
          {expanded ? <ChevronDown className="w-4 h-4 text-[#64748B]" /> : <ChevronRight className="w-4 h-4 text-[#64748B]" />}
        </div>

        {/* Severity badge */}
        <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase flex-shrink-0" style={{ background: sev.bg, color: sev.text, border: `1px solid ${sev.border}` }}>
          {incident.severity}
        </span>

        {/* Title */}
        <div className="flex-1 min-w-0">
          <p className="text-[#F8FAFC] text-sm font-semibold truncate">{summary}</p>
          <div className="flex items-center gap-3 mt-0.5">
            <span className="text-[#64748B] text-[11px] flex items-center gap-1"><User className="w-3 h-3" />{incident.user_id}</span>
            <span className="text-[#64748B] text-[11px] flex items-center gap-1"><Clock className="w-3 h-3" />{new Date(incident.timestamp).toLocaleString('en-IN')}</span>
          </div>
        </div>

        {/* Risk Score */}
        <div className="flex-shrink-0 text-right">
          <div className="text-lg font-bold" style={{ color: sev.text }}>{Math.round(incident.risk_score)}</div>
          <div className="text-[10px] text-[#64748B]">Risk Score</div>
        </div>
      </button>

      {/* Expanded Details */}
      {expanded && (
        <div className="border-t px-5 py-4 space-y-4" style={{ borderColor: sev.border }}>
          {/* Incident Overview */}
          {meta && (
            <div className="flex items-start gap-3 p-3 rounded-lg bg-[#0F172A]/60 border border-[#1E293B]">
              <meta.icon className="w-5 h-5 flex-shrink-0 mt-0.5" style={{ color: meta.color }} />
              <div>
                <p className="text-sm font-semibold" style={{ color: meta.color }}>{meta.label}</p>
                <p className="text-xs text-[#94A3B8] mt-1 leading-relaxed">{meta.desc}</p>
              </div>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            {/* Risk Factors */}
            {riskFactors.length > 0 && (
              <div>
                <p className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold mb-2">Risk Factors</p>
                <ul className="space-y-1">
                  {riskFactors.map((f: string, i: number) => (
                    <li key={i} className="text-xs text-[#94A3B8] flex items-start gap-2">
                      <AlertTriangle className="w-3 h-3 text-[#F59E0B] mt-0.5 flex-shrink-0" />
                      {f}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Behavioral Changes / Detections */}
            {behavioralChanges.length > 0 && (
              <div>
                <p className="text-[10px] text-[#64748B] uppercase tracking-wider font-semibold mb-2">Detection Details</p>
                <ul className="space-y-1">
                  {behavioralChanges.map((c: string, i: number) => (
                    <li key={i} className="text-xs text-[#94A3B8] flex items-start gap-2">
                      <Activity className="w-3 h-3 text-[#22D3EE] mt-0.5 flex-shrink-0" />
                      {c}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Recommended Actions */}
          {recommendedActions.length > 0 && (
            <div className="p-3 rounded-lg bg-[#3B82F6]/5 border border-[#3B82F6]/15">
              <p className="text-[10px] text-[#3B82F6] uppercase tracking-wider font-semibold mb-2">Recommended Response</p>
              <div className="flex flex-wrap gap-2">
                {recommendedActions.map((a: string, i: number) => (
                  <span key={i} className="text-xs text-[#94A3B8] px-2 py-1 bg-[#1E293B] rounded flex items-center gap-1">
                    <ExternalLink className="w-3 h-3 text-[#3B82F6]" />{a}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Meta */}
          <div className="flex items-center gap-4 text-[10px] text-[#475569] pt-2 border-t border-[#1E293B]">
            <span>ID: {incident.alert_id}</span>
            <span>Status: {incident.status}</span>
          </div>
        </div>
      )}
    </div>
  );
}
