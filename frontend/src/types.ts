export type OrderStatus = 'PENDING' | 'PAID' | 'FAILED' | 'BLOCKED';

export interface Product {
  id: string;
  name: string;
  description?: string;
  mrp: number;
  price_floor?: number;
  stock: number;
  similarity_score?: number;
}

export interface AuditLog {
  id: string;
  order_id?: string | null;
  agent_id?: string | null;
  event_type: string;
  payload: Record<string, any>;
  created_at?: string;
}

export interface Order {
  id: string;
  razorpay_order_id: string;
  agent_id: string;
  product_id?: string;
  negotiated_price: number;
  currency: string;
  status: OrderStatus;
  created_at?: string;
  updated_at?: string;
}

export interface AP2Mandate {
  sub: string;
  max_budget: number;
  currency: string;
  exp?: number;
  iat?: number;
  scope?: string[];
}

export interface NegotiationResult {
  success: boolean;
  decision: {
    status: string;
    message: string;
    product_id: string;
    negotiated_price?: number;
    razorpay_order_id?: string;
    amount_in_subunits?: number;
    currency: string;
  };
  audit_event_id?: string;
}
