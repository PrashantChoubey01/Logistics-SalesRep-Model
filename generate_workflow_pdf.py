#!/usr/bin/env python3
"""
Generate PDF from workflow diagram HTML
Requires: selenium, pillow, reportlab
Install: pip install selenium pillow reportlab webdriver-manager
"""

import os
import time
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    from PIL import Image
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.lib.utils import ImageReader
except ImportError as e:
    print(f"Missing required package: {e}")
    print("\nPlease install required packages:")
    print("pip install selenium pillow reportlab webdriver-manager")
    exit(1)


def generate_pdf_from_html(html_file, output_pdf):
    """Generate PDF from HTML file using headless Chrome"""
    
    print("🚀 Starting PDF generation...")
    
    # Get absolute path
    html_path = Path(html_file).resolve()
    if not html_path.exists():
        print(f"❌ Error: HTML file not found: {html_path}")
        return False
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,4500')
    
    try:
        # Initialize Chrome driver
        print("📦 Initializing Chrome driver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Load HTML file
        print(f"📄 Loading HTML file: {html_path}")
        driver.get(f'file://{html_path}')
        
        # Wait for canvas to render
        print("⏳ Waiting for canvas to render...")
        time.sleep(3)
        
        # Get canvas element and take screenshot
        print("📸 Taking screenshot...")
        canvas = driver.find_element('id', 'workflow-canvas')
        
        # Save screenshot
        temp_png = 'temp_workflow_screenshot.png'
        canvas.screenshot(temp_png)
        
        driver.quit()
        print("✅ Screenshot captured successfully")
        
        # Convert PNG to PDF
        print("📝 Converting to PDF...")
        img = Image.open(temp_png)
        img_width, img_height = img.size
        
        # Calculate PDF dimensions (maintain aspect ratio)
        # Use custom page size to fit the entire diagram
        pdf_width = 8.5 * 72  # 8.5 inches in points
        pdf_height = (img_height / img_width) * pdf_width
        
        # Create PDF
        c = pdf_canvas.Canvas(output_pdf, pagesize=(pdf_width, pdf_height))
        
        # Add image to PDF
        c.drawImage(ImageReader(temp_png), 0, 0, width=pdf_width, height=pdf_height)
        
        # Add metadata
        c.setTitle("SeaRates Logistics AI - Workflow Diagram")
        c.setAuthor("SeaRates by DP World")
        c.setSubject("LangGraph Multi-Agent Email Workflow Architecture")
        
        c.save()
        
        # Clean up temp file
        os.remove(temp_png)
        
        print(f"✅ PDF generated successfully: {output_pdf}")
        return True
        
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    script_dir = Path(__file__).parent
    html_file = script_dir / 'workflow_diagram.html'
    output_pdf = script_dir / 'searates-workflow-diagram.pdf'
    
    print("=" * 60)
    print("SeaRates Workflow Diagram - PDF Generator")
    print("=" * 60)
    print()
    
    success = generate_pdf_from_html(html_file, output_pdf)
    
    print()
    print("=" * 60)
    if success:
        print("✅ PDF generation completed successfully!")
        print(f"📄 Output: {output_pdf}")
    else:
        print("❌ PDF generation failed")
    print("=" * 60)


if __name__ == '__main__':
    main()
