import { useState, useEffect, useCallback } from 'react';
import { Wifi, ArrowDown, ArrowUp, Activity, Zap, Clock } from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, LineChart, Line } from 'recharts';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface NetworkData {
  metrics: Array<{
    timestamp: string;
    bytes_in: number;
    bytes_out: number;
    packets_in: number;
    packets_out: number;
    connections: number;
    total_bytes: number;
    total_packets: number;
  }>;
  baseline: {
    status: string;
    samples?: number;
    window_minutes?: number;
    bytes_in?: { mean: number; std: number };
    bytes_out?: { mean: number; std: number };
    packets?: { mean: number; std: number };
    connections?: { mean: number; std: number };
  };
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
}

export function NetworkMonitor() {
  const [data, setData] = useState<NetworkData | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState<number>(60); // Default 1 hour

  const loadData = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/network/metrics?minutes=${timeframe}`);
      if (res.ok) setData(await res.json());
    } catch { /* not connected */ }
    finally { setLoading(false); }
  }, [timeframe]);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, [loadData]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="w-10 h-10 border-4 border-[#3B82F6] border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const metrics = data?.metrics || [];
  const baseline = data?.baseline;
  const latest = metrics.length > 0 ? metrics[metrics.length - 1] : null;

  // Chart data with formatted timestamps
  const chartData = metrics.map(m => ({
    time: new Date(m.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }),
    bytes_in: m.bytes_in,
    bytes_out: m.bytes_out,
    connections: m.connections,
    packets: m.total_packets,
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-[#F8FAFC] text-2xl font-bold tracking-tight">Network Monitor</h1>
          <p className="text-[#94A3B8] text-sm mt-1">
            Bandwidth anomaly detection — DDoS, exfiltration, and connection flood monitoring
          </p>
        </div>
        
        <div className="flex items-center gap-2 bg-[#111827]/60 border border-[#1E293B] rounded-lg p-1.5">
          <Clock className="w-4 h-4 text-[#64748B] ml-2" />
          <select 
            value={timeframe}
            onChange={(e) => setTimeframe(Number(e.target.value))}
            className="bg-transparent text-sm text-[#F8FAFC] border-none focus:ring-0 outline-none cursor-pointer pr-2"
          >
            <option value={60} className="bg-[#0F172A]">Last 1 Hour</option>
            <option value={180} className="bg-[#0F172A]">Last 3 Hours</option>
            <option value={600} className="bg-[#0F172A]">Last 10 Hours</option>
            <option value={1440} className="bg-[#0F172A]">Last 24 Hours</option>
          </select>
        </div>
      </div>

      {/* Live Stats */}
      <div className="grid grid-cols-5 gap-4">
        <NetStat icon={ArrowDown} label="Inbound" value={latest ? formatBytes(latest.bytes_in) : '—'} accent="#3B82F6" />
        <NetStat icon={ArrowUp} label="Outbound" value={latest ? formatBytes(latest.bytes_out) : '—'} accent="#8B5CF6" />
        <NetStat icon={Activity} label="Packets" value={latest ? latest.total_packets.toLocaleString() : '—'} accent="#22D3EE" />
        <NetStat icon={Zap} label="Connections" value={latest ? latest.connections.toLocaleString() : '—'} accent="#F59E0B" />
        <NetStat icon={Wifi} label="Baseline" value={baseline?.status === 'active' ? `${baseline.samples} samples` : baseline?.status || '—'} accent="#10B981" />
      </div>

      {/* Traffic Charts */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-[#111827]/60 border border-[#1E293B] rounded-xl p-5">
          <h3 className="text-[#F8FAFC] font-semibold text-sm mb-4">Traffic Volume (Bytes)</h3>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="inGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="outGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="time" stroke="#64748B" style={{ fontSize: '10px' }} />
                <YAxis stroke="#64748B" style={{ fontSize: '10px' }} tickFormatter={(v) => formatBytes(v)} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0F172A', border: '1px solid #1E293B', borderRadius: '8px', fontSize: '12px' }}
                  formatter={(value: number) => formatBytes(value)}
                />
                <Area type="monotone" dataKey="bytes_in" stroke="#3B82F6" strokeWidth={2} fill="url(#inGrad)" name="Inbound" />
                <Area type="monotone" dataKey="bytes_out" stroke="#8B5CF6" strokeWidth={2} fill="url(#outGrad)" name="Outbound" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <EmptyChart />
          )}
        </div>

        <div className="bg-[#111827]/60 border border-[#1E293B] rounded-xl p-5">
          <h3 className="text-[#F8FAFC] font-semibold text-sm mb-4">Connections & Packets</h3>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="time" stroke="#64748B" style={{ fontSize: '10px' }} />
                <YAxis stroke="#64748B" style={{ fontSize: '10px' }} />
                <Tooltip contentStyle={{ backgroundColor: '#0F172A', border: '1px solid #1E293B', borderRadius: '8px', fontSize: '12px' }} />
                <Line type="monotone" dataKey="connections" stroke="#F59E0B" strokeWidth={2} dot={false} name="Connections" />
                <Line type="monotone" dataKey="packets" stroke="#22D3EE" strokeWidth={2} dot={false} name="Packets" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <EmptyChart />
          )}
        </div>
      </div>

      {/* Baseline Info */}
      {baseline?.status === 'active' && (
        <div className="bg-[#111827]/60 border border-[#1E293B] rounded-xl p-5">
          <h3 className="text-[#F8FAFC] font-semibold text-sm mb-4">Current Baseline (Anomaly Thresholds)</h3>
          <div className="grid grid-cols-4 gap-4">
            <BaselineCard label="Inbound" mean={baseline.bytes_in?.mean || 0} std={baseline.bytes_in?.std || 0} format={formatBytes} />
            <BaselineCard label="Outbound" mean={baseline.bytes_out?.mean || 0} std={baseline.bytes_out?.std || 0} format={formatBytes} />
            <BaselineCard label="Packets" mean={baseline.packets?.mean || 0} std={baseline.packets?.std || 0} />
            <BaselineCard label="Connections" mean={baseline.connections?.mean || 0} std={baseline.connections?.std || 0} />
          </div>
          <p className="text-[10px] text-[#475569] mt-3">
            Anomaly threshold: 3σ above mean. Values exceeding mean + 3×std trigger alerts.
            Window: {baseline.window_minutes} min, {baseline.samples} samples.
          </p>
        </div>
      )}
    </div>
  );
}

function NetStat({ icon: Icon, label, value, accent }: {
  icon: any; label: string; value: string; accent: string;
}) {
  return (
    <div className="bg-[#111827]/60 border border-[#1E293B] rounded-xl p-4">
      <Icon className="w-5 h-5 mb-2" style={{ color: accent }} />
      <p className="text-lg font-bold text-[#F8FAFC]">{value}</p>
      <p className="text-xs text-[#64748B]">{label}</p>
    </div>
  );
}

function BaselineCard({ label, mean, std, format }: {
  label: string; mean: number; std: number; format?: (v: number) => string;
}) {
  const fmt = format || ((v: number) => v.toLocaleString());
  return (
    <div className="bg-[#0F172A] border border-[#1E293B] rounded-lg p-3">
      <p className="text-xs text-[#64748B] mb-1">{label}</p>
      <p className="text-sm text-[#F8FAFC] font-medium">μ = {fmt(mean)}</p>
      <p className="text-xs text-[#475569]">σ = {fmt(std)}</p>
      <p className="text-[10px] text-[#EF4444] mt-1">Alert if &gt; {fmt(mean + 3 * std)}</p>
    </div>
  );
}

function EmptyChart() {
  return (
    <div className="h-[240px] flex items-center justify-center text-[#64748B] text-sm">
      No network data collected yet. Data appears as the backend records metrics.
    </div>
  );
}
