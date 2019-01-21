import enum

class Status(enum.Enum):
    QUEUED = 'queued'
    STARTED = 'started'
    FINISHED = 'finished'
    ERROR = 'error'

    def __str__(self):
        return self.value

QUEUED = Status.QUEUED
STARTED = Status.STARTED
FINISHED = Status.FINISHED
ERROR = Status.ERROR
