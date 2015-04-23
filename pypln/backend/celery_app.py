from celery import Celery

app = Celery('pypln_workers', backend='mongodb',
        broker='amqp://', include=['pypln.backend.workers'])
