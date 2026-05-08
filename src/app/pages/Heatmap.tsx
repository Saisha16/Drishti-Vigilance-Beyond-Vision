import { useState } from 'react';
import { ZoomIn, ZoomOut, Filter, Download } from 'lucide-react';

const users = [
  'USR-1234', 'USR-2345', 'USR-3456', 'USR-4567', 'USR-5678',
  'USR-6789', 'USR-7890', 'USR-8901', 'USR-9012', 'USR-0123',
  'USR-1235', 'USR-2346', 'USR-3457', 'USR-4568', 'USR-5679'
];

const timeSlots = [
  '00:00', '02:00', '04:00', '06:00', '08:00', '10:00',
  '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'
];

const generateHeatmapData = () => {
  return users.map(user =>
    timeSlots.map(() => Math.floor(Math.random() * 100))
  );
};

const getHeatColor = (value: number) => {
  if (value >= 80) return 'bg-[#EF4444]';
  if (value >= 60) return 'bg-[#F59E0B]';
  if (value >= 40) return 'bg-[#3B82F6]';
  if (value >= 20) return 'bg-[#22D3EE]';
  return 'bg-[#1E293B]';
};

export function Heatmap() {
  const [heatmapData] = useState(generateHeatmapData());
  const [zoom, setZoom] = useState(1);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-[#F8FAFC] mb-1" style={{ fontWeight: 700, fontSize: '28px', letterSpacing: '-0.02em' }}>
            Behavioral Heatmap
          </h1>
          <p className="text-[#94A3B8] text-[14px]">Real-time user activity and risk clustering visualization</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-[#1E293B] border border-[#1E293B] text-[#F8FAFC] rounded-lg text-[13px] hover:bg-[#1E293B]/70 transition-colors" style={{ fontWeight: 600 }}>
            <Filter className="w-4 h-4" />
            Filter
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-[#3B82F6] text-white rounded-lg text-[13px] hover:bg-[#3B82F6]/90 transition-colors" style={{ fontWeight: 600 }}>
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-[#94A3B8] text-[13px]">Time Range:</span>
              <select className="bg-[#0F172A] border border-[#1E293B] text-[#F8FAFC] px-3 py-1.5 rounded-lg text-[13px] focus:outline-none focus:border-[#3B82F6]">
                <option>Last 24 Hours</option>
                <option>Last 7 Days</option>
                <option>Last 30 Days</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[#94A3B8] text-[13px]">Department:</span>
              <select className="bg-[#0F172A] border border-[#1E293B] text-[#F8FAFC] px-3 py-1.5 rounded-lg text-[13px] focus:outline-none focus:border-[#3B82F6]">
                <option>All Departments</option>
                <option>Engineering</option>
                <option>Sales</option>
                <option>Finance</option>
              </select>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setZoom(Math.max(0.5, zoom - 0.1))}
              className="p-2 bg-[#1E293B] border border-[#1E293B] text-[#F8FAFC] rounded-lg hover:bg-[#1E293B]/70 transition-colors"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <span className="text-[#94A3B8] text-[13px] min-w-[50px] text-center">{Math.round(zoom * 100)}%</span>
            <button
              onClick={() => setZoom(Math.min(2, zoom + 0.1))}
              className="p-2 bg-[#1E293B] border border-[#1E293B] text-[#F8FAFC] rounded-lg hover:bg-[#1E293B]/70 transition-colors"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-4">
        <div className="flex items-center justify-between">
          <span className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>Risk Level:</span>
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-[#1E293B] rounded"></div>
              <span className="text-[#94A3B8] text-[12px]">Low (0-20)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-[#22D3EE] rounded"></div>
              <span className="text-[#94A3B8] text-[12px]">Medium (20-40)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-[#3B82F6] rounded"></div>
              <span className="text-[#94A3B8] text-[12px]">Elevated (40-60)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-[#F59E0B] rounded"></div>
              <span className="text-[#94A3B8] text-[12px]">High (60-80)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-[#EF4444] rounded"></div>
              <span className="text-[#94A3B8] text-[12px]">Critical (80-100)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Heatmap */}
      <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-5 overflow-auto">
        <div style={{ transform: `scale(${zoom})`, transformOrigin: 'top left' }}>
          <div className="inline-block">
            <div className="flex gap-1 mb-2 ml-20">
              {timeSlots.map((time, i) => (
                <div key={i} className="w-16 text-center">
                  <span className="text-[#94A3B8] text-[11px]">{time}</span>
                </div>
              ))}
            </div>
            {users.map((user, userIndex) => (
              <div key={userIndex} className="flex gap-1 mb-1">
                <div className="w-20 flex items-center">
                  <span className="text-[#94A3B8] text-[11px]" style={{ fontWeight: 500 }}>{user}</span>
                </div>
                {heatmapData[userIndex].map((value, timeIndex) => (
                  <div
                    key={timeIndex}
                    className={`w-16 h-10 ${getHeatColor(value)} rounded cursor-pointer hover:ring-2 hover:ring-[#22D3EE] transition-all relative group`}
                  >
                    <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                      <span className="text-white text-[10px]" style={{ fontWeight: 600 }}>{value}</span>
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Risk Clusters */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-[#EF4444]/10 to-[#EF4444]/5 border border-[#EF4444]/20 rounded-xl p-5">
          <h3 className="text-[#F8FAFC] mb-3" style={{ fontWeight: 600, fontSize: '16px' }}>Critical Risk Cluster</h3>
          <p className="text-[#F8FAFC] mb-2" style={{ fontWeight: 700, fontSize: '28px' }}>8 Users</p>
          <p className="text-[#94A3B8] text-[13px] mb-4">Peak activity: 02:00 - 04:00</p>
          <div className="space-y-2">
            {['USR-4782', 'USR-3291', 'USR-5614'].map((user, i) => (
              <div key={i} className="flex items-center justify-between text-[12px]">
                <span className="text-[#F8FAFC]">{user}</span>
                <span className="text-[#EF4444]" style={{ fontWeight: 600 }}>Risk: {95 - i * 5}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gradient-to-br from-[#F59E0B]/10 to-[#F59E0B]/5 border border-[#F59E0B]/20 rounded-xl p-5">
          <h3 className="text-[#F8FAFC] mb-3" style={{ fontWeight: 600, fontSize: '16px' }}>High Risk Cluster</h3>
          <p className="text-[#F8FAFC] mb-2" style={{ fontWeight: 700, fontSize: '28px' }}>15 Users</p>
          <p className="text-[#94A3B8] text-[13px] mb-4">Peak activity: 18:00 - 20:00</p>
          <div className="space-y-2">
            {['USR-2847', 'USR-6923', 'USR-1456'].map((user, i) => (
              <div key={i} className="flex items-center justify-between text-[12px]">
                <span className="text-[#F8FAFC]">{user}</span>
                <span className="text-[#F59E0B]" style={{ fontWeight: 600 }}>Risk: {72 - i * 4}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gradient-to-br from-[#3B82F6]/10 to-[#3B82F6]/5 border border-[#3B82F6]/20 rounded-xl p-5">
          <h3 className="text-[#F8FAFC] mb-3" style={{ fontWeight: 600, fontSize: '16px' }}>Normal Activity</h3>
          <p className="text-[#F8FAFC] mb-2" style={{ fontWeight: 700, fontSize: '28px' }}>2,824 Users</p>
          <p className="text-[#94A3B8] text-[13px] mb-4">Peak activity: 10:00 - 16:00</p>
          <p className="text-[#10B981] text-[13px]" style={{ fontWeight: 600 }}>
            98.9% of users within normal behavioral patterns
          </p>
        </div>
      </div>
    </div>
  );
}
