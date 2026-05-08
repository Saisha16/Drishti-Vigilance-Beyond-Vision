import { Search, Filter, Download, AlertTriangle, Clock, User } from 'lucide-react';
import { useState } from 'react';

const allAlerts = [
  { id: 'ALT-9847', userId: 'USR-4782', name: 'Michael Chen', threat: 'Mass Data Download', risk: 87, drift: '42%', status: 'Critical', time: '2 min ago', category: 'Data Exfiltration' },
  { id: 'ALT-9846', userId: 'USR-3291', name: 'Sarah Williams', threat: 'After-Hours Access', risk: 72, drift: '38%', status: 'High', time: '18 min ago', category: 'Unauthorized Access' },
  { id: 'ALT-9845', userId: 'USR-5614', name: 'David Martinez', threat: 'Unusual Login Pattern', risk: 64, drift: '31%', status: 'High', time: '1 hr ago', category: 'Anomalous Behavior' },
  { id: 'ALT-9844', userId: 'USR-2847', name: 'Emma Johnson', threat: 'Policy Breach', risk: 51, drift: '22%', status: 'Medium', time: '2 hrs ago', category: 'Policy Violations' },
  { id: 'ALT-9843', userId: 'USR-6923', name: 'James Wilson', threat: 'Resource Anomaly', risk: 43, drift: '18%', status: 'Medium', time: '3 hrs ago', category: 'Anomalous Behavior' },
  { id: 'ALT-9842', userId: 'USR-1456', name: 'Lisa Anderson', threat: 'Suspicious File Transfer', risk: 76, drift: '35%', status: 'High', time: '4 hrs ago', category: 'Data Exfiltration' },
  { id: 'ALT-9841', userId: 'USR-7834', name: 'Robert Taylor', threat: 'Failed Authentication Attempts', risk: 58, drift: '27%', status: 'Medium', time: '5 hrs ago', category: 'Unauthorized Access' },
  { id: 'ALT-9840', userId: 'USR-4521', name: 'Jennifer Brown', threat: 'Geographical Anomaly', risk: 82, drift: '41%', status: 'Critical', time: '6 hrs ago', category: 'Anomalous Behavior' },
];

