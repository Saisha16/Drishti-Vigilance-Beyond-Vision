import { useState, useEffect } from 'react';
import { Link2, ShieldCheck, ShieldAlert, RefreshCw, Hash, Clock } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ChainData {
  blocks: Array<{
    index: number;
    timestamp: string;
    action: string;
    user_id: string;
    details: Record<string, any>;
    previous_hash: string;
    block_hash: string;
  }>;
  summary: {
    total_blocks: number;
    is_valid: boolean;
    integrity_issues: number;
    latest_block_hash: string;
    genesis_hash: string;
    action_counts: Record<string, number>;
    last_event_time: string;
  };
}

export function BlockchainAudit() {
  const [chain, setChain] = useState<ChainData | null>(null);
  const [verification, setVerification] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);

  useEffect(() => { loadChain(); }, []);

  async function loadChain() {
    try {
      const res = await fetch(`${API_BASE}/api/audit/chain?count=100`);
      if (res.ok) setChain(await res.json());
    } catch { /* Backend not running */ }
    finally { setLoading(false); }
  }

  async function verifyChain() {
    setVerifying(true);
    try {
      const res = await fetch(`${API_BASE}/api/audit/verify`);
      if (res.ok) setVerification(await res.json());
    } catch { /* error */ }
    finally { setVerifying(false); }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="w-10 h-10 border-4 border-[#3B82F6] border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const summary = chain?.summary;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-[#F8FAFC] text-2xl font-bold tracking-tight">Blockchain Audit Trail</h1>
          <p className="text-[#94A3B8] text-sm mt-1">SHA-256 hash chain — tamper-proof, immutable audit log</p>
        </div>
        <button
          onClick={verifyChain}
          disabled={verifying}
          className="flex items-center gap-2 bg-[#10B981] text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-[#059669] transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${verifying ? 'animate-spin' : ''}`} />
          {verifying ? 'Verifying...' : 'Verify Chain Integrity'}
        </button>
      </div>

      {/* Verification Result */}
      {verification && (
        <div className={`border rounded-xl p-5 ${
          verification.is_valid
            ? 'bg-[#10B981]/5 border-[#10B981]/20'
            : 'bg-[#EF4444]/5 border-[#EF4444]/20'
        }`}>
          <div className="flex items-center gap-3">
            {verification.is_valid ? (
              <ShieldCheck className="w-8 h-8 text-[#10B981]" />
            ) : (
              <ShieldAlert className="w-8 h-8 text-[#EF4444]" />
            )}
            <div>
              <p className={`text-lg font-bold ${verification.is_valid ? 'text-[#10B981]' : 'text-[#EF4444]'}`}>
                {verification.is_valid ? 'CHAIN INTEGRITY VERIFIED [OK]' : 'INTEGRITY VIOLATION DETECTED [X]'}
              </p>
              <p className="text-sm text-[#94A3B8]">
                {verification.total_blocks} blocks verified • {verification.integrity_issues} issues found •
                Verified at {new Date(verification.verified_at).toLocaleString('en-IN')}
              </p>
            </div>
          </div>
          {verification.issues?.length > 0 && (
            <div className="mt-4 space-y-2">
              {verification.issues.map((issue: any, i: number) => (
                <div key={i} className="bg-[#EF4444]/10 border border-[#EF4444]/20 rounded-lg p-3 text-sm text-[#EF4444]">
                  Block #{issue.block}: {issue.issue}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-4 gap-4">
          <SummaryCard label="Total Blocks" value={summary.total_blocks.toString()} icon={Link2} />
          <SummaryCard label="Chain Status" value={summary.is_valid ? 'Valid' : 'Compromised'} icon={summary.is_valid ? ShieldCheck : ShieldAlert} color={summary.is_valid ? '#10B981' : '#EF4444'} />
          <SummaryCard label="Integrity Issues" value={summary.integrity_issues.toString()} icon={ShieldAlert} color={summary.integrity_issues > 0 ? '#EF4444' : '#10B981'} />
          <SummaryCard label="Last Event" value={summary.last_event_time ? new Date(summary.last_event_time).toLocaleDateString('en-IN') : 'N/A'} icon={Clock} />
        </div>
      )}

      {/* How It Works */}
      <div className="bg-[#111827]/60 border border-[#1E293B] rounded-xl p-5">
        <h3 className="text-[#F8FAFC] font-semibold text-sm mb-3">How Blockchain Audit Works</h3>
        <div className="grid grid-cols-4 gap-4">
          {[
            { step: '1', title: 'Event Logged', desc: 'Every audit action is recorded with timestamp, user, and details' },
            { step: '2', title: 'Hash Computed', desc: 'SHA-256 hash = hash(data + previous_hash + timestamp)' },
            { step: '3', title: 'Chain Linked', desc: 'Each block contains hash of previous block, creating immutable chain' },
            { step: '4', title: 'Verify Anytime', desc: 'Re-compute all hashes — any mismatch = TAMPERING DETECTED' },
          ].map(s => (
            <div key={s.step} className="text-center">
              <div className="w-8 h-8 rounded-full bg-[#3B82F6]/10 text-[#3B82F6] flex items-center justify-center text-sm font-bold mx-auto mb-2">{s.step}</div>
              <p className="text-xs text-[#F8FAFC] font-medium">{s.title}</p>
              <p className="text-[10px] text-[#64748B] mt-1">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Block Explorer */}
      <div className="bg-[#111827]/60 border border-[#1E293B] rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-[#1E293B]">
          <h3 className="text-[#F8FAFC] font-semibold text-sm">Block Explorer</h3>
        </div>
        {chain?.blocks && chain.blocks.length > 0 ? (
          <div className="divide-y divide-[#1E293B]/50 max-h-[500px] overflow-y-auto">
            {chain.blocks.map((block) => (
              <div key={block.index} className="px-5 py-3 hover:bg-[#1E293B]/20 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded bg-[#1E293B] flex items-center justify-center text-xs text-[#3B82F6] font-bold">
                      #{block.index}
                    </div>
                    <div>
                      <p className="text-sm text-[#F8FAFC] font-medium">{block.action}</p>
                      <p className="text-[10px] text-[#64748B]">
                        by {block.user_id} • {new Date(block.timestamp).toLocaleString('en-IN')}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-[10px] text-[#475569] font-mono truncate max-w-[200px]" title={block.block_hash}>
                      <Hash className="w-3 h-3 inline mr-1" />
                      {block.block_hash.substring(0, 16)}...
                    </p>
                    <p className="text-[9px] text-[#334155] font-mono truncate max-w-[200px]" title={block.previous_hash}>
                      prev: {block.previous_hash.substring(0, 12)}...
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="px-5 py-12 text-center text-[#64748B] text-sm">
            No blocks in the chain yet. The genesis block will be created when the backend starts.
          </div>
        )}
      </div>
    </div>
  );
}

function SummaryCard({ label, value, icon: Icon, color = '#3B82F6' }: {
  label: string; value: string; icon: any; color?: string;
}) {
  return (
    <div className="bg-[#111827]/60 border border-[#1E293B] rounded-xl p-4">
      <Icon className="w-5 h-5 mb-2" style={{ color }} />
      <p className="text-xl font-bold text-[#F8FAFC]">{value}</p>
      <p className="text-xs text-[#64748B]">{label}</p>
    </div>
  );
}
