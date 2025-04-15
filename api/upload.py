from flask import Flask, render_template, request, make_response
#from werkzeug import secure_filename
import pandas as pd
#from celery import uuid
import uuid
#from celery.result import AsyncResult
import os

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
      fls = os.path.join('/formatdb_flask/api/tmp', f'{taskid}_{table}.tsv')
      df = pd.read_csv(fls,  sep='\t')
      #os.remove(fls)
      resp = make_response(df.to_csv(sep='\t', index=None))
      resp.headers["Content-Disposition"] = f"attachment; filename={table}.tsv"
      resp.headers["Content-Type"] = "text/tsv"
      return resp

@app.route('/status/<task_id>')
def status(task_id):
    res = AsyncResult(task_id)
    return res.status

if __name__ == '__main__':
    #app.run(debug = True)
    app.run(port=5020)
