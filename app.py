from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = 'calkjsdlkjfqer'
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

ALLOWED_EXTENSIONS = set(['xlsx'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_from_directory(directory='uploads', filename=filename)

def sorted_directory(directory):
    def get_creation_time(entry):
        return entry.stat().st_ctime

    with os.scandir(directory) as entries:
        sorted_entries = sorted(entries, key=get_creation_time)
        sorted_items = [entry.name for entry in sorted_entries]
    return sorted_items


@app.route('/upload', methods=['POST'])
def load_file():
    if 'files[]' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files.getlist('files[]')[0]
    sorted_files = sorted_directory(app.config['UPLOAD_FOLDER'])

    # delete 10 of 20 old files
    if len(sorted_files) > 20:
      for filename in sorted_directory(app.config['UPLOAD_FOLDER'])[:11]:
        if filename != '.DS_Store':
          print("remove old file ", filename)
          os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    if not allowed_file(file.filename):
        print('That file extension is not allowed')
        return jsonify({'error': 'That file extension is not allowed!'})
    else:
        print("sample")
        print(file.filename)
        filename = file.filename # secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        from flask import Flask, make_response, send_file
        from pyexcel_ods3 import save_data
        from pyexcel_xlsx import get_data
        file_path = "/".join([os.path.dirname(os.path.realpath(__file__)), file_path])
        print(file_path)

        data = get_data(file_path)
        file_path = ".".join([file_path.split(".")[0], "ods"])
        print("filepath", file_path)

        save_data(file_path, data)
        return send_file(file_path, as_attachment=True)
        #return jsonify({'success': 'Saved file'})
        #return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
