import json
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

@dataclass
class ClassificationResult:
    """Result of question classification."""
    subject: str
    topic: str
    confidence: float
    matched_keywords: List[str]

class QuestionClassifier:
    """Classify MCQ questions by subject and topic using keyword matching."""
    
    def __init__(self, keywords_path: Optional[Path] = None, confidence_threshold: float = 0.3):
        """
        Initialize question classifier.
        
        Args:
            keywords_path: Path to keywords JSON file
            confidence_threshold: Minimum confidence for classification
        """
        self.confidence_threshold = confidence_threshold
        self.keywords_data = {}
        
        if keywords_path and keywords_path.exists():
            self.load_keywords(keywords_path)
        else:
            self._create_default_keywords()
    
    def load_keywords(self, keywords_path: Path):
        """Load keywords from JSON file."""
        try:
            with open(keywords_path, 'r', encoding='utf-8') as f:
                self.keywords_data = json.load(f)
            logger.info(f"Loaded keywords from {keywords_path}")
        except Exception as e:
            logger.error(f"Error loading keywords: {str(e)}")
            self._create_default_keywords()
    
    def _create_default_keywords(self):
        """Create default keyword mappings based on technical subjects."""
        self.keywords_data = {
            "Electronics": {
                "Basic Electronics": [
                    "resistor", "capacitor", "inductor", "diode", "transistor", "voltage", "current",
                    "ohm", "ampere", "volt", "watt", "power", "circuit", "electronic", "semiconductor",
                    "LED", "photodiode", "zener", "BJT", "FET", "MOSFET", "operational amplifier",
                    "op-amp", "rectifier", "filter", "oscillator", "amplifier"
                ],
                "Digital Electronics": [
                    "logic gate", "AND", "OR", "NOT", "NAND", "NOR", "XOR", "flip-flop", "counter",
                    "multiplexer", "demultiplexer", "encoder", "decoder", "digital", "binary",
                    "boolean", "truth table", "logic", "combinational", "sequential"
                ],
                "Communication": [
                    "modulation", "demodulation", "AM", "FM", "PM", "antenna", "transmission",
                    "receiver", "frequency", "bandwidth", "signal", "noise", "SNR", "communication",
                    "radio", "microwave", "satellite", "fiber optic"
                ]
            },
            "Electrical": {
                "DC Circuits": [
                    "DC", "direct current", "ohm's law", "kirchhoff", "series", "parallel",
                    "resistance", "conductance", "node", "mesh", "superposition", "thevenin",
                    "norton", "maximum power transfer"
                ],
                "AC Circuits": [
                    "AC", "alternating current", "sinusoidal", "phasor", "impedance", "reactance",
                    "capacitive", "inductive", "resonance", "power factor", "RMS", "average",
                    "reactive power", "apparent power", "real power"
                ],
                "Machines": [
                    "motor", "generator", "transformer", "induction", "synchronous", "DC motor",
                    "AC motor", "stepper motor", "servo motor", "torque", "speed", "efficiency",
                    "power factor", "slip", "rotor", "stator", "winding"
                ],
                "Power Systems": [
                    "transmission", "distribution", "protection", "relay", "circuit breaker",
                    "fuse", "earthing", "grounding", "insulation", "conductor", "cable",
                    "overhead line", "substation", "switchgear"
                ]
            },
            "Mechanical": {
                "Thermodynamics": [
                    "heat", "temperature", "entropy", "enthalpy", "pressure", "volume",
                    "thermodynamic", "cycle", "engine", "refrigeration", "heat transfer",
                    "conduction", "convection", "radiation", "thermal"
                ],
                "Fluid Mechanics": [
                    "fluid", "flow", "pressure", "velocity", "viscosity", "turbulent", "laminar",
                    "bernoulli", "continuity", "pump", "turbine", "pipe", "flow rate"
                ],
                "Mechanics": [
                    "force", "moment", "torque", "stress", "strain", "beam", "truss", "material",
                    "strength", "elastic", "plastic", "deformation", "mechanics", "statics",
                    "dynamics", "kinematics"
                ]
            },
            "Computer Science": {
                "Programming": [
                    "algorithm", "data structure", "programming", "code", "function", "variable",
                    "loop", "condition", "array", "pointer", "object", "class", "method",
                    "inheritance", "polymorphism"
                ],
                "Database": [
                    "database", "SQL", "table", "query", "join", "index", "normalization",
                    "primary key", "foreign key", "relationship", "RDBMS", "transaction"
                ],
                "Networks": [
                    "network", "protocol", "TCP", "IP", "HTTP", "FTP", "router", "switch",
                    "hub", "LAN", "WAN", "ethernet", "wireless", "OSI", "packet"
                ]
            },
            "Mathematics": {
                "Algebra": [
                    "equation", "polynomial", "matrix", "determinant", "eigenvalue", "vector",
                    "linear", "quadratic", "algebraic", "coefficient", "variable", "constant"
                ],
                "Calculus": [
                    "derivative", "integral", "limit", "continuity", "differentiation",
                    "integration", "partial", "differential", "calculus", "function"
                ],
                "Statistics": [
                    "probability", "statistics", "mean", "median", "mode", "variance",
                    "standard deviation", "distribution", "normal", "binomial", "poisson"
                ]
            },
            "Physics": {
                "Classical Mechanics": [
                    "motion", "velocity", "acceleration", "momentum", "energy", "work",
                    "power", "friction", "gravity", "newton", "mechanics", "kinematics",
                    "dynamics", "oscillation", "wave"
                ],
                "Electromagnetism": [
                    "electric field", "magnetic field", "electromagnetic", "maxwell",
                    "gauss", "faraday", "lenz", "electromagnetic induction", "flux"
                ],
                "Modern Physics": [
                    "quantum", "relativity", "photon", "electron", "atom", "nucleus",
                    "radioactivity", "particle", "wave-particle duality", "uncertainty"
                ]
            }
        }
    
    def classify_question(self, question_text: str, options_text: str = "") -> ClassificationResult:
        """
        Classify a question by subject and topic.
        
        Args:
            question_text: The main question text
            options_text: Combined text of all options
            
        Returns:
            Classification result with subject, topic, and confidence
        """
        try:
            # Combine question and options text for analysis
            full_text = f"{question_text} {options_text}".lower()
            
            # Clean text for keyword matching
            cleaned_text = self._clean_text_for_matching(full_text)
            
            # Find keyword matches for each subject and topic
            matches = self._find_keyword_matches(cleaned_text)
            
            if not matches:
                return ClassificationResult(
                    subject="General",
                    topic="Miscellaneous",
                    confidence=0.0,
                    matched_keywords=[]
                )
            
            # Calculate scores and find best match
            best_match = self._calculate_best_match(matches, cleaned_text)
            
            return best_match
            
        except Exception as e:
            logger.error(f"Error classifying question: {str(e)}")
            return ClassificationResult(
                subject="General",
                topic="Miscellaneous", 
                confidence=0.0,
                matched_keywords=[]
            )
    
    def _clean_text_for_matching(self, text: str) -> str:
        """Clean text for better keyword matching."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _find_keyword_matches(self, text: str) -> Dict[Tuple[str, str], List[str]]:
        """Find keyword matches for each subject-topic combination."""
        matches = {}
        
        for subject, topics in self.keywords_data.items():
            for topic, keywords in topics.items():
                matched_keywords = []
                
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    # Use word boundaries to avoid partial matches
                    pattern = r'\b' + re.escape(keyword_lower) + r'\b'
                    if re.search(pattern, text):
                        matched_keywords.append(keyword)
                
                if matched_keywords:
                    matches[(subject, topic)] = matched_keywords
        
        return matches
    
    def _calculate_best_match(self, matches: Dict[Tuple[str, str], List[str]], text: str) -> ClassificationResult:
        """Calculate the best subject-topic match based on keyword frequency and relevance."""
        
        scored_matches = []
        
        for (subject, topic), matched_keywords in matches.items():
            # Calculate base score from number of matches
            base_score = len(matched_keywords)
            
            # Calculate frequency score (how often keywords appear)
            frequency_score = 0
            for keyword in matched_keywords:
                keyword_pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                frequency_score += len(re.findall(keyword_pattern, text))
            
            # Calculate length bonus (longer keywords are more specific)
            length_bonus = sum(len(keyword.split()) for keyword in matched_keywords) * 0.1
            
            # Calculate density (keywords per text length)
            text_words = len(text.split())
            density_score = frequency_score / max(text_words, 1) * 10
            
            # Combined score
            total_score = base_score + frequency_score * 0.5 + length_bonus + density_score
            
            scored_matches.append({
                'subject': subject,
                'topic': topic,
                'score': total_score,
                'matched_keywords': matched_keywords,
                'base_score': base_score,
                'frequency_score': frequency_score
            })
        
        if not scored_matches:
            return ClassificationResult(
                subject="General",
                topic="Miscellaneous",
                confidence=0.0,
                matched_keywords=[]
            )
        
        # Sort by score and get the best match
        scored_matches.sort(key=lambda x: x['score'], reverse=True)
        best = scored_matches[0]
        
        # Calculate confidence based on score and competition
        max_score = best['score']
        second_score = scored_matches[1]['score'] if len(scored_matches) > 1 else 0
        
        # Confidence is higher when there's a clear winner
        if max_score > 0:
            confidence = min(max_score / 10, 1.0)  # Normalize to 0-1
            if second_score > 0:
                confidence *= (max_score / (max_score + second_score))  # Reduce if close competition
        else:
            confidence = 0.0
        
        return ClassificationResult(
            subject=best['subject'],
            topic=best['topic'],
            confidence=confidence,
            matched_keywords=best['matched_keywords']
        )
    
    def get_classification_stats(self) -> Dict[str, int]:
        """Get statistics about available classifications."""
        stats = {
            'total_subjects': len(self.keywords_data),
            'total_topics': sum(len(topics) for topics in self.keywords_data.values()),
            'total_keywords': sum(
                len(keywords) 
                for topics in self.keywords_data.values() 
                for keywords in topics.values()
            )
        }
        return stats
    
    def save_keywords(self, keywords_path: Path):
        """Save current keywords to JSON file."""
        try:
            with open(keywords_path, 'w', encoding='utf-8') as f:
                json.dump(self.keywords_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved keywords to {keywords_path}")
        except Exception as e:
            logger.error(f"Error saving keywords: {str(e)}")
            raise