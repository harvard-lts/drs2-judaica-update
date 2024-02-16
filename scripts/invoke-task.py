from celery import Celery
import os
from datetime import datetime

now = datetime.now()
timestamp = now.strftime("%Y%m%d%H%M")
job_ticket_id = f"{timestamp}_etd_base_invoke_task"

app1 = Celery('tasks')
app1.config_from_object('celeryconfig')

arguments = {"job_ticket_id": job_ticket_id, "feature_flags": {
            'dash_feature_flag': "off",
            'alma_feature_flag': "off",
            'send_to_drs_feature_flag': "off",
            'drs_holding_record_feature_flag': "off"},
            "identifier": "30522803"}

res = app1.send_task('etd-base-template.tasks.send_to_base',
                     args=[arguments], kwargs={},
                     queue=os.getenv("CONSUME_QUEUE_NAME",
                                     "etd_base_template"))
