import os
import json
import string
import random
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB limit

CODE_FILE = 'code_store.json'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def load_codes():
    if os.path.exists(CODE_FILE):
        with open(CODE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_codes(codes):
    with open(CODE_FILE, 'w') as f:
        json.dump(codes, f)

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        if uploaded_file and uploaded_file.filename:
            code = generate_code()
            filename = f"{code}_{uploaded_file.filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(filepath)

            codes = load_codes()
            codes[code] = filename
            save_codes(codes)

            return render_template('index.html', code=code)
        else:
            flash('No file selected.')
            return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/download', methods=['GET', 'POST'])
def download():
    if request.method == 'POST':
        code = request.form.get('code', '').strip().upper()
        codes = load_codes()
        filename = codes.get(code)
        if filename:
            return render_template('download.html', filename=filename, code=code)
        else:
            flash('Invalid code. Please try again.')
            return redirect(url_for('download'))
    return render_template('download.html')

@app.route('/delete', methods=['POST'])
def delete_file():
    code = request.form.get('code', '').strip().upper()
    codes = load_codes()
    filename = codes.get(code)

    if filename:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        codes.pop(code, None)
        save_codes(codes)
        flash(f'File for code {code} has been deleted.')
    else:
        flash('Invalid code. Nothing deleted.')
    
    return redirect(url_for('download'))

@app.route('/file/<filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
