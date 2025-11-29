#!/usr/bin/env python3
"""
Benchmark Runner
================

Runs offline evaluation against golden dataset using Evidently.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from eval.descriptors import grammar_score, word_count, mobile_friendly, hallucination_check, EmailQualityDescriptor

def load_golden_dataset(golden_file: Path) -> List[Dict[str, Any]]:
    """Load golden dataset from JSONL file"""
    emails = []
    
    if not golden_file.exists():
        print(f"⚠️  Golden dataset not found: {golden_file}")
        print(f"   Creating template file...")
        create_template_golden_dataset(golden_file)
        return []
    
    with open(golden_file, 'r') as f:
        for line in f:
            if line.strip():
                emails.append(json.loads(line))
    
    return emails

def create_template_golden_dataset(golden_file: Path):
    """Create template golden dataset file"""
    template = [
        {
            "thread_id": "golden_001",
            "email_type": "logistics_request",
            "input": {
                "sender": "customer@example.com",
                "subject": "Shipping Quote Request",
                "content": "Hello, I need a quote for shipping from Shanghai to Los Angeles. Container: 40HC, Quantity: 2."
            },
            "expected_output": {
                "response_type": "confirmation",
                "grammar_score": 95.0,
                "word_count": 150,
                "mobile_friendly": True,
                "hallucination": False
            }
        }
    ]
    
    golden_file.parent.mkdir(parents=True, exist_ok=True)
    with open(golden_file, 'w') as f:
        for item in template:
            f.write(json.dumps(item) + '\n')
    
    print(f"✅ Template created: {golden_file}")

def evaluate_email(email_body: str, thread_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Evaluate a single email"""
    descriptor = EmailQualityDescriptor()
    return descriptor.evaluate(email_body, thread_context)

def run_benchmark(golden_file: Path, current_emails: List[Dict[str, Any]] = None, output_dir: Path = None) -> Dict[str, Any]:
    """Run benchmark evaluation"""
    if output_dir is None:
        output_dir = project_root / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🔍 Loading golden dataset...")
    golden_emails = load_golden_dataset(golden_file)
    
    if not golden_emails:
        print("❌ No golden emails found. Please create golden dataset first.")
        return {"status": "error", "message": "No golden dataset"}
    
    print(f"✅ Loaded {len(golden_emails)} golden emails")
    
    # If current_emails not provided, use golden as current (for testing)
    if current_emails is None:
        current_emails = golden_emails
        print("⚠️  Using golden dataset as current (for testing)")
    
    print(f"📊 Evaluating {len(current_emails)} current emails...")
    
    # Evaluate current emails
    current_results = []
    for email in current_emails:
        email_body = email.get("output", {}).get("body", email.get("expected_output", {}).get("body", ""))
        if not email_body:
            continue
        
        result = evaluate_email(email_body, email.get("thread_context"))
        current_results.append({
            "thread_id": email.get("thread_id", "unknown"),
            "email_type": email.get("email_type", "unknown"),
            **result
        })
    
    # Evaluate golden emails
    golden_results = []
    for email in golden_emails:
        email_body = email.get("expected_output", {}).get("body", "")
        if not email_body:
            continue
        
        result = evaluate_email(email_body, email.get("thread_context"))
        golden_results.append({
            "thread_id": email.get("thread_id", "unknown"),
            "email_type": email.get("email_type", "unknown"),
            **result
        })
    
    # Convert to DataFrames
    current_df = pd.DataFrame(current_results)
    golden_df = pd.DataFrame(golden_results)
    
    # Calculate metrics
    metrics = {
        "grammar_score": {
            "current_avg": current_df["grammar_score"].mean() if "grammar_score" in current_df.columns else 0,
            "golden_avg": golden_df["grammar_score"].mean() if "grammar_score" in golden_df.columns else 0,
            "threshold": 95.0
        },
        "word_count": {
            "current_avg": current_df["word_count"].mean() if "word_count" in current_df.columns else 0,
            "golden_avg": golden_df["word_count"].mean() if "word_count" in golden_df.columns else 0,
            "threshold": 180
        },
        "mobile_friendly": {
            "current_pct": (current_df["mobile_friendly"].sum() / len(current_df) * 100) if "mobile_friendly" in current_df.columns else 0,
            "golden_pct": (golden_df["mobile_friendly"].sum() / len(golden_df) * 100) if "mobile_friendly" in golden_df.columns else 0,
            "threshold": 100.0
        },
        "hallucination": {
            "current_pct": (current_df["hallucination"].apply(lambda x: x.get("has_hallucination", False) if isinstance(x, dict) else False).sum() / len(current_df) * 100) if "hallucination" in current_df.columns else 0,
            "golden_pct": (golden_df["hallucination"].apply(lambda x: x.get("has_hallucination", False) if isinstance(x, dict) else False).sum() / len(golden_df) * 100) if "hallucination" in golden_df.columns else 0,
            "threshold": 0.0  # Should be 0%
        }
    }
    
    # Check if any metric fails
    failed_metrics = []
    
    if metrics["grammar_score"]["current_avg"] < metrics["grammar_score"]["threshold"]:
        failed_metrics.append("grammar_score")
    
    if metrics["word_count"]["current_avg"] > metrics["word_count"]["threshold"]:
        failed_metrics.append("word_count")
    
    if metrics["mobile_friendly"]["current_pct"] < metrics["mobile_friendly"]["threshold"]:
        failed_metrics.append("mobile_friendly")
    
    if metrics["hallucination"]["current_pct"] > metrics["hallucination"]["threshold"]:
        failed_metrics.append("hallucination")
    
    # Generate report
    report = {
        "status": "failed" if failed_metrics else "passed",
        "failed_metrics": failed_metrics,
        "metrics": metrics,
        "summary": {
            "total_emails": len(current_emails),
            "passed": len(failed_metrics) == 0,
            "failed_count": len(failed_metrics)
        }
    }
    
    # Save HTML report
    html_report = generate_html_report(report, current_df, golden_df)
    report_file = output_dir / "benchmark.html"
    report_file.write_text(html_report)
    
    print(f"\n📊 Benchmark Results:")
    print(f"   Status: {'✅ PASSED' if report['status'] == 'passed' else '❌ FAILED'}")
    print(f"   Failed Metrics: {failed_metrics if failed_metrics else 'None'}")
    print(f"   Grammar Score: {metrics['grammar_score']['current_avg']:.2f} (threshold: {metrics['grammar_score']['threshold']})")
    print(f"   Word Count: {metrics['word_count']['current_avg']:.1f} (threshold: {metrics['word_count']['threshold']})")
    print(f"   Mobile Friendly: {metrics['mobile_friendly']['current_pct']:.1f}% (threshold: {metrics['mobile_friendly']['threshold']}%)")
    print(f"   Hallucination: {metrics['hallucination']['current_pct']:.1f}% (threshold: {metrics['hallucination']['threshold']}%)")
    print(f"\n📄 Report saved: {report_file}")
    
    return report

