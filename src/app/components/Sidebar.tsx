import { NavLink } from 'react-router';
import {
  LayoutDashboard,
  AlertTriangle,
  Brain,
  Users,
  MapPin,
  FileText,
  Settings as SettingsIcon,
  Sliders,
  LogOut,
  Shield
} from 'lucide-react';

export function Sidebar() {
  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/alerts', icon: AlertTriangle, label: 'Alerts' },
    { path: '/threat-analysis', icon: Brain, label: 'Threat Analysis' },
    { path: '/user-intelligence', icon: Users, label: 'User Intelligence' },
    { path: '/heatmap', icon: MapPin, label: 'Heatmap' },
    { path: '/reports', icon: FileText, label: 'Reports' },
    { path: '/configuration', icon: Sliders, label: 'Configuration' },
    { path: '/settings', icon: SettingsIcon, label: 'Settings' },
  ];

  return (
    <aside className="w-64 bg-[#0F172A] border-r border-[#1E293B] flex flex-col h-screen fixed left-0 top-0">
      <div className="p-6 border-b border-[#1E293B]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-[#3B82F6] to-[#22D3EE] rounded-lg flex items-center justify-center">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-[#F8FAFC] tracking-tight" style={{ fontWeight: 700 }}>DRISHTI</h1>
            <p className="text-[10px] text-[#22D3EE] tracking-widest uppercase">Vigilance Beyond Vision</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 ${
                isActive
                  ? 'bg-[#3B82F6]/10 text-[#3B82F6] border border-[#3B82F6]/20'
                  : 'text-[#94A3B8] hover:bg-[#1E293B] hover:text-[#F8FAFC]'
              }`
            }
          >
            <item.icon className="w-5 h-5" />
            <span className="text-[14px]" style={{ fontWeight: 500 }}>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-[#1E293B]">
        <button className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-[#EF4444] hover:bg-[#EF4444]/10 transition-all duration-200 w-full">
          <LogOut className="w-5 h-5" />
          <span className="text-[14px]" style={{ fontWeight: 500 }}>Logout</span>
        </button>
      </div>
    </aside>
  );
}
