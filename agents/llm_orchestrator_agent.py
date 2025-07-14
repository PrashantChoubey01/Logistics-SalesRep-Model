"""LLM-based Orchestrator Agent for Intelligent Email Processing with Logging and Indicative Rate Injection"""

import os
import sys
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("llm_orchestrator_agent")

# =====================================================
#                 LLM CONFIGURATION
# =====================================================
DATABRICKS_TOKEN = "dapi81b45be7f09611a410fc3e5104a8cadf-3"
DATABRICKS_BASE_URL = "https://adb-1825279086009288.8.azuredatabricks.net/serving-endpoints"
MODEL_ENDPOINT_ID = "databricks-meta-llama-3-3-70b-instruct"

# Import specialized agents (always use absolute imports)
from agents.classification_agent import ClassificationAgent
from agents.extraction_agent import ExtractionAgent
from agents.validation_agent import ValidationAgent
from agents.country_extractor_agent import CountryExtractorAgent
from agents.forwarder_assignment_agent import ForwarderAssignmentAgent
from agents.clarification_agent import ClarificationAgent
from agents.confirmation_agent import ConfirmationAgent
from agents.rate_parser_agent import RateParserAgent
from agents.response_generator_agent import ResponseGeneratorAgent
from agents.escalation_agent import EscalationAgent
from agents.rate_recommendation_agent import RateRecommendationAgent

from openai import OpenAI

