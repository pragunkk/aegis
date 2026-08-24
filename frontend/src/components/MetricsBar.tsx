import React from 'react';
import { ShieldAlert, CheckCircle2, ShieldCheck, TrendingUp } from 'lucide-react';
import type { AuditLog } from '../types';

interface MetricsBarProps {
  logs: AuditLog[];
}

export const MetricsBar: React.FC<MetricsBarProps> = ({ logs }) => {
  const attacksBlocked = logs.filter((l) => l.event_type === 'PRICE_ATTACK_BLOCKED').length;
  const mandatesVerified = logs.filter((l) => l.event_type === 'MANDATE_VERIFIED').length;
  const ordersCreated = logs.filter((l) => l.event_type === 'ORDER_CREATED').length;
  const paymentsConfirmed = logs.filter((l) => l.event_type === 'PAYMENT_CONFIRMED' || l.event_type === 'SETTLEMENT_CONFIRMED');

  const totalSettledRupees = paymentsConfirmed.reduce((sum, item) => {
    const amt = item.payload?.negotiated_price || item.payload?.amount_paid || (item.payload?.amount ? item.payload.amount / 100 : 0);
    return sum + (Number(amt) || 0);
  }, 0);

  const stats = [
    {
      title: 'Attacks Blocked',
      subtitle: 'Sub-floor exploits intercepted',
      value: attacksBlocked,
      icon: ShieldAlert,
      iconBg: 'bg-rose-500/10 text-rose-400 border border-rose-500/25',
      valueColor: attacksBlocked > 0 ? 'text-rose-400' : 'text-zinc-100',
      borderHighlight: 'hover:border-rose-500/30',
    },
    {
      title: 'Settled Revenue',
      subtitle: 'HMAC verified Razorpay payments',
      value: `₹${totalSettledRupees.toLocaleString('en-IN', { minimumFractionDigits: 0 })}`,
      icon: TrendingUp,
      iconBg: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/25',
      valueColor: 'text-emerald-400',
      borderHighlight: 'hover:border-emerald-500/30',
    },
    {
      title: 'AP2 Mandates',
      subtitle: 'Cryptographic DIT tokens validated',
      value: mandatesVerified,
      icon: ShieldCheck,
      iconBg: 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/25',
      valueColor: 'text-zinc-100',
      borderHighlight: 'hover:border-indigo-500/30',
    },
    {
      title: 'Orders Created',
      subtitle: 'Bounded negotiations accepted',
      value: ordersCreated,
      icon: CheckCircle2,
      iconBg: 'bg-blue-500/10 text-blue-400 border border-blue-500/25',
      valueColor: 'text-zinc-100',
      borderHighlight: 'hover:border-blue-500/30',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, i) => {
        const Icon = stat.icon;
        return (
          <div
            key={i}
            className={`p-4 rounded-xl bg-[#111115] border border-zinc-800/80 ${stat.borderHighlight} transition-all duration-200 flex flex-col justify-between shadow-xs`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-zinc-400">
                {stat.title}
              </span>
              <div className={`p-2 rounded-lg ${stat.iconBg}`}>
                <Icon className="h-4 w-4" />
              </div>
            </div>
            <div className="mt-3.5">
              <div className={`text-2xl font-heading font-bold tracking-tight ${stat.valueColor}`}>
                {stat.value}
              </div>
              <p className="text-[11px] text-zinc-500 mt-0.5 font-normal">
                {stat.subtitle}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
};
