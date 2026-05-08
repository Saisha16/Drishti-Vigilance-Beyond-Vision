import { useState } from 'react';
import { Save, RotateCcw, Shield, Lock } from 'lucide-react';

export function Configuration() {
  const [driftThreshold, setDriftThreshold] = useState(35);
  const [alertSensitivity, setAlertSensitivity] = useState(70);
  const [resourceSensitivity, setResourceSensitivity] = useState(60);
  const [retentionPeriod, setRetentionPeriod] = useState(90);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-[#F8FAFC] mb-1" style={{ fontWeight: 700, fontSize: '28px', letterSpacing: '-0.02em' }}>
            System Configuration
          </h1>
          <p className="text-[#94A3B8] text-[14px]">Configure detection parameters and system behavior</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-[#1E293B] border border-[#1E293B] text-[#F8FAFC] rounded-lg text-[13px] hover:bg-[#1E293B]/70 transition-colors" style={{ fontWeight: 600 }}>
            <RotateCcw className="w-4 h-4" />
            Reset to Defaults
          </button>
          <button className="flex items-center gap-2 bg-[#3B82F6] text-white px-4 py-2 rounded-lg text-[13px] hover:bg-[#3B82F6]/90 transition-colors" style={{ fontWeight: 600 }}>
            <Save className="w-4 h-4" />
            Save Configuration
          </button>
        </div>
      </div>

      {/* Detection Parameters */}
      <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-6">
        <h3 className="text-[#F8FAFC] mb-6" style={{ fontWeight: 600, fontSize: '18px' }}>Detection Parameters</h3>

        <div className="space-y-8">
          {/* Drift Threshold */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <div>
                <label className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>
                  Behavioral Drift Threshold
                </label>
                <p className="text-[#94A3B8] text-[12px] mt-1">
                  Minimum drift percentage to trigger an alert
                </p>
              </div>
              <span className="text-[#3B82F6] text-[18px]" style={{ fontWeight: 700 }}>{driftThreshold}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={driftThreshold}
              onChange={(e) => setDriftThreshold(Number(e.target.value))}
              className="w-full h-2 bg-[#1E293B] rounded-lg appearance-none cursor-pointer accent-[#3B82F6]"
            />
            <div className="flex justify-between mt-2">
              <span className="text-[#94A3B8] text-[11px]">0% (Very Sensitive)</span>
              <span className="text-[#94A3B8] text-[11px]">100% (Less Sensitive)</span>
            </div>
          </div>

          {/* Alert Sensitivity */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <div>
                <label className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>
                  Alert Sensitivity
                </label>
                <p className="text-[#94A3B8] text-[12px] mt-1">
                  Controls how quickly the system generates alerts
                </p>
              </div>
              <span className="text-[#3B82F6] text-[18px]" style={{ fontWeight: 700 }}>{alertSensitivity}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={alertSensitivity}
              onChange={(e) => setAlertSensitivity(Number(e.target.value))}
              className="w-full h-2 bg-[#1E293B] rounded-lg appearance-none cursor-pointer accent-[#3B82F6]"
            />
            <div className="flex justify-between mt-2">
              <span className="text-[#94A3B8] text-[11px]">0% (Fewer Alerts)</span>
              <span className="text-[#94A3B8] text-[11px]">100% (More Alerts)</span>
            </div>
          </div>

          {/* Resource Sensitivity */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <div>
                <label className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>
                  Resource Access Sensitivity
                </label>
                <p className="text-[#94A3B8] text-[12px] mt-1">
                  Weight given to unusual resource access patterns
                </p>
              </div>
              <span className="text-[#3B82F6] text-[18px]" style={{ fontWeight: 700 }}>{resourceSensitivity}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={resourceSensitivity}
              onChange={(e) => setResourceSensitivity(Number(e.target.value))}
              className="w-full h-2 bg-[#1E293B] rounded-lg appearance-none cursor-pointer accent-[#3B82F6]"
            />
            <div className="flex justify-between mt-2">
              <span className="text-[#94A3B8] text-[11px]">0% (Low Priority)</span>
              <span className="text-[#94A3B8] text-[11px]">100% (High Priority)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Data Retention */}
      <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-6">
        <h3 className="text-[#F8FAFC] mb-6" style={{ fontWeight: 600, fontSize: '18px' }}>Data Retention</h3>

        <div>
          <div className="flex items-center justify-between mb-3">
            <div>
              <label className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>
                Retention Period
              </label>
              <p className="text-[#94A3B8] text-[12px] mt-1">
                How long to store behavioral data and alerts
              </p>
            </div>
            <span className="text-[#3B82F6] text-[18px]" style={{ fontWeight: 700 }}>{retentionPeriod} days</span>
          </div>
          <input
            type="range"
            min="30"
            max="365"
            value={retentionPeriod}
            onChange={(e) => setRetentionPeriod(Number(e.target.value))}
            className="w-full h-2 bg-[#1E293B] rounded-lg appearance-none cursor-pointer accent-[#3B82F6]"
          />
          <div className="flex justify-between mt-2">
            <span className="text-[#94A3B8] text-[11px]">30 days</span>
            <span className="text-[#94A3B8] text-[11px]">365 days</span>
          </div>
        </div>
      </div>

      {/* Advanced Settings */}
      <div className="bg-[#111827]/50 backdrop-blur-sm border border-[#1E293B] rounded-xl p-6">
        <h3 className="text-[#F8FAFC] mb-6" style={{ fontWeight: 600, fontSize: '18px' }}>Advanced Settings</h3>

        <div className="space-y-4">
          <div className="flex items-center justify-between py-3 border-b border-[#1E293B]">
            <div>
              <p className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>Real-time Monitoring</p>
              <p className="text-[#94A3B8] text-[12px] mt-1">Enable continuous behavioral analysis</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-[#1E293B] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#3B82F6]"></div>
            </label>
          </div>

          <div className="flex items-center justify-between py-3 border-b border-[#1E293B]">
            <div>
              <p className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>Geolocation Tracking</p>
              <p className="text-[#94A3B8] text-[12px] mt-1">Track user login locations</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-[#1E293B] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#3B82F6]"></div>
            </label>
          </div>

          <div className="flex items-center justify-between py-3 border-b border-[#1E293B]">
            <div>
              <p className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>Device Fingerprinting</p>
              <p className="text-[#94A3B8] text-[12px] mt-1">Identify unique device signatures</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-[#1E293B] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#3B82F6]"></div>
            </label>
          </div>

          <div className="flex items-center justify-between py-3 border-b border-[#1E293B]">
            <div>
              <p className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>Email Notifications</p>
              <p className="text-[#94A3B8] text-[12px] mt-1">Send alerts via email</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" />
              <div className="w-11 h-6 bg-[#1E293B] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#3B82F6]"></div>
            </label>
          </div>

          <div className="flex items-center justify-between py-3">
            <div>
              <p className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>Automatic Response</p>
              <p className="text-[#94A3B8] text-[12px] mt-1">Automatically suspend high-risk users</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" />
              <div className="w-11 h-6 bg-[#1E293B] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#3B82F6]"></div>
            </label>
          </div>
        </div>
      </div>

      {/* Security Status */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gradient-to-br from-[#10B981]/10 to-[#10B981]/5 border border-[#10B981]/20 rounded-xl p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-[#10B981]/20 rounded-lg flex items-center justify-center">
              <Lock className="w-5 h-5 text-[#10B981]" />
            </div>
            <div>
              <p className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>Encryption Status</p>
              <p className="text-[#10B981] text-[12px]">AES-256 Enabled</p>
            </div>
          </div>
          <p className="text-[#94A3B8] text-[12px]">All data is encrypted at rest and in transit</p>
        </div>

        <div className="bg-gradient-to-br from-[#3B82F6]/10 to-[#3B82F6]/5 border border-[#3B82F6]/20 rounded-xl p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-[#3B82F6]/20 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-[#3B82F6]" />
            </div>
            <div>
              <p className="text-[#F8FAFC] text-[14px]" style={{ fontWeight: 600 }}>AI Model Version</p>
              <p className="text-[#3B82F6] text-[12px]">DRISHTI-AI v2.4.1</p>
            </div>
          </div>
          <p className="text-[#94A3B8] text-[12px]">Last updated: May 5, 2026</p>
        </div>
      </div>
    </div>
  );
}
