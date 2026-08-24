import React from 'react';
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
  return (
    <header className="border-b border-zinc-800/80 bg-[#0c0c10]/95 backdrop-blur-md sticky top-0 z-40 px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-lg bg-indigo-600 flex items-center justify-center shadow-md shadow-indigo-950 text-white font-bold">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-heading font-bold text-lg text-white tracking-tight">
                AegisPay
              </span>
              <span className="text-[11px] font-medium bg-zinc-800 text-zinc-300 px-2 py-0.5 rounded-full border border-zinc-700">
                Gateway
              </span>
            </div>
            <p className="text-xs text-zinc-400">
              Agent Payments Protocol & Razorpay Policy Firewall
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-3">
          {/* Live Status */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-zinc-900 border border-zinc-800 text-xs font-medium">
            <span
              className={`h-2 w-2 rounded-full ${
                isLive ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
              }`}
            />
            <span className={isLive ? 'text-zinc-300' : 'text-zinc-400'}>
              {isLive ? 'Live Connected' : 'Connecting...'}
            </span>
          </div>

          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            title="Refresh stream"
            className="p-2 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition cursor-pointer"
          >
            <RefreshCw className="h-4 w-4" />
          </button>

          {/* View Catalog */}
          <button
            onClick={onOpenCatalog}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-700/80 text-zinc-200 text-xs font-medium transition cursor-pointer"
          >
            <Package className="h-4 w-4 text-zinc-400" />
            <span>Product Margins</span>
          </button>

          {/* Open Test Simulator */}
          <button
            onClick={onOpenSimulator}
            className="flex items-center gap-2 px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-sm transition cursor-pointer"
          >
            <Play className="h-3.5 w-3.5 fill-current" />
            <span>Test Agent</span>
          </button>
        </div>
      </div>
    </header>
  );
};
