# MCQ Extractor - Flask Web Application

A comprehensive Flask web application for extracting multiple-choice questions from PDF files with AI-powered classification and export capabilities.

![MCQ Extractor Interface](https://github.com/user-attachments/assets/45d67c57-6c57-483e-afb7-707b643967be)

## 🚀 Features

### Core Functionality
- **PDF Processing**: Extract text using pdfplumber with OCR fallback via pytesseract
- **MCQ Parsing**: Detect and parse multiple-choice questions with intelligent regex patterns
- **Classification**: Categorize questions by subject and topic using keyword matching
- **Web Interface**: Bootstrap 5 UI with drag-drop upload and results display
- **Export Functionality**: Generate JSON and CSV outputs with structured data

### Technical Highlights
- **Modular Architecture**: Separate components for extraction, parsing, classification, and export
- **OCR Fallback**: Automatic OCR processing when text extraction fails
- **Confidence Scoring**: Quality assessment for extracted questions
- **Responsive Design**: Mobile-friendly Bootstrap 5 interface
- **Error Handling**: Comprehensive error handling and logging
- **Security**: Input validation and secure file handling

## 📁 Project Structure

```
mcq-extraction/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── config.py                # Configuration settings
├── src/                     # Core modules
│   ├── __init__.py
│   ├── pdf_extractor.py     # PDF text extraction
│   ├── mcq_parser.py        # MCQ detection & parsing
│   ├── classifier.py        # Subject/topic classification
│   └── exporter.py          # JSON/CSV export
├── data/
│   └── keywords.json        # Classification keywords
├── templates/               # HTML templates
│   ├── base.html
│   ├── upload.html
│   └── results.html
├── static/                  # CSS/JS assets
│   ├── css/style.css
│   └── js/main.js
├── uploads/                 # Temporary file storage
└── outputs/                 # Generated exports
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Tesseract OCR (for OCR functionality)

### Dependencies
```bash
pip install -r requirements.txt
```

**Core Dependencies:**
- Flask - Web framework
- pdfplumber - PDF text extraction
- pytesseract - OCR processing
- opencv-python - Image processing
- pandas - Data manipulation
- numpy - Numerical operations

### Quick Start
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`
4. Open http://localhost:5000 in your browser

## 📊 How It Works

### 1. PDF Processing
- Primary text extraction using pdfplumber
- OCR fallback with pytesseract for image-based content
- Image preprocessing for better OCR accuracy

### 2. MCQ Detection
- Smart regex patterns identify question structures
- Parsing of question text and multiple choice options
- Support for various MCQ formats (A-D, numbered, etc.)

### 3. Classification
- Keyword-based classification system
- 50+ subject categories across multiple domains:
  - Electronics (Basic, Digital, Communication, Power)
  - Electrical (DC/AC Circuits, Machines, Power Systems)
  - Mechanical (Thermodynamics, Fluid Mechanics)
  - Computer Science (Programming, Database, Networks)
  - Mathematics (Algebra, Calculus, Statistics)
  - Physics (Classical, Electromagnetic, Modern)
  - Railway Engineering (Signaling, Safety)

### 4. Export & Results
- JSON format with structured data
- CSV format for spreadsheet compatibility
- Summary reports with statistics
- Interactive web interface for reviewing results

## 🔧 Configuration

### Environment Variables
```bash
FLASK_DEBUG=False              # Debug mode
SECRET_KEY=your-secret-key     # Flask secret key
MAX_CONTENT_LENGTH=16777216    # Max file size (16MB)
```

### Processing Options
- **OCR Languages**: Configure via `OCR_LANGUAGES` in config.py
- **Confidence Thresholds**: Adjust minimum confidence for classification
- **File Limits**: Customize maximum file size and allowed extensions

## 📈 Output Formats

### JSON Structure
```json
{
  "mcqs": [
    {
      "id": "Q001",
      "question_text": "What is the unit of electric current?",
      "options": [
        {"label": "A", "text": "Volt"},
        {"label": "B", "text": "Ampere"},
        {"label": "C", "text": "Ohm"},
        {"label": "D", "text": "Watt"}
      ],
      "correct_answer": "B",
      "subject": "Electronics",
      "topic": "Basic Electronics",
      "confidence": 0.85
    }
  ],
  "metadata": {
    "total_questions": 1,
    "export_timestamp": "2024-01-01T12:00:00",
    "statistics": {...}
  }
}
```

### CSV Format
Structured tabular data with columns for:
- Question ID, Text, Subject, Topic
- Options A-F
- Correct Answer, Confidence Score
- Page Number (if available)

## 🎯 Use Cases

- **Educational Content Processing**: Extract questions from textbooks and study materials
- **Exam Preparation**: Convert PDF question banks to structured formats
- **Content Analysis**: Analyze question distribution across subjects
- **Database Creation**: Build searchable question databases
- **Quality Assessment**: Evaluate question quality and classification accuracy

## 🚦 API Endpoints

- `GET /` - Main upload interface
- `POST /upload` - File upload and processing
- `GET /download/<filename>` - Download generated files
- `GET /api/health` - Health check endpoint
- `GET /api/stats` - Application statistics

## 🔍 Quality Metrics

The system provides confidence scoring based on:
- Question text structure and completeness
- Number and quality of options
- Keyword match relevance for classification
- Overall parsing accuracy

## 🛡️ Security Features

- File type validation (PDF only)
- File size limits (16MB maximum)
- Secure filename handling
- Input sanitization
- Error handling and logging

## 🧪 Testing

Run the functionality tests:
```bash
python test_functionality.py
```

Test coverage includes:
- MCQ parsing with sample text
- Classification accuracy
- Export functionality
- Error handling

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the existing issues on GitHub
- Create a new issue with detailed description
- Include sample files and error logs when applicable

---

**Built with ❤️ for educational content processing**
