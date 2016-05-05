'''
Read the .style.yml and apply appropriate stylecheckers to the appropriate files
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

# TODO: harden all this code; it will behave unpredictably when errors appear

parser = argparse.ArgumentParser(description="check style for a project")
parser.add_argument(
    'web_directory', help="directory in which to write web report")

args = parser.parse_args()

# load the configureation file
config = yaml.load(open(".style.yml"))

# Perform the stylecheck and generate the report
report = {}  # filename: style violations pairs

for stylechecker_name, patterns in config.items():
    stylechecker = __import__("stylecheckers.{}".format(
        stylechecker_name), fromlist=['stylecheckers'])
    files = sum((glob(pattern) for pattern in patterns), [])
    report.update({f: stylechecker.check(f) for f in files})

# Write out style report
# json.dump(report, open(".style_violations.json", 'w'),
#         sort_keys=True, indent=2, separators=(',', ': '))

# Generate report webpages for each code file


def annotate_code(code, violations):
    '''HTML escape the code and insert tags to mark style violations.
    '''
    # Calculate starting index of each line

    line_indices = [0]

    for line_length in map(len, code.split('\n')):
        line_index = line_indices[-1] + line_length
        line_indices.append(line_index)

    # Determine spans to insert and where to inesrt them

    # set of `(index, text)` pairs; `text` will be inserted at `index`
    insertions = set()

    for v in violations:
        index = line_indices[v['row'] - 1] + v['col'] - 1

        insertion = '<div class="violation" type="{}" style="width:{}ch;"><div class="error">{}</div></div>'.format(
            escape(v['type']),
            v.get('length', 1),
            escape(v['message'])
        )

        insertions.add((index, insertion))

    # Build up the escaped code and inserted spans in list of segments

    segments = []
    prev_index = 0
    for index, insertion in sorted(insertions):

        # add escaped code
        segments.append(escape(code[prev_index:index]))

        # add tag
        segments.append(insertion)

        prev_index = index

    # add the remaining text
    segments.append(escape(code[prev_index:]))

    # Join all the segments together and return annotated code
    annotated_code = ''.join(segments)

    return annotated_code

def path_filename(d):
    if not hasattr(path_filename, 'filenames'):
        setattr(path_filename, 'filenames', {})
        path_filename.filenames[''] = 'Index.html'

    if d in path_filename.filenames:
        return path_filename.filenames[d]
    else:
        fname = d.replace('/', '__') + '.html'
        path_filename.filenames[d] = fname
        return fname

def get_parents(path):
    if not path:
        return [("/", path_filename(''))]

    parent, base = os.path.split(path)
    fname = path_filename(path)

    return get_parents(parent) + [(base, fname)]

if not os.path.exists(args.web_directory):
    os.makedirs(args.web_directory)

source_path = os.path.dirname(os.path.realpath(__file__))
template_path = os.path.join(source_path, 'web-template')
env = Environment(loader=FileSystemLoader(template_path),
                  trim_blocks=True, lstrip_blocks=True)
env.filters['quote'] = escape

file_template = env.get_template("file.html")
directory_template = env.get_template("directory.html")

# Copy over supporting CSS and JS
css_path = os.path.join(args.web_directory, 'css')
if not os.path.exists(css_path):
    shutil.copytree(os.path.join(template_path, 'css'), css_path)

js_path = os.path.join(args.web_directory, 'js')
if not os.path.exists(js_path):
    shutil.copytree(os.path.join(template_path, 'js'), js_path)


## Write out the code files
for file, violations in report.items():
    # Render HTML
    dir_path = get_parents(file)
    code = open(file).read()
    annotated_code = annotate_code(code, violations)
    file_html = file_template.render(dir_path=dir_path, language='python', code=annotated_code)

    # Write to file
    html_filename = os.path.join(args.web_directory, path_filename(file))
    open(html_filename, 'w').write(file_html)

directories = {}

# Add file to each directory
for file, violations in report.items():
    directory, base = os.path.split(file)
    if directory not in directories:
        directories[directory] = []
    directories[directory].append({
        "name": base,
        "path": path_filename(file),
        "is_directory": False,
        "errors": len(violations)
    })

# Add subdirs to each directory.
#pdb.set_trace()
for directory in directories:
    if not directory:
        continue

    parent, base = os.path.split(directory)

    directories[parent].append({
        "name": base,
        "path": path_filename(directory),
        "is_directory": True,
        "files": len(directories[directory])
    })

    # Add parent dir link to child directories
    #directories[base].append({
    #    "name": "..",
    #    "path": path_filename(parent)
    #})

# Create HTML for each directory
for directory, contents in directories.items():
    # TODO: split up the whole directory path and create links at each level
    dir_path = get_parents(directory)
    directory_html = directory_template.render(
        dir_path=dir_path, contents=contents)

    dirname = path_filename(directory)
    html_filename = os.path.join(args.web_directory, dirname)
    open(html_filename, 'w').write(directory_html)

# json.dump(directories, sys.stdout,
#         sort_keys=True, indent=2, separators=(',', ': '))
