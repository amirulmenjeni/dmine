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
        try:
            with open(filename, 'wb') as f:
                for i in item:
                    json_str = json.dumps(i)
                    f.write(json_str)
        except TypeError:
            for i in item:
                json_str = json.dumps(i)
                sys.stdout.write(json_str)

    # Store in CSV format.
    elif file_format == 'csv':
        keys = list(list(item)[0].keys())
        try:
            with open(filename, 'w') as f:
                dw = csv.DictWriter(f, keys)
                dw.writeheader()
                for i in item:
                    dw.writerow(i)
            print('to file')
        except TypeError:
            print(','.join(keys))
            for i in item:
                print(i)
                row = ','.join(list(i.values()))
                print(row)
            print('to stdout')

