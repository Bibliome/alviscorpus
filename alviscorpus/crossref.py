import requests

import alviscorpus.config as config
import alviscorpus.step as step
import alviscorpus.provider as provider    


HEADER_LIMIT = 'X-Rate-Limit-Limit'
HEADER_INTERVAL = 'X-Rate-Limit-Interval'
SECTION_CROSSREF = 'crossref'
OPT_HOST = 'host'
VAL_HOST = 'api.crossref.org'
OPT_EMAIL = 'email'
OPT_PROXY = 'proxy'


class CrossRefProvider(provider.LimitIntervalProvider):
    def __init__(self):
        provider.LimitIntervalProvider.__init__(self, 50, 1)
        config.fill_defaults(SECTION_CROSSREF, {
            OPT_HOST: VAL_HOST
        })

    def update_limit_interval(self, headers):
        if HEADER_LIMIT in headers and HEADER_INTERVAL in headers:
            self.limit = int(headers[HEADER_LIMIT])
            self.interval = int(headers[HEADER_INTERVAL][:-1])


_headers_cache = None
def get_headers():
    global _headers_cache
    if _headers_cache is None:
        _headers_cache = {
            'User-Agent': 'alviscorpus/0.0.1 (https://github.com/Bibliome/alviscorpus; mailto: %s)' % config.val(SECTION_CROSSREF, OPT_EMAIL),
            'Accept': '*/*',
            'Host': config.val(SECTION_CROSSREF, OPT_HOST)
        }
    return _headers_cache

# workaround automatic insertion of basic auth by requests
def auth(h):
    return h

_proxy_cache = None
def get_proxy():
    global _proxy_cache
    if _proxy_cache is None:
        if config.has(SECTION_CROSSREF, OPT_PROXY):
            proxy_name = config.val(SECTION_CROSSREF, OPT_PROXY)
            _proxy_cache = config.proxy(proxy_name)
        else:
            _proxy_cache = {}
    return _proxy_cache

class CrossRefBase(step.Step):
    def __init__(self, name):
        step.Step.__init__(self, name, CrossRefProvider)
    
    def process(self, doc, arg):
        pre = self.pre_process(doc, arg)
        if pre is not None:
            return step.pair(pre)
        r = requests.get(
            self.build_url(doc, arg),
            headers=get_headers(),
            auth=auth,
            proxies=get_proxy()
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
        self.provider.update_limit_interval(r.headers)
        return step.pair(next_step)

    def build_url(self, doc, arg):
        return 'https://' + config.val(SECTION_CROSSREF, OPT_HOST) + self.build_url_suffix(doc, arg)

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

    


