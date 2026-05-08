import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Shield, Lock, User, Fingerprint, Eye, EyeOff } from 'lucide-react';

export function Login() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-[#070B14] relative overflow-hidden flex items-center justify-center">
      {/* Animated background */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-0 w-96 h-96 bg-[#3B82F6]/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-[#22D3EE]/5 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-[#3B82F6]/3 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>

      {/* Grid pattern overlay */}
      <div className="absolute inset-0 opacity-10" style={{
        backgroundImage: 'linear-gradient(#3B82F6 1px, transparent 1px), linear-gradient(90deg, #3B82F6 1px, transparent 1px)',
        backgroundSize: '50px 50px'
      }}></div>

      {/* Login card */}
      <div className="relative z-10 w-full max-w-md px-4">
        <div className="bg-[#0F172A]/80 backdrop-blur-xl border border-[#1E293B] rounded-2xl p-8 shadow-2xl">
          {/* Logo and branding */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-[#3B82F6] to-[#22D3EE] rounded-xl mb-4 shadow-lg shadow-[#3B82F6]/20">
              <Shield className="w-9 h-9 text-white" />
            </div>
            <h1 className="text-[#F8FAFC] mb-1" style={{ fontWeight: 800, fontSize: '28px', letterSpacing: '-0.02em' }}>DRISHTI</h1>
            <p className="text-[#22D3EE] text-[11px] tracking-[0.2em] uppercase mb-1" style={{ fontWeight: 600 }}>Vigilance Beyond Vision</p>
            <p className="text-[#94A3B8] text-[13px]">AI-Powered Insider Threat Detection</p>
          </div>

          {/* Secure access badge */}
          <div className="flex items-center justify-center gap-2 mb-6 px-4 py-2 bg-[#10B981]/10 border border-[#10B981]/20 rounded-lg">
            <Lock className="w-4 h-4 text-[#10B981]" />
            <span className="text-[#10B981] text-[12px]" style={{ fontWeight: 600 }}>SECURE ACCESS PORTAL</span>
          </div>

          {/* Login form */}
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-[#F8FAFC] text-[13px] mb-2" style={{ fontWeight: 500 }}>
                Username
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#94A3B8]" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter your username"
                  className="w-full bg-[#111827] border border-[#1E293B] rounded-lg pl-10 pr-4 py-2.5 text-[#F8FAFC] placeholder:text-[#94A3B8] focus:outline-none focus:border-[#3B82F6] focus:ring-1 focus:ring-[#3B82F6]/50 transition-all text-[14px]"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-[#F8FAFC] text-[13px] mb-2" style={{ fontWeight: 500 }}>
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#94A3B8]" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full bg-[#111827] border border-[#1E293B] rounded-lg pl-10 pr-10 py-2.5 text-[#F8FAFC] placeholder:text-[#94A3B8] focus:outline-none focus:border-[#3B82F6] focus:ring-1 focus:ring-[#3B82F6]/50 transition-all text-[14px]"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#94A3B8] hover:text-[#F8FAFC] transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-gradient-to-r from-[#3B82F6] to-[#22D3EE] text-white py-3 rounded-lg hover:shadow-lg hover:shadow-[#3B82F6]/30 transition-all duration-300 text-[14px]"
              style={{ fontWeight: 600 }}
            >
              Access System
            </button>

            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-[#1E293B]"></div>
              </div>
              <div className="relative flex justify-center">
                <span className="bg-[#0F172A] px-3 text-[#94A3B8] text-[12px]">OR</span>
              </div>
            </div>

            <button
              type="button"
              className="w-full bg-[#111827] border border-[#1E293B] text-[#F8FAFC] py-3 rounded-lg hover:bg-[#1E293B] transition-all duration-300 flex items-center justify-center gap-2 text-[14px]"
              style={{ fontWeight: 600 }}
            >
              <Fingerprint className="w-5 h-5 text-[#22D3EE]" />
              Biometric Login
            </button>
          </form>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-[#1E293B]">
            <div className="flex items-center justify-between text-[11px] text-[#94A3B8]">
              <span>Version 2.4.1</span>
              <span>Encrypted Connection</span>
            </div>
          </div>
        </div>

        {/* Monitoring tagline */}
        <div className="text-center mt-6">
          <p className="text-[#94A3B8] text-[12px]">
            Continuous behavioral monitoring • Real-time drift detection
          </p>
        </div>
      </div>
    </div>
  );
}
