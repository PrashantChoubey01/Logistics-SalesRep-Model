# 🚀 LangGraph Orchestrator with Rate Recommendation

## 📋 **OVERVIEW**

I've successfully enhanced the LangGraph orchestrator by adding a dedicated **RATE_RECOMMENDATION** node that fetches indicative rates based on port codes and container type, and includes them in email responses with appropriate disclaimers.

## 🏗️ **UPDATED ARCHITECTURE**

### **📊 Enhanced Graph Structure**

```
┌─────────────────────────────────────────────────────────────────┐
│                    LANGGRAPH ORCHESTRATOR FLOW                  │
└─────────────────────────────────────────────────────────────────┘

START
  │
  ▼
┌─────────────────┐
│  EMAIL_INPUT    │ ← Initialize workflow state
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ CONVERSATION    │ ← Analyze conversation context
│ STATE_ANALYSIS  │
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ CLASSIFICATION  │ ← Classify email type & intent
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ DATA_EXTRACTION │ ← Extract shipment details
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ DATA_ENRICHMENT │ ← Port lookup, container standardization
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ VALIDATION      │ ← Validate data quality
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ RATE_RECOMMENDATION │ ← 🆕 Fetch indicative rates
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ DECISION_NODE   │ ← LLM-based decision on next action
└─────────────────┘
  │
  ├─► INCOMPLETE_DATA ──► CLARIFICATION_REQUEST ──► END
  │
  ├─► COMPLETE_DATA ──► CONFIRMATION_REQUEST ──► END
  │
  ├─► CUSTOMER_CONFIRMS ──► FORWARDER_ASSIGNMENT ──► FORWARDER_EMAIL_GENERATION ──► END
  │
  ├─► FORWARDER_RESPONSE ──► RATE_COLLATION ──► END
  │
  └─► LOW_CONFIDENCE ──► ESCALATION ──► END
```

## 🆕 **NEW RATE_RECOMMENDATION NODE**

### **🎯 Purpose**
The **RATE_RECOMMENDATION** node fetches indicative rates based on:
- **Origin port code** (from port lookup)
- **Destination port code** (from port lookup)  
- **Container type** (from container standardization)

### **🔧 Functionality**

```python
def rate_recommendation_node(state: WorkflowState) -> WorkflowState:
    """
    RATE_RECOMMENDATION Node: Fetch indicative rates based on port codes and container type.
    
    This node uses the port codes from validation and container type to fetch
    indicative rates for reference purposes.
    """
```

### **📊 Input Data**
- **Port codes**: Extracted from `state["enriched_data"]["port_lookup"]["results"]`
- **Container type**: From `state["enriched_data"]["container_standardization"]["standard_type"]`

### **📈 Output Data**
- **Indicative rate**: Formatted rate range (e.g., "$919 - $1,249")
- **Disclaimer**: Clear statement about indicative nature of rates
- **Rate metadata**: Match type, data source, etc.

### **🛡️ Error Handling**
- Graceful handling of missing port codes or container type
- Fallback when rate data is not available
- Comprehensive error logging

## 🎯 **RATE RECOMMENDATION AGENT ENHANCEMENTS**

### **🔧 Fixed Issues**
- **Import path**: Fixed `from base_agent import BaseAgent` to `from .base_agent import BaseAgent`
- **Data validation**: Added null checks for `rates_df`
- **Pandas operations**: Fixed `dropna()` usage on pandas Series
- **Type safety**: Added proper type checking for DataFrame operations

### **📊 Enhanced Functionality**
- **Flexible input**: Accepts multiple field names for origin, destination, container
- **Container normalization**: Maps common container types (20GP→20DC, 40HQ→40HC, etc.)
- **Price parsing**: Converts `[919,1249]` format to `$919 - $1,249`
- **Fallback matching**: Tries route-only matching if exact container match fails

### **🔄 Process Flow**
1. **Extract data** from input (origin, destination, container)
2. **Normalize container type** using mapping
3. **Search for exact match** (origin + destination + container)
4. **Fallback search** if no exact match (origin + destination only)
5. **Parse price range** and format for display
6. **Return comprehensive results** with metadata

## 📧 **EMAIL INTEGRATION**

### **🎯 Rate Information in Responses**
The rate recommendation data is now included in all email responses:

```python
# Rate data passed to response generator
"rate_data": state.get("rate_recommendation", {})
```

### **📝 Disclaimer Included**
Every rate recommendation includes a clear disclaimer:

> "This is an indicative rate for reference purposes only and includes only freight cost. Actual rates may vary based on specific requirements, market conditions, and additional services."

### **📊 Response Types**
- **Clarification requests**: Include rate info if available
- **Confirmation requests**: Include rate info for complete data
- **Standard responses**: Include rate info for customer reference

## 🏗️ **UPDATED STATE MANAGEMENT**