class LLMOrchestratorAgent:
    def __init__(self, llm_api_key=None, llm_base_url=None, llm_model=None):
        self.llm_model = llm_model or MODEL_ENDPOINT_ID
        self.llm_client = OpenAI(
            api_key=llm_api_key or DATABRICKS_TOKEN,
            base_url=llm_base_url or DATABRICKS_BASE_URL
        )
        self.agents = {
            "ClassificationAgent": ClassificationAgent(),
            "ExtractionAgent": ExtractionAgent(),
            "ValidationAgent": ValidationAgent(),
            "CountryExtractorAgent": CountryExtractorAgent(),
            "ForwarderAssignmentAgent": ForwarderAssignmentAgent(),
            "ClarificationAgent": ClarificationAgent(),
            "ConfirmationAgent": ConfirmationAgent(),
            "RateParserAgent": RateParserAgent(),
            "ResponseGeneratorAgent": ResponseGeneratorAgent(),
            "EscalationAgent": EscalationAgent(),
            "RateRecommendationAgent": RateRecommendationAgent(),
        }
        # Initialize context for all agents
        for agent_name, agent in self.agents.items():
            try:
                # agent.load_context()
                logger.info(f"Loaded context for {agent_name}")
            except Exception as e:
                logger.warning(f"Could not load context for {agent_name}: {e}")
        logger.info("All agents loaded and context initialized.")

    def _llm_decide_next_agent(self, workflow_state):
        """Ask the LLM which agent to run next, and why."""
        prompt = self._build_llm_prompt(workflow_state)
        logger.info("Prompting LLM for next agent decision.")
        response = self.llm_client.chat.completions.create(
            model=self.llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=600
        )
        try:
            content = response.choices[0].message.content
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            json_str = content[json_start:json_end]
            logger.info(f"LLM decision raw output: {json_str}")
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"LLM output parsing error: {e}")
            return {
                "next_agent": "EscalationAgent",
                "reason": f"LLM output parsing error: {e}",
                "agent_input": {}
            }

    def _build_llm_prompt(self, workflow_state):
        agent_list = """
- ClassificationAgent: Classifies the type of incoming email (e.g., quote request, booking confirmation, inquiry, etc.).
- ExtractionAgent: Extracts structured shipment information from the email (origin, destination, container type, weight, dates, commodity, etc.).
- ValidationAgent: Validates and normalizes the extracted shipment data, checks for missing or inconsistent fields, and applies business rules.
- CountryExtractorAgent: Converts port codes or city names into country names for routing and compliance.
- ForwarderAssignmentAgent: Assigns the most suitable freight forwarder based on origin, destination, commodity, and other criteria.
- ClarificationAgent: Generates clarification requests for missing, ambiguous, or low-confidence information in the customer’s email.
- ConfirmationAgent: Detects and extracts confirmation intent (e.g., booking, quote acceptance) from customer emails.
- RateParserAgent: Parses and extracts rate/quote information from forwarder emails or attachments.
- RateRecommendationAgent: Provides recommended market rates for a shipment based on origin, destination, and container type.
- ResponseGeneratorAgent: Generates a complete, context-aware response email to the customer, sales person, or freight forwarder, based on all validated and enriched information. If a rate recommendation is available, include the indicative min and max rate in the response.
- EscalationAgent: Decides if the case should be escalated to a human (e.g., due to missing data, anomalies, customer request, or business logic).
"""
        instructions = f"""
You are an orchestration agent for a logistics email automation system.

You have access to the following specialized agents:
{agent_list}

You will be given:
- The original email (subject, body).
- The current workflow state (including results of previous agents).

Your job is to decide, step by step, which agent to invoke next, what input to provide, and why.

Respond in this JSON format:
{{
  "next_agent": "<AgentName>",
  "reason": "<Why this agent is needed next>",
  "agent_input": {{ ... }}
}}

Always explain your reasoning. If the workflow is complete, set "next_agent": "None" and provide a summary.

**Important:** The workflow is only complete when a response email has been generated (by ResponseGeneratorAgent), or if escalation is required (EscalationAgent). The final output should always be an email ready to be sent to the customer, sales person, or freight forwarder, or an escalation notice.

Current workflow state:
{json.dumps(workflow_state, indent=2)}
"""
        return instructions

    def run(self, input_data):
        """Run the LLM-based orchestration loop."""
        workflow_state = {
            "input": {
                "subject": input_data.get("subject", ""),
                "email_text": input_data.get("email_text", ""),
                "thread_id": input_data.get("thread_id", "")
            },
            "steps": [],
            "results": {},
            "status": "in_progress"
        }
        max_steps = 15
        logger.info("Starting orchestration loop.")
        for step_num in range(max_steps):
            llm_decision = self._llm_decide_next_agent(workflow_state)
            next_agent = llm_decision.get("next_agent")
            reason = llm_decision.get("reason", "")
            agent_input = llm_decision.get("agent_input", {})

            logger.info(f"Step {step_num+1}: Next agent: {next_agent} | Reason: {reason}")

            if next_agent is None or next_agent == "None":
                workflow_state["final_summary"] = reason
                workflow_state["status"] = "complete"
                logger.info("Workflow complete.")
                break

            if next_agent not in self.agents:
                workflow_state["status"] = "error"
                workflow_state["error"] = f"Unknown agent: {next_agent}"
                logger.error(f"Unknown agent: {next_agent}")
                break

            # RUN THE AGENT FIRST
            agent_result = self.agents[next_agent].run(agent_input)

            # THEN APPEND THE STEP WITH BOTH INPUT AND OUTPUT
            workflow_state["steps"].append({
                "step": step_num + 1,
                "agent": next_agent,
                "reason": reason,
                "input": agent_input,
                "output": agent_result
            })

            workflow_state["results"][next_agent] = agent_result
            workflow_state["latest_result"] = agent_result

            # Early exit if escalation or error
            if next_agent == "EscalationAgent" or agent_result.get("status") == "error":
                workflow_state["status"] = "escalated"
                break

            workflow_state["results"][next_agent] = agent_result
            workflow_state["latest_result"] = agent_result

            # Check if ValidationAgent should run
            if next_agent in ["ExtractionAgent", "CountryExtractorAgent"]:
                # Only run if not already run in this step
                if "ValidationAgent" not in workflow_state["results"]:
                    validation_input = {"shipment_data": agent_result}
                    validation_result = self.agents["ValidationAgent"].run(validation_input)
                    workflow_state["steps"].append({
                        "step": step_num + 1.1,
                        "agent": "ValidationAgent",
                        "reason": "Auto-validation after extraction/country extraction.",
                        "input": validation_input,
                        "output": validation_result
                    })
                    workflow_state["results"]["ValidationAgent"] = validation_result
                    workflow_state["latest_result"] = validation_result
                    # If validation fails, consider running ClarificationAgent
                    missing_fields = validation_result.get("missing_fields", [])
                    if missing_fields:
                        clarification_input = {
                            "extraction_data": agent_result,
                            "validation": validation_result,
                            "missing_fields": missing_fields
                        }
                        clarification_result = self.agents["ClarificationAgent"].run(clarification_input)
                        workflow_state["steps"].append({
                            "step": step_num + 1.2,
                            "agent": "ClarificationAgent",
                            "reason": "Auto-clarification for missing fields.",
                            "input": clarification_input,
                            "output": clarification_result
                        })
                        workflow_state["results"]["ClarificationAgent"] = clarification_result
                        workflow_state["latest_result"] = clarification_result
                        # Optionally, stop here and return clarification email
                        workflow_state["final_email"] = clarification_result
                        workflow_state["status"] = "clarification_requested"
                        break

            # Special: If RateRecommendationAgent, inject indicative rate into workflow_state for later use
            if next_agent == "RateRecommendationAgent" and agent_result.get("indicative_rate"):
                workflow_state["indicative_rate"] = agent_result["indicative_rate"]
                logger.info(f"Injected indicative rate: {agent_result['indicative_rate']}")

            # If escalation or error, stop
            if next_agent == "EscalationAgent" or agent_result.get("status") == "error":
                workflow_state["status"] = "escalated"
                logger.warning(f"Escalation or error at step {step_num+1}.")
                break

            # If a response email is generated, stop (ResponseGeneratorAgent)
            if next_agent == "ResponseGeneratorAgent":
                # Inject indicative rate info into the response if available
                if "indicative_rate" in workflow_state and "response_email" in agent_result:
                    agent_result["response_email"]["indicative_rate"] = workflow_state["indicative_rate"]
                workflow_state["final_email"] = agent_result
                workflow_state["status"] = "email_generated"
                logger.info("Response email generated. Workflow complete.")
                break

        # Fallback: If loop ends without a response email or escalation, escalate
        if workflow_state["status"] not in ("email_generated", "escalated", "complete"):
            workflow_state["status"] = "escalated"
            workflow_state["final_summary"] = "Workflow did not complete with a response email; escalation required."
            logger.warning("Workflow ended without completion. Escalation required.")

        return workflow_state

# =====================================================
#                 🔁 Local Test Harness
# =====================================================
def test_llm_orchestrator_agent():
    print("=== Testing LLM Orchestrator Agent ===")
    agent = LLMOrchestratorAgent()
    test_cases = [
        {
            "email_text": "Need quote for 2x40ft FCL from Shanghai to Long Beach, electronics, ready July 15th",
            "subject": "Shipping Quote Request"
        },
        {
            "email_text": "Yes, I confirm the booking for the containers",
            "subject": "Re: Booking Confirmation"
        },
        {
            "email_text": "What is your best rate for 20DC from AEAUH to AUBNE?",
            "subject": "Rate Inquiry"
        }
    ]
    for i, test_data in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        result = agent.run(test_data)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_llm_orchestrator_agent()