import os
import logging
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import uuid
from datetime import datetime

# Import our custom modules
from src import PDFExtractor, MCQParser, QuestionClassifier, DataExporter
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcq_extractor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure the app
    Config.init_app(app)
    
    return app

app = create_app()

# Initialize components
pdf_extractor = PDFExtractor(
    ocr_languages=app.config['OCR_LANGUAGES'],
    dpi=app.config['DPI']
)

mcq_parser = MCQParser(
    min_options=app.config['MIN_OPTIONS'],
    max_options=app.config['MAX_OPTIONS']
)

# Initialize classifier with keywords file
keywords_path = Path(app.config['UPLOAD_FOLDER']).parent / 'data' / 'keywords.json'
question_classifier = QuestionClassifier(
    keywords_path=keywords_path,
    confidence_threshold=app.config['CONFIDENCE_THRESHOLD']
)

data_exporter = DataExporter(
    json_indent=app.config['JSON_INDENT'],
    csv_encoding=app.config['CSV_ENCODING']
)

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Main upload page."""
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Handle file upload and processing."""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        file = request.files['file']
        
        # Check if file was actually selected
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        # Validate file
        if not file or not allowed_file(file.filename):
            flash('Please upload a valid PDF file', 'error')
            return redirect(url_for('index'))
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{unique_id}_{original_filename}"
        
        # Save uploaded file
        upload_path = app.config['UPLOAD_FOLDER'] / filename
        file.save(upload_path)
        
        logger.info(f"File uploaded: {filename}")
        
        # Get processing options
        use_ocr = request.form.get('use_ocr') == 'on'
        auto_classify = request.form.get('auto_classify') == 'on'
        
        # Process the PDF
        results = process_pdf(upload_path, use_ocr, auto_classify, unique_id)
        
        if results['success']:
            logger.info(f"Successfully processed {filename}")
            return render_template('results.html', **results['data'])
        else:
            flash(f"Error processing PDF: {results['error']}", 'error')
            return redirect(url_for('index'))
            
    except RequestEntityTooLarge:
        flash('File too large. Maximum size is 16MB.', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error in upload route: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('index'))

def process_pdf(pdf_path, use_ocr=True, auto_classify=True, session_id=None):
    """Process PDF file and extract MCQs."""
    try:
        # Extract text from PDF
        logger.info(f"Extracting text from {pdf_path}")
        text_content = pdf_extractor.extract_text(pdf_path)
        
        if not text_content.strip():
            return {
                'success': False,
                'error': 'No text could be extracted from the PDF. The file might be empty or contain only images.'
            }
        
        # Parse MCQs
        logger.info("Parsing MCQ questions")
        mcqs = mcq_parser.parse_mcqs(text_content)
        
        if not mcqs:
            return {
                'success': False,
                'error': 'No multiple-choice questions found in the PDF. Please check the content format.'
            }
        
        # Classify questions if enabled
        if auto_classify:
            logger.info("Classifying questions")
            for mcq in mcqs:
                options_text = ' '.join([opt.text for opt in mcq.options])
                classification = question_classifier.classify_question(
                    mcq.question_text, options_text
                )
                mcq.subject = classification.subject
                mcq.topic = classification.topic
                # Update confidence to include classification confidence
                mcq.confidence = (mcq.confidence + classification.confidence) / 2
        
        # Generate export files
        session_id = session_id or str(uuid.uuid4())[:8]
        base_filename = f"mcq_export_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        base_path = app.config['OUTPUT_FOLDER'] / base_filename
        
        export_files = data_exporter.export_multiple_formats(
            mcqs, base_path, ['json', 'csv', 'summary']
        )
        
        # Generate statistics
        stats = generate_statistics(mcqs)
        
        # Prepare results data
        results_data = {
            'filename': pdf_path.name,
            'total_questions': len(mcqs),
            'mcqs': [mcq_to_dict(mcq) for mcq in mcqs],
            'json_file': export_files['json'].name,
            'csv_file': export_files['csv'].name,
            'summary_file': export_files['summary'].name,
            **stats
        }
        
        logger.info(f"Processing complete: {len(mcqs)} questions extracted")
        
        # Clean up uploaded file
        try:
            pdf_path.unlink()
        except Exception as e:
            logger.warning(f"Could not remove uploaded file: {e}")
        
        return {
            'success': True,
            'data': results_data
        }
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        return {
            'success': False,
            'error': f'Processing failed: {str(e)}'
        }

def mcq_to_dict(mcq):
    """Convert MCQuestion object to dictionary for template rendering."""
    return {
        'id': mcq.id,
        'question_text': mcq.question_text,
        'options': [{'label': opt.label, 'text': opt.text} for opt in mcq.options],
        'correct_answer': mcq.correct_answer,
        'subject': mcq.subject,
        'topic': mcq.topic,
        'confidence': mcq.confidence,
        'page_number': mcq.page_number
    }

def generate_statistics(mcqs):
    """Generate statistics for the extracted MCQs."""
    if not mcqs:
        return {
            'subjects_count': 0,
            'avg_confidence': 0,
            'questions_with_answers': 0,
            'subject_breakdown': {}
        }
    
    # Count subjects
    subjects = set()
    subject_counts = {}
    
    for mcq in mcqs:
        if mcq.subject:
            subjects.add(mcq.subject)
            subject_counts[mcq.subject] = subject_counts.get(mcq.subject, 0) + 1
    
    # Calculate average confidence
    avg_confidence = sum(mcq.confidence for mcq in mcqs) / len(mcqs) * 100
    
    # Count questions with answers
    questions_with_answers = sum(1 for mcq in mcqs if mcq.correct_answer)
    
    return {
        'subjects_count': len(subjects),
        'avg_confidence': round(avg_confidence, 1),
        'questions_with_answers': questions_with_answers,
        'subject_breakdown': dict(sorted(subject_counts.items(), key=lambda x: x[1], reverse=True))
    }

@app.route('/download/<filename>')
def download(filename):
    """Download generated files."""
    try:
        file_path = app.config['OUTPUT_FOLDER'] / filename
        
        if not file_path.exists():
            flash('File not found', 'error')
            return redirect(url_for('index'))
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {str(e)}")
        flash('Error downloading file', 'error')
        return redirect(url_for('index'))

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stats')
def get_stats():
    """Get application statistics."""
    try:
        classifier_stats = question_classifier.get_classification_stats()
        
        return jsonify({
            'classifier': classifier_stats,
            'supported_formats': list(app.config['ALLOWED_EXTENSIONS']),
            'max_file_size': app.config['MAX_CONTENT_LENGTH'],
            'features': {
                'pdf_extraction': True,
                'ocr_fallback': True,
                'auto_classification': True,
                'export_formats': ['json', 'csv', 'summary']
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': 'Could not retrieve statistics'}), 500

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('upload.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    flash('An internal error occurred. Please try again.', 'error')
    return render_template('upload.html'), 500

@app.errorhandler(RequestEntityTooLarge)
def file_too_large(error):
    """Handle file too large errors."""
    flash('File too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Create necessary directories
    app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)
    app.config['OUTPUT_FOLDER'].mkdir(exist_ok=True)
    
    # Run the application
    debug_mode = app.config.get('DEBUG', False)
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)