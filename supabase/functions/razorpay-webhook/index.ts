import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createHmac } from "node:crypto";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const supabase = createClient(supabaseUrl, supabaseServiceKey);

serve(async (req) => {
  if (req.method !== "POST") return new Response("Method not allowed", { status: 405 });

  try {
    // Read the raw text body to preserve the exact payload for HMAC hashing
    const rawBody = await req.text();
    const razorpaySignature = req.headers.get("x-razorpay-signature");

    if (!razorpaySignature) return new Response("Missing signature", { status: 400 });

    const secret = Deno.env.get("RAZORPAY_WEBHOOK_SECRET");
    if (!secret) throw new Error("Missing Webhook Secret");

    // Compute HMAC-SHA256 signature using the secret
    const expectedSignature = createHmac("sha256", secret).update(rawBody).digest("hex");

    if (expectedSignature !== razorpaySignature) {
      return new Response("Invalid signature", { status: 400 });
    }

    const eventData = JSON.parse(rawBody);

    if (eventData.event === "order.paid") {
      const rzpOrderId = eventData.payload.payment.entity.order_id;
      const amountPaid = eventData.payload.payment.entity.amount / 100;

      await supabase.from("orders").update({ status: "PAID" }).eq("razorpay_order_id", rzpOrderId);
      await supabase.from("audit_logs").insert({
        event_type: "SETTLEMENT_CONFIRMED",
        payload: { razorpay_order_id: rzpOrderId, amount_paid: amountPaid, edge_verified: true }
      });
    }

    return new Response(JSON.stringify({ status: "success" }), { status: 200 });
    
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500 });
  }
});