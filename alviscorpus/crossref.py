import requests


import alviscorpus.config as config
import alviscorpus.step as step
import alviscorpus.provider as provider    


class CrossRefProvider(provider.LimitIntervalProvider):
    HEADER_LIMIT = 'X-Rate-Limit-Limit'
    HEADER_INTERVAL = 'X-Rate-Limit-Interval'
    SECTION_CROSSREF = 'crossref'
    OPT_HOST = 'host'
    VAL_HOST = 'api.crossref.org'
    OPT_EMAIL = 'email'
    OPT_PROXY = 'proxy'
    
    def __init__(self):
        provider.LimitIntervalProvider.__init__(self, 50, 1)
        config.fill_defaults(CrossRefProvider.SECTION_CROSSREF, {
            CrossRefProvider.OPT_HOST: CrossRefProvider.VAL_HOST
        })

class CrossRefBase(step.Step):
    _headers = None
    _proxy = None
    
    def __init__(self, name):
        step.Step.__init__(self, name, CrossRefProvider)

    @staticmethod
    def headers():
        if CrossRefBase._headers is None:
            CrossRefBase._headers = {
                'User-Agent': 'alviscorpus/0.0.1 (https://github.com/Bibliome/alviscorpus; mailto: %s)' % config.val(CrossRefProvider.SECTION_CROSSREF, CrossRefProvider.OPT_EMAIL),
                'Accept': '*/*',
                'Host': config.val(CrossRefProvider.SECTION_CROSSREF, CrossRefProvider.OPT_HOST)
            }
        return CrossRefBase._headers

    @staticmethod
    def proxy():
        if CrossRefBase._proxy is None:
            if config.has(CrossRefProvider.SECTION_CROSSREF, CrossRefProvider.OPT_PROXY):
                proxy_name = config.val(CrossRefProvider.SECTION_CROSSREF, CrossRefProvider.OPT_PROXY)
                CrossRefBase._proxy = config.proxy(proxy_name)
            else:
                CrossRefBase._proxy = {}
        return CrossRefBase._proxy
                
    @staticmethod
    def auth(h):
        return h

    @staticmethod
    def update_limit_interval(headers):
        if CrossRefProvider.HEADER_LIMIT in headers and CrossRefProvider.HEADER_INTERVAL in headers:
            CrossRefProvider._singleton.limit = int(headers[CrossRefProvider.HEADER_LIMIT])
            CrossRefProvider._singleton.interval = int(headers[CrossRefProvider.HEADER_INTERVAL][:-1])
    
    def process(self, doc, arg):
        pre = self.pre_process(doc, arg)
        if pre is not None:
            return step.pair(pre)
        r = requests.get(
            self.build_url(doc, arg),
            headers=CrossRefBase.headers(),
            auth=CrossRefBase.auth,
            proxies=CrossRefBase.proxy()
        )
        self.logger.debug('CrossRef request: %s' % r.url)
        self.logger.debug('CrossRef request headers: %s' % r.request.headers)
        if r.status_code == 200:
            next_step = self.handle_200(doc, arg, r.json())
        elif r.status_code == 404:
            next_step = self.handle_404(doc, arg, r.json())
        else:
            self.logger.error(r.text)
            raise step.StepException('CrossRef server returned status %d' % r.status_code)
        CrossRefBase.update_limit_interval(r.headers)
        return step.pair(next_step)

    def build_url(self, doc, arg):
        return 'https://' + config.val(CrossRefProvider.SECTION_CROSSREF, CrossRefProvider.OPT_HOST) + self.build_url_suffix(doc, arg)

    def pre_process(self, doc, arg):
        raise NotImplemented()
    
    def build_url_suffix(self, doc, arg):
        raise NotImplemented()
    
    def handle_200(self, doc, arg, json):
        raise NotImplemented()

    def handle_404(self, doc, arg, json):
        raise NotImplemented()
        
class CrossRef(CrossRefBase):
    def __init__(self, name, next_step, no_doi_step, not_found_step):
        CrossRefBase.__init__(self, name)
        self.next_step = step.pair(next_step)
        self.no_doi_step = step.pair(no_doi_step)
        self.not_found_step = step.pair(not_found_step)

    def pre_process(self, doc, arg):
        if doc.doi is None:
            return self.no_doi_step
        return None

    def build_url_suffix(self, doc, arg):
        return '/works/' + doc.doi

    def handle_200(self, doc, arg, json):
        doc.data['crossref'] = json
        return self.next_step

    def handle_404(self, doc, arg, json):
        return self.not_found_step

    

