from celery import Celery

app = Celery('workers', backend='mongodb',
        broker='amqp://', include=['pypln.backend.workers'])
