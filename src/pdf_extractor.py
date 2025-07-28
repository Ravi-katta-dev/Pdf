import logging
import io
from typing import Optional, List
from pathlib import Path
import pdfplumber
import pytesseract
from PIL import Image
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class PDFExtractor:
    """Extract text from PDF files using pdfplumber with OCR fallback."""
    
    def __init__(self, ocr_languages: str = 'eng', dpi: int = 300):
        """
        Initialize PDF extractor.
        
        Args:
            ocr_languages: Languages for OCR processing
            dpi: DPI for image conversion
        """
        self.ocr_languages = ocr_languages
        self.dpi = dpi
        
    def extract_text(self, pdf_path: Path) -> str:
        """
        Extract text from PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
            
        Raises:
            Exception: If text extraction fails
        """
        try:
            logger.info(f"Extracting text from {pdf_path}")
            
            # First try pdfplumber for text extraction
            text = self._extract_with_pdfplumber(pdf_path)
            
            # If pdfplumber returns insufficient text, try OCR
            if len(text.strip()) < 100:
                logger.info("Insufficient text from pdfplumber, trying OCR")
                text = self._extract_with_ocr(pdf_path)
                
            logger.info(f"Successfully extracted {len(text)} characters")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            raise
    
    def _extract_with_pdfplumber(self, pdf_path: Path) -> str:
        """Extract text using pdfplumber."""
        text_content = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
                        logger.debug(f"Extracted text from page {page_num}")
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num}: {str(e)}")
                    continue
        
        return '\n'.join(text_content)
    
    def _extract_with_ocr(self, pdf_path: Path) -> str:
        """Extract text using OCR with pytesseract."""
        text_content = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    # Convert page to image
                    page_image = page.to_image(resolution=self.dpi)
                    
                    # Convert PIL image to numpy array for OpenCV processing
                    img_array = np.array(page_image.original)
                    
                    # Preprocess image for better OCR results
                    processed_img = self._preprocess_image(img_array)
                    
                    # Convert back to PIL Image
                    pil_image = Image.fromarray(processed_img)
                    
                    # Perform OCR
                    page_text = pytesseract.image_to_string(
                        pil_image, 
                        lang=self.ocr_languages,
                        config='--psm 6'  # Uniform block of text
                    )
                    
                    if page_text.strip():
                        text_content.append(page_text)
                        logger.debug(f"OCR extracted text from page {page_num}")
                        
                except Exception as e:
                    logger.warning(f"Error during OCR on page {page_num}: {str(e)}")
                    continue
        
        return '\n'.join(text_content)
    
    def _preprocess_image(self, img_array: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR results.
        
        Args:
            img_array: Input image as numpy array
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale if needed
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Apply adaptive thresholding for better text recognition
        processed = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Apply morphological operations to clean up the image
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, kernel)
        
        return processed
    
    def get_pdf_info(self, pdf_path: Path) -> dict:
        """
        Get basic information about the PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with PDF information
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                return {
                    'num_pages': len(pdf.pages),
                    'metadata': pdf.metadata or {},
                    'file_size': pdf_path.stat().st_size,
                    'filename': pdf_path.name
                }
        except Exception as e:
            logger.error(f"Error getting PDF info: {str(e)}")
            return {
                'num_pages': 0,
                'metadata': {},
                'file_size': 0,
                'filename': pdf_path.name,
                'error': str(e)
            }