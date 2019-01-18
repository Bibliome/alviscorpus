import configparser
import logging
import os
import getpass



LOGGER_ROOT = 'alviscorpus'
SECTION_GLOBAL = 'global'
SECTION_LOGGING = 'logging'
SECTION_DOCS = 'documents'
SECTION_PROXIES = 'proxies'
OPT_OUTDIR = 'outdir'
OPT_REPORT_FILENAME = 'report'
OPT_THREAD_POOL = 'threads'
MESSAGE_FORMAT = '[%(asctime)s][%(levelname)-8s][%(name)s] %(message)s'




_instance = configparser.ConfigParser(default_section=SECTION_GLOBAL, interpolation=None)
_instance[SECTION_GLOBAL][OPT_OUTDIR] = '.'
_instance[SECTION_GLOBAL][OPT_REPORT_FILENAME] = 'report.txt'
_instance[SECTION_GLOBAL][OPT_THREAD_POOL] = '4'
_instance.add_section(SECTION_LOGGING)
_instance.add_section(SECTION_DOCS)
_instance.add_section(SECTION_PROXIES)
    
def load(filename):
    return _instance.read(filename)

def _sec_opt(arg1, arg2=None):
    if arg2 is None:
        return SECTION_GLOBAL, arg1
    return arg1, arg2
    
def val(arg1, arg2=None):
    section, opt = _sec_opt(arg1, arg2)
    return _instance[section][opt]

def has(arg1, arg2=None):
    section, opt = _sec_opt(arg1, arg2)
    return _instance.has_option(section, opt)

def fill_defaults(section, opts):
    if not _instance.has_section(section):
        _instance.add_section(section)
    sec = _instance[section]
    for k, v in opts.items():
        if k not in sec:
            sec[k] = v


            
logger = None

def init_logger():
    root_logger = logging.getLogger(LOGGER_ROOT)
    handler = logging.StreamHandler()
    handler.setLevel(logging.WARNING)
    handler.setFormatter(logging.Formatter(MESSAGE_FORMAT))
    root_logger.addHandler(handler)
    global logger
    logger = get_logger('alvis-corpus')

def get_logger(name):
    result = logging.getLogger('%s.%s' % (LOGGER_ROOT, name))
    dirpath = val(SECTION_LOGGING, OPT_OUTDIR)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    path = os.path.join(dirpath, name + '.log')
    filehandler = logging.FileHandler(path, 'w')
    filehandler.setLevel(logging.DEBUG)
    filehandler.setFormatter(logging.Formatter(MESSAGE_FORMAT))
    result.addHandler(filehandler)
    result.setLevel(logging.DEBUG)
    return result




proxies = {}

def proxy(name):
    if name not in proxies:
        proxies[name] = { 'https': _proxy_url(name) }
    return proxies[name]

def _proxy_url(name):
    sec = _instance[SECTION_PROXIES]
    opt_host = name + '.host'
    if opt_host not in sec:
        raise Exception('no host for proxy ' + name)
    host = sec[opt_host]
    opt_user = name + '.user'
    if opt_user in sec:
        user = sec[opt_user]
        opt_password = name + '.password'
        if opt_password in sec:
            password = sec[opt_password]
        else:
            password = getpass.getpass(prompt='Password for %s@%s :' % (user, host))
        return 'https://%s:%s@%s' % (user, password, host)
    return 'https://%s' % host
