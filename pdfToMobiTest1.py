import os
from flask import Flask, request, send_file
from ebooklib import epub
from pathlib import Path
from werkzeug.utils import secure_filename
import subprocess

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'fb2', 'epub'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_mobi(input_file):
    output_file = input_file.with_suffix('.mobi')
    # Используем Calibre для конвертации
    # Убедитесь, что Calibre установлен и доступен в командной строке
    subprocess.run(['ebook-convert', str(input_file), str(output_file)], check=True)
    return output_file

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = Path(app.config['UPLOAD_FOLDER']) / filename
        file.save(filepath)

        mobi_file = convert_to_mobi(filepath)

        return send_file(mobi_file, as_attachment=True)

    return 'Invalid file format', 400

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)