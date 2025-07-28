import re
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MCQOption:
    """Represents a single MCQ option."""
    label: str
    text: str

@dataclass
class MCQuestion:
    """Represents a complete multiple-choice question."""
    id: str
    question_text: str
    options: List[MCQOption]
    correct_answer: Optional[str] = None
    subject: Optional[str] = None
    topic: Optional[str] = None
    confidence: float = 0.0
    page_number: Optional[int] = None

class MCQParser:
    """Parse multiple-choice questions from extracted text."""
    
    def __init__(self, min_options: int = 2, max_options: int = 6):
        """
        Initialize MCQ parser.
        
        Args:
            min_options: Minimum number of options for a valid MCQ
            max_options: Maximum number of options for a valid MCQ
        """
        self.min_options = min_options
        self.max_options = max_options
        
        # Compile regex patterns for efficiency
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for MCQ detection."""
        
        # Pattern for question numbers (various formats)
        self.question_number_pattern = re.compile(
            r'(?:^|\n)\s*(?:'
            r'(?:Q\.?\s*)?(\d+)\.?\s*(?:\)|\.|\s)|'  # Q.1. or 1. or 1)
            r'(\d+)\.\s*(?=\w)|'  # 1. followed by word
            r'Question\s+(\d+)[\.\:\s]|'  # Question 1:
            r'Q\s*(\d+)[\.\:\s]'  # Q 1:
            r')',
            re.MULTILINE | re.IGNORECASE
        )
        
        # Pattern for MCQ options (A, B, C, D with various formats)
        self.option_pattern = re.compile(
            r'\(([a-dA-D])\)\s*([^(]+?)(?=\([a-dA-D]\)|\n\s*\d+\.|\n\s*(?:Answer|Ans)|\Z)',
            re.DOTALL
        )
        
        # Pattern to detect question text (before options)
        self.question_text_pattern = re.compile(
            r'(?:Q\.?\s*)?(?:\d+\.?\s*(?:\)|\.|\s)?)'  # Question number
            r'([^?\n]*\?|[^?\n]*(?:is|are|will|does|can|should|which|what|how|when|where|why)[^?\n]*)',
            re.IGNORECASE | re.MULTILINE
        )
        
        # Pattern for answer keys
        self.answer_pattern = re.compile(
            r'(?:Answer|Ans)\.?\s*[:=\-\s]*([A-Z])\b',
            re.IGNORECASE
        )
    
    def parse_mcqs(self, text: str) -> List[MCQuestion]:
        """
        Parse MCQs from text content.
        
        Args:
            text: Input text content
            
        Returns:
            List of parsed MCQ questions
        """
        try:
            logger.info("Starting MCQ parsing")
            
            # Clean and normalize text
            cleaned_text = self._clean_text(text)
            
            # Split text into potential question blocks
            question_blocks = self._split_into_question_blocks(cleaned_text)
            
            mcqs = []
            for i, block in enumerate(question_blocks, 1):
                try:
                    mcq = self._parse_single_mcq(block, i)
                    if mcq and self._validate_mcq(mcq):
                        mcqs.append(mcq)
                        logger.debug(f"Successfully parsed MCQ {mcq.id}")
                except Exception as e:
                    logger.warning(f"Error parsing question block {i}: {str(e)}")
                    continue
            
            logger.info(f"Successfully parsed {len(mcqs)} MCQs")
            return mcqs
            
        except Exception as e:
            logger.error(f"Error during MCQ parsing: {str(e)}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for better parsing."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR errors
        text = re.sub(r'(?i)0ption', 'Option', text)
        text = re.sub(r'(?i)0uestion', 'Question', text)
        
        # Normalize line breaks
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        
        return text.strip()
    
    def _split_into_question_blocks(self, text: str) -> List[str]:
        """Split text into individual question blocks."""
        # Find all question number positions
        question_matches = list(self.question_number_pattern.finditer(text))
        
        if not question_matches:
            # If no clear question numbers found, try alternative splitting
            return self._alternative_split(text)
        
        blocks = []
        for i, match in enumerate(question_matches):
            start = match.start()
            end = question_matches[i + 1].start() if i + 1 < len(question_matches) else len(text)
            
            block = text[start:end].strip()
            if block:
                blocks.append(block)
        
        return blocks
    
    def _alternative_split(self, text: str) -> List[str]:
        """Alternative method to split text when question numbers aren't clear."""
        # Split by potential question patterns
        patterns = [
            r'\n\s*(?=\([A-Z]\)|\w+\s*\([A-Z]\))',  # Before options
            r'\n\s*(?=\d+\.)',  # Before numbered items
        ]
        
        blocks = [text]
        for pattern in patterns:
            new_blocks = []
            for block in blocks:
                parts = re.split(pattern, block)
                new_blocks.extend([p.strip() for p in parts if p.strip()])
            blocks = new_blocks
        
        return blocks
    
    def _parse_single_mcq(self, block: str, question_id: int) -> Optional[MCQuestion]:
        """Parse a single MCQ from a text block."""
        
        # Extract question text
        question_text = self._extract_question_text(block)
        if not question_text:
            return None
        
        # Extract options
        options = self._extract_options(block)
        if len(options) < self.min_options or len(options) > self.max_options:
            return None
        
        # Extract answer if present
        correct_answer = self._extract_answer(block)
        
        return MCQuestion(
            id=f"Q{question_id:03d}",
            question_text=question_text,
            options=options,
            correct_answer=correct_answer,
            confidence=self._calculate_confidence(question_text, options)
        )
    
    def _extract_question_text(self, block: str) -> Optional[str]:
        """Extract question text from block."""
        lines = block.split('\n')
        
        # Combine lines until we hit options or get a complete question
        question_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip option lines
            if re.match(r'^\s*\(?[a-dA-D]\)?[\.\)\s]', line):
                break
                
            # Skip answer lines
            if re.match(r'(?i)^\s*(?:answer|ans)', line):
                break
            
            # Remove question numbers from start of line
            clean_line = re.sub(r'^\s*(?:Q\.?\s*)?\d+\.?\s*(?:\)|\.|\s)*', '', line)
            if clean_line:
                question_lines.append(clean_line)
        
        if question_lines:
            question_text = ' '.join(question_lines).strip()
            # Clean up extra whitespace
            question_text = re.sub(r'\s+', ' ', question_text)
            return question_text
        
        return None
    
    def _extract_options(self, block: str) -> List[MCQOption]:
        """Extract options from block."""
        options = []
        option_matches = self.option_pattern.findall(block)
        
        for label, text in option_matches:
            text = text.strip()
            if text and len(text) > 1:  # Minimum option length
                options.append(MCQOption(label=label, text=text))
        
        return options
    
    def _extract_answer(self, block: str) -> Optional[str]:
        """Extract correct answer from block."""
        answer_match = self.answer_pattern.search(block)
        return answer_match.group(1) if answer_match else None
    
    def _calculate_confidence(self, question_text: str, options: List[MCQOption]) -> float:
        """Calculate confidence score for MCQ quality."""
        score = 0.0
        
        # Question text quality
        if question_text:
            if question_text.endswith('?'):
                score += 0.3
            if len(question_text) > 20:
                score += 0.2
            if any(word in question_text.lower() for word in ['what', 'which', 'how', 'when', 'where', 'why']):
                score += 0.2
        
        # Options quality
        if len(options) >= 4:
            score += 0.2
        elif len(options) >= 2:
            score += 0.1
        
        # Option text quality
        if options:
            avg_option_length = sum(len(opt.text) for opt in options) / len(options)
            if avg_option_length > 5:
                score += 0.1
        
        return min(score, 1.0)
    
    def _validate_mcq(self, mcq: MCQuestion) -> bool:
        """Validate if parsed MCQ meets quality criteria."""
        if not mcq.question_text or len(mcq.question_text) < 5:  # Reduced from 10
            return False
        
        if len(mcq.options) < self.min_options or len(mcq.options) > self.max_options:
            return False
        
        # Check for duplicate options
        option_texts = [opt.text.lower().strip() for opt in mcq.options]
        if len(set(option_texts)) != len(option_texts):
            return False
        
        return mcq.confidence >= 0.1  # Reduced from 0.3 for testing