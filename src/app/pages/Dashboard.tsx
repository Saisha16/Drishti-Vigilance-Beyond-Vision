import { Users, AlertTriangle, Shield, TrendingUp, Target } from 'lucide-react';
import { MetricCard } from '../components/MetricCard';
import { LineChart, Line, PieChart, Pie, Cell, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Area, AreaChart } from 'recharts';

const riskTrendData = [
  { time: '00:00', risk: 23 },
  { time: '04:00', risk: 18 },
  { time: '08:00', risk: 35 },
  { time: '12:00', risk: 42 },
  { time: '16:00', risk: 38 },
  { time: '20:00', risk: 31 },
  { time: '23:59', risk: 28 },
];

const threatDistribution = [
  { name: 'Data Exfiltration', value: 35, color: '#EF4444' },
  { name: 'Unauthorized Access', value: 28, color: '#F59E0B' },
  { name: 'Policy Violations', value: 22, color: '#3B82F6' },
  { name: 'Anomalous Behavior', value: 15, color: '#22D3EE' },
];

const behavioralDriftData = [
  { date: 'May 1', drift: 12 },
  { date: 'May 2', drift: 15 },
  { date: 'May 3', drift: 23 },
  { date: 'May 4', drift: 19 },
  { date: 'May 5', drift: 28 },
  { date: 'May 6', drift: 32 },
  { date: 'May 7', drift: 27 },
  { date: 'May 8', drift: 31 },
];

const radarData = [
  { metric: 'Access Pattern', value: 78, fullMark: 100 },
  { metric: 'Time Anomaly', value: 62, fullMark: 100 },
  { metric: 'Data Transfer', value: 85, fullMark: 100 },
  { metric: 'Location', value: 45, fullMark: 100 },
  { metric: 'Device Usage', value: 71, fullMark: 100 },
];

const recentAlerts = [
  { userId: 'USR-4782', threat: 'Mass Data Download', risk: 87, drift: '42%', status: 'Critical', time: '2 min ago' },
  { userId: 'USR-3291', threat: 'After-Hours Access', risk: 72, drift: '38%', status: 'High', time: '18 min ago' },
  { userId: 'USR-5614', threat: 'Unusual Login Pattern', risk: 64, drift: '31%', status: 'High', time: '1 hr ago' },
  { userId: 'USR-2847', threat: 'Policy Breach', risk: 51, drift: '22%', status: 'Medium', time: '2 hrs ago' },
  { userId: 'USR-6923', threat: 'Resource Anomaly', risk: 43, drift: '18%', status: 'Medium', time: '3 hrs ago' },
];

