'''
Author: Jeremy Vonderfecht

Command-line utility which checks code style against a standard and produces
html-based report in specified directory. Read the .style.yml and apply
appropriate stylecheckers to the appropriate files write out the results to
web_directory as specified by command line argument
'''
import os
import sys
import json
import yaml
import shutil
import argparse
from glob import glob
from cgi import escape
from jinja2 import Environment, FileSystemLoader

import pdb

# TODO: be consistent with var name conventions, etc

# TODO: more helpful help messages
parser = argparse.ArgumentParser(
    description="check code style of a project based upon settings in .style.yml")
parser.add_argument(
    'web_directory', help="directory in which to write web report")
parser.add_argument(
    '--project_directory', help="directory in which to place your project and .style.yml")

args = parser.parse_args()

if args.project_directory:
    os.chdir(args.project_directory)

# load the configureation file
if not os.path.exists('.style.yml'):
    print("No .style.yml found.")
    exit(1)

config = yaml.load(open(".style.yml"))

# TODO: check format of config against Rx schema

# Perform the stylecheck and generate the report
report = {}  # filename: style violations pairs

for stylechecker_name, patterns in config.items():
    # TODO: report error when stylechecker isn't found
    try:
        stylechecker = __import__("stylecheckers.{}".format(
            stylechecker_name), fromlist=['stylecheckers'])
    except:
        print("Could not find styechecker '{}'.".format(stylechecker_name))
        exit(1)

    files = []
    for pattern in patterns:
        filesMatchingPattern = glob(pattern)

        if not filesMatchingPattern:
            print("Warning: no files match pattern {}".format(pattern))

        files += filesMatchingPattern

    report_files = {}
    for f in files:
        try:
            report_files[f] = stylechecker.check(f)
        except:
            print("Error checking file {}".format(f))

    report.update(report_files)

# Generate report webpages for each code file


def annotate_code(code, violations):
    # TODO: more thorough docstring here
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

        insertion = '<div class="violation" type="{}" style="width:{}ch;">' \
                    + '<div class="error">{}</div></div>'.format(
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
    '''TODO: docstring
    '''
    if not hasattr(path_filename, 'filenames'):
        setattr(path_filename, 'filenames', {})
        path_filename.filenames[''] = 'Index.html'

    if d in path_filename.filenames:
        return path_filename.filenames[d]
    else:
        fname = d.replace('/', '__').replace('\\', '__') + '.html'
        if fname not in path_filename.filenames.values():
            path_filename.filenames[d] = fname
        else:
            i = 1
            old_fname = fname
            fname = old_fname+'({})'.format(i)
            while fname in path_filename.filenames.values():
                i += 1
                fname = old_fname+'({})'.format(i)
            path_filename.filenames[d] = fname

        return fname

def get_parents(path):
    '''TODO: docstring
    '''
    if not path:
        return [("/", path_filename(''))]

    parent, base = os.path.split(path)
    fname = path_filename(path)

    return get_parents(parent) + [(base, fname)]

# TODO: refactor, modularize this

# TODO: if it exists already, 
# completely clear this directory before repopulating

if not os.path.exists(args.web_directory):
    os.makedirs(args.web_directory)

# Set up Jinja2 template envronment
source_path = os.path.dirname(os.path.realpath(__file__))
template_path = os.path.join(source_path, 'web-template')
env = Environment(loader=FileSystemLoader(template_path),
                  trim_blocks=True, lstrip_blocks=True)
env.filters['quote'] = escape

# get jinja templates
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

## Add file to each directory
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

# Create HTML for each directory
for directory, contents in directories.items():
    dir_path = get_parents(directory)
    directory_html = directory_template.render(
        dir_path=dir_path, contents=contents)

    dirname = path_filename(directory)
    html_filename = os.path.join(args.web_directory, dirname)
    open(html_filename, 'w').write(directory_html)

