import { User, TrendingUp, AlertTriangle, Clock, MapPin, Monitor, Database, FileText } from 'lucide-react';
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from 'recharts';

const activityData = [
  { time: '00:00', activity: 5 },
  { time: '03:00', activity: 2 },
  { time: '06:00', activity: 12 },
  { time: '09:00', activity: 45 },
  { time: '12:00', activity: 62 },
  { time: '15:00', activity: 58 },
  { time: '18:00', activity: 38 },
  { time: '21:00', activity: 15 },
  { time: '23:59', activity: 8 },
];

const behaviorMetrics = [
  { metric: 'Login Timing', baseline: 85, current: 42, fullMark: 100 },
  { metric: 'Data Access', baseline: 75, current: 88, fullMark: 100 },
  { metric: 'Location', baseline: 95, current: 35, fullMark: 100 },
  { metric: 'Device Pattern', baseline: 90, current: 68, fullMark: 100 },
  { metric: 'Resource Usage', baseline: 70, current: 92, fullMark: 100 },
];

const suspiciousActivities = [
  { action: 'Downloaded 2.4GB of customer data', time: '2 hours ago', severity: 'Critical' },
  { action: 'Accessed restricted financial records', time: '5 hours ago', severity: 'High' },
  { action: 'Login from new location (Moscow, Russia)', time: '8 hours ago', severity: 'High' },
  { action: 'After-hours database queries', time: '12 hours ago', severity: 'Medium' },
  { action: 'Multiple failed authentication attempts', time: '1 day ago', severity: 'Medium' },
];