def generate_html_report(report: Dict[str, Any], current_df: pd.DataFrame, golden_df: pd.DataFrame) -> str:
    """Generate HTML report"""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Benchmark Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>Benchmark Evaluation Report</h1>
    <p><strong>Status:</strong> <span class="{report['status']}">{report['status'].upper()}</span></p>
    <p><strong>Total Emails:</strong> {report['summary']['total_emails']}</p>
    <p><strong>Failed Metrics:</strong> {', '.join(report['failed_metrics']) if report['failed_metrics'] else 'None'}</p>
    
    <h2>Metrics Comparison</h2>
    <table>
        <tr>
            <th>Metric</th>
            <th>Current</th>
            <th>Golden</th>
            <th>Threshold</th>
            <th>Status</th>
        </tr>
        <tr>
            <td>Grammar Score</td>
            <td>{report['metrics']['grammar_score']['current_avg']:.2f}</td>
            <td>{report['metrics']['grammar_score']['golden_avg']:.2f}</td>
            <td>{report['metrics']['grammar_score']['threshold']}</td>
            <td class="{'passed' if report['metrics']['grammar_score']['current_avg'] >= report['metrics']['grammar_score']['threshold'] else 'failed'}">
                {'✅' if report['metrics']['grammar_score']['current_avg'] >= report['metrics']['grammar_score']['threshold'] else '❌'}
            </td>
        </tr>
        <tr>
            <td>Word Count (avg)</td>
            <td>{report['metrics']['word_count']['current_avg']:.1f}</td>
            <td>{report['metrics']['word_count']['golden_avg']:.1f}</td>
            <td>{report['metrics']['word_count']['threshold']}</td>
            <td class="{'passed' if report['metrics']['word_count']['current_avg'] <= report['metrics']['word_count']['threshold'] else 'failed'}">
                {'✅' if report['metrics']['word_count']['current_avg'] <= report['metrics']['word_count']['threshold'] else '❌'}
            </td>
        </tr>
        <tr>
            <td>Mobile Friendly (%)</td>
            <td>{report['metrics']['mobile_friendly']['current_pct']:.1f}%</td>
            <td>{report['metrics']['mobile_friendly']['golden_pct']:.1f}%</td>
            <td>{report['metrics']['mobile_friendly']['threshold']}%</td>
            <td class="{'passed' if report['metrics']['mobile_friendly']['current_pct'] >= report['metrics']['mobile_friendly']['threshold'] else 'failed'}">
                {'✅' if report['metrics']['mobile_friendly']['current_pct'] >= report['metrics']['mobile_friendly']['threshold'] else '❌'}
            </td>
        </tr>
        <tr>
            <td>Hallucination (%)</td>
            <td>{report['metrics']['hallucination']['current_pct']:.1f}%</td>
            <td>{report['metrics']['hallucination']['golden_pct']:.1f}%</td>
            <td>{report['metrics']['hallucination']['threshold']}%</td>
            <td class="{'passed' if report['metrics']['hallucination']['current_pct'] <= report['metrics']['hallucination']['threshold'] else 'failed'}">
                {'✅' if report['metrics']['hallucination']['current_pct'] <= report['metrics']['hallucination']['threshold'] else '❌'}
            </td>
        </tr>
    </table>
</body>
</html>
"""
    return html

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run benchmark evaluation")
    parser.add_argument("--golden", type=str, default="data/offline_eval/golden_thread.jsonl",
                       help="Path to golden dataset")
    parser.add_argument("--output", type=str, default="reports",
                       help="Output directory for reports")
    
    args = parser.parse_args()
    
    golden_file = project_root / args.golden
    output_dir = project_root / args.output
    
    report = run_benchmark(golden_file, output_dir=output_dir)
    
    # Exit with error code if failed
    if report.get("status") == "failed":
        sys.exit(1)

if __name__ == "__main__":
    main()

