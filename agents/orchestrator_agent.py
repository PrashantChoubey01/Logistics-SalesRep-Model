"""Orchestrator Agent: Manages the end-to-end workflow for intelligent email processing."""

import os
import sys
import json
from copy import deepcopy

# Use absolute imports for package structure
try:
    from agents.base_agent import BaseAgent
    from agents.classification_agent import ClassificationAgent
    from agents.extraction_agent import ExtractionAgent
    from agents.validation_agent import ValidationAgent
    from agents.clarification_agent import ClarificationAgent
    from agents.forwarder_assignment_agent import ForwarderAssignmentAgent
    from agents.rate_parser_agent import RateParserAgent
    from agents.confirmation_agent import ConfirmationAgent
    from agents.response_generator_agent import ResponseGeneratorAgent
    from agents.escalation_agent import EscalationAgent
    from agents.memory_agent import MemoryAgent
    from agents.logging_agent import LoggingAgent
except ImportError:
    # Fallback for direct script run (not recommended for production)
    from base_agent import BaseAgent
    from classification_agent import ClassificationAgent
    from extraction_agent import ExtractionAgent
    from validation_agent import ValidationAgent
    from clarification_agent import ClarificationAgent
    from forwarder_assignment_agent import ForwarderAssignmentAgent
    from rate_parser_agent import RateParserAgent
    from confirmation_agent import ConfirmationAgent
    from response_generator_agent import ResponseGeneratorAgent
    from escalation_agent import EscalationAgent
    from memory_agent import MemoryAgent
    from logging_agent import LoggingAgent

