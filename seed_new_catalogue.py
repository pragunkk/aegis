import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
from google import genai
from google.genai import types

# 1. Load Environment Variables
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

if not all([supabase_url, supabase_key, gemini_key]):
    print("❌ ERROR: Missing Supabase or Gemini API keys in .env")
    sys.exit(1)

# Initialize Clients
supabase: Client = create_client(supabase_url, supabase_key)
client = genai.Client() # Automatically picks up GEMINI_API_KEY

# 2. Define the Realistic Enterprise Catalog
realistic_products = [
    {
        "name": "Enterprise AI Accelerator GPU Node",
        "description": "High-performance compute node for training large language models. Features 8x H100 GPUs and 2TB RAM.",
        "category": "hardware",
        "mrp": 1250000.00,
        "price_floor": 1050000.00,
        "stock": 5
    },
    {
        "name": "Commercial Grade Espresso Machine",
        "description": "Dual-boiler espresso machine for high-volume corporate kitchens. Plumbed-in water line compatible.",
        "category": "office_equipment",
        "mrp": 250000.00,
        "price_floor": 210000.00,
        "stock": 12
    },
    {
        "name": "Ergonomic Mesh Task Chair",
        "description": "Premium office chair with dynamic lumbar support, 4D armrests, and breathable mesh back.",
        "category": "office_furniture",
        "mrp": 45000.00,
        "price_floor": 32000.00,
        "stock": 50
    },
    {
        "name": "UHD 4K Professional Color-Grading Monitor",
        "description": "32-inch 4K IPS display with 99% DCI-P3 color gamut, factory calibrated for design and media teams.",
        "category": "electronics",
        "mrp": 85000.00,
        "price_floor": 72000.00,
        "stock": 25
    },
    {
        "name": "10GbE Managed Network Switch",
        "description": "48-port 10 Gigabit Ethernet managed switch with Layer 3 routing capabilities for enterprise datacenters.",
        "category": "networking",
        "mrp": 115000.00,
        "price_floor": 95000.00,
        "stock": 15
    },
    {
        "name": "Developer Mechanical Keyboard (Tactile)",
        "description": "Hot-swappable 75% mechanical keyboard with sound-dampening foam and tactile brown switches.",
        "category": "electronics",
        "mrp": 12500.00,
        "price_floor": 9000.00,
        "stock": 100
    },
    {
        "name": "Dual-Motor Sit-Stand Desk",
        "description": "Electric height-adjustable desk with memory presets and a solid bamboo desktop. 120kg lift capacity.",
        "category": "office_furniture",
        "mrp": 55000.00,
        "price_floor": 44000.00,
        "stock": 30
    },
    {
        "name": "Enterprise Zero-Trust Firewall Appliance",
        "description": "Next-generation hardware firewall featuring deep packet inspection, VPN, and zero-trust network access.",
        "category": "networking",
        "mrp": 185000.00,
        "price_floor": 150000.00,
        "stock": 8
    },
    {
        "name": "Professional Video Conferencing Kit",
        "description": "Includes a 4K PTZ camera, ceiling-mounted beamforming microphones, and a smart control hub for meeting rooms.",
        "category": "electronics",
        "mrp": 220000.00,
        "price_floor": 185000.00,
        "stock": 20
    },
    {
        "name": "Secure Hardware Security Module (HSM)",
        "description": "FIPS 140-2 Level 3 certified cryptographic module for generating and protecting sensitive payment keys.",
        "category": "hardware",
        "mrp": 310000.00,
        "price_floor": 275000.00,
        "stock": 5
    }
]

print("🧹 Clearing old fictional catalog from Supabase...")
# Note: This will delete existing products. Make sure you don't have active orders tied to them.
try:
    supabase.table("products").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    print("✅ Old catalog cleared.")
except Exception as e:
    print(f"⚠️ Warning during deletion (might already be empty or have foreign key constraints): {e}")

print("\n🚀 Beginning Realistic Catalog Seed...")

# 3. Generate Embeddings and Insert
for product in realistic_products:
    print(f"Embedding: {product['name']}...")
    
    # Generate 768-dimension embedding via Gemini
    embed_response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=f"{product['name']} - {product['description']}",
        config=types.EmbedContentConfig(output_dimensionality=768)
    )
    
    product["embedding"] = embed_response.embeddings[0].values
    
    # Insert into Supabase
    supabase.table("products").insert(product).execute()
    print(f"  ✅ Inserted into database.")

print("\n🎉 Realistic Enterprise Catalog successfully seeded!")