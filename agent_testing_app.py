#!/usr/bin/env python3
"""
Agent Testing Streamlit Application
==================================

A comprehensive testing interface for all 13 essential agents.
"""

import streamlit as st
import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import test cases
from tests.test_all_agents import AGENT_TEST_CASES, get_agent_test_cases, get_all_agent_names, get_agent_info

# Import all agents
from agents.conversation_state_agent import ConversationStateAgent
from agents.classification_agent import ClassificationAgent
from agents.extraction_agent import ExtractionAgent
from agents.port_lookup_agent import PortLookupAgent
from agents.container_standardization_agent import ContainerStandardizationAgent
from agents.enhanced_validation_agent import EnhancedValidationAgent
from agents.rate_recommendation_agent import RateRecommendationAgent
from agents.next_action_agent import NextActionAgent
from agents.response_generator_agent import ResponseGeneratorAgent
from agents.forwarder_assignment_agent import ForwarderAssignmentAgent
from agents.forwarder_detection_agent import ForwarderDetectionAgent
from agents.forwarder_response_agent import ForwarderResponseAgent

# Agent class mapping
AGENT_CLASSES = {
    "conversation_state_agent": ConversationStateAgent,
    "classification_agent": ClassificationAgent,
    "extraction_agent": ExtractionAgent,
    "port_lookup_agent": PortLookupAgent,
    "container_standardization_agent": ContainerStandardizationAgent,
    "enhanced_validation_agent": EnhancedValidationAgent,
    "rate_recommendation_agent": RateRecommendationAgent,
    "next_action_agent": NextActionAgent,
    "response_generator_agent": ResponseGeneratorAgent,
    "forwarder_assignment_agent": ForwarderAssignmentAgent,
    "forwarder_detection_agent": ForwarderDetectionAgent,
    "forwarder_response_agent": ForwarderResponseAgent
}

def initialize_agent(agent_name: str):
    """Initialize an agent and load its context."""
    try:
        agent_class = AGENT_CLASSES.get(agent_name)
        if not agent_class:
            return None, f"Agent class not found: {agent_name}"
        
        agent = agent_class()
        if hasattr(agent, 'load_context'):
            success = agent.load_context()
            if not success:
                return None, f"Failed to load context for {agent_name}"
        
        return agent, None
    except Exception as e:
        return None, f"Error initializing {agent_name}: {str(e)}"

def run_single_test(agent, test_case: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
    """Run a single test case for an agent."""
    start_time = time.time()
    
    try:
        # Run the agent
        result = agent.run(test_case["input"])
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Analyze results based on agent type
        analysis = analyze_test_result(result, test_case, agent_name)
        
        return {
            "status": "success",
            "result": result,
            "duration": duration,
            "analysis": analysis,
            "error": None,
            "test_input": test_case["input"]
        }
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            "status": "error",
            "result": None,
            "duration": duration,
            "analysis": None,
            "error": str(e),
            "test_input": test_case["input"]
        }

