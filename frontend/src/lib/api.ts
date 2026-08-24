import type { Product, AuditLog } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'https://aegis-backend-zxq7.onrender.com';

export async function fetchProducts(): Promise<Product[]> {
  const res = await fetch(`${API_BASE}/api/v1/products`);
  if (!res.ok) throw new Error('Failed to fetch product catalog');
  return res.json();
}

export async function discoverProducts(query: string, limit = 5): Promise<Product[]> {
  const res = await fetch(`${API_BASE}/api/v1/agent/discover`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, limit }),
  });
  if (!res.ok) throw new Error('Discovery query failed');
  return res.json();
}

export async function fetchTestToken(
  agentId = 'agent_simulator_007',
  maxBudget = 10000.0
): Promise<string> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/test/token?agent_id=${agentId}&max_budget=${maxBudget}`);
    if (res.ok) {
      const data = await res.json();
      return data.token;
    }
  } catch (e) {
    console.warn('Could not fetch dynamic test token:', e);
  }
  // Fallback signed token
  return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZ2VudF9zaW11bGF0b3JfMDA3IiwibWF4X2J1ZGdldCI6MTAwMDAuMCwiY3VycmVuY3kiOiJJTlIiLCJpYXQiOjE3ODc1ODg0ODUsImV4cCI6MTgxOTEyNDQ4NSwic2NvcGUiOlsiY29tbWVyY2U6bmVnb3RpYXRlIiwiY29tbWVyY2U6dHJhbnNhY3QiXX0.-idEtk4Nls4esjTmydPDeMa7aHWBHSV1hGfs676sGoM';
}

export async function negotiatePrice(
  token: string,
  productId: string,
  proposedPrice: number,
  reasoning?: string
): Promise<{ ok: boolean; status: number; data: any }> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/agent/negotiate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        product_id: productId,
        proposed_price: proposedPrice,
        reasoning: reasoning || 'Automated agent pricing negotiation proposal',
      }),
    });

    const data = await res.json().catch(() => ({}));
    return { ok: res.ok, status: res.status, data };
  } catch (err: any) {
    return {
      ok: false,
      status: 500,
      data: { message: err.message || 'Network request failed' },
    };
  }
}

export async function sendMockWebhook(
  orderId: string,
  amount: number
): Promise<{ ok: boolean; data: any }> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/test/settle-order`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ order_id: orderId, amount }),
    });
    const data = await res.json().catch(() => ({}));
    return { ok: res.ok, data };
  } catch (err: any) {
    return { ok: false, data: { error: err.message } };
  }
}

export async function fetchAuditLogs(limit = 50): Promise<AuditLog[]> {
  const res = await fetch(`${API_BASE}/api/v1/audit/logs?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to fetch audit logs');
  return res.json();
}

export async function fetchHealth(): Promise<{ status: string; service: string }> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Backend health check failed');
  return res.json();
}
