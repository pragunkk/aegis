import React, { useState } from 'react';
import { Search, CheckCircle2, ShieldAlert, Zap, X, Loader2, Check, AlertCircle } from 'lucide-react';
import { discoverProducts, negotiatePrice, sendMockWebhook, fetchTestToken } from '../lib/api';

interface SimulatorWidgetProps {
  isOpen: boolean;
  onClose: () => void;
  onActionComplete: () => void;
}

const TARGET_PRODUCT_ID = 'a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d'; // Neural Interface (MRP 4500, Floor 3800)

export const SimulatorWidget: React.FC<SimulatorWidgetProps> = ({
  isOpen,
  onClose,
  onActionComplete,
}) => {
  const [running, setRunning] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<{
    status: 'success' | 'blocked' | 'info' | 'error';
    title: string;
    description: string;
    details?: Record<string, any>;
  } | null>(null);
  const [lastOrderId, setLastOrderId] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleDiscovery = async () => {
    setRunning('discovery');
    try {
      const results = await discoverProducts('neural transceiver cyber deck', 3);
      setLastResult({
        status: 'success',
        title: 'Semantic Discovery Successful',
        description: `Agent queried catalog and matched ${results.length} product(s) via pgvector. Price floors remained confidential.`,
        details: {
          matched_products: results.map((r) => `${r.name} (MRP: ₹${r.mrp})`),
        },
      });
      onActionComplete();
    } catch (err: any) {
      setLastResult({
        status: 'error',
        title: 'Discovery Failed',
        description: err.message || 'Discovery request failed',
      });
    } finally {
      setRunning(null);
    }
  };

  const handleValidNegotiation = async () => {
    setRunning('negotiate_valid');
    try {
      const token = await fetchTestToken('agent_simulator_007', 10000.0);
      const res = await negotiatePrice(
        token,
        TARGET_PRODUCT_ID,
        3800.0,
        'Agentic procurement request matching merchant margin'
      );
      if (res.ok && res.data?.success) {
        const orderId = res.data.decision?.razorpay_order_id || null;
        setLastOrderId(orderId);
        setLastResult({
          status: 'success',
          title: 'Offer Accepted — Razorpay Order Created',
          description: `The gateway accepted the negotiated price of ₹3,800.00 (at price floor). A Razorpay order was generated.`,
          details: {
            razorpay_order_id: orderId,
            negotiated_price: '₹3,800.00',
            mrp: '₹4,500.00',
            discount: '₹700.00 (15.5%)',
          },
        });
      } else {
        const errorMsg =
          res.data?.decision?.message ||
          res.data?.detail ||
          res.data?.message ||
          'Negotiation request rejected by gateway';
        setLastResult({
          status: 'error',
          title: 'Negotiation Rejected',
          description: errorMsg,
        });
      }
      onActionComplete();
    } catch (err: any) {
      setLastResult({
        status: 'error',
        title: 'Request Failed',
        description: err.message || 'Failed to submit negotiation',
      });
    } finally {
      setRunning(null);
    }
  };

  const handleSubFloorAttack = async () => {
    setRunning('attack');
    try {
      const token = await fetchTestToken('agent_simulator_007', 10000.0);
      const res = await negotiatePrice(
        token,
        TARGET_PRODUCT_ID,
        2500.0,
        'Exploit attempt: Proposing price below merchant margin'
      );
      const reason =
        res.data?.decision?.message ||
        res.data?.detail ||
        'The agent attempted to offer ₹2,500.00 on a product with a confidential floor of ₹3,800.00. The gateway rejected the request with HTTP 422.';

      setLastResult({
        status: 'blocked',
        title: 'Exploit Blocked by Aegis Firewall',
        description: reason,
        details: {
          offered_price: '₹2,500.00',
          protected_floor: '₹3,800.00',
          exploit_delta_halted: '₹1,300.00 below margin',
          status: '422 Unprocessable Entity',
        },
      });
      onActionComplete();
    } catch (err: any) {
      setLastResult({
        status: 'blocked',
        title: 'Exploit Intercepted',
        description: err.message || 'Sub-floor price attack blocked',
      });
    } finally {
      setRunning(null);
    }
  };

  const handleSettleOrder = async () => {
    if (!lastOrderId) {
      setLastResult({
        status: 'info',
        title: 'No Pending Order',
        description: 'Please click "2. Fair Offer" first to generate an active Razorpay Order ID.',
      });
      return;
    }
    setRunning('settle');
    try {
      const res = await sendMockWebhook(lastOrderId, 3800.0);
      if (res.ok) {
        setLastResult({
          status: 'success',
          title: 'Webhook Settlement Verified',
          description: `Order ${lastOrderId} was settled to PAID after HMAC-SHA256 signature verification.`,
          details: {
            event: 'order.paid',
            order_id: lastOrderId,
            settled_status: 'PAID',
            signature: 'HMAC-SHA256 Verified',
          },
        });
      } else {
        setLastResult({
          status: 'error',
          title: 'Settlement Verification Failed',
          description: res.data?.detail || res.data?.error || 'Webhook verification rejected',
        });
      }
      onActionComplete();
    } catch (err: any) {
      setLastResult({
        status: 'error',
        title: 'Settlement Failed',
        description: err.message || 'Webhook simulation failed',
      });
    } finally {
      setRunning(null);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-xl rounded-2xl bg-[#121216] border border-zinc-800/90 p-6 shadow-2xl space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-zinc-800/80 pb-4">
          <div>
            <h3 className="text-base font-heading font-bold text-zinc-100">
              Agent Test Console
            </h3>
            <p className="text-xs text-zinc-400 mt-0.5">
              Simulate AI buyer agent requests and test gateway defense rules.
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-zinc-400 hover:text-white p-1 rounded-lg hover:bg-zinc-800 transition cursor-pointer"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* 4 Action Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {/* Action 1: Search */}
          <button
            onClick={handleDiscovery}
            disabled={running !== null}
            className="p-3.5 rounded-xl border border-zinc-800 bg-[#16161b] hover:bg-zinc-800/80 text-left transition cursor-pointer disabled:opacity-50 space-y-1 hover:border-cyan-500/30"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-semibold text-cyan-400">
                <Search className="h-4 w-4" />
                <span>1. Search Catalog</span>
              </div>
              {running === 'discovery' && <Loader2 className="h-3.5 w-3.5 animate-spin text-cyan-400" />}
            </div>
            <p className="text-[11px] text-zinc-400">
              Natural language semantic search via pgvector.
            </p>
          </button>

          {/* Action 2: Fair Offer */}
          <button
            onClick={handleValidNegotiation}
            disabled={running !== null}
            className="p-3.5 rounded-xl border border-zinc-800 bg-[#16161b] hover:bg-zinc-800/80 text-left transition cursor-pointer disabled:opacity-50 space-y-1 hover:border-emerald-500/30"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400">
                <CheckCircle2 className="h-4 w-4" />
                <span>2. Fair Offer (₹3,800)</span>
              </div>
              {running === 'negotiate_valid' && <Loader2 className="h-3.5 w-3.5 animate-spin text-emerald-400" />}
            </div>
            <p className="text-[11px] text-zinc-400">
              Haggle down to floor & create Razorpay Order.
            </p>
          </button>

          {/* Action 3: Lowball Attack */}
          <button
            onClick={handleSubFloorAttack}
            disabled={running !== null}
            className="p-3.5 rounded-xl border border-zinc-800 bg-[#16161b] hover:bg-zinc-800/80 text-left transition cursor-pointer disabled:opacity-50 space-y-1 hover:border-rose-500/30"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-semibold text-rose-400">
                <ShieldAlert className="h-4 w-4" />
                <span>3. Lowball Attack (₹2,500)</span>
              </div>
              {running === 'attack' && <Loader2 className="h-3.5 w-3.5 animate-spin text-rose-400" />}
            </div>
            <p className="text-[11px] text-zinc-400">
              Test sub-floor firewall defense (halts with 422).
            </p>
          </button>

          {/* Action 4: Settle Webhook */}
          <button
            onClick={handleSettleOrder}
            disabled={running !== null}
            className="p-3.5 rounded-xl border border-zinc-800 bg-[#16161b] hover:bg-zinc-800/80 text-left transition cursor-pointer disabled:opacity-50 space-y-1 hover:border-indigo-500/30"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-semibold text-indigo-400">
                <Zap className="h-4 w-4" />
                <span>4. Settle Order</span>
              </div>
              {running === 'settle' && <Loader2 className="h-3.5 w-3.5 animate-spin text-indigo-400" />}
            </div>
            <p className="text-[11px] text-zinc-400">
              Trigger signed order.paid webhook.
            </p>
          </button>
        </div>

        {/* Output Result Card */}
        <div className="pt-1">
          {lastResult ? (
            <div
              className={`p-4 rounded-xl border text-xs space-y-2.5 shadow-xs ${
                lastResult.status === 'success'
                  ? 'bg-emerald-950/25 border-emerald-500/35'
                  : lastResult.status === 'blocked'
                  ? 'bg-rose-950/25 border-rose-500/35'
                  : lastResult.status === 'info'
                  ? 'bg-amber-950/25 border-amber-500/35'
                  : 'bg-zinc-900/80 border-zinc-800'
              }`}
            >
              <div className="flex items-center gap-2 font-semibold">
                {lastResult.status === 'success' && <Check className="h-4 w-4 text-emerald-400" />}
                {lastResult.status === 'blocked' && <ShieldAlert className="h-4 w-4 text-rose-400" />}
                {lastResult.status === 'info' && <AlertCircle className="h-4 w-4 text-amber-400" />}
                {lastResult.status === 'error' && <AlertCircle className="h-4 w-4 text-rose-400" />}
                <span
                  className={
                    lastResult.status === 'success'
                      ? 'text-emerald-300'
                      : lastResult.status === 'blocked'
                      ? 'text-rose-300'
                      : lastResult.status === 'info'
                      ? 'text-amber-300'
                      : 'text-rose-300'
                  }
                >
                  {lastResult.title}
                </span>
              </div>
              <p className="text-zinc-300 leading-relaxed text-[11.5px]">{lastResult.description}</p>
              {lastResult.details && (
                <div className="mt-2 pt-2 border-t border-zinc-800/80 grid grid-cols-2 gap-2 text-[11px] font-mono">
                  {Object.entries(lastResult.details).map(([key, val]) => (
                    <div key={key} className="bg-black/20 p-1.5 rounded border border-white/5">
                      <span className="text-zinc-400 capitalize">{key.replace(/_/g, ' ')}:</span>{' '}
                      <span className="text-zinc-100 font-semibold">{Array.isArray(val) ? val.join(', ') : String(val)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="p-5 rounded-xl bg-zinc-900/40 border border-zinc-800/60 text-xs text-zinc-400 text-center py-6">
              Click any of the 4 test actions above to simulate an autonomous agent transaction.
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end pt-1">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-semibold transition cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
