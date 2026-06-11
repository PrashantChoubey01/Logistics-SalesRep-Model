# SeaRates AI — Demo Guide & Recording Script

> Multi-agent email automation for logistics sales (SeaRates by DP World).
> Use this as the narration script while recording the product demo.

---

## 0. One-line pitch (say this first)

> "SeaRates AI is an autonomous sales assistant that reads incoming logistics
> emails, understands what the customer needs, asks for anything missing, sources
> a rate from the right freight forwarder, and hands a ready-to-quote package to
> our sales team — all without a human touching the inbox."

**The problem it solves:** Sales reps spend hours reading emails, chasing missing
shipment details, picking a forwarder, and re-typing everything into a quote.
This does the repetitive 80% and lets the rep focus on the markup and the
relationship.

---

## 1. Before you hit record (setup checklist)

1. Start the servers: `./start_servers.sh`
2. Open the UI: **http://localhost:5002**
3. **Hard-refresh** the page (Cmd+Shift+R) so you get the latest UI.
4. Click **🔄 Reset Thread** so you start a clean conversation.
5. Open the **🤖 Agent Activity** panel (top-right) — you'll show this live.
6. Keep the **Email Templates** dropdown handy; it pre-fills each step so you
   don't type on camera.

> Tip: the whole flow is **one thread** — do NOT reset between steps, or the
> assistant loses the conversation memory.

---

## 2. The demo flow — 4 acts (this is the story)

The narrative is a real shipment: **Maria Garcia (Acme Imports)** wants to move
**2 × 40HC containers of wooden furniture from Shanghai to Rotterdam.**

### ACT 1 — Customer sends an incomplete request
- **Do:** Email From = *Customer*; load template **"Complete FCL"** or type a
  short request ("quote for a 40HC, Shanghai → Rotterdam"). Click **Process**.
- **Say:** "A customer emails in. Notice they left out key details — commodity,
  quantity, ready date, Incoterm."
- **Point at:** the **Agent Activity** panel lighting up — classification →
  extraction → validation → next-action — ~20 specialized agents.
- **Result to highlight:** the assistant replies with a **clarification email**
  asking *only* for the missing fields. "It didn't guess — it asked."

### ACT 2 — Customer supplies the missing info
- **Do:** Same sender, template **"Minimal Information"** / type the details
  (wooden furniture, 2×40HC, ready 2026-07-20, FOB). Process.
- **Say:** "The customer replies with the details. The system *merges* this with
  what it already knew — that's cross-turn memory, not a fresh start."
- **Result to highlight:** a **confirmation email** summarizing the complete,
  validated shipment and asking the customer to confirm.

### ACT 3 — Customer confirms → forwarder is assigned
- **Do:** Same sender, template **"Customer Confirmation"** ("yes, proceed").
  Process.
- **Say:** "Once the customer confirms, the assistant picks a freight forwarder
  **by fulfilment region** and emails them asking for a rate."
- **Point at the Forwarder Assignment card:**
  - **Route: China → Netherlands**
  - **Why this forwarder:** *"…serves the destination region (Netherlands)."*
  - the **rate-request email** drafted and addressed to that forwarder.
- **Say:** "It explains *why* it chose this forwarder — region match — and falls
  back to a random partner only if no regional match exists. Full transparency."

### ACT 4 — Forwarder replies with a rate → collated hand-off to Sales
- **Do:** The form auto-switches to **Forwarder**. Load template
  **"Forwarder Rate Quote"** (or type: "40HC: USD 2,650 all-in, transit 28
  days"). Process.
- **Say:** "The forwarder sends back a price. The assistant parses the rate and
  builds a **collated email for our sales team**."
- **Point at the Collated Email → Sales Team card:**
  - customer requirements + shipment + forwarder details in one place
  - **the forwarder cost rate** (USD 2,650 / container) and a **computed total**
  - the line: *"apply your margin before presenting to the customer."*
- **Say (the punchline):** "Critically — **nothing is auto-sent to the
  customer.** The rep adds their markup and owns the customer conversation. The
  AI does the legwork; the human keeps the relationship and the margin."

---

## 3. Key talking points (sprinkle these in)

- **Truly multi-agent:** ~20 specialized agents (classification, extraction,
  validation, port lookup, container standardization, forwarder assignment,
  sales notification…) orchestrated as a LangGraph state machine — not one big
  prompt.
- **Conversation memory:** every email is part of a thread; data accumulates and
  is re-validated across turns.
- **Asks instead of hallucinating:** missing mandatory fields trigger a
  clarification, never a made-up quote.
- **Explainable routing:** forwarder assignment shows the *reason* (region match)
  — important for trust and auditability.
- **Human-in-the-loop by design:** the collated rate goes to a salesperson for
  markup; the system never prices or emails the customer directly.
- **Built on Databricks** serving Claude (Sonnet 4.6) — enterprise LLM infra.

---

## 4. Architecture one-liner (if asked about tech)

> "FastAPI backend, a LangGraph orchestrator coordinating ~20 Claude-powered
> agents on Databricks serving endpoints, with a lightweight web UI. Each agent
> has a narrow job and a typed output, so the pipeline is debuggable and every
> decision is traceable in the Agent Activity panel you're seeing."

---

## 5. Closing (business value)

> "What you just saw took the assistant under a minute per email and required
> zero rep time until the final markup. Multiply that across an inbox of
> hundreds of quote requests a day — that's faster response times, no dropped
> leads, consistent data, and reps spending their time selling instead of
> retyping shipment details."

---

## 6. Likely questions — quick answers

- **"Does it send anything to the customer automatically?"** No. By design the
  only customer-facing touch is the clarification/confirmation; the final priced
  quote is always sent by a human after markup.
- **"What if a detail is missing?"** It asks a targeted clarification rather than
  guessing.
- **"How does it pick the forwarder?"** By fulfilment region (destination first,
  then origin), with a random fallback — and it shows the reason.
- **"Is it accurate?"** We run an automated 5-criteria scorecard
  (classification, full-pipeline execution, routing, valid response, data
  integrity) over real conversations — currently passing 9/9.
- **"What model / infra?"** Claude (Sonnet 4.6) via Databricks serving endpoints.

---

## 7. 30-second version (if you only have a moment)

1. Customer emails an incomplete request → AI asks for the missing details.
2. Customer replies → AI confirms the full shipment.
3. Customer confirms → AI picks a forwarder *by region* (and says why) and
   requests a rate.
4. Forwarder quotes → AI hands a **collated, markup-ready package to sales** —
   never emailing the customer directly.
