web_category
==============================

Service for analyze categories of domains and urls

Project Organization
------------

    ├── README.md          <- The top-level README for developers using this project.
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── service            <- FastAPI project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── app.py         <- FastAPI app with endpoinds
    │   │
    │   ├── logger.py      <- Logger
    │   │
    │   └── models.py      <- Pydantic models for swagger and other models for service
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    ├── models.dvc         <- File for checking version of model and connect it with git branch
    ├── poetry.lock        <- File with all the packages and their exact versions, locking the project to those specific versions
    └── pyproject.toml     <- File with project's information and dependencies


DVC settings
------------

```console
$ dvc init
$ dvc remote add -d mls3 s3://ml-s3/dvc
$ dvc remote modify mls3 endpointurl https://obs.ru-moscow-1.hc.sbercloud.ru
$ dvc remote modify --local mls3 access_key_id '<key>'
$ dvc remote modify --local mls3 secret_access_key '<secret_key>'
$ dvc pull
```

what has been done
---
1. service on FastApi
2. container registry in yc
3. app's instance in kube
4. object storage s3 with 12Gb data on it
5. dvc for versioning models and data

what is planned to be done
---
1. model retraining pipeline in Airflow
2. monitoring in grafana