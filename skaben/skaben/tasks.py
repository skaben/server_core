from celery import shared_task

@shared_task
def hello():
    print("Hello there!")


"""
task_list:

- send ping
- send configuration to client (result = task_id in return)
- send configuration broadcast

beat:
- send ping
- update visible client status from database

"""