import os
import shutil
from pathlib import Path
import json

def create_dist_directory():
    """Create and clean dist directory"""
    dist_dir = Path('dist')
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    return dist_dir

def copy_static_files(dist_dir):
    """Copy static files to dist directory"""
    # Copy static assets
    static_dir = Path('app/static')
    if static_dir.exists():
        shutil.copytree(static_dir, dist_dir / 'static')

    # Copy templates as static HTML
    templates_dir = Path('app/templates')
    if templates_dir.exists():
        for template in templates_dir.glob('*.html'):
            if template.name != 'base.html':
                shutil.copy2(template, dist_dir)

def create_api_handler():
    """Create API handling JavaScript"""
    api_js = """
    // API handling code
    async function processPDF(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('https://pdf-processor-api.azurewebsites.net/process', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('API request failed');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = file.name.replace('.pdf', '_processed.xlsx');
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
            
        } catch (error) {
            console.error('Error:', error);
            throw error;
        }
    }
    """
    
    return api_js

def create_index_html(dist_dir):
    """Create main index.html file"""
    index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Footnotes Processor</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body class="bg-gray-100 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <header class="text-center mb-12">
            <h1 class="text-4xl font-bold text-gray-800 mb-4">PDF Footnotes Processor</h1>
            <p class="text-xl text-gray-600">Extract and process footnotes from PDF documents</p>
        </header>

        <div class="max-w-xl mx-auto bg-white rounded-lg shadow-lg p-8">
            <form id="uploadForm" class="space-y-6">
                <div class="space-y-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="pdfFile">
                        Upload PDF File
                    </label>
                    <input 
                        type="file" 
                        id="pdfFile" 
                        accept=".pdf"
                        class="w-full p-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                        required
                    >
                </div>

                <div id="fileInfo" class="hidden space-y-2 text-sm text-gray-600"></div>

                <button 
                    type="submit"
                    class="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition-colors"
                >
                    Process PDF
                </button>
            </form>

            <div id="processingStatus" class="mt-4 text-center hidden">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                <p class="mt-2 text-gray-600">Processing your PDF...</p>
            </div>

            <div id="errorMessage" class="mt-4 text-red-500 text-center hidden"></div>
        </div>
    </div>

    <script src="static/js/api.js"></script>
    <script src="static/js/main.js"></script>
</body>
</html>
    """
    
    with open(dist_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)

def create_main_js(dist_dir):
    """Create main JavaScript file"""
    main_js = """
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('pdfFile');
    const processingStatus = document.getElementById('processingStatus');
    const errorMessage = document.getElementById('errorMessage');
    
    if (!fileInput.files[0]) {
        errorMessage.textContent = 'Please select a PDF file';
        errorMessage.classList.remove('hidden');
        return;
    }
    
    try {
        processingStatus.classList.remove('hidden');
        errorMessage.classList.add('hidden');
        
        await processPDF(fileInput.files[0]);
        
        // Show success message
        alert('PDF processed successfully!');
        
    } catch (error) {
        errorMessage.textContent = 'Error processing PDF. Please try again.';
        errorMessage.classList.remove('hidden');
    } finally {
        processingStatus.classList.add('hidden');
    }
});
    """
    
    os.makedirs(dist_dir / 'static/js', exist_ok=True)
    with open(dist_dir / 'static/js/main.js', 'w', encoding='utf-8') as f:
        f.write(main_js)
    
    with open(dist_dir / 'static/js/api.js', 'w', encoding='utf-8') as f:
        f.write(create_api_handler())

def main():
    """Main build function"""
    dist_dir = create_dist_directory()
    copy_static_files(dist_dir)
    create_index_html(dist_dir)
    create_main_js(dist_dir)
    
    print("Build completed successfully!")

if __name__ == '__main__':
    main()
