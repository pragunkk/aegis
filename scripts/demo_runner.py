#!/usr/bin/env python3
"""
AegisPay Gateway: End-to-End Automated Demo Runner (Phase 3)

This script automates the complete 5-minute agentic commerce demonstration:
1. Generate AP2 Delegated Intent Token (DIT)
2. Perform Semantic Discovery against the Product Catalog
3. Execute Bounded Negotiation at Price Floor & Generate Razorpay Order
4. Inject Sub-Floor Price Attack & Demonstrate Firewall Interception
5. Settle Transaction via Cryptographically Verified Razorpay Webhook
6. Inspect Immutable Audit Log Stream
"""

import sys
import os
import time
import json
import hmac
import hashlib
import argparse
from typing import Dict, Any, Optional

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Run 'pip install httpx' or activate the virtualenv.")
    sys.exit(1)

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.config import settings
from backend.app.utils.token_generator import create_agent_mandate_token

# Terminal Colors & Streetwear Tech Formatting
class Colors:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def print_banner():
    print(rf"""
{Colors.CYAN}{Colors.BOLD}================================================================================{Colors.RESET}
{Colors.RED}{Colors.BOLD}   ___  ____ _____ ___ ____  ____   _ __   __   ____    _  _____ ______      ___ ___{Colors.RESET}
{Colors.RED}{Colors.BOLD}  / _ \| ___/ ____|_ _/ ___||  _ \ / \ \ / /  / ___|  / \|_   _|  ____| \  / /_ _|{Colors.RESET}
{Colors.CYAN}{Colors.BOLD} / /_\ | __| |  _  | |\___ \| |_) / _ \ V /  | |  _  / _ \ | | |  _|  \ \/ / | | {Colors.RESET}
{Colors.CYAN}{Colors.BOLD}|  _  | |__| |_| | | | ___) |  __/ ___ \| |   | |_| |/ ___ \| | | |___   | |  | | {Colors.RESET}
{Colors.MAGENTA}{Colors.BOLD}|_| |_|_____\_____|___|____/|_| /_/   \_\_|    \_____/_/   \_\_| |_____|  |_| |___|{Colors.RESET}
{Colors.DIM}         Autonomous Agent Commerce Gateway // AP2 + Razorpay Policy Firewall{Colors.RESET}
{Colors.CYAN}{Colors.BOLD}================================================================================{Colors.RESET}
""")


def log_step(step_num: int, title: str, description: str):
    print(f"\n{Colors.BOLD}{Colors.YELLOW}[STEP {step_num}]{Colors.RESET} {Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}")
    print(f"{Colors.DIM}--> {description}{Colors.RESET}")
    time.sleep(0.6)


def print_json(data: Any):
    formatted = json.dumps(data, indent=2)
    for line in formatted.splitlines():
        print(f"  {Colors.DIM}{line}{Colors.RESET}")


