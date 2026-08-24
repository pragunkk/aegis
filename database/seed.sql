-- ==========================================================
-- AegisPay Gateway: Seed Products Catalog
-- ==========================================================

INSERT INTO products (id, name, description, mrp, price_floor, stock) VALUES
(
    'a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d',
    'Neural Interface Cyber-Deck X9',
    'High-bandwidth direct neural transceiver for autonomous agents and cyborg operators with encrypted sub-millisecond telemetry.',
    4500.00,
    3800.00,
    25
),
(
    'b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e',
    'Quantum Stealth Recon Drone (V2)',
    'Autonomous surveillance unit with low-observable metamaterial skin, LIDAR mesh routing, and edge AI compute.',
    12000.00,
    9500.00,
    10
),
(
    'c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f',
    'Aegis Obsidian Hardware Security Module',
    'FIPS 140-3 Level 4 tamper-resistant cryptographic vault for autonomous payment key authorization and AP2 mandate validation.',
    7500.00,
    6200.00,
    15
),
(
    'd4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f9a',
    'Hyper-Threaded Bio-Telemetry Sensor Suite',
    'Non-invasive dermal sensor array with real-time biometric telemetry and secure Bluetooth Low Energy 5.4 uplink.',
    2800.00,
    2200.00,
    50
)
ON CONFLICT (id) DO NOTHING;
