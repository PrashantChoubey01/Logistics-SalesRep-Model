#!/usr/bin/env python3
"""
Data Flow Tracer
================

Trace how data flows through agents in a thread.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def trace_data_flow(thread_id: str, output_file: str = None):
    """Trace how data flows through agents"""
    threads_dir = project_root / "data" / "threads"
    thread_file = threads_dir / f"{thread_id}.json"
    
    if not thread_file.exists():
        print(f"❌ Thread not found: {thread_file}")
        return
    
    with open(thread_file, 'r') as f:
        thread = json.load(f)
    
    print("🔄 Data Flow Trace:")
    print("=" * 80)
    
    cumulative_data = {}
    flow_steps = []
    
    for i, email in enumerate(thread.get("email_chain", [])):
        print(f"\n📧 Step {i+1}: {email.get('subject', 'No subject')}")
        
        extracted = email.get("extracted_data", {})
        if extracted:
            print(f"   📥 Input to agents:")
            new_fields = {}
            
            for category, data in extracted.items():
                if isinstance(data, dict):
                    for key, value in data.items():
                        if value and str(value).strip():
                            new_fields[f"{category}.{key}"] = value
                            print(f"      - {category}.{key}: {value}")
                elif value:
                    new_fields[category] = data
                    print(f"      - {category}: {data}")
            
            # Merge with cumulative
            for key, value in new_fields.items():
                if value:
                    cumulative_data[key] = value
            
            print(f"   📤 Cumulative data: {len(cumulative_data)} fields")
            
            flow_steps.append({
                "step": i + 1,
                "new_fields": new_fields,
                "cumulative_count": len(cumulative_data)
            })
        else:
            print(f"   📥 No new data extracted")
            flow_steps.append({
                "step": i + 1,
                "new_fields": {},
                "cumulative_count": len(cumulative_data)
            })
    
    # Generate visualization
    if output_file:
        output_path = Path(output_file)
    else:
        output_path = project_root / "reports" / f"{thread_id}_dataflow.html"
        output_path.parent.mkdir(exist_ok=True)
    
    html = generate_dataflow_html(flow_steps, thread_id)
    output_path.write_text(html)
    
    print(f"\n✅ Data flow trace saved to: {output_path}")
    
    return flow_steps

def generate_dataflow_html(flow_steps: List[Dict[str, Any]], thread_id: str) -> str:
    """Generate HTML data flow visualization"""
    
    steps_html = ""
    for step in flow_steps:
        fields_list = ""
        for field, value in step["new_fields"].items():
            fields_list += f"<li><strong>{field}:</strong> {value}</li>"
        
        steps_html += f"""
        <div class="flow-step">
            <h3>Step {step['step']}</h3>
            <p><strong>New Fields:</strong> {len(step['new_fields'])}</p>
            <p><strong>Cumulative Fields:</strong> {step['cumulative_count']}</p>
            <ul>
                {fields_list if fields_list else "<li>No new fields</li>"}
            </ul>
        </div>
        """
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Data Flow Trace - {thread_id}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .flow-step {{
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #2196F3;
        }}
        .flow-step h3 {{
            margin-top: 0;
            color: #2196F3;
        }}
        .flow-step ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .flow-step li {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <h1>Data Flow Trace: {thread_id}</h1>
    {steps_html}
</body>
</html>
"""
    return html

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Trace data flow through agents")
    parser.add_argument("--thread-id", type=str, required=True, help="Thread ID")
    parser.add_argument("--output", type=str, help="Output HTML file")
    
    args = parser.parse_args()
    
    trace_data_flow(args.thread_id, args.output)

if __name__ == "__main__":
    main()

