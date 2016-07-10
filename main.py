import os
from time import time
from flask import Flask, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask.templating import render_template
import DocumentRSOM
from flask.json import jsonify
import uuid
from numpy import integer
from datab import db
from string import lowercase

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf',])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def file_extension(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower()


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return jsonify(flaskerror="No file part.")
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return jsonify(flaskerror="No file selected.")
        if file_extension(file.filename) == "" or file_extension(file.filename) == "":
            return jsonify(flaskerror="Couldn't upload that file for you, make sure it has a valid extension (PDF or TXT).")
        if file and allowed_file(file.filename):
            filename = uuid.uuid4() #secure_filename(file.filename)
            filename = str(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            t0 = time()
            if(request.form['useGPU'] == u"true"):
                useGPUBoolean = True
            else:
                useGPUBoolean = False
            mapSide = int(request.form['mapSide'])
            try:
                DSOM = DocumentRSOM.DSOM(os.path.join(app.config['UPLOAD_FOLDER'], filename), 
                                     file_extension(file.filename), 
                                     useGPU=useGPUBoolean, widthOfMap=mapSide)
                DSOM.readDocument()
            except:
                return jsonify(flaskerror="I had a problem extracting data from that document. Please try again or a different file.")
            try:
                DSOM.train()
            except:
                return jsonify(flaskerror="I had a problem training the SOM, please try again.")
            try:
                separatedText = DSOM.getDataset()
                tfIDFArray = DSOM.tfIDFArray()
                from datab import Upload
                thisUpload = Upload(filename, time()-t0, useGPUBoolean, mapSide)
                db.session.add(thisUpload)
                db.session.commit()
                return jsonify(usedGPU=useGPUBoolean, timeTaken=time() - t0, clusters=DSOM.getClusters(), dataset=separatedText, tfIDF=tfIDFArray )
            except:
                return jsonify(flaskerror="Couldn't return data for this. Oops. Please try again.")
        else:
            return jsonify(flaskerror="Couldn't upload that file for you, make sure it has a valid extension (PDF or TXT).")
    
    return render_template('index.html')
            
from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(threaded=True)