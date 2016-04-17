'''
read the .style.yml and apply appropriate stylecheckers to the appropriate files
write out the results to .style_violations.json
'''
import os
import json
import yaml
from glob import glob

import pdb

# load the configureation file
config = yaml.load(open(".style.yml"))

# generate the style report
report = {} # filename: style violations pairs

for stylechecker_name, patterns in config.items():
	stylechecker = __import__("stylecheckers.{}".format(stylechecker_name), fromlist=['stylecheckers'])
	files = sum((glob(pattern) for pattern in patterns), [])
	report.update({f: stylechecker.check(f) for f in files})

# Write out style report
json.dump(report, open(".style_violations.json", 'w'),
	      sort_keys=True, indent=2, separators=(',', ': '))
