"""
Test script for PDF policy summarization feature.

This script tests:
1. Backend service initialization
2. PDF text extraction
3. AI summarization with BART model
4. Key points extraction
"""

import sys
import os
from io import BytesIO

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.pdf_policy_service import pdf_policy_analyzer

def create_sample_pdf():
    """Create a simple test PDF with sample policy text."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        # Add sample policy text
        policy_text = """
        URBAN GREEN SPACES DEVELOPMENT INITIATIVE
        
        Executive Summary:
        This policy proposes the creation of 15 new public parks across the city over the next 3 years.
        The initiative allocates a $50 million budget for land acquisition and development.
        Community involvement programs will be established for park design and maintenance.
        
        Key Objectives:
        1. Increase green space accessibility for all residents
        2. Improve air quality and urban biodiversity
        3. Create community gathering spaces
        4. Promote physical activity and mental health
        
        Implementation Timeline:
        Phase 1 (Year 1): Land acquisition and community consultation
        Phase 2 (Year 2): Design and initial construction
        Phase 3 (Year 3): Completion and maintenance programs
        
        Expected Outcomes:
        - 20% increase in green space per capita
        - Improved community satisfaction scores
        - Enhanced property values in surrounding areas
        - Reduction in urban heat island effect
        """
        
        # Write text to PDF
        y = 750
        for line in policy_text.split('\n'):
            c.drawString(50, y, line.strip())
            y -= 20
            if y < 50:
                c.showPage()
                y = 750
        
        c.save()
        buffer.seek(0)
        return buffer
        
    except ImportError:
        print("⚠️ reportlab not installed. Skipping PDF creation.")
        print("Install with: pip install reportlab")
        return None

def test_model_initialization():
    """Test if the BART model initializes correctly."""
    print("\n" + "="*60)
    print("TEST 1: Model Initialization")
    print("="*60)
    
    try:
        # Initialize models (this loads BART)
        pdf_policy_analyzer.initialize_models()
        print("✅ BART model initialized successfully")
        print(f"   - Tokenizer: {type(pdf_policy_analyzer.tokenizer).__name__}")
        print(f"   - Model: {type(pdf_policy_analyzer.model).__name__}")
        return True
    except Exception as e:
        print(f"❌ Model initialization failed: {e}")
        return False

def test_text_summarization():
    """Test text summarization with a sample policy text."""
    print("\n" + "="*60)
    print("TEST 2: Text Summarization")
    print("="*60)
    
    sample_text = """
    The Urban Green Spaces Development Initiative proposes the creation of 15 new public parks 
    across the city over the next 3 years. The initiative allocates a $50 million budget for 
    land acquisition and development. Community involvement programs will be established for 
    park design and maintenance. Key objectives include increasing green space accessibility 
    for all residents, improving air quality and urban biodiversity, creating community gathering 
    spaces, and promoting physical activity and mental health. The implementation will occur in 
    three phases: Year 1 focuses on land acquisition and community consultation, Year 2 on design 
    and initial construction, and Year 3 on completion and maintenance programs. Expected outcomes 
    include a 20% increase in green space per capita, improved community satisfaction scores, 
    enhanced property values in surrounding areas, and reduction in urban heat island effect.
    """
    
    try:
        print(f"📝 Input text: {len(sample_text.split())} words")
        
        result = pdf_policy_analyzer.generate_summary(sample_text)
        
        if result and 'summary' in result:
            print("✅ Summarization successful")
            print(f"\n📋 Summary ({result.get('method', 'unknown')} method):")
            print("-" * 60)
            print(result['summary'])
            print("-" * 60)
            
            if 'key_points' in result and result['key_points']:
                print(f"\n🎯 Key Points ({len(result['key_points'])} extracted):")
                for i, point in enumerate(result['key_points'], 1):
                    # Truncate long key points for display
                    point_display = point[:100] + "..." if len(point) > 100 else point
                    print(f"   {i}. {point_display}")
            
            if 'metadata' in result:
                print(f"\n📊 Metadata:")
                for key, value in result['metadata'].items():
                    print(f"   - {key}: {value}")
            
            print(f"\n   - Confidence: {result.get('confidence', 'N/A')}")
            
            return True
        else:
            print(f"❌ Summarization failed: No summary in result")
            return False
            
    except Exception as e:
        print(f"❌ Summarization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pdf_analysis():
    """Test full PDF analysis pipeline."""
    print("\n" + "="*60)
    print("TEST 3: PDF Analysis Pipeline")
    print("="*60)
    
    # Create sample PDF
    pdf_buffer = create_sample_pdf()
    
    if pdf_buffer is None:
        print("⚠️ Skipping PDF test (reportlab not available)")
        return None
    
    try:
        print("📄 Created sample PDF")
        
        # Analyze PDF
        result = pdf_policy_analyzer.analyze_policy_pdf(pdf_buffer, "sample_policy.pdf")
        
        if result['success']:
            print("✅ PDF analysis successful")
            
            print(f"\n📊 Extraction Metadata:")
            metadata = result['extraction_metadata']
            print(f"   - Pages: {metadata['total_pages']}")
            print(f"   - Words: {metadata['word_count']}")
            print(f"   - Extraction method: {metadata['extraction_method']}")
            
            print(f"\n📋 Summary:")
            print("-" * 60)
            print(result['summary']['summary'])
            print("-" * 60)
            
            if result['summary'].get('key_points'):
                print(f"\n🎯 Key Points:")
                for i, point in enumerate(result['summary']['key_points'], 1):
                    print(f"   {i}. {point}")
            
            return True
        else:
            print(f"❌ PDF analysis failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ PDF analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("="*60)
    print("PDF POLICY SUMMARIZATION TEST SUITE")
    print("="*60)
    print("Testing BART-based AI summarization for policy documents")
    
    results = {
        'model_init': test_model_initialization(),
        'text_summary': test_text_summarization(),
        'pdf_analysis': test_pdf_analysis()
    }
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED" if result is not None else "⚠️ SKIPPED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    total = sum(1 for r in results.values() if r is not None)
    passed = sum(1 for r in results.values() if r is True)
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total and total > 0:
        print("\n🎉 All tests passed! PDF summarization is working correctly.")
        print("\n📝 Next steps:")
        print("   1. Start the backend: python backend/main.py")
        print("   2. Start the frontend: cd frontend && npm start")
        print("   3. Navigate to Policy Desk → Upload PDF Policy")
        print("   4. Upload a PDF and test the AI summarization")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
