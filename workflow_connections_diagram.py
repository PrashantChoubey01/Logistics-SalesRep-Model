#!/usr/bin/env python3
"""
LangGraph Workflow Connections Diagram
=====================================

Visual representation of how LangGraph nodes are connected.
"""

def print_workflow_diagram():
    """Print a visual representation of the LangGraph workflow connections."""
    
    print("\n" + "="*100)
    print("🏗️ LANGGRAPH WORKFLOW CONNECTIONS DIAGRAM")
    print("="*100)
    
    print("""
📧 EMAIL_INPUT
    ↓
🔄 CONVERSATION_STATE
    ↓
🔍 FORWARDER_DETECTION
    ↓
    ├─ FORWARDER_PATH ──→ 📧 FORWARDER_RESPONSE ──→ END
    │
    └─ CUSTOMER_PATH ──→ 🏷️ CLASSIFICATION
                            ↓
                        📊 DATA_EXTRACTION
                            ↓
                        🔧 DATA_ENRICHMENT
                            ↓
                        ✅ VALIDATION
                            ↓
                        💰 RATE_RECOMMENDATION
                            ↓
                        🎯 DECISION
                            ↓
                            ├─ CLARIFICATION_REQUEST ──→ END
                            ├─ CONFIRMATION_REQUEST ──→ END
                            ├─ CONFIRMATION_ACKNOWLEDGMENT ──→ END
                            ├─ FORWARDER_ASSIGNMENT ──→ 📧 FORWARDER_RESPONSE ──→ END
                            └─ ESCALATION ──→ END
""")
    
    print("\n" + "="*100)
    print("📋 DETAILED CONNECTION BREAKDOWN")
    print("="*100)
    
    connections = [
        {
            "from": "EMAIL_INPUT",
            "to": "CONVERSATION_STATE",
            "type": "Direct Edge",
            "description": "Initialize workflow and analyze conversation context"
        },
        {
            "from": "CONVERSATION_STATE", 
            "to": "FORWARDER_DETECTION",
            "type": "Direct Edge",
            "description": "Check if sender is a known forwarder"
        },
        {
            "from": "FORWARDER_DETECTION",
            "to": "FORWARDER_RESPONSE",
            "type": "Conditional Edge (FORWARDER_PATH)",
            "description": "If sender is forwarder → handle forwarder communication"
        },
        {
            "from": "FORWARDER_DETECTION",
            "to": "CLASSIFICATION",
            "type": "Conditional Edge (CUSTOMER_PATH)",
            "description": "If sender is customer → start customer processing"
        },
        {
            "from": "CLASSIFICATION",
            "to": "DATA_EXTRACTION",
            "type": "Direct Edge",
            "description": "Extract shipment details from email"
        },
        {
            "from": "DATA_EXTRACTION",
            "to": "DATA_ENRICHMENT",
            "type": "Direct Edge",
            "description": "Enrich data with port codes, container info"
        },
        {
            "from": "DATA_ENRICHMENT",
            "to": "VALIDATION",
            "type": "Direct Edge",
            "description": "Validate extracted data quality"
        },
        {
            "from": "VALIDATION",
            "to": "RATE_RECOMMENDATION",
            "type": "Direct Edge",
            "description": "Generate rate recommendations"
        },
        {
            "from": "RATE_RECOMMENDATION",
            "to": "DECISION",
            "type": "Direct Edge",
            "description": "LLM-based decision on next action"
        },
                            {
                        "from": "DECISION",
                        "to": "CLARIFICATION_REQUEST",
                        "type": "Conditional Edge",
                        "description": "Ask customer for missing information"
                    },
                    {
                        "from": "DECISION",
                        "to": "CONFIRMATION_REQUEST",
                        "type": "Conditional Edge",
                        "description": "Ask customer to confirm details"
                    },
        {
            "from": "DECISION",
            "to": "CONFIRMATION_ACKNOWLEDGMENT",
            "type": "Conditional Edge",
            "description": "Acknowledge customer confirmation"
        },
        {
            "from": "DECISION",
            "to": "FORWARDER_ASSIGNMENT",
            "type": "Conditional Edge",
            "description": "Assign forwarder after customer confirmation"
        },
        {
            "from": "DECISION",
            "to": "ESCALATION",
            "type": "Conditional Edge",
            "description": "Escalate to human for complex cases"
        },
        {
            "from": "FORWARDER_ASSIGNMENT",
            "to": "FORWARDER_RESPONSE",
            "type": "Direct Edge",
            "description": "Generate response after forwarder assignment"
        }
    ]
    
    for i, connection in enumerate(connections, 1):
        print(f"\n{i:2d}. {connection['from']:25} ──{connection['type']:>30}──→ {connection['to']:25}")
        print(f"    {'':25}   {connection['description']}")
    
    print("\n" + "="*100)
    print("🎯 KEY ROUTING DECISIONS")
    print("="*100)
    
    routing_decisions = [
        {
            "node": "FORWARDER_DETECTION",
            "function": "forwarder_routing_decision()",
            "logic": "Check if sender email is in forwarder database",
            "paths": {
                "FORWARDER_PATH": "→ FORWARDER_RESPONSE (handle forwarder communication)",
                "CUSTOMER_PATH": "→ CLASSIFICATION (start customer processing)"
            }
        },
        {
            "node": "DECISION",
            "function": "route_decision()",
            "logic": "LLM-based decision + customer confirmation override",
                                    "paths": {
                            "CLARIFICATION_REQUEST": "→ Ask customer for missing information",
                            "CONFIRMATION_REQUEST": "→ Ask customer to confirm details",
                            "CONFIRMATION_ACKNOWLEDGMENT": "→ Acknowledge customer confirmation",
                            "FORWARDER_ASSIGNMENT": "→ Assign forwarder (after customer confirms)",
                            "ESCALATION": "→ Escalate to human agent"
                        }
        }
    ]
    
    for decision in routing_decisions:
        print(f"\n🔍 {decision['node']}")
        print(f"   Function: {decision['function']}")
        print(f"   Logic: {decision['logic']}")
        print(f"   Paths:")
        for path, description in decision['paths'].items():
            print(f"     • {path}: {description}")
    
    print("\n" + "="*100)
    print("🚀 WORKFLOW PATHS")
    print("="*100)
    
    workflow_paths = [
        {
            "name": "Forwarder Email Path",
            "path": "EMAIL_INPUT → CONVERSATION_STATE → FORWARDER_DETECTION → FORWARDER_RESPONSE",
            "description": "Direct handling of forwarder communications"
        },
                            {
                        "name": "Incomplete Customer Request Path",
                        "path": "EMAIL_INPUT → CONVERSATION_STATE → FORWARDER_DETECTION → CLASSIFICATION → DATA_EXTRACTION → DATA_ENRICHMENT → VALIDATION → RATE_RECOMMENDATION → DECISION → CLARIFICATION_REQUEST",
                        "description": "Process incomplete customer request and ask for missing information"
                    },
                    {
                        "name": "Complete Customer Request Path",
                        "path": "EMAIL_INPUT → CONVERSATION_STATE → FORWARDER_DETECTION → CLASSIFICATION → DATA_EXTRACTION → DATA_ENRICHMENT → VALIDATION → RATE_RECOMMENDATION → DECISION → CONFIRMATION_REQUEST",
                        "description": "Process complete customer request and ask for confirmation"
                    },
        {
            "name": "Customer Confirmation Path",
            "path": "EMAIL_INPUT → CONVERSATION_STATE → FORWARDER_DETECTION → CLASSIFICATION → DATA_EXTRACTION → DATA_ENRICHMENT → VALIDATION → RATE_RECOMMENDATION → DECISION → FORWARDER_ASSIGNMENT → FORWARDER_RESPONSE",
            "description": "Customer confirms details → assign forwarder → generate response"
        },
        {
            "name": "Escalation Path",
            "path": "EMAIL_INPUT → CONVERSATION_STATE → FORWARDER_DETECTION → CLASSIFICATION → DATA_EXTRACTION → DATA_ENRICHMENT → VALIDATION → RATE_RECOMMENDATION → DECISION → ESCALATION",
            "description": "Escalate complex cases to human agent"
        }
    ]
    
    for i, path_info in enumerate(workflow_paths, 1):
        print(f"\n{i}. {path_info['name']}")
        print(f"   Path: {path_info['path']}")
        print(f"   Description: {path_info['description']}")
    
    print("\n" + "="*100)
    print("🔧 CONDITIONAL ROUTING LOGIC")
    print("="*100)
    
    print("""
🎯 FORWARDER_DETECTION Routing:
   • Check sender email against forwarder database
   • If forwarder → FORWARDER_PATH → FORWARDER_RESPONSE
   • If customer → CUSTOMER_PATH → CLASSIFICATION

            🎯 DECISION Routing (with customer confirmation override):
               • Check conversation_state and email_classification
               • If customer_confirmation → FORCE FORWARDER_ASSIGNMENT
               • Otherwise follow LLM decision:
                 - send_clarification_request → CLARIFICATION_REQUEST
                 - send_confirmation_request → CONFIRMATION_REQUEST
                 - send_confirmation_acknowledgment → CONFIRMATION_ACKNOWLEDGMENT
                 - booking_details_confirmed_assign_forwarders → FORWARDER_ASSIGNMENT
                 - escalate_to_human → ESCALATION
""")

def main():
    """Display the workflow connections diagram."""
    print_workflow_diagram()

if __name__ == "__main__":
    main() 