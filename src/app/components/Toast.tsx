import { useState, useCallback, createContext, useContext } from 'react';

// ─── Toast Types ──────────────────────────────────────────────────────────────

interface Toast {
  id: number;
  message: string;
  type: 'success' | 'info' | 'warning' | 'error';
}

interface ToastContext {
  toasts: Toast[];
  toast: (message: string, type?: Toast['type']) => void;
}

const ToastCtx = createContext<ToastContext>({ toasts: [], toast: () => {} });

// ─── Provider ─────────────────────────────────────────────────────────────────

let _nextId = 1;

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((message: string, type: Toast['type'] = 'info') => {
    const id = _nextId++;
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 3500);
  }, []);

  const COLORS: Record<string, { bg: string; border: string; text: string }> = {
    success: { bg: 'rgba(16,185,129,0.12)', border: 'rgba(16,185,129,0.3)', text: '#10B981' },
    info:    { bg: 'rgba(59,130,246,0.12)', border: 'rgba(59,130,246,0.3)', text: '#3B82F6' },
    warning: { bg: 'rgba(245,158,11,0.12)', border: 'rgba(245,158,11,0.3)', text: '#F59E0B' },
    error:   { bg: 'rgba(239,68,68,0.12)', border: 'rgba(239,68,68,0.3)', text: '#EF4444' },
  };

  const ICONS: Record<string, string> = {
    success: '[OK]',
    info: '[i]',
    warning: '[!]',
    error: '[X]',
  };

  return (
    <ToastCtx.Provider value={{ toasts, toast: addToast }}>
      {children}
      {/* Toast Container */}
      <div style={{
        position: 'fixed', top: 20, right: 20, zIndex: 9999,
        display: 'flex', flexDirection: 'column', gap: 8,
        pointerEvents: 'none',
      }}>
        {toasts.map(t => {
          const c = COLORS[t.type];
          return (
            <div key={t.id} style={{
              background: c.bg,
              backdropFilter: 'blur(12px)',
              border: `1px solid ${c.border}`,
              borderRadius: 10,
              padding: '10px 16px',
              color: c.text,
              fontSize: 13,
              fontWeight: 600,
              fontFamily: "'Inter', sans-serif",
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              animation: 'toastIn 0.3s ease',
              boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
              minWidth: 250,
              pointerEvents: 'auto',
            }}>
              <span style={{ fontSize: 16 }}>{ICONS[t.type]}</span>
              {t.message}
            </div>
          );
        })}
      </div>
      <style>{`
        @keyframes toastIn {
          from { opacity: 0; transform: translateX(20px); }
          to { opacity: 1; transform: translateX(0); }
        }
      `}</style>
    </ToastCtx.Provider>
  );
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useToast() {
  return useContext(ToastCtx);
}
