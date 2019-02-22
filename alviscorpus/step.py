

import alviscorpus.config as config
import alviscorpus.status as status

END = 'end'

_registry = {}
    

class Step:
    def __init__(self, name, provider):
        if name in _registry:
            raise Exception()
        _registry[name] = self
        self.name = name
        self.logger = config.get_logger(name)
        self.provider = provider

    def enqueue(self, doc, arg=None):
        self.provider.register(self, doc, arg)
        doc.set_status(self.name, status.QUEUED)
        
    def process(self, doc, arg=None):
        raise NotImplemented()

def pair(value):
    try:
        a, b = value
        return value
    except TypeError:
        return value, None
            
def get(name):
    if name not in _registry:
        raise Exception('unknown step: %s' % name)
    return _registry[name]

def enqueue(name, doc, arg=None):
    thestep = get(END)
    thestep.enqueue(doc, arg)

def init_providers():
    for step in _registry.values():
        step.provider.init()

def close_providers():
    for step in _registry.values():
        step.provider.close()


class StepException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
