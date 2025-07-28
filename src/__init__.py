"""
MCQ Extraction Package

This package provides tools for extracting, parsing, classifying, and exporting
multiple-choice questions from PDF files.
"""

__version__ = "1.0.0"
__author__ = "MCQ Extraction Team"

from .pdf_extractor import PDFExtractor
from .mcq_parser import MCQParser
from .classifier import QuestionClassifier
from .exporter import DataExporter

__all__ = ['PDFExtractor', 'MCQParser', 'QuestionClassifier', 'DataExporter']