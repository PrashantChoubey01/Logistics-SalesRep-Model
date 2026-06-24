# SeaRates SDR AI Model — Demo Run-of-Show & Narration Script

> Multi-agent email automation for logistics sales (SeaRates by DP World).
> Read this top-to-bottom while presenting. It is sequenced to the demo:
> **intro → play the pre-recorded conversation → run it live.**
> Each live email takes ~30–60s to process — every step below has a
> **TALK TRACK** with ~1–2 minutes of material so you're never waiting in silence.

---

## Run-of-show at a glance (~10–12 min)

| # | Segment | You're doing | ~Time |
|---|---------|--------------|-------|
| 0 | **Opening** | Talk to camera (no clicks): what it is, what it does, stack, current scope | 2 min |
| 1 | **Pre-recorded playback** | Show the already-recorded customer↔bot + forwarder↔bot thread | 1–2 min |
| 2 | **Live — Act 1** | Send incomplete customer email → clarification | 1–2 min |
| 3 | **Live — Act 2** | Customer supplies details → confirmation | 1–2 min |
| 4 | **Live — Act 3** | Customer confirms → forwarder assigned (by region) | 1–2 min |
| 5 | **Live — Act 4** | Forwarder sends rate → collated email to Sales | 1–2 min |
| 6 | **Future scope + close** | Talk to camera: roadmap + value | 1–2 min |

> Setup checklist is in **Appendix A** — do it before you hit record.

---

## SEGMENT 0 — OPENING (talk to camera, ~2 min)

Have the UI open but don't click yet. Say, in your own words:

**What it is**
> "This is the SeaRates SDR AI Model — an autonomous sales assistant for
> logistics. It can be integrate with the crm mailbox and handles freight quote requests
> end-to-end."

**What it does**
> "When a customer emails asking for a shipping rate, it reads the email,
> understands the shipment, asks for anything missing, picks the right freight
> forwarder, requests a rate, and then hands a ready-to-quote package to our
> sales team — all automatically. The rep only steps in to add the margin and
> talk to the customer."

**The tech stack (keep it crisp)**
> "Under the hood it's a true **multi-agent system** — around 20 specialized AI
> agents, each with one narrow job — orchestrated with **LangGraph**. The brain
> is **Claude, Sonnet 4.6**, running on **Databricks serving endpoints**, so all
> the inference happens inside our own governed cloud environment. The backend is
> **FastAPI**; what you're looking at is a lightweight web UI."

**Why that matters (security in one breath)**
> "Because it runs on Databricks, our data never leaves our environment — we get
> frontier-model quality with enterprise governance, access control, and audit
> logging."

**Current scope**
> "Today it's a complete quoting assistant for the inbox. It's API-first, so the
> exact same engine can sit behind a **CRM** — Salesforce, HubSpot, or DP World's
> own — and auto-respond to customer enquiries. Let me show you how it thinks."

---

## SEGMENT 1 — PRE-RECORDED PLAYBACK (~1–2 min)

Play the conversation you already recorded (customer↔bot and forwarder↔bot).
While it plays, narrate the arc so the audience sees the whole loop before the
live run:

> "Here's a complete conversation that already happened. A customer asks for a
> quote… the bot notices details are missing and asks for them… the customer
> replies… the bot confirms the shipment… then it reaches out to a forwarder for
> a rate… the forwarder responds… and the bot packages everything for our sales
> team. That's the full journey. Now let me run the same thing **live**, step by
> step, so you can see each agent work in real time."

> Transition line: *"I'll start a fresh thread and send the first email as the
> customer."* (Click **🔄 Reset Thread**, set **Email From = Customer**.)

---

## SEGMENT 2 — LIVE ACT 1: Incomplete request → Clarification

**Scenario:** Maria Garcia (Acme Imports) wants 2 × 40HC of wooden furniture,
**Shanghai → Rotterdam.**

**Click:** Template **"Complete FCL"** (or type a short request that omits
commodity / quantity / ready date / Incoterm) → **Process Email**.

**TALK TRACK — fill ~90s while the agents run:**
- "Watch the **Agent Activity** panel on the right — every box that lights up is
  a separate agent doing one job."
- "First it **classifies** the email — is this a customer, a forwarder, a new
  request or a reply? Then an **extraction** agent pulls out the shipment
  details, a **validation** agent checks them, and a **next-action** agent
  decides what to do."
- "This is the important part: the customer left out key details. A naïve bot
  would hallucinate a quote. This one **recognizes what's missing and asks** —
  exactly like a good sales rep would."
- "Around 20 agents are coordinated here as a state machine, so every decision is
  traceable — nothing is a black box."

**Point at the result:** the **clarification email** requesting only the missing
fields. *"It asked for precisely what it needs — nothing more."*

---

## SEGMENT 3 — LIVE ACT 2: Customer supplies info → Confirmation

**Click:** Same sender, template **"Minimal Information"** (commodity = wooden
furniture, 2 × 40HC, ready 2026-07-20, Incoterm FOB) → **Process**.

**TALK TRACK — fill ~90s:**
- "The customer replies with the missing details. Here's something subtle but
  powerful: the system doesn't start over — it **merges** this new information
  with what it already knew from the first email."
- "That's **cross-turn memory**. Every email is part of one thread, and the
  shipment record accumulates and gets re-validated as the conversation goes on."
- "It also does logistics-specific cleanup — standardizing the container type,
  looking up the actual ports and their codes — so the data is clean and
  consistent, no human transcription errors."

**Point at the result:** the **confirmation email** summarizing the full,
validated shipment and asking the customer to confirm. *"Now it has a complete,
verified picture and it's double-checking with the customer before spending
anyone's time."*

---

## SEGMENT 4 — LIVE ACT 3: Customer confirms → Forwarder assigned