export function Dashboard() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-[#F8FAFC] mb-1" style={{ fontWeight: 700, fontSize: '28px', letterSpacing: '-0.02em' }}>
            Threat Intelligence Dashboard
          </h1>
          <p className="text-[#94A3B8] text-[14px]">Real-time insider threat monitoring and behavioral analysis</p>
        </div>
        <div className="flex items-center gap-3">
          <select className="bg-[#111827] border border-[#1E293B] text-[#F8FAFC] px-4 py-2 rounded-lg text-[13px] focus:outline-none focus:border-[#3B82F6] transition-colors">
            <option>Last 24 Hours</option>
            <option>Last 7 Days</option>
            <option>Last 30 Days</option>
          </select>
          <button className="bg-[#3B82F6] text-white px-4 py-2 rounded-lg text-[13px] hover:bg-[#3B82F6]/90 transition-colors" style={{ fontWeight: 600 }}>
            Generate Report
          </button>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-5 gap-4">
        <MetricCard
          icon={Users}
          title="Total Users Monitored"
          value="2,847"
          trend={12}
          trendLabel="vs last week"
          sparkline={[45, 52, 48, 61, 58, 72, 68, 75, 82]}
          color="blue"
        />
        <MetricCard
          icon={AlertTriangle}
          title="Active Threats"
          value="23"
          trend={-8}
          trendLabel="vs yesterday"
          sparkline={[75, 82, 78, 71, 65, 58, 62, 55, 48]}
          color="red"
        />
        <MetricCard
          icon={Shield}
          title="Critical Alerts"
          value="7"
          trend={3}
          trendLabel="requires attention"
          sparkline={[35, 42, 38, 45, 52, 48, 55, 61, 58]}
          color="amber"
        />
        <MetricCard
          icon={TrendingUp}
          title="Avg Risk Score"
          value="64.2"
          trend={-5}
          trendLabel="improving trend"
          sparkline={[88, 85, 82, 78, 75, 71, 68, 65, 64]}
          color="green"
        />
        <MetricCard
          icon={Target}
          title="Detection Accuracy"
          value="94.7%"
          trend={2}
          trendLabel="AI confidence"
          sparkline={[82, 84, 86, 88, 89, 91, 92, 93, 94]}
          color="blue"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-3 gap-4">
        {/* Risk Trend */}
        <div className="col-span-2 bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-5">
          <h3 className="text-[#F8FAFC] mb-4" style={{ fontWeight: 600, fontSize: '16px' }}>Risk Trend Analysis</h3>
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={riskTrendData}>
              <defs>
                <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
              <XAxis dataKey="time" stroke="#94A3B8" style={{ fontSize: '12px' }} />
              <YAxis stroke="#94A3B8" style={{ fontSize: '12px' }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0F172A', border: '1px solid #1E293B', borderRadius: '8px' }}
                labelStyle={{ color: '#F8FAFC' }}
              />
              <Area type="monotone" dataKey="risk" stroke="#3B82F6" strokeWidth={2} fill="url(#riskGradient)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Threat Distribution */}
        <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-5">
          <h3 className="text-[#F8FAFC] mb-4" style={{ fontWeight: 600, fontSize: '16px' }}>Threat Distribution</h3>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie
                data={threatDistribution}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={2}
                dataKey="value"
              >
                {threatDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#0F172A', border: '1px solid #1E293B', borderRadius: '8px' }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-2 mt-4">
            {threatDistribution.map((item) => (
              <div key={item.name} className="flex items-center justify-between text-[12px]">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }}></div>
                  <span className="text-[#94A3B8]">{item.name}</span>
                </div>
                <span className="text-[#F8FAFC]" style={{ fontWeight: 600 }}>{item.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {/* Behavioral Drift */}
        <div className="col-span-2 bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-5">
          <h3 className="text-[#F8FAFC] mb-4" style={{ fontWeight: 600, fontSize: '16px' }}>Behavioral Drift Timeline</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={behavioralDriftData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
              <XAxis dataKey="date" stroke="#94A3B8" style={{ fontSize: '12px' }} />
              <YAxis stroke="#94A3B8" style={{ fontSize: '12px' }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0F172A', border: '1px solid #1E293B', borderRadius: '8px' }}
                labelStyle={{ color: '#F8FAFC' }}
              />
              <Line type="monotone" dataKey="drift" stroke="#22D3EE" strokeWidth={2} dot={{ fill: '#22D3EE', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* User Risk Radar */}
        <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-5">
          <h3 className="text-[#F8FAFC] mb-4" style={{ fontWeight: 600, fontSize: '16px' }}>Risk Factors</h3>
          <ResponsiveContainer width="100%" height={200}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#1E293B" />
              <PolarAngleAxis dataKey="metric" stroke="#94A3B8" style={{ fontSize: '10px' }} />
              <PolarRadiusAxis stroke="#94A3B8" />
              <Radar name="Risk" dataKey="value" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Alerts Table */}
      <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl overflow-hidden">
        <div className="p-5 border-b border-[#1E293B] flex items-center justify-between">
          <h3 className="text-[#F8FAFC]" style={{ fontWeight: 600, fontSize: '16px' }}>Critical Alerts</h3>
          <button className="text-[#3B82F6] text-[13px] hover:text-[#22D3EE] transition-colors" style={{ fontWeight: 500 }}>
            View All →
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[#1E293B]">
                <th className="px-5 py-3 text-left text-[#94A3B8] text-[12px] uppercase tracking-wider" style={{ fontWeight: 600 }}>User ID</th>
                <th className="px-5 py-3 text-left text-[#94A3B8] text-[12px] uppercase tracking-wider" style={{ fontWeight: 600 }}>Threat Type</th>
                <th className="px-5 py-3 text-left text-[#94A3B8] text-[12px] uppercase tracking-wider" style={{ fontWeight: 600 }}>Risk Score</th>
                <th className="px-5 py-3 text-left text-[#94A3B8] text-[12px] uppercase tracking-wider" style={{ fontWeight: 600 }}>Drift</th>
                <th className="px-5 py-3 text-left text-[#94A3B8] text-[12px] uppercase tracking-wider" style={{ fontWeight: 600 }}>Status</th>
                <th className="px-5 py-3 text-left text-[#94A3B8] text-[12px] uppercase tracking-wider" style={{ fontWeight: 600 }}>Timestamp</th>
                <th className="px-5 py-3 text-left text-[#94A3B8] text-[12px] uppercase tracking-wider" style={{ fontWeight: 600 }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {recentAlerts.map((alert, i) => (
                <tr key={i} className="border-b border-[#1E293B] hover:bg-[#1E293B]/30 transition-colors">
                  <td className="px-5 py-4 text-[#F8FAFC] text-[13px]" style={{ fontWeight: 600 }}>{alert.userId}</td>
                  <td className="px-5 py-4 text-[#F8FAFC] text-[13px]">{alert.threat}</td>
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-1.5 bg-[#1E293B] rounded-full overflow-hidden max-w-[80px]">
                        <div
                          className={`h-full ${alert.risk >= 80 ? 'bg-[#EF4444]' : alert.risk >= 60 ? 'bg-[#F59E0B]' : 'bg-[#10B981]'}`}
                          style={{ width: `${alert.risk}%` }}
                        ></div>
                      </div>
                      <span className="text-[#F8FAFC] text-[13px]" style={{ fontWeight: 600 }}>{alert.risk}</span>
                    </div>
                  </td>
                  <td className="px-5 py-4 text-[#22D3EE] text-[13px]" style={{ fontWeight: 600 }}>{alert.drift}</td>
                  <td className="px-5 py-4">
                    <span className={`px-2.5 py-1 rounded-md text-[11px] ${
                      alert.status === 'Critical' ? 'bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/20' :
                      alert.status === 'High' ? 'bg-[#F59E0B]/10 text-[#F59E0B] border border-[#F59E0B]/20' :
                      'bg-[#3B82F6]/10 text-[#3B82F6] border border-[#3B82F6]/20'
                    }`} style={{ fontWeight: 600 }}>
                      {alert.status}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-[#94A3B8] text-[13px]">{alert.time}</td>
                  <td className="px-5 py-4">
                    <button className="text-[#3B82F6] hover:text-[#22D3EE] text-[13px] transition-colors" style={{ fontWeight: 500 }}>
                      Investigate
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
