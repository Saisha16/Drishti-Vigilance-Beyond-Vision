import { User, Bell, Shield, Database, Monitor, Globe } from 'lucide-react';

export function Settings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-[#F8FAFC] mb-1" style={{ fontWeight: 700, fontSize: '28px', letterSpacing: '-0.02em' }}>
          Settings
        </h1>
        <p className="text-[#94A3B8] text-[14px]">Manage your account and system preferences</p>
      </div>

      {/* Profile Settings */}
      <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-6">
        <h3 className="text-[#F8FAFC] mb-6" style={{ fontWeight: 600, fontSize: '18px' }}>Profile Settings</h3>

        <div className="flex items-start gap-6 mb-6">
          <div className="w-20 h-20 bg-gradient-to-br from-[#3B82F6] to-[#22D3EE] rounded-full flex items-center justify-center">
            <User className="w-10 h-10 text-white" />
          </div>
          <div className="flex-1 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-[#94A3B8] text-[12px] mb-2">Full Name</label>
                <input
                  type="text"
                  defaultValue="Sarah Chen"
                  className="w-full bg-[#0F172A] border border-[#1E293B] rounded-lg px-4 py-2 text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6] text-[14px]"
                />
              </div>
              <div>
                <label className="block text-[#94A3B8] text-[12px] mb-2">Role</label>
                <input
                  type="text"
                  defaultValue="Security Analyst"
                  className="w-full bg-[#0F172A] border border-[#1E293B] rounded-lg px-4 py-2 text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6] text-[14px]"
                />
              </div>
            </div>
            <div>
              <label className="block text-[#94A3B8] text-[12px] mb-2">Email Address</label>
              <input
                type="email"
                defaultValue="sarah.chen@company.com"
                className="w-full bg-[#0F172A] border border-[#1E293B] rounded-lg px-4 py-2 text-[#F8FAFC] focus:outline-none focus:border-[#3B82F6] text-[14px]"
              />
            </div>
          </div>
        </div>

        <button className="bg-[#3B82F6] text-white px-4 py-2 rounded-lg text-[13px] hover:bg-[#3B82F6]/90 transition-colors" style={{ fontWeight: 600 }}>
          Update Profile
        </button>
      </div>

      {/* Notification Preferences */}
      <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-6">
        <div className="flex items-center gap-3 mb-6">
          <Bell className="w-5 h-5 text-[#3B82F6]" />
          <h3 className="text-[#F8FAFC]" style={{ fontWeight: 600, fontSize: '18px' }}>Notification Preferences</h3>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between py-3 border-b border-[#1E293B]">
            <div>
              <p className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>Critical Alerts</p>
              <p className="text-[#94A3B8] text-[12px] mt-1">Immediate notification for critical threats</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-[#1E293B] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#3B82F6]"></div>
            </label>
          </div>

          <div className="flex items-center justify-between py-3 border-b border-[#1E293B]">
            <div>
              <p className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>Daily Summary</p>
              <p className="text-[#94A3B8] text-[12px] mt-1">Receive daily threat summary reports</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-[#1E293B] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#3B82F6]"></div>
            </label>
          </div>

          <div className="flex items-center justify-between py-3 border-b border-[#1E293B]">
            <div>
              <p className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>Weekly Reports</p>
              <p className="text-[#94A3B8] text-[12px] mt-1">Weekly intelligence reports via email</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" />
              <div className="w-11 h-6 bg-[#1E293B] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#3B82F6]"></div>
            </label>
          </div>

          <div className="flex items-center justify-between py-3">
            <div>
              <p className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>System Updates</p>
              <p className="text-[#94A3B8] text-[12px] mt-1">Notifications about system maintenance</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-[#1E293B] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#3B82F6]"></div>
            </label>
          </div>
        </div>
      </div>

      {/* System Information */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-5">
          <div className="flex items-center gap-3 mb-3">
            <Monitor className="w-5 h-5 text-[#3B82F6]" />
            <p className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>System Status</p>
          </div>
          <p className="text-[#10B981] text-[13px] mb-1" style={{ fontWeight: 600 }}>Operational</p>
          <p className="text-[#94A3B8] text-[11px]">All systems running normally</p>
        </div>

        <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-5">
          <div className="flex items-center gap-3 mb-3">
            <Database className="w-5 h-5 text-[#3B82F6]" />
            <p className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>Database</p>
          </div>
          <p className="text-[#10B981] text-[13px] mb-1" style={{ fontWeight: 600 }}>Connected</p>
          <p className="text-[#94A3B8] text-[11px]">Last sync: 2 minutes ago</p>
        </div>

        <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-5">
          <div className="flex items-center gap-3 mb-3">
            <Globe className="w-5 h-5 text-[#3B82F6]" />
            <p className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>API Status</p>
          </div>
          <p className="text-[#10B981] text-[13px] mb-1" style={{ fontWeight: 600 }}>Active</p>
          <p className="text-[#94A3B8] text-[11px]">Latency: 24ms</p>
        </div>
      </div>

      {/* Security */}
      <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-6">
        <div className="flex items-center gap-3 mb-6">
          <Shield className="w-5 h-5 text-[#3B82F6]" />
          <h3 className="text-[#F8FAFC]" style={{ fontWeight: 600, fontSize: '18px' }}>Security</h3>
        </div>

        <div className="space-y-3">
          <button className="w-full flex items-center justify-between p-4 bg-[#0F172A] border border-[#1E293B] rounded-lg hover:border-[#3B82F6] transition-colors">
            <span className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>Change Password</span>
            <span className="text-[#3B82F6] text-[13px]">→</span>
          </button>

          <button className="w-full flex items-center justify-between p-4 bg-[#0F172A] border border-[#1E293B] rounded-lg hover:border-[#3B82F6] transition-colors">
            <span className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>Two-Factor Authentication</span>
            <span className="px-2.5 py-1 bg-[#10B981]/10 border border-[#10B981]/20 text-[#10B981] rounded-md text-[11px]" style={{ fontWeight: 600 }}>
              Enabled
            </span>
          </button>

          <button className="w-full flex items-center justify-between p-4 bg-[#0F172A] border border-[#1E293B] rounded-lg hover:border-[#3B82F6] transition-colors">
            <span className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>Active Sessions</span>
            <span className="text-[#3B82F6] text-[13px]">→</span>
          </button>
        </div>
      </div>

      {/* About */}
      <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-6">
        <h3 className="text-[#F8FAFC] mb-4" style={{ fontWeight: 600, fontSize: '18px' }}>About DRISHTI</h3>
        <div className="space-y-2 text-[13px]">
          <div className="flex items-center justify-between py-2 border-b border-[#1E293B]">
            <span className="text-[#94A3B8]">Version</span>
            <span className="text-[#F8FAFC]" style={{ fontWeight: 600 }}>2.4.1</span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-[#1E293B]">
            <span className="text-[#94A3B8]">AI Model</span>
            <span className="text-[#F8FAFC]" style={{ fontWeight: 600 }}>DRISHTI-AI v2.4</span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-[#1E293B]">
            <span className="text-[#94A3B8]">Last Updated</span>
            <span className="text-[#F8FAFC]" style={{ fontWeight: 600 }}>May 5, 2026</span>
          </div>
          <div className="flex items-center justify-between py-2">
            <span className="text-[#94A3B8]">License</span>
            <span className="text-[#F8FAFC]" style={{ fontWeight: 600 }}>Enterprise</span>
          </div>
        </div>
      </div>
    </div>
  );
}