**Click:** Same sender, template **"Customer Confirmation"** ("yes, proceed") →
**Process**.

**TALK TRACK — fill ~90s:**
- "The customer confirms. Now the assistant does what a rep would do next — it
  goes to find a rate from a **freight forwarder**."
- "It picks the forwarder by **fulfilment region** — it looks at the route and
  chooses a partner who serves that lane."
- "And crucially, it **tells you why**." (Point at the card.)

**Point at the Forwarder Assignment card:**
- **Route: China → Netherlands**
- **Why this forwarder:** *"…serves the destination region (Netherlands)."*
- the **rate-request email** drafted and addressed to that forwarder.

- "So there's no mystery in the routing — it explains the decision, and falls
  back to another partner only if no regional match exists. That explainability
  matters for trust and for audit."

---

## SEGMENT 5 — LIVE ACT 4: Forwarder sends rate → Collated email to Sales

**Click:** The form auto-switches to **Forwarder**. Template **"Forwarder Rate
Quote"** (or type: "40HC: USD 2,650 all-in, transit 28 days") → **Process**.

**TALK TRACK — fill ~90s (this is the climax — land these points):**
- "Now the forwarder replies with a price. The assistant **parses the rate** and
  builds a single **collated email for our sales team**."
- "Everything is in one place — the customer's requirements, the shipment, the
  forwarder's details, the cost rate, and even a computed total."
- "And here's the business rule that matters most:" (point at the card) **"nothing
  is auto-sent to the customer.** The collated rate goes to a **salesperson** with
  a note to **apply their margin** before quoting. The AI does the legwork; the
  human keeps the markup and owns the customer relationship — that's
  human-in-the-loop by design."
- "This is also where the Databricks security story lands: all of this — the
  customer data, the rates — was processed inside our own governed environment,
  never a public API."

**Point at the Collated Email → Sales Team card:** the rate (USD 2,650 / container),
the total, and the *"apply your margin"* line.

---

## SEGMENT 6 — FUTURE SCOPE + CLOSE (talk to camera, ~1–2 min)

**Future scope**
> "What you just saw is the quoting brain — but the same multi-agent architecture
> extends across the whole logistics stack:
> - Integrate with a **TMS** so that once a customer accepts, it auto-creates the
>   booking and tracks milestones — closing the loop from quote to execution.
> - Integrate with a **WMS** to reconcile cargo-readiness dates and schedule dock
>   slots.
> - Add a **pricing/rate engine** so the markup becomes an automatic suggestion.
> - Extend to **WhatsApp and web chat**, and turn every thread into **analytics** —
>   win rates, lane demand, quote turnaround.
>
> Today it quotes; tomorrow it books, schedules, prices, and reports — one agent
> fabric across the logistics lifecycle."

**Close (business value)**
> "Each of those emails took the assistant under a minute and zero rep time until
> the final markup. Across an inbox of hundreds of quote requests a day, that's
> faster responses, no dropped leads, clean consistent data, and reps spending
> their time selling instead of retyping shipment details — all on enterprise-grade,
> secure infrastructure."

---
---

# APPENDIX

## A. Before you hit record (setup checklist)
1. Start the servers: `./start_servers.sh`
2. Open the UI: **http://localhost:5002**
3. **Hard-refresh** (Cmd+Shift+R) for the latest UI.
4. Click **🔄 Reset Thread** for a clean conversation.
5. Open the **🤖 Agent Activity** panel (top-right).
6. Have the **Email Templates** dropdown ready (pre-fills each step — no typing
   on camera).
7. Have your **pre-recorded** customer/forwarder conversation ready to play for
   Segment 1.

> The live flow is **one thread** — do NOT reset between Acts 1–4, or the
> assistant loses its conversation memory.

## B. Likely questions — quick answers
- **"Does it email the customer automatically?"** No. The only customer-facing
  touches are the clarification/confirmation; the final **priced** quote is always
  sent by a human after markup.
- **"What if a detail is missing?"** It asks a targeted clarification instead of
  guessing.
- **"How does it pick the forwarder?"** By fulfilment region (destination first,
  then origin), with a fallback — and it shows the reason.
- **"Is it accurate?"** We run an automated 5-criteria scorecard (classification,
  full-pipeline execution, routing, valid response, data integrity) over real
  conversations — currently passing 9/9.
- **"What model / infra?"** Claude (Sonnet 4.6) via **Databricks** serving endpoints.
- **"Can it plug into our CRM?"** Yes — API-first (email-in / structured-response-out),
  so it sits behind Salesforce, HubSpot, Zoho, or DP World's own CRM.
- **"Where does our data go / is it secure?"** Inference runs on Databricks inside
  our own cloud tenancy — RBAC, audit logging, private networking; not a public API.
- **"Can it do more than quoting?"** The same fabric extends to TMS, WMS, pricing,
  and analytics (see Segment 6).

## C. Tech stack (reference)
- **LLM:** Claude Sonnet 4.6 (latest, most capable tier).
- **LLM infra:** Databricks serving endpoints (OpenAI-compatible, function-calling).
- **Orchestration:** LangGraph state machine, ~20 typed (Pydantic) agents.
- **Backend:** Python + FastAPI (REST API, port 5001).
- **Frontend:** lightweight vanilla JS/HTML/CSS web UI.
- **State:** thread store with cumulative cross-turn extraction.

## D. 30-second version (if you only have a moment)
1. Customer emails an incomplete request → AI asks for the missing details.
2. Customer replies → AI confirms the full shipment.
3. Customer confirms → AI picks a forwarder *by region* (and says why) and
   requests a rate.
4. Forwarder quotes → AI hands a **collated, markup-ready package to sales** —
   never emailing the customer directly.
