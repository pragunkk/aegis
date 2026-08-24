import { useState } from 'react';
import { Header } from './components/Header';
import { MetricsBar } from './components/MetricsBar';
import { AgentActivityFeed } from './components/AgentActivityFeed';
import { SettlementFeed } from './components/SettlementFeed';
import { SimulatorWidget } from './components/SimulatorWidget';
import { CatalogDrawer } from './components/CatalogDrawer';
import { useAuditLogs } from './hooks/useAuditLogs';
import { ShieldCheck, Play, Package } from 'lucide-react';

export function App() {
  const { logs, isLive, refreshLogs } = useAuditLogs();
  const [isSimulatorOpen, setIsSimulatorOpen] = useState(false);
  const [isCatalogOpen, setIsCatalogOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-100 flex flex-col selection:bg-indigo-500 selection:text-white">
      {/* Top Header Navigation */}
      <Header
        isLive={isLive}
        onOpenSimulator={() => setIsSimulatorOpen(true)}
        onOpenCatalog={() => setIsCatalogOpen(true)}
        onRefresh={refreshLogs}
      />

      {/* Main Dashboard Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-7 space-y-6">
        {/* Dashboard Title & Quick Actions */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-heading font-bold text-white tracking-tight">
              Merchant Gateway Dashboard
            </h1>
            <p className="text-xs text-zinc-400 mt-1">
              Live monitoring for AP2 autonomous agent negotiations, price floor policy defenses, and Razorpay settlements.
            </p>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={() => setIsCatalogOpen(true)}
              className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-[#141418] hover:bg-zinc-800 border border-zinc-800 text-zinc-300 text-xs font-medium transition cursor-pointer"
            >
              <Package className="h-4 w-4 text-zinc-400" />
              <span>Catalog & Margins</span>
            </button>
            <button
              onClick={() => setIsSimulatorOpen(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-sm transition cursor-pointer"
            >
              <Play className="h-3.5 w-3.5 fill-current" />
              <span>Simulate Agent Actions</span>
            </button>
          </div>
        </div>

        {/* Real-time KPI Metrics Cards */}
        <MetricsBar logs={logs} />

        {/* 2-Column Split View */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Left Column: Agent Activity & Policy Interceptions */}
          <AgentActivityFeed logs={logs} />

          {/* Right Column: Razorpay Settlement & Order Stream */}
          <SettlementFeed logs={logs} />
        </div>
      </main>

      {/* Minimal Footer */}
      <footer className="border-t border-zinc-800/80 bg-[#0c0c10] px-6 py-4 text-xs text-zinc-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-indigo-400" />
            <span className="font-medium text-zinc-400">AegisPay Gateway</span>
            <span>— Agent Payments Protocol & Razorpay Integration</span>
          </div>
          <div className="flex items-center gap-4 text-zinc-500 text-[11px]">
            <span>FastAPI</span>
            <span>Supabase pgvector</span>
            <span>AP2 Mandates</span>
            <span>Razorpay Webhooks</span>
          </div>
        </div>
      </footer>

      {/* Simulator Modal */}
      <SimulatorWidget
        isOpen={isSimulatorOpen}
        onClose={() => setIsSimulatorOpen(false)}
        onActionComplete={refreshLogs}
      />

      {/* Merchant Product Catalog Modal */}
      <CatalogDrawer
        isOpen={isCatalogOpen}
        onClose={() => setIsCatalogOpen(false)}
      />
    </div>
  );
}

export default App;
