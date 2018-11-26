# Code to stream log events to a file based on a small log files. A random line in the
# original logfile is picked and combined with the current date.

import os
from datetime import datetime
import random
import time
import pytz

# User configurable options
seconds_between_events = 1
input_log = './logs/large_access_log.log'
output_log = './logs/stream.log'


def create_log_event():
    date_now = datetime.now(pytz.timezone(time.localtime().tm_zone))
    i_line = random.randrange(0, n_log_lines)

    date_now_str = date_now.strftime("%d/%b/%Y:%H:%M:%S %z")
    new_log_line = log_lines[i_line].split('\t')
    new_date_item = (
            new_log_line[3][:1] + date_now_str + new_log_line[3][27:]
    )
    new_log_line[3] = new_date_item
    new_log_line = '\t'.join(new_log_line)

    return new_log_line


# Set random seed to make runs reproducible
random.seed(42)

# Read log lines
log_lines = []
for line in open(input_log, 'rb'):
    line_decoded = line.decode('utf8')
    log_lines.append(line_decoded)
n_log_lines = len(log_lines)

# Stream log lines
while True:
    with open(output_log, 'ab') as fid:
        log_line = create_log_event()
        fid.write(log_line.encode('utf8'))
    time.sleep(seconds_between_events)