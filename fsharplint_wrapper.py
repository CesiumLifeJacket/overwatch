#!/usr/bin/python
import re
import sys
import json

# read an error report froom stdin
report = sys.stdin.read()

# convert the report to json
pattern = re.compile('(.*?)\nError in file (.*?) on line (\d+) starting at column (\d+)')

violations = [
    {
        'row': int(row),
        'col': int(col),
        'message': message
    }
    for message, file, row, col in pattern.findall(report)
]

# Write json to stdout
json.dump(violations, sys.stdout)