import json
import csv
import logging
from typing import List, Dict, Any
from pathlib import Path
import pandas as pd
from datetime import datetime

from .mcq_parser import MCQuestion

logger = logging.getLogger(__name__)

class DataExporter:
    """Export MCQ data to various formats (JSON, CSV)."""
    
    def __init__(self, json_indent: int = 2, csv_encoding: str = 'utf-8'):
        """
        Initialize data exporter.
        
        Args:
            json_indent: Indentation for JSON formatting
            csv_encoding: Encoding for CSV files
        """
        self.json_indent = json_indent
        self.csv_encoding = csv_encoding
    
    def export_to_json(self, mcqs: List[MCQuestion], output_path: Path, 
                      include_metadata: bool = True) -> Path:
        """
        Export MCQs to JSON format.
        
        Args:
            mcqs: List of MCQ questions
            output_path: Output file path
            include_metadata: Whether to include metadata
            
        Returns:
            Path to created JSON file
        """
        try:
            logger.info(f"Exporting {len(mcqs)} MCQs to JSON: {output_path}")
            
            # Convert MCQs to dictionaries
            mcq_data = []
            for mcq in mcqs:
                mcq_dict = {
                    'id': mcq.id,
                    'question_text': mcq.question_text,
                    'options': [
                        {'label': opt.label, 'text': opt.text} 
                        for opt in mcq.options
                    ],
                    'correct_answer': mcq.correct_answer,
                    'subject': mcq.subject,
                    'topic': mcq.topic,
                    'confidence': round(mcq.confidence, 3),
                    'page_number': mcq.page_number
                }
                mcq_data.append(mcq_dict)
            
            # Prepare export data
            export_data = {
                'mcqs': mcq_data
            }
            
            # Add metadata if requested
            if include_metadata:
                export_data['metadata'] = self._generate_metadata(mcqs)
            
            # Write to JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=self.json_indent, ensure_ascii=False)
            
            logger.info(f"Successfully exported to JSON: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {str(e)}")
            raise
    
    def export_to_csv(self, mcqs: List[MCQuestion], output_path: Path) -> Path:
        """
        Export MCQs to CSV format.
        
        Args:
            mcqs: List of MCQ questions
            output_path: Output file path
            
        Returns:
            Path to created CSV file
        """
        try:
            logger.info(f"Exporting {len(mcqs)} MCQs to CSV: {output_path}")
            
            # Prepare data for CSV
            csv_data = []
            for mcq in mcqs:
                # Create base row
                row = {
                    'ID': mcq.id,
                    'Question': mcq.question_text,
                    'Subject': mcq.subject or '',
                    'Topic': mcq.topic or '',
                    'Confidence': round(mcq.confidence, 3),
                    'Correct_Answer': mcq.correct_answer or '',
                    'Page_Number': mcq.page_number or ''
                }
                
                # Add options (up to 6 options A-F)
                option_labels = ['A', 'B', 'C', 'D', 'E', 'F']
                for i, label in enumerate(option_labels):
                    option_text = ''
                    for opt in mcq.options:
                        if opt.label == label:
                            option_text = opt.text
                            break
                    row[f'Option_{label}'] = option_text
                
                csv_data.append(row)
            
            # Write to CSV using pandas for better handling
            df = pd.DataFrame(csv_data)
            df.to_csv(output_path, index=False, encoding=self.csv_encoding)
            
            logger.info(f"Successfully exported to CSV: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            raise
    
    def export_summary_report(self, mcqs: List[MCQuestion], output_path: Path) -> Path:
        """
        Export a summary report in JSON format.
        
        Args:
            mcqs: List of MCQ questions
            output_path: Output file path
            
        Returns:
            Path to created summary file
        """
        try:
            logger.info(f"Generating summary report: {output_path}")
            
            # Generate statistics
            stats = self._generate_statistics(mcqs)
            
            # Generate subject/topic breakdown
            subject_breakdown = self._generate_subject_breakdown(mcqs)
            
            # Generate quality metrics
            quality_metrics = self._generate_quality_metrics(mcqs)
            
            # Compile summary
            summary = {
                'summary': {
                    'total_questions': len(mcqs),
                    'export_timestamp': datetime.now().isoformat(),
                    'statistics': stats,
                    'subject_breakdown': subject_breakdown,
                    'quality_metrics': quality_metrics
                }
            }
            
            # Write summary to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=self.json_indent, ensure_ascii=False)
            
            logger.info(f"Successfully generated summary report: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating summary report: {str(e)}")
            raise
    
    def _generate_metadata(self, mcqs: List[MCQuestion]) -> Dict[str, Any]:
        """Generate metadata for export."""
        return {
            'export_timestamp': datetime.now().isoformat(),
            'total_questions': len(mcqs),
            'exporter_version': '1.0.0',
            'statistics': self._generate_statistics(mcqs)
        }
    
    def _generate_statistics(self, mcqs: List[MCQuestion]) -> Dict[str, Any]:
        """Generate basic statistics about the MCQs."""
        if not mcqs:
            return {}
        
        # Count questions by number of options
        option_counts = {}
        for mcq in mcqs:
            count = len(mcq.options)
            option_counts[count] = option_counts.get(count, 0) + 1
        
        # Calculate confidence statistics
        confidences = [mcq.confidence for mcq in mcqs]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Count questions with answers
        questions_with_answers = sum(1 for mcq in mcqs if mcq.correct_answer)
        
        return {
            'total_questions': len(mcqs),
            'questions_with_answers': questions_with_answers,
            'average_confidence': round(avg_confidence, 3),
            'option_distribution': option_counts,
            'confidence_ranges': {
                'high_confidence': sum(1 for c in confidences if c >= 0.7),
                'medium_confidence': sum(1 for c in confidences if 0.4 <= c < 0.7),
                'low_confidence': sum(1 for c in confidences if c < 0.4)
            }
        }
    
    def _generate_subject_breakdown(self, mcqs: List[MCQuestion]) -> Dict[str, Any]:
        """Generate breakdown by subject and topic."""
        subject_counts = {}
        topic_counts = {}
        
        for mcq in mcqs:
            subject = mcq.subject or 'Unclassified'
            topic = mcq.topic or 'General'
            
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
            topic_key = f"{subject}::{topic}"
            topic_counts[topic_key] = topic_counts.get(topic_key, 0) + 1
        
        return {
            'subjects': subject_counts,
            'topics': topic_counts
        }
    
    def _generate_quality_metrics(self, mcqs: List[MCQuestion]) -> Dict[str, Any]:
        """Generate quality metrics for the MCQs."""
        if not mcqs:
            return {}
        
        # Question text length statistics
        question_lengths = [len(mcq.question_text) for mcq in mcqs]
        avg_question_length = sum(question_lengths) / len(question_lengths)
        
        # Option text length statistics
        option_lengths = []
        for mcq in mcqs:
            for opt in mcq.options:
                option_lengths.append(len(opt.text))
        
        avg_option_length = sum(option_lengths) / len(option_lengths) if option_lengths else 0
        
        # Classify questions by quality
        high_quality = sum(1 for mcq in mcqs if mcq.confidence >= 0.7)
        medium_quality = sum(1 for mcq in mcqs if 0.4 <= mcq.confidence < 0.7)
        low_quality = sum(1 for mcq in mcqs if mcq.confidence < 0.4)
        
        return {
            'average_question_length': round(avg_question_length, 1),
            'average_option_length': round(avg_option_length, 1),
            'quality_distribution': {
                'high_quality': high_quality,
                'medium_quality': medium_quality,
                'low_quality': low_quality
            },
            'completeness': {
                'questions_with_subjects': sum(1 for mcq in mcqs if mcq.subject),
                'questions_with_topics': sum(1 for mcq in mcqs if mcq.topic),
                'questions_with_answers': sum(1 for mcq in mcqs if mcq.correct_answer)
            }
        }
    
    def export_multiple_formats(self, mcqs: List[MCQuestion], base_path: Path, 
                              formats: List[str] = None) -> Dict[str, Path]:
        """
        Export MCQs to multiple formats.
        
        Args:
            mcqs: List of MCQ questions
            base_path: Base path for output files (without extension)
            formats: List of formats to export ('json', 'csv', 'summary')
            
        Returns:
            Dictionary mapping format names to output file paths
        """
        if formats is None:
            formats = ['json', 'csv', 'summary']
        
        results = {}
        
        try:
            for fmt in formats:
                if fmt == 'json':
                    output_path = base_path.with_suffix('.json')
                    results['json'] = self.export_to_json(mcqs, output_path)
                elif fmt == 'csv':
                    output_path = base_path.with_suffix('.csv')
                    results['csv'] = self.export_to_csv(mcqs, output_path)
                elif fmt == 'summary':
                    output_path = base_path.with_name(f"{base_path.stem}_summary.json")
                    results['summary'] = self.export_summary_report(mcqs, output_path)
                else:
                    logger.warning(f"Unknown export format: {fmt}")
            
            logger.info(f"Successfully exported to {len(results)} formats")
            return results
            
        except Exception as e:
            logger.error(f"Error in multiple format export: {str(e)}")
            raise