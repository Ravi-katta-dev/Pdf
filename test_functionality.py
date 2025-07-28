#!/usr/bin/env python3
"""
Simple test script to validate the MCQ extraction functionality 
using existing text files without external dependencies.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Mock external dependencies for testing
class MockPDFExtractor:
    def __init__(self, *args, **kwargs):
        pass
    
    def extract_text(self, file_path):
        """Extract text from existing .txt files for testing."""
        if str(file_path).endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        return ""

# Replace imports with mocks for testing
sys.modules['pdfplumber'] = type('MockModule', (), {})()
sys.modules['pytesseract'] = type('MockModule', (), {})()
sys.modules['cv2'] = type('MockModule', (), {})()
sys.modules['PIL'] = type('MockModule', (), {'Image': type('MockImage', (), {})()})()
sys.modules['numpy'] = type('MockModule', (), {})()
sys.modules['pandas'] = type('MockModule', (), {
    'DataFrame': lambda x: type('MockDataFrame', (), {
        'to_csv': lambda *args, **kwargs: None
    })()
})()

# Now import our modules
from mcq_parser import MCQParser, MCQuestion, MCQOption
from classifier import QuestionClassifier

def test_mcq_parsing():
    """Test MCQ parsing functionality."""
    print("Testing MCQ Parser...")
    
    # Initialize parser
    parser = MCQParser()
    
    # Use sample MCQ text for testing
    sample_text = """
    74.  If 'M' is the mutual inductance between two 
    coils connected in series cummulatively 
    coupled, the equivalent inductance is
     (a) Leq = L1 + L2 + 2M  (b) Leq = L1 = L2 – 2M  
     (c) Leq = L1 + L2 – 2M (d) None of the above 
    
    75.  In a two-watt power meter, for all lagging
    power factors, first meter shows positive and 
    second meter shows negative reading. What is
    the power factor? 
    (a) 0 to 0.5 (b) 0.866 to 1   
     (c) 0 to 1 (d) 0.5 to 1
    
    76.  What is the unit of magnetic field intensity?   
     (a) Volt per meter  (b) Ampere per meter  
     (c) Volt per square meter (d) Weber per meter
    
    77.  Which of the following provides maximum  
    capacitance in the smallest space with the least  
    cost?  
     (a) Electrolytic capacitor  (b) Paper   
     (c) Ceramic (d) Mica
    """
    
    # Parse MCQs
    mcqs = parser.parse_mcqs(sample_text)
    
    print(f"Found {len(mcqs)} MCQ questions")
    
    # Display first few MCQs
    for i, mcq in enumerate(mcqs[:3]):
        print(f"\nMCQ {i+1}:")
        print(f"ID: {mcq.id}")
        print(f"Question: {mcq.question_text[:100]}...")
        print(f"Options: {len(mcq.options)}")
        for opt in mcq.options:
            print(f"  {opt.label}) {opt.text[:50]}...")
        print(f"Confidence: {mcq.confidence:.2f}")
        
    return len(mcqs) > 0

def test_classification():
    """Test question classification."""
    print("\nTesting Question Classifier...")
    
    # Initialize classifier
    classifier = QuestionClassifier()
    
    # Test classification with sample questions
    test_questions = [
        "What is the unit of electric current?",
        "Which logic gate performs AND operation?",
        "What is the formula for Ohm's law?",
        "How does a transistor work?"
    ]
    
    for question in test_questions:
        result = classifier.classify_question(question)
        print(f"Question: {question}")
        print(f"Subject: {result.subject}, Topic: {result.topic}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Keywords: {result.matched_keywords}")
        print()
    
    return True

def test_export():
    """Test export functionality."""
    print("Testing Data Exporter...")
    
    # Create sample MCQ data
    sample_mcq = MCQuestion(
        id="Q001",
        question_text="What is the unit of electric current?",
        options=[
            MCQOption("A", "Volt"),
            MCQOption("B", "Ampere"),
            MCQOption("C", "Ohm"),
            MCQOption("D", "Watt")
        ],
        correct_answer="B",
        subject="Electrical",
        topic="Basic Electronics",
        confidence=0.85
    )
    
    # Mock exporter for testing (without pandas)
    class MockExporter:
        def export_to_json(self, mcqs, path, include_metadata=True):
            import json
            data = {
                "mcqs": [
                    {
                        "id": mcq.id,
                        "question_text": mcq.question_text,
                        "options": [{"label": opt.label, "text": opt.text} for opt in mcq.options],
                        "correct_answer": mcq.correct_answer,
                        "subject": mcq.subject,
                        "topic": mcq.topic,
                        "confidence": mcq.confidence
                    }
                    for mcq in mcqs
                ]
            }
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            return path
    
    exporter = MockExporter()
    
    # Test JSON export
    json_path = Path("/tmp/test_export.json")
    exporter.export_to_json([sample_mcq], json_path)
    
    if json_path.exists():
        print(f"JSON export successful: {json_path}")
        print(f"File size: {json_path.stat().st_size} bytes")
        json_path.unlink()  # Clean up
        return True
    
    return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("MCQ Extractor - Functionality Test")
    print("=" * 50)
    
    tests = [
        ("MCQ Parsing", test_mcq_parsing),
        ("Classification", test_classification),
        ("Export", test_export)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result, None))
            print(f"✓ {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"✗ {test_name}: FAILED - {str(e)}")
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("=" * 50)
    
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    
    for test_name, result, error in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:<8} {test_name}")
        if error:
            print(f"         Error: {error}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)