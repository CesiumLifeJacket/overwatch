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
overwatch interface for fsharplint
'''
import re
import sys
import json
import subprocess

pattern = re.compile('(.*?)\nError in file (.*?) on line (\d+) starting at column (\d+)')


def check(filename):
    # TODO: get output from pep8
    process = subprocess.Popen(['fsharplint', filename],
                               stdout=subprocess.PIPE)

    output, _ = process.communicate()
    output = output.decode("utf-8")


    # convert the report to json
    violations = [
        {
            'row': int(row),
            'col': int(col),
            'message': message
        }
        for message, file, row, col in pattern.findall(output)
    ]

    return violations
