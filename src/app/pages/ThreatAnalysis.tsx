import { Brain, Clock, FileText, MapPin, AlertTriangle, CheckCircle } from 'lucide-react';
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

const timelineData = [
  { time: '08:00', risk: 12 },
  { time: '10:00', risk: 18 },
  { time: '12:00', risk: 42 },
  { time: '14:00', risk: 68 },
  { time: '16:00', risk: 87 },
  { time: '18:00', risk: 92 },
  { time: '20:00', risk: 85 },
];

const evidenceItems = [
  { type: 'Location Anomaly', severity: 'Critical', details: 'Login from Moscow, Russia - 8,427 miles from usual location', time: '2 hours ago' },
  { type: 'Data Transfer', severity: 'Critical', details: 'Downloaded 2.4GB of customer database records', time: '2 hours ago' },
  { type: 'Device Change', severity: 'High', details: 'New MacBook Pro detected - unregistered device', time: '3 hours ago' },
  { type: 'Access Pattern', severity: 'High', details: 'After-hours database queries (02:00 - 04:00 AM)', time: '5 hours ago' },
  { type: 'Resource Access', severity: 'Medium', details: 'Accessed restricted financial records', time: '6 hours ago' },
];

export function ThreatAnalysis() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-[#F8FAFC] mb-1" style={{ fontWeight: 700, fontSize: '28px', letterSpacing: '-0.02em' }}>
            Threat Analysis
          </h1>
          <p className="text-[#94A3B8] text-[14px]">Deep dive investigation and behavioral reconstruction</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="px-4 py-2 bg-[#1E293B] border border-[#1E293B] text-[#F8FAFC] rounded-lg text-[13px] hover:bg-[#1E293B]/70 transition-colors" style={{ fontWeight: 600 }}>
            Export Analysis
          </button>
          <button className="px-4 py-2 bg-[#EF4444] text-white rounded-lg text-[13px] hover:bg-[#EF4444]/90 transition-colors" style={{ fontWeight: 600 }}>
            Escalate Threat
          </button>
        </div>
      </div>

      {/* Threat Summary */}
      <div className="bg-gradient-to-br from-[#EF4444]/10 to-[#EF4444]/5 border border-[#EF4444]/20 rounded-xl p-6">
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 bg-[#EF4444]/20 rounded-xl flex items-center justify-center flex-shrink-0">
            <AlertTriangle className="w-7 h-7 text-[#EF4444]" />
          </div>
          <div className="flex-1">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h2 className="text-[#F8FAFC] mb-1" style={{ fontWeight: 700, fontSize: '20px' }}>Mass Data Exfiltration Attempt</h2>
                <p className="text-[#94A3B8] text-[14px]">Threat ID: THR-2024-0847 • Detected: May 8, 2026 at 14:23 UTC</p>
              </div>
              <span className="px-3 py-1.5 bg-[#EF4444]/10 border border-[#EF4444]/20 text-[#EF4444] rounded-lg text-[12px]" style={{ fontWeight: 600 }}>
                CRITICAL SEVERITY
              </span>
            </div>
            <div className="grid grid-cols-4 gap-4">
              <div>
                <p className="text-[#94A3B8] text-[11px] mb-1">Risk Score</p>
                <p className="text-[#F8FAFC]" style={{ fontWeight: 700, fontSize: '20px' }}>87</p>
              </div>
              <div>
                <p className="text-[#94A3B8] text-[11px] mb-1">Confidence</p>
                <p className="text-[#F8FAFC]" style={{ fontWeight: 700, fontSize: '20px' }}>94.7%</p>
              </div>
              <div>
                <p className="text-[#94A3B8] text-[11px] mb-1">User</p>
                <p className="text-[#F8FAFC]" style={{ fontWeight: 700, fontSize: '16px' }}>USR-4782</p>
              </div>
              <div>
                <p className="text-[#94A3B8] text-[11px] mb-1">Status</p>
                <p className="text-[#F59E0B]" style={{ fontWeight: 700, fontSize: '16px' }}>Under Investigation</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Analysis */}
      <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-gradient-to-br from-[#3B82F6] to-[#22D3EE] rounded-lg flex items-center justify-center">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <h3 className="text-[#F8FAFC]" style={{ fontWeight: 600, fontSize: '18px' }}>Explainable AI Analysis</h3>
        </div>
        <div className="bg-[#0F172A]/50 border border-[#1E293B] rounded-lg p-5">
          <p className="text-[#F8FAFC] text-[14px] leading-relaxed mb-4">
            The behavioral analysis engine has detected a <span className="text-[#EF4444]" style={{ fontWeight: 600 }}>significant deviation</span> from established baseline patterns for user USR-4782 (Michael Chen). The threat classification model indicates a <span className="text-[#EF4444]" style={{ fontWeight: 600 }}>95% probability</span> of malicious data exfiltration based on the following key indicators:
          </p>
          <ul className="space-y-2 text-[#F8FAFC] text-[14px]">
            <li className="flex items-start gap-2">
              <span className="text-[#EF4444] mt-1">•</span>
              <span><span style={{ fontWeight: 600 }}>Geographical anomaly:</span> Login from Moscow, Russia represents a 100% deviation from typical access patterns (San Francisco, CA)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[#EF4444] mt-1">•</span>
              <span><span style={{ fontWeight: 600 }}>Volume anomaly:</span> Downloaded 2.4GB of data, 847% above the user's 30-day average of 0.28GB</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[#EF4444] mt-1">•</span>
              <span><span style={{ fontWeight: 600 }}>Temporal anomaly:</span> Database queries executed at 02:00-04:00 AM, outside normal working hours</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[#EF4444] mt-1">•</span>
              <span><span style={{ fontWeight: 600 }}>Device fingerprint mismatch:</span> New unregistered MacBook Pro detected, diverging from established device profile</span>
            </li>
          </ul>
          <div className="mt-4 pt-4 border-t border-[#1E293B] flex items-center justify-between">
            <span className="text-[#94A3B8] text-[13px]">Model: DRISHTI-AI v2.4 • Ensemble Decision Tree + Neural Network</span>
            <span className="text-[#22D3EE] text-[13px]" style={{ fontWeight: 600 }}>Confidence: 94.7%</span>
          </div>
        </div>
      </div>

      {/* Timeline Reconstruction */}
      <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <Clock className="w-5 h-5 text-[#3B82F6]" />
          <h3 className="text-[#F8FAFC]" style={{ fontWeight: 600, fontSize: '18px' }}>Timeline Reconstruction</h3>
        </div>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={timelineData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
            <XAxis dataKey="time" stroke="#94A3B8" style={{ fontSize: '12px' }} />
            <YAxis stroke="#94A3B8" style={{ fontSize: '12px' }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#0F172A', border: '1px solid #1E293B', borderRadius: '8px' }}
              labelStyle={{ color: '#F8FAFC' }}
            />
            <Line type="monotone" dataKey="risk" stroke="#EF4444" strokeWidth={3} dot={{ fill: '#EF4444', r: 5 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Evidence Cards */}
        <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <FileText className="w-5 h-5 text-[#3B82F6]" />
            <h3 className="text-[#F8FAFC]" style={{ fontWeight: 600, fontSize: '18px' }}>Evidence Chain</h3>
          </div>
          <div className="space-y-3">
            {evidenceItems.map((item, i) => (
              <div key={i} className="bg-[#0F172A]/50 border border-[#1E293B] rounded-lg p-4 hover:border-[#3B82F6]/30 transition-colors">
                <div className="flex items-start justify-between mb-2">
                  <span className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>{item.type}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] ${
                    item.severity === 'Critical' ? 'bg-[#EF4444]/10 text-[#EF4444]' :
                    item.severity === 'High' ? 'bg-[#F59E0B]/10 text-[#F59E0B]' :
                    'bg-[#3B82F6]/10 text-[#3B82F6]'
                  }`} style={{ fontWeight: 600 }}>
                    {item.severity}
                  </span>
                </div>
                <p className="text-[#94A3B8] text-[12px] mb-1">{item.details}</p>
                <p className="text-[#94A3B8] text-[11px]">{item.time}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Behavioral Changes */}
        <div className="space-y-4">
          <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <MapPin className="w-5 h-5 text-[#3B82F6]" />
              <h3 className="text-[#F8FAFC]" style={{ fontWeight: 600, fontSize: '18px' }}>Behavioral Changes</h3>
            </div>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-[#EF4444]/10 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                  <AlertTriangle className="w-4 h-4 text-[#EF4444]" />
                </div>
                <div>
                  <p className="text-[#F8FAFC] text-[13px] mb-1" style={{ fontWeight: 600 }}>Location Drift: 100%</p>
                  <p className="text-[#94A3B8] text-[12px]">Switched from San Francisco, CA to Moscow, Russia</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-[#EF4444]/10 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                  <AlertTriangle className="w-4 h-4 text-[#EF4444]" />
                </div>
                <div>
                  <p className="text-[#F8FAFC] text-[13px] mb-1" style={{ fontWeight: 600 }}>Volume Drift: 847%</p>
                  <p className="text-[#94A3B8] text-[12px]">Data transfer volume 8.5x above baseline</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-[#F59E0B]/10 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                  <AlertTriangle className="w-4 h-4 text-[#F59E0B]" />
                </div>
                <div>
                  <p className="text-[#F8FAFC] text-[13px] mb-1" style={{ fontWeight: 600 }}>Time Drift: 76%</p>
                  <p className="text-[#94A3B8] text-[12px]">Activity during unusual hours (02:00-04:00 AM)</p>
                </div>
              </div>
            </div>
          </div>

          {/* Analyst Notes */}
          <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-6">
            <h3 className="text-[#F8FAFC] mb-3" style={{ fontWeight: 600, fontSize: '16px' }}>Analyst Notes</h3>
            <textarea
              placeholder="Add your investigation notes here..."
              rows={4}
              className="w-full bg-[#0F172A] border border-[#1E293B] rounded-lg px-4 py-3 text-[#F8FAFC] placeholder:text-[#94A3B8] focus:outline-none focus:border-[#3B82F6] text-[13px] resize-none"
            ></textarea>
            <button className="mt-3 w-full bg-[#3B82F6] text-white py-2 rounded-lg text-[13px] hover:bg-[#3B82F6]/90 transition-colors" style={{ fontWeight: 600 }}>
              Save Notes
            </button>
          </div>
        </div>
      </div>

      {/* Action Workflow */}
      <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-6">
        <h3 className="text-[#F8FAFC] mb-4" style={{ fontWeight: 600, fontSize: '18px' }}>Escalation Workflow</h3>
        <div className="grid grid-cols-4 gap-3">
          <button className="flex items-center justify-center gap-2 bg-[#10B981]/10 border border-[#10B981]/20 text-[#10B981] px-4 py-3 rounded-lg hover:bg-[#10B981]/20 transition-colors text-[13px]" style={{ fontWeight: 600 }}>
            <CheckCircle className="w-4 h-4" />
            Mark as False Positive
          </button>
          <button className="flex items-center justify-center gap-2 bg-[#3B82F6]/10 border border-[#3B82F6]/20 text-[#3B82F6] px-4 py-3 rounded-lg hover:bg-[#3B82F6]/20 transition-colors text-[13px]" style={{ fontWeight: 600 }}>
            <Clock className="w-4 h-4" />
            Continue Monitoring
          </button>
          <button className="flex items-center justify-center gap-2 bg-[#F59E0B]/10 border border-[#F59E0B]/20 text-[#F59E0B] px-4 py-3 rounded-lg hover:bg-[#F59E0B]/20 transition-colors text-[13px]" style={{ fontWeight: 600 }}>
            <AlertTriangle className="w-4 h-4" />
            Suspend User Access
          </button>
          <button className="flex items-center justify-center gap-2 bg-[#EF4444]/10 border border-[#EF4444]/20 text-[#EF4444] px-4 py-3 rounded-lg hover:bg-[#EF4444]/20 transition-colors text-[13px]" style={{ fontWeight: 600 }}>
            <AlertTriangle className="w-4 h-4" />
            Escalate to SOC
          </button>
        </div>
      </div>
    </div>
  );
}
