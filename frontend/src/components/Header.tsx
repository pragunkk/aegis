import React, { useState } from 'react';
import { ShieldCheck, Play, Package, RefreshCw } from 'lucide-react';

interface HeaderProps {
  isLive: boolean;
  onOpenSimulator: () => void;
  onOpenCatalog: () => void;
  onRefresh: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  isLive,
  onOpenSimulator,
  onOpenCatalog,
  onRefresh,
}) => {
  const [isRotating, setIsRotating] = useState(false);

  const handleRefreshClick = () => {
    setIsRotating(true);
    onRefresh();
    setTimeout(() => setIsRotating(false), 700);
  };

  return (
    <header className="border-b border-zinc-800/80 bg-[#0c0c10]/95 backdrop-blur-md sticky top-0 z-40 px-6 py-3.5 transition-all">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        {/* Brand Identity */}
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-700 flex items-center justify-center shadow-lg shadow-indigo-950/50 text-white font-bold ring-1 ring-white/20">
            <ShieldCheck className="h-5 w-5 drop-shadow-xs" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-heading font-bold text-lg text-white tracking-tight">
                AegisPay
              </span>
              <span className="text-[10px] font-semibold bg-indigo-500/15 text-indigo-300 px-2 py-0.5 rounded-full border border-indigo-500/30 tracking-wide uppercase">
                Gateway
              </span>
            </div>
            <p className="text-xs text-zinc-400 font-normal">
              AP2 Agent Payments & Razorpay Policy Firewall
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2.5">
          {/* Live Status Indicator */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-zinc-900/90 border border-zinc-800 text-xs font-medium shadow-xs">
            <span
              className={`h-2 w-2 rounded-full transition-colors ${
                isLive ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)] animate-pulse' : 'bg-amber-400'
              }`}
            />
            <span className={isLive ? 'text-zinc-200' : 'text-zinc-400'}>
              {isLive ? 'Realtime Connected' : 'Polling Active'}
            </span>
          </div>

          {/* Quick Refresh Stream */}
          <button
            onClick={handleRefreshClick}
            title="Refresh logs stream"
            className="p-2 rounded-lg bg-zinc-900/80 border border-zinc-800 hover:border-zinc-700 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition cursor-pointer"
          >
            <RefreshCw className={`h-4 w-4 transition-transform duration-700 ${isRotating ? 'rotate-180' : ''}`} />
          </button>

          {/* Product Margins Drawer */}
          <button
            onClick={onOpenCatalog}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-[#141419] hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 text-zinc-300 hover:text-white text-xs font-medium transition cursor-pointer"
          >
            <Package className="h-4 w-4 text-zinc-400" />
            <span>Product Margins</span>
          </button>

          {/* Launch Agent Simulator */}
          <button
            onClick={onOpenSimulator}
            className="flex items-center gap-2 px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-950/40 transition cursor-pointer active:scale-98"
          >
            <Play className="h-3.5 w-3.5 fill-current" />
            <span>Simulate Agent</span>
          </button>
        </div>
      </div>
    </header>
  );
};
