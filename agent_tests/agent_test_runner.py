#!/usr/bin/env python3
"""
Agent Test Runner - Utility for testing individual agents

This module provides utilities for:
1. Loading test cases from JSON files
2. Running individual agent tests
3. Comparing actual vs expected results
4. Generating performance metrics
5. Creating detailed reports
"""

import json
import time
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd

# Add the parent directory to the path to import agents
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


class AgentTestRunner:
    """
    Utility class for running agent tests with performance tracking
    """
    
    def __init__(self, test_cases_file: str, results_dir: str):
        """
        Initialize the test runner
        
        Args:
            test_cases_file: Path to the JSON file containing test cases
            results_dir: Directory to save test results
        """
        self.test_cases_file = test_cases_file
        self.results_dir = results_dir
        self.test_cases = self._load_test_cases()
        
        # Create results directory if it doesn't exist
        os.makedirs(results_dir, exist_ok=True)
    
    def _load_test_cases(self) -> Dict[str, Any]:
        """Load test cases from JSON file"""
        try:
            with open(self.test_cases_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading test cases: {e}")
            return {}
    
    def run_agent_test(self, agent_name: str, agent_instance, verbose: bool = True) -> Dict[str, Any]:
        """
        Run tests for a specific agent
        
        Args:
            agent_name: Name of the agent (e.g., 'classification_agent')
            agent_instance: Instance of the agent to test
            verbose: Whether to print detailed output
            
        Returns:
            Dictionary containing test results and metrics
        """
        if agent_name not in self.test_cases:
            print(f"❌ No test cases found for agent: {agent_name}")
            return {}
        
        agent_tests = self.test_cases[agent_name]
        test_cases = agent_tests.get("test_cases", [])
        
        if verbose:
            print(f"\n🧪 Testing Agent: {agent_name}")
            print(f"📊 Total Test Cases: {len(test_cases)}")
            print("=" * 60)
        
        results = {
            "agent_name": agent_name,
            "test_cases": [],
            "summary": {
                "total_tests": len(test_cases),
                "passed": 0,
                "failed": 0,
                "accuracy": 0.0,
                "avg_response_time": 0.0,
                "avg_confidence": 0.0
            },
            "timestamp": datetime.now().isoformat()
        }
        
        total_response_time = 0
        total_confidence = 0
        passed_tests = 0
        
        for i, test_case in enumerate(test_cases, 1):
            if verbose:
                print(f"\n📝 Test Case {i}/{len(test_cases)}: {test_case['id']}")
                print(f"   Description: {test_case['description']}")
                print(f"   Category: {test_case['category']}")
            
            # Run the test
            start_time = time.time()
            try:
                actual_output = agent_instance.process(test_case["input"])
                response_time = time.time() - start_time
                
                # Compare with expected output
                test_result = self._compare_results(
                    test_case["expected_output"], 
                    actual_output, 
                    test_case
                )
                
                # Update metrics
                total_response_time += response_time
                total_confidence += actual_output.get("confidence", 0)
                
                if test_result["passed"]:
                    passed_tests += 1
                    if verbose:
                        print(f"   ✅ PASSED (Response time: {response_time:.2f}s)")
                else:
                    if verbose:
                        print(f"   ❌ FAILED (Response time: {response_time:.2f}s)")
                        print(f"   Expected: {test_case['expected_output']}")
                        print(f"   Actual: {actual_output}")
                
                # Store test result
                test_result["response_time"] = response_time
                test_result["actual_output"] = actual_output
                results["test_cases"].append(test_result)
                
            except Exception as e:
                response_time = time.time() - start_time
                if verbose:
                    print(f"   💥 ERROR: {e} (Response time: {response_time:.2f}s)")
                
                # Store error result
                error_result = {
                    "test_id": test_case["id"],
                    "passed": False,
                    "error": str(e),
                    "response_time": response_time,
                    "actual_output": {"error": str(e)}
                }
                results["test_cases"].append(error_result)
        
        # Calculate summary metrics
        if len(test_cases) > 0:
            results["summary"]["passed"] = passed_tests
            results["summary"]["failed"] = len(test_cases) - passed_tests
            results["summary"]["accuracy"] = passed_tests / len(test_cases)
            results["summary"]["avg_response_time"] = total_response_time / len(test_cases)
            results["summary"]["avg_confidence"] = total_confidence / len(test_cases)
        
        if verbose:
            self._print_summary(results["summary"])
        
        return results
    
    def _compare_results(self, expected: Dict[str, Any], actual: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare actual results with expected results
        
        Args:
            expected: Expected output from test case
            actual: Actual output from agent
            test_case: Full test case for context
            
        Returns:
            Dictionary with comparison results
        """
        comparison = {
            "test_id": test_case["id"],
            "passed": True,
            "differences": [],
            "score": 0.0
        }
        
        # Check each expected field
        for field, expected_value in expected.items():
            actual_value = actual.get(field)
            
            if field == "confidence":
                # For confidence, allow some tolerance
                if abs(actual_value - expected_value) > 0.2:
                    comparison["differences"].append(f"Confidence: expected {expected_value}, got {actual_value}")
                    comparison["passed"] = False
            elif field == "escalation_needed":
                # For escalation, exact match required
                if actual_value != expected_value:
                    comparison["differences"].append(f"Escalation: expected {expected_value}, got {actual_value}")
                    comparison["passed"] = False
            else:
                # For other fields, exact match required
                if actual_value != expected_value:
                    comparison["differences"].append(f"{field}: expected {expected_value}, got {actual_value}")
                    comparison["passed"] = False
        
        # Calculate score based on number of correct fields
        total_fields = len(expected)
        correct_fields = total_fields - len(comparison["differences"])
        comparison["score"] = correct_fields / total_fields if total_fields > 0 else 0.0
        
        return comparison
    
    def _print_summary(self, summary: Dict[str, Any]):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Accuracy: {summary['accuracy']:.1%}")
        print(f"Avg Response Time: {summary['avg_response_time']:.2f}s")
        print(f"Avg Confidence: {summary['avg_confidence']:.2f}")
        print("=" * 60)
    
    def save_results(self, results: Dict[str, Any], agent_name: str) -> str:
        """
        Save test results to files
        
        Args:
            results: Test results dictionary
            agent_name: Name of the agent
            
        Returns:
            Path to the saved results file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_filename = f"{agent_name}_results_{timestamp}.json"
        json_path = os.path.join(self.results_dir, json_filename)
        
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Create CSV report
        csv_filename = f"{agent_name}_report_{timestamp}.csv"
        csv_path = os.path.join(self.results_dir, csv_filename)
        
        self._create_csv_report(results, csv_path)
        
        print(f"\n💾 Results saved:")
        print(f"   JSON: {json_path}")
        print(f"   CSV: {csv_path}")
        
        return json_path
    
    def _create_csv_report(self, results: Dict[str, Any], csv_path: str):
        """Create CSV report from test results"""
        report_data = []
        
        for test_case in results["test_cases"]:
            row = {
                "test_id": test_case["test_id"],
                "passed": test_case["passed"],
                "response_time": test_case.get("response_time", 0),
                "score": test_case.get("score", 0),
                "differences": "; ".join(test_case.get("differences", [])),
                "error": test_case.get("error", "")
            }
            
            # Add actual output fields
            actual_output = test_case.get("actual_output", {})
            row.update({
                "email_type": actual_output.get("email_type", ""),
                "sender_type": actual_output.get("sender_type", ""),
                "confidence": actual_output.get("confidence", 0),
                "escalation_needed": actual_output.get("escalation_needed", False)
            })
            
            report_data.append(row)
        
        # Add summary row
        summary = results["summary"]
        summary_row = {
            "test_id": "SUMMARY",
            "passed": f"{summary['passed']}/{summary['total_tests']}",
            "response_time": summary["avg_response_time"],
            "score": summary["accuracy"],
            "differences": f"Accuracy: {summary['accuracy']:.1%}",
            "error": "",
            "email_type": "",
            "sender_type": "",
            "confidence": summary["avg_confidence"],
            "escalation_needed": ""
        }
        report_data.append(summary_row)
        
        # Create DataFrame and save
        df = pd.DataFrame(report_data)
        df.to_csv(csv_path, index=False)
    
    def add_test_case(self, agent_name: str, test_case: Dict[str, Any]):
        """
        Add a new test case to the test cases file
        
        Args:
            agent_name: Name of the agent
            test_case: Test case dictionary
        """
        if agent_name not in self.test_cases:
            self.test_cases[agent_name] = {
                "description": f"Test cases for {agent_name}",
                "test_cases": []
            }
        
        self.test_cases[agent_name]["test_cases"].append(test_case)
        
        # Save updated test cases
        with open(self.test_cases_file, 'w') as f:
            json.dump(self.test_cases, f, indent=2)
        
        print(f"✅ Added test case {test_case['id']} to {agent_name}") 