class OrchestratorAgent(BaseAgent):
    """Coordinates all agents and manages the workflow."""

    def __init__(self):
        super().__init__("orchestrator_agent")
        self.classifier = ClassificationAgent()
        self.extractor = ExtractionAgent()
        self.validator = ValidationAgent()
        self.clarifier = ClarificationAgent()
        self.forwarder_assigner = ForwarderAssignmentAgent()
        self.rate_parser = RateParserAgent()
        self.confirmer = ConfirmationAgent()
        self.responder = ResponseGeneratorAgent()
        self.escalator = EscalationAgent()
        self.memory = MemoryAgent()

    def process(self, input_data):
        """
        input_data: {
            "subject": str,
            "email_text": str,
            "thread_id": str,
            "workflow_state": dict (optional, for ongoing threads)
        }
        """
        workflow = {
            "steps": [],
            "results": {},
            "final_action": None,
            "status": "in_progress"
        }
        # Load or initialize workflow state
        state = deepcopy(input_data.get("workflow_state", {}))
        thread_id = input_data.get("thread_id", "default-thread")
        clarification_attempted = state.get("clarification_attempted", False)

        # Step 1: Classification
        self.logger.info("Classifying email")
        classification = self.classifier.run(input_data)
        workflow["steps"].append({"classification": classification})
        workflow["results"]["classification"] = classification
        email_type = classification.get("email_type")
        confidence = classification.get("confidence", 1.0)
        extraction_input = {**input_data, **classification}
        extraction = self.extractor.run(extraction_input)

        # Escalate if classification fails or is low confidence
        if not email_type or confidence < 0.5:
            self.logger.info("Escalating due to failed/low-confidence classification")
            escalation = self.escalator.run({
                "email_text": input_data["email_text"],
                "subject": input_data["subject"],
                "prior_results": workflow["results"]
            })
            workflow["steps"].append({"escalation": escalation})
            workflow["final_action"] = {"action": "escalate_to_human", "details": escalation}
            workflow["status"] = "escalated"
            self.memory.run({"action": "store", "thread_id": thread_id, "message": workflow})
            workflow["workflow_state"] = deepcopy(state)
            return workflow

        # Step 2: Branch by email type
        if email_type == "logistics_request" or email_type == "clarification_reply":
            # Extraction
            self.logger.info("Extracting shipment info")
            extraction = self.extractor.run(input_data)
            workflow["steps"].append({"extraction": extraction})
            workflow["results"]["extraction"] = extraction

            # Validation
            self.logger.info("Validating extracted info")
            validation = self.validator.run({"extraction_data": extraction, "email_type": email_type})
            workflow["steps"].append({"validation": validation})
            workflow["results"]["validation"] = validation

            is_valid = validation.get("overall_validity", False)
            missing_fields = validation.get("missing_fields", []) + validation.get("llm_missing_fields", [])
            low_confidence = confidence < 0.7

            if is_valid and not missing_fields:
                # Forwarder Assignment
                self.logger.info("Assigning forwarder")
                forwarder_assignment = self.forwarder_assigner.run({"extraction_data": extraction})
                workflow["steps"].append({"forwarder_assignment": forwarder_assignment})
                workflow["results"]["forwarder_assignment"] = forwarder_assignment

                # Generate response email to forwarder (rate request)
                forwarder_emails = forwarder_assignment.get("assigned_forwarders", [])
                sales_email = forwarder_assignment.get("sales_email", "sales@example.com")
                response_to_forwarder = self.responder.run({
                    "recipient_type": "forwarder",
                    "context": {
                        "extraction": extraction,
                        "validation": validation,
                        "forwarder_assignment": forwarder_assignment
                    },
                    "custom_instructions": f"Send rate request to forwarder(s), CC sales ({sales_email}), include all customer requirements.",
                    "previous_messages": [],
                })
                workflow["steps"].append({"rate_request_to_forwarder": response_to_forwarder})
                workflow["results"]["rate_request_to_forwarder"] = response_to_forwarder

                # Optionally, notify sales
                response_to_sales = self.responder.run({
                    "recipient_type": "sales",
                    "context": {
                        "extraction": extraction,
                        "validation": validation,
                        "forwarder_assignment": forwarder_assignment
                    },
                    "custom_instructions": "Notify sales that rate request was sent to forwarder(s).",
                    "previous_messages": [],
                })
                workflow["steps"].append({"notify_sales": response_to_sales})
                workflow["results"]["notify_sales"] = response_to_sales

                workflow["final_action"] = {
                    "action": "wait_for_forwarder_response",
                    "details": {
                        "forwarder_emails": forwarder_emails,
                        "sales_email": sales_email,
                        "response_email": response_to_forwarder.get("response_email", "No response email generated."),
                        "recommended_forwarders": forwarder_emails
                    }
                }
                workflow["status"] = "waiting"
                self.memory.run({"action": "store", "thread_id": thread_id, "message": workflow})
                workflow["workflow_state"] = deepcopy(state)
                return workflow

            else:
                # If missing info and clarification not yet attempted, ask customer
                if not clarification_attempted:
                    self.logger.info("Requesting clarification from customer")
                    clarification = self.clarifier.run({
                        "extraction_data": extraction,
                        "validation": validation,
                        "missing_fields": missing_fields,
                        "thread_id": thread_id
                    })
                    workflow["steps"].append({"clarification": clarification})
                    workflow["results"]["clarification"] = clarification
                    workflow["final_action"] = {
                        "action": "request_clarification_from_customer",
                        "details": {
                            "clarification": clarification,
                            "response_email": clarification.get("clarification_message", "No clarification message generated.")
                        }
                    }
                    workflow["status"] = "waiting_for_customer"
                    # Mark clarification attempted in memory
                    state["clarification_attempted"] = True
                    self.memory.run({"action": "store", "thread_id": thread_id, "message": workflow})
                    workflow["workflow_state"] = deepcopy(state)
                    return workflow
                else:
                    # Already attempted clarification, escalate to human
                    self.logger.info("Escalating after failed clarification")
                    escalation = self.escalator.run({
                        "email_text": input_data["email_text"],
                        "subject": input_data["subject"],
                        "prior_results": workflow["results"]
                    })
                    workflow["steps"].append({"escalation": escalation})
                    workflow["final_action"] = {"action": "escalate_to_human", "details": escalation}
                    workflow["status"] = "escalated"
                    self.memory.run({"action": "store", "thread_id": thread_id, "message": workflow})
                    workflow["workflow_state"] = deepcopy(state)
                    return workflow

        elif email_type == "forwarder_response":
            # Rate Parsing
            self.logger.info("Parsing forwarder rate")
            rate_parsed = self.rate_parser.run(input_data)
            workflow["steps"].append({"rate_parsed": rate_parsed})
            workflow["results"]["rate_parsed"] = rate_parsed

            # Optionally validate the quote
            validation = self.validator.run({"extraction_data": rate_parsed, "email_type": email_type})
            workflow["steps"].append({"validation": validation})
            workflow["results"]["validation"] = validation

            # Notify sales with forwarder's quote
            response_to_sales = self.responder.run({
                "recipient_type": "sales",
                "context": {
                    "rate_parsed": rate_parsed,
                    "validation": validation
                },
                "custom_instructions": "Forwarder has sent a quote. Please review and share with customer as appropriate.",
                "previous_messages": [],
            })
            workflow["steps"].append({"notify_sales": response_to_sales})
            workflow["results"]["notify_sales"] = response_to_sales

            workflow["final_action"] = {
                "action": "wait_for_customer_confirmation",
                "details": {"sales_email": "sales@example.com"}
            }
            workflow["status"] = "waiting"
            self.memory.run({"action": "store", "thread_id": thread_id, "message": workflow})
            workflow["workflow_state"] = deepcopy(state)
            return workflow

        elif email_type == "confirmation_reply":
            # Confirmation
            self.logger.info("Processing confirmation")
            confirmation = self.confirmer.run(input_data)
            workflow["steps"].append({"confirmation": confirmation})
            workflow["results"]["confirmation"] = confirmation

            # Notify customer, sales, and/or forwarder
            response_to_customer = self.responder.run({
                "recipient_type": "customer",
                "context": {"confirmation": confirmation},
                "custom_instructions": "Acknowledge receipt of confirmation and provide next steps.",
                "previous_messages": [],
            })
            workflow["steps"].append({"acknowledge_customer": response_to_customer})
            workflow["results"]["acknowledge_customer"] = response_to_customer

            response_to_sales = self.responder.run({
                "recipient_type": "sales",
                "context": {"confirmation": confirmation},
                "custom_instructions": "Notify sales of customer confirmation.",
                "previous_messages": [],
            })
            workflow["steps"].append({"notify_sales": response_to_sales})
            workflow["results"]["notify_sales"] = response_to_sales

            workflow["final_action"] = {
                "action": "confirmation_processed",
                "details": {
                    "customer_acknowledged": True,
                    "sales_notified": True,
                    "response_email": response_to_customer.get("response_email", "No response email generated.")
                }
            }
            workflow["status"] = "completed"
            self.memory.run({"action": "store", "thread_id": thread_id, "message": workflow})
            workflow["workflow_state"] = deepcopy(state)
            return workflow

        elif email_type == "non_logistics":
            # Forward to support or ignore
            self.logger.info("Forwarding to support")
            workflow["final_action"] = {"action": "forward_to_support", "details": {}}
            workflow["status"] = "completed"
            self.memory.run({"action": "store", "thread_id": thread_id, "message": workflow})
            workflow["workflow_state"] = deepcopy(state)
            return workflow

        else:
            # Unknown type, escalate
            self.logger.info("Escalating unknown type")
            escalation = self.escalator.run({
                "email_text": input_data["email_text"],
                "subject": input_data["subject"],
                "prior_results": workflow["results"]
            })
            workflow["steps"].append({"escalation": escalation})
            workflow["final_action"] = {"action": "escalate_to_human", "details": escalation}
            workflow["status"] = "escalated"
            self.memory.run({"action": "store", "thread_id": thread_id, "message": workflow})
            workflow["workflow_state"] = deepcopy(state)
            return workflow

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_orchestrator_agent():
    print("=== Testing Orchestrator Agent ===")
    agent = OrchestratorAgent()
    agent.load_context()
    thread_id = "thread-001"

    test_cases = [
        # Customer logistics request, complete info
        {
            "subject": "Shipping Quote Request",
            "email_text": "Need quote for 2x40ft FCL from Shanghai to Long Beach, electronics, ready July 15th",
            "thread_id": thread_id,
            "workflow_state": {}
        },
        # Customer logistics request, missing info (should clarify)
        {
            "subject": "Shipping Quote Request",
            "email_text": "Need quote for shipping, thanks.",
            "thread_id": "thread-002",
            "workflow_state": {}
        },
        # Customer clarification reply (after clarification attempted)
        {
            "subject": "Re: Shipping Quote Request",
            "email_text": "Origin is Shanghai, destination is Long Beach.",
            "thread_id": "thread-002",
            "workflow_state": {"clarification_attempted": True}
        },
        # Forwarder response
        {
            "subject": "Rate Quote",
            "email_text": "Our rate is $2500 USD for FCL 40ft, valid until month end",
            "thread_id": "thread-003",
            "workflow_state": {}
        },
        # Customer confirmation
        {
            "subject": "Re: Booking Confirmation",
            "email_text": "Yes, I confirm the booking for the containers",
            "thread_id": "thread-004",
            "workflow_state": {}
        },
        # Non-logistics email
        {
            "subject": "Hello",
            "email_text": "Just checking in, hope you're well.",
            "thread_id": "thread-005",
            "workflow_state": {}
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Subject: {test_case['subject']}")
        result = agent.run(test_case)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_orchestrator_agent()