import requests
import getpass
from datetime import datetime
from configparser import ConfigParser
from sys import stderr, argv

def log(msg):
    d = datetime.now()
    stderr.write('[' + d.strftime('%Y-%m-%d %H:%M:%S') + '] ' + msg + '\n')
    stderr.flush()


class SourceConfig(ConfigParser):
    def __init__(self, filename):
        ConfigParser.__init__(self, interpolation=None)
        self.read(filename)
        self.proxy_cache = {}

    def get_proxy(self, name):
        if name in self.proxy_cache:
            return self.proxy_cache[name]
        if name not in self:
            raise Exception('no configuration for proxy: %s' % name)
        proxy_cfg = self[name]
        protocol = proxy_cfg.get('protocol', 'https')
        host = proxy_cfg.get('host')
        if 'user' in proxy_cfg:
            user = proxy_cfg['user']
            if 'password' in proxy_cfg:
                password = proxy_cfg['password']
            else:
                password = getpass.getpass('Password for user %s in proxy %s (%s): ' % (user, name, host))
            url = '%s://%s:%s@%s' % (protocol, user, password, host)
        else:
            url = '%s://%s' % (protocol, host)
        result = {protocol: url}
        self.proxy_cache[name] = result
        return result

    
class ContentSource:
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.proxy = None

    def get_proxy(self):
        if self.proxy is None:
            if self.name in self.config:
                cfg = self.config[self.name]
                if 'proxy' in cfg:
                    proxy = cfg['proxy']
                    self.proxy = self.config.get_proxy(proxy)
                else:
                    self.proxy = {}
            else:
                self.proxy = {}
        return self.proxy
    
    def fetch(self, docid, scheme='doi'):
        method_name = 'fetch_' + scheme
        if hasattr(self, method_name):
            return getattr(self, method_name)(docid)
        else:
            raise Exception('source %s does not support id scheme %s' % (self.name, scheme))



class ElsevierSource(ContentSource):
    def __init__(self, config):
        ContentSource.__init__(self, 'elsevier', config)
        self.api_key = None

    def get_api_key(self):
        if self.api_key is None:
            if self.name not in self.config:
                raise Exception('missing configuration for %s' % self.name)
            cfg = self.config[self.name]
            if 'api_key' not in cfg:
                raise Exception('missing api_key for %s' % self.name)
            self.api_key = cfg['api_key']
        return self.api_key
    
    def fetch_doi(self, doi):
        return requests.get(
            'https://api.elsevier.com/content/article/doi/{}'.format(doi),
            proxies = self.get_proxy(),
            params = {'view': 'FULL'},
            headers = {'X-ELS-APIKey': self.get_api_key()}
        )
    
    def fetch_pmid(self, pmid):
        return requests.get(
            'https://api.elsevier.com/content/article/pubmed_id/{}'.format(pmid),
            proxies = self.get_proxy(),
            params = {'view': 'FULL'},
            headers = {'X-ELS-APIKey': self.get_api_key()}
        )
    
    def fetch_pii(self, pii):
        return requests.get(
            'https://api.elsevier.com/content/article/pii/{}'.format(pii),
            proxies = self.get_proxy(),
            params = {'view': 'FULL'},
            headers = {'X-ELS-APIKey': self.get_api_key()}
        )



class PMCEuropeSource(ContentSource):
    def __init__(self, config):
        ContentSource.__init__(self, 'pmc-europe', config)

    def fetch_pmc(self, pmcid):
        return requests.get(
            'https://www.ebi.ac.uk/europepmc/webservices/rest/{}/fullTextXML'.format(pmcid),
            proxies = self.get_proxy()
        )

    def fetch_doi(self, doi):
        r = requests.get(
            'https://www.ebi.ac.uk/europepmc/webservices/rest/search',
            params = {'query': 'DOI:'+doi},
            proxies = self.get_proxy()
        )

    def fetch_pmid(self, pmid):
        r = requests.get(
            'https://www.ebi.ac.uk/europepmc/webservices/rest/search',
            params = {'query': 'EXT_ID:'+pmid},
            proxies = self.get_proxy()
        )
        print (r.text)


    

config = SourceConfig(argv[1])
def test(src, id, scheme):
    r = src.fetch(id, scheme)
    print (r.url)
    print (r.status_code)
    print ()


e = ElsevierSource(config)
test(e, '10.1016/j.ijfoodmicro.2014.08.018', 'doi') # 10.6026/97320630009937
test(e, 'S0168-1605(14)00422-X', 'pii')
test(e, '25180667', 'pmid')

p = PMCEuropeSource(config)
test(p, '25180667', 'pmid')
