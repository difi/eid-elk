import os
from datetime import datetime
import random

# User configurable options
n_log_lines_to_generate = 100000
min_date = datetime(2018, 1, 1)
max_date = datetime.now()
input_logs_dir = [
    './application_logs',
    './access_logs'
]
log_type = [
    'application',
    'access'
]
output_logs = [
    './logs/large_application_log.log',
    './logs/large_access_log.log'
]

# Set random seed to make runs reproducible
random.seed(42)


def create_random_logs(input_logs_dir, log_type, output_log):

    if log_type not in ['application', 'access']:
        print('Invalid log format.')
        exit(-1)

    # Read log lines
    log_lines = []
    for filename in os.listdir(input_logs_dir):
        for line in open(os.path.join(input_logs_dir, filename), 'rb'):
            line_decoded = line.decode('utf8')
            if log_type == 'application':
                try:
                    date = datetime.strptime(line_decoded[:23], "%Y-%m-%d %H:%M:%S,%f")
                    log_lines.append(line_decoded)
                except:
                    log_lines[-1] = log_lines[-1] + line_decoded
            elif log_type == 'access':
                log_lines.append(line_decoded)

    n_log_lines = len(log_lines)

    # Create output folder if it does not exist
    if not os.path.exists(os.path.dirname(output_log)):
        os.makedirs(os.path.dirname(output_log))

    # Write pick random lines from the original log, replace the date with a new random date
    # in the desired range, and write it to file.
    with open(output_log, 'wb') as fid:
        for i in range(n_log_lines_to_generate):
            random_date = (max_date - min_date)*random.uniform(0, 1) + min_date
            i_line = random.randrange(0, n_log_lines)
            if log_type == 'application':
                random_date_str = random_date.strftime("%Y-%m-%d %H:%M:%S,%f")[:23]
                new_log_line = random_date_str + log_lines[i_line][23:]
            elif log_type == 'access':
                random_date_str = random_date.strftime("%d/%b/%Y:%H:%M:%S")
                new_log_line = log_lines[i_line].split('\t')
                new_date_item = (
                        new_log_line[3][:1] + random_date_str + new_log_line[3][21:]
                )
                new_log_line[3] = new_date_item
                new_log_line = '\t'.join(new_log_line)

            fid.write(new_log_line.encode('utf8'))


for i in range(len(input_logs_dir)):
    create_random_logs(input_logs_dir[i], log_type[i], output_logs[i])
