# 🛡️ AegisPay Gateway: Agentic Commerce Middleware

> **A cryptographically verifiable, policy-firewalled gateway enabling autonomous AI agents to negotiate and transact with merchants using standard Agent Payments Protocol (AP2) mandates, pgvector semantic discovery, and deterministic Razorpay settlement.**

---

## 📌 Table of Contents

1. [System Architecture & Standards](#-system-architecture--standards)
2. [Core Architecture Flow](#-core-architecture-flow)
3. [Exact Repository File Structure](#-exact-repository-file-structure)
4. [Security, Firewall & AP2 Protocol Specifications](#-security-firewall--ap2-protocol-specifications)
5. [Database Schema & Seed Data](#-database-schema--seed-data)
6. [API Reference & Route Specifications](#-api-reference--route-specifications)
7. [Frontend Command Center Overview](#-frontend-command-center-overview)
8. [Installation & Setup Guide](#-installation--setup-guide)
9. [Running the Application](#-running-the-application)
10. [Testing & Verification Guide](#-testing--verification-guide)
    - [Automated Unit & Integration Tests (pytest)](#1-automated-unit--integration-tests-pytest)
    - [Automated 5-Minute Demo Script (CLI)](#2-automated-5-minute-demo-script-cli)
    - [Manual Browser Testing via Command Center](#3-manual-browser-testing-via-command-center)
11. [Environment Variables Reference](#-environment-variables-reference)
12. [Current Hard-Coded Elements & Production Roadmap](#-current-hard-coded-elements--production-roadmap)
    - [Current Hard-Coded / In-Memory Mock Fallbacks](#1-current-hard-coded--in-memory-mock-fallbacks)
    - [Pending Implementations & Production Roadmap](#2-pending-implementations--production-roadmap)

---

## 🏛️ System Architecture & Standards

AegisPay sits as a security and policy enforcement middleware between **Autonomous AI Buyer Agents** and **Merchant Payment Infrastructure (Razorpay & Supabase)**.

It explicitly divides the agentic commerce workflow into two isolated layers:
- **Flexible AI Reasoning Layer**: Enables autonomous discovery and natural language negotiation.
- **Deterministic Tamper-Proof Execution Environment**: Strict price-floor firewalls, cryptographic JWT mandate validation, and HMAC-SHA256 signed Razorpay settlements.

```
                                 AEGISPAY GATEWAY ARCHITECTURE
                                 
 +---------------------+               +-------------------------------------------------------------+
 |                     |  AP2 Mandate  |                     AegisPay Gateway                        |
 |   AI Buyer Agent    |  (JWT Token)  |                                                             |
 |  (Autonomous LLM)   | ------------> |  [1] AP2 Mandate Security Middleware                        |
 |                     |  Negotiation  |      - Decodes cryptographic Delegated Intent Token (DIT)   |
 +---------------------+               |      - Validates signature, expiry & max_budget limits     |
            |                          |                                                             |
            | Semantic Discovery       |  [2] Semantic Product Discovery Layer                       |
            | Intent Queries           |      - Natural language vector search (pgvector)            |
            v                          |      - Strips & shields confidential merchant price floors  |
 +---------------------+               |                                                             |
 |  Merchant Catalog   | <-----------> |  [3] Bounded Negotiation Engine & Policy Firewall           |
 | (Supabase pgvector) |               |      - Deterministic Price-Floor Hallucination Defense      |
 +---------------------+               |      - Rejects proposals below floor (HTTP 422 Blocked)     |
                                       |      - Approves valid offers & invokes Razorpay API         |
                                       |                                                             |
                                       |  [4] Razorpay Deterministic Settlement Handler              |
                                       |      - Validates x-razorpay-signature (HMAC-SHA256)         |
                                       |      - Transitions order state to PAID                      |
                                       |                                                             |
                                       |  [5] Immutable Audit Trail Ledger                           |
                                       |      - Persists security violations & transaction events    |
                                       +-------------------------------------------------------------+
                                                    |                                 |
                                                    v                                 v
                                      +--------------------------+      +---------------------------+
                                      |  Razorpay Payment Engine |      | Merchant Command Center   |
                                      |  (Orders, Webhooks API)  |      | (Vite + React Dashboard)  |
                                      +--------------------------+      +---------------------------+
```

---

## 🔄 Core Architecture Flow

1. **Discovery (ACP/UCP Layer)**:
   The AI Buyer queries the merchant's semantic catalog. AegisPay matches products via vector embeddings and keyword indexes while **strictly stripping confidential price floors** from public responses.
2. **Authorization (AP2 Protocol Layer)**:
   The agent presents an **AP2 Delegated Intent Token (DIT)**—a signed cryptographic JWT declaring `agent_id`, authorized `max_budget`, currency, and capabilities.
3. **Bounded Negotiation & Firewall Interception**:
   The agent submits a price proposal. The gateway evaluates it against deterministic guardrails:
   - **Hallucination / Sub-Floor Attack Check**: If `proposed_price < price_floor`, the request is **immediately halted with HTTP 422** and logged as `PRICE_ATTACK_BLOCKED`.
   - **Budget Guardrail Check**: If `proposed_price > mandate.max_budget`, the request is rejected with `BUDGET_EXCEEDED`.
   - **Approved Negotiation**: If `price_floor <= proposed_price <= max_budget`, the price is locked and a Razorpay Order ID is generated.
4. **Deterministic Settlement**:
   Razorpay triggers an `order.paid` webhook with header `x-razorpay-signature`. The gateway verifies the cryptographic signature using HMAC-SHA256 and transitions the order to `PAID`.
5. **Real-time Observability**:
   The Merchant Command Center displays live agent telemetry, blocked attacks, and settlements.

---

## 📂 Exact Repository File Structure

```
aegis/
├── .env.example                          # Environment variables template
├── Implementation.md                     # Original hackathon specifications
├── pytest.ini                            # Asyncio-aware pytest configuration
├── README.md                             # Comprehensive project documentation
├── requirements.txt                      # Backend Python dependencies
│
├── database/
│   ├── schema.sql                        # Supabase pgvector schema (products, orders, audit_logs)
│   └── seed.sql                          # Seed products with MRPs and confidential price floors
│
├── backend/
│   └── app/
│       ├── __init__.py                   # App package initialization
│       ├── config.py                     # Pydantic BaseSettings environment manager
│       ├── database.py                   # Unified repository (Supabase + local mock fallback)
│       ├── main.py                       # FastAPI application entrypoint, CORS, & routers
│       │
│       ├── middleware/
│       │   ├── __init__.py
│       │   └── ap2_mandate.py            # AP2 cryptographic mandate verification dependency
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── domain.py                 # Domain entities (Product, Order, AuditLog, OrderStatus)
│       │   └── schemas.py                # Pydantic API request & response schemas
│       │
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── audit.py                  # Audit log inspection route (/api/v1/audit/logs)
│       │   ├── discovery.py              # Semantic catalog search (/api/v1/agent/discover)
│       │   ├── negotiate.py              # Bounded negotiation endpoint (/api/v1/agent/negotiate)
│       │   └── webhooks.py               # Razorpay webhook settlement (/api/v1/webhooks/razorpay)
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── audit_service.py          # Immutable security & transactional event logger
│       │   ├── negotiation_service.py    # Policy firewall & price-floor enforcement engine
│       │   └── razorpay_service.py       # Razorpay API client wrapper & HMAC signature validator
│       │
│       └── utils/
│           ├── __init__.py
│           └── token_generator.py        # Utility to generate signed AP2 DIT mandate tokens
│
├── frontend/                             # Merchant Command Center (Vite + React + TypeScript)
│   ├── index.html                        # HTML shell with Inter & Plus Jakarta Sans typography
│   ├── package.json                      # Frontend dependencies (React 18, Tailwind, Lucide)
│   ├── tsconfig.json                     # TypeScript configuration
│   ├── tsconfig.app.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts                    # Vite build config with Tailwind & backend proxy
│   │
│   └── src/
│       ├── App.tsx                       # Main dashboard shell & split-view container
│       ├── index.css                     # Modern dark SaaS design system & tokens
│       ├── main.tsx                      # React DOM mounting entrypoint
│       ├── types.ts                      # TypeScript interfaces (Product, Order, AuditLog)
│       │
│       ├── components/
│       │   ├── AgentActivityFeed.tsx     # Left Split View: Agent queries & blocked attacks
│       │   ├── CatalogDrawer.tsx         # Modal: Merchant product catalog & floor margins
│       │   ├── Header.tsx                # Clean SaaS navigation header with live status
│       │   ├── MetricsBar.tsx            # KPI metric cards (Attacks, Revenue, Mandates, Orders)
│       │   ├── SettlementFeed.tsx        # Right Split View: Orders & Razorpay settlements
│       │   └── SimulatorWidget.tsx       # Interactive 4-step agent test console
│       │
│       ├── hooks/
│       │   └── useAuditLogs.ts           # Real-time Supabase subscription + polling fallback
│       │
│       └── lib/
│           ├── api.ts                    # Backend API client
│           └── supabaseClient.ts         # Supabase browser client with safe fallback
│
├── scripts/
│   └── demo_runner.py                    # End-to-end automated 5-minute CLI demo script
│
└── tests/                                # Automated unit and integration test suite
    ├── __init__.py
    ├── conftest.py                       # Pytest fixtures and mock tokens
    ├── test_ap2_mandate.py               # Security tests for AP2 token validation & expiry
    ├── test_audit.py                     # Tests for audit log query endpoints
    ├── test_discovery.py                 # Tests for semantic catalog search & margin shielding
    ├── test_negotiate.py                 # Tests for price floor firewall & Razorpay order creation
    └── test_webhooks.py                  # Tests for Razorpay webhook HMAC signature verification
```

---

## 🔒 Security, Firewall & AP2 Protocol Specifications

### 1. AP2 Delegated Intent Token (DIT) Structure
The AI Buyer Agent authenticates via standard HTTP Bearer token:
```json
{
  "sub": "agent_nexus_007",
  "max_budget": 10000.00,
  "currency": "INR",
  "iat": 1724500000,
  "exp": 1724507200,
  "scope": ["commerce:negotiate", "commerce:transact"]
}
```
- **Verification Rule**: Tokens are validated cryptographically against `AP2_SECRET_KEY` using HMAC-SHA256 (`HS256`).
- **Enforcement**: Expired tokens, tampered signatures, or missing authorizations return `HTTP 401/403` and generate an immutable `MANDATE_REJECTED` audit log.

### 2. Hallucination & Sub-Floor Attack Defense
- **Merchant Minimum Margin**: Each product has an internal confidential `price_floor`.
- **Deterministic Rule**:
  $$\text{If } \text{proposed\_price} < \text{price\_floor} \implies \text{HALT with HTTP 422}$$
- **Audit Logging**: Emits a `PRICE_ATTACK_BLOCKED` event capturing `agent_id`, `product_id`, `proposed_price`, `price_floor`, and `delta_below_floor`.

### 3. Deterministic Settlement with Razorpay Signature
Incoming webhooks on `/api/v1/webhooks/razorpay` require header `x-razorpay-signature`.
- **HMAC Verification**:
  $$\text{Expected Signature} = \text{HMAC-SHA256}(\text{raw\_body}, \text{RAZORPAY\_WEBHOOK\_SECRET})$$
- Order state is only updated to `PAID` once the signature strictly matches.

---

## 🗄️ Database Schema & Seed Data

Execute [database/schema.sql](file:///Users/pragunkk/Library/CloudStorage/OneDrive-iiit-b/Hackathons/razorpayBuildathon/aegis/database/schema.sql) in Supabase:

```sql
-- Enable vector extension for semantic catalog search
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Product Catalog (Confidential price_floor is shielded from agents)
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    mrp DECIMAL(10,2) NOT NULL,
    price_floor DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0,
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agentic Orders
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    razorpay_order_id TEXT UNIQUE NOT NULL,
    agent_id TEXT NOT NULL,
    product_id UUID REFERENCES products(id),
    negotiated_price DECIMAL(10,2) NOT NULL,
    currency TEXT DEFAULT 'INR',
    status TEXT DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PAID', 'FAILED', 'BLOCKED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Immutable Security & Transaction Audit Trail
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(id),
    agent_id TEXT,
    event_type TEXT NOT NULL,
    payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Pre-Seeded Catalog Items:
| Product Name | Public MRP | Confidential Price Floor | Max Allowed Discount |
|---|---|---|---|
| **Neural Interface Cyber-Deck X9** | ₹4,500.00 | **₹3,800.00** | ₹700.00 (16%) |
| **Quantum Stealth Recon Drone (V2)** | ₹12,000.00 | **₹9,500.00** | ₹2,500.00 (21%) |
| **Aegis Obsidian HSM Vault** | ₹7,500.00 | **₹6,200.00** | ₹1,300.00 (17%) |
| **Hyper-Threaded Bio-Telemetry Suite** | ₹2,800.00 | **₹2,200.00** | ₹600.00 (21%) |

---

## 📡 API Reference & Route Specifications

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/health` | Diagnostic server health check | None |
| `GET` | `/api/v1/products` | List public catalog (`price_floor` stripped) | None |
| `GET` | `/api/v1/products/{id}` | Get product details | None |
| `POST` | `/api/v1/agent/discover` | Semantic vector search for buyer intent | None |
| `POST` | `/api/v1/agent/negotiate` | Bounded price negotiation & Razorpay order creation | **Bearer AP2 Mandate JWT** |
| `POST` | `/api/v1/webhooks/razorpay` | Settle orders via HMAC-signed Razorpay webhook | **`x-razorpay-signature` Header** |
| `GET` | `/api/v1/audit/logs` | Query recent immutable audit log stream | None |

---

## 🖥️ Frontend Command Center Overview

The frontend Command Center is built with **Vite, React 18, TypeScript, and Tailwind CSS**.

### Key UI Features:
1. **Real-time KPI Metrics Bar**:
   - **Attacks Blocked**: Total sub-floor exploit proposals intercepted.
   - **Settled Revenue**: Total sum of orders transitioned to `PAID` via verified webhooks.
   - **AP2 Mandates**: Total cryptographic Delegated Intent Tokens validated.
   - **Negotiated Orders**: Total orders created with Razorpay IDs.
2. **Left Split View: Agent Traffic & Policy Firewall**:
   - Filter by **All**, **Attacks**, **Searches**, **Mandates**.
   - Displays real-time semantic discovery queries and cosine matches.
   - Highlights blocked price attacks in clean, structured red cards displaying *Attempted Price*, *Protected Floor*, and *Exploit Delta*.
3. **Right Split View: Razorpay Settlements**:
   - Filter by **All**, **Paid**, **Pending**.
   - Real-time status badges (`Paid & Settled`, `Order Created`).
   - Click-to-copy Razorpay Order IDs.
   - Verified HMAC-SHA256 signature indicator.
4. **Interactive Agent Test Console (Simulator Modal)**:
   - 1-click execution for:
     1. *Search Catalog*
     2. *Fair Offer (₹3,800)*
     3. *Lowball Attack (₹2,500)*
     4. *Settle Order*
5. **Product Margins Drawer**:
   - Merchant inspector showing confidential floor prices and allowed discount percentages.

---

## ⚙️ Installation & Setup Guide

### Prerequisites
- **Python 3.10+** (Python 3.11 / 3.12 / 3.13 supported)
- **Node.js 18+** and **npm**
- **Git**

### Step 1: Clone the Repository
```bash
git clone <repository_url> aegis
cd aegis
```

### Step 2: Set Up Backend Virtual Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS / Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
```bash
cp .env.example .env
```
*(The default configuration includes fallback mock keys so you can develop and test immediately without blocking on external cloud accounts).*

### Step 4: Set Up Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 🚀 Running the Application

### 1. Start the FastAPI Backend Gateway
In your first terminal:
```bash
source .venv/bin/activate
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Base URL: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 2. Start the Frontend Command Center
In your second terminal:
```bash
cd frontend
npm run dev
```
- Dashboard URL: **`http://localhost:5173`**

---

## 🧪 Testing & Verification Guide

### 1. Automated Unit & Integration Tests (pytest)
Run the full 15-test automated test suite:
```bash
source .venv/bin/activate
pytest -v
```

#### Expected Output:
```text
tests/test_ap2_mandate.py::test_mandate_authorized_access PASSED         [  6%]
tests/test_ap2_mandate.py::test_mandate_missing_token PASSED             [ 13%]
tests/test_ap2_mandate.py::test_mandate_invalid_signature PASSED         [ 20%]
tests/test_ap2_mandate.py::test_mandate_expired_token PASSED             [ 26%]
tests/test_audit.py::test_get_audit_logs PASSED                          [ 33%]
tests/test_discovery.py::test_list_products_excludes_price_floor PASSED  [ 40%]
tests/test_discovery.py::test_discover_products_semantic_search PASSED   [ 46%]
tests/test_discovery.py::test_get_product_by_id PASSED                   [ 53%]
tests/test_negotiate.py::test_negotiation_success_at_price_floor PASSED  [ 60%]
tests/test_negotiate.py::test_negotiation_sub_floor_attack_blocked PASSED [ 66%]
tests/test_negotiate.py::test_negotiation_budget_guardrail_exceeded PASSED [ 73%]
tests/test_negotiate.py::test_negotiation_non_existent_product PASSED    [ 80%]
tests/test_webhooks.py::test_webhook_order_paid_success PASSED           [ 86%]
tests/test_webhooks.py::test_webhook_invalid_signature_rejected PASSED   [ 93%]
tests/test_webhooks.py::test_webhook_missing_signature_rejected PASSED   [100%]

============================== 15 passed in 0.03s ==============================
```

---

### 2. Automated 5-Minute Demo Script (CLI)

Ensure the backend server is running on `http://127.0.0.1:8000`, then execute the demo runner:

```bash
# Option A: Automated continuous run
source .venv/bin/activate
python3 scripts/demo_runner.py

# Option B: Interactive step-by-step mode (press Enter between steps)
python3 scripts/demo_runner.py --interactive
```

#### What the Demo Runner executes:
1. **[STEP 1] Generate AP2 Mandate Token**: Creates a signed cryptographic DIT JWT for `agent_nexus_007` with `max_budget=₹10,000`.
2. **[STEP 2] Semantic Catalog Discovery**: Queries `/api/v1/agent/discover` with `"neural transceiver cyber deck with low-latency telemetry"`. Resolves product ID while keeping `price_floor` protected.
3. **[STEP 3] Bounded Negotiation**: Proposes ₹3,800 (at floor price). Gateway approves and generates Razorpay Order ID.
4. **[STEP 4] Sub-Floor Attack Injection**: Attempts exploit with ₹2,500 (< ₹3,800). Gateway intercepts and blocks with **HTTP 422**.
5. **[STEP 5] Webhook Settlement**: Dispatches HMAC-SHA256 signed `order.paid` event. Gateway verifies signature and marks order **`PAID`**.
6. **[STEP 6] Audit Trail**: Queries `/api/v1/audit/logs` and confirms all events are logged.

---

### 3. Manual Browser Testing via Command Center

1. Open **`http://localhost:5173`** in your browser.
2. Click the **"Test Agent"** button in the top right.
3. Execute the 4 test cases sequentially:
   - **Click `1. Search Catalog`**:
     - *Result*: Left feed updates with a cyan `Semantic Product Search` card matching 1 catalog item.
   - **Click `2. Fair Offer (₹3,800)`**:
     - *Result*: Left feed records `AP2 Token Authorized`. Right feed creates an indigo `Order Created // Pending` card showing `₹3,800.00` and the Razorpay Order ID. Top metric *Orders Created* increments.
   - **Click `3. Lowball Attack (₹2,500)`**:
     - *Result*: Left feed displays a red `Sub-Floor Price Attack Blocked` card showing *Attempted: ₹2,500* vs *Floor: ₹3,800* and *Exploit Delta: -₹1,300*. Top metric *Attacks Blocked* increments.
   - **Click `4. Settle Order`**:
     - *Result*: Right feed updates with an emerald `Paid & Settled` card with `HMAC-SHA256 signature verified`. Top metric *Settled Revenue* increments.
4. Click **"Product Margins"** in the top navigation to inspect the merchant catalog, confidential floor prices, and margin guardrails.

---

## 🔐 Environment Variables Reference

| Variable | Description | Default / Example Value |
|---|---|---|
| `HOST` | Backend host binding | `0.0.0.0` |
| `PORT` | Backend port binding | `8000` |
| `ENVIRONMENT` | Environment stage (`development` / `production`) | `development` |
| `LOG_LEVEL` | Application logging level | `INFO` |
| `SUPABASE_URL` | Supabase Project URL for pgvector & tables | `https://your-project.supabase.co` |
| `SUPABASE_KEY` | Supabase Anon / Service Role API Key | `your-supabase-key` |
| `AP2_SECRET_KEY` | Secret key used to sign & verify AP2 DIT JWT tokens | `aegis_ap2_super_secret_mandate_signing_key_2026` |
| `AP2_ALGORITHM` | JWT signing algorithm | `HS256` |
| `RAZORPAY_KEY_ID` | Razorpay Merchant Key ID | `rzp_test_YourKeyId` |
| `RAZORPAY_KEY_SECRET` | Razorpay Merchant Key Secret | `YourRazorpaySecret` |
| `RAZORPAY_WEBHOOK_SECRET`| Razorpay Webhook Secret for HMAC verification | `rzp_webhook_secret_2026` |
| `OPENAI_API_KEY` | OpenAI API Key for embeddings (optional) | `sk-...` |

---

## 🚧 Current Hard-Coded Elements & Production Roadmap

This section documents all components that currently utilize hard-coded or mock values for standalone local demonstration, along with the concrete engineering tasks required for full enterprise production deployment.

### 1. Current Hard-Coded / In-Memory Mock Fallbacks

| Area | File Location | Current Implementation / Mock Fallback | Why It Was Hard-Coded | Production Replacement |
|---|---|---|---|---|
| **Product Catalog & Floor Margins** | `backend/app/database.py`<br>`frontend/src/components/CatalogDrawer.tsx` | Pre-defined in `DEFAULT_PRODUCTS` and `MERCHANT_FLOOR_DATA` dictionary mapping. | Allows immediate standalone demo and testing when Supabase cloud credentials are not supplied. | Persist catalog & confidential floor prices directly in Supabase PostgreSQL tables with encrypted columns and Row-Level Security (RLS). |
| **Razorpay Order Generation** | `backend/app/services/razorpay_service.py` | Generates deterministic UUID order IDs (`order_<hex>`) when keys start with `rzp_test_default_mock`. | Prevents blocking on external Razorpay Merchant account approval and API key generation during local builds. | Connect directly to live Razorpay Orders API (`client.order.create(...)`) with live sandbox credentials. |
| **AP2 Mandate Cryptography** | `backend/app/config.py`<br>`backend/app/middleware/ap2_mandate.py` | Uses symmetric `HS256` signing key (`AP2_SECRET_KEY`) shared between gateway and agent. | Simplifies initial prototype authorization without needing an external public key infrastructure (PKI) registry. | Implement asymmetric cryptography (`Ed25519` / `ES256`) with a public JWKS endpoint (`/.well-known/jwks.json`) and Decentralized Identifier (DID) resolution. |
| **Simulator Test Agent & Target** | `frontend/src/components/SimulatorWidget.tsx` | Fixed agent subject `agent_simulator_007`, budget ₹10,000, and target product UUID `a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d`. | Provides deterministic 1-click test buttons for video demos and hackathon judging. | Add a dynamic agent configuration form allowing users to select any discovered product, customize buyer agent personas, and set custom budgets. |
| **Single-Turn Bounded Negotiation** | `backend/app/services/negotiation_service.py` | Evaluates price offers deterministically against `price_floor` in a single request-response cycle. | Ensures 100% deterministic margin protection and prevents LLM discount hallucinations. | Integrate a multi-turn LLM reasoning agent with dynamic volume bargaining, time-decay pricing, and buyer credit scoring. |

---

### 2. Pending Implementations & Production Roadmap

#### A. Multi-Turn Autonomous LLM Bargaining Engine
- [ ] **Dynamic Counter-Offer Generation**: Implement an LLM reasoning loop (powered by Gemini 1.5 / OpenAI GPT-4o) bounded by merchant policy guardrails.
- [ ] **Contextual Discount Factors**: Factor in order quantity, stock velocity, customer lifetime value, and historical negotiation patterns when formulating counter-offers between MRP and the confidential floor price.

#### B. Decentralized AP2 Mandate Verification (Asymmetric PKI)
- [ ] **Decentralized Identifiers (DIDs)**: Support agent identities registered on decentralized identity registries.
- [ ] **Asymmetric JWKS Verification**: Replace shared secret HS256 with asymmetric key pairs (ES256 / Ed25519) where the gateway fetches the buyer's public key from `https://agent-domain.com/.well-known/jwks.json`.
- [ ] **Fine-Grained Capability Delegation**: Support delegated sub-tokens with specific category restrictions (e.g. `allowed_categories: ["electronics"]`, `max_per_item: 5000`).

#### C. Live Supabase pgvector Pipeline
- [ ] **Automated Embedding Pipeline**: Integrate LangChain / OpenAI `text-embedding-3-small` in the backend product creation route to automatically generate 1536-dimensional vector embeddings on catalog updates.
- [ ] **Hybrid Search**: Combine pgvector cosine distance search with PostgreSQL full-text search (`tsvector`) for hybrid precision ranking.

#### D. Production Webhook Delivery & Payment Gateway
- [ ] **Live Webhook Gateway**: Expose public HTTPS endpoints via Cloudflare Tunnels / AWS API Gateway to ingest real-time callbacks directly from the live Razorpay Dashboard.
- [ ] **Razorpay Standard / Custom Checkout**: Support automated Razorpay Payment Link generation and UPI mandate auto-debit for agent transactions.

#### E. Merchant Multi-Tenancy & Management UI
- [ ] **Merchant Authentication & RLS**: Protect the Command Center behind Supabase Auth (OAuth / Email) with PostgreSQL Row-Level Security isolating merchant accounts.
- [ ] **Dynamic Margin Management UI**: Build a merchant console interface to add/edit products, adjust confidential price floors in real time, and toggle automated sales campaigns.
- [ ] **Anti-Probing & Sybil Defense**: Implement token-bucket rate limiting per `agent_id` to prevent malicious agents from probe-testing and guessing merchant price floor thresholds.

---

## 🏆 Summary

AegisPay Gateway bridges autonomous agent reasoning with deterministic financial security:
- **AP2 Cryptographic Mandates** protect the buyer from rogue spending.
- **Price-Floor Policy Firewalls** protect the merchant from LLM hallucination and sub-floor exploits.
- **Razorpay Cryptographic Settlement** ensures deterministic payment confirmation.
- **Merchant Command Center** delivers real-time observability over all agent transactions.

