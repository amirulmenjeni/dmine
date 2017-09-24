# utils.py
#
#

import json
import csv
import sys

# @param item: The item to append to the a file.
# @param filename: The filename of the file.
#
# If no filename is specified, then print to stdout.
# Otherwise, print to specified file.
def to_file(item, filename=None, file_format='json'):
 
    # Store in JSON format.
    if file_format == 'json':
        if filename:
            with open(filename, 'w') as f:
                for i in item:
                    json_str = json.dumps(i)
                    f.write(json_str)
        else:
            for i in item:
                json_str = json.dumps(i)
                sys.stdout.write(json_str)

    # Store in CSV format.
    elif file_format == 'csv':
        if filename:
            with open(filename, 'w') as f:
                f.write(keys)
                for i in item:
                    row = ','.join(list(i.values()))
                    f.write(row)
        else:
            for i in item:
                row = ','.join(['\"' + v + '\"' for v in list(i.values())])
                sys.stdout.write(row)

