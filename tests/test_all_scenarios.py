#!/usr/bin/env python3
"""
Comprehensive Test Script for All Email Scenarios

This script tests all possible email scenarios:
1. Customer Email Scenarios (Full Processing Path)
2. Forwarder Email Scenarios (Direct Acknowledgment)
3. Sales Person Email Scenarios (Direct Acknowledgment)
4. Edge Case Scenarios

Each test case will be executed and results stored in JSON format.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, List
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph_workflow_orchestrator import LangGraphWorkflowOrchestrator


class ComprehensiveScenarioTester:
    """Comprehensive tester for all email scenarios"""
    
    def __init__(self):
        self.orchestrator = LangGraphWorkflowOrchestrator()
        self.test_results = []
        self.output_dir = "tests/test_outputs"
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_test_scenarios(self) -> List[Dict[str, Any]]:
        """Define all test scenarios"""
        return [
            # 1. CUSTOMER EMAIL SCENARIOS
            {
                "id": "1.1",
                "category": "Customer Email",
                "subcategory": "Complete Quote Request (High Confidence)",
                "description": "Customer provides complete shipping details",
                "expected_path": "Full processing → Forwarder assignment",
                "email_data": {
                    "sender": "john.doe@company.com",
                    "subject": "FCL Shipping Quote Request - Shanghai to Los Angeles",
                    "content": "Hello,\n\nI need a quote for shipping a full container load from Shanghai, China to Los Angeles, USA.\n\nDetails:\n- Origin: Shanghai, China\n- Destination: Los Angeles, USA\n- Container Type: 40HC\n- Commodity: Electronics\n- Weight: 20,000 kg\n- Volume: 75 CBM\n- Ready Date: 2024-02-15\n- Incoterm: FOB\n\nPlease provide rates and transit time. Thank you.\n\nBest regards,\nJohn Doe\nLogistics Manager\nABC Electronics"
                }
            },
            {
                "id": "1.2",
                "category": "Customer Email",
                "subcategory": "Incomplete Quote Request (Missing Fields)",
                "description": "Customer provides minimal information",
                "expected_path": "Full processing → Clarification request",
                "email_data": {
                    "sender": "jane.smith@imports.com",
                    "subject": "Shipping quote needed",
                    "content": "Hi,\n\nI need shipping rates from China to USA. Can you help?\n\nThanks,\nJane"
                }
            },
            {
                "id": "1.3",
                "category": "Customer Email",
                "subcategory": "Customer Confirmation (Triggers Forwarder Assignment)",
                "description": "Customer confirms extracted details",
                "expected_path": "Full processing → Confirmation acknowledgment → Forwarder assignment",
                "email_data": {
                    "sender": "john.doe@company.com",
                    "subject": "Re: Shipping Quote - Confirmation",
                    "content": "Thank you for the quote. Yes, I confirm all the details:\n\n- Origin: Shanghai, China\n- Destination: Los Angeles, USA\n- Container Type: 40HC\n- Commodity: Electronics\n- Weight: 20,000 kg\n- Volume: 75 CBM\n- Ready Date: 2024-02-15\n- Incoterm: FOB\n\nPlease proceed with the booking. I also need transit time information.\n\nBest regards,\nJohn Doe"
                }
            },
            {
                "id": "1.4",
                "category": "Customer Email",
                "subcategory": "Customer Clarification Response",
                "description": "Customer provides missing information",
                "expected_path": "Full processing → Confirmation request",
                "email_data": {
                    "sender": "jane.smith@imports.com",
                    "subject": "Re: Clarification Request",
                    "content": "Thank you for asking. Here are the additional details:\n\n- Origin: Guangzhou, China\n- Destination: New York, USA\n- Container Type: 20GP\n- Commodity: Textiles\n- Weight: 15,000 kg\n- Volume: 30 CBM\n- Ready Date: 2024-02-20\n- Incoterm: CIF\n\nPlease provide updated rates.\n\nRegards,\nJane Smith"
                }
            },
            {
                "id": "1.5",
                "category": "Customer Email",
                "subcategory": "Vague Customer Response",
                "description": "Customer provides unclear information",
                "expected_path": "Full processing → Clarification request",
                "email_data": {
                    "sender": "customer@vague.com",
                    "subject": "Re: Your inquiry",
                    "content": "Hi,\n\nYes, that sounds good. Let me know when you have more information.\n\nThanks"
                }
            },
            {
                "id": "1.6",
                "category": "Customer Email",
                "subcategory": "Customer Follow-up Question",
                "description": "Customer asks follow-up questions",
                "expected_path": "Full processing → Acknowledgment",
                "email_data": {
                    "sender": "john.doe@company.com",
                    "subject": "Re: Shipping Quote - Follow up",
                    "content": "Thank you for the quote. I have a few questions:\n\n1. What is the exact transit time?\n2. Are there any additional charges?\n3. Can you provide tracking information?\n4. What documents do I need to prepare?\n\nPlease let me know.\n\nBest regards,\nJohn Doe"
                }
            },
            {
                "id": "1.7",
                "category": "Customer Email",
                "subcategory": "Customer Change Request",
                "description": "Customer requests changes to shipment",
                "expected_path": "Full processing → Clarification request",
                "email_data": {
                    "sender": "jane.smith@imports.com",
                    "subject": "Re: Shipping Quote - Change Request",
                    "content": "Hello,\n\nI need to change the shipment details:\n\n- Change container type from 40HC to 20GP\n- Change destination from Los Angeles to Seattle\n- Change ready date to 2024-02-25\n\nPlease provide updated rates for these changes.\n\nRegards,\nJane Smith"
                }
            },
            {
                "id": "1.8",
                "category": "Customer Email",
                "subcategory": "Customer Complaint",
                "description": "Customer reports issues",
                "expected_path": "Full processing → Acknowledgment → Escalation",
                "email_data": {
                    "sender": "angry.customer@company.com",
                    "subject": "Complaint - Delayed Shipment",
                    "content": "I am very disappointed with your service. My shipment was supposed to arrive last week but it's still delayed. This is causing significant problems for my business.\n\nPlease provide an immediate update on the status and compensation for the delay.\n\nRegards,\nFrustrated Customer"
                }
            },
            {
                "id": "1.9",
                "category": "Customer Email",
                "subcategory": "Urgent Customer Request",
                "description": "Customer has urgent requirements",
                "expected_path": "Full processing → Acknowledgment → Escalation",
                "email_data": {
                    "sender": "urgent@company.com",
                    "subject": "URGENT - Need immediate shipping quote",
                    "content": "URGENT REQUEST\n\nI need an immediate quote for shipping from Shenzhen to Miami. This is extremely urgent and I need rates within the next hour.\n\n- Origin: Shenzhen, China\n- Destination: Miami, USA\n- Container Type: 40HC\n- Commodity: Medical Supplies\n- Weight: 25,000 kg\n- Volume: 80 CBM\n- Ready Date: Tomorrow\n- Incoterm: EXW\n\nPlease respond immediately.\n\nBest regards,\nUrgent Customer"
                }
            },
            {
                "id": "1.10",
                "category": "Customer Email",
                "subcategory": "Non-Logistics Customer Query",
                "description": "Customer asks about non-logistics topics",
                "expected_path": "Full processing → Acknowledgment",
                "email_data": {
                    "sender": "billing@company.com",
                    "subject": "Billing Question",
                    "content": "Hello,\n\nI have a question about my recent invoice #INV-2024-001. There seems to be an error in the calculation.\n\nCan you please review and correct it?\n\nThanks,\nBilling Department"
                }
            },
            
            # 2. FORWARDER EMAIL SCENARIOS
            {
                "id": "2.1",
                "category": "Forwarder Email",
                "subcategory": "Forwarder Rate Quote",
                "description": "Forwarder provides rate quote",
                "expected_path": "Direct acknowledgment",
                "email_data": {
                    "sender": "dhl.global.forwarding@logistics.com",
                    "subject": "Rate Quote - Shanghai to Los Angeles",
                    "content": "Dear Searates Team,\n\nThank you for your rate request for the shipment from Shanghai to Los Angeles.\n\nPlease find our competitive rates below:\n\n- 40HC: $3,200 USD\n- Transit Time: 18 days\n- Valid until: 2024-02-28\n\nPlease let us know if you need any additional information.\n\nBest regards,\nDHL Global Forwarding Team"
                }
            },
            {
                "id": "2.2",
                "category": "Forwarder Email",
                "subcategory": "Forwarder Clarification Request",
                "description": "Forwarder asks for clarification",
                "expected_path": "Direct acknowledgment",
                "email_data": {
                    "sender": "kuehne..nagel@logistics.com",
                    "subject": "Clarification Request - Shipment Details",
                    "content": "Hello Searates,\n\nRegarding your rate request for the China to USA shipment, we need some clarification:\n\n1. What is the exact commodity description?\n2. Are there any special handling requirements?\n3. What is the preferred shipping line?\n\nPlease provide these details so we can give you the most accurate quote.\n\nRegards,\nKuehne + Nagel Team"
                }
            },
            {
                "id": "2.3",
                "category": "Forwarder Email",
                "subcategory": "Forwarder Booking Confirmation",
                "description": "Forwarder confirms booking",
                "expected_path": "Direct acknowledgment",
                "email_data": {
                    "sender": "db.schenker@logistics.com",
                    "subject": "Booking Confirmation - Booking #BK-2024-001",
                    "content": "Dear Searates,\n\nWe are pleased to confirm your booking for the shipment from Shanghai to Los Angeles.\n\nBooking Details:\n- Booking Number: BK-2024-001\n- Vessel: MSC OSCAR\n- ETD: 2024-02-15\n- ETA: 2024-03-05\n- Container: TCLU1234567\n\nPlease find attached the booking confirmation.\n\nBest regards,\nDB Schenker Team"
                }
            },
            {
                "id": "2.4",
                "category": "Forwarder Email",
                "subcategory": "Forwarder Problem Report",
                "description": "Forwarder reports issues",
                "expected_path": "Direct acknowledgment",
                "email_data": {
                    "sender": "dhl.global.forwarding@logistics.com",
                    "subject": "Issue Report - Container Delay",
                    "content": "Dear Searates,\n\nWe regret to inform you that there has been a delay with your container TCLU1234567.\n\nThe vessel has been delayed due to weather conditions and the new ETA is 2024-03-10.\n\nWe apologize for any inconvenience this may cause.\n\nBest regards,\nDHL Global Forwarding Team"
                }
            },
            {
                "id": "2.5",
                "category": "Forwarder Email",
                "subcategory": "Forwarder General Acknowledgment",
                "description": "Forwarder acknowledges request",
                "expected_path": "Direct acknowledgment",
                "email_data": {
                    "sender": "kuehne..nagel@logistics.com",
                    "subject": "Acknowledgment - Rate Request Received",
                    "content": "Dear Searates,\n\nThank you for your rate request. We have received your inquiry and our team is working on providing you with competitive rates.\n\nYou can expect our response within 24 hours.\n\nBest regards,\nKuehne + Nagel Team"
                }
            },
            
            # 3. SALES PERSON EMAIL SCENARIOS
            {
                "id": "3.1",
                "category": "Sales Person Email",
                "subcategory": "Sales Person Inquiry",
                "description": "Sales person asks for information",
                "expected_path": "Direct acknowledgment",
                "email_data": {
                    "sender": "sarah.johnson@searates.com",
                    "subject": "Inquiry - Customer Feedback",
                    "content": "Hi Team,\n\nI received feedback from a customer about our recent shipment. They mentioned some delays in the process.\n\nCan you please check the status of booking #BK-2024-001 and provide me with an update?\n\nThanks,\nSarah Johnson\nDigital Sales Specialist"
                }
            },
            {
                "id": "3.2",
                "category": "Sales Person Email",
                "subcategory": "Sales Person Update",
                "description": "Sales person provides update",
                "expected_path": "Direct acknowledgment",
                "email_data": {
                    "sender": "michael.chen@searates.com",
                    "subject": "Update - New Customer Onboarding",
                    "content": "Hello Team,\n\nI wanted to update you about the new customer we're onboarding - ABC Electronics.\n\nThey have confirmed their first shipment and I've assigned them to our Asia-Pacific route.\n\nPlease ensure they receive priority support.\n\nBest regards,\nMichael Chen\nDigital Sales Specialist"
                }
            },
            {
                "id": "3.3",
                "category": "Sales Person Email",
                "subcategory": "Sales Person Acknowledgment",
                "description": "Sales person acknowledges action",
                "expected_path": "Direct acknowledgment",
                "email_data": {
                    "sender": "emily.rodriguez@searates.com",
                    "subject": "Acknowledgment - Rate Request Processed",
                    "content": "Hi,\n\nI wanted to acknowledge that I've processed the rate request for the Shanghai to Los Angeles shipment.\n\nThe forwarder has been assigned and the rate request email has been sent.\n\nI'll keep you updated on the response.\n\nRegards,\nEmily Rodriguez\nDigital Sales Specialist"
                }
            },
            
            # 4. EDGE CASE SCENARIOS
            {
                "id": "4.1",
                "category": "Edge Case",
                "subcategory": "Confusing/Unclear Email",
                "description": "Email is unclear or confusing",
                "expected_path": "Escalation needed",
                "email_data": {
                    "sender": "confused@company.com",
                    "subject": "Help needed",
                    "content": "Hi,\n\nI don't know what to do. Can you help me?\n\nThanks"
                }
            },
            {
                "id": "4.2",
                "category": "Edge Case",
                "subcategory": "Escalation Needed",
                "description": "Complex requirements need escalation",
                "expected_path": "Escalation needed",
                "email_data": {
                    "sender": "complex@company.com",
                    "subject": "Complex Shipment Requirements",
                    "content": "Hello,\n\nWe have a very complex shipment that requires special handling:\n\n- Hazardous materials\n- Temperature controlled\n- Oversized cargo\n- Multiple destinations\n- Special permits required\n\nThis is beyond our standard procedures and needs expert attention.\n\nPlease escalate to senior management.\n\nRegards,\nComplex Customer"
                }
            },
            {
                "id": "4.3",
                "category": "Edge Case",
                "subcategory": "Thread Continuation",
                "description": "Email continues existing conversation",
                "expected_path": "Full processing",
                "email_data": {
                    "sender": "john.doe@company.com",
                    "subject": "Re: Re: Re: Shipping Quote - Additional Questions",
                    "content": "Thank you for the clarification. I have a few more questions:\n\n1. What about insurance coverage?\n2. Can you provide door-to-door service?\n3. What are the payment terms?\n\nPlease let me know.\n\nBest regards,\nJohn Doe"
                }
            },
            {
                "id": "4.4",
                "category": "Edge Case",
                "subcategory": "New Thread Start",
                "description": "New customer starts conversation",
                "expected_path": "Full processing",
                "email_data": {
                    "sender": "new.customer@company.com",
                    "subject": "First Time Customer - Shipping Inquiry",
                    "content": "Hello,\n\nThis is our first time working with Searates. We're looking for a reliable shipping partner for our regular shipments from China to Europe.\n\nCan you tell us more about your services and provide a sample quote?\n\nWe typically ship:\n- 2-3 containers per month\n- Electronics and textiles\n- From Shenzhen to Rotterdam\n\nLooking forward to your response.\n\nBest regards,\nNew Customer Team"
                }
            }
        ]
    
    async def run_single_test(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test scenario"""
        test_id = scenario["id"]
        category = scenario["category"]
        subcategory = scenario["subcategory"]
        
        print(f"\n{'='*80}")
        print(f"🧪 TESTING: {test_id} - {category} - {subcategory}")
        print(f"📝 Description: {scenario['description']}")
        print(f"🎯 Expected Path: {scenario['expected_path']}")
        print(f"{'='*80}")
        
        try:
            # Run the workflow
            start_time = datetime.now()
            result = await self.orchestrator.process_email(scenario["email_data"])
            end_time = datetime.now()
            
            # Calculate execution time
            execution_time = (end_time - start_time).total_seconds()
            
            # Analyze the result
            workflow_result = result.get("result", {})
            workflow_history = workflow_result.get("workflow_history", [])
            final_response = workflow_result.get("final_response", {})
            
            # Determine actual path taken
            actual_path = " → ".join(workflow_history) if workflow_history else "No path recorded"
            
            # Check if expected outcome was achieved
            success = self.analyze_success(scenario, result)
            
            test_result = {
                "test_id": test_id,
                "category": category,
                "subcategory": subcategory,
                "description": scenario["description"],
                "expected_path": scenario["expected_path"],
                "actual_path": actual_path,
                "success": success,
                "execution_time_seconds": execution_time,
                "input_email": scenario["email_data"],
                "workflow_result": result,
                "timestamp": datetime.now().isoformat()
            }
            
            # Print summary
            print(f"✅ Test completed in {execution_time:.2f} seconds")
            print(f"🎯 Success: {success}")
            print(f"📊 Actual Path: {actual_path}")
            
            return test_result
            
        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}")
            return {
                "test_id": test_id,
                "category": category,
                "subcategory": subcategory,
                "description": scenario["description"],
                "expected_path": scenario["expected_path"],
                "actual_path": "ERROR",
                "success": False,
                "execution_time_seconds": 0,
                "input_email": scenario["email_data"],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_success(self, scenario: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """Analyze if the test achieved expected outcome"""
        category = scenario["category"]
        expected_path = scenario["expected_path"]
        workflow_result = result.get("result", {})
        workflow_history = workflow_result.get("workflow_history", [])
        
        if category == "Customer Email":
            # Customer emails should go through full processing
            expected_nodes = ["classify_email", "conversation_state", "analyze_thread", "extract_information"]
            return all(node in workflow_history for node in expected_nodes)
        
        elif category == "Forwarder Email":
            # Forwarder emails should get direct acknowledgment
            return "generate_acknowledgment_response" in workflow_history
        
        elif category == "Sales Person Email":
            # Sales person emails should get direct acknowledgment
            return "generate_acknowledgment_response" in workflow_history
        
        elif category == "Edge Case":
            if "Escalation needed" in expected_path:
                return "check_escalation" in workflow_history
            else:
                # Other edge cases should go through normal processing
                return "classify_email" in workflow_history
        
        return False
    
    async def run_all_tests(self):
        """Run all test scenarios"""
        print("🚀 Starting Comprehensive Scenario Testing")
        print(f"📁 Output directory: {self.output_dir}")
        
        scenarios = self.get_test_scenarios()
        total_scenarios = len(scenarios)
        
        print(f"📊 Total scenarios to test: {total_scenarios}")
        
        # Run tests by category
        categories = ["Customer Email", "Forwarder Email", "Sales Person Email", "Edge Case"]
        
        for category in categories:
            category_scenarios = [s for s in scenarios if s["category"] == category]
            print(f"\n{'='*60}")
            print(f"📋 TESTING CATEGORY: {category} ({len(category_scenarios)} scenarios)")
            print(f"{'='*60}")
            
            for scenario in category_scenarios:
                result = await self.run_single_test(scenario)
                self.test_results.append(result)
                
                # Save individual test result
                filename = f"test_{scenario['id'].replace('.', '_')}_{category.replace(' ', '_').lower()}.json"
                filepath = os.path.join(self.output_dir, filename)
                
                with open(filepath, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                
                print(f"💾 Saved result to: {filepath}")
        
        # Generate summary report
        await self.generate_summary_report()
    
    async def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        print(f"\n{'='*80}")
        print("📊 GENERATING SUMMARY REPORT")
        print(f"{'='*80}")
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.get("success", False))
        failed_tests = total_tests - successful_tests
        
        # Category-wise breakdown
        category_stats = {}
        for result in self.test_results:
            category = result["category"]
            if category not in category_stats:
                category_stats[category] = {"total": 0, "success": 0, "failed": 0}
            
            category_stats[category]["total"] += 1
            if result.get("success", False):
                category_stats[category]["success"] += 1
            else:
                category_stats[category]["failed"] += 1
        
        # Generate summary
        summary = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
                "timestamp": datetime.now().isoformat()
            },
            "category_breakdown": category_stats,
            "detailed_results": self.test_results
        }
        
        # Save summary report
        summary_filepath = os.path.join(self.output_dir, "comprehensive_test_summary.json")
        with open(summary_filepath, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        # Print summary
        print(f"📈 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {successful_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {summary['test_summary']['success_rate']:.1f}%")
        
        print(f"\n📋 CATEGORY BREAKDOWN:")
        for category, stats in category_stats.items():
            success_rate = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"   {category}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        print(f"\n💾 Summary saved to: {summary_filepath}")
        
        # Save individual test results
        all_results_filepath = os.path.join(self.output_dir, "all_test_results.json")
        with open(all_results_filepath, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"💾 All results saved to: {all_results_filepath}")
        
        return summary


async def main():
    """Main function to run comprehensive testing"""
    tester = ComprehensiveScenarioTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    print("🧪 Comprehensive Scenario Testing Script")
    print("=" * 50)
    
    # Run the tests
    asyncio.run(main())
    
    print("\n🎉 Testing completed!")
    print("📁 Check the 'tests/test_outputs' directory for detailed results.") 