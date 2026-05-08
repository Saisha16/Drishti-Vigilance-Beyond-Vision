import { Search, Bell, Activity, User } from 'lucide-react';

export function Navbar() {
  return (
    <header className="h-16 bg-[#0F172A] border-b border-[#1E293B] fixed top-0 right-0 left-64 z-10">
      <div className="h-full px-6 flex items-center justify-between">
        <div className="flex-1 max-w-xl">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#94A3B8]" />
            <input
              type="text"
              placeholder="Search threats, users, or alerts..."
              className="w-full bg-[#111827] border border-[#1E293B] rounded-lg pl-10 pr-4 py-2 text-[#F8FAFC] placeholder:text-[#94A3B8] focus:outline-none focus:border-[#3B82F6] transition-colors text-[14px]"
            />
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-[#10B981]/10 border border-[#10B981]/30 rounded-full">
            <div className="w-2 h-2 bg-[#10B981] rounded-full animate-pulse"></div>
            <span className="text-[12px] text-[#10B981]" style={{ fontWeight: 600 }}>LIVE MONITORING</span>
          </div>

          <div className="relative">
            <Bell className="w-5 h-5 text-[#94A3B8] hover:text-[#F8FAFC] cursor-pointer transition-colors" />
            <div className="absolute -top-1 -right-1 w-4 h-4 bg-[#EF4444] rounded-full flex items-center justify-center">
              <span className="text-[10px] text-white" style={{ fontWeight: 700 }}>3</span>
            </div>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 bg-[#111827] border border-[#1E293B] rounded-lg">
            <Activity className="w-4 h-4 text-[#22D3EE]" />
            <span className="text-[12px] text-[#F8FAFC]" style={{ fontWeight: 500 }}>AI Active</span>
          </div>

          <div className="h-8 w-px bg-[#1E293B]"></div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-[13px] text-[#F8FAFC]" style={{ fontWeight: 600 }}>Sarah Chen</p>
              <p className="text-[11px] text-[#94A3B8]">Security Analyst</p>
            </div>
            <div className="w-9 h-9 bg-gradient-to-br from-[#3B82F6] to-[#22D3EE] rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-white" />
            </div>
          </div>

          <div className="px-3 py-1.5 bg-[#F59E0B]/10 border border-[#F59E0B]/30 rounded-lg">
            <span className="text-[12px] text-[#F59E0B]" style={{ fontWeight: 600 }}>THREAT LEVEL: MEDIUM</span>
          </div>
        </div>
      </div>
    </header>
  );
}
