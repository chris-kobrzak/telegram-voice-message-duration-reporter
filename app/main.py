import io
import os
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename

from reporter import generate_report

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = '/var/tmp/'
app.config['MAX_CONTENT_LENGTH'] = 15 * 1024 * 1024


@app.route('/')
def render_form():
    return render_template('generate_report.html')


@app.route('/generate_report', methods=['POST'])
def upload_file():
    try:
        uploaded_file = request.files['file']
        upload_path = app.config['UPLOAD_FOLDER'] + \
            secure_filename(uploaded_file.filename)

        uploaded_file.save(upload_path)
        report_filename = generate_report(
            upload_path, app.config['UPLOAD_FOLDER'])
        os.remove(upload_path)

        report_path = app.config['UPLOAD_FOLDER'] + report_filename
        file_stream = convert_file_to_stream(report_path)

        return send_file(
            file_stream,
            mimetype='text/csv',
            attachment_filename=report_filename,
            as_attachment=True
        )
    except IsADirectoryError as exception:
        print('IsADirectoryError: ' + str(exception))
        return render_template('error.html')
    except UnicodeDecodeError as exception:
        print('UnicodeDecodeError: ' + str(exception))
        os.remove(upload_path)
        return render_template('error.html')
    except KeyError as exception:
        print('KeyError: ' + str(exception))
        os.remove(upload_path)
        return render_template('error.html')
    except Exception as exception:
        print('Exception: ' + str(exception))
        return render_template('error.html')


def convert_file_to_stream(file_path):
    stream = io.BytesIO()
    with open(file_path, 'rb') as file:
        stream.write(file.read())
    stream.seek(0)
    os.remove(file_path)
    return stream


if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
