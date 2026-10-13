from pathlib import Path
import hashlib
import json
import os
import subprocess
import yaml
import pandas as pd
import mlflow

mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI', 'http://127.0.0.1:5000'))
mlflow.set_experiment('tp3-dvc')
P = yaml.safe_load(Path('params.yaml').read_text(encoding='utf-8-sig'))
ticket = yaml.safe_load(Path('data/transactions.csv.dvc').read_text(encoding='utf-8'))['outs'][0]
empreinte = hashlib.md5(Path('data/transactions.csv').read_bytes()).hexdigest()
if empreinte != ticket['md5']:
    raise RuntimeError('Le CSV ne correspond pas au ticket : executer dvc add puis dvc repro.')
statut = subprocess.check_output(['dvc', 'status', '--json'], text=True)
if json.loads(statut):
    raise RuntimeError('Le pipeline a change : executer dvc repro avant de journaliser.')
if subprocess.check_output(['git', 'status', '--porcelain'], text=True).strip():
    raise RuntimeError('Enregistrer les fichiers suivis avec Git avant de journaliser.')
mets = json.loads(Path('reports/metrics.json').read_text(encoding='utf-8'))
commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
n = len(pd.read_csv('data/transactions.csv'))
with mlflow.start_run(run_name=f"donnees-{ticket['md5'][:8]}") as run:
    mlflow.log_params(P['entrainement'])
    mlflow.log_metrics(mets)
    mlflow.set_tags({'commit': commit, 'donnees_md5': ticket['md5'], 'donnees_lignes': n})
    mlflow.log_artifact('dvc.lock')
    print('run_id :', run.info.run_id)
print('run MLflow cree : donnees', ticket['md5'][:8], '-', n, 'lignes')
