import os.path

import alviscorpus.config as config
import alviscorpus.step as step
import alviscorpus.provider as provider    
import alviscorpus.document as document




class EndReportStep(step.Step):
    def __init__(self):
        step.Step.__init__(self, step.END, provider.pool())
        outdir = config.val(config.OPT_OUTDIR)
        filename = config.val(config.OPT_REPORT_FILENAME)
        self.filepath = os.path.join(outdir, filename)
        self.handle = open(self.filepath, 'w')

    def process(self, doc, arg):
        self.handle.write('%s\t%s\t%s\n' % (doc, ', '.join('%s: %s'%i for i in doc.status.items() if i[0] != self.name), arg))
        self.handle.flush()
        doc.dump_metadata()
        if document.decr():
            step.close_providers()
            self.handle.close()
        return None, None
EndReportStep()

    

class CheckDocumentDataProvider(provider.ConstantDelayProvider):
    def __init__(self):
        provider.ConstantDelayProvider.__init__(self)

class CheckDOI(step.Step):
    def __init__(self, name, with_doi, without_doi):
        step.Step.__init__(self, name, CheckDocumentDataProvider)
        self.with_doi = step.pair(with_doi)
        self.without_doi = step.pair(without_doi)

    def process(self, doc, arg):
        if doc.doi is None:
            return self.without_doi
        return self.with_doi

class CheckMetadata(step.Step):
    def __init__(self, name, ns, field, with_field, without_field, without_ns):
        step.Step.__init__(self, name, CheckDocumentDataProvider)
        self.ns = ns
        self.field = field
        self.with_field = step.pair(with_field)
        self.without_field = step.pair(without_field)
        self.without_ns = step.pair(without_ns)

    def process(self, doc, arg):
        if self.ns not in doc.data:
            return self.without_ns
        if self.field is None:
            return self.with_field
        data = doc.data[self.ns]
        if self.field not in data:
            return self.without_field
        return self.with_field

def CheckMetadataNamespace(name, ns, with_ns, without_ns):
    return CheckMetadata(name, ns, None, with_ns, None, without_ns)
