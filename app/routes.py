from flask import Blueprint, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from app.utils.pdf_processor import PDFProcessor
import os
import tempfile
import logging

main = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/process', methods=['POST'])
def process_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
                file.save(temp_pdf.name)
                
                # Process PDF
                processor = PDFProcessor()
                excel_path = processor.process_pdf(temp_pdf.name)
                
                # Send the Excel file
                return send_file(
                    excel_path,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True,
                    download_name=f"{os.path.splitext(file.filename)[0]}_processed.xlsx"
                )
                
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return jsonify({'error': str(e)}), 500
            
        finally:
            # Cleanup temporary files
            try:
                os.remove(temp_pdf.name)
                if excel_path and os.path.exists(excel_path):
                    os.remove(excel_path)
            except Exception as e:
                logger.error(f"Error cleaning up files: {str(e)}")
    
    return jsonify({'error': 'Invalid file type'}), 400
