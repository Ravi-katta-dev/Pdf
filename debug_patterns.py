#!/usr/bin/env python3
"""
Debug MCQ parsing patterns
"""

import re

def debug_patterns():
    """Debug the MCQ parsing patterns."""
    
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
    """
    
    print("Sample text:")
    print(repr(sample_text))
    print("\n" + "="*50)
    
    # Test question number pattern
    question_pattern = re.compile(
        r'(?:^|\n)\s*(?:'
        r'(?:Q\.?\s*)?(\d+)\.?\s*(?:\)|\.|\s)|'  # Q.1. or 1. or 1)
        r'(\d+)\.\s*(?=\w)|'  # 1. followed by word
        r'Question\s+(\d+)[\.\:\s]|'  # Question 1:
        r'Q\s*(\d+)[\.\:\s]'  # Q 1:
        r')',
        re.MULTILINE | re.IGNORECASE
    )
    
    print("Question number matches:")
    matches = question_pattern.findall(sample_text)
    for i, match in enumerate(matches):
        print(f"Match {i+1}: {match}")
    
    print("\n" + "="*30)
    
    # Test option pattern
    option_pattern = re.compile(
        r'(?:^|\n)\s*'
        r'\(?([a-zA-Z])\)?[\.\)\s]+'  # (a) or a) or a.
        r'([^\n\r]+?)(?=\n\s*\(?[a-zA-Z]\)?[\.\)\s]|\n\s*(?:Q\.?\s*)?\d+\.|\n\s*Answer|\n\s*Ans|\Z)',
        re.MULTILINE | re.DOTALL
    )
    
    print("Option matches:")
    option_matches = option_pattern.findall(sample_text)
    for i, (label, text) in enumerate(option_matches):
        print(f"Option {i+1}: {label} -> {text.strip()}")
    
    print("\n" + "="*30)
    
    # Simpler option pattern
    simple_option_pattern = re.compile(r'\(([a-d])\)\s*([^(]+?)(?=\([a-d]\)|$)', re.DOTALL)
    
    print("Simple option matches:")
    simple_matches = simple_option_pattern.findall(sample_text)
    for i, (label, text) in enumerate(simple_matches):
        print(f"Simple Option {i+1}: {label} -> {text.strip()}")

if __name__ == "__main__":
    debug_patterns()