export function Alerts() {
  const [filterStatus, setFilterStatus] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredAlerts = allAlerts.filter(alert => {
    const matchesStatus = filterStatus === 'All' || alert.status === filterStatus;
    const matchesSearch = alert.userId.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         alert.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         alert.threat.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-[#F8FAFC] mb-1" style={{ fontWeight: 700, fontSize: '28px', letterSpacing: '-0.02em' }}>
            Active Alerts
          </h1>
          <p className="text-[#94A3B8] text-[14px]">Monitor and manage security threats in real-time</p>
        </div>
        <button className="flex items-center gap-2 bg-[#3B82F6] text-white px-4 py-2 rounded-lg text-[13px] hover:bg-[#3B82F6]/90 transition-colors" style={{ fontWeight: 600 }}>
          <Download className="w-4 h-4" />
          Export Alerts
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-[#EF4444]/10 to-[#EF4444]/5 border border-[#EF4444]/20 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <AlertTriangle className="w-5 h-5 text-[#EF4444]" />
            <span className="text-[#EF4444] text-[11px]" style={{ fontWeight: 600 }}>CRITICAL</span>
          </div>
          <p className="text-[#F8FAFC] mb-1" style={{ fontWeight: 700, fontSize: '24px' }}>2</p>
          <p className="text-[#94A3B8] text-[12px]">Requires immediate action</p>
        </div>
        <div className="bg-gradient-to-br from-[#F59E0B]/10 to-[#F59E0B]/5 border border-[#F59E0B]/20 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <AlertTriangle className="w-5 h-5 text-[#F59E0B]" />
            <span className="text-[#F59E0B] text-[11px]" style={{ fontWeight: 600 }}>HIGH</span>
          </div>
          <p className="text-[#F8FAFC] mb-1" style={{ fontWeight: 700, fontSize: '24px' }}>4</p>
          <p className="text-[#94A3B8] text-[12px]">Needs investigation</p>
        </div>
        <div className="bg-gradient-to-br from-[#3B82F6]/10 to-[#3B82F6]/5 border border-[#3B82F6]/20 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <AlertTriangle className="w-5 h-5 text-[#3B82F6]" />
            <span className="text-[#3B82F6] text-[11px]" style={{ fontWeight: 600 }}>MEDIUM</span>
          </div>
          <p className="text-[#F8FAFC] mb-1" style={{ fontWeight: 700, fontSize: '24px' }}>2</p>
          <p className="text-[#94A3B8] text-[12px]">Monitor closely</p>
        </div>
        <div className="bg-gradient-to-br from-[#22D3EE]/10 to-[#22D3EE]/5 border border-[#22D3EE]/20 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <Clock className="w-5 h-5 text-[#22D3EE]" />
            <span className="text-[#22D3EE] text-[11px]" style={{ fontWeight: 600 }}>24H AVG</span>
          </div>
          <p className="text-[#F8FAFC] mb-1" style={{ fontWeight: 700, fontSize: '24px' }}>18.4</p>
          <p className="text-[#94A3B8] text-[12px]">Alerts per day</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-4">
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#94A3B8]" />
            <input
              type="text"
              placeholder="Search by user ID, name, or threat type..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-[#0F172A] border border-[#1E293B] rounded-lg pl-10 pr-4 py-2 text-[#F8FAFC] placeholder:text-[#94A3B8] focus:outline-none focus:border-[#3B82F6] transition-colors text-[13px]"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-[#94A3B8]" />
            <span className="text-[#94A3B8] text-[13px]">Filter:</span>
            {['All', 'Critical', 'High', 'Medium'].map((status) => (
              <button
                key={status}
                onClick={() => setFilterStatus(status)}
                className={`px-3 py-1.5 rounded-lg text-[12px] transition-colors ${
                  filterStatus === status
                    ? 'bg-[#3B82F6] text-white'
                    : 'bg-[#1E293B] text-[#94A3B8] hover:bg-[#1E293B]/70'
                }`}
                style={{ fontWeight: 500 }}
              >
                {status}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[#1E293B] bg-[#0F172A]/50">
                <th className="px-5 py-4 text-left text-[#94A3B8] text-[11px] uppercase tracking-wider" style={{ fontWeight: 600 }}>Alert ID</th>
                <th className="px-5 py-4 text-left text-[#94A3B8] text-[11px] uppercase tracking-wider" style={{ fontWeight: 600 }}>User</th>
                <th className="px-5 py-4 text-left text-[#94A3B8] text-[11px] uppercase tracking-wider" style={{ fontWeight: 600 }}>Threat Type</th>
                <th className="px-5 py-4 text-left text-[#94A3B8] text-[11px] uppercase tracking-wider" style={{ fontWeight: 600 }}>Category</th>
                <th className="px-5 py-4 text-left text-[#94A3B8] text-[11px] uppercase tracking-wider" style={{ fontWeight: 600 }}>Risk Score</th>
                <th className="px-5 py-4 text-left text-[#94A3B8] text-[11px] uppercase tracking-wider" style={{ fontWeight: 600 }}>Drift</th>
                <th className="px-5 py-4 text-left text-[#94A3B8] text-[11px] uppercase tracking-wider" style={{ fontWeight: 600 }}>Status</th>
                <th className="px-5 py-4 text-left text-[#94A3B8] text-[11px] uppercase tracking-wider" style={{ fontWeight: 600 }}>Timestamp</th>
                <th className="px-5 py-4 text-left text-[#94A3B8] text-[11px] uppercase tracking-wider" style={{ fontWeight: 600 }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredAlerts.map((alert, i) => (
                <tr key={i} className="border-b border-[#1E293B] hover:bg-[#1E293B]/30 transition-colors">
                  <td className="px-5 py-4 text-[#3B82F6] text-[13px]" style={{ fontWeight: 600 }}>{alert.id}</td>
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-gradient-to-br from-[#3B82F6] to-[#22D3EE] rounded-full flex items-center justify-center">
                        <User className="w-4 h-4 text-white" />
                      </div>
                      <div>
                        <p className="text-[#F8FAFC] text-[13px]" style={{ fontWeight: 600 }}>{alert.name}</p>
                        <p className="text-[#94A3B8] text-[11px]">{alert.userId}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-4 text-[#F8FAFC] text-[13px]">{alert.threat}</td>
                  <td className="px-5 py-4">
                    <span className="text-[#94A3B8] text-[12px]">{alert.category}</span>
                  </td>
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-1.5 bg-[#1E293B] rounded-full overflow-hidden max-w-[100px]">
                        <div
                          className={`h-full ${alert.risk >= 80 ? 'bg-[#EF4444]' : alert.risk >= 60 ? 'bg-[#F59E0B]' : 'bg-[#10B981]'}`}
                          style={{ width: `${alert.risk}%` }}
                        ></div>
                      </div>
                      <span className="text-[#F8FAFC] text-[13px] min-w-[30px]" style={{ fontWeight: 600 }}>{alert.risk}</span>
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
                    <button className="px-3 py-1.5 bg-[#3B82F6]/10 border border-[#3B82F6]/20 text-[#3B82F6] rounded-lg hover:bg-[#3B82F6]/20 text-[12px] transition-colors" style={{ fontWeight: 500 }}>
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
