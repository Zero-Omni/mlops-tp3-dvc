# TP3 DVC — Détection de fraude bancaire

ELATTAR Abderrahman · EL MRHARI Marouane · 5IASD G7

Ce projet reprend les trois scripts de préparation, entraînement et évaluation du TP2.
DVC suit les données et les sorties ; Git conserve le code, les tickets et les métriques.
L'expérience MLflow `tp3-dvc` relie chaque exécution au commit et au MD5 du CSV.

## Installation sous PowerShell

Python 3.12 et Git doivent être accessibles dans le terminal.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-lock.txt
```

`requirements.txt` décrit les dépendances principales ; `requirements-lock.txt`
conserve les versions installées pendant le TP.

## Récupérer les fichiers versionnés

Le remote DVC `stockage` pointe vers `../dvc-stockage`, un dossier voisin qui
simule un stockage partagé. GitHub ne contient pas les données ni le modèle.
Le dossier de stockage est fourni avec l'archive du rendu. Placez-le à côté du
projet avant de lancer :

```powershell
dvc pull
dvc status
dvc repro
dvc metrics show
```

Un clone GitHub seul ne suffit pas à restaurer les données. Pour travailler à
plusieurs, utilisez un remote DVC accessible à tous et les droits appropriés
(S3, Azure, Google Drive ou dossier réseau).

## Recréer les données à partir du code

Si aucun stockage n'est disponible, ces données synthétiques peuvent être recréées
avec les scripts. Cela recalcule le pipeline au lieu de restaurer les objets stockés.
Sur `main` (v2, 7000 lignes) :

```powershell
python donnees.py
python nouvelles_donnees.py
dvc repro
```

`nouvelles_donnees.py` attend exactement 5000 lignes pour empêcher un ajout répété.
Vérifiez ensuite `dvc status`. Pour restaurer exactement les objets d'origine,
utilisez plutôt le remote fourni et `dvc pull`.

## Relance partielle

Passez `entrainement.max_depth` de 12 à 8 dans `params.yaml`, puis :

```powershell
dvc status
dvc repro
dvc params diff
dvc metrics diff
git restore params.yaml
dvc repro
```

La préparation est inchangée. L'entraînement et l'évaluation sont recalculés ;
le retour à une configuration déjà exécutée réutilise le cache.

## MLflow

Dans un premier terminal :

```powershell
mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlartifacts
```

Dans le second terminal, après `dvc repro` et après avoir commité les fichiers :

```powershell
python src/journaliser.py
```

Le script vérifie que le MD5 du CSV correspond au ticket DVC, que le pipeline est
à jour et que le dépôt est propre. Il conserve les paramètres, métriques, tags
`commit`, `donnees_md5`, `donnees_lignes` et l'artefact `dvc.lock`.
Le modèle est suivi par DVC, sans nouvel enregistrement dans le registre MLflow.

## Revenir à une version

```powershell
git checkout v1
dvc checkout
(Import-Csv data/transactions.csv).Count
Get-Content reports/metrics.json
git checkout main
dvc checkout
(Import-Csv data/transactions.csv).Count
```

Si le cache local manque, remplacez `dvc checkout` par `dvc pull`.
`git checkout` restaure le code, les tickets et les métriques suivies par Git ;
DVC restaure les CSV, le modèle et la matrice de confusion.

## Publication

```powershell
git push -u origin main
git push --tags
dvc push
```

Les deux push ont des destinations différentes : GitHub pour le code et les
métadonnées ; le remote DVC pour les fichiers lourds.

Documentation : https://dvc.org/doc/command-reference/repro et
https://dvc.org/doc/command-reference/checkout.
