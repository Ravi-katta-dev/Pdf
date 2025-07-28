import os
from pathlib import Path

class Config:
    """Configuration settings for the MCQ extraction application."""
    
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
    OUTPUT_FOLDER = Path(__file__).parent / 'outputs'
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # PDF processing configuration
    OCR_LANGUAGES = 'eng'  # Language for OCR processing
    DPI = 300  # DPI for image conversion when using OCR
    
    # MCQ parsing configuration
    MIN_OPTIONS = 2  # Minimum number of options for a valid MCQ
    MAX_OPTIONS = 6  # Maximum number of options for a valid MCQ
    
    # Classification configuration
    CONFIDENCE_THRESHOLD = 0.3  # Minimum confidence score for classification
    
    # Export configuration
    JSON_INDENT = 2
    CSV_ENCODING = 'utf-8'
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration."""
        # Create necessary directories
        Config.UPLOAD_FOLDER.mkdir(exist_ok=True)
        Config.OUTPUT_FOLDER.mkdir(exist_ok=True)
        
        # Set Flask configuration
        app.config.from_object(Config)