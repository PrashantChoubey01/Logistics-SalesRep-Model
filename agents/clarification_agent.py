"""Clarification Agent: Checks if customer email requires clarification using LLM function calling."""

import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from agents.base_agent import BaseAgent
except ImportError:
    from base_agent import BaseAgent

class ClarificationAgent(BaseAgent):
    """Agent to check if clarification is needed on customer emails using LLM function calling."""

    def __init__(self):
        super().__init__("clarification_agent")

    def process(self, input_data):
        """
        input_data should include:
            - email_text
            - subject
            - extraction_data (dict, optional)
            - validation (dict, optional)
            - missing_fields (list, optional)
        """
        email_text = input_data.get("email_text", "")
        subject = input_data.get("subject", "")
        extraction = input_data.get("extraction_data", {})
        validation = input_data.get("validation", {})
        missing_fields = input_data.get("missing_fields", []) or validation.get("missing_fields", [])

        # Find fields with low confidence (if available)
        low_conf_fields = []
        field_confidence = extraction.get("field_confidence", {})  # e.g. {"origin": 0.6, ...}
        for field, conf in field_confidence.items():
            if conf < 0.75:
                low_conf_fields.append((field, extraction.get(field)))

        # Build clarification questions
        clarification_questions = []
        for field in missing_fields:
            clarification_questions.append(f"Could you please provide the {field}?")

        for field, value in low_conf_fields:
            if value:
                clarification_questions.append(f"We detected your {field} as '{value}'. Can you confirm if this is correct?")

        clarification_needed = bool(clarification_questions)

        # Compose a suggested message
        clarification_message = "Dear Customer,\n\n"
        if clarification_questions:
            clarification_message += "To proceed with your shipping request, we need a bit more information:\n"
            for q in clarification_questions:
                clarification_message += f"- {q}\n"
            clarification_message += "\nThank you!"
        else:
            clarification_message += "All required information appears to be present. Thank you!"

        # Optionally, use LLM to refine the message
        if self.client:
            try:
                llm_result = self._llm_function_call(subject, email_text, missing_fields, low_conf_fields)
                llm_result["clarification_needed"] = clarification_needed
                llm_result["clarification_questions"] = clarification_questions
                return llm_result
            except Exception as e:
                print(f"[WARN] LLM function call failed: {e}")
                # Fallback to manual message
                return {
                    "clarification_needed": clarification_needed,
                    "clarification_questions": clarification_questions,
                    "clarification_message": clarification_message,
                    "fields_to_confirm": low_conf_fields,
                    "missing_fields": missing_fields,
                    "reasoning": "LLM call failed, fallback to manual message"
                }
        else:
            return {
                "clarification_needed": clarification_needed,
                "clarification_questions": clarification_questions,
                "clarification_message": clarification_message,
                "fields_to_confirm": low_conf_fields,
                "missing_fields": missing_fields,
                "reasoning": "LLM client not available, fallback to manual message"
            }

    def _llm_function_call(self, subject, email_text, missing_fields, low_conf_fields):
        import json
        function_schema = {
            "name": "check_clarification_needed",
            "description": "Generate clarification and confirmation questions for a customer shipping request email.",
            "parameters": {
                "type": "object",
                "properties": {
                    "clarification_needed": {
                        "type": "boolean",
                        "description": "True if clarification is needed"
                    },
                    "clarification_questions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of clarification or confirmation questions to ask the customer"
                    },
                    "fields_to_confirm": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Fields detected with low confidence that need confirmation"
                    },
                    "clarification_message": {
                        "type": "string",
                        "description": "Suggested clarification message to send to customer"
                    },
                    "missing_fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of missing or unclear fields"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Explanation for why clarification is needed or not"
                    }
                },
                "required": ["clarification_needed", "clarification_questions", "fields_to_confirm", "clarification_message", "missing_fields", "reasoning"]
            }
        }

        # Build a prompt for the LLM
        prompt = f"""
    You are an assistant that checks if a customer shipping request email is missing information or has fields that are uncertain.
    - If any required fields are missing, generate a clarification question for each.
    - If any fields were extracted with low confidence, generate a confirmation question for each.
    - Compose a polite message to the customer combining these questions.
    - List all missing fields and fields to confirm.

    Email:
    Subject: {subject}
    Body: {email_text}

    Missing fields: {missing_fields}
    Fields to confirm: {low_conf_fields}
    """

        response = self.client.chat.completions.create(
            model=self.config.get("model_name", "databricks-meta-llama-3-3-70b-instruct"),
            messages=[{"role": "user", "content": prompt}],
            tools=[{
                "type": "function",
                "function": function_schema
            }],
            tool_choice={"type": "function", "function": {"name": function_schema["name"]}},
            temperature=0.0,
            max_tokens=600
        )
        tool_calls = getattr(response.choices[0].message, "tool_calls", None)
        if not tool_calls:
            raise Exception("No tool_calls in LLM response")
        tool_args = tool_calls[0].function.arguments
        if isinstance(tool_args, str):
            tool_args = json.loads(tool_args)
        result = dict(tool_args)
        result["extraction_method"] = "databricks_llm_function_call"
        return result

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_clarification_agent():
    print("=== Testing Clarification Agent (Databricks LLM Function Calling) ===")
    agent = ClarificationAgent()
    context_loaded = agent.load_context()
    print(f"Context loaded: {context_loaded}, Has LLM client: {bool(agent.client)}")

    test_cases = [
        {
            "email_text": "Need quote for FCL shipment from Shanghai to Long Beach.",
            "subject": "Shipping Quote Request"
        },
        {
            "email_text": "Shipping request: 2x40ft containers, electronics, dangerous goods.",
            "subject": "Dangerous Goods"
        },
        {
            "email_text": "Please provide a quote. Destination: Rotterdam.",
            "subject": "Quote Request"
        },
        {
            "email_text": "LCL shipment, 5 CBM, from Mumbai to Hamburg, textiles, ready July 15th.",
            "subject": "LCL Export"
        },
        {
            "email_text": "I want to ship chemicals, but not sure about the container type.",
            "subject": "Chemicals"
        },
        {
            "email_text": "Need shipping, but no other details.",
            "subject": "Vague Request"
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Input: {test_case['subject']}")
        result = agent.run(test_case)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_clarification_agent()