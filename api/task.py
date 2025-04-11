import celery
import os
from api.pyclassrich import params, runpyClassRich
from config.settings import EMAIL, PASSWORD, MODELNAME
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import bz2
import json


#app.conf.update(BROKER_URL='redis://localhost:6379/0',
#                CELERY_RESULT_BACKEND='redis://localhost:6379/0')


app = celery.Celery('tasks', backend='redis://redis:6379/0',
                broker='redis://redis:6379/0')

@app.task
def longtask(email, gtaskid, classes, field, htest,
             atype, canopus, ispositive, adduct, ppm):
    chwcmd = f'python network_walk random-walk --taskid {gtaskid} --workflow FBMN-gnps2\
              --comp 0  --savegraph 1 --db COCONUT.psv\
              --metfragpath MetFrag2.3-CL.jar --kw '
    cwpar = {"ispositive": ispositive, "adduct": adduct, "ppm": ppm}
    chwcmd = chwcmd+json.dumps(cwpar)+'--out '+gtaskid[:5]
    try:
        params['gnps_taskid'] = gtaskid
        params['gnps_workflow'] = 'FBMN-gnps2'
        params['comparison']['classes'] = classes
        params['comparison']['field'] = field
        params['comparison']['test'] = htest
        params['chw'] = gtaskid[:5]+'.tsv'
        fls = os.path.join('/formatdb_flask/api/tmp', canopus)
        params['canopus_file'] = fls
        params['type'] = atype
        chemrich, clusterdf = runpyClassRich(params)
        chemrich.to_csv(fls+'_chemrich.tsv', index=False, sep='\t')
        clusterdf.to_csv(fls+'_clusterdf.tsv', index=False, sep='\t')

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.connect("smtp.gmail.com",587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(EMAIL, PASSWORD)

        msg = MIMEMultipart()
        msg['From'] = EMAIL
        msg['To'] = email
        msg['Subject'] = 'Result from pyClassRich'

        text = ("Your data is available for download here:\n"+
                "http://seriema.fcfrp.usp.br:5002/download/"+fls+"_chemrich.tsv"+"\n"+
                "http://seriema.fcfrp.usp.br:5002/download/"+fls+"_clusterdf.tsv"+"\n"+
                "WARNING: the data will be available for a single download.") 
        part1 = MIMEText(text, 'plain')
        msg.attach(part1)
        server.sendmail(EMAIL, email, msg.as_string())
        server.quit()
    except Exception as exc:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.connect("smtp.gmail.com",587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(EMAIL, PASSWORD)

        msg = MIMEMultipart()
        msg['From'] = EMAIL
        msg['To'] = email
        msg['Subject'] = 'Result from pyClassRich'

        formated = 'FAIL'
        text = ("Your task appear to have failed here is the error:\n"+
              str(exc)+'\n'+
              "If you are unable to understant the error reply this email.")
        part1 = MIMEText(text, 'plain')
        msg.attach(part1)
        server.sendmail(EMAIL, email, msg.as_string())
        server.quit()
    return 'Success!'