export function UserAnalysis() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-[#F8FAFC] mb-1" style={{ fontWeight: 700, fontSize: '28px', letterSpacing: '-0.02em' }}>
            User Intelligence Profile
          </h1>
          <p className="text-[#94A3B8] text-[14px]">Deep behavioral analysis and threat assessment</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="px-4 py-2 bg-[#1E293B] border border-[#1E293B] text-[#F8FAFC] rounded-lg text-[13px] hover:bg-[#1E293B]/70 transition-colors" style={{ fontWeight: 600 }}>
            View History
          </button>
          <button className="px-4 py-2 bg-[#EF4444] text-white rounded-lg text-[13px] hover:bg-[#EF4444]/90 transition-colors" style={{ fontWeight: 600 }}>
            Flag User
          </button>
        </div>
      </div>

      {/* User Profile Header */}
      <div className="bg-gradient-to-br from-[#111827]/80 to-[#1E293B]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-6">
        <div className="flex items-start gap-6">
          <div className="w-24 h-24 bg-gradient-to-br from-[#3B82F6] to-[#22D3EE] rounded-xl flex items-center justify-center">
            <User className="w-12 h-12 text-white" />
          </div>
          <div className="flex-1">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h2 className="text-[#F8FAFC] mb-1" style={{ fontWeight: 700, fontSize: '22px' }}>Michael Chen</h2>
                <p className="text-[#94A3B8] text-[14px] mb-1">USR-4782 • Senior Software Engineer</p>
                <p className="text-[#94A3B8] text-[13px]">Engineering Department • San Francisco, CA</p>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-center">
                  <div className="w-20 h-20 relative">
                    <svg className="w-20 h-20 transform -rotate-90">
                      <circle cx="40" cy="40" r="32" stroke="#1E293B" strokeWidth="6" fill="none" />
                      <circle
                        cx="40"
                        cy="40"
                        r="32"
                        stroke="#EF4444"
                        strokeWidth="6"
                        fill="none"
                        strokeDasharray={`${87 * 2.01} 201`}
                        className="transition-all duration-500"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-[#F8FAFC]" style={{ fontWeight: 700, fontSize: '18px' }}>87</span>
                    </div>
                  </div>
                  <p className="text-[#EF4444] text-[12px] mt-1" style={{ fontWeight: 600 }}>Risk Score</p>
                </div>
                <div className="text-center">
                  <div className="w-20 h-20 relative">
                    <svg className="w-20 h-20 transform -rotate-90">
                      <circle cx="40" cy="40" r="32" stroke="#1E293B" strokeWidth="6" fill="none" />
                      <circle
                        cx="40"
                        cy="40"
                        r="32"
                        stroke="#F59E0B"
                        strokeWidth="6"
                        fill="none"
                        strokeDasharray={`${42 * 2.01} 201`}
                        className="transition-all duration-500"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-[#F8FAFC]" style={{ fontWeight: 700, fontSize: '18px' }}>42%</span>
                    </div>
                  </div>
                  <p className="text-[#F59E0B] text-[12px] mt-1" style={{ fontWeight: 600 }}>Drift</p>
                </div>
              </div>
            </div>
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-[#0F172A]/50 border border-[#1E293B] rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <Clock className="w-4 h-4 text-[#22D3EE]" />
                  <span className="text-[#94A3B8] text-[11px]">Last Seen</span>
                </div>
                <p className="text-[#F8FAFC] text-[13px]" style={{ fontWeight: 600 }}>14 minutes ago</p>
              </div>
              <div className="bg-[#0F172A]/50 border border-[#1E293B] rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <MapPin className="w-4 h-4 text-[#22D3EE]" />
                  <span className="text-[#94A3B8] text-[11px]">Location</span>
                </div>
                <p className="text-[#F8FAFC] text-[13px]" style={{ fontWeight: 600 }}>Moscow, Russia</p>
              </div>
              <div className="bg-[#0F172A]/50 border border-[#1E293B] rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <Monitor className="w-4 h-4 text-[#22D3EE]" />
                  <span className="text-[#94A3B8] text-[11px]">Device</span>
                </div>
                <p className="text-[#F8FAFC] text-[13px]" style={{ fontWeight: 600 }}>MacBook Pro (New)</p>
              </div>
              <div className="bg-[#0F172A]/50 border border-[#1E293B] rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <Database className="w-4 h-4 text-[#22D3EE]" />
                  <span className="text-[#94A3B8] text-[11px]">Data Accessed</span>
                </div>
                <p className="text-[#F8FAFC] text-[13px]" style={{ fontWeight: 600 }}>2.4 GB Today</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {/* Activity Timeline */}
        <div className="col-span-2 bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-5">
          <h3 className="text-[#F8FAFC] mb-4" style={{ fontWeight: 600, fontSize: '16px' }}>24-Hour Activity Pattern</h3>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={activityData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
              <XAxis dataKey="time" stroke="#94A3B8" style={{ fontSize: '12px' }} />
              <YAxis stroke="#94A3B8" style={{ fontSize: '12px' }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0F172A', border: '1px solid #1E293B', borderRadius: '8px' }}
                labelStyle={{ color: '#F8FAFC' }}
              />
              <Line type="monotone" dataKey="activity" stroke="#3B82F6" strokeWidth={2} dot={{ fill: '#3B82F6', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Behavioral Deviation */}
        <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-5">
          <h3 className="text-[#F8FAFC] mb-4" style={{ fontWeight: 600, fontSize: '16px' }}>Behavior Deviation</h3>
          <ResponsiveContainer width="100%" height={240}>
            <RadarChart data={behaviorMetrics}>
              <PolarGrid stroke="#1E293B" />
              <PolarAngleAxis dataKey="metric" stroke="#94A3B8" style={{ fontSize: '10px' }} />
              <PolarRadiusAxis stroke="#94A3B8" />
              <Radar name="Baseline" dataKey="baseline" stroke="#10B981" fill="#10B981" fillOpacity={0.2} />
              <Radar name="Current" dataKey="current" stroke="#EF4444" fill="#EF4444" fillOpacity={0.3} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* AI Analysis */}
      <div className="bg-gradient-to-br from-[#3B82F6]/10 to-[#22D3EE]/5 border border-[#3B82F6]/20 rounded-xl p-5">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 bg-gradient-to-br from-[#3B82F6] to-[#22D3EE] rounded-lg flex items-center justify-center flex-shrink-0">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <div className="flex-1">
            <h3 className="text-[#F8FAFC] mb-2" style={{ fontWeight: 600, fontSize: '16px' }}>AI-Generated Threat Assessment</h3>
            <p className="text-[#F8FAFC] text-[14px] leading-relaxed mb-3">
              User exhibits <span className="text-[#EF4444]" style={{ fontWeight: 600 }}>significant behavioral drift</span> from established baseline patterns. Notable anomalies include access from a high-risk geographical location (Moscow, Russia), use of an unregistered device, and mass data download during non-business hours. The combination of these factors suggests potential data exfiltration activity.
            </p>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="text-[#94A3B8] text-[13px]">Confidence:</span>
                <span className="text-[#3B82F6] text-[13px]" style={{ fontWeight: 600 }}>94.7%</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[#94A3B8] text-[13px]">Model:</span>
                <span className="text-[#22D3EE] text-[13px]" style={{ fontWeight: 600 }}>DRISHTI-AI v2.4</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Suspicious Activities */}
      <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl overflow-hidden">
        <div className="p-5 border-b border-[#1E293B]">
          <h3 className="text-[#F8FAFC]" style={{ fontWeight: 600, fontSize: '16px' }}>Suspicious Activity Feed</h3>
        </div>
        <div className="divide-y divide-[#1E293B]">
          {suspiciousActivities.map((activity, i) => (
            <div key={i} className="p-4 hover:bg-[#1E293B]/30 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <AlertTriangle className={`w-5 h-5 mt-0.5 ${
                    activity.severity === 'Critical' ? 'text-[#EF4444]' :
                    activity.severity === 'High' ? 'text-[#F59E0B]' :
                    'text-[#3B82F6]'
                  }`} />
                  <div>
                    <p className="text-[#F8FAFC] text-[14px] mb-1">{activity.action}</p>
                    <p className="text-[#94A3B8] text-[12px]">{activity.time}</p>
                  </div>
                </div>
                <span className={`px-2.5 py-1 rounded-md text-[11px] ${
                  activity.severity === 'Critical' ? 'bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/20' :
                  activity.severity === 'High' ? 'bg-[#F59E0B]/10 text-[#F59E0B] border border-[#F59E0B]/20' :
                  'bg-[#3B82F6]/10 text-[#3B82F6] border border-[#3B82F6]/20'
                }`} style={{ fontWeight: 600 }}>
                  {activity.severity}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Deviating Features */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-5">
          <h3 className="text-[#F8FAFC] mb-4" style={{ fontWeight: 600, fontSize: '16px' }}>Top Deviating Features</h3>
          <div className="space-y-3">
            {[
              { feature: 'Login Geography', deviation: 92, color: '#EF4444' },
              { feature: 'Data Transfer Volume', deviation: 88, color: '#EF4444' },
              { feature: 'Access Time Pattern', deviation: 76, color: '#F59E0B' },
              { feature: 'Device Fingerprint', deviation: 64, color: '#F59E0B' },
              { feature: 'Resource Access Pattern', deviation: 52, color: '#3B82F6' },
            ].map((item, i) => (
              <div key={i}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[#F8FAFC] text-[13px]">{item.feature}</span>
                  <span className="text-[#F8FAFC] text-[13px]" style={{ fontWeight: 600 }}>{item.deviation}%</span>
                </div>
                <div className="h-2 bg-[#1E293B] rounded-full overflow-hidden">
                  <div
                    className="h-full transition-all duration-500"
                    style={{ width: `${item.deviation}%`, backgroundColor: item.color }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-5">
          <h3 className="text-[#F8FAFC] mb-4" style={{ fontWeight: 600, fontSize: '16px' }}>Threat Classification</h3>
          <div className="space-y-3">
            <div className="bg-[#EF4444]/10 border border-[#EF4444]/20 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>Data Exfiltration</span>
                <span className="text-[#EF4444] text-[13px]" style={{ fontWeight: 600 }}>95%</span>
              </div>
              <p className="text-[#94A3B8] text-[12px]">High probability of unauthorized data transfer</p>
            </div>
            <div className="bg-[#F59E0B]/10 border border-[#F59E0B]/20 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>Account Compromise</span>
                <span className="text-[#F59E0B] text-[13px]" style={{ fontWeight: 600 }}>78%</span>
              </div>
              <p className="text-[#94A3B8] text-[12px]">Unusual location and device indicate possible breach</p>
            </div>
            <div className="bg-[#3B82F6]/10 border border-[#3B82F6]/20 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>Policy Violation</span>
                <span className="text-[#3B82F6] text-[13px]" style={{ fontWeight: 600 }}>62%</span>
              </div>
              <p className="text-[#94A3B8] text-[12px]">After-hours access to restricted resources</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
