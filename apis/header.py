import re
import os
import os.path

HEADER_PATTERN = re.compile('^(#+)\s+(.*)$')
def header_level(line):
    m = HEADER_PATTERN.match(line)
    if m is None:
        return None, None
    hashes = m.group(1)
    lvl = len(hashes) - 1
    if lvl == 0:
        return None, None
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

class MDFile:
    def __init__(self, filename):
        self.filename = filename

    def read_lines(self):
        header = False
        self.lines = []
        self.headers = []
        with open(self.filename) as f:
            for line in f:
                line = line.strip()
                if line == '<header/>':
                    header = True
                if header:
                    lvl, title = header_level(line)
                    if lvl:
                        anchor = header_anchor(title)
                        self.headers.append('%s* [%s](%s)' % (' '*((lvl-1)*2), title, anchor))
                    self.lines.append(line)
        if not header:
            raise Exception('no header in %s' % self.filename)

    def overwrite_file(self, menu):
        with open(self.filename, 'w') as f:
            f.write(menu)
            f.write('\n')
            writelines(f, self.headers)
            f.write('\n')
            writelines(f, self.lines)
            f.write('\n')



MDFILES = tuple(MDFile(f) for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.md') and not f.startswith('.'))
for mdf in MDFILES:
    mdf.read_lines()


