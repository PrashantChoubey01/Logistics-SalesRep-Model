#!/usr/bin/env python3
"""
Model Accuracy Test Harness
===========================
Runs representative emails through the FULL LangGraph agent pipeline
(`LangGraphWorkflowOrchestrator.process_email`) and scores every email
against 5 best-practice (BP) performance criteria.

The model is considered to "respond properly to every email by passing
through all the agents" only when all 5 BPs pass for every scenario.

5 Best-Practice criteria
-------------------------
BP1  Correct Classification   email_type matches the expected category
BP2  Full Pipeline Execution  status == completed AND no agent reported an error
BP3  Correct Routing          the populated response branch is one the scenario allows
BP4  Valid Response           a non-empty subject + body was produced (addressed by name)
BP5  Data Integrity           required fields present / no hallucinated ports / clarifications
                              actually list the missing fields

Usage:
    source venv_ai_model/bin/activate
    python3 test_model_accuracy.py
    python3 test_model_accuracy.py --json reports/accuracy.json   # also dump machine-readable results

Exit code is 0 only if every scenario passes all 5 BPs.
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from langgraph_workflow_orchestrator import LangGraphWorkflowOrchestrator  # noqa: E402

# Ordered priority of response keys -> the customer/sales facing email each represents.
RESPONSE_KEYS = [
    "clarification_response_result",
    "confirmation_response_result",
    "acknowledgment_response_result",
    "confirmation_acknowledgment_result",
    "customer_quote_result",
    "sales_notification_result",
    "forwarder_assignment_result",
]

# Agent result keys that must NOT contain an "error" for the pipeline to be "clean".
CRITICAL_AGENT_KEYS = [
    "classification_result",
    "extraction_result",
    "validation_result",
    "next_action_result",
]


# ---------------------------------------------------------------------------
# Test scenarios
# ---------------------------------------------------------------------------
# Each scenario optionally seeds the thread with `setup` emails (not scored),
# then scores the final `email`. `accept_response_keys` is the set of response
# branches that are valid routing outcomes for that scenario (BP3). `accept_types`
# is the set of acceptable email_type classifications (BP1).
SCENARIOS: List[Dict[str, Any]] = [
    {
        "name": "Complete FCL quote request",
        "email": {
            "sender": "john.doe@techcorp.com",
            "subject": "FCL Shipping Quote - Shanghai to Los Angeles",
            "content": (
                "Hi,\n\nI need a quote for an FCL shipment:\n"
                "Origin: Shanghai, China\nDestination: Los Angeles, USA\n"
                "Container Type: 40HC\nQuantity: 2 containers\n"
                "Commodity: Electronics\nWeight: 15,000 kg\n"
                "Ready Date: 2026-07-15\nIncoterm: FOB\n\n"
                "Please send rates.\n\nBest regards,\nJohn Doe"
            ),
        },
        "accept_types": {"customer_quote_request", "customer_clarification"},
        "accept_response_keys": {
            "confirmation_response_result",
            "clarification_response_result",
        },
    },
    {
        "name": "Minimal info request",
        "email": {
            "sender": "jane.smith@imports.com",
            "subject": "Shipping quote needed",
            "content": (
                "Hi, I need shipping rates from China to USA. "
                "Can you help?\n\nThanks,\nJane Smith"
            ),
        },
        "accept_types": {"customer_quote_request", "customer_clarification"},
        "accept_response_keys": {"clarification_response_result"},
        "expect_missing_fields": True,
    },
    {
        "name": "LCL quote request",
        "email": {
            "sender": "mike.chen@trading.com",
            "subject": "LCL Shipping Quote Request",
            "content": (
                "Hello,\n\nLCL shipment quote please:\n"
                "From: Singapore\nTo: New York\n"
                "Weight: 500 kg\nVolume: 2.5 CBM\n"
                "Commodity: Textiles\nReady: 2026-08-01\n\n"
                "Regards,\nMike Chen"
            ),
        },
        "accept_types": {"customer_quote_request", "customer_clarification"},
        "accept_response_keys": {
            "confirmation_response_result",
            "clarification_response_result",
        },
    },
    {
        "name": "Customer confirmation (after complete quote)",
        "setup": [
            {
                "sender": "john.doe@techcorp.com",
                "subject": "FCL Shipping Quote - Shanghai to Los Angeles",
                "content": (
                    "Hi,\n\nFCL shipment:\nOrigin: Shanghai, China\n"
                    "Destination: Los Angeles, USA\nContainer Type: 40HC\n"
                    "Quantity: 2\nCommodity: Electronics\nWeight: 15,000 kg\n"
                    "Ready Date: 2026-07-15\nIncoterm: FOB\n\nThanks,\nJohn Doe"
                ),
            }
        ],
        "email": {
            "sender": "john.doe@techcorp.com",
            "subject": "Re: FCL Shipping Quote - Shanghai to Los Angeles",
            "content": (
                "Hi,\n\nI confirm all the details are correct. "
                "Please proceed with the booking.\n\nBest regards,\nJohn Doe"
            ),
        },
        "accept_types": {"customer_confirmation", "customer_clarification"},
        "accept_response_keys": {
            "confirmation_acknowledgment_result",
            "acknowledgment_response_result",
            "forwarder_assignment_result",
        },
    },
    {
        "name": "Forwarder rate response",
        "email": {
            "sender": "ops@pacificbridgelogistics.com",
            "subject": "Rate Quote - Shanghai to Los Angeles",
            "content": (
                "Hello,\n\nOur rate for Shanghai (CNSHG) to Los Angeles (USLAX):\n"
                "40HC: USD 2,850 all-in\nTransit: 18 days\n"
                "Validity: until 2026-12-31\n\nRegards,\nPacific Bridge Logistics"
            ),
        },
        # Classifier's canonical label for a forwarder rate email is `forwarder_rate_quote`
        # (see test_cases/classification_test_cases.json CLS_003); accept both.
        "accept_types": {"forwarder_response", "forwarder_rate_quote"},
        "accept_response_keys": {
            "sales_notification_result",
            "acknowledgment_response_result",
            "customer_quote_result",
        },
    },
]


# ---------------------------------------------------------------------------
# Multi-turn conversations
# ---------------------------------------------------------------------------
# Each conversation runs all turns on ONE shared thread_id; every turn is scored
# against the 5 BPs with its own expectations. This exercises the whole workflow
# end-to-end (clarification -> confirmation -> forwarder assignment -> sales
# notification + customer quote), including cumulative cross-turn data merging.
CONVERSATIONS: List[Dict[str, Any]] = [
    {
        "name": "Maria Garcia full journey",
        "turns": [
            {
                "name": "T1 incomplete request -> clarification",
                "email": {
                    "sender": "maria.garcia@acmeimports.com",
                    "subject": "Shipping Quote Request",
                    "content": (
                        "Hi,\n\nI'd like a quote to ship a 40HC container from "
                        "Shanghai to Rotterdam. Could you let me know your rates?\n\n"
                        "Thanks,\nMaria Garcia"
                    ),
                },
                "accept_types": {"customer_quote_request", "customer_clarification"},
                "accept_response_keys": {"clarification_response_result"},
                "expect_missing_fields": True,
            },
            {
                "name": "T2 supplies info -> confirmation",
                "email": {
                    "sender": "maria.garcia@acmeimports.com",
                    "subject": "Re: Shipping Quote Request",
                    "content": (
                        "Thanks for the quick reply. Here are the details:\n"
                        "- Commodity: Wooden furniture\n"
                        "- Quantity: 2 x 40HC containers\n"
                        "- Ready date: 2026-07-20\n"
                        "- Incoterm: FOB\n\nPlease send the rates.\n\nMaria"
                    ),
                },
                "accept_types": {"customer_quote_request", "customer_clarification"},
                "accept_response_keys": {
                    "confirmation_response_result",
                    "clarification_response_result",
                },
            },
            {
                "name": "T3 confirms -> ack + forwarder assignment",
                "email": {
                    "sender": "maria.garcia@acmeimports.com",
                    "subject": "Re: Shipping Quote Request",
                    "content": (
                        "Yes, all the details are correct. Please go ahead and "
                        "proceed with the booking.\n\nBest regards,\nMaria Garcia"
                    ),
                },
                "accept_types": {"customer_confirmation", "customer_clarification"},
                "accept_response_keys": {
                    "confirmation_acknowledgment_result",
                    "acknowledgment_response_result",
                    "forwarder_assignment_result",
                },
            },
            {
                "name": "T4 forwarder rate -> sales notification + customer quote",
                "email": {
                    "sender": "ops@pacificbridgelogistics.com",
                    "subject": "Rate Quote - Shanghai to Rotterdam",
                    "content": (
                        "Hello,\n\nOur rate for Shanghai (CNSHG) to Rotterdam (NLRTM):\n"
                        "- 40HC: USD 2,650 all-in, per container\n"
                        "- Transit: 28 days\n- Validity: until 2026-12-31\n\n"
                        "Regards,\nPacific Bridge Logistics"
                    ),
                },
                "accept_types": {"forwarder_response", "forwarder_rate_quote"},
                "accept_response_keys": {
                    "sales_notification_result",
                    "acknowledgment_response_result",
                    "customer_quote_result",
                },
                # Proves the forwarder rate flows into the sales notification / customer
                # quote (regression guard for the two orchestrator key-mismatch bugs).
                "expect_content": ["2,650"],
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------
def _first_populated_response(result: Dict[str, Any]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """Return (key, value) of the highest-priority populated response branch."""
    for key in RESPONSE_KEYS:
        val = result.get(key)
        if val and not (isinstance(val, dict) and val.get("error")):
            return key, val
    return None, None


def _agent_errors(result: Dict[str, Any]) -> List[str]:
    errors = []
    for key in CRITICAL_AGENT_KEYS:
        val = result.get(key)
        if isinstance(val, dict) and val.get("error"):
            errors.append(f"{key}: {val['error']}")
    return errors


def score_scenario(scenario: Dict[str, Any], outcome: Dict[str, Any]) -> Dict[str, Any]:
    """Score a single processed email against the 5 BPs."""
    status = outcome.get("status")
    result = outcome.get("result") or {}
    checks: Dict[str, Dict[str, Any]] = {}

    # --- BP1: Correct Classification ---
    classification = result.get("classification_result") or {}
    email_type = classification.get("email_type")
    bp1_pass = email_type in scenario["accept_types"]
    checks["BP1_classification"] = {
        "pass": bp1_pass,
        "detail": f"email_type={email_type!r} expected one of {sorted(scenario['accept_types'])}",
    }

    # --- BP2: Full Pipeline Execution ---
    errors = _agent_errors(result)
    bp2_pass = status == "completed" and not outcome.get("error") and not errors
    checks["BP2_pipeline"] = {
        "pass": bp2_pass,
        "detail": f"status={status}"
        + (f", workflow_error={outcome.get('error')}" if outcome.get("error") else "")
        + (f", agent_errors={errors}" if errors else ""),
    }

    # --- BP3: Correct Routing ---
    resp_key, resp_val = _first_populated_response(result)
    bp3_pass = resp_key in scenario["accept_response_keys"]
    checks["BP3_routing"] = {
        "pass": bp3_pass,
        "detail": f"response={resp_key!r} expected one of {sorted(scenario['accept_response_keys'])}",
    }

    # --- BP4: Valid Response Generated ---
    subject = (resp_val or {}).get("subject", "") if resp_val else ""
    body = (resp_val or {}).get("body", "") if resp_val else ""
    bp4_pass = bool(subject and body and len(body.strip()) > 20)
    # Penalise generic salutation when a real name was available.
    generic = "valued customer" in body.lower()
    checks["BP4_response"] = {
        "pass": bp4_pass and not generic,
        "detail": f"subject_len={len(subject)}, body_len={len(body)}"
        + (", generic_salutation=True" if generic else ""),
    }

    # --- BP5: Data Integrity ---
    bp5_pass = True
    bp5_detail = []
    if scenario.get("expect_missing_fields"):
        missing = (resp_val or {}).get("missing_fields") or []
        if not missing:
            bp5_pass = False
            bp5_detail.append("expected non-empty missing_fields for clarification")
        else:
            bp5_detail.append(f"missing_fields={len(missing)}")
    # No hallucinated rate: a customer-facing email should not invent a USD rate
    # unless this scenario actually carried rate info (forwarder/quote flows).
    if resp_key in {"clarification_response_result", "confirmation_response_result"}:
        if body and ("USD" in body or "$" in body):
            # Confirmation/clarification should not quote a price.
            bp5_pass = False
            bp5_detail.append("hallucinated price in non-quote response")
    # Required content: the substring(s) must appear in some populated response body.
    # Used to prove data actually flows end-to-end (e.g. forwarder rate -> sales/customer quote).
    expect_content = scenario.get("expect_content") or []
    if expect_content:
        all_bodies = " ".join(
            str((result.get(k) or {}).get("body", "")) for k in RESPONSE_KEYS
        )
        norm = all_bodies.replace(",", "").replace(" ", "")
        for needle in expect_content:
            if needle.replace(",", "").replace(" ", "") not in norm:
                bp5_pass = False
                bp5_detail.append(f"missing expected content {needle!r} in responses")
            else:
                bp5_detail.append(f"found {needle!r}")
    checks["BP5_data_integrity"] = {
        "pass": bp5_pass,
        "detail": "; ".join(bp5_detail) or "ok",
    }

    all_pass = all(c["pass"] for c in checks.values())
    return {
        "scenario": scenario["name"],
        "all_pass": all_pass,
        "checks": checks,
        "email_type": email_type,
        "response_branch": resp_key,
        "subject": subject,
        "body_preview": (body[:200] + "…") if body and len(body) > 200 else body,
    }


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
async def run() -> Tuple[List[Dict[str, Any]], bool]:
    print("=" * 70)
    print("🧪  MODEL ACCURACY TEST — full agent pipeline")
    print("=" * 70)
    orchestrator = LangGraphWorkflowOrchestrator()

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    scored: List[Dict[str, Any]] = []

    for idx, scenario in enumerate(SCENARIOS, 1):
        thread_id = f"acctest_{stamp}_{idx}"
        print(f"\n{'─' * 70}\n▶  Scenario {idx}/{len(SCENARIOS)}: {scenario['name']}")
        print(f"   thread_id={thread_id}")

        # Seed prior turns (not scored) so routing-dependent scenarios are realistic.
        for setup_email in scenario.get("setup", []):
            await orchestrator.process_email({**setup_email, "thread_id": thread_id})

        try:
            outcome = await orchestrator.process_email({**scenario["email"], "thread_id": thread_id})
        except Exception as exc:  # noqa: BLE001 - report any crash as a failed scenario
            outcome = {"status": "failed", "error": str(exc), "result": {}}

        card = score_scenario(scenario, outcome)
        scored.append(card)

        flag = "✅ PASS" if card["all_pass"] else "❌ FAIL"
        print(f"   {flag}  classified={card['email_type']!r} route={card['response_branch']!r}")
        for name, chk in card["checks"].items():
            mark = "✓" if chk["pass"] else "✗"
            print(f"      {mark} {name}: {chk['detail']}")

    # Multi-turn conversations: all turns share one thread; every turn is scored.
    for cidx, convo in enumerate(CONVERSATIONS, 1):
        thread_id = f"acctest_{stamp}_convo{cidx}"
        print(f"\n{'═' * 70}\n💬  Conversation {cidx}/{len(CONVERSATIONS)}: {convo['name']}")
        print(f"   thread_id={thread_id}")
        for tidx, turn in enumerate(convo["turns"], 1):
            print(f"\n   ── Turn {tidx}/{len(convo['turns'])}: {turn['name']}")
            try:
                outcome = await orchestrator.process_email({**turn["email"], "thread_id": thread_id})
            except Exception as exc:  # noqa: BLE001
                outcome = {"status": "failed", "error": str(exc), "result": {}}

            # Label the scorecard row with the conversation + turn name.
            turn_scenario = {**turn, "name": f"{convo['name']} · {turn['name']}"}
            card = score_scenario(turn_scenario, outcome)
            scored.append(card)

            flag = "✅ PASS" if card["all_pass"] else "❌ FAIL"
            print(f"      {flag}  classified={card['email_type']!r} route={card['response_branch']!r}")
            for name, chk in card["checks"].items():
                mark = "✓" if chk["pass"] else "✗"
                print(f"         {mark} {name}: {chk['detail']}")

    # Summary table
    print(f"\n{'=' * 70}\n📊  SCORECARD\n{'=' * 70}")
    bp_names = ["BP1_classification", "BP2_pipeline", "BP3_routing", "BP4_response", "BP5_data_integrity"]
    header = f"{'Scenario':<42}" + "".join(f"{n.split('_')[0]:>6}" for n in bp_names) + "  Result"
    print(header)
    print("-" * len(header))
    for card in scored:
        row = f"{card['scenario'][:41]:<42}"
        for n in bp_names:
            row += f"{'  ✓' if card['checks'][n]['pass'] else '  ✗':>6}"
        row += "   PASS" if card["all_pass"] else "   FAIL"
        print(row)

    total = len(scored)
    passed = sum(1 for c in scored if c["all_pass"])
    bp_totals = {n: sum(1 for c in scored if c["checks"][n]["pass"]) for n in bp_names}
    print("-" * len(header))
    print(f"\nScenarios fully passing all 5 BPs: {passed}/{total} ({100 * passed / total:.0f}%)")
    for n in bp_names:
        print(f"   {n:<22} {bp_totals[n]}/{total} ({100 * bp_totals[n] / total:.0f}%)")

    return scored, passed == total


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the model accuracy test harness.")
    parser.add_argument("--json", type=str, default=None, help="Optional path to dump JSON results.")
    args = parser.parse_args()

    scored, all_passed = asyncio.run(run())

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(scored, indent=2, default=str))
        print(f"\n💾  JSON results written to {out}")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
