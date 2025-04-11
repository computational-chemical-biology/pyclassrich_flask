FROM continuumio/miniconda:latest
MAINTAINER Ricardo R. da Silva <ridasilva@usp.br>

ENV INSTALL_PATH /formatdb_flask
RUN mkdir -p $INSTALL_PATH
WORKDIR $INSTALL_PATH

RUN conda create -n pyclassrich python=3 
RUN echo "source activate pyclassrich" > ~/.bashrc
ENV PATH /opt/conda/envs/pyclassrich/bin:$PATH
RUN conda install -n pyclassrich -c rdkit rdkit -y
#RUN conda install -c conda-forge scikit-bio -y
RUN pip install gevent 
RUN pip install flask
RUN pip install werkzeug
#RUN pip install --upgrade pip
#RUN pip install celery==5.4.0
RUN pip install importlib-metadata==4.8.3
RUN pip install celery
RUN pip install redis
RUN pip install gunicorn 
RUN pip install python-dotenv
RUN /opt/conda/envs/pyclassrich/bin/pip install networkx pyteomics requests scikit-learn urllib3 xmltodict zipp csvkit scipy statsmodels seaborn sqlalchemy==1.3.23 gseapy obonet pyyaml ipython
RUN /opt/conda/envs/pyclassrich/bin/pip install git+https://github.com/computational-chemical-biology/ChemWalker.git 
RUN wget https://github.com/computational-chemical-biology/ChemWalker/blob/master/bin/MetFrag2.3-CL.jar
RUN apt-get update -y --allow-releaseinfo-change 
RUN dpkg --configure -a
RUN apt --fix-broken -y install 
RUN echo "export PATH=$PATH:/usr/lib/jvm/default-java/bin/" >> ~/.bashrc
ENV PATH /usr/lib/jvm/default-java/bin/:$PATH
#RUN apt install -y default-jre
COPY . .
RUN cd /formatdb_flask/pyClassRich \
    && /opt/conda/envs/pyclassrich/bin/python setup.py install

CMD gunicorn -b 0.0.0.0:8000 --access-logfile - "api.upload:app"

