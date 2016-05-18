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