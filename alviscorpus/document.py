import threading
import uuid
import collections
import os
import os.path
import json
import alviscorpus.config as config
import urllib.parse

_lock = threading.Lock()

def _incr():
    with _lock:
        Document.count += 1

def decr():
    with _lock:
        Document.count -= 1
    return decr == 0

class Document:
    count = 0
    
    def __init__(self):
        self.local_id = str(uuid.uuid4())
        self.doi = None
        self.data = collections.defaultdict(dict)
        self.status = collections.OrderedDict()
        _incr()

    def __str__(self):
        if self.doi is None:
            return self.local_id
        return self.doi

    def safe_doi(self):
        if self.doi is None:
            raise Exception()
        return urllib.parse.quote(self.doi, safe='')

    def get_dir(self):
        if self.doi is None:
            raise Exception()
        outdir = config.val(config.SECTION_DOCS, config.OPT_OUTDIR)
        r = os.path.join(outdir, self.safe_doi())
        if not os.path.exists(r):
            os.makedirs(r)
        return r

    def get_filename(self, ext):
        basename = '%s.%s' % (self.safe_doi(), ext)
        return os.path.join(self.get_dir(), basename)
    
    def dump_metadata(self):
        outfile = self.get_filename('md.json')
        with open(outfile, 'w') as f:
            json.dump(self.data, f, indent=2)

    def set_status(self, step, status):
        self.status[step] = status

