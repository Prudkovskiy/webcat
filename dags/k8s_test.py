from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
    KubernetesPodOperator,
)

with DAG(
    dag_id="example_k8s_operator",
    schedule_interval="0 0 * * *",
    start_date=datetime(2023, 1, 1),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
) as dag:
    k = KubernetesPodOperator(
        name="hello",
        image="ubuntu",
        cmds=["bash", "-cx"],
        arguments=["sleep 10"],
        labels={"foo": "bar"},
        task_id="dry_run_demo",
        is_delete_operator_pod=False,
        do_xcom_push=True,
        # config_file='/'
    )

if __name__ == "__main__":
    dag.test()
