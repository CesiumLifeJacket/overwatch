'''
overwatch interface for RuboCop
'''
import re
import sys
import json
import subprocess

pattern = re.compile('(.*?)[:](\d+)[:](\d+)[:][ ]([CEFW])[:][ ]([\w\-\'[:space:].]+\.)')

def check(filename):
    # TODO: get output from RuboCop
    process = subprocess.Popen(['rubocop', filename],
                               stdout=subprocess.PIPE)

    output, _ = process.communicate()

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