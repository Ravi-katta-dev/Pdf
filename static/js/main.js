// Main JavaScript for MCQ Extractor

// Global variables
let uploadedFile = null;
let isProcessing = false;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeTooltips();
    initializeFileUpload();
    initializeFormValidation();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// File upload functionality
function initializeFileUpload() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('file');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const removeFileBtn = document.getElementById('removeFile');
    const uploadForm = document.getElementById('uploadForm');
    
    if (!uploadZone || !fileInput) return;

    // Drag and drop handlers
    uploadZone.addEventListener('dragover', handleDragOver);
    uploadZone.addEventListener('dragleave', handleDragLeave);
    uploadZone.addEventListener('drop', handleDrop);
    uploadZone.addEventListener('click', () => fileInput.click());

    // File input change handler
    fileInput.addEventListener('change', handleFileSelect);

    // Remove file handler
    if (removeFileBtn) {
        removeFileBtn.addEventListener('click', clearFile);
    }

    // Form submission handler
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleFormSubmit);
    }
}

// Drag over handler
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.add('dragover');
}

// Drag leave handler
function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('dragover');
}

// Drop handler
function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelection(files[0]);
    }
}

// File select handler
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFileSelection(files[0]);
    }
}

// Handle file selection
function handleFileSelection(file) {
    // Validate file
    if (!validateFile(file)) {
        return;
    }
    
    uploadedFile = file;
    displayFileInfo(file);
}

// Validate selected file
function validateFile(file) {
    const maxSize = 16 * 1024 * 1024; // 16MB
    const allowedTypes = ['application/pdf'];
    
    if (!allowedTypes.includes(file.type)) {
        showAlert('Please select a PDF file.', 'error');
        return false;
    }
    
    if (file.size > maxSize) {
        showAlert('File size must be less than 16MB.', 'error');
        return false;
    }
    
    return true;
}

// Display file information
function displayFileInfo(file) {
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const uploadZone = document.getElementById('uploadZone');
    
    if (fileName) fileName.textContent = file.name;
    if (fileSize) fileSize.textContent = formatFileSize(file.size);
    
    if (fileInfo) {
        fileInfo.classList.remove('d-none');
        fileInfo.classList.add('fade-in');
    }
    
    if (uploadZone) {
        uploadZone.classList.add('success');
    }
}

// Clear selected file
function clearFile() {
    uploadedFile = null;
    const fileInput = document.getElementById('file');
    const fileInfo = document.getElementById('fileInfo');
    const uploadZone = document.getElementById('uploadZone');
    
    if (fileInput) fileInput.value = '';
    if (fileInfo) fileInfo.classList.add('d-none');
    if (uploadZone) {
        uploadZone.classList.remove('success', 'error');
    }
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

// Handle form submission
function handleFormSubmit(e) {
    e.preventDefault();
    
    if (isProcessing) {
        return;
    }
    
    const fileInput = document.getElementById('file');
    if (!fileInput.files[0] && !uploadedFile) {
        showAlert('Please select a PDF file to upload.', 'error');
        return;
    }
    
    startProcessing();
    
    // Submit the form
    e.target.submit();
}

// Start processing animation
function startProcessing() {
    isProcessing = true;
    
    const submitBtn = document.getElementById('submitBtn');
    const progressSection = document.getElementById('progressSection');
    
    if (submitBtn) {
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
    }
    
    if (progressSection) {
        progressSection.classList.remove('d-none');
        progressSection.classList.add('fade-in');
        simulateProgress();
    }
}

// Simulate progress for better UX
function simulateProgress() {
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    
    if (!progressBar || !progressText) return;
    
    const steps = [
        { percent: 10, text: 'Uploading file...' },
        { percent: 25, text: 'Extracting text from PDF...' },
        { percent: 50, text: 'Parsing MCQ questions...' },
        { percent: 75, text: 'Classifying questions...' },
        { percent: 90, text: 'Generating reports...' },
        { percent: 100, text: 'Processing complete!' }
    ];
    
    let currentStep = 0;
    
    const updateProgress = () => {
        if (currentStep < steps.length) {
            const step = steps[currentStep];
            progressBar.style.width = step.percent + '%';
            progressText.textContent = step.text;
            currentStep++;
            
            const delay = currentStep === 1 ? 500 : 1000; // Faster initial step
            setTimeout(updateProgress, delay);
        }
    };
    
    updateProgress();
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertContainer.innerHTML = `
        <i class="bi bi-${type === 'error' ? 'exclamation-triangle' : type === 'success' ? 'check-circle' : 'info-circle'}"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the page
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertContainer, container.firstChild);
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            if (alertContainer.parentNode) {
                alertContainer.remove();
            }
        }, 5000);
    }
}

// Utility function to copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('Copied to clipboard!', 'success');
    }).catch(() => {
        showAlert('Failed to copy to clipboard.', 'error');
    });
}

// Export utility functions
const ExportUtils = {
    // Download data as JSON
    downloadJSON: function(data, filename) {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        this.downloadBlob(blob, filename);
    },
    
    // Download data as CSV
    downloadCSV: function(data, filename) {
        const csv = this.convertToCSV(data);
        const blob = new Blob([csv], { type: 'text/csv' });
        this.downloadBlob(blob, filename);
    },
    
    // Convert array of objects to CSV
    convertToCSV: function(data) {
        if (!data || data.length === 0) return '';
        
        const headers = Object.keys(data[0]);
        const csvHeaders = headers.join(',');
        
        const csvRows = data.map(row => {
            return headers.map(header => {
                const value = row[header];
                // Escape quotes and wrap in quotes if contains comma
                const escaped = String(value).replace(/"/g, '""');
                return escaped.includes(',') ? `"${escaped}"` : escaped;
            }).join(',');
        });
        
        return [csvHeaders, ...csvRows].join('\n');
    },
    
    // Download blob as file
    downloadBlob: function(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
};

// Performance monitoring
const Performance = {
    marks: {},
    
    mark: function(name) {
        this.marks[name] = performance.now();
    },
    
    measure: function(name, startMark) {
        const end = performance.now();
        const start = this.marks[startMark] || 0;
        console.log(`${name}: ${(end - start).toFixed(2)}ms`);
        return end - start;
    }
};

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    // Could implement error reporting here
});

// Unhandled promise rejection handling
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    // Could implement error reporting here
});

// Export utilities for use in other scripts
window.MCQExtractor = {
    ExportUtils,
    Performance,
    showAlert,
    copyToClipboard
};