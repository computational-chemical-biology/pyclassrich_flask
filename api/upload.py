from flask import Flask, render_template, request, make_response, flash, send_file
#from werkzeug import secure_filename
import pandas as pd
#from celery import uuid
import uuid
#from celery.result import AsyncResult
import os
from pyclassrich.models import impact_plot

from api import task

app = Flask(__name__)
app.secret_key = 'alura'

@app.route('/upload')
def upload_temp():
   return render_template('upload.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['canopus']
      canopus = str(uuid.uuid1())
      fls = os.path.join('/formatdb_flask/api/tmp', canopus)
      f.save(fls)
      result = request.form
      email = result['email']
      gtaskid = result['gtaskid']
      classes = result['classes']
      field = result['field']
      htest = result['htest']
      atype = result['atype']
      ispositive = int(result['ispositive'])
      adduct = result['adduct']
      ppm = int(result['ppm'])
      task_id = canopus
      df = task.longtask.apply_async(args=[email, gtaskid, classes, field, htest,
                                           atype, canopus, ispositive, adduct, ppm], task_id=task_id)
      return ('This is your task id: ' + task_id + '\n' +
              'You should receive an email with a download link soon')

@app.route('/download')
def download():
    taskid = request.args.get('taskid')
    table = request.args.get('table')
    ftype = request.args.get('ftype')
    if ftype=='tsv':
        fls = os.path.join('/formatdb_flask/api/tmp', f'{taskid}_{table}.{ftype}')
        df = pd.read_csv(fls,  sep='\t')
        #os.remove(fls)
        resp = make_response(df.to_csv(sep='\t', index=None))
        resp.headers["Content-Disposition"] = f"attachment; filename={table}.tsv"
        resp.headers["Content-Type"] = "text/tsv"
    elif ftype=='pdf':
        fls = os.path.join('/formatdb_flask/api/tmp', f'{taskid}.{ftype}')
        resp = send_file(fls, as_attachment=True)
    else:
        return ''
    return resp

@app.route('/impactplot', methods=['GET', 'POST'])
def impactplot():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'clusterdf' not in request.files or 'chemrich' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file1 = request.files['clusterdf']
        file2 = request.files['chemrich']
        scaling = int(request.form['scaling'])
        top = int(request.form['top'])
        # if user does not select file, browser also
        # submit an empty part without filename
        if file1.filename == '' or file2.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file1 and file2:
            clusterdf = pd.read_csv(request.files.get('clusterdf'), sep='\t')
            chemrich = pd.read_csv(request.files.get('chemrich'), sep='\t')
            # If you want to save the file
            #filename = secure_filename(file.filename)
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #return redirect(url_for('uploaded_file',
            #                        filename=filename))
            chemrich = chemrich.copy().loc[~chemrich['cluster.index'].isnull(),
                                     ['Identifier', 'class_name', 'InChI', 'pval', 'fchange']]
            chemrich.columns = ['Compound_Name', 'Class', 'InChI', 'pvalue', 'foldchange']

            taskid = file1.filename.split('_')[0]
            impact_plot(clusterdf, chemrich, cfield='Class', nfield='Compound_Name',
                        scaling_factor=scaling, top=top, outdir='/formatdb_flask/api/tmp',
                        filename=f'{taskid}.pdf')
            result = f"http://200.144.213.125:5020/download?taskid={taskid}&table=clusterdf&ftype=pdf"
            return render_template('view.html',
                                   result=result)
    else:
        result = None

    return render_template('view.html',
                           result=result)

@app.route('/status/<task_id>')
def status(task_id):
    res = AsyncResult(task_id)
    return res.status

if __name__ == '__main__':
    #app.run(debug = True)
    app.run(port=5020)
