from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import os
import threading

app = Flask(__name__)

# Folder pentru upload și thumbnails
UPLOAD_FOLDER = 'uploads'
THUMB_FOLDER = 'uploads/thumbs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(THUMB_FOLDER, exist_ok=True)

# Tipuri de fișiere permise
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'ogg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Verifică extensia fișierului
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Creează thumbnail pentru imagini
def create_thumbnail(file_path, thumb_path):
    try:
        img = Image.open(file_path)
        img.thumbnail((200, 200))
        img.save(thumb_path)
    except Exception as e:
        print(f"Thumbnail error: {e}")

# Rute
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/uploads/thumbs/<filename>')
def thumb_file(filename):
    return send_from_directory(THUMB_FOLDER, filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist('file')
    threads = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Creează thumbnail în thread separat (rapiditate)
            if filename.lower().endswith(('png','jpg','jpeg','gif')):
                thumb_path = os.path.join(THUMB_FOLDER, filename)
                t = threading.Thread(target=create_thumbnail, args=(filepath, thumb_path))
                t.start()
                threads.append(t)
    
    for t in threads:
        t.join()
    return jsonify({'status':'ok'})

@app.route('/list_media')
def list_media():
    media = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if allowed_file(filename):
            media.append({
                'name': filename,
                'url': url_for('uploaded_file', filename=filename),
                'thumb': url_for('thumb_file', filename=filename) if filename.lower().endswith(('png','jpg','jpeg','gif')) else url_for('uploaded_file', filename=filename),
                'type': 'video' if filename.lower().endswith(('mp4','webm','ogg')) else 'image'
            })
    return jsonify(media)

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
