# Agent Testing Framework

This framework allows you to test individual agents in isolation with comprehensive test cases and performance tracking.

## 🎯 Overview

The testing framework consists of:
- **Test Cases**: JSON files containing input/output pairs for each agent
- **Test Runner**: Utility class for running tests and generating reports
- **Agent Test Scripts**: Individual scripts for testing specific agents
- **Results**: Detailed reports in JSON and CSV formats

## 📁 File Structure

```
agent_tests/
├── agent_test_runner.py          # Main test runner utility
├── test_classification_agent.py  # Classification agent test script
├── README.md                     # This file
└── ...

test_cases/
├── classification_test_cases.json # Test cases for classification agent
└── ...

results/
├── classification_results/        # Results for classification agent
└── ...
```

## 🚀 Quick Start

### 1. Test the Classification Agent

```bash
cd agent_tests
python3 test_classification_agent.py
```

This will:
- Load 10 predefined test cases
- Run the classification agent on each case
- Compare results with expected outputs
- Generate performance metrics
- Save detailed reports

### 2. Add Custom Test Cases

You can easily add new test cases by editing the JSON file:

```json
{
  "id": "CLS_CUSTOM_001",
  "description": "Your test description",
  "category": "customer_quote_request",
  "input": {
    "email_text": "Your test email content",
    "sender": "test@example.com",
    "thread_id": "thread_test",
    "thread_history": [],
    "customer_context": {},
    "forwarder_context": {}
  },
  "expected_output": {
    "email_type": "customer_quote_request",
    "sender_type": "customer",
    "confidence": 0.8,
    "escalation_needed": false
  }
}
```

### 3. Programmatically Add Test Cases

```python
from agent_test_runner import AgentTestRunner

test_runner = AgentTestRunner("test_cases/classification_test_cases.json", "results/")
test_runner.add_test_case("classification_agent", your_test_case)
```

## 📊 Test Results

The framework generates:

### JSON Results
- Complete test results with actual vs expected outputs
- Performance metrics (accuracy, response time, confidence)
- Detailed error information for failed tests

### CSV Reports
- Summary table with all test cases
- Performance metrics per test case
- Easy to analyze in Excel or other tools

### Console Output
- Real-time test progress
- Detailed analysis of results
- Performance breakdown by category

## 🧪 Test Case Format

Each test case includes:

```json
{
  "id": "Unique test ID",
  "description": "Human-readable description",
  "category": "Test category for grouping",
  "input": {
    // Agent-specific input data
  },
  "expected_output": {
    // Expected agent output
  }
}
```

## 📈 Performance Metrics

The framework tracks:

- **Accuracy**: Percentage of tests that passed
- **Response Time**: Average time per test case
- **Confidence**: Average confidence scores
- **Category Performance**: Breakdown by email type
- **Error Analysis**: Detailed failure reasons

## 🔧 Extending the Framework

### Adding New Agents

1. Create test cases in `test_cases/your_agent_test_cases.json`
2. Create test script `test_your_agent.py`
3. Follow the pattern in `test_classification_agent.py`

### Custom Metrics

You can extend the `AgentTestRunner` class to add:
- Custom comparison logic
- Additional performance metrics
- Specialized reporting formats

## 🎯 Example Output

```
🧪 Testing Agent: classification_agent
📊 Total Test Cases: 10
============================================================

📝 Test Case 1/10: CLS_001
   Description: Customer quote request - electronics shipment
   Category: customer_quote_request
   ✅ PASSED (Response time: 2.34s)

...

============================================================
📊 TEST SUMMARY
============================================================
Total Tests: 10
Passed: 8 ✅
Failed: 2 ❌
Accuracy: 80.0%
Avg Response Time: 2.45s
Avg Confidence: 0.85
============================================================
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure the agent modules are in your Python path
2. **LLM Connection**: Check your Databricks API credentials
3. **Test Case Format**: Ensure JSON is valid and follows the expected structure

### Debug Mode

Set `verbose=True` in the test runner for detailed output:

```python
results = test_runner.run_agent_test("classification_agent", agent, verbose=True)
```

## 📝 Next Steps

1. Test the classification agent to see the framework in action
2. Add more test cases to improve coverage
3. Create test scripts for other agents (escalation, clarification, etc.)
4. Customize the framework for your specific needs

The framework is designed to be modular and extensible, making it easy to test all your agents systematically! 