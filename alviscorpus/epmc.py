import requests

import alviscorpus.config as config
import alviscorpus.step as step
import alviscorpus.provider as provider    

SECTION_EPMC = 'epmc'
OPT_URL_BASE = 'url_base'
VAL_URL_BASE = 'www.ebi.ac.uk/europepmc/webservices/rest'
OPT_EMAIL = 'email'
OPT_PROXY = 'proxy'

class EPMCProvider(provider.ConstantDelayProvider):
    def __init__(self):
        provider.ConstantDelayProvider.__init__(self, 0)
        config.fill_defaults(SECTION_EPMC, {
            OPT_URL_BASE: VAL_URL_BASE
        })

_proxy_cache = None
def get_proxy():
    global _proxy_cache
    if _proxy_cache is None:
        if config.has(SECTION_EPMC, OPT_PROXY):
            proxy_name = config.val(SECTION_EPMC, OPT_PROXY)
            _proxy_cache = config.proxy(proxy_name)
        else:
            _proxy_cache = {}
    return _proxy_cache

class EPMCBase(step.Step):
    def __init__(self, name):
        step.Step.__init__(self, name, EPMCProvider)

    def process(self, doc, arg):
        pre = self.pre_process(doc, arg)
        if pre is not None:
            return step.pair(pre)
        r = requests.get(
            self.build_url(doc, arg),
            proxies=get_proxy()
        )
        self.logger.debug('EPMC request: %s' % r.url)
        if r.status_code == 200:
            next_step = self.handle_200(doc, arg, r.json())
        elif r.status_code == 404:
            next_step = self.handle_404(doc, arg, r.text)
        else:
            self.logger.error(r.text)
            raise step.StepException('EPMC server returned status %d' % r.status_code)
        return step.pair(next_step)

    def build_url(self, doc, arg):
        return 'https://' + config.val(SECTION_EPMC, OPT_URL_BASE) + self.build_url_suffix(doc, arg)

    def pre_process(self, doc, arg):
        raise NotImplemented()
    
    def build_url_suffix(self, doc, arg):
        raise NotImplemented()
    
    def handle_200(self, doc, arg, json):
        raise NotImplemented()

    def handle_404(self, doc, arg, json):
        raise NotImplemented()

