# AegisPay Gateway: Agentic Commerce Implementation Plan

## 1. System Architecture & Standards

AegisPay is a secure, middleware gateway enabling autonomous AI agents to negotiate and transact with merchants using standard AP2 (Agent Payments Protocol) cryptographic mandates and Razorpay APIs [cite: 1.2.1, 1.2.2]. It explicitly divides the workflow into a flexible AI reasoning layer and a deterministic, tamper-proof execution environment.

### 1.1 Core Architecture Flow

1.  **Discovery (ACP/UCP Layer):** The AI Buyer queries the merchant's semantic catalog (Supabase `pgvector`).
2.  **Authorization (AP2 Layer):** The Buyer provides a Delegated Intent Token (DIT) or AP2 Mandate defining `max_budget` [cite: 1.2.1].
3.  **Negotiation Sandbox:** A bounded FastAPI route where the LLM negotiates the price. An internal guardrail (hallucination detection validator) ensures the LLM does not hallucinate discounts below the `price_floor`.
4.  **Deterministic Settlement:** FastAPI generates a Razorpay Order ID [cite: 1.1.5]. The backend listens for the `order.paid` webhook, verifying the `x-razorpay-signature` [cite: 1.1.3].

---

## 2. Environment & Database Initialization (Supabase)

**Agent Instructions:** Initialize a Supabase project and execute the following SQL to set up vector storage and relational tables.

```sql
-- Enable vector extension for semantic catalog search
CREATE EXTENSION IF NOT EXISTS vector;

-- Product Catalog
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    mrp DECIMAL(10,2) NOT NULL,
    price_floor DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0,
    embedding vector(1536) -- OpenAI text-embedding-3-small
);

-- Agentic Orders (Razorpay linked)
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    razorpay_order_id TEXT UNIQUE NOT NULL,
    agent_id TEXT NOT NULL,
    negotiated_price DECIMAL(10,2) NOT NULL,
    status TEXT DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PAID', 'FAILED', 'BLOCKED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Immutable Audit Log
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(id),
    event_type TEXT NOT NULL,
    payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 3. Backend Implementation (Python / FastAPI)

**Agent Instructions:** Set up a FastAPI project. This acts as the policy firewall and the AP2 mandate verifier [cite: 1.2.1].

### 3.1 Project Setup
```bash
pip install fastapi uvicorn supabase pydantic langchain openai python-jose razorpay
```

### 3.2 AP2 Mandate / DIT Security Firewall
Create `middleware.py` to intercept requests.
```python
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer
from jose import jwt

# Simulating AP2 mandate verification
def verify_agent_mandate(token: str = Security(HTTPBearer())):
    try:
        # Secret should match the issuer's key
        payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        if payload.get("max_budget") < 0:
            raise ValueError("Invalid budget")
        return payload
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid or expired AP2 mandate")
```

### 3.3 The Bounded Negotiation Engine
Create `routes/negotiate.py`. 
**Crucial Instruction for AI Agent:** Ensure you implement a strict hallucination detection check before validating the LLM's final price. Do not rely solely on the LLM to respect the `price_floor`.

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel
import supabase

router = APIRouter()

class NegotiateRequest(BaseModel):
    product_id: str
    proposed_price: float

@router.post("/api/v1/agent/negotiate")
async def negotiate_price(req: NegotiateRequest, mandate: dict = Depends(verify_agent_mandate)):
    # 1. Fetch product from Supabase
    # 2. Hallucination / Firewall Check: Is proposed price below floor?
    # 3. Guardrail: Is proposed price > mandate['max_budget']?
    # 4. If pass, trigger Razorpay Order creation.
    pass
```

### 3.4 Razorpay Webhook Verification
Create `routes/webhooks.py`. This is strictly deterministic [cite: 1.1.2].

```python
import razorpay
from fastapi import Request, Header, HTTPException

rzp_client = razorpay.Client(auth=("YOUR_KEY_ID", "YOUR_KEY_SECRET"))

@router.post("/api/v1/webhooks/razorpay")
async def razorpay_webhook(req: Request, x_razorpay_signature: str = Header(None)):
    payload = await req.body()
    try:
        # Verify the signature against your webhook secret [cite: 1.1.3]
        rzp_client.utility.verify_webhook_signature(
            payload.decode("utf-8"), 
            x_razorpay_signature, 
            "YOUR_WEBHOOK_SECRET"
        )
        # Update Supabase orders table to 'PAID'
        return {"status": "ok"}
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid Signature")
```

---

## 4. Frontend Command Center (Vite + React + TypeScript)

**Agent Instructions:** Create a real-time monitoring dashboard for the merchant. The design language must be minimalist and modern, incorporating subtle street-style typography for the headers.

### 4.1 Setup
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install @supabase/supabase-js tailwindcss lucide-react
```

### 4.2 Real-time Audit Hook
Create `useAuditLogs.ts` to subscribe to Supabase.
```typescript
import { useEffect, useState } from 'react';
import { supabase } from './supabaseClient';

export function useAuditLogs() {
    const [logs, setLogs] = useState<any[]>([]);

    useEffect(() => {
        const channel = supabase
            .channel('audit-inserts')
            .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'audit_logs' }, (payload) => {
                setLogs((prev) => [payload.new, ...prev]);
            })
            .subscribe();
        return () => { supabase.removeChannel(channel) };
    }, []);

    return logs;
}
```

### 4.3 UI Implementation Details
*   **Split View:** Left side showing real-time agent semantic search queries; Right side showing successful Razorpay settlements.
*   **Styling:** Use a stark monochrome palette (black, white, zinc-800) with bold, graffiti-inspired accent fonts for the dashboard metrics to give it a modern, aggressive tech feel.

---

## 5. End-to-End Testing (The 5-Minute Demo Script)

**Agent Instructions:** Build `scripts/demo_runner.py` to automate the transaction for the video recording.
1.  **Generate DIT:** Create a valid JWT payload for the AI buyer [cite: 1.2.2].
2.  **Semantic Search:** Fire a natural language query to the FastAPI backend.
3.  **Haggle & Settle:** Submit a price exactly at the `price_floor`. Ensure the backend calls the Razorpay API to generate an `order_id` [cite: 1.1.5].
4.  **Inject Attack:** Attempt to pass a price below the floor, proving the API rejects it automatically and logs it in the UI.