def analyze_test_result(result: Dict[str, Any], test_case: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
    """Analyze test results based on agent type."""
    analysis = {
        "passed": False,
        "score": 0.0,
        "details": []
    }
    
    if result.get("status") == "success":
        analysis["details"].append("✅ Agent executed successfully")
        analysis["score"] += 0.3
        
        # Agent-specific analysis
        if agent_name == "conversation_state_agent":
            expected_state = test_case.get("expected_state")
            actual_state = result.get("conversation_state")
            if expected_state and actual_state:
                if expected_state == actual_state:
                    analysis["details"].append(f"✅ State prediction correct: {actual_state}")
                    analysis["score"] += 0.7
                    analysis["passed"] = True
                else:
                    analysis["details"].append(f"❌ State prediction incorrect: expected {expected_state}, got {actual_state}")
            
            confidence = result.get("confidence_score", 0.0)
            if confidence > 0.7:
                analysis["details"].append(f"✅ High confidence: {confidence:.2f}")
            elif confidence > 0.5:
                analysis["details"].append(f"⚠️ Medium confidence: {confidence:.2f}")
            else:
                analysis["details"].append(f"❌ Low confidence: {confidence:.2f}")
        
        elif agent_name == "classification_agent":
            expected_type = test_case.get("expected_type")
            actual_type = result.get("email_type")
            if expected_type and actual_type:
                if expected_type == actual_type:
                    analysis["details"].append(f"✅ Email type correct: {actual_type}")
                    analysis["score"] += 0.7
                    analysis["passed"] = True
                else:
                    analysis["details"].append(f"❌ Email type incorrect: expected {expected_type}, got {actual_type}")
        
        elif agent_name == "extraction_agent":
            expected_fields = test_case.get("expected_fields", [])
            extracted_data = result.get("extracted_data", {})
            
            if expected_fields:
                found_fields = 0
                for field in expected_fields:
                    if field in extracted_data and extracted_data[field]:
                        found_fields += 1
                        analysis["details"].append(f"✅ Found field: {field}")
                    else:
                        analysis["details"].append(f"❌ Missing field: {field}")
                
                field_score = found_fields / len(expected_fields) if expected_fields else 0
                analysis["score"] += field_score * 0.7
                analysis["passed"] = field_score > 0.7
        
        elif agent_name == "forwarder_detection_agent":
            expected = test_case.get("expected")
            actual = result.get("is_forwarder", False)
            if expected == actual:
                analysis["details"].append(f"✅ Forwarder detection correct: {actual}")
                analysis["score"] += 0.7
                analysis["passed"] = True
            else:
                analysis["details"].append(f"❌ Forwarder detection incorrect: expected {expected}, got {actual}")
        
        else:
            # Generic analysis for other agents
            analysis["details"].append("✅ Agent returned valid response")
            analysis["score"] += 0.7
            analysis["passed"] = True
    
    else:
        analysis["details"].append(f"❌ Agent execution failed: {result.get('error', 'Unknown error')}")
    
    return analysis

def display_test_results(test_results: List[Dict[str, Any]], agent_name: str):
    """Display test results in a formatted way."""
    if not test_results:
        st.warning("No test results to display")
        return
    
    # Results Summary Section
    st.markdown("---")
    st.subheader("📊 Test Results Summary")
    
    # Summary statistics
    total_tests = len(test_results)
    successful_tests = sum(1 for r in test_results if r["status"] == "success")
    passed_tests = sum(1 for r in test_results if r.get("analysis", {}).get("passed", False))
    avg_duration = sum(r["duration"] for r in test_results) / total_tests
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tests", total_tests)
    with col2:
        st.metric("Successful", successful_tests)
    with col3:
        st.metric("Passed", passed_tests)
    with col4:
        st.metric("Avg Duration", f"{avg_duration:.2f}s")
    
    # Success rate with visual indicator
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    if success_rate >= 80:
        st.success(f"🎉 Overall Success Rate: {success_rate:.1f}%")
    elif success_rate >= 60:
        st.warning(f"⚠️ Overall Success Rate: {success_rate:.1f}%")
    else:
        st.error(f"❌ Overall Success Rate: {success_rate:.1f}%")
    
    # Detailed Results Section
    st.markdown("---")
    st.subheader("🔍 Detailed Test Results")
    
    for i, test_result in enumerate(test_results):
        test_name = test_result.get('test_name', f'Test {i+1}')
        test_status = "✅ Passed" if test_result.get("analysis", {}).get("passed", False) else "⚠️ Partial" if test_result["status"] == "success" else "❌ Failed"
        
        with st.expander(f"{test_status} - {test_name}", expanded=False):
            # Test Overview
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**Test:** {test_name}")
                st.markdown(f"**Status:** {test_status}")
                st.markdown(f"**Duration:** {test_result['duration']:.2f}s")
            
            with col2:
                if test_result["status"] == "success":
                    analysis = test_result.get("analysis", {})
                    score = analysis.get("score", 0.0)
                    st.progress(score)
                    st.markdown(f"**Score:** {score:.1f}/1.0")
                else:
                    st.error("❌ Failed")
            
            with col3:
                # Show key result data
                if test_result["status"] == "success" and test_result["result"]:
                    result = test_result["result"]
                    
                    # Show key fields based on agent type
                    if agent_name == "conversation_state_agent":
                        st.markdown(f"**State:** {result.get('conversation_state', 'N/A')}")
                        st.markdown(f"**Confidence:** {result.get('confidence_score', 0.0):.2f}")
                    elif agent_name == "classification_agent":
                        st.markdown(f"**Type:** {result.get('email_type', 'N/A')}")
                        st.markdown(f"**Confidence:** {result.get('confidence', 0.0):.2f}")
                    elif agent_name == "extraction_agent":
                        extracted_data = result.get("extracted_data", {})
                        if extracted_data:
                            st.markdown(f"**Fields:** {len(extracted_data)} extracted")
                    elif agent_name == "forwarder_detection_agent":
                        st.markdown(f"**Is Forwarder:** {result.get('is_forwarder', False)}")
                        st.markdown(f"**Confidence:** {result.get('confidence', 0.0):.2f}")
            
            # Input and Output Section
            st.markdown("---")
            st.markdown("**📥 Input vs 📤 Output**")
            
            input_col, output_col = st.columns(2)
            
            with input_col:
                st.markdown("**📥 Test Input:**")
                if "test_input" in test_result:
                    st.json(test_result["test_input"])
                else:
                    st.info("Input data not available")
            
            with output_col:
                st.markdown("**📤 Agent Output:**")
                if test_result["status"] == "success" and test_result["result"]:
                    st.json(test_result["result"])
                else:
                    st.error(f"❌ Error: {test_result.get('error', 'Unknown error')}")
            
            # Analysis Details
            if test_result["status"] == "success":
                st.markdown("---")
                st.markdown("**🔍 Analysis Details:**")
                
                analysis = test_result.get("analysis", {})
                for detail in analysis.get("details", []):
                    if detail.startswith("✅"):
                        st.success(detail)
                    elif detail.startswith("❌"):
                        st.error(detail)
                    elif detail.startswith("⚠️"):
                        st.warning(detail)
                    else:
                        st.info(detail)

def main():
    st.set_page_config(
        page_title="Agent Testing Dashboard",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 Agent Testing Dashboard")
    st.markdown("Comprehensive testing interface for all 13 essential agents")
    
    # Sidebar for agent selection
    st.sidebar.header("🎯 Agent Selection")
    
    agent_names = get_all_agent_names()
    selected_agent = st.sidebar.selectbox(
        "Choose Agent to Test:",
        agent_names,
        format_func=lambda x: get_agent_info(x)["name"]
    )
    
    # Display agent info
    agent_info = get_agent_info(selected_agent)
    st.sidebar.markdown(f"**Agent:** {agent_info['name']}")
    st.sidebar.markdown(f"**Description:** {agent_info['description']}")
    st.sidebar.markdown(f"**Test Cases:** {agent_info['test_count']}")
    
    # Main content area
    st.markdown("---")
    st.header(f"🧪 Testing: {agent_info['name']}")
    st.markdown(f"*{agent_info['description']}*")
    
    # Agent info summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Agent Type:** {agent_info['name']}")
    with col2:
        st.info(f"**Test Cases:** {agent_info['test_count']}")
    with col3:
        st.info(f"**Status:** Ready to Test")
    
    # Test Cases Section
    st.subheader("📋 Available Test Cases")
    
    # Get test cases for selected agent
    test_cases = get_agent_test_cases(selected_agent)
    
    if not test_cases:
        st.warning("No test cases available for this agent")
        return
    
    # Display test cases in a clean format
    for i, test_case in enumerate(test_cases["test_cases"]):
        with st.expander(f"📝 Test {i+1}: {test_case['name']}", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**📥 Test Input:**")
                st.json(test_case["input"])
            
            with col2:
                st.markdown("**🎯 Expected Results:**")
                if "expected_state" in test_case:
                    st.info(f"**Expected State:** {test_case['expected_state']}")
                elif "expected_type" in test_case:
                    st.info(f"**Expected Type:** {test_case['expected_type']}")
                elif "expected_fields" in test_case:
                    st.info(f"**Expected Fields:** {', '.join(test_case['expected_fields'])}")
                elif "expected" in test_case:
                    st.info(f"**Expected Result:** {test_case['expected']}")
                else:
                    st.info("No specific expectations defined")
    
    # Quick Actions Section
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    # Create action buttons in a clean layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Run All Tests", type="primary", use_container_width=True):
            run_all_tests(selected_agent)
    
    with col2:
        # Run single test
        test_options = [f"Test {i+1}: {tc['name']}" for i, tc in enumerate(test_cases["test_cases"])]
        selected_test = st.selectbox("Choose test:", test_options, key="single_test")
        
        if st.button("▶️ Run Selected Test", use_container_width=True):
            test_index = int(selected_test.split(":")[0].split()[1]) - 1
            run_single_test_case(selected_agent, test_cases["test_cases"][test_index], test_index)
    
    with col3:
        if st.button("🔧 Run Custom Test", use_container_width=True):
            st.session_state.show_custom_test = True
    
    # Custom Test Section
    if st.session_state.get("show_custom_test", False):
        st.markdown("---")
        st.subheader("🔧 Custom Test Input")
        
        # Create a clean custom test interface
        with st.container():
            st.markdown("**📝 Enter your custom test data:**")
            
            # Agent-specific custom input
            if selected_agent == "conversation_state_agent":
                col1, col2 = st.columns(2)
                with col1:
                    email_content = st.text_area("Email Content:", 
                        value="Hi, I need a quote for shipping 2 containers from Shanghai to Los Angeles. Can you help?",
                        height=150)
                with col2:
                    conversation_history = st.text_area("Conversation History:", 
                        value="Previous messages...",
                        height=150)
                
                custom_input = {
                    "email_content": email_content,
                    "conversation_history": conversation_history
                }
            
            elif selected_agent == "classification_agent":
                col1, col2 = st.columns(2)
                with col1:
                    email_content = st.text_area("Email Content:", 
                        value="Subject: Urgent - Need shipping quote\n\nHi, I need a quote for shipping 2 containers from Shanghai to Los Angeles. Can you help?",
                        height=150)
                with col2:
                    sender_info = st.text_input("Sender Info:", value="customer@example.com")
                
                custom_input = {
                    "email_content": email_content,
                    "sender_info": sender_info
                }
            
            elif selected_agent == "extraction_agent":
                col1, col2 = st.columns(2)
                with col1:
                    email_content = st.text_area("Email Content:", 
                        value="Hi, I need a quote for shipping 2 containers from Shanghai to Los Angeles. Container type: 40ft HC. Cargo: Electronics. Can you help?",
                        height=150)
                with col2:
                    email_type = st.selectbox("Email Type:", ["rate_request", "clarification", "confirmation"])
                
                custom_input = {
                    "email_content": email_content,
                    "email_type": email_type
                }
            
            elif selected_agent == "forwarder_detection_agent":
                col1, col2 = st.columns(2)
                with col1:
                    email_content = st.text_area("Email Content:", 
                        value="Hi, I'm a freight forwarder and I need a quote for my client. Can you help?",
                        height=150)
                with col2:
                    sender_info = st.text_input("Sender Info:", value="forwarder@example.com")
                
                custom_input = {
                    "email_content": email_content,
                    "sender_info": sender_info
                }
            
            else:
                # Generic custom input for other agents
                email_content = st.text_area("Email Content:", 
                    value="Hi, I need a quote for shipping containers. Can you help?",
                    height=150)
                
                custom_input = {
                    "email_content": email_content
                }
            
            # Action buttons
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write("")  # Spacer
            with col2:
                if st.button("🚀 Run Custom Test", type="primary", use_container_width=True):
                    # Initialize agent
                    with st.spinner("Initializing agent..."):
                        agent, error = initialize_agent(selected_agent)
                        if error:
                            st.error(f"Failed to initialize agent: {error}")
                            return
                    
                    # Run custom test
                    with st.spinner("Running custom test..."):
                        custom_test_case = {"input": custom_input, "name": "Custom Test"}
                        result = run_single_test(agent, custom_test_case, selected_agent)
                        result["test_name"] = "Custom Test"
                    
                    # Display result
                    display_test_results([result], selected_agent)
            
            with col3:
                if st.button("❌ Close", use_container_width=True):
                    st.session_state.show_custom_test = False
                    st.rerun()

def run_all_tests(agent_name: str):
    """Run all test cases for a specific agent."""
    st.subheader("🚀 Running All Tests")
    
    # Initialize agent
    with st.spinner("Initializing agent..."):
        agent, error = initialize_agent(agent_name)
        if error:
            st.error(f"Failed to initialize agent: {error}")
            return
    
    # Get test cases
    test_cases = get_agent_test_cases(agent_name)
    if not test_cases:
        st.warning("No test cases available")
        return
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    test_results = []
    
    # Run each test case
    for i, test_case in enumerate(test_cases["test_cases"]):
        status_text.text(f"Running test {i+1}/{len(test_cases['test_cases'])}: {test_case['name']}")
        
        # Run test
        result = run_single_test(agent, test_case, agent_name)
        result["test_name"] = test_case["name"]
        test_results.append(result)
        
        # Update progress
        progress = (i + 1) / len(test_cases["test_cases"])
        progress_bar.progress(progress)
    
    status_text.text("✅ All tests completed!")
    
    # Display results
    display_test_results(test_results, agent_name)
    
    # Store results in session state
    st.session_state.test_results = test_results
    st.session_state.current_agent = agent_name

def run_single_test_case(agent_name: str, test_case: Dict[str, Any], test_index: int):
    """Run a single test case."""
    st.subheader(f"▶️ Running Test {test_index + 1}")
    
    # Initialize agent
    with st.spinner("Initializing agent..."):
        agent, error = initialize_agent(agent_name)
        if error:
            st.error(f"Failed to initialize agent: {error}")
            return
    
    # Run test
    with st.spinner(f"Running test: {test_case['name']}"):
        result = run_single_test(agent, test_case, agent_name)
        result["test_name"] = test_case["name"]
    
    # Display result
    display_test_results([result], agent_name)

if __name__ == "__main__":
    main() 