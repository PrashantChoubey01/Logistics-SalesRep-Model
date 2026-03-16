#!/usr/bin/env python3
"""
Simple PDF generator using browser automation
This script opens the HTML in your default browser and guides you to save as PDF
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Open HTML and provide instructions for PDF generation"""
    
    script_dir = Path(__file__).parent
    html_file = script_dir / 'workflow_diagram.html'
    
    if not html_file.exists():
        print(f"❌ Error: HTML file not found: {html_file}")
        return
    
    print("=" * 70)
    print("SeaRates Workflow Diagram - PDF Generator")
    print("=" * 70)
    print()
    print("📄 Opening workflow diagram in your browser...")
    print()
    
    # Open HTML file in default browser
    if sys.platform == 'darwin':  # macOS
        subprocess.run(['open', str(html_file)])
    elif sys.platform == 'win32':  # Windows
        subprocess.run(['start', str(html_file)], shell=True)
    else:  # Linux
        subprocess.run(['xdg-open', str(html_file)])
    
    print("✅ Browser opened!")
    print()
    print("📝 To save as PDF:")
    print()
    print("   Option 1: Use the 'Print/Save PDF' button")
    print("   ─────────────────────────────────────────")
    print("   1. Click the 'Print/Save PDF' button at the bottom right")
    print("   2. In the print dialog, select 'Save as PDF'")
    print("   3. Choose location and save")
    print()
    print("   Option 2: Use browser menu (Recommended)")
    print("   ─────────────────────────────────────────")
    print("   1. Press Cmd+P (Mac) or Ctrl+P (Windows/Linux)")
    print("   2. Select 'Save as PDF' as the destination")
    print("   3. Adjust settings:")
    print("      • Layout: Portrait")
    print("      • Paper size: A4 or Letter")
    print("      • Margins: Default or Minimum")
    print("      • Background graphics: ON (important!)")
    print("   4. Click 'Save'")
    print()
    print("   Option 3: Use the 'Generate PDF' button")
    print("   ─────────────────────────────────────────")
    print("   1. Click the 'Generate PDF' button")
    print("   2. Wait for the PDF to be generated")
    print("   3. The PDF will download automatically")
    print()
    print("=" * 70)


if __name__ == '__main__':
    main()