### **WorkflowState Enhancement**
```python
class WorkflowState(TypedDict):
    # ... existing fields ...
    
    # Rate Data
    rate_recommendation: Dict[str, Any]
    
    # ... rest of fields ...
```

### **Rate Recommendation Structure**
```python
rate_recommendation = {
    "indicative_rate": "$919 - $1,249",
    "disclaimer": "This is an indicative rate for reference purposes only...",
    "query": {
        "Origin_Code": "CNSHA",
        "Destination_Code": "USLAX", 
        "Container_Type": "40HC"
    },
    "rate_recommendation": {
        "match_type": "exact_match",
        "total_rates_found": 1,
        "rate_range": "$919 - $1,249",
        "price_range_recommendation": "[919,1249]",
        "formatted_rate_range": "$919 - $1,249"
    },
    "data_source": "rate_recommendation.csv",
    "total_records_searched": 1000
}
```

## 🔄 **UPDATED WORKFLOW**

### **📊 New Node Sequence**
1. **EMAIL_INPUT** → **CONVERSATION_STATE_ANALYSIS** → **CLASSIFICATION** → **DATA_EXTRACTION** → **DATA_ENRICHMENT** → **VALIDATION** → **🆕 RATE_RECOMMENDATION** → **DECISION_NODE**

### **🎯 Conditional Routing**
- **RATE_RECOMMENDATION** node executes after **VALIDATION**
- Rate data is available for all subsequent nodes
- **DECISION_NODE** can consider rate availability in routing decisions

## 🚀 **STREAMLIT INTEGRATION**

### **📊 Updated Visualization**
- **New node position**: RATE_RECOMMENDATION at position (6, 0)
- **Updated graph layout**: Extended x-axis range to accommodate new node
- **Enhanced edges**: Added VALIDATION → RATE_RECOMMENDATION → DECISION_NODE

### **📈 Rate Display**
- **Rate information**: Shows indicative rates in results
- **Disclaimer display**: Clear indication of rate nature
- **Metadata**: Shows rate source and match type

## 🧪 **TESTING**

### **📊 Test Script**
Created `test_langgraph_simple.py` to verify:
- ✅ LangGraph orchestrator import
- ✅ Orchestrator initialization  
- ✅ Workflow execution with rate recommendation
- ✅ RATE_RECOMMENDATION node execution
- ✅ Rate data availability in final state

### **🎯 Expected Results**
- **Workflow history**: Should include "RATE_RECOMMENDATION"
- **Rate data**: Should contain indicative rate and disclaimer
- **Email responses**: Should include rate information with disclaimer

## 🎯 **KEY BENEFITS**

### **1. 🎯 Enhanced Customer Experience**
- **Immediate rate information**: Customers get indicative rates in responses
- **Clear expectations**: Disclaimer sets proper expectations
- **Professional presentation**: Formatted rate ranges look professional

### **2. 🧠 Better Decision Making**
- **Rate-aware routing**: Decision node can consider rate availability
- **Complete information**: All nodes have access to rate data
- **Contextual responses**: Responses include relevant rate information

### **3. 🛡️ Robust Error Handling**
- **Graceful degradation**: Works even when rate data is unavailable
- **Clear messaging**: Users understand when rates aren't available
- **Comprehensive logging**: Full visibility into rate recommendation process

### **4. 📊 Better Monitoring**
- **Rate success tracking**: Can monitor rate recommendation success rates
- **Data quality insights**: Understand rate data coverage
- **Performance metrics**: Track rate lookup performance

## 🚀 **USAGE**

### **📧 Sample Email Processing**
```python
# Email with rate request
email_data = {
    'email_text': 'Hi, I need rates for 2x40HC from Shanghai to Los Angeles...',
    'subject': 'Rate Request - Shanghai to LA',
    'sender': 'customer@company.com',
    'thread_id': 'thread-123',
    'timestamp': '2024-04-15T10:30:00Z'
}

# Process with LangGraph orchestrator
result = orchestrator.orchestrate_workflow(email_data)

# Check rate recommendation
rate_data = result['final_state']['rate_recommendation']
print(f"Indicative Rate: {rate_data['indicative_rate']}")
print(f"Disclaimer: {rate_data['disclaimer']}")
```

### **📊 Expected Output**
```
Indicative Rate: $919 - $1,249
Disclaimer: This is an indicative rate for reference purposes only and includes only freight cost. Actual rates may vary based on specific requirements, market conditions, and additional services.
```

## 📝 **CONCLUSION**

The enhanced LangGraph orchestrator with rate recommendation provides:

- **🎯 Immediate value**: Customers get indicative rates in responses
- **🛡️ Clear expectations**: Proper disclaimers about rate nature
- **🧠 Better decisions**: Rate-aware workflow routing
- **📊 Better monitoring**: Comprehensive rate recommendation tracking
- **🔄 Seamless integration**: Rate data flows through entire workflow

This implementation successfully addresses the requirement to include indicative rates in email responses while maintaining the robust, state-driven architecture of the LangGraph orchestrator. 