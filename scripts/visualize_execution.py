#!/usr/bin/env python3
"""
Execution Visualizer
====================

Creates timeline visualization of agent execution in a thread.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def visualize_thread_execution(thread_id: str, output_file: str = None):
    """Create timeline visualization of agent execution"""
    threads_dir = project_root / "data" / "threads"
    thread_file = threads_dir / f"{thread_id}.json"
    
    if not thread_file.exists():
        print(f"❌ Thread not found: {thread_file}")
        return
    
    with open(thread_file, 'r') as f:
        thread = json.load(f)
    
    print("📊 Execution Timeline:")
    print("=" * 80)
    
    timeline = []
    
    for i, email in enumerate(thread.get("email_chain", [])):
        step_info = {
            "step": i + 1,
            "timestamp": email.get("timestamp", "unknown"),
            "sender": email.get("sender", "unknown"),
            "subject": email.get("subject", "No subject"),
            "direction": email.get("direction", "unknown"),
            "has_extraction": bool(email.get("extracted_data")),
            "has_response": bool(email.get("bot_response")),
            "workflow_id": email.get("workflow_id", "unknown")
        }
        
        timeline.append(step_info)
        
        print(f"\n📧 Step {step_info['step']}: {step_info['subject']}")
        print(f"   Timestamp: {step_info['timestamp']}")
        print(f"   Sender: {step_info['sender']} ({step_info['direction']})")
        
        if step_info['has_extraction']:
            extracted = email.get("extracted_data", {})
            print(f"   ✅ Extracted: {len(extracted)} categories")
            if "shipment_details" in extracted:
                shipment = extracted["shipment_details"]
                if shipment.get("origin"):
                    print(f"      - Origin: {shipment['origin']}")
                if shipment.get("destination"):
                    print(f"      - Destination: {shipment['destination']}")
        
        if step_info['has_response']:
            response = email.get("bot_response", {})
            response_type = response.get("response_type", "unknown")
            print(f"   📤 Response Type: {response_type}")
        
        if step_info['workflow_id'] != "unknown":
            print(f"   🔄 Workflow: {step_info['workflow_id']}")
    
    # Generate HTML visualization
    html = generate_html_timeline(timeline, thread_id)
    
    if output_file:
        output_path = Path(output_file)
        output_path.write_text(html)
        print(f"\n✅ Timeline saved to: {output_path}")
    else:
        output_path = project_root / "reports" / f"{thread_id}_timeline.html"
        output_path.parent.mkdir(exist_ok=True)
        output_path.write_text(html)
        print(f"\n✅ Timeline saved to: {output_path}")
    
    return timeline

def generate_html_timeline(timeline: List[Dict[str, Any]], thread_id: str) -> str:
    """Generate HTML timeline visualization"""
    
    timeline_html = ""
    for step in timeline:
        color = "#4CAF50" if step['direction'] == 'inbound' else "#2196F3"
        icon = "📥" if step['direction'] == 'inbound' else "📤"
        
        timeline_html += f"""
        <div class="timeline-item" style="border-left-color: {color};">
            <div class="timeline-marker" style="background-color: {color};">
                {icon}
            </div>
            <div class="timeline-content">
                <h3>Step {step['step']}: {step['subject']}</h3>
                <p><strong>From:</strong> {step['sender']}</p>
                <p><strong>Time:</strong> {step['timestamp']}</p>
                <p><strong>Direction:</strong> {step['direction']}</p>
                {f"<p>✅ Extracted data available</p>" if step['has_extraction'] else ""}
                {f"<p>📤 Response generated</p>" if step['has_response'] else ""}
            </div>
        </div>
        """
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Execution Timeline - {thread_id}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .timeline {{
            position: relative;
            padding: 20px 0;
        }}
        .timeline-item {{
            position: relative;
            padding-left: 40px;
            margin-bottom: 30px;
            border-left: 3px solid #ddd;
        }}
        .timeline-marker {{
            position: absolute;
            left: -12px;
            top: 0;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
        }}
        .timeline-content {{
            background: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .timeline-content h3 {{
            margin-top: 0;
            color: #333;
        }}
        .timeline-content p {{
            margin: 5px 0;
            color: #666;
        }}
    </style>
</head>
<body>
    <h1>Execution Timeline: {thread_id}</h1>
    <div class="timeline">
        {timeline_html}
    </div>
</body>
</html>
"""
    return html

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Visualize thread execution timeline")
    parser.add_argument("--thread-id", type=str, required=True, help="Thread ID to visualize")
    parser.add_argument("--output", type=str, help="Output HTML file")
    
    args = parser.parse_args()
    
    visualize_thread_execution(args.thread_id, args.output)

if __name__ == "__main__":
    main()

