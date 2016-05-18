'''
overwatch interface for pep8
'''
import re
import sys
import json
import subprocess
import pdb

pattern = re.compile('(.*?):(\d+):(\d+): (\w+) (.*)')


def check(filename):
    # TODO: get output from pep8
    process = subprocess.Popen(['pep8', filename],
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