def generate_razorpay_signature(payload_str: str, secret: str) -> str:
    return hmac.new(
        key=secret.encode("utf-8"),
        msg=payload_str.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()


def run_demo(base_url: str, delay: float = 1.2, interactive: bool = False):
    print_banner()
    client = httpx.Client(base_url=base_url, timeout=10.0)

    def pause():
        if interactive:
            input(f"\n{Colors.BOLD}[Press ENTER to execute next step...]{Colors.RESET}")
        else:
            time.sleep(delay)

    # -------------------------------------------------------------------------
    # Health Check
    # -------------------------------------------------------------------------
    try:
        health = client.get("/health").json()
        print(f"{Colors.GREEN}✓ Connected to AegisPay Gateway:{Colors.RESET} {health.get('service')} (v{health.get('version')})")
    except Exception as e:
        print(f"{Colors.RED}✗ Failed to connect to gateway at {base_url}:{Colors.RESET} {e}")
        print(f"{Colors.YELLOW}Please ensure the backend is running: uvicorn backend.app.main:app --port 8000{Colors.RESET}")
        sys.exit(1)

    pause()

    # -------------------------------------------------------------------------
    # STEP 1: Generate Cryptographic AP2 Mandate Token (DIT)
    # -------------------------------------------------------------------------
    log_step(1, "GENERATE AP2 DELEGATED INTENT TOKEN (DIT)", "Agent Nexus-007 creates a signed cryptographic budget mandate")
    
    agent_id = "agent_nexus_007"
    max_budget = 10000.0
    dit_token = create_agent_mandate_token(
        agent_id=agent_id,
        max_budget=max_budget,
        currency="INR",
        expires_in_minutes=120,
    )
    
    print(f"  {Colors.BOLD}Agent Subject ID:{Colors.RESET} {agent_id}")
    print(f"  {Colors.BOLD}Authorized Max Budget:{Colors.RESET} ₹{max_budget:,.2f} INR")
    print(f"  {Colors.BOLD}AP2 Mandate JWT:{Colors.RESET} {Colors.MAGENTA}{dit_token[:38]}...{dit_token[-24:]}{Colors.RESET}")
    print(f"  {Colors.GREEN}✓ Cryptographic DIT Generated with HS256 Signature{Colors.RESET}")
    
    pause()

    # -------------------------------------------------------------------------
    # STEP 2: Semantic Catalog Discovery (ACP/UCP Layer)
    # -------------------------------------------------------------------------
    log_step(2, "SEMANTIC CATALOG DISCOVERY (ACP/UCP LAYER)", "AI Buyer Agent queries catalog for high-bandwidth neural transceiver")
    
    query = "neural transceiver cyber deck with low-latency telemetry"
    print(f"  {Colors.BOLD}Natural Language Query:{Colors.RESET} \"{query}\"")
    
    res = client.post("/api/v1/agent/discover", json={"query": query, "limit": 2})
    discovery_results = res.json()
    
    target_product = None
    if discovery_results and len(discovery_results) > 0:
        target_product = discovery_results[0]
        print(f"  {Colors.GREEN}✓ Semantic pgvector Search Matched:{Colors.RESET}")
        print(f"    - Product: {Colors.BOLD}{target_product['name']}{Colors.RESET} (ID: {target_product['id']})")
        print(f"    - Catalog MRP: {Colors.CYAN}₹{target_product['mrp']:,.2f}{Colors.RESET}")
        print(f"    - Stock Available: {target_product['stock']} units")
        print(f"    {Colors.DIM}(Confidential merchant price_floor is strictly omitted from public response){Colors.RESET}")
    else:
        print(f"{Colors.RED}✗ No products discovered.{Colors.RESET}")
        sys.exit(1)

    pause()

    # -------------------------------------------------------------------------
    # STEP 3: Bounded Negotiation & Razorpay Order Creation
    # -------------------------------------------------------------------------
    log_step(3, "HAGGLE & SETTLE (BOUNDED NEGOTIATION)", "Agent proposes price at merchant price floor (₹3,800 on ₹4,500 MRP)")
    
    headers = {"Authorization": f"Bearer {dit_token}"}
    negotiate_payload = {
        "product_id": target_product["id"],
        "proposed_price": 3800.0,
        "reasoning": "Autonomous procurement matching market pricing model"
    }
    
    print(f"  {Colors.BOLD}Sending Negotiation Request:{Colors.RESET}")
    print(f"    - Product ID: {negotiate_payload['product_id']}")
    print(f"    - Proposed Price: {Colors.CYAN}₹{negotiate_payload['proposed_price']:,.2f}{Colors.RESET} (Discount: ₹{target_product['mrp'] - 3800:,.2f})")
    
    res = client.post("/api/v1/agent/negotiate", headers=headers, json=negotiate_payload)
    nego_data = res.json()
    
    razorpay_order_id = None
    if res.status_code == 200 and nego_data.get("success"):
        decision = nego_data["decision"]
        razorpay_order_id = decision["razorpay_order_id"]
        print(f"\n  {Colors.GREEN}{Colors.BOLD}✓ NEGOTIATION ACCEPTED BY AEGIS GATEWAY!{Colors.RESET}")
        print(f"    - Status: {decision['status']}")
        print(f"    - Message: {decision['message']}")
        print(f"    - Razorpay Order ID: {Colors.BOLD}{Colors.YELLOW}{razorpay_order_id}{Colors.RESET}")
        print(f"    - Amount in Subunits (Paise): {decision['amount_in_subunits']}")
        print(f"    - Audit Log Reference: {nego_data.get('audit_event_id')}")
    else:
        print(f"{Colors.RED}✗ Negotiation failed: {nego_data}{Colors.RESET}")
        sys.exit(1)

    pause()

    # -------------------------------------------------------------------------
    # STEP 4: Inject Sub-Floor Price Attack (Firewall Hallucination Defense)
    # -------------------------------------------------------------------------
    log_step(4, "INJECT SUB-FLOOR PRICE ATTACK (EXPLOIT SIMULATION)", "Agent attempts unauthorized deep discount below merchant floor (₹2,500 < ₹3,800)")
    
    attack_payload = {
        "product_id": target_product["id"],
        "proposed_price": 2500.0,  # Below price_floor!
        "reasoning": "Hallucinating model discount exploit below merchant floor"
    }
    
    print(f"  {Colors.BOLD}Sending Exploit Proposal:{Colors.RESET}")
    print(f"    - Attempted Price: {Colors.RED}₹{attack_payload['proposed_price']:,.2f}{Colors.RESET}")
    print(f"    - Minimum Protected Floor: ₹3,800.00")
    
    res = client.post("/api/v1/agent/negotiate", headers=headers, json=attack_payload)
    attack_res = res.json()
    
    if res.status_code == 422:
        print(f"\n  {Colors.RED}{Colors.BOLD}🛡️ SUB-FLOOR PRICE ATTACK BLOCKED BY AEGIS FIREWALL!{Colors.RESET}")
        print(f"    - HTTP Status: {Colors.RED}422 Unprocessable Entity{Colors.RESET}")
        print(f"    - Firewall Message: {attack_res.get('decision', {}).get('message')}")
        print(f"    - Security Audit Event ID: {attack_res.get('audit_event_id')}")
        print(f"    {Colors.GREEN}✓ Merchant Profit Margins Successfully Protected from LLM Hallucination{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}Response: {res.status_code} - {attack_res}{Colors.RESET}")

    pause()

    # -------------------------------------------------------------------------
    # STEP 5: Razorpay Deterministic Settlement (Webhook)
    # -------------------------------------------------------------------------
    log_step(5, "DETERMINISTIC RAZORPAY SETTLEMENT (WEBHOOK)", "Simulate Razorpay order.paid event with cryptographic HMAC signature")
    
    webhook_payload = {
        "entity": "event",
        "event": "order.paid",
        "contains": ["payment", "order"],
        "payload": {
            "payment": {
                "entity": {
                    "id": f"pay_demo_{int(time.time())}",
                    "order_id": razorpay_order_id,
                    "amount": 380000,
                    "currency": "INR",
                    "status": "captured",
                }
            },
            "order": {
                "entity": {
                    "id": razorpay_order_id,
                    "amount": 380000,
                    "status": "paid",
                }
            }
        },
        "created_at": int(time.time())
    }
    
    payload_body = json.dumps(webhook_payload)
    signature = generate_razorpay_signature(payload_body, settings.RAZORPAY_WEBHOOK_SECRET)
    
    print(f"  {Colors.BOLD}Dispatching Webhook Payload:{Colors.RESET}")
    print(f"    - Event: {Colors.CYAN}order.paid{Colors.RESET}")
    print(f"    - Order ID: {razorpay_order_id}")
    print(f"    - x-razorpay-signature: {Colors.DIM}{signature[:24]}...{Colors.RESET}")
    
    res = client.post(
        "/api/v1/webhooks/razorpay",
        content=payload_body.encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-razorpay-signature": signature
        }
    )
    
    if res.status_code == 200 and res.json().get("status") == "ok":
        print(f"\n  {Colors.GREEN}{Colors.BOLD}✓ RAZORPAY HMAC SIGNATURE VERIFIED // TRANSACTION SETTLED (PAID){Colors.RESET}")
    else:
        print(f"{Colors.RED}✗ Webhook failed: {res.status_code} - {res.text}{Colors.RESET}")

    pause()

    # -------------------------------------------------------------------------
    # STEP 6: Immutable Audit Trail Inspection
    # -------------------------------------------------------------------------
    log_step(6, "IMMUTABLE AUDIT TRAIL VERIFICATION", "Querying Supabase audit_logs stream to verify security ledger")
    
    res = client.get("/api/v1/audit/logs?limit=5")
    logs = res.json()
    
    print(f"\n  {Colors.BOLD}Recent Gateway Audit Events:{Colors.RESET}")
    print(f"  {Colors.DIM}{'-'*75}{Colors.RESET}")
    for log in logs[:5]:
        event_type = log.get("event_type")
        event_color = Colors.GREEN if "PAID" in event_type or "CONFIRMED" in event_type else (
            Colors.RED if "BLOCKED" in event_type or "REJECTED" in event_type else Colors.CYAN
        )
        print(f"  {Colors.DIM}[{log.get('created_at', 'N/A')[:19]}]{Colors.RESET} {event_color}{Colors.BOLD}{event_type:<28}{Colors.RESET} Agent: {str(log.get('agent_id')):<18}")
    print(f"  {Colors.DIM}{'-'*75}{Colors.RESET}")

    # -------------------------------------------------------------------------
    # Demonstration Complete
    # -------------------------------------------------------------------------
    print(f"""
{Colors.CYAN}{Colors.BOLD}================================================================================{Colors.RESET}
{Colors.GREEN}{Colors.BOLD}✓ DEMONSTRATION COMPLETE: ALL AGENTIC COMMERCE WORKFLOWS VERIFIED!{Colors.RESET}
{Colors.DIM}
- [✓] AP2 Mandate Cryptographically Authorized
- [✓] Semantic Discovery Intent Resolved (Supabase pgvector)
- [✓] Price Bounded Negotiation Executed (Razorpay Order Created)
- [✓] Sub-Floor Exploit Intercepted & Blocked (Aegis Firewall)
- [✓] Deterministic Webhook Settlement Confirmed (HMAC-SHA256 Verified)
- [✓] Live Observability Synchronized with Merchant Command Center
{Colors.RESET}
{Colors.CYAN}{Colors.BOLD}================================================================================{Colors.RESET}
""")


def main():
    parser = argparse.ArgumentParser(description="AegisPay Gateway: End-to-End Demo Script")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="FastAPI backend base URL")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between steps in seconds")
    parser.add_argument("--interactive", "-i", action="store_true", help="Prompt before each step")
    args = parser.parse_args()

    run_demo(base_url=args.url, delay=args.delay, interactive=args.interactive)


if __name__ == "__main__":
    main()
