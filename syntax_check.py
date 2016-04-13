#!/home/jeremy/anaconda2/bin/python
import re
import sys
import json
import jinja2
import cgi

errfile = sys.argv[1]
codefile = sys.argv[2]

violations = json.load(open(errfile))

# get code
code = open(codefile).read()


## add error markup to code
lines = list(code.split('\n'))

for v in sorted(violations, 
                key=lambda v: (v['col'], v['row']), 
                reverse=True):
    line = lines[v['row']-1]
    col = v['col']-1
    newline = \
        cgi.escape(line[:col]) \
        + '<span class="violation" title="{}: {}">'.format(cgi.escape(v['type']), cgi.escape(v['message'])) \
        + (cgi.escape(line[col]) if col < len(line) else '&nbsp;') \
        + '</span>' \
        + (cgi.escape(line[col+1:]) if col+1 < len(line) else '')

    lines[v['row']-1] = newline

marked_code = '\n'.join(lines)

# produce the HTML
template = jinja2.Template(open('report.html').read())
html =  template.render(language='python', code=marked_code)

print html
