import os
from datetime import datetime
import random

# User configurable options
n_log_lines_to_generate = 1000000
min_date = datetime(2018, 1, 1)
max_date = datetime.now()
input_logs_dir = '/Users/dsa/Downloads/logs'
output_logs = './logs/large_log.log'

# Read log lines
log_lines = []
for filename in os.listdir(input_logs_dir):
    for line in open(os.path.join(input_logs_dir, filename), 'rb'):
        line_decoded = line.decode('ascii')
        try:
            date = datetime.strptime(line_decoded[:23], "%Y-%m-%d %H:%M:%S,%f")
            log_lines.append(line_decoded)
        except:
            log_lines[-1] = log_lines[-1] + line_decoded
n_log_lines = len(log_lines)

# Create output folder if it does not exist
if not os.path.exists(os.path.dirname(output_logs)):
    os.makedirs(os.path.dirname(output_logs))

# Write pick random lines from the original log, replace the date with a new random date
# in the desired range, and write it to file.
with open(output_logs, 'wb') as fid:
    for i in range(n_log_lines_to_generate):
        random_date = (max_date - min_date)*random.uniform(0, 1) + min_date
        random_date_str = random_date.strftime("%Y-%m-%d %H:%M:%S,%f")[:23]

        i_line = random.randrange(0, n_log_lines)
        new_log_line = random_date_str + log_lines[i_line][23:]

        fid.write(new_log_line.encode('ascii'))