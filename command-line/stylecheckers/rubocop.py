#*********************************************************************************
#  ___ _        _   __      __    _      _             ___ ___  
# / __| |_ _  _| |__\ \    / /_ _| |_ __| |_  ___ _ _ |_ _/ _ \ 
# \__ \  _| || | / -_) \/\/ / _` |  _/ _| ' \/ -_) '_| | | (_) |
# |___/\__|\_, |_\___|\_/\_/\__,_|\__\__|_||_\___|_|(_)___\___/ 
#          |__/                                                 
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
overwatch interface for RuboCop
'''
import re
import sys
import json
import subprocess

pattern = re.compile('(.*?):(\d+):(\d+): ([CEFW]): (.*)')


def check(filename):
    # TODO: get output from RuboCop
    process = subprocess.Popen(['rubocop', filename],
                               stdout=subprocess.PIPE)

    output, _ = process.communicate()
    output = output.decode("utf-8")

    # convert the report to json
    violations = [
        {
            'row': int(row),
            'col': int(col),
            'type': t,
            'message': message
        }
        for f, row, col, t, message in pattern.findall(output)
    ]

    return violations
