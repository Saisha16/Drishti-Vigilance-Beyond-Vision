import { useState, useEffect, useRef, useCallback } from 'react';
import {
  Play, Trash2, Shield, Wifi, Lock, AlertTriangle,
  CheckCircle, Globe, Zap, Database, Eye, Terminal,
  Activity, Server, UserX, RefreshCw,
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// ─── Types ────────────────────────────────────────────────────────────────────

interface Detection {
  engine: string;
  type: string;
  severity: string;
  confidence: number;
  description: string;
}

interface FeedEntry {
  id: string;
  timestamp: string;
  scenario: string;
  source: string;
  detected: boolean;
  detections: Detection[];
  event_data: Record<string, unknown>;
}

// ─── Scenario Definitions ─────────────────────────────────────────────────────

const NORMAL_SCENARIOS = [
  {
    id: 'normal_login',
    label: 'Normal Login',
    icon: CheckCircle,
    color: '#10B981',
    bg: 'rgba(16,185,129,0.08)',
    border: 'rgba(16,185,129,0.25)',
    desc: 'Employee authenticates from office IP',
    repeat: 1,
    terminalLines: ['> Authenticating user...', '> 2FA verified [OK]', '> Session started'],
  },
  {
    id: 'normal_browse',
    label: 'Browse Files',
    icon: Database,
    color: '#22D3EE',
    bg: 'rgba(34,211,238,0.08)',
    border: 'rgba(34,211,238,0.25)',
    desc: 'Normal internal file access',
    repeat: 1,
    terminalLines: ['> Fetching /docs/report.pdf...', '> 2.1 MB received', '> Rendered successfully'],
  },
  {
    id: 'normal_browse',
    label: 'Send Email',
    icon: Globe,
    color: '#8B5CF6',
    bg: 'rgba(139,92,246,0.08)',
    border: 'rgba(139,92,246,0.25)',
    desc: 'Standard SMTP outbound email',
    repeat: 1,
    terminalLines: ['> SMTP handshake...', '> Sending 14 KB message', '> Delivered [OK]'],
  },
  {
    id: 'normal_browse',
    label: 'Download Report',
    icon: Activity,
    color: '#3B82F6',
    bg: 'rgba(59,130,246,0.08)',
    border: 'rgba(59,130,246,0.25)',
    desc: 'Quarterly analytics export',
    repeat: 1,
    terminalLines: ['> GET /api/reports/Q1...', '> 8.4 MB transfer', '> Download complete [OK]'],
  },
];

const ATTACK_SCENARIOS = [
  {
    id: 'brute_force',
    label: 'Brute Force',
    icon: Lock,
    color: '#EF4444',
    bg: 'rgba(239,68,68,0.08)',
    border: 'rgba(239,68,68,0.25)',
    desc: 'Repeated password attempts on one account',
    repeat: 10,
    terminalLines: [
      '> LOGIN FAILED: attempt 1', '> LOGIN FAILED: attempt 2', '> LOGIN FAILED: attempt 3',
      '> LOGIN FAILED: attempt 4', '> LOGIN FAILED: attempt 5 [!]',
      '> LOGIN FAILED: attempt 6', '> LOGIN FAILED: attempt 7',
      '> LOGIN FAILED: attempt 8', '> LOGIN FAILED: attempt 9',
      '> LOGIN FAILED: attempt 10 — LOCKOUT TRIGGERED',
    ],
  },
  {
    id: 'password_spray',
    label: 'Password Spray',
    icon: UserX,
    color: '#F97316',
    bg: 'rgba(249,115,22,0.08)',
    border: 'rgba(249,115,22,0.25)',
    desc: 'One password tried across many accounts',
    repeat: 8,
    terminalLines: [
      '> Trying "Summer2024!" on user_A', '> Trying "Summer2024!" on user_B',
      '> Trying "Summer2024!" on user_C', '> Trying "Summer2024!" on user_D',
      '> Trying "Summer2024!" on user_E', '> Trying "Summer2024!" on user_F',
      '> Trying "Summer2024!" on user_G', '> Trying "Summer2024!" on user_H',
    ],
  },
  {
    id: 'impossible_travel',
    label: 'Impossible Travel',
    icon: Globe,
    color: '#A855F7',
    bg: 'rgba(168,85,247,0.08)',
    border: 'rgba(168,85,247,0.25)',
    desc: 'Login from Mumbai then New York in 30s',
    repeat: 1,
    terminalLines: [
      '> LOGIN SUCCESS: Mumbai, IN (103.21.244.10)',
      '> [30 seconds later...]',
      '> LOGIN SUCCESS: New York, US (198.51.100.25)',
      '> [!] Distance: 11,550 km in 30 seconds!',
    ],
  },
  {
    id: 'ddos',
    label: 'DDoS Flood',
    icon: Wifi,
    color: '#EF4444',
    bg: 'rgba(239,68,68,0.08)',
    border: 'rgba(239,68,68,0.3)',
    desc: 'Massive inbound UDP packet flood',
    repeat: 1,
    terminalLines: [
      '> Inbound traffic: 12.5 Gbps (25× baseline)',
      '> UDP packets: 890k pps',
      '> Connections: 8,000 (baseline: ~50)',
      '> Protocol: 90% UDP — SYN flood pattern',
    ],
  },
  {
    id: 'exfiltration',
    label: 'Data Exfiltration',
    icon: Server,
    color: '#F59E0B',
    bg: 'rgba(245,158,11,0.08)',
    border: 'rgba(245,158,11,0.25)',
    desc: 'Huge outbound data transfer detected',
    repeat: 1,
    terminalLines: [
      '> Outbound spike: 4.2 GB/s (20× baseline)',
      '> Destination: 198.51.100.x (unknown)',
      '> Protocol: TCP/443 — encrypted channel',
      '> Pattern matches known exfil signatures',
    ],
  },
  {
    id: 'credential_stuffing',
    label: 'Credential Stuffing',
    icon: Eye,
    color: '#EC4899',
    bg: 'rgba(236,72,153,0.08)',
    border: 'rgba(236,72,153,0.25)',
    desc: 'Known breach pairs from rotating IPs',
    repeat: 6,
    terminalLines: [
      '> Breach pair #1 from 10.0.44.12', '> Breach pair #2 from 10.0.89.201',
      '> Breach pair #3 from 10.0.12.77', '> Breach pair #4 from 10.0.200.33',
      '> Breach pair #5 from 10.0.67.144', '> Breach pair #6 from 10.0.31.99',
    ],
  },
];

// ─── Severity config ──────────────────────────────────────────────────────────

const SEV: Record<string, { color: string; bg: string; label: string }> = {
  critical: { color: '#EF4444', bg: 'rgba(239,68,68,0.15)', label: 'CRITICAL' },
  high:     { color: '#F97316', bg: 'rgba(249,115,22,0.15)', label: 'HIGH' },
  medium:   { color: '#F59E0B', bg: 'rgba(245,158,11,0.15)', label: 'MEDIUM' },
  low:      { color: '#10B981', bg: 'rgba(16,185,129,0.15)', label: 'LOW' },
};

const TYPE_LABELS: Record<string, string> = {
  brute_force: 'Brute Force',
  password_spray: 'Password Spray',
  distributed_brute_force: 'Distributed BF',
  impossible_travel: 'Impossible Travel',
  credential_stuffing: 'Credential Stuffing',
  ddos_inbound: 'DDoS Inbound',
  exfiltration: 'Data Exfiltration',
  connection_flood: 'Connection Flood',
  normal_login: 'Normal Login',
  normal_browse: 'Normal Browse',
};

// ─── Component ────────────────────────────────────────────────────────────────

export function LiveDemo() {
  const [feed, setFeed]                     = useState<FeedEntry[]>([]);
  const [terminalLines, setTerminalLines]   = useState<string[]>(['> Drishti Live Demo ready. Select an action below.', '> Waiting...']);
  const [running, setRunning]               = useState(false);
  const [stats, setStats]                   = useState({ total: 0, detected: 0, clean: 0 });
  const [activeScenario, setActiveScenario] = useState<string | null>(null);
  const feedRef  = useRef<HTMLDivElement>(null);
  const termRef  = useRef<HTMLDivElement>(null);
  const abortRef = useRef(false);

  // Auto-scroll feed and terminal
  useEffect(() => {
    feedRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
  }, [feed]);
  useEffect(() => {
    termRef.current?.scrollTo({ top: termRef.current.scrollHeight, behavior: 'smooth' });
  }, [terminalLines]);

  const pushTerminal = useCallback((lines: string[]) => {
    setTerminalLines(prev => {
      const next = [...prev, ...lines];
      return next.slice(-60); // keep last 60 lines
    });
  }, []);

  const addToFeed = useCallback((entries: FeedEntry[]) => {
    setFeed(prev => [...entries, ...prev].slice(0, 100));
    setStats(prev => {
      const detected = entries.filter(e => e.detected).length;
      return {
        total: prev.total + entries.length,
        detected: prev.detected + detected,
        clean: prev.clean + (entries.length - detected),
      };
    });
  }, []);

  const runScenario = useCallback(async (scenario: typeof ATTACK_SCENARIOS[0]) => {
    if (running) return;
    setRunning(true);
    setActiveScenario(scenario.id);
    abortRef.current = false;

    pushTerminal([``, `> ── ${scenario.label.toUpperCase()} ─────────────────────`]);

    const delay = (ms: number) => new Promise<void>(res => setTimeout(res, ms));

    try {
      for (let i = 0; i < scenario.terminalLines.length; i++) {
        if (abortRef.current) break;
        pushTerminal([scenario.terminalLines[i]]);
        await delay(180);

        // For animated scenarios, fire a single API event per terminal line
        if (scenario.repeat > 1 && i < scenario.repeat) {
          try {
            const res = await fetch(`${API_BASE}/api/demo/simulate`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                scenario: scenario.id,
                user_id: 'demo_user',
                ip_address: '203.0.113.42',
                geo_location: 'Mumbai',
                repeat: 1,
              }),
            });
            if (res.ok) {
              const data = await res.json();
              addToFeed(data.results ?? []);
              // Show alert in terminal
              const alerts = (data.results ?? []).flatMap((r: FeedEntry) => r.detections);
              if (alerts.length > 0) {
                pushTerminal([`  [ALERT] ${alerts[0].type} [${alerts[0].severity.toUpperCase()}]`]);
              }
            }
          } catch {
            pushTerminal(['  [!] API unreachable']);
          }
          await delay(150);
        }
      }

      // For single-shot scenarios (repeat=1), fire once at the end
      if (scenario.repeat === 1 && !abortRef.current) {
        try {
          const res = await fetch(`${API_BASE}/api/demo/simulate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              scenario: scenario.id,
              user_id: 'demo_user',
              ip_address: '203.0.113.42',
              geo_location: 'Mumbai',
              repeat: 1,
            }),
          });
          if (res.ok) {
            const data = await res.json();
            addToFeed(data.results ?? []);
            const alerts = (data.results ?? []).flatMap((r: FeedEntry) => r.detections);
            if (alerts.length > 0) {
              pushTerminal([`  [ALERT] DETECTED: ${alerts.map(a => a.type).join(', ')}`]);
            } else {
              pushTerminal(['  [OK] No anomalies detected']);
            }
          }
        } catch {
          pushTerminal(['  [!] API unreachable']);
        }
      }

      pushTerminal([`> Scenario complete.`]);
    } finally {
      setRunning(false);
      setActiveScenario(null);
    }
  }, [running, pushTerminal, addToFeed]);

  const clearAll = async () => {
    setFeed([]);
    setStats({ total: 0, detected: 0, clean: 0 });
    setTerminalLines(['> Feed cleared. Ready.', '> Waiting...']);
    abortRef.current = true;
    try { await fetch(`${API_BASE}/api/demo/feed`, { method: 'DELETE' }); } catch { /* ok */ }
  };

  // ─── Render ───────────────────────────────────────────────────────────────

  return (
    <div style={{ minHeight: '100vh', background: '#070C14', color: '#F8FAFC', fontFamily: "'Inter', sans-serif", padding: '24px' }}>

      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 6 }}>
          <div style={{ width: 36, height: 36, background: 'linear-gradient(135deg, #3B82F6, #22D3EE)', borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Play size={18} color="white" />
          </div>
          <div>
            <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0 }}>Live Demo Simulator</h1>
            <p style={{ fontSize: 12, color: '#64748B', margin: 0 }}>Fire real events through Drishti's detection engines and watch them trigger live</p>
          </div>
          <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
            {/* Stats */}
            {[
              { label: 'Total Events', val: stats.total, color: '#94A3B8' },
              { label: 'Detected',     val: stats.detected, color: '#EF4444' },
              { label: 'Clean',        val: stats.clean,    color: '#10B981' },
            ].map(s => (
              <div key={s.label} style={{ padding: '6px 14px', background: '#0F172A', border: '1px solid #1E293B', borderRadius: 8, textAlign: 'center' }}>
                <div style={{ fontSize: 18, fontWeight: 700, color: s.color }}>{s.val}</div>
                <div style={{ fontSize: 10, color: '#475569' }}>{s.label}</div>
              </div>
            ))}
            <button onClick={clearAll} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '6px 14px', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)', borderRadius: 8, color: '#EF4444', cursor: 'pointer', fontSize: 12, fontWeight: 600 }}>
              <Trash2 size={13} /> Clear
            </button>
          </div>
        </div>
      </div>

      {/* Main grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, height: 'calc(100vh - 160px)' }}>

        {/* LEFT — Workstation Simulator */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>

          {/* Terminal */}
          <div style={{ background: '#0A0F1A', border: '1px solid #1E293B', borderRadius: 12, flex: '0 0 200px', overflow: 'hidden' }}>
            <div style={{ padding: '10px 14px', borderBottom: '1px solid #1E293B', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Terminal size={13} color="#22D3EE" />
              <span style={{ fontSize: 11, color: '#64748B', fontWeight: 600 }}>SIMULATED WORKSTATION</span>
              {running && (
                <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 5 }}>
                  <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#EF4444', animation: 'pulse 1s infinite' }} />
                  <span style={{ fontSize: 10, color: '#EF4444', fontWeight: 700 }}>EXECUTING</span>
                </div>
              )}
            </div>
            <div ref={termRef} style={{ padding: '10px 14px', height: 160, overflowY: 'auto', fontFamily: 'monospace', fontSize: 11, lineHeight: 1.7, color: '#94A3B8' }}>
              {terminalLines.map((line, i) => (
                <div key={i} style={{ color: line.includes('[ALERT]') || line.includes('ALERT') ? '#EF4444' : line.includes('[OK]') ? '#10B981' : line.includes('[!]') ? '#F59E0B' : line.startsWith('> ──') ? '#22D3EE' : '#94A3B8' }}>
                  {line}
                </div>
              ))}
            </div>
          </div>

          {/* Normal actions */}
          <div style={{ background: '#0A0F1A', border: '1px solid #1E293B', borderRadius: 12, padding: 14 }}>
            <p style={{ fontSize: 10, color: '#475569', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 10 }}>Normal Activities</p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              {NORMAL_SCENARIOS.map((s, i) => {
                const Icon = s.icon;
                const isActive = activeScenario === s.id && running;
                return (
                  <button
                    key={i}
                    id={`demo-btn-${s.label.replace(/\s+/g, '-').toLowerCase()}`}
                    onClick={() => runScenario(s)}
                    disabled={running}
                    style={{
                      display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px',
                      background: isActive ? s.bg : '#111827',
                      border: `1px solid ${isActive ? s.border : '#1E293B'}`,
                      borderRadius: 8, cursor: running ? 'not-allowed' : 'pointer',
                      opacity: running && !isActive ? 0.5 : 1,
                      transition: 'all 0.2s', textAlign: 'left',
                    }}
                  >
                    <div style={{ width: 28, height: 28, background: s.bg, border: `1px solid ${s.border}`, borderRadius: 6, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                      <Icon size={13} color={s.color} />
                    </div>
                    <div>
                      <div style={{ fontSize: 12, fontWeight: 600, color: '#F8FAFC' }}>{s.label}</div>
                      <div style={{ fontSize: 10, color: '#475569', lineHeight: 1.3 }}>{s.desc}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Attack scenarios */}
          <div style={{ background: '#0A0F1A', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 12, padding: 14, flex: 1 }}>
            <p style={{ fontSize: 10, color: '#EF4444', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 10 }}>Attack Scenarios -- fires through real detection engines</p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              {ATTACK_SCENARIOS.map((s, i) => {
                const Icon = s.icon;
                const isActive = activeScenario === s.id && running;
                return (
                  <button
                    key={i}
                    id={`demo-btn-${s.label.replace(/\s+/g, '-').toLowerCase()}`}
                    onClick={() => runScenario(s)}
                    disabled={running}
                    style={{
                      display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px',
                      background: isActive ? s.bg : '#111827',
                      border: `1px solid ${isActive ? s.border : '#1E293B'}`,
                      borderRadius: 8, cursor: running ? 'not-allowed' : 'pointer',
                      opacity: running && !isActive ? 0.5 : 1,
                      transition: 'all 0.2s', textAlign: 'left',
                    }}
                  >
                    <div style={{ width: 28, height: 28, background: s.bg, border: `1px solid ${s.border}`, borderRadius: 6, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                      <Icon size={13} color={s.color} />
                    </div>
                    <div>
                      <div style={{ fontSize: 12, fontWeight: 600, color: '#F8FAFC' }}>{s.label}</div>
                      <div style={{ fontSize: 10, color: '#475569', lineHeight: 1.3 }}>{s.desc}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* RIGHT — Live Detection Feed */}
        <div style={{ background: '#0A0F1A', border: '1px solid #1E293B', borderRadius: 12, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid #1E293B', display: 'flex', alignItems: 'center', gap: 8 }}>
            <Shield size={14} color="#22D3EE" />
            <span style={{ fontSize: 12, fontWeight: 700, color: '#F8FAFC' }}>Drishti Detection Feed</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: 5, marginLeft: 8 }}>
              <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#10B981', animation: 'pulse 2s infinite' }} />
              <span style={{ fontSize: 10, color: '#10B981', fontWeight: 600 }}>LIVE</span>
            </div>
            <span style={{ marginLeft: 'auto', fontSize: 10, color: '#475569' }}>{feed.length} events</span>
          </div>

          <div ref={feedRef} style={{ flex: 1, overflowY: 'auto', padding: '10px 12px', display: 'flex', flexDirection: 'column', gap: 8 }}>
            {feed.length === 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: 12 }}>
                <Shield size={40} color="#1E293B" />
                <p style={{ color: '#475569', fontSize: 13, textAlign: 'center' }}>
                  No events yet.<br />Click an action on the left to start.
                </p>
              </div>
            )}
            {feed.map((entry) => (
              <FeedCard key={entry.id} entry={entry} />
            ))}
          </div>
        </div>
      </div>

      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
        @keyframes slideIn { from{opacity:0;transform:translateY(-8px)} to{opacity:1;transform:translateY(0)} }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #1E293B; border-radius: 4px; }
      `}</style>
    </div>
  );
}

// ─── Feed Card ────────────────────────────────────────────────────────────────

function FeedCard({ entry }: { entry: FeedEntry }) {
  const isClean = !entry.detected;
  const time = new Date(entry.timestamp).toLocaleTimeString();

  return (
    <div style={{
      borderRadius: 10, overflow: 'hidden',
      border: `1px solid ${isClean ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}`,
      background: isClean ? 'rgba(16,185,129,0.04)' : 'rgba(239,68,68,0.04)',
      animation: 'slideIn 0.25s ease',
    }}>
      {/* Card header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 12px', borderBottom: `1px solid ${isClean ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)'}` }}>
        {isClean
          ? <CheckCircle size={12} color="#10B981" />
          : <AlertTriangle size={12} color="#EF4444" />
        }
        <span style={{ fontSize: 11, fontWeight: 600, color: isClean ? '#10B981' : '#EF4444' }}>
          {isClean ? 'CLEAN' : `${entry.detections.length} DETECTION${entry.detections.length > 1 ? 'S' : ''}`}
        </span>
        <span style={{ fontSize: 10, color: '#64748B', marginLeft: 4 }}>
          {TYPE_LABELS[entry.scenario] ?? entry.scenario}
        </span>
        <span style={{ marginLeft: 'auto', fontSize: 10, color: '#475569', fontFamily: 'monospace' }}>{time}</span>
      </div>

      {/* Detections */}
      {entry.detections.length > 0 && (
        <div style={{ padding: '8px 12px', display: 'flex', flexDirection: 'column', gap: 6 }}>
          {entry.detections.map((d, i) => {
            const sev = SEV[d.severity] ?? SEV.medium;
            return (
              <div key={i} style={{ display: 'flex', gap: 8, alignItems: 'flex-start' }}>
                <span style={{ padding: '1px 7px', borderRadius: 4, fontSize: 9, fontWeight: 700, color: sev.color, background: sev.bg, border: `1px solid ${sev.color}30`, flexShrink: 0, lineHeight: '18px' }}>
                  {sev.label}
                </span>
                <div>
                  <span style={{ fontSize: 10, fontWeight: 600, color: '#F8FAFC', display: 'block' }}>
                    {TYPE_LABELS[d.type] ?? d.type} — {d.engine === 'network' ? 'Network' : 'Auth'}
                  </span>
                  <span style={{ fontSize: 10, color: '#94A3B8', lineHeight: 1.4 }}>{d.description}</span>
                  <span style={{ fontSize: 9, color: '#475569' }}> · confidence {(d.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {isClean && (
        <div style={{ padding: '6px 12px 8px', fontSize: 10, color: '#64748B' }}>
          All checks passed -- no anomalous behaviour detected
        </div>
      )}
    </div>
  );
}
