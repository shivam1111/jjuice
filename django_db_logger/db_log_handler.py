import logging
import traceback
from sendgrid.message import SendGridEmailMessage
from constance import config

class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        trace = None
        if record.exc_info:
            trace = traceback.format_exc()
        kwargs = {
            'logger_name': record.name,
            'level': record.levelno,
            'msg': record.getMessage(),
            'trace': trace
        }
        from django_db_logger.models import StatusLog
        log = StatusLog.objects.create(**kwargs)
        body = record.getMessage() + " ===========> Check Record no %s"%log.id
        try:
            email = SendGridEmailMessage('Error Level %s'%record.levelno,body,config.SUPPORT_EMAIL,[config.ERROR_EMAIL])
            email.send();
        except Exception as e:
            pass