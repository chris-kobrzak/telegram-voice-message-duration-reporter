import os
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from packages.reporter import generate_report

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = './tmp/'
app.config['MAX_CONTENT_LENGTH'] = 15 * 1024 * 1024

@app.route('/')
def render_form():
   return render_template('generate_report.html')

@app.route('/generate_report', methods = ['POST'])
def upload_file():
   if request.method == 'POST':
      file = request.files['file']
      upload_path = os.path.abspath(app.config['UPLOAD_FOLDER'] + secure_filename(file.filename))
      file.save(upload_path)
      report_filename = generate_report(upload_path, app.config['UPLOAD_FOLDER'])
      os.remove(upload_path)

      return send_from_directory(os.path.abspath(app.config['UPLOAD_FOLDER']), report_filename, as_attachment=True)

if __name__ == '__main__':
   app.run(debug = True)