'''
overwatch interface for fsharplint
'''
import re
import sys
import json
import subprocess

pattern = re.compile('<error line="(\d+)" column="(\d+)" severity="(.*?)" message="(.*?)" source="(.*?)"\/>')

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
        for row, col, sev, message, file in pattern.findall(output)
    ]

    return violations