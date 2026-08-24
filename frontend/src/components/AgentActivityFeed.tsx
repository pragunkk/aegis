import React, { useState } from 'react';
import { ShieldAlert, Search, Key, AlertTriangle, Radio, Info } from 'lucide-react';
import type { AuditLog } from '../types';

interface AgentActivityFeedProps {
  logs: AuditLog[];
}

export const AgentActivityFeed: React.FC<AgentActivityFeedProps> = ({ logs }) => {
  const [filter, setFilter] = useState<'ALL' | 'ATTACKS' | 'SEARCH' | 'MANDATES'>('ALL');

  const agentLogs = logs.filter((l) =>
    [
      'DISCOVERY_QUERY',
      'MANDATE_VERIFIED',
      'MANDATE_REJECTED',
      'PRICE_ATTACK_BLOCKED',
      'BUDGET_EXCEEDED',
    ].includes(l.event_type)
  );

  const attacksCount = agentLogs.filter((l) => l.event_type === 'PRICE_ATTACK_BLOCKED' || l.event_type === 'BUDGET_EXCEEDED').length;
  const searchCount = agentLogs.filter((l) => l.event_type === 'DISCOVERY_QUERY').length;
  const mandateCount = agentLogs.filter((l) => l.event_type === 'MANDATE_VERIFIED' || l.event_type === 'MANDATE_REJECTED').length;

  const filteredLogs = agentLogs.filter((l) => {
    if (filter === 'ATTACKS') return l.event_type === 'PRICE_ATTACK_BLOCKED' || l.event_type === 'BUDGET_EXCEEDED';
    if (filter === 'SEARCH') return l.event_type === 'DISCOVERY_QUERY';
    if (filter === 'MANDATES') return l.event_type === 'MANDATE_VERIFIED' || l.event_type === 'MANDATE_REJECTED';
    return true;
  });

  return (
    <div className="flex flex-col h-[580px] rounded-xl border border-zinc-800/80 bg-[#111115] overflow-hidden shadow-xs">
      {/* Feed Header */}
      <div className="px-5 py-3.5 border-b border-zinc-800/70 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-[#15151a]">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-md bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Radio className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-zinc-100">
              Agent Traffic & Policy Firewall
            </h3>
            <p className="text-[11px] text-zinc-400">Live intent queries & blocked exploits</p>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center gap-1 bg-zinc-900/90 p-1 rounded-lg border border-zinc-800 text-xs">
          <button
            onClick={() => setFilter('ALL')}
            className={`px-2.5 py-1 rounded-md transition cursor-pointer flex items-center gap-1.5 ${
              filter === 'ALL' ? 'bg-zinc-800 text-white font-medium shadow-xs' : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <span>All</span>
            <span className="text-[10px] text-zinc-500 font-mono">({agentLogs.length})</span>
          </button>
          <button
            onClick={() => setFilter('ATTACKS')}
            className={`px-2.5 py-1 rounded-md transition cursor-pointer flex items-center gap-1.5 ${
              filter === 'ATTACKS' ? 'bg-rose-500/20 text-rose-300 font-medium' : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <span>Attacks</span>
            {attacksCount > 0 && (
              <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-rose-500/30 text-rose-300 font-semibold font-mono">
                {attacksCount}
              </span>
            )}
          </button>
          <button
            onClick={() => setFilter('SEARCH')}
            className={`px-2.5 py-1 rounded-md transition cursor-pointer flex items-center gap-1.5 ${
              filter === 'SEARCH' ? 'bg-zinc-800 text-white font-medium' : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <span>Searches</span>
            <span className="text-[10px] text-zinc-500 font-mono">({searchCount})</span>
          </button>
          <button
            onClick={() => setFilter('MANDATES')}
            className={`px-2.5 py-1 rounded-md transition cursor-pointer flex items-center gap-1.5 ${
              filter === 'MANDATES' ? 'bg-zinc-800 text-white font-medium' : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <span>Mandates</span>
            <span className="text-[10px] text-zinc-500 font-mono">({mandateCount})</span>
          </button>
        </div>
      </div>

      {/* Feed List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2.5">
        {filteredLogs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-zinc-500 text-xs space-y-2 py-12">
            <Info className="h-6 w-6 text-zinc-600" />
            <p>No activity logged for this category yet.</p>
            <p className="text-[11px] text-zinc-600">Run the Agent Simulator to trigger live transactions.</p>
          </div>
        ) : (
          filteredLogs.map((log) => {
            const time = log.created_at
              ? new Date(log.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
              : 'Just now';

            if (log.event_type === 'PRICE_ATTACK_BLOCKED') {
              return (
                <div
                  key={log.id}
                  className="p-3.5 rounded-xl bg-rose-950/20 border border-rose-500/30 space-y-2 transition shadow-xs"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="p-1 rounded bg-rose-500/20 text-rose-400">
                        <ShieldAlert className="h-3.5 w-3.5" />
                      </div>
                      <span className="text-xs font-semibold text-rose-300">
                        Sub-Floor Price Attack Blocked
                      </span>
                    </div>
                    <span className="text-[11px] text-zinc-500 font-mono">{time}</span>
                  </div>

                  <div className="text-xs text-zinc-300 space-y-1.5">
                    <div className="font-medium text-zinc-200">
                      Product: {log.payload?.product_name || 'Protected Catalog Item'}
                    </div>
                    <div className="flex items-center gap-4 text-xs bg-black/20 p-2 rounded-lg border border-rose-500/15">
                      <div>
                        <span className="text-zinc-500 text-[11px]">Offered:</span>{' '}
                        <span className="text-rose-400 font-semibold line-through">
                          ₹{log.payload?.proposed_price}
                        </span>
                      </div>
                      <div>
                        <span className="text-zinc-500 text-[11px]">Protected Floor:</span>{' '}
                        <span className="text-emerald-400 font-semibold">
                          ₹{log.payload?.price_floor}
                        </span>
                      </div>
                      <div className="ml-auto text-[11px] text-rose-300 font-mono">
                        -₹{log.payload?.delta_below_floor} exploit halted
                      </div>
                    </div>
                  </div>
                </div>
              );
            }

            if (log.event_type === 'DISCOVERY_QUERY') {
              return (
                <div
                  key={log.id}
                  className="p-3.5 rounded-xl bg-zinc-900/60 border border-zinc-800/80 hover:border-zinc-700/80 transition space-y-1.5 shadow-xs"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Search className="h-3.5 w-3.5 text-cyan-400" />
                      <span className="text-xs font-medium text-zinc-300">
                        Semantic Catalog Search
                      </span>
                    </div>
                    <span className="text-[11px] text-zinc-500 font-mono">{time}</span>
                  </div>
                  <p className="text-xs text-zinc-100 font-medium">
                    "{log.payload?.query}"
                  </p>
                  <div className="flex items-center justify-between text-[11px] text-zinc-400 pt-0.5">
                    <span>Matched {log.payload?.results_count || 0} product(s)</span>
                    <span className="text-zinc-500 font-mono text-[10px] bg-zinc-800/60 px-1.5 py-0.5 rounded">pgvector cosine</span>
                  </div>
                </div>
              );
            }

            if (log.event_type === 'MANDATE_VERIFIED') {
              return (
                <div
                  key={log.id}
                  className="p-3.5 rounded-xl bg-zinc-900/60 border border-zinc-800/80 space-y-1.5 shadow-xs"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Key className="h-3.5 w-3.5 text-indigo-400" />
                      <span className="text-xs font-medium text-zinc-300">
                        AP2 Token Authorized
                      </span>
                    </div>
                    <span className="text-[11px] text-zinc-500 font-mono">{time}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs text-zinc-300">
                    <span className="text-zinc-400 font-mono text-[11px] truncate max-w-[200px]">
                      Agent: {log.agent_id}
                    </span>
                    <span className="text-indigo-300 font-medium">
                      Max Budget: ₹{log.payload?.max_budget?.toLocaleString('en-IN')}
                    </span>
                  </div>
                </div>
              );
            }

            if (log.event_type === 'BUDGET_EXCEEDED') {
              return (
                <div
                  key={log.id}
                  className="p-3.5 rounded-xl bg-amber-950/20 border border-amber-500/30 space-y-1.5 shadow-xs"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
                      <span className="text-xs font-semibold text-amber-300">
                        Mandate Budget Exceeded
                      </span>
                    </div>
                    <span className="text-[11px] text-zinc-500 font-mono">{time}</span>
                  </div>
                  <p className="text-xs text-zinc-300">
                    Offer ₹{log.payload?.proposed_price} exceeds token max budget ₹{log.payload?.mandate_max_budget}.
                  </p>
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
