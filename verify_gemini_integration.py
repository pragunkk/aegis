import os
import sys
import json
from dotenv import load_dotenv
from supabase import create_client, Client
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# 1. Load Environment Config
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

if not all([supabase_url, supabase_key, gemini_key]):
    print("❌ ERROR: Missing Supabase or Gemini API keys in .env")
    sys.exit(1)

supabase: Client = create_client(supabase_url, supabase_key)
client = genai.Client()  # Automatically picks up GEMINI_API_KEY

print("✅ Configuration loaded successfully.")

# 2. Test Gemini Embeddings (text-embedding-004)
print("\n🧠 Generating Gemini Embedding for new catalog item...")
product_name = "Agentic Procurement Drone v4"
product_desc = "Fully autonomous aerial drone for enterprise logistics and supply chain delivery."

try:
    embed_response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=f"{product_name} - {product_desc}",
        config=types.EmbedContentConfig(output_dimensionality=768)
    )
    embedding_vector = embed_response.embeddings[0].values
    print(f"✅ Generated vector with exactly {len(embedding_vector)} dimensions.")
    assert len(embedding_vector) == 768, "Dimensionality mismatch!"
except Exception as e:
    print(f"❌ Gemini Embedding Failed: {e}")
    sys.exit(1)

# 3. Test Database Insertion
print("\n📦 Inserting product into Supabase...")
insert_resp = supabase.table("products").insert({
    "name": product_name,
    "description": product_desc,
    "mrp": 15000.00,
    "price_floor": 12000.00,
    "embedding": embedding_vector
}).execute()
product_id = insert_resp.data[0]["id"]
print(f"✅ Product inserted with ID: {product_id}")

# 4. Test pgvector Semantic Search
print("\n🔎 Testing Semantic Vector Search...")
search_query = "I need an automated flying delivery robot for my warehouse"
search_embed = client.models.embed_content(
    model="gemini-embedding-001", 
    contents=search_query,
    config=types.EmbedContentConfig(output_dimensionality=768)
).embeddings[0].values

search_resp = supabase.rpc("match_products", {
    "query_embedding": search_embed,
    "query_text": search_query,
    "match_threshold": 0.5,
    "match_count": 1
}).execute()

if len(search_resp.data) > 0:
    matched_product = search_resp.data[0]
    print(f"✅ Match Found! {matched_product['name']} (Similarity: {matched_product['similarity']:.3f})")
else:
    print("❌ Vector search returned no results.")
    sys.exit(1)

# 5. Test Gemini 2.5 Flash Bounded Negotiation
print("\n💬 Testing Gemini 2.5 Flash Negotiation Engine...")
class CounterOfferResponse(BaseModel):
    counter_offer: float = Field(description="The numeric price for the counter-offer.")
    reasoning: str = Field(description="Business reasoning behind the counter-offer.")

system_prompt = f"""You are the AegisPay Merchant Gateway.
Product: {matched_product['name']} 
MRP: ₹{matched_product['mrp']} 
Hard Minimum Floor: ₹12000

The buyer offered ₹12500. Compute a strict counter-offer between ₹13000 and ₹15000.
Never offer anything below ₹12000."""

try:
    chat_response = client.models.generate_content(
        model='gemini-3.6-flash', 
        contents=system_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CounterOfferResponse,
            temperature=0.3
        )
    )
    parsed_offer = json.loads(chat_response.text)
    print(f"✅ Gemini Negotiation Success!")
    print(f"🤖 Counter Offer: ₹{parsed_offer['counter_offer']}")
    print(f"📜 Reasoning: {parsed_offer['reasoning']}")
except Exception as e:
    print(f"❌ Gemini Negotiation Failed: {e}")
    sys.exit(1)

print("\n🎉 ALL AI INTEGRATION CHECKS PASSED PERFECTLY!")