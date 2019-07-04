from transcript_traversal import TranscriptTraversal
from requests.exceptions import InvalidURL, MissingSchema
import sys
from os import path

from flask import Flask, render_template, request, jsonify

if getattr(sys, 'frozen', False):
    base_dir = '.'
    if hasattr(sys, '_MEIPASS'):
        base_dir = path.join(sys._MEIPASS)
    app = Flask(__name__,
                static_folder=path.join(base_dir, 'static'),
                template_folder=path.join(base_dir, 'templates'))
else:
    app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        try:
            print(request.form)
            if request.form['requested-data'] == 'structured-transcript':
                return jsonify(TranscriptTraversal(request.form['transcript-url']).structured_transcript)
            elif request.form['requested-data'] == 'word-count':
                return jsonify(TranscriptTraversal(request.form['transcript-url']).get_word_count())
        except InvalidURL:
            return render_template('invalid-url.html')
        except MissingSchema:
            return render_template('invalid-url.html')

    else:
        print(request.method)

if __name__ == '__main__':
    app.run(debug=False)
    print()
