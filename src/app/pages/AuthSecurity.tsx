import { useState, useEffect } from 'react';
import { Lock, ShieldAlert, Globe, Clock, Users } from 'lucide-react';
import { BarChart, Bar, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell } from 'recharts';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface AuthData {
  stats: {
    total_events: number;
    failed_attempts: number;
    successful_logins: number;
    failure_rate: number;
    unique_attacking_ips: number;
    targeted_users: number;
    time_window_hours: number;
  };
  recent_events: Array<{
    timestamp: string;
    user_id: string;
    ip_address: string;
    success: boolean;
    failure_reason: string | null;
    geo_location: string | null;
  }>;
  top_attacking_ips: Array<{ ip: string; attempts: number }>;
}

const COLORS = ['#EF4444', '#F59E0B', '#3B82F6', '#22D3EE', '#10B981'];

export function AuthSecurity() {
  const [data, setData] = useState<AuthData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 15000);
    return () => clearInterval(interval);
  }, []);

  async function loadData() {
    try {
      const res = await fetch(`${API_BASE}/api/security/auth-threats`);
      if (res.ok) setData(await res.json());
    } catch { /* not connected */ }
    finally { setLoading(false); }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="w-10 h-10 border-4 border-[#3B82F6] border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center h-[60vh] text-[#64748B]">
        Connect to the backend to see auth security data.
      </div>
    );
  }

  const { stats, recent_events, top_attacking_ips } = data;

  // Prepare pie chart data
  const pieData = [
    { name: 'Successful', value: stats.successful_logins, color: '#10B981' },
    { name: 'Failed', value: stats.failed_attempts, color: '#EF4444' },
  ].filter(d => d.value > 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-[#F8FAFC] text-2xl font-bold tracking-tight">Authentication Security</h1>
        <p className="text-[#94A3B8] text-sm mt-1">
          Brute force detection, credential stuffing, and impossible travel monitoring
        </p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-5 gap-4">
        <StatTile label="Total Events" value={stats.total_events} icon={Clock} accent="#3B82F6" />
        <StatTile label="Failed Attempts" value={stats.failed_attempts} icon={ShieldAlert} accent="#EF4444" />
        <StatTile label="Success Rate" value={`${(100 - stats.failure_rate).toFixed(1)}%`} icon={Lock} accent="#10B981" />
        <StatTile label="Attacking IPs" value={stats.unique_attacking_ips} icon={Globe} accent="#F59E0B" />
        <StatTile label="Users Targeted" value={stats.targeted_users} icon={Users} accent="#8B5CF6" />
      </div>

      <div className="grid grid-cols-3 gap-4">
        {/* Auth Success/Failure Pie */}
        <div className="bg-[#111827]/60 border border-[#1E293B] rounded-xl p-5">
          <h3 className="text-[#F8FAFC] font-semibold text-sm mb-4">Auth Distribution (24h)</h3>
          {pieData.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={75} dataKey="value" paddingAngle={2}>
                    {pieData.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#0F172A', border: '1px solid #1E293B', borderRadius: '8px', fontSize: '12px' }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-2 mt-3">
                {pieData.map(d => (
                  <div key={d.name} className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: d.color }}></div>
                      <span className="text-[#94A3B8]">{d.name}</span>
                    </div>
                    <span className="text-[#F8FAFC] font-semibold">{d.value}</span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="h-[200px] flex items-center justify-center text-[#64748B] text-sm">No auth data</div>
          )}
        </div>

        {/* Top Attacking IPs */}
        <div className="col-span-2 bg-[#111827]/60 border border-[#1E293B] rounded-xl p-5">
          <h3 className="text-[#F8FAFC] font-semibold text-sm mb-4">Top Attacking IPs</h3>
          {top_attacking_ips.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={top_attacking_ips} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis type="number" stroke="#64748B" style={{ fontSize: '11px' }} />
                <YAxis dataKey="ip" type="category" stroke="#64748B" style={{ fontSize: '10px' }} width={120} />
                <Tooltip contentStyle={{ backgroundColor: '#0F172A', border: '1px solid #1E293B', borderRadius: '8px', fontSize: '12px' }} />
                <Bar dataKey="attempts" fill="#EF4444" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[250px] flex items-center justify-center text-[#64748B] text-sm">
              No attacking IPs detected
            </div>
          )}
        </div>
      </div>

      {/* Recent Auth Events */}
      <div className="bg-[#111827]/60 border border-[#1E293B] rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-[#1E293B]">
          <h3 className="text-[#F8FAFC] font-semibold text-sm">Recent Authentication Events</h3>
        </div>
        {recent_events.length > 0 ? (
          <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
            <table className="w-full">
              <thead className="sticky top-0 bg-[#111827]">
                <tr className="border-b border-[#1E293B]">
                  <th className="px-5 py-3 text-left text-[#64748B] text-[11px] uppercase tracking-wider font-semibold">Time</th>
                  <th className="px-5 py-3 text-left text-[#64748B] text-[11px] uppercase tracking-wider font-semibold">User</th>
                  <th className="px-5 py-3 text-left text-[#64748B] text-[11px] uppercase tracking-wider font-semibold">IP Address</th>
                  <th className="px-5 py-3 text-left text-[#64748B] text-[11px] uppercase tracking-wider font-semibold">Status</th>
                  <th className="px-5 py-3 text-left text-[#64748B] text-[11px] uppercase tracking-wider font-semibold">Location</th>
                  <th className="px-5 py-3 text-left text-[#64748B] text-[11px] uppercase tracking-wider font-semibold">Reason</th>
                </tr>
              </thead>
              <tbody>
                {recent_events.map((e, i) => (
                  <tr key={i} className="border-b border-[#1E293B]/50 hover:bg-[#1E293B]/20 transition-colors">
                    <td className="px-5 py-2.5 text-[#94A3B8] text-xs">{new Date(e.timestamp).toLocaleString('en-IN')}</td>
                    <td className="px-5 py-2.5 text-[#F8FAFC] text-sm font-medium">{e.user_id}</td>
                    <td className="px-5 py-2.5 text-[#94A3B8] text-xs font-mono">{e.ip_address}</td>
                    <td className="px-5 py-2.5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        e.success
                          ? 'bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/20'
                          : 'bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/20'
                      }`}>
                        {e.success ? 'SUCCESS' : 'FAILED'}
                      </span>
                    </td>
                    <td className="px-5 py-2.5 text-[#94A3B8] text-xs">{e.geo_location || '—'}</td>
                    <td className="px-5 py-2.5 text-[#64748B] text-xs">{e.failure_reason || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="px-5 py-12 text-center text-[#64748B] text-sm">
            No authentication events recorded yet.
          </div>
        )}
      </div>
    </div>
  );
}

function StatTile({ label, value, icon: Icon, accent }: {
  label: string; value: any; icon: any; accent: string;
}) {
  return (
    <div className="bg-[#111827]/60 border border-[#1E293B] rounded-xl p-4">
      <Icon className="w-5 h-5 mb-2" style={{ color: accent }} />
      <p className="text-xl font-bold text-[#F8FAFC]">{value}</p>
      <p className="text-xs text-[#64748B]">{label}</p>
    </div>
  );
}
