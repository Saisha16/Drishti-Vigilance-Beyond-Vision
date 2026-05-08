import { FileText, Download, Calendar, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react';

const weeklyReports = [
  { week: 'Week of May 1', threats: 142, critical: 8, resolved: 128, avgRisk: 58.4, trend: -5 },
  { week: 'Week of Apr 24', threats: 156, critical: 12, resolved: 138, avgRisk: 61.2, trend: 3 },
  { week: 'Week of Apr 17', threats: 149, critical: 9, resolved: 132, avgRisk: 59.8, trend: -2 },
  { week: 'Week of Apr 10', threats: 163, critical: 15, resolved: 145, avgRisk: 62.5, trend: 8 },
];

const monthlyMetrics = [
  { metric: 'Total Threats Detected', value: '610', change: '+2.3%', trend: 'up' },
  { metric: 'Critical Incidents', value: '44', change: '-8.4%', trend: 'down' },
  { metric: 'Average Response Time', value: '12 min', change: '-15.2%', trend: 'down' },
  { metric: 'False Positive Rate', value: '3.2%', change: '-1.8%', trend: 'down' },
  { metric: 'Users Flagged', value: '87', change: '+5.1%', trend: 'up' },
  { metric: 'Data Exfiltration Attempts', value: '23', change: '-12.3%', trend: 'down' },
];

export function Reports() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-[#F8FAFC] mb-1" style={{ fontWeight: 700, fontSize: '28px', letterSpacing: '-0.02em' }}>
            Intelligence Reports
          </h1>
          <p className="text-[#94A3B8] text-[14px]">Comprehensive security analytics and compliance metrics</p>
        </div>
        <div className="flex items-center gap-3">
          <select className="bg-[#111827] border border-[#1E293B] text-[#F8FAFC] px-4 py-2 rounded-lg text-[13px] focus:outline-none focus:border-[#3B82F6]">
            <option>Last 30 Days</option>
            <option>Last 90 Days</option>
            <option>Last Year</option>
          </select>
        </div>
      </div>

      {/* Quick Export */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gradient-to-br from-[#3B82F6]/10 to-[#22D3EE]/5 border border-[#3B82F6]/20 rounded-xl p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-[#3B82F6] to-[#22D3EE] rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <span className="px-3 py-1 bg-[#10B981]/10 border border-[#10B981]/20 text-[#10B981] rounded-md text-[11px]" style={{ fontWeight: 600 }}>
              READY
            </span>
          </div>
          <h3 className="text-[#F8FAFC] mb-2" style={{ fontWeight: 600, fontSize: '18px' }}>Weekly Threat Intelligence</h3>
          <p className="text-[#94A3B8] text-[13px] mb-4">Comprehensive analysis of threats detected in the past week</p>
          <button className="w-full flex items-center justify-center gap-2 bg-[#3B82F6] text-white px-4 py-2.5 rounded-lg hover:bg-[#3B82F6]/90 transition-colors text-[14px]" style={{ fontWeight: 600 }}>
            <Download className="w-4 h-4" />
            Export PDF Report
          </button>
        </div>

        <div className="bg-gradient-to-br from-[#F59E0B]/10 to-[#F59E0B]/5 border border-[#F59E0B]/20 rounded-xl p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-[#F59E0B] to-[#EF4444] rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-white" />
            </div>
            <span className="px-3 py-1 bg-[#10B981]/10 border border-[#10B981]/20 text-[#10B981] rounded-md text-[11px]" style={{ fontWeight: 600 }}>
              READY
            </span>
          </div>
          <h3 className="text-[#F8FAFC] mb-2" style={{ fontWeight: 600, fontSize: '18px' }}>Incident Response Log</h3>
          <p className="text-[#94A3B8] text-[13px] mb-4">Detailed log of all security incidents and response actions</p>
          <button className="w-full flex items-center justify-center gap-2 bg-[#F59E0B] text-white px-4 py-2.5 rounded-lg hover:bg-[#F59E0B]/90 transition-colors text-[14px]" style={{ fontWeight: 600 }}>
            <Download className="w-4 h-4" />
            Export CSV Data
          </button>
        </div>
      </div>

      {/* Monthly Analytics */}
      <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-[#F8FAFC]" style={{ fontWeight: 600, fontSize: '18px' }}>Monthly Security Metrics</h3>
          <div className="flex items-center gap-2 text-[#94A3B8] text-[13px]">
            <Calendar className="w-4 h-4" />
            <span>April 2026</span>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          {monthlyMetrics.map((metric, i) => (
            <div key={i} className="bg-[#0F172A]/50 border border-[#1E293B] rounded-lg p-4">
              <p className="text-[#94A3B8] text-[12px] mb-2">{metric.metric}</p>
              <div className="flex items-end justify-between">
                <p className="text-[#F8FAFC]" style={{ fontWeight: 700, fontSize: '24px' }}>{metric.value}</p>
                <div className={`flex items-center gap-1 ${
                  metric.trend === 'up' ? 'text-[#EF4444]' : 'text-[#10B981]'
                }`}>
                  {metric.trend === 'up' ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                  <span className="text-[12px]" style={{ fontWeight: 600 }}>{metric.change}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Weekly Reports */}
      <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl overflow-hidden">
        <div className="p-5 border-b border-[#1E293B]">
          <h3 className="text-[#F8FAFC]" style={{ fontWeight: 600, fontSize: '18px' }}>Weekly Intelligence Reports</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[#1E293B] bg-[#0F172A]/50">
                <th className="px-5 py-4 text-left text-[#94A3B8] text-[11px] uppercase tracking-wider" style={{ fontWeight: 600 }}>Period</th>
                <th className="px-5 py-4 text-left text-[#94A3B8] text-[11px] uppercase tracking-wider" style={{ fontWeight: 600 }}>Total Threats</th>
                <th className="px-5 py-4 text-left text-[#94A3B8] text-[11px] uppercase tracking-wider" style={{ fontWeight: 600 }}>Critical</th>
                <th className="px-5 py-4 text-left text-[#94A3B8] text-[11px] uppercase tracking-wider" style={{ fontWeight: 600 }}>Resolved</th>
                <th className="px-5 py-4 text-left text-[#94A3B8] text-[11px] uppercase tracking-wider" style={{ fontWeight: 600 }}>Avg Risk Score</th>
                <th className="px-5 py-4 text-left text-[#94A3B8] text-[11px] uppercase tracking-wider" style={{ fontWeight: 600 }}>Trend</th>
                <th className="px-5 py-4 text-left text-[#94A3B8] text-[11px] uppercase tracking-wider" style={{ fontWeight: 600 }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {weeklyReports.map((report, i) => (
                <tr key={i} className="border-b border-[#1E293B] hover:bg-[#1E293B]/30 transition-colors">
                  <td className="px-5 py-4 text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>{report.week}</td>
                  <td className="px-5 py-4 text-[#F8FAFC] text-[14px]">{report.threats}</td>
                  <td className="px-5 py-4">
                    <span className="px-2.5 py-1 bg-[#EF4444]/10 border border-[#EF4444]/20 text-[#EF4444] rounded-md text-[12px]" style={{ fontWeight: 600 }}>
                      {report.critical}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-[#10B981] text-[14px]" style={{ fontWeight: 600 }}>{report.resolved}</td>
                  <td className="px-5 py-4 text-[#F8FAFC] text-[14px]">{report.avgRisk}</td>
                  <td className="px-5 py-4">
                    <div className={`flex items-center gap-1 ${report.trend > 0 ? 'text-[#EF4444]' : 'text-[#10B981]'}`}>
                      {report.trend > 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                      <span className="text-[13px]" style={{ fontWeight: 600 }}>{Math.abs(report.trend)}%</span>
                    </div>
                  </td>
                  <td className="px-5 py-4">
                    <button className="text-[#3B82F6] hover:text-[#22D3EE] text-[13px] transition-colors flex items-center gap-1" style={{ fontWeight: 500 }}>
                      <Download className="w-4 h-4" />
                      Download
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Compliance Status */}
      <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-6">
        <h3 className="text-[#F8FAFC] mb-4" style={{ fontWeight: 600, fontSize: '18px' }}>Security Compliance Metrics</h3>
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center">
            <div className="w-24 h-24 mx-auto mb-3 relative">
              <svg className="w-24 h-24 transform -rotate-90">
                <circle cx="48" cy="48" r="40" stroke="#1E293B" strokeWidth="8" fill="none" />
                <circle
                  cx="48"
                  cy="48"
                  r="40"
                  stroke="#10B981"
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray={`${98 * 2.51} 251`}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-[#F8FAFC]" style={{ fontWeight: 700, fontSize: '20px' }}>98%</span>
              </div>
            </div>
            <p className="text-[#F8FAFC] text-[14px] mb-1" style={{ fontWeight: 600 }}>SOC 2 Compliance</p>
            <p className="text-[#10B981] text-[12px]">Compliant</p>
          </div>
          <div className="text-center">
            <div className="w-24 h-24 mx-auto mb-3 relative">
              <svg className="w-24 h-24 transform -rotate-90">
                <circle cx="48" cy="48" r="40" stroke="#1E293B" strokeWidth="8" fill="none" />
                <circle
                  cx="48"
                  cy="48"
                  r="40"
                  stroke="#10B981"
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray={`${95 * 2.51} 251`}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-[#F8FAFC]" style={{ fontWeight: 700, fontSize: '20px' }}>95%</span>
              </div>
            </div>
            <p className="text-[#F8FAFC] text-[14px] mb-1" style={{ fontWeight: 600 }}>GDPR Compliance</p>
            <p className="text-[#10B981] text-[12px]">Compliant</p>
          </div>
          <div className="text-center">
            <div className="w-24 h-24 mx-auto mb-3 relative">
              <svg className="w-24 h-24 transform -rotate-90">
                <circle cx="48" cy="48" r="40" stroke="#1E293B" strokeWidth="8" fill="none" />
                <circle
                  cx="48"
                  cy="48"
                  r="40"
                  stroke="#10B981"
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray={`${97 * 2.51} 251`}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-[#F8FAFC]" style={{ fontWeight: 700, fontSize: '20px' }}>97%</span>
              </div>
            </div>
            <p className="text-[#F8FAFC] text-[14px] mb-1" style={{ fontWeight: 600 }}>ISO 27001</p>
            <p className="text-[#10B981] text-[12px]">Compliant</p>
          </div>
          <div className="text-center">
            <div className="w-24 h-24 mx-auto mb-3 relative">
              <svg className="w-24 h-24 transform -rotate-90">
                <circle cx="48" cy="48" r="40" stroke="#1E293B" strokeWidth="8" fill="none" />
                <circle
                  cx="48"
                  cy="48"
                  r="40"
                  stroke="#F59E0B"
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray={`${88 * 2.51} 251`}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-[#F8FAFC]" style={{ fontWeight: 700, fontSize: '20px' }}>88%</span>
              </div>
            </div>
            <p className="text-[#F8FAFC] text-[14px] mb-1" style={{ fontWeight: 600 }}>HIPAA Compliance</p>
            <p className="text-[#F59E0B] text-[12px]">Needs Attention</p>
          </div>
        </div>
      </div>
    </div>
  );
}
