import re
import os
import os.path
import operator
import sys

HEADER_PATTERN = re.compile('^(#+)\s+(.*)$')
def header_level(line):
    m = HEADER_PATTERN.match(line)
    if m is None:
        return None, None
    hashes = m.group(1)
    lvl = len(hashes)
    return lvl, m.group(2)

ANCHOR_REMOVE = re.compile('[^\w\s-]+')
def header_anchor(title):
    anchor = title.lower()
    anchor = ANCHOR_REMOVE.sub('', anchor)
    anchor = anchor.replace(' ', '-')
    return anchor

def writelines(f, lines):
    for line in lines:
        f.write(line)
        f.write('\n')

def hr(f):
    f.write('\n---\n')
        
class MDFile:
    def __init__(self, filename):
        self.filename = filename

    def read_lines(self):
        sys.stderr.write('reading %s\n' % self.filename)
        header = False
        self.lines = []
        self.headers = []
        with open(self.filename) as f:
            for line in f:
                line = line.rstrip()
                if line == '<header/>':
                    header = True
                if header:
                    lvl, title = header_level(line)
                    if lvl == 1:
                        self.title = title
                    elif lvl:
                        anchor = header_anchor(title)
                        self.headers.append('%s* [%s](#%s)' % (' '*((lvl-2)*2), title, anchor))
                    self.lines.append(line)
        if not header:
            raise Exception('no header in %s' % self.filename)
        if not self.title:
            raise Exception('no title in %s' % self.filename)

    def overwrite_file(self, menu):
        sys.stderr.write('overwriting %s\n' % self.filename)
        with open(self.filename, 'w') as f:
            f.write(menu)
            hr(f)
            f.write('\n')
            writelines(f, self.headers)
            hr(f)
            f.write('\n')
            writelines(f, self.lines)


sys.stderr.write('listing files\n')
MDFILES = tuple(MDFile(f) for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.md') and not f.startswith('.'))

for mdf in MDFILES:
    mdf.read_lines()

sys.stderr.write('building top menu\n')
MENU = '| ' + '\n| '.join(('[%s](%s)' % (mdf.title, mdf.filename)) for mdf in sorted(MDFILES, key=operator.attrgetter('title'))) + '\n|\n'
for mdf in MDFILES:
    mdf.overwrite_file(MENU)
