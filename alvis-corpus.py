import alviscorpus.config as config
import alviscorpus.document as document
import alviscorpus.step as step
import alviscorpus.steplib as steplib
import alviscorpus.crossref as crossref

config.load('alvis-corpus.rc')
config.init_logger()
steplib.ReportStep(step.END, None)
cr = crossref.CrossRef('crossref', (step.END, 'ok'), (step.END, 'cr-no-doi'), (step.END, 'cr-not-found'))
step.init_providers()
with open('test-doi.txt') as f:
    for doi in f:
        doc = document.Document()
        doc.doi = doi.strip()
        cr.enqueue(doc)
