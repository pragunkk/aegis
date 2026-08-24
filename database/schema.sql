-- ==========================================================
-- AegisPay Gateway: Database Schema for Supabase (pgvector)
-- ==========================================================

-- Enable the pgvector extension for semantic catalog search
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- Product Catalog
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    mrp DECIMAL(10,2) NOT NULL,
    price_floor DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0,
    embedding vector(1536), -- OpenAI text-embedding-3-small
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agentic Orders (Razorpay linked)
CREATE TABLE IF NOT EXISTS orders (
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

-- Immutable Audit Log
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(id),
    agent_id TEXT,
    event_type TEXT NOT NULL,
    payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_products_embedding ON products USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_orders_razorpay_order_id ON orders(razorpay_order_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at DESC);
