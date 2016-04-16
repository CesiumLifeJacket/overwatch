#!/usr/bin/python
import re
import sys
import json

# read an error report froom stdin
report = sys.stdin.read()

# convert the report to json
pattern = re.compile('(.*?):(\d+):(\d+): (\w+) (.*)')
violations = [
    {
        'row': int(row),
        'col': int(col),
        'type': t,
        'message': message
    }
    for f, row, col, t, message in pattern.findall(report)
]

# Write json to stdout
json.dump(violations, sys.stdout)
