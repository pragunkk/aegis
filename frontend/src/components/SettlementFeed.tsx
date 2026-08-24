import React, { useState } from 'react';
import { CreditCard, CheckCircle2, Clock, ShieldCheck, Copy, Check, Info } from 'lucide-react';
import type { AuditLog } from '../types';

interface SettlementFeedProps {
  logs: AuditLog[];
}

export const SettlementFeed: React.FC<SettlementFeedProps> = ({ logs }) => {
  const [filter, setFilter] = useState<'ALL' | 'PAID' | 'PENDING'>('ALL');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const settlementLogs = logs.filter((l) =>
    [
      'ORDER_CREATED',
      'PAYMENT_CONFIRMED',
      'PAYMENT_FAILED',
      'SIGNATURE_VERIFICATION_FAILED',
    ].includes(l.event_type)
  );

  const filteredLogs = settlementLogs.filter((l) => {
    if (filter === 'PAID') return l.event_type === 'PAYMENT_CONFIRMED';
    if (filter === 'PENDING') return l.event_type === 'ORDER_CREATED';
    return true;
  });

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(text);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="flex flex-col h-[580px] rounded-xl border border-zinc-800/90 bg-[#121216] overflow-hidden">
      {/* Feed Header */}
      <div className="px-5 py-3.5 border-b border-zinc-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-[#16161b]">
        <div className="flex items-center gap-2">
          <CreditCard className="h-4 w-4 text-emerald-400" />
          <h3 className="text-sm font-semibold text-zinc-100">
            Razorpay Orders & Settlement Stream
          </h3>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center gap-1 bg-zinc-900/90 p-0.5 rounded-lg border border-zinc-800 text-xs">
          <button
            onClick={() => setFilter('ALL')}
            className={`px-2.5 py-1 rounded-md transition cursor-pointer ${
              filter === 'ALL' ? 'bg-zinc-800 text-white font-medium shadow-sm' : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('PAID')}
            className={`px-2.5 py-1 rounded-md transition cursor-pointer ${
              filter === 'PAID' ? 'bg-emerald-500/20 text-emerald-300 font-medium' : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Paid
          </button>
          <button
            onClick={() => setFilter('PENDING')}
            className={`px-2.5 py-1 rounded-md transition cursor-pointer ${
              filter === 'PENDING' ? 'bg-zinc-800 text-white font-medium' : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Pending
          </button>
        </div>
      </div>

      {/* Transactions List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {filteredLogs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-zinc-500 text-xs space-y-2 py-8">
            <Info className="h-6 w-6 text-zinc-600" />
            <p>No transactions recorded yet.</p>
          </div>
        ) : (
          filteredLogs.map((log) => {
            const time = log.created_at
              ? new Date(log.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
              : 'Just now';

            if (log.event_type === 'PAYMENT_CONFIRMED') {
              const orderId = log.payload?.razorpay_order_id || 'N/A';
              return (
                <div
                  key={log.id}
                  className="p-3.5 rounded-lg bg-emerald-950/20 border border-emerald-500/30 space-y-2 transition"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="badge-pill bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                        <CheckCircle2 className="h-3 w-3" />
                        <span>Paid & Settled</span>
                      </span>
                      <span className="text-xs font-semibold text-zinc-200">
                        Webhook Received
                      </span>
                    </div>
                    <span className="text-[11px] text-zinc-500 font-mono">{time}</span>
                  </div>

                  <div className="text-xs text-zinc-300 space-y-1.5 pt-0.5">
                    <div className="flex items-center justify-between">
                      <span className="text-zinc-400">Order ID:</span>
                      <button
                        onClick={() => handleCopy(orderId)}
                        className="flex items-center gap-1 font-mono text-[11px] bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800 hover:border-zinc-700 text-zinc-300 transition cursor-pointer"
                        title="Click to copy ID"
                      >
                        <span>{orderId}</span>
                        {copiedId === orderId ? (
                          <Check className="h-3 w-3 text-emerald-400" />
                        ) : (
                          <Copy className="h-3 w-3 text-zinc-500" />
                        )}
                      </button>
                    </div>

                    <div className="flex items-center gap-1.5 text-[11px] text-emerald-400/90 pt-1 border-t border-emerald-900/40">
                      <ShieldCheck className="h-3.5 w-3.5 shrink-0" />
                      <span>HMAC-SHA256 signature verified</span>
                    </div>
                  </div>
                </div>
              );
            }

            if (log.event_type === 'ORDER_CREATED') {
              const orderId = log.payload?.razorpay_order_id || 'N/A';
              return (
                <div
                  key={log.id}
                  className="p-3.5 rounded-lg bg-zinc-900/60 border border-zinc-800/80 hover:border-zinc-700/80 transition space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="badge-pill bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                        <Clock className="h-3 w-3" />
                        <span>Order Created</span>
                      </span>
                      <span className="text-xs font-medium text-zinc-300 truncate max-w-[180px]">
                        {log.payload?.product_name}
                      </span>
                    </div>
                    <span className="text-sm font-semibold text-emerald-400">
                      ₹{log.payload?.negotiated_price?.toLocaleString('en-IN')}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-xs text-zinc-400 pt-1 border-t border-zinc-800/60">
                    <button
                      onClick={() => handleCopy(orderId)}
                      className="flex items-center gap-1 font-mono text-[11px] text-zinc-400 hover:text-zinc-200 transition cursor-pointer"
                    >
                      <span>{orderId}</span>
                      {copiedId === orderId ? (
                        <Check className="h-3 w-3 text-emerald-400" />
                      ) : (
                        <Copy className="h-3 w-3 text-zinc-600" />
                      )}
                    </button>
                    <div className="flex items-center gap-3 text-[11px]">
                      <span>MRP: ₹{log.payload?.mrp}</span>
                      {log.payload?.discount_given > 0 && (
                        <span className="text-indigo-400">
                          -₹{log.payload?.discount_given}
                        </span>
                      )}
                      <span className="font-mono text-zinc-500">{time}</span>
                    </div>
                  </div>
                </div>
              );
            }

            return null;
          })
        )}
      </div>
    </div>
  );
};
