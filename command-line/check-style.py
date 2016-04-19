'''
read the .style.yml and apply appropriate stylecheckers to the appropriate files
write out the results to .style_violations.json
'''
import os
import sys
from cgi import escape
import json
import yaml
import shutil
from jinja2 import Environment, FileSystemLoader
import argparse
from glob import glob

import pdb

parser = argparse.ArgumentParser(description="check style for a project")
parser.add_argument('web_directory', help="directory in which to write web report")

args = parser.parse_args()

# load the configureation file
config = yaml.load(open(".style.yml"))

# generate the style report
report = {} # filename: style violations pairs

for stylechecker_name, patterns in config.items():
    stylechecker = __import__("stylecheckers.{}".format(stylechecker_name), fromlist=['stylecheckers'])
    files = sum((glob(pattern) for pattern in patterns), [])
    report.update({f: stylechecker.check(f) for f in files})

# Write out style report
#json.dump(report, open(".style_violations.json", 'w'),
#         sort_keys=True, indent=2, separators=(',', ': '))

#TODO: turn json report into webpages

# Generate report webpages for each code file
def annotate_code(code, violations):
    violations = iter(sorted(violations, key=lambda v: (v['row'], v['col']) ))

    insertions = set() # (index, "text-to-insert") pairs.
    col = 1
    line = 1
    last_i = 0
    violation = next(violations)

    # Produce spans and where to insert them

    for index, char in enumerate(code):
        
        if line == violation['row'] and col == violation['col']:
            
            # span tags
            span_start = '<span class="violation" title="{}">'.format(
                escape(violation['message'])
                )
            span_end = '</span>'

            # index where the span ends
            end_index = index + violation.get('length', 1)

            # queue these up for insertion
            insertions.add((index, span_start))
            insertions.add((end_index, span_end))

            # get the next violation
            try:
                violation = next(violations)
            except StopIteration:
                break

        if char == '\n':
            line += 1
            col = 1
        else:
            col += 1

    # Insert the spans
    
    segments = []
    prev_index = 0
    for index, text in sorted(insertions):

        # add the code itself, with HTML special chars escaped
        segments.append(escape(code[prev_index:index]))

        # add the annotation (span)
        segments.append(text)

        # move the previous index up
        prev_index = index

    # Wdd the remaining text
    segments.append(escape(code[prev_index:]))

    # Join all the segments together into the final product
    annotated_code = ''.join(segments)

    return annotated_code

if not os.path.exists(args.web_directory):
    os.makedirs(args.web_directory)

source_path = os.path.dirname(os.path.realpath(__file__))
template_path = os.path.join(source_path, 'web-template')
env = Environment(loader=FileSystemLoader(template_path), trim_blocks=True, lstrip_blocks=True)
env.filters['quote'] = escape 

file_template = env.get_template("file.html")
directory_template = env.get_template("directory.html")
# TODO: copy over supporting CSS and JS
css_path = os.path.join(args.web_directory, 'css')
if not os.path.exists(css_path):
    shutil.copytree(os.path.join(template_path, 'css'), css_path)

js_path = os.path.join(args.web_directory, 'js')
if not os.path.exists(js_path):
    shutil.copytree(os.path.join(template_path, 'js'), js_path)

for file, violations in report.items():
    code = open(file).read()
    annotated_code = annotate_code(code, violations)
    file_html = file_template.render(language='python', code=annotated_code)
    file = file.replace('/', '__')
    html_filename = os.path.join(args.web_directory, "{}.html".format(file))
    open(html_filename, 'w').write(file_html)

directories = {}

# add file to each directory
for file, violations in report.items():
    directory, base = os.path.split(file)
    if directory not in directories:
        directories[directory] = []
    directories[directory].append({
        "name": base,
        "path": file.replace('/', '__')+'.html',
        "is_directory": False,
        "errors": len(violations)
        })

# TODO: Add subdirs to each directory. How?
for directory in directories:
    if not directory: continue

    parent, base = os.path.split(directory)

    directories[parent].append({
        "name": base,
        "path": directory.replace('/', '__')+'.html',
        "is_directory": True,
        "files": len(directories[base]) # TOOD: harden this
        })

# create HTML for each directory
for directory, contents in directories.items():
    dirname = directory or 'Index'
    directory_html = directory_template.render(directory=dirname,contents=contents)
    dirname = dirname.replace('/', '__')
    html_filename = os.path.join(args.web_directory, "{}.html".format(dirname))
    open(html_filename, 'w').write(directory_html)

#json.dump(directories, sys.stdout,
#         sort_keys=True, indent=2, separators=(',', ': '))