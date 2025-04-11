from pyclassrich.gnps import Proteosafe
import matplotlib.pyplot as plt

from pyclassrich.models import class_enrichment, impact_plot, ont_graph, get_ont_graph
from pyclassrich.utils import *
import pandas as pd
import json

from pyclassrich.stats import *

params = {
    "mzmine": False,
    "mzmine_batch": False,
    "desc": 'description',
    "gnps_taskid": '',
    "gnps_workflow": '',
    "gnps_nap": False,
    "nap_taskid": '',
    "classify": True,
    "normalization": {
        "perform": True,
        "type": 'TIC'
    },
    "enrich": True,
    "comparison": {
        "classes": '',
        "field": '',
        "test": 'ttest',
        "vthr": 0.5
    },
    "summarize": True,
    "pcoa": True,
    "pcoa_metric": 'canberra',
    "pcoa_norm": True,
    "pcoa_scale": True,
    "email": 'email@gmail.com',
    "chw": '',
    "type": '',
    "canopus_file": ''
}

def runpyClassRich(params):
    db = get_db('COCONUT')

    gnps = Proteosafe(params['gnps_taskid'], 'FBMN-gnps2')
    gnps.get_gnps()

    feat = gnps.feat
    meta = gnps.meta

    meta.filename = meta.filename.str.replace(' Peak area', '')

    tabgnps = pd.merge(gnps.gnps, gnps.dbmatch,  left_on='cluster index', right_on='#Scan#', how='left')
    if tabgnps.shape[0] == 0:
        raise ValueError("Error on data and metadata naming match.")

    annotated = classifyChemWalker(params['chw'], 'COCONUT', tabgnps)
    tabgnps = tabgnps.rename(columns={'cluster index': 'cluster.index', 'parent mass':'parent.mass', 'SpectrumID':'LibraryID'})

    df = univariate(annotated, tabgnps,
                    params, feat, meta)

    if params['type']=='chemwalker':
        chemrich = df.copy().loc[~df['cluster.index'].isnull(),
                                 ['Identifier', 'class_name', 'InChI',
                                  'pval', 'fchange']]

        chemrich.columns = ['Compound_Name', 'Class', 'InChI', 'pvalue', 'foldchange']
        clusterdf = class_enrichment(chemrich, cfield='Class', nfield='Compound_Name')
    elif params['type']=='canopus':
        canopus = pd.read_csv(params['canopus_file'], sep='\t')
        canopus['cluster index'] = canopus['id'].apply(lambda a: a.split('_')[3])
        canopus['cluster index'] = canopus['cluster index'].astype(int)
        uni = pd.merge(df,
                       canopus[['cluster index', 'ClassyFire#most specific class']],
                       left_on='row ID', right_on='cluster index',
                       how='left')

        uni.drop(['class_name'], axis=1, inplace=True)
        uni.rename(columns={'ClassyFire#most specific class': 'class_name'}, inplace=True)
        uni['class_name'] = uni['class_name'].fillna('')

        chemrich = uni.copy().loc[~uni['cluster.index'].isnull(),
                                 ['Identifier', 'class_name', 'InChI',
                                  'pval', 'fchange']]

        chemrich.columns = ['Compound_Name', 'Class', 'InChI', 'pvalue', 'foldchange']

        clusterdf = class_enrichment(chemrich, cfield='Class', nfield='Compound_Name')
    else:
        raise ValueError("Unknown annotation type.")

    return chemrich, clusterdf
