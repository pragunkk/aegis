import { useEffect, useState, useCallback } from 'react';
import { supabase, isSupabaseConfigured } from '../lib/supabaseClient';
import { fetchAuditLogs } from '../lib/api';
import type { AuditLog } from '../types';

export function useAuditLogs() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isLive, setIsLive] = useState<boolean>(false);

  const refreshLogs = useCallback(async () => {
    try {
      const data = await fetchAuditLogs(100);
      setLogs(data);
      setIsLive(true);
    } catch (err) {
      console.warn('Could not fetch audit logs from backend:', err);
      setIsLive(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Initial fetch
    refreshLogs();

    // 1. If Supabase is configured, subscribe to postgres_changes channel
    const client = supabase;
    if (isSupabaseConfigured && client) {
      const channel = client
        .channel('audit-inserts')
        .on(
          'postgres_changes',
          { event: 'INSERT', schema: 'public', table: 'audit_logs' },
          (payload) => {
            const newLog = payload.new as AuditLog;
            setLogs((prev) => [newLog, ...prev.filter((l) => l.id !== newLog.id)]);
          }
        )
        .subscribe((status) => {
          if (status === 'SUBSCRIBED') {
            setIsLive(true);
          }
        });

      return () => {
        client.removeChannel(channel);
      };
    } else {
      // 2. Fallback: Fast polling interval for local backend testing
      const interval = setInterval(refreshLogs, 1500);
      return () => clearInterval(interval);
    }
  }, [refreshLogs]);

  return { logs, setLogs, loading, isLive, refreshLogs };
}
