import { LucideIcon } from 'lucide-react';
import { ReactNode } from 'react';

interface MetricCardProps {
  icon: LucideIcon;
  title: string;
  value: string | number;
  trend?: number;
  trendLabel?: string;
  sparkline?: number[];
  color?: 'blue' | 'red' | 'green' | 'amber';
}

export function MetricCard({ icon: Icon, title, value, trend, trendLabel, sparkline, color = 'blue' }: MetricCardProps) {
  const colorClasses = {
    blue: 'from-[#3B82F6]/10 to-[#22D3EE]/5 border-[#3B82F6]/20 text-[#3B82F6]',
    red: 'from-[#EF4444]/10 to-[#EF4444]/5 border-[#EF4444]/20 text-[#EF4444]',
    green: 'from-[#10B981]/10 to-[#10B981]/5 border-[#10B981]/20 text-[#10B981]',
    amber: 'from-[#F59E0B]/10 to-[#F59E0B]/5 border-[#F59E0B]/20 text-[#F59E0B]',
  };

  const glowClasses = {
    blue: 'group-hover:shadow-[#3B82F6]/20',
    red: 'group-hover:shadow-[#EF4444]/20',
    green: 'group-hover:shadow-[#10B981]/20',
    amber: 'group-hover:shadow-[#F59E0B]/20',
  };

  return (
    <div className={`group relative bg-gradient-to-br ${colorClasses[color]} border backdrop-blur-sm rounded-xl p-5 transition-all duration-300 hover:shadow-lg ${glowClasses[color]} cursor-default`}>
      <div className="flex items-start justify-between mb-3">
        <div className={`w-11 h-11 bg-gradient-to-br ${colorClasses[color]} rounded-lg flex items-center justify-center`}>
          <Icon className="w-5 h-5" />
        </div>
        {trend !== undefined && (
          <div className={`flex items-center gap-1 px-2 py-1 rounded-md text-[11px] ${
            trend > 0 ? 'bg-[#10B981]/10 text-[#10B981]' : 'bg-[#EF4444]/10 text-[#EF4444]'
          }`} style={{ fontWeight: 600 }}>
            <span>{trend > 0 ? '↑' : '↓'}</span>
            <span>{Math.abs(trend)}%</span>
          </div>
        )}
      </div>

      <h3 className="text-[#94A3B8] text-[13px] mb-1">{title}</h3>
      <p className="text-[#F8FAFC] mb-2" style={{ fontWeight: 700, fontSize: '26px', letterSpacing: '-0.02em' }}>{value}</p>

      {trendLabel && (
        <p className="text-[#94A3B8] text-[11px]">{trendLabel}</p>
      )}

      {sparkline && (
        <div className="flex items-end gap-1 mt-3 h-8">
          {sparkline.map((height, i) => (
            <div
              key={i}
              className={`flex-1 bg-gradient-to-t ${colorClasses[color]} rounded-sm transition-all duration-300`}
              style={{ height: `${height}%` }}
            ></div>
          ))}
        </div>
      )}
    </div>
  );
}
