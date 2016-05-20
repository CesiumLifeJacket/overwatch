#*********************************************************************************
#    ___         _     ___ _        _   _     
#   / __|___  __| |___/ __| |_ _  _| | (_)___ 
#  | (__/ _ \/ _` / -_)__ \  _| || | |_| / _ \
#   \___\___/\__,_\___|___/\__|\_, |_(_)_\___/
#                              |__/                                                         
#
#
# Originaly developed by students of Whitworth University -> http://www.whitworth.edu/cms/
# 
# Incepted and maintained by Will Czifro -> will@czifrotech.com
#
#
# This software is distributed on an "AS IS" basis, WITHOUT WARRANTY OF ANY
# KIND, either express or implied.
#
#*********************************************************************************
'''
Author: Jeremy Vonderfecht

Command-line utility which checks code style against a standard and produces
html-based report in specified directory. Read the .style.yml and apply
appropriate stylecheckers to the appropriate files write out the results to
web_directory as specified by command line argument
'''
import os
import Rx
import sys
import json
import yaml
import shutil
import argparse
from glob import glob
from cgi import escape
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

import pdb

### Set up Jinja2 Environment and Get Templates ------------------------------

source_path = Path(__file__).resolve().parent
template_path = source_path / 'web-template'
env = Environment(loader=FileSystemLoader(str(template_path)),
                  trim_blocks=True, lstrip_blocks=True)
env.filters['quote'] = escape

# Get jinja templates
file_template = env.get_template("file.html")
directory_template = env.get_template("directory.html")

### Get Rx Schema for The Configuration File ---------------------------------

config_schema_file = source_path / 'config-schema.yml'
config_schema = yaml.load(config_schema_file.open())
config_schema = Rx.make_schema(config_schema)

### Parse Command Line Arguments ---------------------------------------------

parser = argparse.ArgumentParser(
    description="check code style of a project based upon settings in " +
    ".style.yml")
parser.add_argument(
    'web_directory',
    help="directory in which to write web report")
parser.add_argument(
    '--project_directory',
    help="directory in which to place your project " +
    "and .style.yml")

args = parser.parse_args()

web_directory = Path(args.web_directory)

if args.project_directory:
    os.chdir(args.project_directory)

### Load the Style Configuration File ----------------------------------------
config_path = Path('.style.yml')

try:
    config = yaml.load(config_path.open())
    config_schema.validate(config)
except FileNotFoundError as e:
    print("Could not find required config file {}".format(config_path))
    exit(1)
except Rx.SchemaMismatch as e:
    print("malformed {}:".format(config_path))
    print(e)
    exit(1)

### Perform Style Checking for the Project -----------------------------------

# Perform the stylecheck and generate the report
report = {}  # filename: style violations pairs

for stylechecker_name, patterns in config.items():
    # TODO: report error when stylechecker isn't found
    try:
        stylechecker = __import__("stylecheckers.{}".format(
            stylechecker_name), fromlist=['stylecheckers'])
    except:
        print("Could not find stylechecker '{}'.".format(stylechecker_name))
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
            report_files[Path(f)] = stylechecker.check(f)
        except:
            print("Error checking file {}".format(f))

    report.update(report_files)


def annotate_code(code, violations):
    # TODO: more thorough docstring here
    '''HTML escape the code and insert tags to mark style violations.
    '''
    # Calculate starting index of each line
    line_indices = [0]

    for line_length in map(len, code.split('\n')):
        line_index = line_indices[-1] + line_length + 1
        line_indices.append(line_index)

    # Determine spans to insert and where to inesrt them

    # set of `(index, text)` pairs; `text` will be inserted at `index`
    insertions = set()

    for v in violations:
        index = line_indices[v['row'] - 1] + v['col'] - 1

        insertion = ('<div class="violation" type="{}" style="width:{}ch;">' +
                     '<div class="error">{}</div></div>').format(
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


### Generate directory report information ------------------------------------


def path_filename(path):
    '''Returns unique .html file name for the given path.

    Maps paths to directories and files in the project
    to unique html filenames for the html report.
    '''
    if not hasattr(path_filename, 'filenames'):
        setattr(path_filename, 'filenames', {})
        path_filename.filenames[''] = 'Index.html'

    if path in path_filename.filenames:
        return path_filename.filenames[path]
    else:
        if str(path) == '.':
            return "index.html"
        fname = str(path).replace('/', '__').replace('\\', '__') + '.html'
        if fname not in path_filename.filenames.values():
            path_filename.filenames[path] = fname
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
    '''return a list of (name, html filename) pairs for each parent directory
    of path.
    '''
    path_parts = list(reversed(path.parents)) + [path]

    return [(parent.name, path_filename(parent)) for parent in path_parts]

directories = {}

## Add files to each directory report.
for file, violations in report.items():
    directory = file.parent
    base = file.name

    if directory not in directories:
        directories[directory] = []

    directories[directory].append({
        "name": base,
        "path": path_filename(file),
        "is_directory": False,
        "errors": len(violations)
    })

## Add subdirectories to each directory report.
for directory in directories:
    if directory == Path('.'):
        continue

    parent = directory.parent
    base = directory.name

    directories[parent].append({
        "name": base,
        "path": path_filename(directory),
        "is_directory": True,
        "files": len(directories[directory])
    })


### Generate Web Report Files and Directories --------------------------------

# Create the main report directory
if not web_directory.exists():
    os.makedirs(str(web_directory))

##  Copy over supporting CSS and JS into the report directory
css_path = web_directory / 'css'
if not css_path.exists():
    shutil.copytree(str(template_path / 'css'), str(css_path))

js_path = web_directory / 'js'
if not js_path.exists():
    shutil.copytree(str(template_path / 'js'), str(js_path))

## Create HTML for the file reports
for file, violations in report.items():
    # Render HTML
    dir_path = get_parents(file)
    code = file.open().read()
    annotated_code = annotate_code(code, violations)
    file_html = file_template.render(
        dir_path=dir_path,
        language='python',
        code=annotated_code
        )

    # Write to file
    html_filename = web_directory / path_filename(file)
    html_filename.open('w').write(file_html)

# Create HTML for each directory
for directory, contents in directories.items():
    dir_path = get_parents(directory)
    directory_html = directory_template.render(
        dir_path=dir_path, contents=contents)

    dirname = path_filename(directory)
    html_filename = web_directory / dirname
    html_filename.open('w').write(directory_html)
